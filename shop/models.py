from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """Product categories like Nannari, Rose, Fruit syrups etc."""
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop') + f'?category={self.slug}'


class Product(models.Model):
    """Individual syrup products."""
    SIZE_CHOICES = [
        ('200ml', '200 ml'),
        ('500ml', '500 ml'),
        ('700ml', '700 ml'),
        ('750ml', '750 ml'),
        ('1L', '1 Litre'),
    ]

    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField()
    ingredients = models.TextField(blank=True, default='')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Price in INR')
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text='Discounted price in INR')
    image = models.ImageField(upload_to='products/')
    secondary_image = models.ImageField(upload_to='products/', blank=True, null=True, help_text='Secondary image displayed on hover')
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, default='700ml')
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False, help_text='Show on homepage')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.get_size_display()})'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    @property
    def effective_price(self):
        """Return discount price if available, else regular price."""
        return self.discount_price if self.discount_price else self.price

    @property
    def discount_percentage(self):
        """Calculate discount percentage."""
        if self.discount_price and self.price > 0:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0

    @property
    def average_rating(self):
        """Calculate average rating from reviews."""
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    @property
    def image_url(self):
        """Return a reliable image URL mapped to static assets on serverless environments."""
        from django.conf import settings
        mapping = {
            'ice': 'ICECREAM_SYRUP.png',
            'grape': 'GRAPE_CRUSH.png',
            'pineapple': 'PINEAPPLE_CRUSH.png',
            'orange': 'ORANGE_CRUSH.png',
            'mango': 'mango_crush.png',
            'rose': 'rose_syrup.png',
            'sarasaparilla': 'SARASAPARILLA SYRUP.png',
            'nannari': 'Janatha Nannari Syrup Image.png',
        }
        slug_lower = (self.slug or '').lower()
        name_lower = (self.name or '').lower()
        for key, filename in mapping.items():
            if key in slug_lower or key in name_lower:
                return f"{settings.STATIC_URL}images/products/{filename}"
        if self.image:
            return self.image.url
        return f"{settings.STATIC_URL}images/logo.png"

    @property
    def secondary_image_url(self):
        """Return a reliable secondary image URL."""
        from django.conf import settings
        mapping = {
            'ice': 'ICECREAM_SYRUP.png',
            'grape': 'GRAPE_CRUSH.png',
            'pineapple': 'PINEAPPLE_CRUSH.png',
            'orange': 'ORANGE_CRUSH.png',
            'mango': 'mango_crush.png',
            'rose': 'rose.png',
            'sarasaparilla': 'sarasaparilla.png',
            'nannari': 'nannari-hero.png',
        }
        slug_lower = (self.slug or '').lower()
        name_lower = (self.name or '').lower()
        for key, filename in mapping.items():
            if key in slug_lower or key in name_lower:
                return f"{settings.STATIC_URL}images/products/{filename}"
        if self.secondary_image:
            return self.secondary_image.url
        return None

    @property
    def review_count(self):
        return self.reviews.count()



class Review(models.Model):
    """Customer product reviews."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')

    def __str__(self):
        return f'{self.user.username} - {self.product.name} ({self.rating}★)'


class Order(models.Model):
    """Customer orders."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('upi', 'UPI Payment'),
        ('card', 'Credit/Debit Card'),
        ('netbanking', 'Net Banking'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.order_number} — {self.full_name}'

    def save(self, *args, **kwargs):
        if not self.order_number:
            import random
            import string
            self.order_number = 'JS' + ''.join(random.choices(string.digits, k=8))
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Individual items within an order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=300)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.product_name} x {self.quantity}'

    @property
    def subtotal(self):
        if self.price is None:
            return 0
        return self.price * self.quantity


class ContactMessage(models.Model):
    """Contact form submissions."""
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    subject = models.CharField(max_length=300)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.subject}'


class NewsletterSubscriber(models.Model):
    """Newsletter email subscribers."""
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class DeliveryOrder(Order):
    """Proxy model for delivery staff — provides a restricted admin view."""
    class Meta:
        proxy = True
        verbose_name = 'Delivery Order'
        verbose_name_plural = 'Delivery Orders'

