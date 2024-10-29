from cProfile import label

from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm, PasswordChangeForm
from django import forms
import uuid
from datetime import timedelta
from users.tasks import send_email_verification
from django.core.exceptions import ValidationError
from django.http import request, HttpResponseRedirect
from django.urls import reverse
from django.utils.timezone import now
# from users.tasks import send_email_verification
from .models import User, EmailVerification


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control py-4',
        'placeholder': 'Введіть імя користувача:',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control py-4',
        'placeholder': 'Введіть пароль користувача:',
    }))

    class Meta:
        model = User
        fields = ('username', 'password')


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control py-4',
        'placeholder': 'Введіть імя:',
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control py-4',
        'placeholder': 'Введіть фамілію:',
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control py-4',
        'placeholder': 'Введіть імя користувача:',
    }))
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'form-control py-4',
        'placeholder': 'Введіть E-mail:',
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control py-4',
        'placeholder': 'Введіть пароль:',
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control py-4',
        'placeholder': 'Підтвердіть пароль:',
    }))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')

    def save(self, commit=True): # методпри збереженні форми, який викликається
        user = super(UserRegistrationForm, self).save(commit=True) # щоб те шо ми переоприділили виконалося, а далі наш код
        # expiration = now() + timedelta(hours=48)  # ми беремо той час який зараз і добавляємо до нього 48 годин, щоб посилання працювало два дні
        # expiration = now() + timedelta(minutes=1)
        # record = EmailVerification.objects.create(code=uuid.uuid4(), user=user, expiration=expiration)
        # record.send_verification_email()
        send_email_verification.delay(user.id) # виконуємо в фоні
        return user


class UserProfileForm(UserChangeForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control py-4',}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control py-4',}))
    image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'custom-file-input'}), required=False)
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control py-4', 'readonly': True}))
    email = forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control py-4', 'readonly': True}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'image', 'username', 'email')


class MyPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control py-4'}), label='Старий пароль')
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control py-4'}), label='Новий пароль')
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control py-4'}), label='Повторіть новий пароль')

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')