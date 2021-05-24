from django.shortcuts import render, redirect
from django.http import HttpResponse
from django import forms
from django.urls import reverse
from django.http.response import JsonResponse
from django.views.generic import CreateView, DetailView, UpdateView, ListView, View
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from uuid import uuid4
from datetime import timedelta, datetime, time, date
import calendar

from . import form
from booking import models as booking_models
from booking import book
from member import models as member_models
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput)


class Login(View):
    def get(self, request):
        return render(request, 'adminsite/login.html', {'form': LoginForm})

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        auth = authenticate(username=username, password=password)
        if auth is not None:
            login(request, auth)
            return redirect('/adminsite/')
        else:
            return HttpResponse('try again')


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)


class Register(PermissionRequiredMixin, View):
    permission_required = 'is_staff'
    login_url = '/adminsite/login/'

    def get(self, request):
        return render(request, 'adminsite/register.html', {'form': RegisterForm})

    def post(self, request):
        data = request.POST
        username = data['username']
        password = data['password']
        try:
            user = User.objects.create_user(
                username=username, password=password, is_staff=True, is_superuser=True)
        except Exception as e:
            print(f'Error: {e}')
            return render(request, 'adminsite/register.html', {'form': RegisterForm})
        return HttpResponse('Register Successful')


def Logout(request):
    try:
        print('going to logout')
        logout(request)
        print('logouted')
        return JsonResponse({'msg': 'logout successfully'}, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({'msg': 'error'}, status=404)


class AdminHome(PermissionRequiredMixin, View):
    permission_required = 'is_staff'
    login_url = '/adminsite/login/'

    def get(self, request):
        return render(request, 'adminsite/home.html')


class SettingHome(PermissionRequiredMixin, View):
    permission_required = 'is_staff'
    login_url = '/adminsite/login/'

    def get(self, request):
        court_number = booking_models.EachCourtInfo.objects.values_list(
            "court_number", flat=True).order_by('court_number')
        return render(request, 'adminsite/setting_home.html', {'court_number': court_number})


class AllCourtSetting(PermissionRequiredMixin, View):
    permission_required = 'is_staff'
    login_url = '/adminsite/login/'

    def get(self, request):
        query_obj = booking_models.AllCourtInfo.objects.values().all()[0]
        myform = form.AllCourtForm(query_obj)
        return render(request, 'adminsite/setting_allcourt.html', {'form': myform})

    def post(self, request):
        query_obj = booking_models.AllCourtInfo.objects.all()[0]
        myform = form.AllCourtForm(request.POST, instance=query_obj)

        if myform.is_valid():
            myform.save(commit=True)
        return render(request, 'adminsite/setting_allcourt.html', {'form': myform})


class EachCourtSetting(PermissionRequiredMixin, UpdateView):
    permission_required = 'is_staff'
    login_url = '/adminsite/login/'

    form_class = form.EachCourtForm
    model = booking_models.EachCourtInfo
    template_name = 'adminsite/setting_eachcourt.html'
    slug_field = 'court_number'
    slug_url_kwarg = 'court_number'
    success_url = '/adminsite/setting/'


class AdminBooking(PermissionRequiredMixin, View):
    permission_required = 'is_staff'
    login_url = '/adminsite/login/'

    def get(self, request):
        dt_now = datetime.now()
        mydate = dt_now.date()
        from_time = time(dt_now.hour)
        to_time = time(dt_now.hour+1)
        data = {'date': mydate, 'from_time': from_time,
                'to_time': to_time}
        myform = form.BookingForm(initial=data)
        return render(request, 'adminsite/booking.html', {'form': myform})

    def post(self, request):
        data = request.POST
        myform = form.BookingForm(data)

        if myform.is_valid():
            booking_obj_list = list()
            all_price_normal = 0
            all_ds_time = 0
            all_ds_mem = 0
            from_time = data['from_time']
            to_time = data['to_time']
            str_date = data['date']
            court = data['court']
            name = data['name']
            tel = data['tel']
            email = data['email']

            q_allcourtinfo = booking_models.AllCourtInfo.objects.all()[0]
            booking_date = datetime.strptime(str_date, '%Y-%m-%d').date()

            dt_now = timezone.make_aware(datetime.now())
            exp = q_allcourtinfo.payment_guest_duration
            dt_exp = dt_now + exp

            # from_time = datetime.strptime(from_time, '%H:%M:%S').hour
            # to_time = datetime.strptime(to_time, '%H:%M:%S').hour
            from_time = int(from_time[:2])
            to_time = int(to_time[:2])
            booking_time = []
            for mytime in range(from_time, to_time):
                if mytime in form.time_range():
                    booking_time.append(mytime)

            for mytime in booking_time:
                if book.check_valid(court=court, mytime=mytime, mydate=booking_date):
                    booking_datetime = timezone.make_aware(
                        datetime.combine(booking_date, time(mytime)))
                    q_court = booking_models.EachCourtInfo.objects.get(
                        court_number=court)
                    price_normal = q_court.price_normal
                    ds_mem = 0
                    ds_time = q_court.price_ds_time
                    ds_time_start = q_court.time_ds_start.hour
                    ds_time_end = q_court.time_ds_end.hour

                    if not mytime in range(int(ds_time_start), int(ds_time_end)):
                        ds_time = 0

                    while True:
                        bookingid = uuid4().hex
                        if booking_models.Booking.objects.filter(bookingid=bookingid).exists():
                            pass
                        else:
                            break

                    booking_obj, booking_created = booking_models.Booking.objects.get_or_create(
                        name=name,
                        email=email,
                        tel=tel,
                        member=None,
                        court=q_court,
                        booking_datetime=booking_datetime,
                        exp_datetime=dt_exp,
                        price_normal=price_normal,
                        price_ds=ds_mem+ds_time,
                        price_pay=price_normal-ds_mem-ds_time,
                        bookingid=bookingid)

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

            if len(booking_time) != len(booking_obj_list):
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

        return render(request, 'adminsite/booking.html', {'form': myform})


class ListBooking(PermissionRequiredMixin, ListView):
    permission_required = 'is_staff'
    login_url = '/adminsite/login/'

    model = member_models.Member
    template_name = 'adminsite/booking_list.html'

    def get_queryset(self):
        member = booking_models.Booking.objects.all().order_by(
            'is_deleted').order_by('-booking_datetime')
        return member


class DetailBooking(PermissionRequiredMixin, UpdateView):
    permission_required = 'is_staff'
    login_url = '/adminsite/login/'
    fields = ('__all__')
    # form_class = form.MemberForm
    model = booking_models.Booking
    template_name = 'adminsite/booking_detail.html'
    success_url = '/adminsite/booking/'


class ListMember(ListView):
    permission_required = 'is_staff'
    login_url = '/adminsite/login/'

    model = member_models.Member
    template_name = 'adminsite/member.html'

    def get_queryset(self):
        member = member_models.Member.objects.filter(
            is_staff=False)  # .filter(is_active=True)
        return member


class DetailMember(PermissionRequiredMixin, UpdateView):
    permission_required = 'is_staff'
    login_url = '/adminsite/login/'

    form_class = form.MemberForm
    model = member_models.Member
    template_name = 'adminsite/member_detail.html'
    success_url = '/adminsite/member/'


class CheckPayment(PermissionRequiredMixin, View):
    permission_required = 'is_staff'
    login_url = '/adminsite/login/'

    def get(self, request):
        q_payment = booking_models.Payment.objects.all().order_by('is_checked', '-timestamp')
        return render(request, 'adminsite/check_payment.html', {'form': q_payment})

    def post(self, request):
        found = request.POST.get('found', None)
        not_found = request.POST.get('not_found', None)

        q_payment = booking_models.Payment.objects.all().order_by('is_checked', '-timestamp')

        if found == not_found:
            return render(request, 'adminsite/check_payment.html', {'form': myform})

        if found is not None:
            q_booking = booking_models.Booking.objects.filter(paymentid=found)
            for value in q_booking:
                value.payment_state = 1
                value.is_deleted = False
                value.save()
            mypayment = booking_models.Payment.objects.get(paymentid=found)
            mypayment.is_checked = True
            mypayment.save()

        elif not_found is not None:
            q_booking = booking_models.Booking.objects.filter(
                paymentid=not_found)
            for value in q_booking:
                value.payment_state = 3
                value.is_deleted = True
                value.save()
            mypayment = booking_models.Payment.objects.get(paymentid=not_found)
            mypayment.is_checked = True
            mypayment.save()

        q_payment = booking_models.Payment.objects.all().order_by('is_checked', '-timestamp')

        return render(request, 'adminsite/check_payment.html', {'form': q_payment})


class CheckRefund(PermissionRequiredMixin, View):
    permission_required = 'is_staff'
    login_url = '/adminsite/login/'

    def get(self, request):
        q_refund = booking_models.Refund.objects.all().order_by('is_refunded', 'timestamp')
        return render(request, 'adminsite/check_refund.html', {'form': q_refund})

    def post(self, request):
        check = request.POST.get('check', None)
        uncheck = request.POST.get('uncheck', None)

        q_refund = booking_models.Refund.objects.all().order_by('is_refunded', 'timestamp')

        if check == uncheck:
            return render(request, 'adminsite/check_refund.html', {'form': q_refund})

        if check is not None:
            myrefund = booking_models.Refund.objects.get(refundid=check)
            myrefund.is_refunded = True
            myrefund.save()

        elif uncheck is not None:
            myrefund = booking_models.Refund.objects.get(refundid=uncheck)
            myrefund.is_refunded = False
            myrefund.save()

        q_refund = booking_models.Refund.objects.all().order_by('is_refunded', 'timestamp')

        return render(request, 'adminsite/check_refund.html', {'form': q_refund})


class IncomeHome(PermissionRequiredMixin, View):
    permission_required = 'is_staff'
    login_url = '/adminsite/login/'

    def get(self, request):
        myform = form.IncomeForm
        return render(request, 'adminsite/income_home.html', {'form': myform})


class Income(PermissionRequiredMixin, View):
    permission_required = 'is_staff'
    login_url = '/adminsite/login/'

    def get(self, request):
        month_list = list(range(1, 13))
        labels = [calendar.month_name[i] for i in month_list]
        year = request.GET.get('year', None)
        if year is None:
            year = datetime.now().year
        year = int(year)
        while True:
            try:
                datetime(year, 1, 1)
                break
            except Exception as e:
                year = datetime.now().year
                break
        income_list = []
        usage_list = []
        for month in month_list:
            income = 0
            count = 0
            q_booking = booking_models.Booking.objects.filter(payment_state=1).filter(
                is_deleted=False).filter(booking_datetime__year=year).filter(booking_datetime__month=month)
            for value in q_booking:
                income += value.price_pay
                count += 1
            income_list.append(income)
            usage_list.append(count)
            # q_usage = booking_models.Booking.objects.filter(payment_state=1).filter(
            #     is_deleted=False).filter(booking_datetime__year=year).filter(booking_datetime__month=month)
        data = income_list
        return render(request, 'adminsite/income.html', {'labels': labels,
                                                         'income': income_list,
                                                         'usage': usage_list
                                                         })


class UsageHome(PermissionRequiredMixin, View):
    permission_required = 'is_staff'
    login_url = '/adminsite/login/'

    def get(self, request):
        myform = form.UsageForm()
        # myform.fields['year'].choices = [(1, 1), (2, 2)]
        return render(request, 'adminsite/usage_home.html', {'form': myform})


class UsageInTime(PermissionRequiredMixin, View):
    permission_required = 'is_staff'
    login_url = '/adminsite/login/'

    def get(self, request):
        q_allcourtinfo = booking_models.AllCourtInfo.objects.all()[0]
        time_open = q_allcourtinfo.open_time.hour
        time_close = q_allcourtinfo.close_time.hour
        time_list = range(0, 24)
        if time_open > time_close:
            time_list = list(range(time_close, time_open))
            l = list(range(0, 24))
            for value in time_list:
                if value in l:
                    l.remove(value)
            time_list = l
        else:
            time_list = list(range(time_open, time_close))
        month_list = list(range(1, 13))
        labels = [calendar.month_name[i] for i in month_list]  # month_list
        year_month = request.GET.get('year_month', None)
        if year_month is None:
            dt_now = datetime.now()
            year = dt_now.year
            month = dt_now.month
        else:
            yearmonth_list = year_month.split('-')
            print(yearmonth_list)
            year = yearmonth_list[0]
            month = yearmonth_list[1]
        year = int(year)
        month = int(month)
        while True:
            try:
                datetime(year, month, 1)
                break
            except Exception as e:
                year = datetime.now().year
                break
        income_list = []
        usage_list = []
        # time_list = list(range(0, 24))
        labels = [str(t)+':00' for t in time_list]
        for time in time_list:
            income = 0
            count = 0
            q_booking = booking_models.Booking.objects.filter(payment_state=1).filter(
                is_deleted=False).filter(booking_datetime__year=year).filter(booking_datetime__month=month).filter(booking_datetime__hour=time)
            usage_list.append(q_booking.count())
        return render(request, 'adminsite/usage.html', {'labels': labels,
                                                        'usage': usage_list
                                                        })
