from django.http import JsonResponse
from django.views import View


class LoginView(View):
    def get(self, request, *args, **kwargs):
        username = request.GET["username"]
        password = request.GET["password"]
        if username == "admin" and password == "admin":
            return JsonResponse(
                {
                    "username": username,
                    "token": "<token>",
                },
            )

        return JsonResponse(
            {
                "message": "Invalid password",
            },
            status=401,
        )
