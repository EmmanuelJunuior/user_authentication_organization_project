from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        email = self.normalize_email(email)
        if not email:
            raise ValueError('The Email field must be set')
        first_name = first_name.strip()
        if not first_name:
            raise ValueError('First Name must be set')
        
        last_name = last_name.strip()
        if not last_name:
            raise ValueError('Last Name must be set')
        
        if not password:
            raise ValueError('Password must be set')
    
        user = self.model(email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None):
        user = self.create_user(email, first_name, last_name, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=25, null=False)
    last_name = models.CharField(max_length=25, null=False)
    email = models.EmailField(unique=True, null=False)
    phone = models.CharField(max_length=12, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

class Organisation(models.Model):
    name = models.CharField(max_length=255, null=False)
    id = models.AutoField(primary_key=True)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    users = models.ManyToManyField(User, related_name='organisations')

    def save(self, *args, **kwargs):
        if not self.name:
            if self.users.exists():  # Check if there are associated users
                first_user = self.users.first()
                self.name = f"{first_user.first_name}'s Organisation"
            elif self.owner:  # Fallback to owner's first name if no users are associated
                self.name = f"{self.owner.first_name}'s Organisation"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name