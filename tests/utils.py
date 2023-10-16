from django.template import engines


def render_template(value, **context):
    template = engines["django"].from_string(value)
    request = context.pop("request", None)
    return template.render(context, request)


def get_custom_ip(request):
    return "123.123.123.123"
