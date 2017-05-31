try:
    from django.apps import AppConfig
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    raise ImportError(
        'You are using the `wagtail_personalisation` app which requires the `django` module.'
        'Be sure to add `django` to your INSTALLED_APPS for `wagtail_personalisation` to work properly.'
)


class WagtailPersonalisationConfig(AppConfig):
    label = 'wagtail_personalisation'
    name = 'wagtail_personalisation'
    verbose_name = _('Wagtail Personalisation')

    def ready(self):
        from wagtail_personalisation import receivers

        receivers.register()
