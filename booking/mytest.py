from . import models
from django.utils import timezone

def test():
    booking_date = timezone.now().date()
    q_allcourtinfo = models.AllCourtInfo.objects.all()[0]
    q_fes = models.FestivalInfo.objects.all()
    in_fes =False

    for fes_obj in q_fes:
        fes_start = fes_obj.fes_date_start
        fes_end = fes_obj.fes_date_end
        if booking_date >= fes_start and booking_date <= fes_end:
            exp = fes_obj.payment_member_duration_fes
            refund_dur = fes_obj.refund_member_duration_fes
            in_fes = True

    if not in_fes:
        exp = q_allcourtinfo.payment_member_duration
        refund_dur = q_allcourtinfo.refund_member_duration

    print(exp)
    print(refund_dur)