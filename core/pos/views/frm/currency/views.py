import json
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from core.pos.models import Currency
from core.pos.forms import CurrencyForm
from core.security.mixins import PermissionMixin


class CurrencyListView(PermissionMixin, ListView):
    model = Currency
    template_name = 'frm/currency/list.html'
    permission_required = 'view_currency'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('currency_create')
        context['title'] = 'Listado de Monedas'
        return context


class CurrencyCreateView(PermissionMixin, CreateView):
    model = Currency
    template_name = 'frm/currency/create.html'
    form_class = CurrencyForm
    success_url = reverse_lazy('currency_list')
    permission_required = 'add_currency'

    def validate_data(self):
        data = {'valid': True}
        try:
            type = self.request.POST['type']
            obj = self.request.POST['obj'].strip()
            if type == 'name':
                if Currency.objects.filter(name__iexact=obj):
                    data['valid'] = False
            elif type == 'code':
                if Currency.objects.filter(code__iexact=obj):
                    data['valid'] = False
        except:
            pass
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'add':
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
        context['title'] = 'Nuevo registro de una Moneda'
        context['action'] = 'add'
        return context


class CurrencyUpdateView(PermissionMixin, UpdateView):
    model = Currency
    template_name = 'frm/currency/create.html'
    form_class = CurrencyForm
    success_url = reverse_lazy('currency_list')
    permission_required = 'change_currency'

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
                if Currency.objects.filter(name__iexact=obj).exclude(pk=id):
                    data['valid'] = False
            elif type == 'code':
                if Currency.objects.filter(code__iexact=obj).exclude(pk=id):
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
        context['title'] = 'Editar Moneda'
        context['action'] = 'edit'
        return context


class CurrencyDeleteView(PermissionMixin, DeleteView):
    model = Currency
    template_name = 'frm/currency/delete.html'
    success_url = reverse_lazy('currency_list')
    permission_required = 'delete_currency'

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
