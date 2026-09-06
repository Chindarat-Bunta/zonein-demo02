# Obsolete migration replaced by unified schema
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0002_wishlist"),
    ]
    operations = []
