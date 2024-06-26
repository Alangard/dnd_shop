import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.


class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, phone_number, password=None):
        if not email:
            raise ValueError('User must haven an email address')
        
        if not username:
            raise ValueError('User must have an username')
        
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
            phone_number = phone_number,
        ) 

        
        user.set_password(password)
        user.save(using=self._db)
        user_profile = UserProfile(user = user)
        user_profile.save(using=self._db)
        return user
    

    def create_superuser(self, first_name, last_name, username, email, password=None, phone_number=None):

        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=self.normalize_email(email),
            password=password,
            phone_number= phone_number or f'admin_test_phone_{str(uuid.uuid4())[:8]}'
        )
        
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.is_superadmin = True
        user.save(using=self._db)
        
        return user
    



class Account(AbstractBaseUser):
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    username = models.CharField(max_length = 50, unique = True)
    email = models.EmailField(max_length = 100, unique = True)
    phone_number = models.CharField(max_length = 50, blank = True, unique = True)

    #required 
    date_joined = models.DateTimeField(auto_now_add = True)
    last_login = models.DateTimeField(auto_now_add = True)
    is_admin = models.BooleanField(default = False)
    is_staff = models.BooleanField(default = False)
    is_active = models.BooleanField(default = False)
    is_superadmin = models.BooleanField(default = False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager()

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, add_label):
        return True
    
    def full_name(self):
        return f'{self.first_name} { self.last_name}'


class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete = models.CASCADE)
    address_line_1 = models.CharField(max_length = 100, blank = True)
    address_line_2 = models.CharField(max_length = 100, blank = True)
    profile_picture = models.ImageField(upload_to = 'user_profile/', blank = True)
    city = models.CharField(max_length = 20, blank = True)
    state = models.CharField(max_length = 20, blank = True)
    country = models.CharField(max_length = 20, blank = True)

    def __str__(self):
        return f'{self.user.full_name()}'
    
    def full_address(self):
        return f'{self.country}, {self.state}, {self.city}, {self.address_line_1} { self.address_line_2}'
    
    def get_profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        else:
            return settings.STATIC_URL + 'images/avatars/avatar1.svg'

