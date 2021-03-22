from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    currentGame = models.ForeignKey('api.GameBoard', null=True, on_delete=models.PROTECT)
    pass