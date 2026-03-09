import json
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from core.pos.models import PaymentMethodModel
from core.pos.forms import PaymentMethodForm
from core.security.mixins import PermissionMixin


class PaymentMethodListView(PermissionMixin, ListView):
    model = PaymentMethodModel
    template_name = 'frm/paymentmethod/list.html'
    permission_required = 'view_paymentmethodmodel'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('paymentmethod_create')
        context['title'] = 'Listado de Formas de Pago'
        return context


class PaymentMethodCreateView(PermissionMixin, CreateView):
    model = PaymentMethodModel
    template_name = 'frm/paymentmethod/create.html'
    form_class = PaymentMethodForm
    success_url = reverse_lazy('paymentmethod_list')
    permission_required = 'add_paymentmethodmodel'

    def validate_data(self):
        data = {'valid': True}
        try:
            type = self.request.POST['type']
            obj = self.request.POST['obj'].strip()
            if type == 'name':
                if PaymentMethodModel.objects.filter(name__iexact=obj):
                    data['valid'] = False
            elif type == 'code':
                if PaymentMethodModel.objects.filter(code__iexact=obj):
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
        context['title'] = 'Nuevo registro de una Forma de Pago'
        context['action'] = 'add'
        return context


class PaymentMethodUpdateView(PermissionMixin, UpdateView):
    model = PaymentMethodModel
    template_name = 'frm/paymentmethod/create.html'
    form_class = PaymentMethodForm
    success_url = reverse_lazy('paymentmethod_list')
    permission_required = 'change_paymentmethodmodel'

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
                if PaymentMethodModel.objects.filter(name__iexact=obj).exclude(pk=id):
                    data['valid'] = False
            elif type == 'code':
                if PaymentMethodModel.objects.filter(code__iexact=obj).exclude(pk=id):
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
        context['title'] = 'Editar Forma de Pago'
        context['action'] = 'edit'
        return context


class PaymentMethodDeleteView(PermissionMixin, DeleteView):
    model = PaymentMethodModel
    template_name = 'frm/paymentmethod/delete.html'
    success_url = reverse_lazy('paymentmethod_list')
    permission_required = 'delete_paymentmethodmodel'

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
