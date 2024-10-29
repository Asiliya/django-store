from django.contrib import auth, messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, TemplateView, UpdateView

from common.views import TitleMixin
from products.models import Basket
from users.forms import UserLoginForm, UserRegistrationForm, UserProfileForm, MyPasswordChangeForm
from users.models import User, EmailVerification


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = UserLoginForm

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_verified_email:
            messages.error(self.request, ('Ваш акаунт не підтверджено. Будь ласка, перевірте вашу пошту.'))
            return redirect(reverse_lazy('users:login'))
        return super().form_valid(form)


class UserRegistrationView(TitleMixin, SuccessMessageMixin, CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/registration.html'
    success_url = reverse_lazy('users:login')
    success_message = 'Вітаємо! Ви успішно зареєструвалися!'
    title = 'ModaMix - Реєстрація'


class EmailVerificationView(TitleMixin, TemplateView):
    title = 'Store - підтвердження електронної пошти'
    template_name = 'users/email_verification.html'

    def get(self, request, *args, **kwargs):
        code = kwargs['code']
        user = User.objects.get(email=kwargs['email'])
        email_verifications = EmailVerification.objects.filter(user=user, code=code)
        if email_verifications.exists():
            verification_record = email_verifications.first()

            if verification_record.is_expired():
                user.is_verified_email = True
                user.save()
                return super(EmailVerificationView, self).get(request, *args, **kwargs)
            else:
                messages.error(request, 'Термін дії посилання для підтвердження минув. Ваш обліковий запис видалено.')
                user.delete()
                email_verifications.delete()
                return HttpResponseRedirect(reverse('index'))
        else:
            print(code)
            print(user)
            return HttpResponseRedirect(reverse('index'))


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))


class UserProfileView(UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('users:profile')

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data()
        context['title'] = 'ModaMix - Профіль'
        context['baskets'] = Basket.objects.filter(user=self.request.user)
        baskets = Basket.objects.filter(user=self.request.user)
        context['total_sum'] = sum(basket.sum() for basket in baskets)
        context['total_quantity'] = sum(basket.quantity for basket in baskets)
        return context


class UserPasswordChange(PasswordChangeView):
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy("users:password_change_done")
    template_name = 'users/password_change.html'