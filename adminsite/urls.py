from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views

from . import views

urlpatterns = [
    path('register/', views.Register.as_view(), name='admin_register'),
    path('login/', views.Login.as_view(), name='admin_login'),
    path('logout/', views.Logout),
    path('', views.AdminHome.as_view(), name='home'),
    path('setting/', views.SettingHome.as_view(), name='setting_home'),
    path('setting/allcourt/', views.AllCourtSetting.as_view(),
         name='allcourt_setting'),
    path('setting/<court_number>/', views.EachCourtSetting.as_view(),
         name='eachcourt_setting'),
    path('adminbooking/', views.AdminBooking.as_view(), name='admin_booking'),
    path('booking/', views.ListBooking.as_view(), name='booking'),
    path('booking/<pk>', views.DetailBooking.as_view(), name='booking_detail'),
    path('member/', views.ListMember.as_view(), name='member'),
    path('member/<pk>', views.DetailMember.as_view(), name='member_detail'),
    path('checkpayment/', views.CheckPayment.as_view(), name='check_payment'),
    path('checkrefund/', views.CheckRefund.as_view(), name='check_refund'),
    path('income_home/', views.IncomeHome.as_view(), name='income_home'),
    path('income/', views.Income.as_view(), name='income'),
    path('usage_home/', views.UsageHome.as_view(), name='usage_home'),
    path('usage/', views.UsageInTime.as_view(), name='usage'),

]
