from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Sum
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from core.security.mixins import ModuleMixin
from core.user.models import User
from core.pos.models import Sale
from core.pos.choices import payment_method
from datetime import datetime


class UserSalesReportView(LoginRequiredMixin, ModuleMixin, TemplateView):
    template_name = 'frm/user_sales_report/list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reporte de Ventas por Usuario'
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
                
                # Agrupar por método de pago
                sales_by_method = {}
                total_general = 0
                total_cantidad = 0
                
                # Inicializar con todos los métodos de pago
                for method_code, method_name in payment_method:
                    sales_by_method[method_code] = {
                        'name': method_name,
                        'total': 0.00,
                        'cantidad': 0,
                        'count': 0,
                        'sales': []
                    }
                
                # Agrupar ventas por método de pago
                for sale in sales_query.select_related('client', 'employee', 'payment_bank'):
                    method = sale.payment_method
                    
                    sales_by_method[method]['total'] += float(sale.total)
                    sales_by_method[method]['count'] += 1
                    total_general += float(sale.total)
                    
                    # Contar cantidad de productos
                    cant = sale.saledetail_set.aggregate(total_cant=Sum('cant'))['total_cant'] or 0
                    sales_by_method[method]['cantidad'] += cant
                    total_cantidad += cant
                    
                    # Agregar detalles de la venta
                    sales_by_method[method]['sales'].append({
                        'id': sale.id,
                        'nro': sale.nro(),
                        'date': sale.date_joined.strftime('%d/%m/%Y %H:%M'),
                        'type_voucher': sale.get_type_voucher_display(),
                        'client': sale.client.user.full_name if sale.client else 'Sin cliente',
                        'subtotal': float(sale.subtotal),
                        'total_dscto': float(sale.total_dscto),
                        'total': float(sale.total),
                        'cantidad': cant
                    })
                
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
                
                sales_query = Sale.objects.all()
                
                # Filtrar por fechas
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
                
                # Agrupar por usuario y método de pago
                users_summary = {}
                
                for sale in sales_query.select_related('employee'):
                    if not sale.employee:
                        continue
                    
                    user_id = sale.employee.id
                    user_name = sale.employee.full_name
                    method = sale.payment_method
                    method_name = sale.get_payment_method_display()
                    
                    if user_id not in users_summary:
                        users_summary[user_id] = {
                            'user_name': user_name,
                            'total_vendido': 0.00,
                            'total_transacciones': 0,
                            'metodos': {}
                        }
                    
                    if method not in users_summary[user_id]['metodos']:
                        users_summary[user_id]['metodos'][method] = {
                            'name': method_name,
                            'total': 0.00,
                            'count': 0
                        }
                    
                    users_summary[user_id]['total_vendido'] += float(sale.total)
                    users_summary[user_id]['total_transacciones'] += 1
                    users_summary[user_id]['metodos'][method]['total'] += float(sale.total)
                    users_summary[user_id]['metodos'][method]['count'] += 1
                
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
