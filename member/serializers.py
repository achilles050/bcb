from rest_framework import serializers
from rest_framework.serializers import UUIDField
from . import models


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Member
        fields = ['username', 'first_name', 'last_name',
                  'email', 'tel', 'birthday', 'gender']


class CreateGroupMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Member
        # fields = ['id', 'username']
        fields = ['virtualid', 'first_name']


class GroupDataSerializer(serializers.ModelSerializer):
    public = serializers.BooleanField(source='is_public')

    class Meta:
        model = models.Group
        # fields = ['announce', 'is_public']
        fields = ['public', ]
