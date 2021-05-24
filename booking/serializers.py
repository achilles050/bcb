from rest_framework import serializers
from . import models
from datetime import datetime as dt


class EachCourtInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EachCourtInfo
        fields = ('court_number', 'price_normal', 'price_ds_mem',
                  'price_ds_time', 'time_ds_start', 'time_ds_end')


class EachCourtInfo2Serializer(serializers.ModelSerializer):
    class Meta:
        model = models.EachCourtInfo
        fields = ('court_number', 'price_normal', 'price_ds_group',
                  'price_ds_time', 'time_ds_start', 'time_ds_end')


class PaymentSerializer(serializers.ModelSerializer):
    number = serializers.IntegerField(allow_null=True)
    timestamp = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S')

    class Meta:
        model = models.Payment
        exclude = ('id', 'member', 'group', 'is_checked', 'is_founded')


class HistorySerializer(serializers.ModelSerializer):

    number = serializers.IntegerField(allow_null=True)
    court = serializers.IntegerField(source='court.court_number')
    date = serializers.DateTimeField(
        source='booking_datetime', format="%d-%m-%Y")
    time = serializers.DateTimeField(
        source='booking_datetime', format="%H:%M")

    class Meta:
        model = models.Booking
        fields = ('number', 'date', 'court', 'time', 'bookingid')
