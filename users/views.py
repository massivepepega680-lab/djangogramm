from django.http import HttpResponse


def register_view(request):
    return HttpResponse("This is the user registration page.")

def login_view(request):
    return HttpResponse("This is the user login page.")

def profile_view(request):
    return HttpResponse("This is the user profile page.")