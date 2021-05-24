from . import models
from booking import models as booking_models
from . import serializers as s
from .form import LoginForm
from .token import account_activation_token
from . import group
from func.disable import DisableCSRF

from booking.book import AddMonths

from datetime import date, datetime, time
import json
import urllib.parse

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt  # csrf_clear
from django.contrib.auth import authenticate, login, logout, get_user
from django.http.response import JsonResponse
from django.utils import timezone
from django.urls import reverse_lazy

from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import send_mail

from django.contrib.auth.views import PasswordResetView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.utils.translation import gettext_lazy as _

from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes


class Index(APIView):
    def get(self, request):
        info = booking_models.AllCourtInfo.objects.all()[0]
        announce = info.announce
        contacts = info.contacts
        rules = info.rules
        return JsonResponse({'announce': announce, 'contacts': contacts, 'rules': rules, 'member': str(request.user)})


class Register(APIView):
    def post(self, request):
        data = request.data
        username = data['username']
        password = data['password']
        password2 = data['confirmpass']
        firstname = data['firstname']
        lastname = data['lastname']
        email = data['email']
        # tel = '00000221'
        tel = ''  # data['tel']
        try:
            user = models.Member.objects.create_user(
                username=username, password=password, email=email, is_active=True)
            user.first_name = firstname
            user.last_name = lastname
            user.tel = tel
            user.is_active = False
            user.save()
        except Exception as e:
            print(e)
            return JsonResponse({'msg': 'Try again!!!'})

        context = {
            'user': username,
            'email': email,
            'protocol': 'https' if request.is_secure() else "http",
            'domain': request.get_host(),
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user)
        }
        text = render_to_string('registration/activate_email.txt', context)
        send_mail(
            'Verify email to Activate your account',
            message=text,
            recipient_list=[email],
            from_email=None,
            fail_silently=False,
        )
        return JsonResponse({'msg': 'Register Success Pls activate your email'})


class ActivateEmail(APIView):
    def get(self, request, uidb64, token):
        uid = urlsafe_base64_decode(uidb64).decode()
        try:
            user = models.Member.objects.get(pk=uid)
        except:
            msg = 'This Account Not Found!!!'
            return render(request, 'registration/result.html', {'msg': msg})
        if account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            msg = 'Activate Email Success'
            return render(request, 'registration/result.html', {'msg': msg})
        else:
            msg = 'Link not correct or expired'
            return render(request, 'registration/result.html', {'msg': msg})


class Login(APIView):
    def get(self, request):
        return render(request, 'login.html', {'form': LoginForm})

    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        auth = authenticate(username=username, password=password)
        if auth is not None:
            login(request, auth)
            return JsonResponse({'username': username}, status=200)
        else:
            return JsonResponse({'message': 'try again'}, status=404)


def Logout(request):
    try:
        print('going to logout')
        logout(request)
        print('logouted')
        return JsonResponse({'msg': 'logout successfully'}, status=200)
        # return HttpResponse('ok logouted')
    except Exception as e:
        print(e)
        return JsonResponse({'msg': 'error'}, status=404)


class Profile(APIView):
    def get(self, request):
        try:
            if request.user.id is not None:
                print(f'This is {request.user} profile')
                member = models.Member.objects.get(pk=request.user.id)
                mem_serializer = s.MemberSerializer(member)
                return JsonResponse(mem_serializer.data)
            return JsonResponse({'message': 'Pls login. (GET)'})
        except Exception as e:
            print(f'Error {e}')
            return JsonResponse({'message': 'Error(GET)'})

    def put(self, request):
        try:
            if request.user.id is not None:
                member_obj = models.Member.objects.get(pk=request.user.id)
                mem_serializer = s.MemberSerializer(
                    member_obj, data=request.data)
                if mem_serializer.is_valid():
                    mem_serializer.save()
                    return JsonResponse(mem_serializer.data)
                return JsonResponse({'message': 'NOT CHANGE'})
        except Exception as e:
            print(f'Error {e}')
            return JsonResponse({'message': 'Error(POST)'})


class Creategroup(APIView):
    def get(self, request):
        try:
            if request.user.id is None:
                return JsonResponse({'msg': 'Login before create group'})
            mem_q = models.Member.objects.filter(
                is_active=True).filter(public=True).exclude(username=request.user)
            mem_s = s.CreateGroupMemberSerializer(mem_q, many=True)
            return JsonResponse(mem_s.data, safe=False)
        except Exception as e:
            print(f'Error = {e}')
            return JsonResponse({'msg': 'Error (GET)'})

    def post(self, request):
        q_allcourt = booking_models.AllCourtInfo.objects.all()[0]
        number_creategroup = q_allcourt.num_of_creategroup
        if request.user.id is None:
            return JsonResponse({'msg': 'Login before create group'})

        q_header = models.Member.objects.get(username=request.user)
        member = request.data['member']
        group_name = request.data['group_name']

        if group_name == '':
            return JsonResponse({'msg': f'pls fill your group name!!!'}, status=400)

        if models.GroupMember.objects.filter(role='h').filter(member_id=request.user.id).exists():
            return JsonResponse({'msg': f'Can not create group because you are header in another group'}, status=400)

        if len(member) != number_creategroup:
            return JsonResponse({'msg': f'Error create group with {number_creategroup} member!!!'}, status=400)

        for value in member:
            if models.Member.objects.filter(virtualid=value).exists():
                pass
            else:
                return JsonResponse({'message': f'Error this userid {value} not found'}, status=404)

        group_obj, create = models.Group.objects.get_or_create(
            group_name=group_name, is_active=False)

        if not create:
            return JsonResponse({'message': f'Error this group name {group_obj.group_name} exists '}, status=400)
        else:
            models.GroupMember.objects.get_or_create(
                group=group_obj, member=q_header, role='h')

        for value in member:
            virtualid = value
            q_receiver = models.Member.objects.get(virtualid=virtualid)
            models.Request.objects.create(
                group=group_obj, sender=q_header, receiver=q_receiver, action=0)
        return JsonResponse({'msg': f'create group {group_obj.group_name} success waiting for accept from another member'})


class AllGroup(APIView):
    def get(self, request):
        try:
            query = models.Group.objects.filter(
                is_active=True)
            d = dict()
            l = []
            for value in query:
                q_group_member = models.GroupMember.objects.filter(
                    group=value.id).filter(role='m')
                q_header = models.GroupMember.objects.filter(
                    group=value.id).filter(role='h')[0]

                member_list = []
                for innner_value in q_group_member:
                    member_list.append({'id': innner_value.member.virtualid,
                                        'firstname': innner_value.member.first_name
                                        })
                detail_dict = dict({'announce': value.announce,
                                    'member': member_list
                                    })

                l.append({'group_name': value.group_name,
                          'header': q_header.member.first_name,
                          'public': value.is_public,
                          'detail': detail_dict if value.is_public is True else {}
                          })

            d['data'] = l
            return JsonResponse(d)
        except Exception as e:
            print(f'Error {e}')
            return JsonResponse({'message': 'Error(GET)'}, safe=False)


class MyGroup(APIView):
    def get(self, request, groupname):
        try:
            groupname = urllib.parse.unquote_plus(groupname)
            mygroup = models.Group.objects.get(group_name=groupname)
            groupid = mygroup.id
            is_member = group.group_mem_per(
                groupid=groupid, memberid=request.user.id)
            is_header = group.group_head_per(
                groupid=groupid, memberid=request.user.id)
            if is_member:
                if is_header:
                    role = 'header'
                else:
                    role = 'member'
            else:
                if request.user.id is not None:
                    if models.GroupMember.objects.filter(role='j').filter(member_id=request.user.id).filter(
                            group_id=groupid).exists():
                        role = 'waiting'
                    else:
                        role = 'free'
                else:
                    role = 'guest'

            q_group_member = models.GroupMember.objects.filter(
                group_id=groupid).filter(role='m')
            q_group_header = models.GroupMember.objects.filter(
                group_id=groupid).filter(role='h')[0]

            member_list = []
            announce = ""
            groupbooking_list = []
            thismonth_booking_list = []
            nextmonth_booking_list = []
            payment_list = []

            if mygroup.is_public is True or is_header or is_member:
                if is_header:
                    announce = mygroup.announce
                    for i, innner_value in enumerate(q_group_member):
                        member_list.append({'number': i+1,
                                            'id': innner_value.member.virtualid,
                                            'firstname': innner_value.member.first_name,
                                            'delete': False
                                            })
                else:
                    for i, innner_value in enumerate(q_group_member):
                        member_list.append({'number': i+1,
                                            'id': innner_value.member.virtualid,
                                            'firstname': innner_value.member.first_name
                                            })

                date_now = datetime.now().date()
                date_nextmonth = AddMonths(date_now, 1)

                thismonth_booking_list = group.group_booking_by_date(
                    mydate=date_now, mygroup=mygroup)
                nextmonth_booking_list = group.group_booking_by_date(
                    mydate=date_nextmonth, mygroup=mygroup)
                payment_list = group.group_payment(mygroup=mygroup)

            d = dict()
            d = {'group_name': mygroup.group_name,
                 'header': q_group_header.member.first_name,
                 'public': mygroup.is_public,
                 'role': role,
                 'detail': {"announce": announce, "member": member_list,
                            "groupbooking": {"this_month": thismonth_booking_list,
                                             "next_month": nextmonth_booking_list},
                            "payment": payment_list}
                 }

            return JsonResponse(d)
        except Exception as e:
            print(f'Error {e}')
            return JsonResponse({'message': 'Error(GET)'}, safe=False)

    def post(self, request, groupname):
        try:
            groupname = urllib.parse.unquote_plus(groupname)
            if request.user.id is not None:
                mygroup = models.Group.objects.get(group_name=groupname)
                groupid = mygroup.id
                mem = models.Member.objects.get(pk=request.user.id)
                header = models.GroupMember.objects.filter(
                    group=mygroup).filter(role='h')[0].member
                is_member = group.group_mem_per(
                    groupid=groupid, memberid=request.user.id)
                is_header = group.group_head_per(
                    groupid=groupid, memberid=request.user.id)
                if is_header or is_member:
                    return JsonResponse({'msg': "You're already in this group"})

                obj, created = models.GroupMember.objects.get_or_create(
                    group=mygroup, member=mem, role='j')
                if created:
                    models.Request.objects.create(
                        sender=mem, receiver=header, action=1, group_id=obj.group_id)
                    return JsonResponse({'msg': 'join success waiting for accept from header this group'})
                else:
                    q_request = models.Request.objects.filter(
                        sender=mem, receiver=header, action=1, group_id=obj.group_id, read=0)
                    q_request.delete()
                    obj.delete()
                    return JsonResponse({'msg': 'cancel joining this group success'})
            else:
                return JsonResponse({'msg': 'pls login first'})
        except Exception as e:
            print(e)
            return JsonResponse({'msg': 'Error'})

    def put(self, request, groupname):
        groupname = urllib.parse.unquote_plus(groupname)
        mygroup = models.Group.objects.get(group_name=groupname)
        groupid = mygroup.id
        is_header = group.group_head_per(
            groupid=groupid, memberid=request.user.id)
        if is_header:
            group_serializer = s.GroupDataSerializer(
                mygroup, data=request.data)
            if group_serializer.is_valid():
                group_serializer.save()
                return JsonResponse(group_serializer.data)
            return JsonResponse({'message': 'NOT CHANGE'})
        else:
            return JsonResponse({'msg': 'permission denied'}, status=400)

    def delete(self, request, groupname):
        try:
            groupname = urllib.parse.unquote_plus(groupname)
            if request.user.id is not None:
                mygroup = models.Group.objects.get(group_name=groupname)
                groupid = mygroup.id

                is_member = group.group_mem_per(
                    groupid=groupid, memberid=request.user.id)
                is_header = group.group_head_per(
                    groupid=groupid, memberid=request.user.id)

                if is_member or is_header:
                    if is_header:
                        virtualid = request.GET.get('id', None)
                        if virtualid is not None:
                            member = models.Member.objects.get(
                                virtualid=virtualid)
                            msg = 'delete member'
                        else:
                            return JsonResponse({'msg': 'Error send not have membergroupid'}, status=400)
                    else:
                        member = models.Member.objects.get(id=request.user.id)
                        msg = 'leave group'
                    q_gm = models.GroupMember.objects.get(
                        group=mygroup, role='m', member=member)
                    q_gm.delete()
                    return JsonResponse({'msg': f'{msg} successful'})
                else:
                    return JsonResponse({'msg': 'You dont have permission !!!'}, status=400)

        except Exception as e:
            print(e)
            return JsonResponse({'msg': 'Error'})


class Request(APIView):

    def get(self, request):
        try:
            if request.user.id is not None:
                query = models.Request.objects.filter(
                    receiver=request.user).filter(read=False)
                mydict = dict()
                l = list()
                for i in query:
                    if i.action == 0:
                        msg = 'accept create group'
                    elif i.action == 1:
                        msg = 'join group'
                    else:
                        msg = ''
                    l.append(
                        {'id': i.id, 'sender': i.sender.first_name, 'msg': msg, 'group': i.group.group_name})
                mydict['data'] = l
                return JsonResponse(mydict)
            return HttpResponse('Pls login (GET)')
        except Exception as e:
            print('error = ', e)
            return HttpResponse('Error (GET)')

    def post(self, request):
        try:
            if request.user.id is not None:
                myid = request.data['id']
                accept = request.data['accept']
                query = models.Request.objects.get(pk=myid)
                q_group = models.Group.objects.get(pk=query.group_id)
                if query.read == True:
                    return JsonResponse({'msg': 'try again'}, status=400)
                if query.action == 0:  # accept create group
                    if accept is True:
                        if request.user.id == query.receiver.id:
                            pass
                        else:
                            return JsonResponse({'msg': 'you not have permission'}, status=400)
                        q_allcourt = booking_models.AllCourtInfo.objects.all()[
                            0]
                        number_creategroup = q_allcourt.num_of_creategroup
                        mem = models.Member.objects.get(pk=query.receiver)

                        obj, created = models.GroupMember.objects.get_or_create(
                            group=q_group, member=mem, role='m')
                        if created:
                            query.read = 1
                            query.save()
                        if len(models.GroupMember.objects.filter(role='m').filter(group=q_group)) == number_creategroup:
                            q_group.is_active = True
                            q_group.save()
                    else:
                        q_group.delete()

                elif query.action == 1:  # accept join group
                    if group.group_head_per(memberid=request.user.id, groupid=q_group.id):
                        q_gm = models.GroupMember.objects.get(
                            member_id=query.sender, group_id=q_group.id, role='j')

                        if accept is True:
                            q_gm.role = 'm'
                            q_gm.save()
                            query.read = 1
                            query.save()
                        else:
                            q_gm.delete()
                            query.read = 1
                            query.save()
                    else:
                        return JsonResponse({'msg': 'you not have permission (header only)'}, status=400)

                return JsonResponse({'msg': 'ok'})
            return JsonResponse({'msg': 'pls login'})

        except Exception as e:
            print('error = ', e)
            return HttpResponse('Error (POST)')
