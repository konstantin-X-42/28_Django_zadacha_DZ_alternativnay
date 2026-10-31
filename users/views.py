import secrets

from django.conf import settings  # <-- ПРАВИЛЬНЫЙ ИМПОРТ НАСТРОЕК DJANGO
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView

from users.forms import UserRegisterForm
from users.models import User


class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        user.is_active = True # Активируем пользователя сразу при создании!  #False  # Блокируем до подтверждения почты
        # token = secrets.token_hex(16)
        # user.token = token
        user.save()

        # host = self.request.get_host()
        # url = f"http://{host}/users/email-confirm/{token}/"
        #
        # # Безопасная отправка: использует console.EmailBackend и глушит любые системные ошибки SSL
        # send_mail(
        #     subject="Подтверждение почты",
        #     message=f"Привет, перейди по ссылке для подтверждения почты {url}",
        #     from_email=settings.DEFAULT_FROM_EMAIL,  # <-- Берем адрес через settings
        #     recipient_list=[user.email],
        #     fail_silently=True,  # <-- Игнорируем любые капризы Windows с сертификатами
        # )
        return super().form_valid(form)


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()  # Сохраняем изменения в базу данных
    return redirect(reverse("users:login"))  # Перенаправляем на страницу входа





#-------------------------писал по видео --------------------------------
# import secrets
#
# from django.core.mail import send_mail
# from django.urls import reverse_lazy
# from django.views.generic import CreateView
#
# from users.forms import UserRegisterForm
# from users.models import User
# from config.settings import EMAIL_HOST_USER
# from django.shortcuts import get_object_or_404, redirect
# from django.urls import reverse
#
#
# class UserCreateView(CreateView):
#     model = User
#     form_class = UserRegisterForm
#     success_url = reverse_lazy('users:login')
#
#     def form_valid(self, form):
#         user = form.save()
#         user.is_active = False
#         token = secrets.token_hex(16)
#         user.token = token
#         user.save()
#         host = self.request.get_host()
#         url = f'http://{host}/users/email-confirm/{token}/'
#         send_mail(
#             subject="Подтверждение почты",
#             message=f"Привет, перейди по ссылке для подтверждения почты {url}",
#             from_email=EMAIL_HOST_USER,
#             recipient_list=[user.email]
#         )
#         return super().form_valid(form)
#
#
# def email_verification(request, token):
#     user = get_object_or_404(User, token=token)
#     user.is_active = True
#     user.save()  # <-- Обязательно сохраняем изменения в базу данных!
#     return redirect(reverse("users:login"))  # <-- Перенаправляем на страницу входа
