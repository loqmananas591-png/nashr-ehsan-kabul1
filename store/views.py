from decimal import Decimal
from urllib.parse import quote
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Q, Sum, F, Count, Avg
from django.http import HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from .forms import RegisterForm, CheckoutForm, BookReviewForm, ContactMessageForm, NewsletterForm
from .models import Book, Category, Order, OrderItem, BookReview, NewsletterSubscriber

def home(request):
    featured = Book.objects.filter(is_active=True, is_featured=True, stock__gt=0).select_related("author", "category")[:8]
    newest = Book.objects.filter(is_active=True, stock__gt=0).select_related("author", "category")[:12]
    newsletter_form = NewsletterForm()
    return render(request, "store/home.html", {"featured": featured, "newest": newest, "newsletter_form": newsletter_form})

def book_list(request):
    books = Book.objects.filter(is_active=True).select_related("author", "category")
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    availability = request.GET.get("available", "")
    if query: books = books.filter(Q(title__icontains=query) | Q(author__name__icontains=query) | Q(description__icontains=query))
    if category.isdigit(): books = books.filter(category_id=int(category))
    if min_price:
        try: books = books.filter(price__gte=Decimal(min_price))
        except Exception: pass
    if max_price:
        try: books = books.filter(price__lte=Decimal(max_price))
        except Exception: pass
    if availability == "1": books = books.filter(stock__gt=0)
    sort = request.GET.get("sort", "newest")
    if sort == "price_low": books = books.order_by("price")
    elif sort == "price_high": books = books.order_by("-price")
    elif sort == "title": books = books.order_by("title")
    paginator = Paginator(books, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "store/book_list.html", {"books": page_obj, "page_obj": page_obj, "categories": Category.objects.all(), "q": query})

def book_detail(request, slug):
    book = get_object_or_404(Book.objects.select_related("author", "category"), slug=slug, is_active=True)
    review_form = BookReviewForm()
    reviews = book.reviews.filter(is_approved=True).select_related("user")
    user_review = None
    if request.user.is_authenticated:
        user_review = book.reviews.filter(user=request.user).first()
    average_rating = reviews.aggregate(avg=Avg("rating"))["avg"]
    return render(request, "store/book_detail.html", {"book": book, "reviews": reviews, "review_form": review_form, "user_review": user_review, "average_rating": average_rating})

@require_POST
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, pk=book_id, is_active=True)
    try: quantity = max(1, min(20, int(request.POST.get("quantity", "1"))))
    except ValueError: quantity = 1
    if book.stock < 1:
        messages.error(request, "این کتاب فعلاً موجود نیست.")
    else:
        cart = request.session.get("cart", {})
        current = int(cart.get(str(book.id), 0))
        cart[str(book.id)] = min(book.stock, current + quantity)
        request.session["cart"] = cart
        request.session.modified = True
        messages.success(request, "کتاب به سبد خرید اضافه شد.")
    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(next_url)
    return redirect("cart")

def cart(request):
    cart_data = request.session.get("cart", {})
    ids = [int(k) for k in cart_data.keys() if str(k).isdigit()]
    books = Book.objects.filter(id__in=ids, is_active=True)
    items, total = [], Decimal("0.00")
    for book in books:
        quantity = min(int(cart_data.get(str(book.id), 1)), book.stock)
        if quantity < 1: continue
        subtotal = book.price * quantity
        items.append({"book": book, "quantity": quantity, "subtotal": subtotal})
        total += subtotal
    return render(request, "store/cart.html", {"items": items, "total": total})

@require_POST
def update_cart(request, book_id):
    cart_data = request.session.get("cart", {})
    book = get_object_or_404(Book, pk=book_id)
    try: quantity = int(request.POST.get("quantity", "1"))
    except ValueError: quantity = 1
    if quantity <= 0: cart_data.pop(str(book_id), None)
    elif book.is_active and book.stock: cart_data[str(book_id)] = min(quantity, book.stock)
    else: cart_data.pop(str(book_id), None)
    request.session["cart"] = cart_data
    request.session.modified = True
    return redirect("cart")

@login_required
def checkout(request):
    cart_data = request.session.get("cart", {})
    if not cart_data:
        messages.info(request, "سبد خرید شما خالی است.")
        return redirect("book_list")
    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                ids = [int(k) for k in cart_data if str(k).isdigit()]
                locked_books = {str(b.id): b for b in Book.objects.select_for_update().filter(id__in=ids, is_active=True)}
                order_lines, total = [], Decimal("0.00")
                for key, raw_qty in cart_data.items():
                    book = locked_books.get(key)
                    if not book: continue
                    qty = min(max(1, int(raw_qty)), book.stock)
                    if qty < 1:
                        messages.error(request, f"کتاب «{book.title}» موجود نیست؛ لطفاً سبد خرید را اصلاح کنید.")
                        return redirect("cart")
                    order_lines.append((book, qty))
                    total += book.price * qty
                if not order_lines:
                    return redirect("cart")
                data = form.cleaned_data
                order = Order.objects.create(customer=request.user, full_name=data["full_name"], phone=data["phone"],
                    country=data["country"], city=data["city"], province=data["province"], postal_code=data["postal_code"],
                    address=data["address"], note=data["note"], total=total)
                for book, qty in order_lines:
                    OrderItem.objects.create(order=order, book=book, title=book.title, price=book.price, quantity=qty)
                    book.stock -= qty
                    book.save(update_fields=["stock"])
            request.session["cart"] = {}
            request.session.modified = True
            messages.success(request, f"سفارش شما با شماره {order.pk} ثبت شد.")
            return redirect("order_detail", order_id=order.pk)
    else:
        form = CheckoutForm(initial={"full_name": request.user.get_full_name() or request.user.username, "phone": "", "country": "افغانستان", "city": "کابل"})
    return render(request, "store/checkout.html", {"form": form})

@login_required
def account(request):
    orders = Order.objects.filter(customer=request.user).order_by("-created_at")
    return render(request, "store/account.html", {"orders": orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("items"), pk=order_id, customer=request.user)
    return render(request, "store/order_detail.html", {"order": order})

@login_required
@require_POST
def cancel_order(request, order_id):
    with transaction.atomic():
        order = get_object_or_404(Order.objects.select_for_update(), pk=order_id, customer=request.user)
        if order.status != "pending":
            messages.error(request, "این سفارش دیگر قابل لغو نیست.")
            return redirect("order_detail", order_id=order.pk)
        for item in order.items.select_related("book"):
            item.book.stock = F("stock") + item.quantity
            item.book.save(update_fields=["stock"])
        order.status = "cancelled"
        order.save(update_fields=["status"])
    messages.success(request, "سفارش لغو شد.")
    return redirect("order_detail", order_id=order.pk)

def register(request):
    if request.user.is_authenticated: return redirect("account")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "حساب کاربری شما ساخته شد.")
            return redirect("account")
    else: form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})

def whatsapp_order(request):
    cart_data = request.session.get("cart", {})
    if not settings.WHATSAPP_NUMBER:
        messages.error(request, "شماره واتساپ فروشگاه هنوز در تنظیمات پروژه ثبت نشده است.")
        return redirect("cart")
    books = Book.objects.filter(id__in=[int(k) for k in cart_data if str(k).isdigit()], is_active=True)
    lines = ["سلام، می‌خواهم این کتاب‌ها را سفارش بدهم:"]
    for book in books:
        qty = int(cart_data.get(str(book.id), 0))
        if qty: lines.append(f"{book.title} — تعداد {qty} — {book.price} افغانی")
    if len(lines) == 1:
        messages.info(request, "سبد خرید خالی است.")
        return redirect("cart")
    url = "https://wa.me/" + "".join(c for c in settings.WHATSAPP_NUMBER if c.isdigit()) + "?text=" + quote("\n".join(lines))
    return redirect(url)


@user_passes_test(lambda u: u.is_authenticated and u.is_staff)
def sales_report(request):
    today = timezone.localdate()
    daily = Order.objects.filter(created_at__date=today).exclude(status="cancelled").aggregate(total=Sum("total"), count=Count("id"))
    monthly = Order.objects.filter(created_at__year=today.year, created_at__month=today.month).exclude(status="cancelled").aggregate(total=Sum("total"), count=Count("id"))
    yearly = Order.objects.filter(created_at__year=today.year).exclude(status="cancelled").aggregate(total=Sum("total"), count=Count("id"))
    bestsellers = OrderItem.objects.filter(order__status__in=["confirmed", "shipping", "completed"]).values("title").annotate(
        quantity_sold=Sum("quantity"), revenue=Sum(F("price") * F("quantity"))
    ).order_by("-quantity_sold")[:10]
    recent_orders = Order.objects.select_related("customer").order_by("-created_at")[:20]
    return render(request, "store/sales_report.html", {
        "today": today, "daily": daily, "monthly": monthly, "yearly": yearly,
        "bestsellers": bestsellers, "recent_orders": recent_orders,
    })


def about(request):
    return render(request, "store/about.html")

def faq(request):
    return render(request, "store/faq.html")

def shipping_policy(request):
    return render(request, "store/shipping.html")

def privacy_policy(request):
    return render(request, "store/privacy.html")

@require_http_methods(["GET", "POST"])
def contact(request):
    if request.method == "POST":
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "پیام شما ثبت شد. پس از بررسی با شما تماس می‌گیریم.")
            return redirect("contact")
    else:
        form = ContactMessageForm()
    return render(request, "store/contact.html", {"form": form})

@login_required
@require_POST
def add_review(request, slug):
    book = get_object_or_404(Book, slug=slug, is_active=True)
    if BookReview.objects.filter(book=book, user=request.user).exists():
        messages.info(request, "شما قبلاً برای این کتاب نظر ثبت کرده‌اید.")
        return redirect(book.get_absolute_url())
    form = BookReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.book = book
        review.user = request.user
        review.save()
        messages.success(request, "نظر شما ثبت شد و پس از بررسی مدیر نمایش داده می‌شود.")
    else:
        messages.error(request, "لطفاً امتیاز و متن نظر را درست وارد کنید.")
    return redirect(book.get_absolute_url())

@require_POST
def newsletter_subscribe(request):
    form = NewsletterForm(request.POST)
    if form.is_valid():
        NewsletterSubscriber.objects.get_or_create(email=form.cleaned_data["email"], defaults={"is_active": True})
        messages.success(request, "ایمیل شما برای دریافت خبرهای نشر احسان ثبت شد.")
    else:
        messages.error(request, "لطفاً یک ایمیل معتبر وارد کنید.")
    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(next_url)
    return redirect("home")


def sitemap_xml(request):
    from django.http import HttpResponse
    from django.urls import reverse
    from django.utils.html import escape
    paths = [reverse(name) for name in ("home", "book_list", "about", "contact", "faq", "shipping_policy", "privacy_policy")]
    urls = [request.build_absolute_uri(path) for path in paths]
    for slug in Book.objects.filter(is_active=True).values_list("slug", flat=True).iterator():
        urls.append(request.build_absolute_uri(reverse("book_detail", args=[slug])))
    xml = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{escape(url)}</loc></url>" for url in urls) + "</urlset>"
    return HttpResponse(xml, content_type="application/xml; charset=utf-8")


def robots_txt(request):
    from django.http import HttpResponse
    content = "User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /account/\nDisallow: /cart/\nDisallow: /checkout/\nSitemap: " + request.build_absolute_uri("/sitemap.xml") + "\n"
    return HttpResponse(content, content_type="text/plain; charset=utf-8")
