from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from uuid import uuid4
from django.conf import settings

# Create your models here.


class Group(models.Model):
    class Meta:
        db_table = 'bcb_group'
    group_name = models.CharField(max_length=100, unique=True)
    announce = models.CharField(max_length=500)
    # change when pay to next month court to True(use cronjob check this change below)
    is_continue = models.BooleanField(default=False)
    # change when not pay next month(use cronjob to change) False = not use now(not show in list group)
    is_active = models.BooleanField(default=False)
    # for public this group
    is_public = models.BooleanField(default=False)


class GroupMember(models.Model):
    class Meta:
        db_table = 'bcb_groupmember'
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, null=True, related_name='groups', db_constraint=False)
    member = models.ForeignKey(
        'Member', on_delete=models.CASCADE, related_name='members')
    # for show role in group h = header, m = member, j=join
    role = models.CharField(max_length=1, default='')
    on_court = models.BooleanField(default=False)


class Member(User):

    def randomint():
        return uuid4().hex[:8]

    class Meta:
        db_table = 'bcb_member'
    user_ptr = models.OneToOneField(auto_created=True, on_delete=models.CASCADE,
                                    parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, db_constraint=False)
    tel = models.CharField(max_length=10)
    birthday = models.DateField(null=True)
    gender = models.CharField(max_length=10)
    # for show in creategroup request
    public = models.BooleanField(default=True)
    virtualid = models.CharField(
        max_length=8, default=randomint, unique=True)


class Request(models.Model):

    class Meta:
        db_table = 'bcb_request'
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, null=True, db_constraint=False)
    sender = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name='receiver')
    # when request to create group = 0, join = 1, change header = 2
    action = models.IntegerField(default=None)
    # change to True when action that request
    read = models.BooleanField(default=False)
