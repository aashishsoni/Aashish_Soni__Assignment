from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    def _create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        # extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()


class UserProfile(models.Model):
    user = models.ForeignKey(User, related_name='Userdetails', on_delete=models.CASCADE)
    mobile = models.CharField(max_length=200, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    full_name = models.CharField(max_length=200, blank=True, null=True)
    profile_image = models.ImageField(upload_to='user_avatar', default='logo.jpeg')

    def save(self, *args, **kwargs):
        """ for user full name """
        self.full_name = self.user.first_name + ' ' + self.user.last_name
        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.full_name)



@receiver(post_save, sender=User)
def create_auth_token(instance=None, created=False, **kwargs):
    """ create user token """
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_user_details(sender, instance, created, **kwargs):
    """ creating user profile instance of user """
    if created:
        UserProfile.objects.create(user=instance, full_name=instance.first_name + ' ' + instance.last_name)
