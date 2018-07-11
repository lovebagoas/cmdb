# coding: utf-8
import json
import requests
from pyzabbix import ZabbixAPI
from bs4 import BeautifulSoup
from mico.settings import ZABBIX_INFO, GRAFANA_URL, SENTRY_URL

from django.shortcuts import render,render_to_response,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User,Group
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from asset.models import UserProfile
from asset.utils import deny_resubmit
from django.forms import ModelForm
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


# Create your views here.
class EZUser(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.email = username + '@ezbuy.com'

    def create_zabbix(self, url, admin_user, admin_pass, usrgrpid):
        """
        :param url: URL of zabbix server
        :param admin_user: login name of zabbix admin
        :param admin_pass: login password of zabbix admin
        :param usrgrpid: zabbix groups attach to :username
        :return: None
        """
        za = ZabbixAPI(url)
        print '-- Zabbix Login: %s@%s' % (admin_user, url)
        za.login(admin_user, admin_pass)
        params = {
            'alias': self.username,
            'passwd': self.password,
            'usrgrps': [
                {'usrgrpid': usrgrpid}
            ]
        }
        print params
        resp = za.do_request(method='user.create', params=params)
        print resp

    def delete_zabbix(self, url, admin_user, admin_pass, usrgrpid):
        """Delete zabbix user.

        :param url: URL of zabbix server
        :param admin_user: login name of zabbix admin
        :param admin_pass: login password of zabbix admin
        :param usrgrpid: zabbix groups attach to :username
        :return: None
        """
        za = ZabbixAPI(url)
        print '-- Zabbix Login: %s@%s' % (admin_user, url)
        za.login(admin_user, admin_pass)

        # -- get user id
        params = {
            'filter': {
                'alias': self.username
            },
        }
        resp = za.do_request(method='user.get', params=params)
        try:
            userid = resp['result'][0]['userid']
        except IndexError:
            return None
        except Exception as e:
            print e
            return None

        # -- delete user id
        resp = za.do_request(method='user.delete', params=[userid])
        print resp

    def create_grafana(self, url):
        """
        :param url: URL of grafana
        :return: bool
        """
        req_url = url + '/api/admin/users'
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        data = dict(name=self.username, email=self.email, login=self.username, password=self.password)
        resp = requests.post(req_url, data=json.dumps(data), headers=headers)
        return resp.status_code == 200

    def delete_grafana(self, url):
        """
        :param url: URL of grafana
        :return: bool
        """
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        # -- get user id
        req_url = '%s/api/users' % (url,)
        resp = requests.get(req_url, headers=headers)
        try:
            for x in resp.json():
                if x['email'] == self.email:
                    userid = x['id']
                    break
            else:
                raise Exception('Not found user: %s' % self.email)
        except Exception as e:
            print e
            return True

        # -- delete user id
        req_url = '%s/api/admin/users/%s' % (url, userid)
        resp = requests.delete(req_url, headers=headers)
        return resp.status_code == 200

    def create_sentry(self, url):
        req_url = url + '/auth/login/sentry/'
        s = requests.session()
        resp = s.get(req_url)
        soup = BeautifulSoup(resp.content, 'html.parser')
        csrf = soup.select_one('form.form-stacked input[name="csrfmiddlewaretoken"]').get('value')
        op = 'register'

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://sentry.65dg.me/auth/login/sentry/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/64.0.3282.186 Safari/537.36',
        }
        data = dict(csrfmiddlewaretoken=csrf, op=op, username=self.email, password=self.password)
        resp2 = s.post(req_url, data=data, headers=headers)
        return resp2.status_code == 200


@login_required
def user_list(request):
    users_list = User.objects.all().order_by('username')
    paginator = Paginator(users_list,10)
    page = request.GET.get('page')

    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)

    return render(request,'user_list.html',{'user_list':contacts})

@login_required
@deny_resubmit(page_key='add_user')
def user_add_html(request):
    groups = Group.objects.all()
    return  render(request,'user_add.html',{'groups':groups})

@login_required
@deny_resubmit(page_key='add_user')
def user_add(request):
    try:
        name = request.POST.get('name')
        full_name = request.POST.get('full_name')
        password = request.POST.get('password')
        group_id = request.POST.getlist('group_id')
        phone = request.POST.get('phone')
        email = name + '@ezbuy.com'
        info = User.objects.create_user(username=name,password=password,first_name=full_name,email=email)
        UserProfile.objects.create(phone_number=phone, user=info)
        for id in group_id:
            info.groups.add(id)
        print '-------%s--%s-------%s--%s' % (name,full_name,group_id,phone)
        result = [{'add_user':'successful'}]
    except Exception, e:
        print e
        result = [{'add_user': 'failed'}]
    else:
        third = request.POST.getlist('third')
        if third:
            ez = EZUser(name, password)
            if u'zabbix' in third:
                # create zabbix user
                for zbx in ZABBIX_INFO:
                    try:
                        ez.create_zabbix(*zbx)
                        result.append({'add_user zabbix(%s)' % zbx[0]: 'successful'})
                    except Exception as e:
                        print e
                        result.append({'add_user zabbix(%s)' % zbx[0]: 'failed'})

            if u'statsd' in third:
                # create grafana user
                try:
                    code_g = ez.create_grafana(GRAFANA_URL)
                    if code_g:
                        result.append({'add_user grafana': 'successful'})
                    else:
                        raise Exception('Grafana response code %s' % code_g)
                except Exception as e:
                    print e
                    result.append({'add_user grafana': 'failed'})

            if u'sentry' in third:
                # create sentry user
                try:
                    code_s = ez.create_sentry(SENTRY_URL)
                    if code_s:
                        result.append({'add_user sentry': 'successful'})
                    else:
                        raise Exception('Sentry response code %s' % code_s)
                except Exception as e:
                    print e
                    result.append({'add_user sentry': 'failed'})

    return render(request,'getdata.html',{'result':result})

class user_edit_form(ModelForm):
    class Meta:
        model = User
        fields = ["username","first_name"]

@login_required
@deny_resubmit(page_key='edit_user')
def user_edit(request, id):
    user_info = User.objects.get(id=id)
    print '-----user_info---',user_info
    if request.method == 'GET':
        groups = Group.objects.all()
        return render(request,'user_edit.html',{'user_info':user_info,'groups':groups})
    elif request.method == 'POST':
        try:
            name = request.POST.get('name')
            full_name = request.POST.get('full_name')
            password = request.POST.get('password')
            group_id = request.POST.getlist('group_id')
            phone = request.POST.get('phone')
            email = request.POST.get('email')

            print '-------%s--%s-------%s--%s' % (name,full_name,group_id,phone)
            user_info.username = name
            user_info.first_name = full_name
            user_info.email = email
            phone_obj = UserProfile.objects.get(user=user_info)
            phone_obj.phone_number = phone
            phone_obj.save()
            if password != '':
                user_info.set_password(password)

            for id in group_id:
                user_info.groups.add(int(id))
            for info in user_info.groups.all():
                if str(info.id) not in group_id:
                    user_info.groups.remove(info.id)
            user_info.save()
            result = [{'user_update': 'successful'}]
        except Exception, e:
            print e
            result = [{'user_update': 'failed'}]
        return render(request, 'getdata.html', {'result': result})


@login_required
def user_is_active(request,id):
    user_info = User.objects.get(id=id)
    if user_info.is_active:
        user_info.is_active = False

        # -- Delete third party account
        ez = EZUser(user_info.username, None)
        # delete zabbix user
        for zbx in ZABBIX_INFO:
            try:
                ez.delete_zabbix(*zbx)
            except Exception as e:
                print e

        # delete grafana user
        try:
            ez.delete_grafana(GRAFANA_URL)
        except Exception as e:
            print e
    else:
        user_info.is_active = True

    user_info.save()
    return HttpResponseRedirect('/users/user_list/')




