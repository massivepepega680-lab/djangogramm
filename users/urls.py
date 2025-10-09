from django.urls import path
from . import views


app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name="register"),
    path('login/', views.login_view, name="login"),
    path('profile/edit/', views.profile_edit_view, name="profile_edit"),
    path('<str:username>/', views.profile_view, name="profile"),
    path('<str:username>/follow/', views.follow_user, name="follow"),
    path('<str:username>/unfollow/', views.unfollow_user, name="unfollow"),
]