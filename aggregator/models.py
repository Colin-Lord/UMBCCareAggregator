from django.contrib.auth.models import AbstractUser
from django.db import models

class Office(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    email = models.EmailField(unique=True)
    office = models.ForeignKey(
        Office,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username']