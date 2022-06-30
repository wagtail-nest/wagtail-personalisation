from django import VERSION as DJANGO_VERSION
from django.apps import AppConfig

if DJANGO_VERSION >= (3, 0):
    from django.utils.translation import gettext_lazy as _
else:
    from django.utils.translation import ugettext_lazy as _


class WagtailPersonalisationConfig(AppConfig):
    label = "wagtail_personalisation"
    name = "wagtail_personalisation"
    verbose_name = _("Wagtail Personalisation")

    def ready(self):
        from wagtail_personalisation import receivers

        receivers.register()
