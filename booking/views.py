import json
from datetime import time, timedelta, date
from uuid import uuid4
import calendar
import urllib.parse

from . import models
from . import book
from member import group
from .book import AddMonths

from member import models as mem_models
from . import serializers

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user
from django.http.response import JsonResponse
# from django.core import serializers
from django.forms.models import model_to_dict
# from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from django.utils.datetime_safe import datetime
from django.template.loader import render_to_string
from django.core.mail import send_mail

from rest_framework.views import APIView
# Create your views here.


class CheckRange(APIView):
    def get(sself, request):
        try:
            q_allcourt = models.AllCourtInfo.objects.all()[0]
            range_booking = q_allcourt.range_booking
            dt_range = datetime.now() + range_booking
            date_range = timezone.make_aware(dt_range).date()
            return JsonResponse({'range': date_range}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'msg': 'error'}, status=400)

    def post(self, request):
        try:
            y = request.data['year']
            m = request.data['month']
            d = request.data['day']
            info = models.AllCourtInfo.objects.all()[0]
            dt = datetime(year=int(y), month=int(m)+1, day=int(d))
            inrange_less = dt.date() <= timezone.make_aware(
                datetime.now() + info.range_booking).date()
            inrange_more = dt.date() >= timezone.make_aware(datetime.now()).date()
            if inrange_less and inrange_more:
                date = str(y)+str(int(m)+1)+str(d)
                return JsonResponse({'msg': True, 'date': date}, status=200)
            else:
                return JsonResponse({'msg': False}, status=404)
        except Exception as e:
            print(e)
            return JsonResponse({'msg': False}, status=404)


class CheckPrice(APIView):
    def post(self, request):
        all_bookingid = request.data['bookingid']
        booking_obj_list = []
        pay = 0
        discount = 0

        for bookingid in all_bookingid:
            now = timezone.make_aware(datetime.now())
            q_bookingid = models.Booking.objects.filter(bookingid=bookingid).filter(payment_state=1).filter(is_deleted=False).exclude(
                exp_datetime__lt=now).exists()

            if q_bookingid:
                q_booking = models.Booking.objects.get(bookingid=bookingid)
                pay += q_booking.price_pay
                discount += q_booking.price_ds
                booking_obj_list.append(q_booking)
            else:
                return JsonResponse({'message': 'error bookingid not available'}, status=404)
        d = dict()
        d['Bookingid'] = all_bookingid
        d['price'] = pay
        d['discount'] = discount
        return JsonResponse(d)


class Booking(APIView):
    def get(self, request):  # query status court
        if not models.AllCourtInfo.objects.all()[0].force_close:
            get_date = request.GET.get('d', None)
            if get_date is not None:
                strdate = str(get_date)
                mydate = datetime.strptime(strdate, '%Y%m%d').date()
            else:
                mydate = datetime.now().date()
            q_allcourtinfo = models.AllCourtInfo.objects.all()[0]
            time_open = q_allcourtinfo.open_time.hour
            time_close = q_allcourtinfo.close_time.hour
            time = range(0, 24)
            if time_open > time_close:
                time = list(range(time_close, time_open))
                l = list(range(0, 24))
                for value in time:
                    if value in l:
                        l.remove(value)
                time = l
            else:
                time = list(range(time_open, time_close))
            court_list = models.EachCourtInfo.objects.values_list(
                "court_number", flat=True).order_by('court_number')
            status_list = list()
            for i, t in enumerate(time):
                str_time = str('%02d:00' % t+'-'+'%02d:00' % (t+1))
                status_list.append({'time': str_time})
                for c in court_list:
                    str_court = 'Court'+str(c)
                    if book.check_valid(court=c, mytime=t, mydate=mydate):
                        status_list[i][str_court] = True
                    else:
                        status_list[i][str_court] = False
            data = dict({'date': mydate})
            data['status'] = status_list
            q_eachcourtinfo = models.EachCourtInfo.objects.all()
            s_eachcourtinfo = serializers.EachCourtInfoSerializer(
                q_eachcourtinfo, many=True)
            data['eachcourt_info'] = s_eachcourtinfo.data
            return JsonResponse(data)
        else:
            return JsonResponse({'status': 'close'})

    def post(self, request):  # book court
        booking = request.data['arr']
        strbooking_date = request.data['date']

        booking_date = datetime.strptime(strbooking_date, '%Y-%m-%d').date()
        booking_obj_list = list()
        all_price_normal = 0
        all_ds_time = 0
        all_ds_mem = 0

        q_allcourtinfo = models.AllCourtInfo.objects.all()[0]
        fes_start = q_allcourtinfo.fes_date_start
        fes_end = q_allcourtinfo.fes_date_end

        if request.user.id is not None:
            name = request.user.first_name
            email = request.user.email
            tel = mem_models.Member.objects.get(username=request.user).tel
            member = mem_models.Member.objects.get(username=request.user)
            if booking_date >= fes_start and booking_date <= fes_end:
                exp = q_allcourtinfo.payment_member_duration_fes
                refund_dur = q_allcourtinfo.refund_member_duration_fes
            else:
                exp = q_allcourtinfo.payment_member_duration
                refund_dur = q_allcourtinfo.refund_member_duration
        else:
            name = request.data['name']
            email = request.data['email']
            tel = request.data['phone']
            member = None
            exp = q_allcourtinfo.payment_guest_duration

        print(email)
        dt_now = timezone.make_aware(datetime.now())
        dt_exp = dt_now + exp

        for value in booking:
            court = int(value['column'][5:])
            mytime = int(value['time'][:2])

            if book.check_valid(court=court, mytime=mytime, mydate=booking_date):
                booking_datetime = timezone.make_aware(
                    datetime.combine(booking_date, time(mytime)))
                q_court = models.EachCourtInfo.objects.get(court_number=court)
                price_normal = q_court.price_normal
                ds_mem = q_court.price_ds_mem if request.user.id is not None else 0
                ds_time = q_court.price_ds_time
                ds_time_start = q_court.time_ds_start.hour
                ds_time_end = q_court.time_ds_end.hour

                if not mytime in range(int(ds_time_start), int(ds_time_end)):
                    ds_time = 0

                while True:
                    bookingid = uuid4().hex
                    if models.Booking.objects.filter(bookingid=bookingid).exists():
                        pass
                    else:
                        break

                booking_obj, booking_created = models.Booking.objects.get_or_create(
                    name=name,
                    email=email,
                    tel=tel,
                    member=member,
                    court=q_court,
                    booking_datetime=booking_datetime,
                    exp_datetime=dt_exp,
                    price_normal=price_normal,
                    price_ds=ds_mem+ds_time,
                    price_pay=price_normal-ds_mem-ds_time,
                    bookingid=bookingid,
                    refund_datetime=booking_datetime - refund_dur)

                if booking_created:
                    booking_obj_list.append(booking_obj)
                    all_price_normal += price_normal
                    all_ds_mem += ds_mem
                    all_ds_time += ds_time
                else:
                    booking_obj.delete()
                    break
            else:
                break

        if len(booking) != len(booking_obj_list):
            if len(booking_obj_list) != 0:
                for value in booking_obj_list:
                    value.delete()
            return JsonResponse({'success': False})
        else:
            response_dict = dict()
            response_dict['success'] = True
            response_dict['bookingid'] = [
                value.bookingid for value in booking_obj_list]
            response_dict['price'] = {}
            response_dict['price']['normal_price'] = all_price_normal
            response_dict['price']['discount_time'] = all_ds_time
            response_dict['price']['discount_member'] = all_ds_mem
            response_dict['price']['pay'] = all_price_normal - \
                all_ds_time-all_ds_mem
            return JsonResponse(response_dict)


class GroupBooking(APIView):
    def get(self, request):
        print(datetime.now())
        if request.user.id is None:
            return JsonResponse({'msg': 'Pls login'})
        is_headergroupmember = mem_models.GroupMember.objects.filter(
            role='h').filter(member_id=request.user.id).exists()

        if is_headergroupmember:
            q_headergroupmember = mem_models.GroupMember.objects.get(
                role='h', member_id=request.user.id)
            q_group = mem_models.Group.objects.get(
                id=q_headergroupmember.group_id)
        else:
            return JsonResponse({'msg': 'You re not header'}, status=400)

        if not models.AllCourtInfo.objects.all()[0].force_close:
            get_date = request.GET.get('d', None)
            if get_date is not None:
                dayofweek = int(get_date)
                dayrange = range(dayofweek, dayofweek+1)
            else:
                dayofweek = 0
                dayrange = range(0, 7)

            dt_now = timezone.make_aware(datetime.now())
            date_nm = book.AddMonths(dt_now, 1)

            q_allcourtinfo = models.AllCourtInfo.objects.all()[0]
            time_open = q_allcourtinfo.open_time.hour
            time_close = q_allcourtinfo.close_time.hour
            time24 = range(0, 24)
            court_list = models.EachCourtInfo.objects.values_list(
                "court_number", flat=True).order_by('court_number')
            status_list = list()
            history_groupbooking_list = list()
            if time_open > time_close:
                time24 = list(range(time_close, time_open))
                l = list(range(0, 24))
                for value in time24:
                    if value in l:
                        l.remove(value)
                time24 = l
            else:
                time24 = list(range(time_open, time_close))
            dt_now = timezone.make_aware(datetime.now())
            gapday = q_allcourtinfo.groupbooking_lastmonth_day
            gapdate = timezone.make_aware(
                datetime(dt_now.year, dt_now.month, gapday))
            if dt_now > gapdate:
                for intday, intday2 in enumerate(dayrange):
                    day = calendar.monthcalendar(date_nm.year, date_nm.month)[
                        1][intday2]
                    mydate = date(date_nm.year, date_nm.month, day)
                    weekday = mydate.strftime('%A')
                    status_list.append({'weekday': weekday, 'status': {}})
                    inner_status_list = list()

                    for i, t in enumerate(time24):
                        str_time = str('%02d:00' % t+'-'+'%02d:00' % (t+1))
                        inner_status_list.append({'time': str_time})
                        for c in court_list:
                            str_court = 'Court'+str(c)
                            if book.check_valid_group(court=c, mytime=t, mydate=mydate):
                                inner_status_list[i][str_court] = True
                            else:
                                inner_status_list[i][str_court] = False
                    status_list[intday]['status'] = inner_status_list

            else:
                for intday, intday2 in enumerate(dayrange):
                    day = calendar.monthcalendar(date_nm.year, date_nm.month)[
                        1][intday2]
                    mydate = date(date_nm.year, date_nm.month, day)
                    weekday = mydate.strftime('%A')
                    status_list.append({'weekday': weekday, 'status': {}})
                    inner_status_list = list()
                    history_day = calendar.monthcalendar(dt_now.year, dt_now.month)[
                        1][intday2]
                    history_mydate = date(
                        dt_now.year, dt_now.month, history_day)

                    for i, t in enumerate(time24):
                        str_time = str('%02d:00' % t+'-'+'%02d:00' % (t+1))
                        inner_status_list.append({'time': str_time})
                        for c in court_list:
                            str_court = 'Court'+str(c)
                            check_history = book.check_valid_group_history(
                                court=c, mytime=t, mydate=history_mydate)
                            check_yourhistory = book.check_valid_group_history_for_booking(
                                court=c, mytime=t, mydate=history_mydate, mygroup=q_group)
                            check_all = check_history or check_yourhistory
                            if book.check_valid_group(court=c, mytime=t, mydate=mydate) and check_all:
                                inner_status_list[i][str_court] = True
                            else:
                                inner_status_list[i][str_court] = False
                    status_list[intday]['status'] = inner_status_list

                mon = calendar.monthcalendar(dt_now.year, dt_now.month)[1][0]
                sun = calendar.monthcalendar(dt_now.year, dt_now.month)[1][6]
                day1 = date(dt_now.year, dt_now.month, mon)
                day7 = date(dt_now.year, dt_now.month, sun)

                dt0 = timezone.make_aware(datetime.combine(day1, time(0)))
                dt23 = timezone.make_aware(datetime.combine(day7, time(23)))

                history_groupbooking = models.Booking.objects.filter(group=q_group).filter(
                    booking_datetime__gte=dt0).filter(booking_datetime__lte=dt23).filter(
                    payment_state=1).filter(is_deleted=False)

                history_groupbooking = sorted(history_groupbooking, key=lambda x: (
                    x.booking_datetime.date(), x.court.court_number, x.booking_datetime.time()))

                for value in history_groupbooking:
                    booked_dt = value.booking_datetime
                    booked_hour = int(booked_dt.strftime('%H'))
                    booked_t = str('%02d:00' % booked_hour+'-' +
                                   '%02d:00' % (booked_hour+1))
                    calendar.weekday(
                        booked_dt.year, booked_dt.month, booked_dt.day)
                    history_groupbooking_list.append({'weekday': booked_dt.strftime('%A'),
                                                      'court': value.court.court_number,
                                                      'time': booked_t})

            stryear_month = mydate.strftime('%Y-%m')
            q_eachcourtinfo = models.EachCourtInfo.objects.all()
            s_eachcourtinfo = serializers.EachCourtInfo2Serializer(
                q_eachcourtinfo, many=True)

            data = dict()
            data['date'] = {'year_month': stryear_month}
            data['group'] = q_group.group_name
            data['status'] = status_list
            data['booking_history'] = history_groupbooking_list
            # data['eachcourt_info'] = s_eachcourtinfo.data

            print(datetime.now())
            return JsonResponse(data)
        else:
            return JsonResponse({'status': 'close'})

    def post(self, request):
        if request.user.id is None:
            return JsonResponse({'msg': 'Pls login'})
        is_headergroupmember = mem_models.GroupMember.objects.filter(
            role='h').filter(member_id=request.user.id).exists()

        if is_headergroupmember:
            q_headergroupmember = mem_models.GroupMember.objects.get(
                role='h', member_id=request.user.id)
            q_group = mem_models.Group.objects.get(
                id=q_headergroupmember.group_id)
            q_header = mem_models.Member.objects.get(id=request.user.id)
        else:
            return JsonResponse({'msg': 'You re not header'}, status=400)

        year_month = request.data['year_month']
        raw_booking = request.data['arr']
        dt_now = timezone.make_aware(datetime.now())

        if book.AddMonths(dt_now.date(), 1) != datetime.strptime(year_month, '%Y-%m').date():
            return JsonResponse({'msg': 'try again (year_month not correct)'})

        booking = list()
        for value in raw_booking:
            if len(value) == 1:
                continue
            print(value[0])
            for i in range(len(value)-1):
                booking.append(
                    {'weekday': value[0], 'column': value[i+1]['column'], 'time': value[i+1]['time']})

        booking_obj_list = list()
        booking_date_list = list()
        all_price_normal = 0
        all_ds_time = 0
        all_ds_group = 0

        q_allcourtinfo = models.AllCourtInfo.objects.all()[0]
        name = request.user.first_name
        email = request.user.email
        tel = q_header.tel
        member = q_header
        exp = q_allcourtinfo.payment_group_duration
        gapday = q_allcourtinfo.groupbooking_lastmonth_day
        refund_day = q_allcourtinfo.refund_group_day

        dt_exp = dt_now + exp
        gapdate = timezone.make_aware(
            datetime(dt_now.year, dt_now.month, gapday))
        refund_datetime = timezone.make_aware(
            datetime(dt_now.year, dt_now.month, refund_day, 0, 0, 0))

        if dt_now <= gapdate:  # for old groupbooking in this gap
            for value in booking:
                court = int(value['column'][5:])
                mytime = int(value['time'][:2])

                strday = value['weekday']
                mydate = datetime.strptime(year_month, '%Y-%m').date()
                day_of_week = list(calendar.day_name).index(strday)

                thismonth_day = calendar.monthcalendar(
                    dt_now.year, dt_now.month)[1][day_of_week]
                thismonth_date = datetime(
                    dt_now.year, dt_now.month, thismonth_day)
                thismonth_date = timezone.make_aware(thismonth_date)

                valid_history = book.check_valid_group_history(
                    court=court, mydate=thismonth_date, mytime=mytime)
                valid_yourhistory = book.check_valid_group_history_for_booking(
                    court=court, mydate=thismonth_date, mytime=mytime, mygroup=q_group)
                valid_thismonth = valid_history or valid_yourhistory

                for day in calendar.monthcalendar(mydate.year, mydate.month):
                    if day[day_of_week] != 0:
                        booking_date = date(
                            mydate.year, mydate.month, day[day_of_week])
                        booking_date_list.append(booking_date)
                        check_valid_group = book.check_valid_group(
                            court=court, mytime=mytime, mydate=booking_date)

                        if check_valid_group and valid_thismonth:
                            booking_datetime = timezone.make_aware(
                                datetime.combine(booking_date, time(mytime)))
                            bookingid = uuid4().hex
                            q_court = models.EachCourtInfo.objects.get(
                                court_number=court)
                            price_normal = q_court.price_normal
                            ds_group = q_court.price_ds_group
                            ds_time = q_court.price_ds_time
                            ds_time_start = q_court.time_ds_start.hour
                            ds_time_end = q_court.time_ds_end.hour

                            if not mytime in range(int(ds_time_start), int(ds_time_end)):
                                ds_time = 0

                            booking_obj, booking_created = models.Booking.objects.get_or_create(
                                name=name,
                                email=email,
                                tel=tel,
                                member=member,
                                group=q_group,
                                court=q_court,
                                booking_datetime=booking_datetime,
                                exp_datetime=dt_exp,
                                price_normal=price_normal,
                                price_ds=ds_group+ds_time,
                                price_pay=price_normal-ds_group-ds_time,
                                bookingid=bookingid,
                                refund_datetime=refund_datetime)

                            if booking_created:
                                booking_obj_list.append(booking_obj)
                                all_price_normal += price_normal
                                all_ds_group += ds_group
                                all_ds_time += ds_time
                            else:
                                booking_obj.delete()
                                break
                        else:
                            break
                else:
                    continue
                break
        else:
            for value in booking:
                court = int(value['column'][5:])
                mytime = int(value['time'][:2])

                strday = value['weekday']
                mydate = datetime.strptime(year_month, '%Y-%m').date()
                day_of_week = list(calendar.day_name).index(strday)

                for day in calendar.monthcalendar(mydate.year, mydate.month):
                    if day[day_of_week] != 0:
                        print('pass')
                        booking_date = date(
                            mydate.year, mydate.month, day[day_of_week])
                        booking_date_list.append(booking_date)

                        if book.check_valid_group(court=court, mytime=mytime, mydate=booking_date):
                            print(book.check_valid_group(court=court,
                                                         mytime=mytime, mydate=booking_date))
                            booking_datetime = timezone.make_aware(
                                datetime.combine(booking_date, time(mytime)))
                            bookingid = uuid4().hex
                            q_court = models.EachCourtInfo.objects.get(
                                court_number=court)
                            price_normal = q_court.price_normal
                            ds_group = q_court.price_ds_group
                            ds_time = q_court.price_ds_time
                            ds_time_start = q_court.time_ds_start.hour
                            ds_time_end = q_court.time_ds_end.hour

                            if not mytime in range(int(ds_time_start), int(ds_time_end)):
                                ds_time = 0

                            booking_obj, booking_created = models.Booking.objects.get_or_create(
                                name=name,
                                email=email,
                                tel=tel,
                                member=member,
                                group=q_group,
                                court=q_court,
                                booking_datetime=booking_datetime,
                                exp_datetime=dt_exp,
                                price_normal=price_normal,
                                price_ds=ds_group+ds_time,
                                price_pay=price_normal-ds_group-ds_time,
                                bookingid=bookingid,
                                refund_datetime=refund_datetime)

                            if booking_created:
                                booking_obj_list.append(booking_obj)
                                all_price_normal += price_normal
                                all_ds_group += ds_group
                                all_ds_time += ds_time
                            else:
                                booking_obj.delete()
                                break
                        else:
                            break
                else:
                    continue
                break

        if len(booking_date_list) != len(booking_obj_list):
            if len(booking_obj_list) != 0:
                for value in booking_obj_list:
                    value.delete()
            return JsonResponse({'success': False})
        else:
            response_dict = dict()
            response_dict['success'] = True
            response_dict['bookingid'] = [
                value.bookingid for value in booking_obj_list]
            response_dict['price'] = {}
            response_dict['price']['normal_price'] = all_price_normal
            response_dict['price']['discount_time'] = all_ds_time
            response_dict['price']['discount_group'] = all_ds_group
            response_dict['price']['pay'] = all_price_normal - \
                all_ds_time-all_ds_group
            return JsonResponse(response_dict)


class Payment(APIView):
    def get(self, request):
        if request.user.id is None:
            return JsonResponse({'msg': 'Pls login'}, status=404)
        data = dict()
        action = request.GET.get('q', None)
        if action == 'group':
            is_headergroupmember = mem_models.GroupMember.objects.filter(
                role='h').filter(member_id=request.user.id).exists()

            if is_headergroupmember:
                headergroupmember_q = mem_models.GroupMember.objects.get(
                    role='h', member_id=request.user.id)
                group_q = mem_models.Group.objects.get(
                    id=headergroupmember_q.group_id)
                payment_q = models.Payment.objects.filter(group=group_q)
                data['group'] = group_q.group_name
            else:
                return JsonResponse({'msg': 'You re not header'}, status=400)

        else:
            mem_q = mem_models.Member.objects.get(id=request.user.id)
            payment_q = models.Payment.objects.filter(
                member=mem_q).filter(group=None).filter(is_founded=True)
        payment_s = serializers.PaymentSerializer(payment_q, many=True)
        payment_list = list(payment_s.data)
        for i in range(len(payment_list)):
            payment_list[i]['number'] = i+1
        data['data'] = payment_list
        return JsonResponse(data)

    def post(self, request):
        all_bookingid = request.data['bookingid']
        if len(all_bookingid) == 0:
            return JsonResponse({'msg': 'Try Again not have any bookingid'})
        is_groupbooking = request.data['group']
        booking_obj_list = []
        pay = 0
        if is_groupbooking:
            if request.user.id is None:
                return JsonResponse({'msg': 'Pls login', 'success': False})
            is_headergroupmember = mem_models.GroupMember.objects.filter(
                role='h').filter(member_id=request.user.id).exists()

            if is_headergroupmember:
                q_headergroupmember = mem_models.GroupMember.objects.get(
                    role='h', member_id=request.user.id)
                q_group = mem_models.Group.objects.get(
                    id=q_headergroupmember.group_id)
                member = q_headergroupmember.member
            else:
                return JsonResponse({'msg': 'You re not header', 'success': False}, status=400)

        else:
            if request.user.id is not None:
                member = mem_models.Member.objects.get(id=request.user.id)
            else:
                member = None
            q_group = None
        for bookingid in all_bookingid:
            now = timezone.make_aware(datetime.now())
            q_bookingid = models.Booking.objects.filter(bookingid=bookingid).filter(
                member=member).filter(payment_state=0).exclude(exp_datetime__lt=now).exists()

            if q_bookingid:
                q_booking = models.Booking.objects.get(bookingid=bookingid)
                pay += q_booking.price_pay
                booking_obj_list.append(q_booking)
            else:
                return JsonResponse({'message': f'error bookingid {bookingid} not available', 'success': False}, status=404)
        while True:
            payment_obj, payment_created = models.Payment.objects.get_or_create(
                paymentid=uuid4().hex,
                pay=pay,
                member=member,
                group=q_group)
            if payment_created:
                break

        if payment_created:
            for value in booking_obj_list:
                value.payment_state = 1
                value.paymentid = payment_obj.paymentid
                value.exp_datetime = None
                value.save()
            email = booking_obj_list[0].email
            print(email)
            html = render_to_string('booking_success.html', {'object': booking_obj_list,
                                                             'paymentid': payment_obj.paymentid})
            send_mail(
                'Booking Badminton Court Successfully',
                message=None,
                html_message=html,
                recipient_list=[email],
                from_email=None,
                fail_silently=False,
            )

            return JsonResponse({'message': 'confirm success', 'success': True})
        else:
            return JsonResponse({'message': 'confirm unsuccess', 'success': False}, status=400)


class Refunding(APIView):
    def post(self, request):
        if request.user.id is None:
            return JsonResponse({'msg': 'Pls login', 'success': False})
        data = request.data
        action = data['action']
        all_bookingid = data['bookingid']
        dt_now = timezone.make_aware(datetime.now())
        if len(all_bookingid) == 0:
            return JsonResponse({'msg': 'Try Again not have any bookingid', 'success': False})
        banking_id = data['banking_id']
        banking_name = data['banking_name']
        refund_obj_list = list()
        price = 0
        for bookingid in all_bookingid:
            try:
                obj = models.Booking.objects.get(member_id=request.user.id, group=None,
                                                 bookingid=bookingid, payment_state=1, is_deleted=False, refund_datetime__gt=dt_now)
            except Exception as e:
                print(e)
                return JsonResponse({'msg': f'bookingid {bookingid} not found',
                                     'success': False})
            price += obj.price_pay
            refund_obj_list.append(obj)
        while True:
            refundid = uuid4().hex
            refund_obj, refund_created = models.Refund.objects.get_or_create(
                refundid=refundid,
                price=price,
                member_id=request.user.id,
                bank_acc_id=banking_id,
                bank_acc_name=banking_name
            )

            if refund_created:
                break

        for value in refund_obj_list:
            value.payment_state = 3
            value.refundid = refund_obj.refundid
            value.save()

        return JsonResponse({'msg': 'Refund successful', 'success': True})


class GroupRefund(APIView):
    def get(self, request, groupname):
        try:
            groupname = urllib.parse.unquote_plus(groupname)
            if request.user.id is not None:
                mygroup = mem_models.Group.objects.get(group_name=groupname)
                groupid = mygroup.id
                is_header = group.group_head_per(
                    groupid=groupid, memberid=request.user.id)
                if not is_header:
                    return JsonResponse({'msg': "You're not header", 'success': False})
            else:
                return JsonResponse({'msg': "Pls login", 'success': False})
            q_allcourtinfo = models.AllCourtInfo.objects.all()[0]
            date_now = datetime.now().date()

            gapday = q_allcourtinfo.groupbooking_lastmonth_day
            gapdate = timezone.make_aware(
                datetime(date_now.year, date_now.month, gapday))

            if date_now > gapdate:
                return JsonResponse({'msg': 'cant refund', 'success': False})

            date_nextmonth = AddMonths(date_now, 1)
            nextmonth_booking_list = group.group_booking_by_date(
                mydate=date_nextmonth, mygroup=mygroup)

            data = {'group_booking': nextmonth_booking_list}
            return JsonResponse(data)

        except Exception as e:
            print(e)
            return JsonResponse({'msg': 'error', 'success': False})

    def post(self, request, groupname):
        try:
            groupname = urllib.parse.unquote_plus(groupname)
            if request.user.id is not None:
                mygroup = mem_models.Group.objects.get(group_name=groupname)
                groupid = mygroup.id
                is_header = group.group_head_per(
                    groupid=groupid, memberid=request.user.id)
                if not is_header:
                    return JsonResponse({'msg': "You're not header", 'success': False})
            else:
                return JsonResponse({'msg': "Pls login", 'success': False})
            q_allcourtinfo = models.AllCourtInfo.objects.all()[0]
            date_now = datetime.now().date()

            gapday = q_allcourtinfo.groupbooking_lastmonth_day
            gapdate = timezone.make_aware(
                datetime(date_now.year, date_now.month, gapday))

            if date_now > gapdate:
                return JsonResponse({'msg': 'cant refund', 'success': False})

            date_nextmonth = AddMonths(date_now, 1)
            nextmonth_booking_list = group.group_booking_by_date2(
                mydate=date_nextmonth, mygroup=mygroup)

            data = request.data
            group_booking_list = data['group_booking']
            banking_id = data['banking_id']
            banking_name = data['banking_name']
            price = 0
            booking_list = []

            for value in group_booking_list:
                if value in nextmonth_booking_list:
                    strday = value['weekday']
                    mytime = int(value['time'][:2])
                    court = value['court']
                    mydate = date_nextmonth
                    day_of_week = list(calendar.day_name).index(strday)
                    for day in calendar.monthcalendar(mydate.year, mydate.month):
                        if day[day_of_week] != 0:
                            booking_date = date(
                                mydate.year, mydate.month, day[day_of_week])
                            booking_datetime = timezone.make_aware(
                                datetime.combine(booking_date, time(mytime)))
                            booking_list.append({'datetime': booking_datetime,
                                                 'court': court})
                else:
                    return JsonResponse({'msg': 'your data not correct', 'success': False})

            refund_obj_list = []
            for value in booking_list:
                try:
                    obj = models.Booking.objects.get(
                        booking_datetime=value['datetime'], court=value['court'], group=mygroup, payment_state=1, is_deleted=False)
                except Exception as e:
                    print(e)
                    return JsonResponse({'msg': 'your data not found',
                                         'success': False})

                price += obj.price_pay
                refund_obj_list.append(obj)

            while True:
                refundid = uuid4().hex
                refund_obj, refund_created = models.Refund.objects.get_or_create(
                    refundid=refundid,
                    price=price,
                    member_id=request.user.id,
                    group=mygroup,
                    bank_acc_id=banking_id,
                    bank_acc_name=banking_name
                )

                if refund_created:
                    break

            for value in refund_obj_list:
                value.payment_state = 3
                value.refundid = refund_obj.refundid
                value.save()

            return JsonResponse({'msg': 'ok', 'success': True})
        except Exception as e:
            print(e)
            return JsonResponse({'msg': 'error', 'success': False})


class History(APIView):
    def get(self, request):
        if request.user.id is None:
            return JsonResponse({'msg': 'Pls login', 'success': False})
        q_allcourtinfo = models.AllCourtInfo.objects.all()[0]
        dt_now = timezone.make_aware(datetime.now())
        refund_dur = q_allcourtinfo.refund_member_duration
        refund_datetime = dt_now+refund_dur
        booking_q = models.Booking.objects.filter(
            member_id=request.user.id).filter(group=None).exclude(exp_datetime__lt=dt_now).filter(is_deleted=False)
        booking_q = sorted(booking_q, key=lambda x: (
            x.booking_datetime.date(), x.court.court_number, x.booking_datetime.time()))
        booking_s = serializers.HistorySerializer(booking_q, many=True)
        booking_list = list(booking_s.data)

        for i in range(len(booking_list)):
            booking_list[i]['number'] = i+1
            if booking_q[i].payment_state == 0:
                booking_list[i]['state'] = 'booking'
                booking_list[i]['timeout'] = booking_q[i].exp_datetime.strftime(
                    "%d-%m-%Y %H:%M")
                booking_list[i]['action'] = ['pay', 'cancel']
            elif booking_q[i].payment_state == 1:
                booking_list[i]['state'] = 'success'
                if booking_q[i].refund_datetime > dt_now:
                    booking_list[i]['timeout'] = (
                        booking_q[i].refund_datetime).strftime("%d-%m-%Y %H:%M")
                    booking_list[i]['action'] = ['refund']
                else:
                    booking_list[i]['timeout'] = None
                    booking_list[i]['action'] = None
            elif booking_q[i].payment_state == 2:
                booking_list[i]['state'] = 'checking_payment'
                booking_list[i]['timeout'] = None
                booking_list[i]['action'] = None
            elif booking_q[i].payment_state == 3:
                booking_list[i]['state'] = 'refunded'
                booking_list[i]['timeout'] = None
                booking_list[i]['action'] = None
            elif booking_q[i].payment_state == 4:
                booking_list[i]['state'] = 'checking_payment_false'
                booking_list[i]['timeout'] = None
                booking_list[i]['action'] = None
        return JsonResponse({'data': booking_list, 'success': True})


class HistoryPaymentPersonal(APIView):
    def get(self, request):
        return Payment().get(request)


class BookingToPaymentAndCancel(APIView):
    def get(self, request):
        if request.user.id is None:
            return JsonResponse({'msg': 'Pls login', 'success': False})
        dt_now = timezone.make_aware(datetime.now())
        booking_q = models.Booking.objects.filter(
            member_id=request.user.id).filter(group=None).filter(payment_state=0).exclude(exp_datetime__lt=dt_now).filter(is_deleted=False)
        booking_q = sorted(booking_q, key=lambda x: (
            x.booking_datetime.date(), x.court.court_number, x.booking_datetime.time()))
        booking_s = serializers.HistorySerializer(booking_q, many=True)
        booking_list = list(booking_s.data)
        for i in range(len(booking_list)):
            booking_list[i]['number'] = i+1
            booking_list[i]['timeout'] = booking_q[i].exp_datetime.strftime(
                "%d-%m-%Y %H:%M")

        return JsonResponse({'data': booking_list, 'success': True})

    def post(self, request):
        if request.user.id is None:
            return JsonResponse({'msg': 'Pls login', 'success': False})
        data = request.data
        action = data['action']
        booking_obj_list = list()
        if action == 'pay':
            request.data['group'] = False
            return Payment().post(request)
        elif action == 'cancel':
            all_bookingid = data['bookingid']
            for bookingid in all_bookingid:
                try:
                    obj = models.Booking.objects.get(member_id=request.user.id, group=None,
                                                     bookingid=bookingid, payment_state=0, is_deleted=False)
                except Exception as e:
                    print(e)
                    return JsonResponse({'msg': f'bookingid {bookingid} not found', 'success': False})
                booking_obj_list.append(obj)
            for value in booking_obj_list:
                value.exp_datetime = None
                value.is_deleted = True
                value.save()

            return JsonResponse({'msg': 'Cancel successful', 'success': False})


class SuccessToRefunding(APIView):
    def get(self, request):
        if request.user.id is None:
            return JsonResponse({'msg': 'Pls login', 'success': False})

        q_allcourtinfo = models.AllCourtInfo.objects.all()[0]
        dt_now = timezone.make_aware(datetime.now())
        refund_dur = q_allcourtinfo.refund_member_duration
        refund_datetime = dt_now+refund_dur

        booking_q = models.Booking.objects.filter(
            member_id=request.user.id).filter(group=None).filter(payment_state=1).filter(booking_datetime__gt=refund_datetime)

        booking_q = sorted(booking_q, key=lambda x: (
            x.booking_datetime.date(), x.court.court_number, x.booking_datetime.time()))

        booking_s = serializers.HistorySerializer(booking_q, many=True)

        booking_list = list(booking_s.data)

        for i in range(len(booking_list)):
            booking_list[i]['number'] = i+1
            booking_list[i]['timeout'] = (
                booking_q[i].refund_datetime).strftime("%d-%m-%Y %H:%M")

        return JsonResponse({'data': booking_list, 'success': True})

    def post(self, request):
        return Refunding().post(request)
