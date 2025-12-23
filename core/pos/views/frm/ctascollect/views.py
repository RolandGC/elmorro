import json
from decimal import Decimal
from datetime import date, datetime
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DeleteView, CreateView, FormView

from core.pos.forms import *
from core.reports.forms import ReportForm
from core.security.mixins import PermissionMixin


class CtasCollectListView(PermissionMixin, FormView):
    template_name = 'frm/ctascollect/list.html'
    permission_required = 'view_ctascollect'
    form_class = ReportForm

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action')
        try:
            if action == 'search':
                data = []
                search = CtasCollect.objects.all()
                start_date = request.POST.get('start_date')
                end_date = request.POST.get('end_date')
                if start_date and end_date:
                    search = search.filter(date_joined__range=[start_date, end_date])
                for ctascollect in search:
                    data.append(ctascollect.toJSON())
            elif action == 'search_pays':
                data = []
                pos = 1
                for payment in PaymentsCtaCollect.objects.filter(ctascollect_id=request.POST.get('id')).order_by('id'):
                    payment_data = payment.toJSON()
                    payment_data['pos'] = pos
                    data.append(payment_data)
                    pos += 1
            elif action == 'delete_pay':
                id = request.POST.get('id')
                payment = PaymentsCtaCollect.objects.get(pk=id)
                ctascollect = payment.ctascollect
                payment.delete()
                ctascollect.validate_debt()
            else:
                data['error'] = 'No ha ingresado una opción válida'
        except Exception as e:
            data['error'] = str(e)
        # Serializar datos a una cadena JSON usando DjangoJSONEncoder
        json_data = json.dumps(data, cls=DjangoJSONEncoder)
        # Devolver respuesta JSON
        return HttpResponse(json_data, content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Cuentas por Cobrar'
        context['create_url'] = reverse_lazy('ctascollect_create')
        return context


class CtasCollectCreateView(PermissionMixin, CreateView):
    model = CtasCollect
    template_name = 'frm/ctascollect/create.html'
    form_class = PaymentsCtaCollectForm
    success_url = reverse_lazy('ctascollect_list')
    permission_required = 'add_ctascollect'

    class DjangoEncoder(DjangoJSONEncoder):
        def default(self, obj):
            if isinstance(obj, Decimal):
                return str(obj)  # Serializa los objetos Decimal como cadenas para evitar errores de serialización
            return super().default(obj)

    def post(self, request, *args, **kwargs):
        action = request.POST['action']
        data = {}
        try:
            if action == 'search_ctascollect':
                data = []
                term = request.POST['term']
                for i in CtasCollect.objects.filter(Q(sale__client__user__full_name__icontains=term) | Q(
                    sale__client__user__dni__icontains=term)
                                                    ).exclude(state=False)[0:10]:
                    item = i.toJSON()
                    item['text'] = i.__str__()
                    
                    # Verificar si la deuda está vencida (hoy o después)
                    is_overdue = date.today() >= i.end_date
                    item['is_overdue'] = is_overdue
                    item['days_overdue'] = (date.today() - i.end_date).days if is_overdue else 0
                    
                    data.append(item)
            elif action == 'add':
                with transaction.atomic():
                    ctascollect = CtasCollect.objects.get(pk=int(request.POST['ctascollect']))
                    payment_date = request.POST['date_joined']
                    payment_valor = Decimal(request.POST['valor'])
                    
                    # Verificar si la deuda está vencida (hoy o después)
                    payment_date_obj = datetime.strptime(payment_date, '%Y-%m-%d').date()
                    is_overdue = payment_date_obj >= ctascollect.end_date
                    
                    if is_overdue:
                        # Si está vencida o es el día de vencimiento, obligar a pagar el saldo completo
                        if payment_valor < ctascollect.saldo:
                            data['error'] = f'La deuda vence el {ctascollect.end_date.strftime("%d/%m/%Y")}. Debe pagar el saldo completo de S/. {ctascollect.saldo:.2f}'
                            return HttpResponse(json.dumps(data, cls=self.DjangoEncoder), content_type='application/json')
                    
                    payment = PaymentsCtaCollect()
                    payment.ctascollect_id = ctascollect.id
                    payment.date_joined = payment_date
                    payment.valor = payment_valor
                    payment.desc = request.POST['desc']
                    if len(payment.desc) == 0:
                        payment.desc = 'Sin detalles'
                    payment.save()
                    payment.ctascollect.validate_debt()
            else:
                data['error'] = 'No ha ingresado una opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data, cls=self.DjangoEncoder), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['title'] = 'Nuevo registro de un Pago'
        context['action'] = 'add'
        return context

class CtasCollectDeleteView(PermissionMixin, DeleteView):
    model = CtasCollect
    template_name = 'frm/ctascollect/delete.html'
    success_url = reverse_lazy('ctascollect_list')
    permission_required = 'delete_ctascollect'

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
