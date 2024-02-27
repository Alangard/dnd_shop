from django.conf import settings

def paypal_context(request):
    return {
        'PAYPAL_CLIENT_ID': settings.PAYPAL_CLIENT_ID,
    }