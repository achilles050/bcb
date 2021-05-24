from django.contrib import admin
from django.urls import path, include, reverse_lazy
from . import views


from django.contrib.auth.views import PasswordResetView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


urlpatterns = [

    path('', views.Index.as_view()),
    path('register/', views.Register.as_view()),
    path('activate_email/<uidb64>/<token>/',
         views.ActivateEmail.as_view(), name='activate_email'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout),
    path('profile/', views.Profile.as_view()),
    path('group/', views.AllGroup.as_view()),
    path('group/<groupname>/', views.MyGroup.as_view()),
    path('creategroup/', views.Creategroup.as_view()),
    path('request/', views.Request.as_view()),
]
