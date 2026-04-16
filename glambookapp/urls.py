from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='root'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    path('profile/', views.profile_view, name='edit_profile'),
    path('tasks/', views.tasks_view, name='view_tasks'),
]
