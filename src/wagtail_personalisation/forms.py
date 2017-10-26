from __future__ import absolute_import, unicode_literals

from importlib import import_module

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.test.client import RequestFactory
from django.utils import timezone
from django.utils.lru_cache import lru_cache
from django.utils.translation import ugettext_lazy as _
from wagtail.wagtailadmin.forms import WagtailAdminModelForm



SessionStore = import_module(settings.SESSION_ENGINE).SessionStore


@lru_cache(maxsize=1000)
def user_from_data(user_id):
    User = get_user_model()
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser



class SegmentAdminForm(WagtailAdminModelForm):
    def clean(self):
        cleaned_data = super(SegmentAdminForm, self).clean()
        Segment = self._meta.model

        rules = [
            form.instance for formset in self.formsets.values()
            for form in formset
            if form not in formset.deleted_forms
        ]
        consistent = rules and Segment.all_static(rules)

        if cleaned_data.get('type') == Segment.TYPE_STATIC and not cleaned_data.get('count') and not consistent:
            self.add_error('count', _('Static segments with non-static compatible rules must include a count.'))

        return cleaned_data

    def save(self, *args, **kwargs):
        is_new = not self.instance.id

        instance = super(SegmentAdminForm, self).save(*args, **kwargs)

        if is_new and instance.is_static and instance.all_rules_static:
            from .adapters import get_segment_adapter

            request = RequestFactory().get('/')
            request.session = SessionStore()
            adapter = get_segment_adapter(request)

            for session in Session.objects.filter(expire_date__gt=timezone.now()).iterator():
                session_data = session.get_decoded()
                user = user_from_data(session_data.get('_auth_id'))
                request.user = user
                request.session = SessionStore(session_key=session.session_key)
                passes = adapter._test_rules(instance.get_rules(), request, instance.match_any)
                if passes:
                    instance.sessions.add(session)

        return instance
