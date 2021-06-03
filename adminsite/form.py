from django import forms
from django.utils import timezone
from booking.models import AllCourtInfo, EachCourtInfo, Payment, FestivalInfo, Booking
from member.models import Member, Group
from datetime import timedelta, time, datetime

class AllCourtForm(forms.ModelForm):
    class Meta:
        model = AllCourtInfo
        fields = ('__all__')
        widgets = {
            'force_close': forms.CheckboxInput(attrs={'class': 'fa fa-share'}),
            'open_time': forms.TimeInput(format='%H:%M'),
            'close_time': forms.TimeInput(format='%H:%M'),
            'announce': forms.Textarea(),
            'contacts': forms.Textarea(),
            'rules': forms.Textarea(),
        }
        labels = {
            'force_close': 'ปิดสนามทั้งหมด',
            'groupbooking_lastmonth_day': 'กลุ่มสามารถจองสนามเดิมได้ภายในวันที่',
            'refund_group_day': 'กลุ่มสามารถขอยกเลิกและทำการคืนเงินได้ภายในวันที่',
            'open_time': 'เวลาเปิดทำการ',
            'close_time': 'เวลาปิดทำการ',
            'num_of_creategroup': 'จำนวนสมาชิกที่ใช้เพื่อสร้างกลุ่ม',
            'announce': 'ประกาศ',
            'contacts': 'ติดต่อ',
            'rules': 'กฎการใช้สนาม',
        }

    range_booking = forms.ChoiceField(
        choices=[
            (timedelta(days=1), "1 วัน"),
            (timedelta(days=3), "3 วัน"),
            (timedelta(days=5), "5 วัน"),
            (timedelta(days=7), "7 วัน"),
        ],
        label='ระยะเวลาในการจองล่วงหน้า'
    )

    payment_member_duration = forms.ChoiceField(
        choices=[
            (timedelta(minutes=1), "1 นาที"),
            (timedelta(minutes=3), "3 นาที"),
            (timedelta(minutes=5), "5 นาที"),
            (timedelta(minutes=10), "10 นาที"),
            (timedelta(minutes=30), "30 นาที"),
            (timedelta(hours=1), "1 ชั่วโมง"),
            (timedelta(days=1), "1 วัน"),
        ],
        label='ระยะเวลาชำระเงินหลังจากจองสนาม สำหรับสมาชิก'
    )

    payment_guest_duration = forms.ChoiceField(
        choices=[
            (timedelta(minutes=1), "1 นาที"),
            (timedelta(minutes=3), "3 นาที"),
            (timedelta(minutes=5), "5 นาที"),
            (timedelta(minutes=10), "10 นาที"),
            (timedelta(minutes=30), "30 นาที"),
            (timedelta(hours=1), "1 ชั่วโมง"),
        ],
        label='ระยะเวลาชำระเงินหลังจากจองสนาม สำหรับบุคคลทั่วไป'
    )

    payment_group_duration = forms.ChoiceField(
        choices=[
            (timedelta(minutes=1), "1 นาที"),
            (timedelta(minutes=3), "3 นาที"),
            (timedelta(minutes=5), "5 นาที"),
            (timedelta(minutes=10), "10 นาที"),
            (timedelta(minutes=30), "30 นาที"),
            (timedelta(hours=1), "1 ชั่วโมง"),
        ],
        label='ระยะเวลาชำระเงินหลังจากจองสนาม สำหรับกลุ่ม'
    )

    refund_member_duration = forms.ChoiceField(
        choices=[
            (timedelta(days=1), "1 วัน"),
            (timedelta(days=3), "3 วัน"),
            (timedelta(days=5), "5 วัน"),
            (timedelta(days=7), "7 วัน"),
        ],
        label='ระยะเวลาขอยกเลิกและคืนเงินก่อนเวลาที่จอง สำหรับสมาชิก'
    )


class FestivalForm(forms.ModelForm):
    class Meta:
        model = FestivalInfo
        fields = ('__all__')
        widgets = {
            'fes_date_start': forms.SelectDateWidget(),
            'fes_date_end': forms.SelectDateWidget(),
        }
        labels = {
            'fes_name': 'ชื่อเทศกาล',
            'fes_date_start': 'ตั้งแต่วันที่',
            'fes_date_end': 'ถึงวันที่',
        }

    payment_member_duration_fes = forms.ChoiceField(
        choices=[
            (timedelta(minutes=1), "1 นาที"),
            (timedelta(minutes=3), "3 นาที"),
            (timedelta(minutes=5), "5 นาที"),
            (timedelta(minutes=10), "10 นาที"),
            (timedelta(minutes=30), "30 นาที"),
            (timedelta(hours=1), "1 ชั่วโมง"),
            (timedelta(days=1), "1 วัน"),
        ],
        label='ระยะเวลาชำระเงินหลังจากจองสนาม สำหรับสมาชิก ในช่วงเวลาพิเศษ'
    )

    refund_member_duration_fes = forms.ChoiceField(
        choices=[
            (timedelta(days=1), "1 วัน"),
            (timedelta(days=3), "3 วัน"),
            (timedelta(days=5), "5 วัน"),
            (timedelta(days=7), "7 วัน"),
        ],
        label='ระยะเวลาขอยกเลิกและคืนเงินก่อนเวลาที่จอง สำหรับสมาชิก ในช่วงเวลาพิเศษ'
    )

class EachCourtForm(forms.ModelForm):
    class Meta:
        model = EachCourtInfo
        fields = ('__all__')
        widgets = {
            'time_ds_start': forms.TimeInput(format='%H:%M'),
            'time_ds_end': forms.TimeInput(format='%H:%M'),
        }
        labels = {
            'court_number': 'สนามที่',
            'price_normal': 'ราคาปกติ',
            'price_ds_mem': 'ส่วนลดสมาชิก',
            'price_ds_group': 'ส่วนลดกลุ่ม',
            'price_ds_time': 'ส่วนลดในช่วงเวลา',
            'time_ds_start': 'ส่วนลดเวลาจาก',
            'time_ds_end': 'ถึง',
            'is_maintain': 'ปิดปรับปรุงสนาม',
        }


class BookingForm(forms.Form):
    date = forms.ChoiceField(label='วันที่')
    from_time = forms.ChoiceField(label='จากเวลา')
    to_time = forms.ChoiceField(label='ถึงเวลา')
    court = forms.ChoiceField(label='สนามที่')
    name = forms.CharField(label='ชื่อ')
    tel = forms.CharField(label='เบอร์โทรศัพท์')
    email = forms.EmailField(label='อีเมล')



class MemberForm(forms.ModelForm):

    class Meta:
        model = Member
        fields = ('username', 'first_name', 'last_name', 'email',
                  'is_active', 'tel', 'public', 'virtualid')
        widgets = {
            'birthday': forms.SelectDateWidget(years=range(datetime.now().year-100, datetime.now().year+1))
        }
        labels = {
            'username': 'ชื่อผู้ใช้งาน',
            'first_name': 'ชื่อ',
            'last_name': 'นามสกุล',
            'email': 'อีเมล',
            'is_active': 'ให้สมาชิกอยู่ในระบบ',
            'tel': 'เบอร์โทรศัพท์',
            'public': 'เปิดเป็นสาธารณะ',
            'virtualid': 'ID',
        }


class BookingDetailForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('__all__')
        labels = {
            'name': 'ชื่อผู้ใช้งาน',
            'email': 'ชื่อ',
            'tel': 'นามสกุล',
            'email': 'อีเมล',
            'member': 'สมาชิก',
            'group': 'กลุ่ม',
            'court': 'สนามที่',
            'booking_datetime': 'วันเวลาที่จอง',
            'exp_datetime': 'ชำระเงินภายใน',
            'refund_datetime': 'ขอคืนเงินภายใน',
            'price_normal': 'ราคาปกติ',
            'price_ds': 'ส่วนลด',
            'price_pay': 'ราคาที่ต้องจ่าย',
            # 0 = booking, 1 = success, 2 = refunded, 3 = checkedPayment false(checking not found transaction)
            'payment_state': 'สถานะการจ่ายเงิน (0-ยังไม่จ่ายเงิน 1-ชำระเงินแล้ว 2-ขอคืนเงิน 3-การชำระเงินผิดพลาด)',
            'timestamp': 'เวลาที่จอง',
            'bookingid': 'bookingID',
            'paymentid': 'paymentID',
            'refundid': 'refundID',
            'is_deleted': 'ลบการจองนี้',
        }


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['group_name', 'announce', 'is_active', 'is_public']
        labels = {
            'group_name': 'ชื่อกลุ่ม',
            'announce': 'ประกาศ',
            'is_active': 'ให้กลุ่มอยู่ในระบบ',
            'is_public': 'เปิดเป็นสาธารณะ',
        }

class CheckPaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ('__all__')


class IncomeForm(forms.Form):
    year = forms.ChoiceField()


class UsageForm(forms.Form):
    year_month = forms.ChoiceField()
