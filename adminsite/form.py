from django import forms
from django.utils import timezone
from booking.models import AllCourtInfo, EachCourtInfo, Payment
from member.models import Member
from datetime import timedelta, time, datetime


class AllCourtForm(forms.ModelForm):
    class Meta:
        model = AllCourtInfo
        fields = ('__all__')
        widgets = {
            'open_time': forms.TimeInput(format='%H:%M'),
            'close_time': forms.TimeInput(format='%H:%M'),
            'announce': forms.Textarea(),
            'contacts': forms.Textarea(),
            'rules': forms.Textarea(),
            'fes_date_start': forms.SelectDateWidget(),
            'fes_date_end': forms.SelectDateWidget()
        }
        labels = {
            'num_of_creategroup': 'Number of create group',
            'announce': 'Announce',
            'contacts': 'Contacts',
            'rules': 'Rules',
            'fes_date_start': 'Festival Date Start',
            'fes_date_end': 'Festival Date End'
        }

    range_booking = forms.ChoiceField(
        choices=[
            (timedelta(days=1), "1 day"),
            (timedelta(days=3), "3 days"),
            (timedelta(days=7), "7 days"),
        ],
        label='Range personal booking'
    )

    payment_member_duration = forms.ChoiceField(
        choices=[
            (timedelta(minutes=1), "1 min"),
            (timedelta(minutes=3), "3 mins"),
            (timedelta(minutes=5), "5 mins"),
            (timedelta(minutes=10), "10 mins"),
            (timedelta(minutes=30), "30 mins"),
            (timedelta(hours=1), "1 hour"),
        ],
        label='Payment after booking for member'
    )

    payment_guest_duration = forms.ChoiceField(
        choices=[
            (timedelta(minutes=1), "1 min"),
            (timedelta(minutes=3), "3 mins"),
            (timedelta(minutes=5), "5 mins"),
            (timedelta(minutes=10), "10 mins"),
            (timedelta(minutes=30), "30 mins"),
            (timedelta(hours=1), "1 hour"),
        ],
        label='Payment after booking for guest'
    )

    payment_group_duration = forms.ChoiceField(
        choices=[
            (timedelta(minutes=1), "1 min"),
            (timedelta(minutes=3), "3 mins"),
            (timedelta(minutes=5), "5 mins"),
            (timedelta(minutes=10), "10 mins"),
            (timedelta(minutes=30), "30 mins"),
            (timedelta(hours=1), "1 hour"),
        ],
        label='Payment after booking for group'
    )

    refund_member_duration = forms.ChoiceField(
        choices=[
            (timedelta(days=1), "1 day"),
            (timedelta(days=3), "3 days"),
            (timedelta(days=7), "7 days"),
        ],
        label='Refund before ... for member'
    )

    payment_member_duration_fes = forms.ChoiceField(
        choices=[
            (timedelta(minutes=1), "1 min"),
            (timedelta(minutes=3), "3 mins"),
            (timedelta(minutes=5), "5 mins"),
            (timedelta(minutes=10), "10 mins"),
            (timedelta(minutes=30), "30 mins"),
            (timedelta(hours=1), "1 hour"),
        ],
        label='Payment after booking for member in Festival time'
    )

    refund_member_duration_fes = forms.ChoiceField(
        choices=[
            (timedelta(days=1), "1 day"),
            (timedelta(days=3), "3 days"),
            (timedelta(days=7), "7 days"),
        ],
        label='Refund before ... for member in Festival time'
    )


class EachCourtForm(forms.ModelForm):
    class Meta:
        model = EachCourtInfo
        fields = ['court_number', 'price_normal', 'price_ds_mem', 'price_ds_group',
                  'price_ds_time', 'time_ds_start', 'time_ds_end', 'is_maintain']
        widgets = {
            'time_ds_start': forms.TimeInput(format='%H:%M'),
            'time_ds_end': forms.TimeInput(format='%H:%M'),
        }


class BookingForm(forms.Form):
    date = forms.ChoiceField()
    from_time = forms.ChoiceField()
    to_time = forms.ChoiceField()
    court = forms.ChoiceField()
    name = forms.CharField()
    tel = forms.CharField()
    email = forms.EmailField()


class MemberForm(forms.ModelForm):

    class Meta:
        model = Member
        fields = ('username', 'first_name', 'last_name', 'email',
                  'is_active', 'tel', 'birthday', 'gender', 'public', 'virtualid')
        widgets = {
            'birthday': forms.SelectDateWidget(years=range(datetime.now().year-100, datetime.now().year+1))
        }


class CheckPaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ('__all__')


class IncomeForm(forms.Form):
    year = forms.ChoiceField()


class UsageForm(forms.Form):
    year_month = forms.ChoiceField()
