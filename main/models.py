"""Models

Contain classes describe DB models.
"""
from typing import Optional, Any

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.dispatch import receiver
from django.db.models.signals import post_save

from mptt.models import MPTTModel, TreeForeignKey
from ckeditor.fields import RichTextField

from py_dev_user.utilities import get_timestamp_path


class CategoryModel(MPTTModel):
    """Category model

    :param name: category name
    :type name: str
    :param parent: parent category
    :type parent: int
    :param published: publish category or no
    :type published: bool, defaults to True
    """
    name = models.CharField(max_length=100, verbose_name='Name')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',
                            verbose_name='Parent category')
    published = models.BooleanField(verbose_name='Published', default=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Category'


class TagModel(models.Model):
    """Tag model

    :param tag: tag name
    :type tag: str
    :param published: published tag or no
    :type published: bool, defaults to True
    """
    tag = models.CharField(max_length=50, verbose_name='Tag')
    published = models.BooleanField(verbose_name='Published', default=True)

    def __str__(self) -> str:
        return self.tag

    class Meta:
        verbose_name = 'Tag'


class CurrencyModel(models.Model):
    """Currency model

    :param full_name: full name of currency
    :type full_name: str
    :param short_name: short name of currency
    :type short_name: str
    """
    full_name = models.CharField(max_length=25, verbose_name='Полное имя')
    short_name = models.CharField(max_length=5, verbose_name='Короткое имя')

    def __str__(self) -> str:
        return self.short_name

    class Meta:
        verbose_name = 'Currency'


class SellerModel(User):
    """Seller model

    Model extend the User model.
    :param phone: phone number
    :type phone: str
    """
    phone = models.CharField(max_length=25, verbose_name='Phone', null=True, blank=True)

    class Meta:
        verbose_name = 'Seller'


class ItemModel(models.Model):
    """Item model

    Discribe of some Item.
    :param short_name: item name
    :type short_name: str
    :param description: item description
    :type description: RichText object
    :param image: avatar
    :type image: Image object
    :param tag: Tag
    :type tag: Tag model object
    :param seller: Seller
    :type seller: Seller model object
    :param category: Category
    :type category: Category model object
    :param price: item price
    :type price: float
    :param currency: Currency
    :type currency: Currency model object
    :param published: published item or no
    :type published: bool, defaults to True
    :param in_stock: item present n stock or no
    :type in_stock: bool, defaults to True
    :param item_create: when item was created
    :type item_create: datetime, defaults on auto add now
    :param item_update: when item was updated
    :type item_update: datetime, defaults on auto now
    """
    short_name = models.CharField(max_length=100, verbose_name='Object name', db_index=True)
    description = RichTextField()
    image = models.ImageField(verbose_name='Image', blank=True, null=True, upload_to=get_timestamp_path)
    tag = models.ManyToManyField(TagModel, blank=True)
    seller = models.ForeignKey(SellerModel, on_delete=models.CASCADE)
    category = models.ForeignKey(CategoryModel, on_delete=models.SET_NULL, blank=True, null=True)
    price = models.FloatField(verbose_name='Price', default=0.0)
    currency = models.ForeignKey(CurrencyModel, on_delete=models.SET_NULL, blank=True, null=True)
    published = models.BooleanField(verbose_name='Published', default=True)
    in_stock = models.BooleanField(verbose_name='In stock', default=True)
    item_create = models.DateTimeField(auto_now_add=True, verbose_name='created')
    item_update = models.DateTimeField(auto_now=True, verbose_name='updated')

    def __str__(self) -> str:
        return self.short_name

    def delete(self, *args: tuple, **kwargs: dict) -> None:
        for ai in self.additionalimage_set.all():
            ai.delete()

        super().delete(*args, **kwargs)

    def get_absolute_url(self) -> Optional[str]:
        return reverse('item_detail', args=[str(self.id)])

    class Meta:
        verbose_name = 'Item'
        ordering = ['-item_create']


class AdditionalImage(models.Model):
    """Additional images model

    :param item: Item
    :type item: Item model object
    :param image: additional image of item
    :type image: Image
    """
    item = models.ForeignKey(ItemModel, on_delete=models.CASCADE, verbose_name='Item')
    image = models.ImageField(upload_to=get_timestamp_path, verbose_name='Image')

    def __str__(self) -> str:
        return self.image.name

    class Meta:
        verbose_name = 'Additional imge'
        verbose_name_plural = 'Additional images'


class Subscriber(models.Model):
    """Subscriber model

    :param user: subscriber
    :type user: ref to User model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.user.username


class ItemReports(models.Model):
    """Item report model

    :param item: Item
    :type item: Item model object
    :param is_send: flag - information was sent or no
    :type is_send: bool, defaults on False
    """
    item = models.OneToOneField(ItemModel, on_delete=models.CASCADE)
    is_send = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.item.short_name

    class Meta:
        verbose_name = 'Item report'
        ordering = ['-is_send']


class SMSLog(models.Model):
    """SMS log model

    :paran user: User
    :type user: ref on User model
    :param message: message
    :type message: str
    :param response: response
    :type response: str
    :param log_created: when record was created
    :type log_created: datetime, defaults on auto add now
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=2048)
    response = models.CharField(max_length=10)
    log_create = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'SMS Log'

# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     avatar = models.ImageField(verbose_name='Avatar', blank=True, null=True, upload_to=get_timestamp_path)
#     date_of_birth = models.DateField(blank=True, null=True)
#
#     def __str__(self):
#         return ''   # self.user.username
#
#
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()


@receiver(post_save, sender=ItemModel)
def create_item_dispatcher(sender: Any, **kwargs: dict) -> None:
    """Executor of POST_SAVE signal

    :param sender: sender
    :type sender: some object
    :param kwargs: keyword arguments
    :type kwargs: dict
    :return: None
    """
    item = kwargs['instance']
    item_reports = ItemReports()
    item_reports.item = item
    item_reports.save()
