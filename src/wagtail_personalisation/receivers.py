from django.db.models.signals import pre_save
from django.utils import timezone

from wagtail_personalisation.models import Segment


def check_status_change(sender, instance, *args, **kwargs):
    """Check if the status has changed. Alter dates accordingly."""
    try:
        original_status = sender.objects.get(pk=instance.id).status
    except sender.DoesNotExist:
        original_status = ""

    if original_status != instance.status:
        if instance.status == instance.STATUS_ENABLED:
            instance.enable_date = timezone.now()
            instance.visit_count = 0
            return instance
        if instance.status == instance.STATUS_DISABLED:
            instance.disable_date = timezone.now()


def register():
    pre_save.connect(check_status_change, sender=Segment)
