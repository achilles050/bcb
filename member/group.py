from django.utils import timezone

from . import models
from booking import models as booking_models

from datetime import date, datetime, time
import calendar
# from django.db.models import Q


def group_mem_per(memberid, groupid):
    q_m = models.GroupMember.objects.filter(
        group_id=groupid).filter(member_id=memberid).filter(role='m').exists()
    q_h = models.GroupMember.objects.filter(
        group_id=groupid).filter(member_id=memberid).filter(role='h').exists()
    return q_m or q_h


def group_head_per(memberid, groupid):
    q = models.GroupMember.objects.filter(
        group_id=groupid).filter(member_id=memberid).filter(role='h').exists()
    return q


def group_booking_by_date(mydate, mygroup):
    group_booking_list = []
    mon = calendar.monthcalendar(mydate.year, mydate.month)[1][0]
    sun = calendar.monthcalendar(mydate.year, mydate.month)[1][6]
    day1 = date(mydate.year, mydate.month, mon)
    day7 = date(mydate.year, mydate.month, sun)

    dt0 = timezone.make_aware(datetime.combine(day1, time(0)))
    dt23 = timezone.make_aware(datetime.combine(day7, time(23)))

    group_booking = booking_models.Booking.objects.filter(group=mygroup).filter(
        booking_datetime__gte=dt0).filter(booking_datetime__lte=dt23).filter(
        payment_state=1)

    group_booking = sorted(group_booking, key=lambda x: (
        x.booking_datetime.date(), x.court.court_number, x.booking_datetime.time()))

    for index, value in enumerate(group_booking):
        booked_dt = value.booking_datetime
        booked_hour = int(booked_dt.strftime('%H'))
        booked_t = str('%02d:00' % booked_hour+'-' +
                       '%02d:00' % (booked_hour+1))
        calendar.weekday(
            booked_dt.year, booked_dt.month, booked_dt.day)
        group_booking_list.append({'number': index+1,
                                   'weekday': booked_dt.strftime('%A'),
                                   'court': value.court.court_number,
                                   'time': booked_t})
    return group_booking_list


def group_booking_by_date2(mydate, mygroup):
    group_booking_list = []
    mon = calendar.monthcalendar(mydate.year, mydate.month)[1][0]
    sun = calendar.monthcalendar(mydate.year, mydate.month)[1][6]
    day1 = date(mydate.year, mydate.month, mon)
    day7 = date(mydate.year, mydate.month, sun)

    dt0 = timezone.make_aware(datetime.combine(day1, time(0)))
    dt23 = timezone.make_aware(datetime.combine(day7, time(23)))

    group_booking = booking_models.Booking.objects.filter(group=mygroup).filter(
        booking_datetime__gte=dt0).filter(booking_datetime__lte=dt23).filter(
        payment_state=1)

    group_booking = sorted(group_booking, key=lambda x: (
        x.booking_datetime.date(), x.court.court_number, x.booking_datetime.time()))

    for index, value in enumerate(group_booking):
        booked_dt = value.booking_datetime
        booked_hour = int(booked_dt.strftime('%H'))
        booked_t = str('%02d:00' % booked_hour+'-' +
                       '%02d:00' % (booked_hour+1))
        calendar.weekday(
            booked_dt.year, booked_dt.month, booked_dt.day)
        group_booking_list.append({'weekday': booked_dt.strftime('%A'),
                                   'court': value.court.court_number,
                                   'time': booked_t})
    return group_booking_list


def group_payment(mygroup):
    payment_list = list()
    payment = booking_models.Payment.objects.filter(
        group=mygroup).filter(is_founded=True)
    for index, value in enumerate(payment):
        payment_list.append({'number': index+1,
                             'date': value.timestamp.strftime("%d-%m-%Y %H:%M"),
                             'price': value.pay,
                             'paymentid': value.paymentid})
    return payment_list
