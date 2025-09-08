from django.http import HttpResponse


def feed_view(request):
    return HttpResponse("This is the main post feed.")

def create_post_view(request):
    return HttpResponse("This is the page to create a new post.")

def post_details_view(request, post_id):
    return HttpResponse(f"This is the detail view for post #{post_id}.")