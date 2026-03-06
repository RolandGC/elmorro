from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Sum
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from core.security.mixins import ModuleMixin
from core.user.models import User
from core.pos.models import Sale, SalePayment, PaymentMethodModel
from datetime import datetime


class UserSalesReportView(LoginRequiredMixin, ModuleMixin, TemplateView):
    template_name = 'frm/user_sales_report/list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reporte de Cobranzas por Usuario'
        return context
    
    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action')
        
        try:
            if action == 'search_users':
                # Obtener solo usuarios con los roles: Supervisor, Vendedor y Reparto
                # Excluir: Cliente y Administrador
                from django.contrib.auth.models import Group
                
                allowed_groups = Group.objects.filter(name__in=['Supervisor', 'Vendedor', 'Reparto'])
                users = User.objects.filter(groups__in=allowed_groups).distinct().values('id', 'full_name', 'dni').order_by('full_name')
                
                data = list(users)
                
            elif action == 'get_user_sales':
                user_id = request.POST.get('user_id')
                date_from = request.POST.get('date_from')
                date_to = request.POST.get('date_to')
                
                # Construir query base
                sales_query = Sale.objects.filter(employee_id=user_id)
                
                # Filtrar por fechas si se proporcionan
                if date_from:
                    try:
                        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                        sales_query = sales_query.filter(date_joined__date__gte=date_from_obj)
                    except:
                        pass
                
                if date_to:
                    try:
                        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                        sales_query = sales_query.filter(date_joined__date__lte=date_to_obj)
                    except:
                        pass
                
                # Agrupar por método de pago usando SalePayment
                sales_by_method = {}
                total_general = 0
                total_cantidad = 0
                
                # Inicializar con todos los métodos de pago activos
                for pm in PaymentMethodModel.objects.filter(is_active=True):
                    sales_by_method[pm.code] = {
                        'name': pm.name,
                        'total': 0.00,
                        'cantidad': 0,
                        'count': 0,
                        'sales': []
                    }
                
                # Agrupar ventas por método de pago a través de SalePayment
                for sale in sales_query.select_related('client', 'employee'):
                    # Obtener los pagos de esta venta
                    sale_payments = sale.payments.select_related('payment_method').all()
                    
                    # Contar cantidad de productos
                    cant = sale.saledetail_set.aggregate(total_cant=Sum('cant'))['total_cant'] or 0
                    total_cantidad += cant
                    total_general += float(sale.total)
                    
                    sale_data = {
                        'id': sale.id,
                        'nro': sale.nro(),
                        'date': sale.date_joined.strftime('%d/%m/%Y %H:%M'),
                        'type_voucher': sale.get_type_voucher_display(),
                        'client': sale.client.user.full_name if sale.client else 'Sin cliente',
                        'subtotal': float(sale.subtotal),
                        'total_dscto': float(sale.total_dscto),
                        'total': float(sale.total),
                        'cantidad': cant
                    }
                    
                    if sale_payments.exists():
                        for sp in sale_payments:
                            method_code = sp.payment_method.code
                            if method_code not in sales_by_method:
                                sales_by_method[method_code] = {
                                    'name': sp.payment_method.name,
                                    'total': 0.00,
                                    'cantidad': 0,
                                    'count': 0,
                                    'sales': []
                                }
                            sales_by_method[method_code]['total'] += float(sp.amount)
                            sales_by_method[method_code]['count'] += 1
                            sales_by_method[method_code]['cantidad'] += cant
                            sales_by_method[method_code]['sales'].append(sale_data)
                    else:
                        # Venta sin pagos registrados (legacy)
                        if 'sin_pago' not in sales_by_method:
                            sales_by_method['sin_pago'] = {
                                'name': 'Sin pago registrado',
                                'total': 0.00,
                                'cantidad': 0,
                                'count': 0,
                                'sales': []
                            }
                        sales_by_method['sin_pago']['total'] += float(sale.total)
                        sales_by_method['sin_pago']['count'] += 1
                        sales_by_method['sin_pago']['cantidad'] += cant
                        sales_by_method['sin_pago']['sales'].append(sale_data)
                
                # Obtener información del usuario
                try:
                    user = User.objects.get(id=user_id)
                    user_info = {
                        'id': user.id,
                        'full_name': user.full_name,
                        'dni': user.dni
                    }
                except:
                    user_info = {}
                
                data = {
                    'user': user_info,
                    'sales_by_method': sales_by_method,
                    'total_general': total_general,
                    'total_cantidad': total_cantidad,
                    'date_from': date_from,
                    'date_to': date_to
                }
                
            elif action == 'get_summary':
                # Obtener resumen general de todos los usuarios
                date_from = request.POST.get('date_from')
                date_to = request.POST.get('date_to')
                
                # Construir filtro de pagos
                payments_query = SalePayment.objects.select_related('sale__employee', 'payment_method').all()
                
                if date_from:
                    try:
                        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                        payments_query = payments_query.filter(sale__date_joined__date__gte=date_from_obj)
                    except:
                        pass
                
                if date_to:
                    try:
                        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                        payments_query = payments_query.filter(sale__date_joined__date__lte=date_to_obj)
                    except:
                        pass
                
                # Agrupar por usuario y método de pago
                users_summary = {}
                
                for sp in payments_query:
                    if not sp.sale.employee:
                        continue
                    
                    uid = sp.sale.employee.id
                    user_name = sp.sale.employee.full_name
                    method = sp.payment_method.code
                    method_name = sp.payment_method.name
                    
                    if uid not in users_summary:
                        users_summary[uid] = {
                            'user_name': user_name,
                            'total_vendido': 0.00,
                            'total_transacciones': 0,
                            'metodos': {}
                        }
                    
                    if method not in users_summary[uid]['metodos']:
                        users_summary[uid]['metodos'][method] = {
                            'name': method_name,
                            'total': 0.00,
                            'count': 0
                        }
                    
                    users_summary[uid]['total_vendido'] += float(sp.amount)
                    users_summary[uid]['total_transacciones'] += 1
                    users_summary[uid]['metodos'][method]['total'] += float(sp.amount)
                    users_summary[uid]['metodos'][method]['count'] += 1
                
                # Convertir a lista ordenada por total vendido
                summary_list = sorted(
                    users_summary.values(),
                    key=lambda x: x['total_vendido'],
                    reverse=True
                )
                
                data = {
                    'summary': summary_list,
                    'total_general': sum(u['total_vendido'] for u in summary_list),
                    'total_transacciones': sum(u['total_transacciones'] for u in summary_list)
                }
        
        except Exception as e:
            data['error'] = str(e)
        
        return JsonResponse(data, safe=False)
