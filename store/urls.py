from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("faq/", views.faq, name="faq"),
    path("shipping/", views.shipping_policy, name="shipping_policy"),
    path("privacy/", views.privacy_policy, name="privacy_policy"),
    path("newsletter/subscribe/", views.newsletter_subscribe, name="newsletter_subscribe"),
    path("books/", views.book_list, name="book_list"),
    path("books/<slug:slug>/", views.book_detail, name="book_detail"),
    path("books/<slug:slug>/review/", views.add_review, name="add_review"),
    path("cart/", views.cart, name="cart"),
    path("cart/add/<int:book_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:book_id>/", views.update_cart, name="update_cart"),
    path("cart/whatsapp/", views.whatsapp_order, name="whatsapp_order"),
    path("checkout/", views.checkout, name="checkout"),
    path("account/", views.account, name="account"),
    path("staff/reports/", views.sales_report, name="sales_report"),
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),
    path("orders/<int:order_id>/cancel/", views.cancel_order, name="cancel_order"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
