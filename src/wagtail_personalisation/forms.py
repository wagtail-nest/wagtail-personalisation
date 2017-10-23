from importlib import import_module

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.test.client import RequestFactory
from django.utils import timezone
from django.utils.lru_cache import lru_cache
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

        rules = [form for formset in self.formsets.values() for form in formset if form not in formset.deleted_forms]
        consistent = rules and all(rule.instance.static for rule in rules)

        from .models import Segment
        if cleaned_data.get('type') == Segment.TYPE_STATIC and not cleaned_data.get('count') and not consistent:
            raise ValidationError({
                'count': ('Static segments with non-static compatible rules must include a count.'),
            })

        return cleaned_data

    def save(self, *args, **kwargs):
        instance = super(SegmentAdminForm, self).save(*args, **kwargs)

        if instance.can_populate:
            request = RequestFactory().get('/')

            for session in Session.objects.filter(expire_date__gt=timezone.now()).iterator():
                session_data = session.get_decoded()
                user = user_from_data(session_data.get('_auth_id'))
                request.user = user
                request.session = SessionStore(session_key=session.session_key)
                all_pass = all(rule.test_user(request) for rule in instance.get_rules() if rule.static)
                if all_pass:
                    instance.sessions.add(session)

        instance.frozen = True
        instance.save()
        return instance
