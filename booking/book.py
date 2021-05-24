from . import models
from datetime import time, datetime, date  # , timedelta
from django.core.mail import send_mail
from django.utils import timezone


def AddMonths(dt, d, m=1):
    newmonth = (((dt.month - 1) + m) % 12) + 1
    newyear = int(dt.year + (((dt.month - 1) + m) / 12))
    return date(newyear, newmonth, d)


def check_valid(court, mytime, mydate):  # time in hour unit
    try:
        dt = timezone.make_aware(datetime.combine(mydate, time(mytime)))
        info = models.AllCourtInfo.objects.all()[0]
        maintain = models.EachCourtInfo.objects.get(
            court_number=court).is_maintain
        now = datetime.now()
        now_hour = timezone.make_aware(
            datetime.combine(now.date(), time(now.hour)))
        past = dt >= now_hour
        inrange = dt <= timezone.make_aware(
            datetime.now() + info.range_booking)
        valid = not models.Booking.objects.filter(
            booking_datetime=dt).filter(court_id__court_number=court).filter(is_deleted=False).exclude(exp_datetime__lt=timezone.make_aware(datetime.now())).exists()
        if info.open_time.hour > info.close_time.hour:
            time_range = list(
                range(info.close_time.hour, info.open_time.hour))
            l = list(range(0, 24))
            for value in time_range:
                if value in l:
                    l.remove(value)
            time_range = l
        else:
            time_range = list(range(info.open_time.hour, info.close_time.hour))
        if mytime in time_range and valid and not maintain and past and inrange:
            return True
        else:
            return False

    except Exception as e:
        print('Error is : ', e)
        return None


def check_valid_group(court, mytime, mydate):  # time in hour unit
    try:
        dt = timezone.make_aware(datetime.combine(mydate, time(mytime)))
        info = models.AllCourtInfo.objects.all()[0]
        now = timezone.make_aware(datetime.now())
        twomonth = AddMonths(now, 1, m=2)
        range_member_dt = datetime.combine(
            AddMonths(now, 1, m=1), time(0)) - info.range_booking

        maintain = models.EachCourtInfo.objects.get(
            court_number=court).is_maintain
        now_hour = timezone.make_aware(
            datetime.combine(now.date(), time(now.hour)))
        past = dt >= now_hour
        inrange = dt.date() < twomonth
        inrange_member = not dt <= timezone.make_aware(
            datetime.now() + info.range_booking)
        valid = not models.Booking.objects.filter(
            booking_datetime=dt).filter(court_id__court_number=court).filter(is_deleted=False).exclude(exp_datetime__lt=timezone.make_aware(datetime.now())).exists()

        if info.open_time.hour > info.close_time.hour:
            time_range = list(
                range(info.close_time.hour, info.open_time.hour))
            l = list(range(0, 24))
            for value in time_range:
                if value in l:
                    l.remove(value)
            time_range = l
        else:
            time_range = list(range(info.open_time.hour, info.close_time.hour))
        if mytime in time_range and valid and not maintain and past and inrange and inrange_member:
            return True
        else:
            return False

    except Exception as e:
        print('Error is : ', e)
        return None


def check_valid_group_history(court, mytime, mydate):
    try:
        dt = timezone.make_aware(datetime.combine(mydate, time(mytime)))
        valid = not models.Booking.objects.filter(booking_datetime=dt).filter(
            court_id__court_number=court).filter(payment_state=1).filter(is_deleted=False).exclude(group=None).exists()
        return valid
    except Exception as e:
        print('Error is : ', e)
        return None


def check_valid_group_history_for_booking(court, mydate, mytime, mygroup):
    try:
        dt = timezone.make_aware(datetime.combine(mydate, time(mytime)))
        valid = models.Booking.objects.filter(booking_datetime=dt).filter(
            court_id__court_number=court).filter(payment_state=1).filter(is_deleted=False).filter(group=mygroup).exists()
        return valid
    except Exception as e:
        print('Error is : ', e)
        return None
