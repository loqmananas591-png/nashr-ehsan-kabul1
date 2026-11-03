from django.core.management.base import BaseCommand
from store.models import Category, Author, Book

class Command(BaseCommand):
    help = "Adds optional demo categories, authors, and books."
    def handle(self, *args, **options):
        cat, _ = Category.objects.get_or_create(name="ادبیات و فرهنگ")
        author, _ = Author.objects.get_or_create(name="نمونه نویسنده")
        Book.objects.get_or_create(title="نمونه کتاب برای آغاز کار", defaults={
            "category": cat, "author": author,
            "description": "این یک کتاب نمونه است. از پنل مدیریت می‌توانید آن را ویرایش یا حذف کنید.",
            "price": 150, "stock": 5, "is_featured": True
        })
        self.stdout.write(self.style.SUCCESS("نمونه‌های اولیه اضافه شدند."))
