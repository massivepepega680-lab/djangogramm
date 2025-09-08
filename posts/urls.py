from django.urls import path
from . import views


app_name = "posts"

urlpatterns = [
    path('', views.feed_view, name="feed"),
    path('create/', views.create_post_view, name="create_post"),
    path('post/<int:post_id>/', views.post_details_view, name="post_details"),
]