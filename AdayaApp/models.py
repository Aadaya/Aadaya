from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from ckeditor.fields import RichTextField

# Create your models here.
from django.urls import reverse
from django.utils import timezone


class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an email address')

        if not username:
            raise ValueError('User must have an username')
        now = timezone.now()
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_active = False
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True

        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)

    # required
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    objects = MyAccountManager()

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True


RETAILER_CHOICES = (
    ("Hospital Pharmacy", "Hospital Pharmacy"),
    ("Medical Store", "Medical Store"),
    ("Chain Pharmacy", "Chain Pharmacy"),
    ("FMCG", "FMCG"),
    ("Others", "Others"),

)

DISTRICT_CHOICES = (
    ('Alappuzha', 'Alappuzha'),
    ('Ernakulam', 'Ernakulam'),
    ('Idukki', 'Idukki'),
    ('Kannur', 'Kannur'),
    ('Kasaragod', 'Kasaragod'),
    ('Kollam', 'Kollam'),
    ('Kottayam', 'Kottayam'),
    ('Kozhikode', 'Kozhikode'),
    ('Malappuram', 'Malappuram'),
    ('Palakkad', 'Palakkad'),
    ('Pathanamthitta', 'Pathanamthitta'),
    ('Thrissur', 'Thrissur'),
    ('Wayanad', 'Wayanad'),

)


class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, null=True)
    owner_name = models.CharField('Owner Name', max_length=6, null=True)
    state = models.CharField("State", default='Kerala', max_length=20)
    district = models.CharField("District", choices=DISTRICT_CHOICES, max_length=20)
    landmark = models.CharField("Landmark", max_length=50, blank=True)
    retailer_type = models.CharField('Retailer Type', max_length=20, choices=RETAILER_CHOICES)
    dl_number1 = models.CharField('DL Number2', max_length=20)
    dl_number2 = models.CharField('DL Number2', max_length=20)
    dl_expiry_date = models.DateField('DL Expiry Date')
    gst = models.CharField('GST', max_length=20)
    phone = models.CharField("Phone", max_length=50, blank=True)

    retailer_name = models.CharField('Retailer Name', max_length=20)

    joined_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.retailer_name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Contact(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def get_url(self):
        return reverse('products_by_category', args=[self.slug])

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.category_name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    drug_code = models.CharField(max_length=20)
    brand_name = models.CharField(max_length=50, null=True)
    company_name = models.CharField(max_length=50, null=True)
    pack = models.CharField(max_length=50, null=True)
    product_name = models.CharField(max_length=100)
    batch = models.CharField(max_length=100)
    expiry_date = models.DateField()
    unit_quantity = models.IntegerField()
    MRP = models.FloatField()
    Rate = models.FloatField()
    stock = models.IntegerField()
    gst18 = models.BooleanField(default=False)
    gst15 = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name


class Notification(models.Model):
    heading = models.CharField(max_length=50)
    description = RichTextField()
    date = models.DateField()


class TermsAndConditions(models.Model):
    heading = models.CharField(max_length=50)
    description = RichTextField()
    date = models.DateField()
