# myproject/context_processors.py

from django.conf import settings

def site_domain(request):
    return {
        'site_domain': settings.SITE_DOMAIN,
    }
