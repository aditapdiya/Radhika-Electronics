from django.apps import AppConfig

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        import main.signals 



from django.contrib.auth import get_user_model
from main.models import UserProfile

User = get_user_model()

if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='Admin@123'
    )

    UserProfile.objects.create(
        user=user,
        mobile='9876543210',
        address='Admin Address'
    )