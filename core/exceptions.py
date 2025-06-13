from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        data = response.data
        # DRF 3.14+ wraps errors differently; handle both cases:
        message = data.get('detail') if isinstance(data, dict) else None
        response.data = {
            'error': {
                'code': response.status_code,
                'message': message or data,
                'details': data
            }
        }
    else:
        response = Response({
            'error': {
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'Internal server error',
                'details': str(exc)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return response
