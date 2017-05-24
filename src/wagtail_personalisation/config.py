from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class WagtailPersonalisationConfig(AppConfig):
    label = 'wagtail_personalisation'
    name = 'wagtail_personalisation'
    verbose_name = _('Wagtail Personalisation')

    def ready(self):
        from wagtail_personalisation import receivers

        receivers.register()
