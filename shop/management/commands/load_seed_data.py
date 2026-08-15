import os
from django.core.management.base import BaseCommand
from django.core.files import File
from shop.models import Category, Product


class Command(BaseCommand):
    help = 'Load all product data for Janatha Syrup with standard pricing (Rs 150, offer Rs 105, 750ml)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Updating all products to Rs. 150 (Offer Rs. 105, 750ml)...')

        # ─── Categories ──────────────────────────────
        nannari, _ = Category.objects.get_or_create(
            slug='nannari',
            defaults={
                'name': 'Nannari Syrups',
                'description': 'Traditional Sarasaparilla root syrup — a beloved South Indian favorite.',
            }
        )

        rose, _ = Category.objects.get_or_create(
            slug='rose',
            defaults={
                'name': 'Rose Syrups',
                'description': 'Fragrant rose-flavored syrup crafted with real rose extracts.',
            }
        )

        crushes, _ = Category.objects.get_or_create(
            slug='fruit-crushes',
            defaults={
                'name': 'Fruit Crushes',
                'description': 'Rich and delicious fruit crushes made with real fruit pulp.',
            }
        )

        specialty, _ = Category.objects.get_or_create(
            slug='specialty',
            defaults={
                'name': 'Specialty Syrups',
                'description': 'Unique flavors and special editions for desserts, ice creams, and drinks.',
            }
        )

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {Category.objects.count()} categories'))

        # ─── Standardized Products Data ──────────────
        # Price: Rs.150, Offer: Rs.105 (30% OFF), Size: 750ml
        products_data = [
            {
                'name': 'Janatha Nannari Syrup',
                'slug': 'janatha-nannari-syrup',
                'category': nannari,
                'description': 'The iconic Janatha Nannari Syrup — made from natural Sarasaparilla root extract. Mix with cold water and lemon for instant refreshment.',
                'ingredients': 'Water, Sugar, Sarasaparilla (Nannari) root extract, Citric acid, Sodium benzoate.',
                'price': 150,
                'discount_price': 105,
                'size': '750ml',
                'featured': True,
                'image_filename': 'Janatha Nannari Syrup Image.png',
            },
            {
                'name': 'Janatha Sarasaparilla Syrup',
                'slug': 'janatha-sarasaparilla-syrup',
                'category': nannari,
                'description': 'Premium golden Sarasaparilla syrup crafted from selected Nannari roots for a delicate, aromatic taste.',
                'ingredients': 'Water, Sugar, Natural Sarasaparilla root extract, Citric acid, Sodium benzoate.',
                'price': 150,
                'discount_price': 105,
                'size': '750ml',
                'featured': True,
                'image_filename': 'SARASAPARILLA SYRUP.png',
            },
            {
                'name': 'Janatha Rose Syrup',
                'slug': 'janatha-rose-syrup',
                'category': rose,
                'description': 'Crafted with fragrant rose extracts. Perfect for making rose milk, falooda, lassi, or dessert toppings.',
                'ingredients': 'Water, Sugar, Rose extract, Permitted food color, Citric acid, Sodium benzoate.',
                'price': 150,
                'discount_price': 105,
                'size': '750ml',
                'featured': True,
                'image_filename': 'rose_syrup.png',
            },
            {
                'name': 'Janatha Mango Crush',
                'slug': 'janatha-mango-crush',
                'category': crushes,
                'description': 'Luscious mango crush made with juicy mango pulp. Delicious in milkshakes, mocktails, and ice creams.',
                'ingredients': 'Mango pulp, Sugar, Water, Citric acid, Permitted food color, Sodium benzoate.',
                'price': 150,
                'discount_price': 105,
                'size': '750ml',
                'featured': True,
                'image_filename': 'mango_crush.png',
            },
            {
                'name': 'Janatha Orange Crush',
                'slug': 'janatha-orange-crush',
                'category': crushes,
                'description': 'Tangy and sweet orange crush packed with citrus flavor. Great for slushes, sodas, and coolers.',
                'ingredients': 'Orange pulp & juice extract, Sugar, Water, Citric acid, Sodium benzoate.',
                'price': 150,
                'discount_price': 105,
                'size': '750ml',
                'featured': True,
                'image_filename': 'ORANGE_CRUSH.png',
            },
            {
                'name': 'Janatha Pineapple Crush',
                'slug': 'janatha-pineapple-crush',
                'category': crushes,
                'description': 'Tropical pineapple crush with rich pineapple taste. Perfect for refreshing summer drinks and dessert toppings.',
                'ingredients': 'Pineapple pulp, Sugar, Water, Citric acid, Sodium benzoate.',
                'price': 150,
                'discount_price': 105,
                'size': '750ml',
                'featured': True,
                'image_filename': 'PINEAPPLE_CRUSH.png',
            },
            {
                'name': 'Janatha Grape Crush',
                'slug': 'janatha-grape-crush',
                'category': crushes,
                'description': 'Rich black grape crush bursting with authentic fruity sweetness. A crowd favorite for juice bars and home drinks.',
                'ingredients': 'Grape extract, Sugar, Water, Citric acid, Sodium benzoate.',
                'price': 150,
                'discount_price': 105,
                'size': '750ml',
                'featured': True,
                'image_filename': 'GRAPE_CRUSH.png',
            },
            {
                'name': 'Janatha Ice Cream Syrup',
                'slug': 'janatha-icecream-syrup',
                'category': specialty,
                'description': 'Vibrant green syrup designed specially for falooda, ice cream sundaes, and chilled milk drinks.',
                'ingredients': 'Water, Sugar, Permitted flavors & colors, Citric acid, Sodium benzoate.',
                'price': 150,
                'discount_price': 105,
                'size': '750ml',
                'featured': True,
                'image_filename': 'ICECREAM_SYRUP.png',
            },
        ]

        from django.conf import settings
        img_dir = os.path.join(settings.BASE_DIR, 'products', 'product_image')

        # Clean existing products to avoid duplicates
        Product.objects.all().delete()

        for data in products_data:
            image_filename = data.pop('image_filename')
            product = Product.objects.create(**data)

            # Assign image
            image_path = os.path.join(img_dir, image_filename)
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    product.image.save(image_filename, File(f), save=True)

            self.stdout.write(f'  ✓ {product.name} (Rs. 150 -> Rs. 105)')

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Successfully updated database! {Product.objects.count()} products configured.'
        ))
