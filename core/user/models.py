# -*- codign: utf-8 -*-
import os
import uuid
from django.core.exceptions import ValidationError
import requests
from crum import get_current_request
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms.models import model_to_dict

from config import settings


class User(AbstractUser):
    full_name = models.CharField(max_length=150, blank=False, verbose_name="Nombres completos")
    dni = models.CharField(max_length=13, unique=True, verbose_name='Dni o RUC')
    image = models.ImageField(upload_to='users/%Y/%m/%d', verbose_name='Imagen', null=True, blank=True)
    is_change_password = models.BooleanField(default=False)
    token = models.UUIDField(primary_key=False, editable=False, null=True, blank=True, default=uuid.uuid4, unique=True)
    email = models.EmailField(blank=True, null=True)

        
    def toJSON(self):
        item = model_to_dict(self, exclude=['last_login', 'token', 'password', 'user_permissions'])
        item['image'] = self.get_image()
        item['full_name'] = self.full_name
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['groups'] = self.get_groups()
        item['last_login'] = None if self.last_login is None else self.last_login.strftime('%Y-%m-%d')
        return item

    def generate_token(self):
        return uuid.uuid4()

    def get_image(self):
        if self.image:
            return '{}{}'.format(settings.MEDIA_URL, self.image)
        return '{}{}'.format(settings.STATIC_URL, 'img/default/logoMorroHoriztl.png')

    def remove_image(self):
        try:
            if self.image:
                os.remove(self.image.path)
        except:
            pass
        finally:
            self.image = None

    def delete(self, using=None, keep_parents=False):
        try:
            os.remove(self.image.path)
        except:
            pass
        super(User, self).delete()

    def get_groups(self):
        data = []
        for i in self.groups.all():
            data.append({'id': i.id, 'name': i.name})
        return data

    def get_group_id_session(self):
        try:
            request = get_current_request()
            return int(request.session['group'].id)
        except:
            return 0

    def set_group_session(self):
        try:
            request = get_current_request()
            groups = request.user.groups.all()
            if groups:
                if 'group' not in request.session:
                    request.session['infobyip'] = self.infobyip()
                    request.session['group'] = groups[0]
        except:
            pass

    def create_or_update_password(self, password):
        try:
            if self.pk is None:
                self.set_password(password)
            else:
                user = User.objects.get(pk=self.pk)
                if user.password != password:
                    self.set_password(password)
        except:
            pass

    def is_client(self):
        try:
            if hasattr(self, 'client'):
                return True
        except:
            pass
        return False

    def infobyip(self):
        response = {'ipaddress': '', 'location': '', 'isp': '', 'countrycode': ''}
        try:
            request = requests.get('https://wtfismyip.com/json').json()
            response = {
                'ipaddress': request['YourFuckingIPAddress'],
                'location': request['YourFuckingLocation'],
                'isp': request['YourFuckingISP'],
                'countrycode': request['YourFuckingCountryCode'],
            }
        except:
            pass
        return response

    def __str__(self):
        return self.full_name