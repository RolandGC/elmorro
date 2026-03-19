import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, ListView, UpdateView, DeleteView, FormView, View
from core.security.mixins import PermissionMixin, ModuleMixin
from django.template.loader import get_template
from weasyprint import HTML, CSS
from config import settings
import os
import logging

logger = logging.getLogger(__name__)

from core.pos.forms import BoxForm, Box, BoxFormListView
from core.pos.models import Company



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
            from datetime import datetime
            from django.db.models import Sum
            
            user = self.request.user
            fecha_actual = datetime.now()
            
            from core.pos.models import Expenses, SalePayment
            
            # Obtener el último cierre de caja del usuario
            ultimo_cierre = Box.objects.filter(user=user).order_by('-datetime_close').first()
            
            if ultimo_cierre and ultimo_cierre.datetime_close:
                fecha_inicio = ultimo_cierre.datetime_close
            else:
                # Si no hay cierre anterior, usar el inicio del día
                fecha_inicio = datetime.combine(fecha_actual.date(), datetime.min.time())
            
            # Obtener todos los pagos en el rango de fecha, agrupados por moneda y método
            pagos = SalePayment.objects.filter(
                sale__employee=user,
                sale__date_joined__range=[fecha_inicio, fecha_actual]
            ).values('currency__code', 'currency__name', 'currency__symbol', 'payment_method__code').annotate(total=Sum('amount'))
            
            # Crear diccionarios con montos por moneda y método
            total_pagos = 0
            monto_soles = 0.0
            monto_dolares = 0.0
            efectivo_soles = 0.0
            efectivo_dolares = 0.0
            yape_soles = 0.0
            plin_soles = 0.0
            transferencia_soles = 0.0
            transferencia_dolares = 0.0
            deposito_soles = 0.0
            deposito_dolares = 0.0
            
            for pago in pagos:
                codigo = pago['currency__code']
                metodo = pago['payment_method__code']
                monto = float(pago['total']) or 0
                
                total_pagos += monto
                
                # Identificar soles y dólares
                es_soles = codigo.upper() in ['PEN', 'SOL']
                es_dolares = codigo.upper() in ['USD', 'DOL']
                
                # Agregar al total general
                if es_soles:
                    monto_soles += monto
                elif es_dolares:
                    monto_dolares += monto
                
                # Agregar por método de pago
                if metodo and metodo.lower() == 'efectivo':
                    if es_soles:
                        efectivo_soles += monto
                    elif es_dolares:
                        efectivo_dolares += monto
                elif metodo and metodo.lower() == 'yape':
                    if es_soles:
                        yape_soles += monto
                elif metodo and metodo.lower() == 'plin':
                    if es_soles:
                        plin_soles += monto
                elif metodo and metodo.lower() == 'transferencia':
                    if es_soles:
                        transferencia_soles += monto
                    elif es_dolares:
                        transferencia_dolares += monto
                elif metodo and metodo.lower() == 'deposito':
                    if es_soles:
                        deposito_soles += monto
                    elif es_dolares:
                        deposito_dolares += monto
            
            # Guardar montos separados por moneda y método
            data['monto_soles'] = round(monto_soles, 2)
            data['monto_dolares'] = round(monto_dolares, 2)
            data['initial_box_soles'] = 0.0
            data['initial_box_dolares'] = 0.0
            data['efectivo_soles'] = round(efectivo_soles, 2)
            data['efectivo_dolares'] = round(efectivo_dolares, 2)
            data['yape_soles'] = round(yape_soles, 2)
            data['plin_soles'] = round(plin_soles, 2)
            data['transferencia_soles'] = round(transferencia_soles, 2)
            data['transferencia_dolares'] = round(transferencia_dolares, 2)
            data['deposito_soles'] = round(deposito_soles, 2)
            data['deposito_dolares'] = round(deposito_dolares, 2)
            
            # Calcular gastos del período (siempre en soles)
            total_gastos = Expenses.objects.filter(
                user=user,
                date_joined__range=[fecha_inicio.date(), fecha_actual.date()]
            ).aggregate(total=Sum('valor'))['total'] or 0
            data['bills'] = round(float(total_gastos), 2)
            
            # Mantener campos antiguos para compatibilidad (todos en 0)
            data['efectivo'] = 0
            data['transferencia'] = 0
            data['deposito'] = 0
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
            elif action == 'add' or not action:
                # El formulario se envía normalmente (sin action específica)
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
                
                # Manejar los nuevos campos de moneda dual
                initial_box_soles = float(request.POST.get('initial_box_soles', 0)) or 0
                initial_box_dolares = float(request.POST.get('initial_box_dolares', 0)) or 0
                efectivo_soles = float(request.POST.get('efectivo_soles', 0)) or 0
                efectivo_dolares = float(request.POST.get('efectivo_dolares', 0)) or 0
                transferencia_soles = float(request.POST.get('transferencia_soles', 0)) or 0
                transferencia_dolares = float(request.POST.get('transferencia_dolares', 0)) or 0
                deposito_soles = float(request.POST.get('deposito_soles', 0)) or 0
                deposito_dolares = float(request.POST.get('deposito_dolares', 0)) or 0
                bills = float(request.POST.get('bills', 0)) or 0
                box_final_soles = float(request.POST.get('box_final_soles', 0)) or 0
                box_final_dolares = float(request.POST.get('box_final_dolares', 0)) or 0
                
                # Asignar valores al modelo
                box.initial_box_soles = initial_box_soles
                box.initial_box_dolares = initial_box_dolares
                box.efectivo_soles = efectivo_soles
                box.efectivo_dolares = efectivo_dolares
                box.transferencia_soles = transferencia_soles
                box.transferencia_dolares = transferencia_dolares
                box.deposito_soles = deposito_soles
                box.deposito_dolares = deposito_dolares
                box.yape = float(request.POST.get('yape', 0)) or 0
                box.plin = float(request.POST.get('plin', 0)) or 0
                box.bills = bills
                box.box_final_dolares = box_final_dolares
                box.box_final_soles = box_final_soles
                
                box.desc = request.POST.get('desc', '')
                box.save()
                data['status'] = 'ok'
                data['message'] = 'Cierre de caja guardado exitosamente'
            elif action == 'validate_data':
                return self.validate_data()
            else:
                data['error'] = 'No ha ingresado datos'
        except Exception as e:
            import traceback
            traceback.print_exc()
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['title'] = 'Nuevo registro de un cierre de caja'
        context['action'] = 'add'
        return context


class BoxPrintTicketView(LoginRequiredMixin, View):
    """Genera un PDF con los datos del cierre de caja"""
    success_url = reverse_lazy('box_list')

    def get(self, request, *args, **kwargs):
        try:
            box = Box.objects.get(pk=self.kwargs['pk'])
            company = Company.objects.first()
            context = {
                'box': box,
                'company': company
            }
            template = get_template('frm/box/print/ticket.html')
            html_template = template.render(context).encode(encoding="UTF-8")
            url_css = os.path.join(settings.BASE_DIR, 'static/lib/bootstrap-4.6.0/css/bootstrap.min.css')
            pdf_file = HTML(string=html_template, base_url=request.build_absolute_uri()).write_pdf(
                stylesheets=[CSS(url_css)], presentational_hints=True)
            response = HttpResponse(pdf_file, content_type='application/pdf')
            return response
        except Exception as e:
            logger.error(f"Error generating box print: {str(e)}", exc_info=True)
        return HttpResponseRedirect(self.success_url)


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
            from datetime import datetime
            from django.db.models import Sum
            
            user = self.request.user
            fecha_actual = datetime.now()
            
            from core.pos.models import Expenses, SalePayment
            
            # Obtener el último cierre de caja del usuario
            ultimo_cierre = Box.objects.filter(user=user).order_by('-datetime_close').first()
            
            if ultimo_cierre and ultimo_cierre.datetime_close:
                fecha_inicio = ultimo_cierre.datetime_close
            else:
                # Si no hay cierre anterior, usar el inicio del día
                fecha_inicio = datetime.combine(fecha_actual.date(), datetime.min.time())
            
            # Obtener todos los pagos en el rango de fecha, agrupados por moneda
            pagos = SalePayment.objects.filter(
                sale__employee=user,
                sale__date_joined__range=[fecha_inicio, fecha_actual]
            ).values('currency__code', 'currency__name', 'currency__symbol').annotate(total=Sum('amount'))
            
            # Crear diccionario con montos por moneda
            montos_por_moneda = {}
            total_pagos = 0
            for pago in pagos:
                codigo = pago['currency__code']
                nombre = pago['currency__name']
                simbolo = pago['currency__symbol']
                monto = float(pago['total']) or 0
                
                montos_por_moneda[codigo] = {
                    'nombre': nombre,
                    'simbolo': simbolo,
                    'monto': round(monto, 2)
                }
                total_pagos += monto
            
            # Guardar resumen de monedas en formato legible
            data['montos_por_moneda'] = montos_por_moneda
            data['resumen_monedas'] = ', '.join([
                f"{v['simbolo']} {v['monto']:.2f}" for v in montos_por_moneda.values()
            ]) if montos_por_moneda else 'Sin pagos'
            
            # Calcular gastos del período
            total_gastos = Expenses.objects.filter(
                user=user,
                date_joined__range=[fecha_inicio.date(), fecha_actual.date()]
            ).aggregate(total=Sum('valor'))['total'] or 0
            data['bills'] = round(float(total_gastos), 2)
            
            # Calcular el total del box (pagos - gastos)
            data['box_final'] = round(total_pagos - float(total_gastos), 2)
            
            # Mantener campos antiguos para compatibilidad (todos en 0)
            data['efectivo'] = 0
            data['yape'] = 0
            data['plin'] = 0
            data['transferencia'] = 0
            data['deposito'] = 0
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
