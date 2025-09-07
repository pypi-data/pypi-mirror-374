import base64
import json

from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin

from ..auth.Authentication import validate
from ..classes.valar_response import ValarResponse


class ValarMiddleware(MiddlewareMixin):
    @staticmethod
    def process_response(request: HttpRequest, response: ValarResponse):
        auth = request.headers.get("Auth")
        if auth:
            payload, _ = validate(request)
            if not payload:
                return ValarResponse(False, '无效权限', 'error', status=403)
        if type(response) == ValarResponse:
            valar_message, valar_code = response.valar_message, response.valar_code
            data = {
                'payload': json.loads(response.content),
                'message': valar_message,
                'code': valar_code
            }
            response.content = json.dumps(data, ensure_ascii=False).encode("utf-8")
            response["Content-Type"] = "application/json; charset=utf-8"
        return response
