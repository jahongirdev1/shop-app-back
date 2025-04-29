from django.core.exceptions import ValidationError
from django.db import models


class CategoryModel(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='categories/', blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class UserModel(models.Model):
    fullName = models.CharField(max_length=255)
    phoneNumber = models.CharField(max_length=20)
    password = models.CharField(max_length=255)
    favoriteProducts = models.ManyToManyField('ProductModel', blank=True)
    orders = models.ManyToManyField('OrderModel', related_name='user_orders', blank=True)

    def __str__(self):
        return f"{self.fullName} --> {self.phoneNumber}"


class ProductModel(models.Model):
    image = models.ImageField(upload_to='products/')
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    description = models.TextField()
    category = models.ForeignKey(CategoryModel, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    status = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.category} --> {self.name}"


class OrderModel(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='order_user', default=1)
    productsList = models.ManyToManyField('ProductModel', related_name='order_product')
    description = models.TextField(default='')
    locationLink = models.URLField()
    totalPrice = models.DecimalField(max_digits=10, decimal_places=2)
    createdAt = models.DateTimeField(auto_now_add=True)
    isAccepted = models.BooleanField(default=False)
    isProcess = models.BooleanField(default=False)
    isDelivered = models.BooleanField(default=False)
    isCompleted = models.BooleanField(default=False)
    isCanceled = models.BooleanField(default=False)

    def __str__(self):
      return f"{self.user.fullName} --> № - {self.id}"

class PosterModel(models.Model):
    image = models.ImageField(upload_to='poster/', null=True)
    status = models.IntegerField(default = 0)

    def __str__(self):
      return f"{self.id}"


# class BranchModel(models.Model):
#     isOpen = models.BooleanField(default=True)
#     name = models.CharField(max_length=255)
#     address = models.CharField(max_length=255)
#     phoneNumber = models.CharField(max_length=20, blank=True, null=True)
#     email = models.EmailField(blank=True, null=True)
#     openingHours = models.CharField(max_length=100, blank=True, null=True)
#     latitude = models.FloatField(blank=True, null=True)
#     longitude = models.FloatField(blank=True, null=True)
#     status = models.IntegerField(default=0)
#
#
#     def __str__(self):
#         return f"{self.name} --> {self.address}"
#




# class SettingsModel(models.Model):
#     delivery_price_9_6 = models.IntegerField(default=0)
#     delivery_price_6_2 = models.IntegerField(default=0)
#
#     def save(self, *args, **kwargs):
#         if not self.pk and SettingsModel.objects.exists():
#             raise ValidationError("Only one instance of SettingsModel is allowed.")
#         super().save(*args, **kwargs)
#
#     def __str__(self):
#         return "Settings"
#
#

