import jwt
from django.conf import settings

from ..classes.valar_response import ValarResponse


def auth_required(view_func):
    def wrapper(request, *args, **kwargs):
        payload, response = validate(request)
        if payload:
            request.user_id = payload["user_id"]
            return view_func(request, *args, **kwargs)
        else:
            return response

    return wrapper


def validate(request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, ValarResponse(False, '请登录系统', 'info', status=401)
    token = auth_header.split(" ")[1]
    if not token:
        return None, ValarResponse(False, status=401)
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload, ValarResponse(False)
    except jwt.ExpiredSignatureError:
        return None, ValarResponse(False, '状态已过期，请重新登录', 'warning', status=401)
    except jwt.InvalidTokenError:
        return None, ValarResponse(False, '错误状态，请重新登录', 'error', status=401)
