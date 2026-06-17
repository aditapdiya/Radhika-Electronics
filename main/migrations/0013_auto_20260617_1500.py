from django.db import migrations

def create_admin(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('main', 'UserProfile')

    if not User.objects.filter(username='admin').exists():
        user = User.objects.create_superuser(
            username='admin',
            email='jajsandesh@gmail.com',
            password='Sandesh@123'
        )

        UserProfile.objects.create(
            user=user,
            mobile='7841950262',
            address='Ujani, Latur, Maharashtra, India'
        )

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_order_payment_method_alter_order_status_and_more'),
    ]

    operations = [
    ]
