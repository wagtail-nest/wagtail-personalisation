from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WagtailPersonalisationConfig(AppConfig):
    label = "wagtail_personalisation"
    name = "wagtail_personalisation"
    verbose_name = _("Wagtail Personalisation")
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from wagtail_personalisation import receivers

        receivers.register()
