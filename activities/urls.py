from django.urls import path
from . import views

app_name = "activities"

urlpatterns = [
    path('feed/', views.feed_view, name="feed"),
]