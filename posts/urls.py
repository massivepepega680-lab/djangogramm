from django.urls import path
from . import views


app_name = "posts"

urlpatterns = [
    path('create/', views.create_post_view, name="create_post"),
    path('post/<int:post_id>/', views.post_details_view, name="post_details"),
    path('post/<int:post_id>/delete/', views.post_delete_view, name="post_delete"),
    path('post/<int:post_id>/toggle_like/', views.toggle_like_view, name="toggle_like"),
]