from django.http import JsonResponse
from django.views import View


class LoginView(View):
    def get(self, request, *args, **kwargs):
        username = request.GET["username"]
        password = request.GET["password"]
        try:
            import loader

            file_loader = loader.EncryptFileLoader("")
            if file_loader.license is True and file_loader.check() is False:
                return JsonResponse({"message": "License is not valid"}, status=403)
        except ModuleNotFoundError:
            pass
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=403)

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
