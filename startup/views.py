from django.http import JsonResponse


def index(request):
    return JsonResponse({"version": "1.0.1"})
