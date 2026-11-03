from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order

class RegisterForm(UserCreationForm):
    email = forms.EmailField(label="ایمیل", required=False)
    first_name = forms.CharField(label="نام", max_length=150, required=True)
    class Meta:
        model = User
        fields = ("username", "first_name", "email", "password1", "password2")
        labels = {"username": "نام کاربری", "password1": "رمز عبور", "password2": "تکرار رمز عبور"}

class CheckoutForm(forms.Form):
    full_name = forms.CharField(label="نام مکمل گیرنده", max_length=160, widget=forms.TextInput(attrs={"autocomplete": "name"}))
    phone = forms.CharField(label="شماره تماس با کد کشور", max_length=40, widget=forms.TextInput(attrs={"placeholder": "+93 ...", "autocomplete": "tel"}))
    country = forms.CharField(label="کشور", max_length=100, widget=forms.TextInput(attrs={"placeholder": "مثلاً افغانستان، آلمان، کانادا", "autocomplete": "country-name"}))
    city = forms.CharField(label="شهر", max_length=100, widget=forms.TextInput(attrs={"autocomplete": "address-level2"}))
    province = forms.CharField(label="ولایت / ایالت / منطقه (اختیاری)", max_length=100, required=False, widget=forms.TextInput(attrs={"autocomplete": "address-level1"}))
    postal_code = forms.CharField(label="کد پستی (اگر دارید)", max_length=30, required=False, widget=forms.TextInput(attrs={"autocomplete": "postal-code"}))
    address = forms.CharField(label="آدرس کامل، کوچه و شماره خانه", widget=forms.Textarea(attrs={"rows": 3, "autocomplete": "street-address"}))
    note = forms.CharField(label="یادداشت (اختیاری)", required=False, widget=forms.Textarea(attrs={"rows": 2}))

from .models import BookReview, ContactMessage, NewsletterSubscriber

class BookReviewForm(forms.ModelForm):
    class Meta:
        model = BookReview
        fields = ("rating", "title", "body")
        widgets = {
            "rating": forms.Select(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"placeholder": "عنوان کوتاه (اختیاری)"}),
            "body": forms.Textarea(attrs={"rows": 4, "placeholder": "تجربه و نظر خود را درباره این کتاب بنویسید"}),
        }

class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ("name", "phone", "email", "subject", "message")
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ("email",)
        widgets = {"email": forms.EmailInput(attrs={"placeholder": "ایمیل شما", "aria-label": "ایمیل برای عضویت در خبرنامه"})}
