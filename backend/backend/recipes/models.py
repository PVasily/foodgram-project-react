from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

from .validators import UsernameValidator


User = get_user_model()

# class User(AbstractUser):
#     username_validator = UsernameValidator()
#     username = models.CharField(
#         validators=(username_validator,),
#         max_length=150,
#         unique=True,
#         blank=False,
#         null=False
#     )
#     email = models.EmailField(
#         max_length=255,
#         unique=True,
#         blank=False,
#         null=False
#     )
#     first_name = models.CharField(
#         'Имя',
#         max_length=150,
#         blank=True
#     )
#     last_name = models.CharField(
#         'Фамилия',
#         max_length=150,
#         blank=True
#     )
#     is_subscribed = models.BooleanField(default=False)

#     class Meta:
#         ordering = ('id',)
#         verbose_name = 'Пользователь'
#         verbose_name_plural = 'Пользователи'

#     def __str__(self):
#         return self.username

class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
