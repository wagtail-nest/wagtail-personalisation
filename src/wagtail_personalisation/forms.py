from __future__ import absolute_import, unicode_literals

from datetime import datetime
from importlib import import_module
from itertools import takewhile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.test.client import RequestFactory
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
        return AnonymousUser()


class SegmentAdminForm(WagtailAdminModelForm):

    def count_matching_users(self, rules, match_any):
        """ Calculates how many users match the given static rules
        """
        count = 0

        static_rules = [rule for rule in rules if rule.static]

        if not static_rules:
            return count

        User = get_user_model()
        users = User.objects.filter(is_active=True, is_staff=False)

        for user in users.iterator():
            if match_any:
                if any(rule.test_user(None, user) for rule in static_rules):
                    count += 1
            elif all(rule.test_user(None, user) for rule in static_rules):
                count += 1

        return count

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

        if self.instance.id and self.instance.is_static:
            if self.has_changed():
                self.add_error_to_fields(self, excluded=['name', 'enabled'])

            for formset in self.formsets.values():
                if formset.has_changed():
                    for form in formset:
                        if form not in formset.deleted_forms:
                            self.add_error_to_fields(form)

        return cleaned_data

    def add_error_to_fields(self, form, excluded=list()):
        for field in form.changed_data:
            if field not in excluded:
                form.add_error(field, _('Cannot update a static segment'))

    def save(self, *args, **kwargs):
        is_new = not self.instance.id

        if not self.instance.is_static:
            self.instance.count = 0

        if is_new:
            rules = [
                form.instance for formset in self.formsets.values()
                for form in formset
                if form not in formset.deleted_forms
            ]
            self.instance.matched_users_count = self.count_matching_users(
                rules, self.instance.match_any)
            self.instance.matched_count_updated_at = datetime.now()

        instance = super(SegmentAdminForm, self).save(*args, **kwargs)

        if is_new and instance.is_static and instance.all_rules_static:
            from .adapters import get_segment_adapter

            request = RequestFactory().get('/')
            request.session = SessionStore()
            adapter = get_segment_adapter(request)

            users_to_add = []
            users_to_exclude = []
            sessions = Session.objects.iterator()
            take_session = takewhile(
                lambda x: instance.count == 0 or len(users_to_add) <= instance.count,
                sessions
            )
            for session in take_session:
                session_data = session.get_decoded()
                user = user_from_data(session_data.get('_auth_user_id'))
                if user.is_authenticated():
                    request.user = user
                    request.session = SessionStore(session_key=session.session_key)
                    passes = adapter._test_rules(instance.get_rules(), request, instance.match_any)
                    if passes and instance.randomise_into_segment():
                        users_to_add.append(user)
                    elif passes:
                        users_to_exclude.append(user)

            instance.static_users.add(*users_to_add)
            instance.excluded_users.add(*users_to_exclude)

        return instance

    @property
    def media(self):
        media = super(SegmentAdminForm, self).media
        media.add_js(
            [static('js/segment_form_control.js')]
        )
        return media
