from django.contrib import admin
from .models import Category, Author, Book, Order, OrderItem, BookReview, ContactMessage, NewsletterSubscriber

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "price", "stock", "is_active", "is_featured")
    list_filter = ("category", "is_active", "is_featured")
    search_fields = ("title", "author__name", "description")
    list_editable = ("price", "stock", "is_active", "is_featured")
    prepopulated_fields = {"slug": ("title",)}

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("book", "title", "price", "quantity")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "country", "city", "phone", "total", "status", "created_at")
    list_filter = ("status", "created_at", "country")
    search_fields = ("full_name", "phone", "id")
    list_editable = ("status",)
    readonly_fields = ("customer", "full_name", "phone", "country", "city", "province", "postal_code", "address", "note", "total", "created_at")
    inlines = [OrderItemInline]


@admin.register(BookReview)
class BookReviewAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "rating", "is_approved", "created_at")
    list_filter = ("is_approved", "rating", "created_at")
    search_fields = ("book__title", "user__username", "title", "body")
    list_editable = ("is_approved",)
    readonly_fields = ("book", "user", "rating", "title", "body", "created_at")

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "phone", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "phone", "email", "subject", "message")
    list_editable = ("is_read",)
    readonly_fields = ("name", "phone", "email", "subject", "message", "created_at")

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("email",)
    list_editable = ("is_active",)
