from decimal import Decimal
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField("نام دسته", max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True, allow_unicode=True)
    description = models.TextField("توضیحات", blank=True)

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True) or "category"
            base, i = self.slug, 2
            while Category.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base}-{i}"; i += 1
        super().save(*args, **kwargs)

    def __str__(self): return self.name

class Author(models.Model):
    name = models.CharField("نام نویسنده", max_length=160, unique=True)
    biography = models.TextField("زندگی‌نامه", blank=True)
    class Meta:
        verbose_name = "نویسنده"
        verbose_name_plural = "نویسندگان"
        ordering = ["name"]
    def __str__(self): return self.name

class Book(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="books", verbose_name="دسته‌بندی")
    author = models.ForeignKey(Author, on_delete=models.PROTECT, related_name="books", verbose_name="نویسنده")
    title = models.CharField("نام کتاب", max_length=220)
    slug = models.SlugField(unique=True, blank=True, allow_unicode=True)
    description = models.TextField("توضیحات")
    price = models.DecimalField("قیمت (افغانی)", max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField("موجودی", default=0)
    cover = models.ImageField("تصویر کتاب", upload_to="books/", blank=True, null=True)
    is_featured = models.BooleanField("نمایش در صفحه اصلی", default=False)
    is_active = models.BooleanField("فعال", default=True)
    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)

    class Meta:
        verbose_name = "کتاب"
        verbose_name_plural = "کتاب‌ها"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True) or "book"
            base, i = self.slug, 2
            while Book.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base}-{i}"; i += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self): return reverse("book_detail", args=[self.slug])
    def __str__(self): return self.title

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "در انتظار تأیید"), ("confirmed", "تأیید شده"),
        ("shipping", "در حال ارسال"), ("completed", "تکمیل شده"),
        ("cancelled", "لغو شده"),
    ]
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders", verbose_name="مشتری")
    full_name = models.CharField("نام مشتری", max_length=160)
    phone = models.CharField("شماره تماس", max_length=40)
    country = models.CharField("کشور", max_length=100, default="افغانستان")
    province = models.CharField("ولایت / ایالت / منطقه", max_length=100, blank=True)
    city = models.CharField("شهر", max_length=100, default="کابل")
    postal_code = models.CharField("کد پستی (در صورت موجود بودن)", max_length=30, blank=True)
    address = models.TextField("آدرس مکمل و دقیق")
    note = models.TextField("یادداشت", blank=True)
    status = models.CharField("وضعیت", max_length=20, choices=STATUS_CHOICES, default="pending")
    total = models.DecimalField("مجموع (افغانی)", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField("تاریخ سفارش", auto_now_add=True)

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        ordering = ["-created_at"]

    def __str__(self): return f"سفارش #{self.pk} — {self.full_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="سفارش")
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name="order_items", verbose_name="کتاب")
    title = models.CharField("نام کتاب هنگام سفارش", max_length=220)
    price = models.DecimalField("قیمت هنگام سفارش", max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField("تعداد")
    class Meta:
        verbose_name = "قلم سفارش"
        verbose_name_plural = "اقلام سفارش"
    @property
    def subtotal(self): return self.price * self.quantity

class BookReview(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews", verbose_name="کتاب")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="book_reviews", verbose_name="کاربر")
    rating = models.PositiveSmallIntegerField("امتیاز", choices=[(1, "۱ - ضعیف"), (2, "۲ - قابل قبول"), (3, "۳ - خوب"), (4, "۴ - بسیار خوب"), (5, "۵ - عالی")])
    title = models.CharField("عنوان نظر", max_length=120, blank=True)
    body = models.TextField("نظر شما", max_length=1500)
    is_approved = models.BooleanField("تأیید شده", default=False)
    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)

    class Meta:
        verbose_name = "نظر کتاب"
        verbose_name_plural = "نظرهای کتاب"
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["book", "user"], name="unique_review_per_user_book")]

    def __str__(self):
        return f"نظر {self.user} برای {self.book}"


class ContactMessage(models.Model):
    name = models.CharField("نام", max_length=120)
    phone = models.CharField("شماره تماس", max_length=40, blank=True)
    email = models.EmailField("ایمیل", blank=True)
    subject = models.CharField("موضوع", max_length=180)
    message = models.TextField("پیام", max_length=4000)
    is_read = models.BooleanField("خوانده شده", default=False)
    created_at = models.DateTimeField("تاریخ دریافت", auto_now_add=True)

    class Meta:
        verbose_name = "پیام مشتری"
        verbose_name_plural = "پیام‌های مشتریان"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} — {self.name}"


class NewsletterSubscriber(models.Model):
    email = models.EmailField("ایمیل", unique=True)
    is_active = models.BooleanField("فعال", default=True)
    created_at = models.DateTimeField("تاریخ عضویت", auto_now_add=True)

    class Meta:
        verbose_name = "عضو خبرنامه"
        verbose_name_plural = "اعضای خبرنامه"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email
