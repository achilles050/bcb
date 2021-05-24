from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('checkprice/', views.CheckPrice.as_view()),
    path('checkrange/', views.CheckRange.as_view()),
    path('booking/', views.Booking.as_view()),
    path('payment/', views.Payment.as_view()),
    path('groupbooking/', views.GroupBooking.as_view()),
    path('history/', views.History.as_view()),
    path('history/booking/', views.BookingToPaymentAndCancel.as_view()),
    path('history/refund/', views.SuccessToRefunding.as_view()),
    path('history/payment/', views.HistoryPaymentPersonal.as_view()),
    path('group/<groupname>/refund/', views.GroupRefund.as_view()),
]
