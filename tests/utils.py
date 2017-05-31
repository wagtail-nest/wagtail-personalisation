from django.template import engines
from django.contrib.sessions.middleware import SessionMiddleware


def render_template(value, **context):
    template = engines['django'].from_string(value)
    request = context.pop('request', None)
    return template.render(context, request)


def add_session_to_request(request):
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()