from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from userauths.models import User
from taggit.managers import TaggableManager
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.

STATUS_CHOICES = (
    ("processing", "Processing"),
    ("shipped", "Shipped"),
    ("delivered", "Delivered"),
)

STATUS = (
    ("draft", "Draft"),
    ("disabled", "Disabled"),
    ("rejected", "Rejected"),
    ("in_review", "In Review"),
    ("published", "Published"),
)

Rating = (
    (1, "★☆☆☆☆"),
    (2, "★★☆☆☆"),
    (3, "★★★☆☆"),
    (4, "★★★★☆"),
    (5, "★★★★★"),
)


def user_directory_path(instance, filename):
    return "user_{0}/{1}".format(instance.user.id, filename)


class Category(models.Model):
    cid = ShortUUIDField(
        unique=True, length=10, max_length=20, prefix="cat", alphabet="abcdef12345"
    )
    title = models.CharField(max_length=100, default="Food")
    image = models.ImageField(upload_to="category", default="category.jpg")

    class Meta:
        verbose_name_plural = "Categories"

    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title


class Tags(models.Model):
    pass


class Vendor(models.Model):
    vid = ShortUUIDField(
        unique=True, length=10, max_length=20, prefix="ven", alphabet="abcdef12345"
    )
    title = models.CharField(max_length=100, default="Automated Vendor Title")
    cover_image = models.ImageField(upload_to=user_directory_path, default="vendor.jpg")
    image = models.ImageField(upload_to=user_directory_path, default="vendor.jpg")
    description = RichTextUploadingField(
        null=True, blank=True, default="This is Vendor Desc."
    )

    address = models.CharField(max_length=100, default="Samras Boyz, BK-385566")
    contact = models.CharField(max_length=100, default="+91 6359970942")
    chat_res_time = models.CharField(max_length=100, default="100")
    shipping_on_time = models.CharField(max_length=100, default="100")
    authentic_rating = models.CharField(max_length=100, default="100")
    days_return = models.CharField(max_length=100, default="100")
    warranty_period = models.CharField(max_length=100, default="100")

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Vendor"

    def vendor_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title


class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdef12345")

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="category"
    )
    vendor = models.ForeignKey(
        Vendor, on_delete=models.SET_NULL, null=True, related_name="vendor"
    )

    title = models.CharField(max_length=100, default="Automated Type")
    image = models.ImageField(upload_to=user_directory_path, default="product.jpg")
    description = RichTextUploadingField(
        null=True, blank=True, default="This is Product Desc."
    )

    price = models.DecimalField(
        max_digits=999999999999999, decimal_places=2, default="199"
    )
    old_price = models.DecimalField(
        max_digits=999999999999999, decimal_places=2, default="299"
    )

    specifications = RichTextUploadingField(
        null=True, blank=True, default="This is Automated specs."
    )
    type = models.CharField(
        max_length=100, default="Automated Title", blank=True, null=True
    )
    life = models.CharField(max_length=100, default="100 Days", blank=True, null=True)
    stock_count = models.PositiveIntegerField(default="7", blank=True, null=True)
    mfd = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    tags = TaggableManager(blank=True)

    product_status = models.CharField(
        choices=STATUS, max_length=10, default="in_review"
    )

    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    digital = models.BooleanField(default=False)

    sku = ShortUUIDField(
        unique=True, length=4, max_length=10, prefix="sku", alphabet="1234567890"
    )

    date = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Product"

    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title

    def get_percentage(self):
        new_price = (self.price / self.old_price) * 100
        return new_price


class ProductImages(models.Model):
    images = models.ImageField(upload_to="product-image", default="product.jpg")
    product = models.ForeignKey(
        Product, related_name="p_images", on_delete=models.SET_NULL, null=True
    )
    date = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name_plural = "Product Images"


######################### Cart, order, order item and address ########################
######################### Cart, order, order item and address ########################
######################### Cart, order, order item and address ########################


class CartOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(
        max_digits=999999999999999, decimal_places=2, default="199"
    )
    paid_status = models.BooleanField(default=False)
    order_date = models.DateTimeField(
        auto_now_add=True,
    )
    product_status = models.CharField(
        choices=STATUS_CHOICES, max_length=30, default="processing"
    )

    class Meta:
        verbose_name_plural = "Cart Order"


class CartOrderItems(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length=200)
    product_status = models.CharField(max_length=200)
    item = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    qty = models.IntegerField(default=0)
    price = models.DecimalField(
        max_digits=999999999999999, decimal_places=2, default="199"
    )
    total = models.DecimalField(
        max_digits=999999999999999, decimal_places=2, default="199"
    )

    class Meta:
        verbose_name_plural = "Cart Order Items"

    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def order_img(self):
        return mark_safe(
            '<img src="/media/%s" width="50" height="50" />' % (self.image)
        )


######################### Product review, whishlilst, address ########################
######################### Product review, whishlilst, address ########################
######################### Product review, whishlilst, address ########################


class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, related_name="reviews"
    )
    review = models.TextField()
    rating = models.IntegerField(choices=Rating, default=None)
    date = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name_plural = "Product Reviews"

    def __str__(self):
        return self.product.title

    def get_rating(self):
        return self.rating


class wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name_plural = "Wishlists"

    def __str__(self):
        return self.product.title


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=100, null=True)
    mobile = models.CharField(max_length=30, null=True)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Address"
