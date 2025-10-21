from django.urls import path
from . import views


app_name = 'users'

urlpatterns = [
    path('signup/', views.signup_view, name="register"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('activation_sent/', views.activation_sent_view, name="activation_sent"),
    path('activate/<slug:uidb64>/<slug:token>/', views.activate_view, name="activate"),
    path('profile/setup/', views.profile_setup_view, name="profile_setup"),
    path('profile/edit/', views.profile_edit_view, name="profile_edit"),
    path('<str:username>/', views.profile_view, name="profile"),
    path('<str:username>/follow/', views.follow_user, name="follow"),
    path('<str:username>/unfollow/', views.unfollow_user, name="unfollow"),
]