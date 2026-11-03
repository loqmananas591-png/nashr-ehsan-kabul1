# Generated for the additional customer features.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('store', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BookReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(choices=[(1, '۱ - ضعیف'), (2, '۲ - قابل قبول'), (3, '۳ - خوب'), (4, '۴ - بسیار خوب'), (5, '۵ - عالی')], verbose_name='امتیاز')),
                ('title', models.CharField(blank=True, max_length=120, verbose_name='عنوان نظر')),
                ('body', models.TextField(max_length=1500, verbose_name='نظر شما')),
                ('is_approved', models.BooleanField(default=False, verbose_name='تأیید شده')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='store.book', verbose_name='کتاب')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_reviews', to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={'verbose_name': 'نظر کتاب', 'verbose_name_plural': 'نظرهای کتاب', 'ordering': ['-created_at']},
        ),
        migrations.AddConstraint(
            model_name='bookreview',
            constraint=models.UniqueConstraint(fields=('book', 'user'), name='unique_review_per_user_book'),
        ),
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name='نام')),
                ('phone', models.CharField(blank=True, max_length=40, verbose_name='شماره تماس')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='ایمیل')),
                ('subject', models.CharField(max_length=180, verbose_name='موضوع')),
                ('message', models.TextField(max_length=4000, verbose_name='پیام')),
                ('is_read', models.BooleanField(default=False, verbose_name='خوانده شده')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ دریافت')),
            ],
            options={'verbose_name': 'پیام مشتری', 'verbose_name_plural': 'پیام‌های مشتریان', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='NewsletterSubscriber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='ایمیل')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ عضویت')),
            ],
            options={'verbose_name': 'عضو خبرنامه', 'verbose_name_plural': 'اعضای خبرنامه', 'ordering': ['-created_at']},
        ),
    ]
