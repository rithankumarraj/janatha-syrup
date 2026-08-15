from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from shop.models import DeliveryOrder


class Command(BaseCommand):
    help = 'Create a delivery staff user who can only update order shipping status'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username for the delivery person')
        parser.add_argument('password', type=str, help='Password for the delivery person')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']

        # Create or get the "Delivery Staff" group
        group, created = Group.objects.get_or_create(name='Delivery Staff')

        if created:
            # Grant permissions ONLY for viewing and changing orders
            ct = ContentType.objects.get_for_model(DeliveryOrder)
            view_perm = Permission.objects.get(codename='view_order', content_type=ct)
            change_perm = Permission.objects.get(codename='change_order', content_type=ct)
            group.permissions.add(view_perm, change_perm)
            self.stdout.write(self.style.SUCCESS('✅ Created "Delivery Staff" group with restricted permissions'))
        else:
            self.stdout.write('ℹ️  "Delivery Staff" group already exists')

        # Create the user
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            self.stdout.write(f'ℹ️  User "{username}" already exists, updating...')
        else:
            user = User.objects.create_user(username=username, password=password)
            self.stdout.write(self.style.SUCCESS(f'✅ Created user "{username}"'))

        # Configure user: staff access but NOT superuser
        user.is_staff = True
        user.is_superuser = False
        user.set_password(password)
        user.save()

        # Add to Delivery Staff group
        user.groups.add(group)

        self.stdout.write(self.style.SUCCESS(
            f'\n🚚 Delivery staff "{username}" is ready!\n'
            f'   Login: http://127.0.0.1:8000/admin/\n'
            f'   They can ONLY view orders and change shipping status.'
        ))
