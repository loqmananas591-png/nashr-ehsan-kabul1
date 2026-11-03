from django.conf import settings
from .models import Category

def shop_context(request):
    return {
        "nav_categories": Category.objects.all()[:8],
        "whatsapp_number": settings.WHATSAPP_NUMBER,
        "cart_count": sum(int(v) for v in request.session.get("cart", {}).values()),
    }
