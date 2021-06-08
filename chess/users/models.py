from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager


class MyUserManager(UserManager):
    def get_by_natural_key(self, username):
        return self.get(username__iexact=username)

    
class User(AbstractUser):
    currentGame = models.ForeignKey('api.GameBoard', null=True, on_delete=models.PROTECT)
    objects = MyUserManager()