from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        max_length=254, unique=True, verbose_name='Адрес электронной почты'
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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['-id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='follower',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        verbose_name='Подписки',
        related_name='following',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique follow'
            ),
        )

    def __str__(self):
        return f'{self.user} - {self.author}'
