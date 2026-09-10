# Obsolete migration replaced by unified 0001_initial and 0002_notification
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0002_notification"),
    ]
    operations = []
