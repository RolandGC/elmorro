import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, ListView, UpdateView, DeleteView, FormView
from core.security.mixins import PermissionMixin, ModuleMixin

from core.pos.forms import BoxForm, Box, BoxFormListView



class BoxListView(PermissionMixin, FormView):
    template_name = 'frm/box/list.html'
    permission_required = 'view_box'
    form_class = BoxFormListView

    def post(self, request, *args, **kwargs):
        data = {}  # Inicializa data como un diccionario vacío
        action = request.POST['action']
        try:
            if action == 'search':
                data = []
                search = Box.objects.filter()
                start_date = request.POST['start_date']
                end_date = request.POST['end_date']
                if len(start_date) and len(end_date):
                    search = search.filter(date_joined__range=[start_date, end_date])
                for a in search:
                    data.append(a.toJSON())
            else:
                data['error'] = 'No ha ingresado unqa opción'  # Ahora data es un diccionario válido
        except Exception as e:
            data = {'error': str(e)}  # Asigna el error como un valor del diccionario
        print(data)
        json_data = json.dumps(data, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Cierre de Caja'
        context['create_url'] = reverse_lazy('box_create')
        return context

class BoxCreateView(PermissionMixin, CreateView):
    model = Box
    template_name = 'frm/box/create.html'
    form_class = BoxForm
    success_url = reverse_lazy('box_list')
    permission_required = 'add_box'

    def validate_data(self):
        data = {'valid': 'True'}
        try:
            type = self.request.POST['type']
            obj = self.request.POST['obj'].strip()
            if type == 'data_close':
                if Box.objects.filter(name__iaxact=obj):
                    data['valid'] = True
        except:
            pass
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'add':
                box = Box()
                box.date_close = request.POST['date_close']
                box.hours_close = request.POST['hours_close']
                box.cash_sale = float(request.POST['cash_sale'])
                box.bills = float(request.POST['bills'])
                box.sale_card = float(request.POST['sale_card'])
                box.initial_box = float(request.POST['initial_box'])
                box.box_final = float(request.POST['box_final'])
                box.desc = request.POST['desc']
                box.save()
            elif action == 'validate_data':
                return self.validate_data()
            else:
                data['error'] = 'No ha ingresado datos'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['title'] = 'Nuevo registro de un cierre de caja'
        context['action'] = 'add'
        return context


class BoxUpdateView(PermissionMixin, UpdateView):
    model = Box
    template_name = 'frm/box/create.html'
    form_class = BoxForm
    success_url = reverse_lazy('box_list')
    permission_required = 'change_box'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def validate_data(self):
        data = {'valid': True}
        try:
            type = self.request.POST['type']
            obj = self.request.POST['obj'].strip()
            id = self.get_object().id
            if type == 'name':
                if Box.objects.filter(name__iexact=obj).exclude(id=id):
                    data['valid'] = False
        except:
            pass
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'edit':
                data = self.get_form().save()
            elif action == 'validate_data':
                return self.validate_data()
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['title'] = 'Edición de un registro Caja'
        context['action'] = 'edit'
        return context


class BoxDeleteView(PermissionRequiredMixin, DeleteView):
    model = Box
    template_name = 'frm/box/delete.html'
    success_url = reverse_lazy('box_list')
    permission_required = 'delete_box'

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.get_object().delete()
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Notificacion de eliminación'
        context['list_url'] = self.success_url
        return context
