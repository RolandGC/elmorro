import json
import os
import subprocess
from datetime import datetime

from django.core.files import File
from django.db import connection
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DeleteView, TemplateView

from config import settings
from core.security.mixins import PermissionMixin
from core.security.models import DatabaseBackups


class DatabaseBackupsListView(PermissionMixin, TemplateView):
    template_name = 'databasebackups/list.html'
    permission_required = 'view_databasebackups'

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'search':
                data = []
                search = DatabaseBackups.objects.filter()
                start_date = request.POST['start_date']
                end_date = request.POST['end_date']
                if len(start_date) and len(end_date):
                    search = search.filter(date_joined__range=[start_date, end_date])
                for a in search:
                    data.append(a.toJSON())
            else:
                data['error'] = 'No ha ingresado una opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de respaldos de la base de datos'
        context['create_url'] = reverse_lazy('databasebackups_create')
        return context


# class DatabaseBackupsCreateView(PermissionMixin, TemplateView):
#     template_name = 'databasebackups/create.html'
#     success_url = reverse_lazy('databasebackups_list')
#     permission_required = 'add_databasebackups'

#     def create_backup_sqlite(self):
#         file = ''
#         data = {}
#         try:
#             db_name = connection.settings_dict['NAME']
#             data_now = '{0:%Y-%m-%d_%H-%M-%S}'.format(datetime.now())  # Modificar el formato del nombre del archivo
#             name_backup = "{}_{}.db".format('backup', data_now)
#             script = 'sqlite3 {} ".backup {}"'.format(db_name, name_backup)  # Modificar el script para ejecutar SQLite3
#             subprocess.call(script, shell=True)
#             file = os.path.join(settings.BASE_DIR, name_backup)
#             db = DatabaseBackups()
#             db.user = self.request.user
#             db.archive.save(name_backup, File(open(file, 'rb')), save=False)
#             db.save()
#         except Exception as e:
#             data['error'] = str(e)
#         finally:
#             if len(file):
#                 os.remove(file)
#         return data

#     def post(self, request, *args, **kwargs):
#         data = {}
#         action = request.POST.get('action', '')  # Utilizar get para evitar excepciones si 'action' no está presente
#         try:
#             if action == 'add':
#                 db_type = connection.vendor
#                 if db_type == 'sqlite':
#                     data = self.create_backup_sqlite()
#                 else:
#                     data['error'] = 'No se ha podido sacar el respaldo de la base de datos {}'.format(db_type)
#             else:
#                 data['error'] = 'No ha seleccionado ninguna opción'
#         except Exception as e:
#             data['error'] = str(e)
#         return HttpResponse(json.dumps(data), content_type='application/json')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data()
#         context['list_url'] = self.success_url
#         context['title'] = 'Nuevo registro de un Respaldo de Base de Datos'
#         context['action'] = 'add'
#         return context
class DatabaseBackupsCreateView(PermissionMixin, TemplateView):
    template_name = 'databasebackups/create.html'
    success_url = reverse_lazy('databasebackups_list')
    permission_required = 'add_databasebackups'

    def create_backup_sqlite(self):
        file = ''
        data = {}
        try:
            db_name = connection.settings_dict['NAME']
            data_now = '{0:%Y-%m-%d_%H-%M-%S}'.format(datetime.now())  # Modificar el formato del nombre del archivo
            name_backup = "{}_{}.db".format('backup', data_now)
            script = 'sqlite3 {} ".backup {}"'.format(db_name, name_backup)  # Modificar el script para ejecutar SQLite3
            subprocess.call(script, shell=True)
            file = os.path.join(settings.BASE_DIR, name_backup)
            db = DatabaseBackups()
            db.user = self.request.user
            db.archive.save(name_backup, File(open(file, 'rb')), save=False)
            db.save()
        except Exception as e:
            data['error'] = str(e)
        finally:
            if len(file):
                os.remove(file)
        return data

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action', '')  # Utilizar get para evitar excepciones si 'action' no está presente
        try:
            if action == 'add':
                db_type = connection.vendor
                if db_type == 'sqlite':
                    data = self.create_backup_sqlite()
                else:
                    data['error'] = 'No se ha podido sacar el respaldo de la base de datos {}'.format(db_type)
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_url'] = self.success_url
        context['title'] = 'Nuevo registro de un Respaldo de Base de Datos'
        context['action'] = 'add'
        return context
    
class DatabaseBackupsDeleteView(PermissionMixin, DeleteView):
    model = DatabaseBackups
    template_name = 'databasebackups/delete.html'
    success_url = reverse_lazy('databasebackups_list')
    permission_required = 'delete_databasebackups'

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.get_object().delete()
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Notificación de eliminación'
        context['list_url'] = self.success_url
        return context
