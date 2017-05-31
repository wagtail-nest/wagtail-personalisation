from django.template import engines


def render_template(value, **context):
    template = engines['django'].from_string(value)
    request = context.pop('request', None)
    return template.render(context, request)
