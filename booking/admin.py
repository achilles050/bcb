from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.AllCourtInfo)
admin.site.register(models.EachCourtInfo)
admin.site.register(models.Booking)
admin.site.register(models.Payment)
admin.site.register(models.Refund)
