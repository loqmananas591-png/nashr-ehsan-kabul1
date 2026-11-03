from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("store", "0002_bookreview_contactmessage_newslettersubscriber")]

    operations = [
        migrations.AddField(
            model_name="order", name="country",
            field=models.CharField(default="افغانستان", max_length=100, verbose_name="کشور"),
        ),
        migrations.AddField(
            model_name="order", name="city",
            field=models.CharField(default="کابل", max_length=100, verbose_name="شهر"),
        ),
        migrations.AddField(
            model_name="order", name="postal_code",
            field=models.CharField(blank=True, max_length=30, verbose_name="کد پستی (در صورت موجود بودن)"),
        ),
        migrations.AlterField(
            model_name="order", name="province",
            field=models.CharField(blank=True, max_length=100, verbose_name="ولایت / ایالت / منطقه"),
        ),
        migrations.AlterField(
            model_name="order", name="address",
            field=models.TextField(verbose_name="آدرس مکمل و دقیق"),
        ),
    ]
