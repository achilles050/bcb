from booking.models import AllCourtInfo, EachCourtInfo, Booking
from datetime import timedelta, time, datetime


def time_choices():
    info = AllCourtInfo.objects.all()[0]
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
    data = list()
    for t in time_range:
        data.append((str(t)+':00:00', str(t)+':00'))
    return data


def time_choices2():
    info = AllCourtInfo.objects.all()[0]
    if info.open_time.hour > info.close_time.hour:
        time_range = list(
            range((info.close_time.hour+1), (info.open_time.hour+1)))
        l = list(range(1, 25))
        for value in time_range:
            if value in l:
                l.remove(value)
        time_range = l
    else:
        time_range = list(range(info.open_time.hour, info.close_time.hour))
    data = list()
    for t in time_range:
        data.append((str(t)+':00:00', str(t)+':00'))
    return data


def court_choices():
    court_number = EachCourtInfo.objects.values_list(
        "court_number", flat=True).order_by('court_number')
    data = list()
    for c in court_number:
        data.append((c, 'Court '+str(c)))
    return data


def date_choices():
    info = AllCourtInfo.objects.all()[0]
    numdays = info.range_booking.days
    dateList = []
    for x in range(0, numdays):
        dateList.append(datetime.now().date() + timedelta(days=x))
    date_choice_list = []
    for value in dateList:
        date_choice_list.append((value, value.isoformat()))
    return date_choice_list


def year_choices():
    q = Booking.objects.filter(payment_state=1).filter(
        is_deleted=False)
    year_list = list(dict.fromkeys([x.booking_datetime.year for x in q]))
    year_dict = list()
    for value in year_list:
        year_dict.append((value, value))
    return year_dict


def yearmonth_choices():
    q = Booking.objects.filter(payment_state=1).filter(
        is_deleted=False)
    yearmonth_list = list(dict.fromkeys(
        [str(x.booking_datetime.year)+str(x.booking_datetime.month) for x in q]))
    yearmonth_dict = list()
    for value in yearmonth_list:
        yearmonth_dict.append(
            (value[:4]+'-'+value[4:], value[:4]+'-'+value[4:]))
    return yearmonth_dict
