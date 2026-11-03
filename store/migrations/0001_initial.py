# Generated initial migration for the Nashr Ehsan bookstore.
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=160, unique=True, verbose_name='نام نویسنده')),
                ('biography', models.TextField(blank=True, verbose_name='زندگی‌نامه')),
            ],
            options={'verbose_name': 'نویسنده', 'verbose_name_plural': 'نویسندگان', 'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='نام دسته')),
                ('slug', models.SlugField(allow_unicode=True, blank=True, unique=True)),
                ('description', models.TextField(blank=True, verbose_name='توضیحات')),
            ],
            options={'verbose_name': 'دسته‌بندی', 'verbose_name_plural': 'دسته‌بندی‌ها', 'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=160, verbose_name='نام مشتری')),
                ('phone', models.CharField(max_length=40, verbose_name='شماره تماس')),
                ('province', models.CharField(max_length=80, verbose_name='ولایت')),
                ('address', models.TextField(verbose_name='آدرس مکمل')),
                ('note', models.TextField(blank=True, verbose_name='یادداشت')),
                ('status', models.CharField(choices=[('pending', 'در انتظار تأیید'), ('confirmed', 'تأیید شده'), ('shipping', 'در حال ارسال'), ('completed', 'تکمیل شده'), ('cancelled', 'لغو شده')], default='pending', max_length=20, verbose_name='وضعیت')),
                ('total', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='مجموع (افغانی)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ سفارش')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='مشتری')),
            ],
            options={'verbose_name': 'سفارش', 'verbose_name_plural': 'سفارش‌ها', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=220, verbose_name='نام کتاب')),
                ('slug', models.SlugField(allow_unicode=True, blank=True, unique=True)),
                ('description', models.TextField(verbose_name='توضیحات')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='قیمت (افغانی)')),
                ('stock', models.PositiveIntegerField(default=0, verbose_name='موجودی')),
                ('cover', models.ImageField(blank=True, null=True, upload_to='books/', verbose_name='تصویر کتاب')),
                ('is_featured', models.BooleanField(default=False, verbose_name='نمایش در صفحه اصلی')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='books', to='store.author', verbose_name='نویسنده')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='books', to='store.category', verbose_name='دسته‌بندی')),
            ],
            options={'verbose_name': 'کتاب', 'verbose_name_plural': 'کتاب‌ها', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=220, verbose_name='نام کتاب هنگام سفارش')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='قیمت هنگام سفارش')),
                ('quantity', models.PositiveIntegerField(verbose_name='تعداد')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='order_items', to='store.book', verbose_name='کتاب')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='store.order', verbose_name='سفارش')),
            ],
            options={'verbose_name': 'قلم سفارش', 'verbose_name_plural': 'اقلام سفارش'},
        ),
    ]
