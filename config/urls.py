from django.contrib import admin
from django.urls import path, include
from store import views as store_views
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "مدیریت کتاب‌فروشی نشر احسان کابل"
admin.site.site_title = "مدیریت نشر احسان"
admin.site.index_title = "مدیریت فروشگاه و سفارش‌ها"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", store_views.sitemap_xml, name="sitemap_xml"),
    path("robots.txt", store_views.robots_txt, name="robots_txt"),
    path("", include("store.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
