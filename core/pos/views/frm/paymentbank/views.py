import json

from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from core.pos.models import PaymentBank
from core.pos.forms import PaymentBankForm
from core.security.mixins import PermissionMixin


class PaymentBankListView(PermissionMixin, ListView):
    model = PaymentBank
    template_name = 'frm/paymentbank/list.html'
    permission_required = 'view_paymentbank'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('paymentbank_create')
        context['title'] = 'Listado de Bancos de Pago'
        return context


class PaymentBankCreateView(PermissionMixin, CreateView):
    model = PaymentBank
    template_name = 'frm/paymentbank/create.html'
    form_class = PaymentBankForm
    success_url = reverse_lazy('paymentbank_list')
    permission_required = 'add_paymentbank'

    def validate_data(self):
        data = {'valid': True}
        try:
            type = self.request.POST['type']
            obj = self.request.POST['obj'].strip()
            if type == 'name':
                if PaymentBank.objects.filter(name__iexact=obj):
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
        context['title'] = 'Nuevo registro de un Banco de Pago'
        context['action'] = 'add'
        return context


class PaymentBankUpdateView(PermissionMixin, UpdateView):
    model = PaymentBank
    template_name = 'frm/paymentbank/create.html'
    form_class = PaymentBankForm
    success_url = reverse_lazy('paymentbank_list')
    permission_required = 'change_paymentbank'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def validate_data(self):
        data = {'valid': True}
        try:
            type = self.request.POST['type']
            id = self.get_object().id
            obj = self.request.POST['obj'].strip()
            if type == 'name':
                if PaymentBank.objects.filter(name__iexact=obj).exclude(pk=id):
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
        context['title'] = 'Editar Banco de Pago'
        context['action'] = 'edit'
        return context


class PaymentBankDeleteView(PermissionMixin, DeleteView):
    model = PaymentBank
    success_url = reverse_lazy('paymentbank_list')
    permission_required = 'delete_paymentbank'

    def delete(self, request, *args, **kwargs):
        data = {}
        try:
            super().delete(request, *args, **kwargs)
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')
