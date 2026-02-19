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
                search = Box.objects.filter(user=request.user)
                start_date = request.POST['start_date']
                end_date = request.POST['end_date']
                if len(start_date) and len(end_date):
                    from datetime import datetime, timedelta
                    try:
                        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                        end_date_obj = end_date_obj + timedelta(days=1)
                        search = search.filter(date_joined__range=[start_date, end_date_obj.date()])
                    except:
                        search = search.filter(date_joined__range=[start_date, end_date])
                for a in search:
                    data.append(a.toJSON())
            else:
                data['error'] = 'No ha ingresado una opción'  # Ahora data es un diccionario válido
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial_values(self):
        """Retorna los valores iniciales para el formulario"""
        data = {}
        try:
            from datetime import date
            from django.db.models import Sum
            
            user = self.request.user
            fecha_actual = date.today()
            
            from core.pos.models import Sale, Expenses, PaymentsCtaCollect
            
            total_efectivo = Sale.objects.filter(
                employee=user,
                payment_condition='contado',
                payment_method='efectivo',
                date_joined__date=fecha_actual
            ).aggregate(total=Sum('total'))['total'] or 0
            data['efectivo'] = round(float(total_efectivo), 2)
            
            # Calcular yape
            total_yape = Sale.objects.filter(
                employee=user,
                payment_condition='contado',
                payment_method='yape',
                date_joined__date=fecha_actual
            ).aggregate(total=Sum('total'))['total'] or 0
            data['yape'] = round(float(total_yape), 2)
            
            # Calcular plin
            total_plin = Sale.objects.filter(
                employee=user,
                payment_condition='contado',
                payment_method='plin',
                date_joined__date=fecha_actual
            ).aggregate(total=Sum('total'))['total'] or 0
            data['plin'] = round(float(total_plin), 2)
            
            # Calcular transferencia
            total_transfer = Sale.objects.filter(
                employee=user,
                payment_condition='contado',
                payment_method='tarjeta_debito_credito',
                date_joined__date=fecha_actual
            ).aggregate(total=Sum('total'))['total'] or 0
            data['transferencia'] = round(float(total_transfer), 2)
            
            # Calcular deposito
            total_deposito = Sale.objects.filter(
                employee=user,
                payment_condition='contado',
                payment_method='efectivo_tarjeta',
                date_joined__date=fecha_actual
            ).aggregate(total=Sum('total'))['total'] or 0
            data['deposito'] = round(float(total_deposito), 2)
            
            # Calcular total de pagos de métodos
            total_pagos = (float(total_efectivo) + 
                    float(total_yape) + 
                    float(total_plin) + 
                    float(total_transfer) + 
                    float(total_deposito))
            
            # Calcular gastos del día
            total_gastos = Expenses.objects.filter(
                user=user,
                date_joined=fecha_actual
            ).aggregate(total=Sum('valor'))['total'] or 0
            data['bills'] = round(float(total_gastos), 2)
            
            # Calcular el total del box (pagos - gastos)
            data['box_final'] = round(total_pagos - float(total_gastos), 2)
        except Exception as e:
            import traceback
            traceback.print_exc()
            data['error'] = str(e)
        
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action', '')
        try:
            if action == 'get_initial_values':
                return self.get_initial_values()
            elif action == 'add':
                from datetime import datetime
                box = Box()
                box.user = request.user
                
                # Obtener datetime_close del POST
                datetime_str = request.POST.get('datetime_close', '')
                if datetime_str:
                    try:
                        # El navegador envía en formato: 2025-12-19T14:30
                        box.datetime_close = datetime.fromisoformat(datetime_str)
                    except:
                        box.datetime_close = datetime.now()
                else:
                    box.datetime_close = datetime.now()
                
                box.efectivo = float(request.POST.get('efectivo', 0))
                box.yape = float(request.POST.get('yape', 0))
                box.plin = float(request.POST.get('plin', 0))
                box.transferencia = float(request.POST.get('transferencia', 0))
                box.deposito = float(request.POST.get('deposito', 0))
                box.bills = float(request.POST.get('bills', 0))
                box.initial_box = float(request.POST.get('initial_box', 0))
                
                # Calcular box_final automáticamente: efectivo + yape + plin + transferencia + deposito + initial_box - bills
                box.box_final = float(box.efectivo) + float(box.yape) + float(box.plin) + float(box.transferencia) + float(box.deposito) + float(box.initial_box) - float(box.bills)
                
                box.desc = request.POST.get('desc', '')
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial_values(self):
        """Retorna los valores iniciales para el formulario"""
        data = {}
        try:
            from datetime import date
            from django.db.models import Sum
            
            user = self.request.user
            fecha_actual = date.today()
            
            from core.pos.models import Sale, Expenses, PaymentsCtaCollect
            
            total_efectivo = Sale.objects.filter(
                employee=user,
                payment_condition='contado',
                payment_method='efectivo',
                date_joined__date=fecha_actual
            ).aggregate(total=Sum('total'))['total'] or 0
            data['efectivo'] = round(float(total_efectivo), 2)
            
            # Calcular yape
            total_yape = Sale.objects.filter(
                employee=user,
                payment_condition='contado',
                payment_method='yape',
                date_joined__date=fecha_actual
            ).aggregate(total=Sum('total'))['total'] or 0
            data['yape'] = round(float(total_yape), 2)
            
            # Calcular plin
            total_plin = Sale.objects.filter(
                employee=user,
                payment_condition='contado',
                payment_method='plin',
                date_joined__date=fecha_actual
            ).aggregate(total=Sum('total'))['total'] or 0
            data['plin'] = round(float(total_plin), 2)
            
            # Calcular transferencia
            total_transfer = Sale.objects.filter(
                employee=user,
                payment_condition='contado',
                payment_method='tarjeta_debito_credito',
                date_joined__date=fecha_actual
            ).aggregate(total=Sum('total'))['total'] or 0
            data['transferencia'] = round(float(total_transfer), 2)
            
            # Calcular deposito
            total_deposito = Sale.objects.filter(
                employee=user,
                payment_condition='contado',
                payment_method='efectivo_tarjeta',
                date_joined__date=fecha_actual
            ).aggregate(total=Sum('total'))['total'] or 0
            data['deposito'] = round(float(total_deposito), 2)
            
            # Calcular total de pagos de métodos
            total_pagos = (float(total_efectivo) + 
                    float(total_yape) + 
                    float(total_plin) + 
                    float(total_transfer) + 
                    float(total_deposito))
            
            # Calcular gastos del día
            total_gastos = Expenses.objects.filter(
                user=user,
                date_joined=fecha_actual
            ).aggregate(total=Sum('valor'))['total'] or 0
            data['bills'] = round(float(total_gastos), 2)
            
            # Calcular el total del box (pagos - gastos)
            data['box_final'] = round(total_pagos - float(total_gastos), 2)
        except Exception as e:
            import traceback
            traceback.print_exc()
            data['error'] = str(e)
        
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action', '')
        try:
            if action == 'get_initial_values':
                return self.get_initial_values()
            elif action == 'edit':
                from datetime import datetime
                box = self.get_object()
                
                # Obtener datetime_close del POST
                datetime_str = request.POST.get('datetime_close', '')
                if datetime_str:
                    try:
                        # El navegador envía en formato: 2025-12-19T14:30
                        box.datetime_close = datetime.fromisoformat(datetime_str)
                    except:
                        pass
                
                box.efectivo = float(request.POST.get('efectivo', 0))
                box.yape = float(request.POST.get('yape', 0))
                box.plin = float(request.POST.get('plin', 0))
                box.transferencia = float(request.POST.get('transferencia', 0))
                box.deposito = float(request.POST.get('deposito', 0))
                box.bills = float(request.POST.get('bills', 0))
                box.initial_box = float(request.POST.get('initial_box', 0))
                
                # Calcular box_final automáticamente: efectivo + yape + plin + transferencia + deposito + initial_box - bills
                box.box_final = float(box.efectivo) + float(box.yape) + float(box.plin) + float(box.transferencia) + float(box.deposito) + float(box.initial_box) - float(box.bills)
                
                box.desc = request.POST.get('desc', '')
                box.save()
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
