from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]

    email = models.EmailField(
        'Email',
        max_length=254,
        unique=True,
    )
    
    username = models.CharField(
        max_length=150, unique=True, verbose_name='Уникальный юзернейм'
    )
    first_name = models.CharField(
        max_length=150, verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150, verbose_name='Фамилия'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Пользователь'

    def __str__(self):
        return self.username