from django import forms

from django_select2.forms import Select2Widget, Select2MultipleWidget

from .models import *


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': 'username(email)',
                   'style': 'padding-left:5px;'
                   }))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'style': 'padding-left:5px;'
            }))


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title", "author", "image", "category", "isbn", "publisher",
                  "published_date", "available", "number_in_stock", ]
        widgets = {
            "title": forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Book Title',
                'required': 'true',
            }),
            "author": forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Author',
                'required': 'true',
            }),
            "category": Select2Widget(attrs={
                'data-width': '100%',
            }),
            "isbn": forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Book ISBN',
                'required': 'true',
            }),
            "publisher": Select2Widget(attrs={
                'data-width': '100%',
            }),
            "published_date": forms.DateInput(attrs={
                'class': 'datepicker',
                'placeholder': 'Published Date',
            }),
            "available": forms.CheckboxInput(),
            "number_in_stock":  forms.NumberInput(attrs={
                'class': 'form-control',
                'disabled': 'true',
            }),
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['number_in_stock'].required = False


class BookDeleteForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['deleted_at', ]
        widgets = {
            'deleted_at': forms.HiddenInput(),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title', ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Category Title',
                'required': 'true',
            }),
        }


class CategoryDeleteForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['deleted_at']
        widgets = {
            'deleted_at': forms.HiddenInput(),
        }


class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ['title', ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Publisher Title',
                'required': 'true',
            }),
        }


class PublisherDeleteForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ['deleted_at']
        widgets = {
            'deleted_at': forms.HiddenInput(),
        }


class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['title', 'position', 'urls', 'parent', ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Menu Title',
                'required': 'true',
            }),
            "position":  forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Position',
            }),
            'urls': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'URLS',
                'required': 'true',
            }),
            'parent': Select2Widget(attrs={
                'data-width': '100%',
            }),
        }


class MenuDeleteForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['deleted_at']
        widgets = {
            'deleted_at': forms.HiddenInput(),
        }


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['user', 'book', 'status', 'return_date',]
        widgets = {
            "user": Select2Widget(attrs = {
                "data-width": "100%",
            }),
            "book": Select2Widget(attrs = {
                "data-width": "100%",
            }),
            "status": Select2Widget(attrs = {
                "date-width": "100%",
            }),
            "return_date": forms.DateInput(attrs={
                'class': 'datepicker',
            }),
        }


class BookingDeleteForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['deleted_at']
        widgets = {
            'deleted_at': forms.HiddenInput(),
        }


class TestimonialForm(forms.ModelForm):
    class Meta:
        model = MemberTestimonial
        fields = ['testimonial_text', ]
        widgets = {
            'testimonial_text': forms.Textarea()
        }


class TestimonialDeleteForm(forms.ModelForm):
    class Meta:
        model = MemberTestimonial
        fields = ['deleted_at']
        widgets = {
            'deleted_at': forms.HiddenInput(),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contacts
        fields = ['name', 'email', 'subject', 'message', ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name',
                'required': 'true',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Your Email',
                'class': 'form-control',
                'required': 'true',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject',
                'required': 'true',
            }),
            'testimonial_text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Message',
                'required': 'true',
            }),
        }


class ContactDeleteForm(forms.ModelForm):
    class Meta:
        model = Contacts
        fields = ['deleted_at']
        widgets = {
            'deleted_at': forms.HiddenInput(),
        }


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Current Password'}))
    password = forms.CharField(label="New Password", widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'New Password',}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))


class ProfessionForm(forms.ModelForm):
    class Meta:
        model = Profession
        fields = ("title",)
