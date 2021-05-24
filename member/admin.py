from django.contrib import admin
from . import models
from booking import models as bk_models
# Register your models here.

admin.site.register(models.Member)
admin.site.register(models.Group)
admin.site.register(models.GroupMember)
admin.site.register(models.Request)
