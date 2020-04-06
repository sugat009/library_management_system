from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.safestring import mark_safe

from .models import Librarian, Member, User

from my_app.models import Category, Profession


class LibrarianForm(forms.ModelForm):
    class Meta:
        model = Librarian
        fields = ['first_name', 'last_name', 'username',
                  'email', 'address', 'phone_number', 'photo', 'joined_date', ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'true',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'true',
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'true',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'required': 'true',
            }),
            "address": forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'true',
            }),
            "phone_number": forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'False',
            }),
            "joined_date": forms.DateInput(attrs={
                'class': 'datepicker',
                'placeholder': 'Joined Date',
            }),
        }


class LibrarianDeleteForm(forms.ModelForm):
    class Meta:
        model = Librarian
        fields = ['deleted_at']
        widgets = {
            'deleted_at': forms.HiddenInput(),
        }


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'username',
                  'email', 'address', 'phone_number', 'photo']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'true',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'true',
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'true',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'required': 'true',
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'true',
            }),
            "phone_number": forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'False',
            }),

        }


class MemberDeleteForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['deleted_at']
        widgets = {
            'deleted_at': forms.HiddenInput(),
        }


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = Member
        fields = ['username', 'email', 'password1', 'password2', ]


class FirstLoginForm(forms.Form):
    first_name = forms.CharField(label="First Name")
    last_name = forms.CharField(label="Last Name")
    photo = forms.ImageField(label="Profile Picture", required=False)
    phone_number = forms.CharField(label="Phone Number", required=False)
    address = forms.CharField(label="Address")
    profession = forms.ModelChoiceField(label="Profession", queryset=Profession.objects.filter(
        deleted_at__isnull=True).order_by('title'))
    category_interests = forms.ModelMultipleChoiceField(
        label="Interested Categories", queryset=Category.objects.filter(deleted_at__isnull=True).order_by('title'))

    first_name.widget.attrs.update(
        {'class': 'form-control', 'required': 'True', })
    last_name.widget.attrs.update(
        {'class': 'form-control', 'required': 'True', })
    photo.widget.attrs.update({'class': 'form-control', })
    phone_number.widget.attrs.update({'class': 'form-control', })
    address.widget.attrs.update({'class': 'form-control', })
    profession.widget.attrs.update({'class': 'profession-select', })
    category_interests.widget.attrs.update({'class': 'select-multiple', })

    class Meta:
        model = Member
        fields = ['photo', 'phone_number', 'address', 'profession', 'category_interests', ]


class MemberLoginForm(forms.Form):
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


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        max_length=254, help_text='Required. Inform a valid email address.')


class NewPassword(forms.Form):
    password1 = forms.CharField(max_length=100, widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=100, widget=forms.PasswordInput)
