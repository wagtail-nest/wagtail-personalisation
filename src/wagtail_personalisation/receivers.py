try:
    from django.db.models.signals import pre_save
    from django.utils import timezone
except ImportError:
    raise ImportError(
        'You are using the `wagtail_personalisation` app which requires the `django` module.'
        'Be sure to add `django` to your INSTALLED_APPS for `wagtail_personalisation` to work properly.'
)

from wagtail_personalisation.models import Segment


def check_status_change(sender, instance, *args, **kwargs):
    """Check if the status has changed. Alter dates accordingly."""
    try:
        original_status = sender.objects.get(pk=instance.id).status
    except sender.DoesNotExist:
        original_status = ""

    if original_status != instance.status:
        if instance.status == "enabled":
            instance.enable_date = timezone.now()
            instance.visit_count = 0
            return instance
        if instance.status == "disabled":
            instance.disable_date = timezone.now()


def register():
    pre_save.connect(check_status_change, sender=Segment)
