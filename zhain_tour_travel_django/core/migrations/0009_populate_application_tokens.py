import uuid
from django.db import migrations


def populate_tokens(apps, schema_editor):
    BookingInquiry = apps.get_model('core', 'BookingInquiry')

    for booking in BookingInquiry.objects.filter(application_token__isnull=True).iterator():
        booking.application_token = uuid.uuid4()
        booking.save(update_fields=['application_token'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_bookinginquiry_application_token_and_more'),
    ]

    operations = [
        migrations.RunPython(
            populate_tokens,
            migrations.RunPython.noop
        ),
    ]