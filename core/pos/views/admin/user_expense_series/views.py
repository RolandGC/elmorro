import json

from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, FormView

from core.pos.forms import UserExpenseSeriesForm
from core.pos.models import UserExpenseSeries
from core.security.mixins import PermissionMixin


class UserExpenseSeriesListView(PermissionMixin, FormView):
    template_name = 'admin/user_expense_series/list.html'
    form_class = UserExpenseSeriesForm
    permission_required = 'view_userexpenseseries'

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action')
        try:
            if action == 'search':
                data = []
                term = request.POST.get('term', '')
                search = UserExpenseSeries.objects.all()
                if term:
                    search = search.filter(user__full_name__icontains=term)
                for user_expense_series in search:
                    data.append(user_expense_series.toJSON())
            else:
                data['error'] = 'Acción inválida'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('user_expense_series_create')
        context['title'] = 'Administración de Asignación de Series de Gastos'
        return context


class UserExpenseSeriesCreateView(PermissionMixin, CreateView):
    model = UserExpenseSeries
    template_name = 'admin/user_expense_series/create.html'
    form_class = UserExpenseSeriesForm
    success_url = reverse_lazy('user_expense_series_list')
    permission_required = 'add_userexpenseseries'

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        data = {}
        
        if action == 'add':
            form = UserExpenseSeriesForm(request.POST)
            if form.is_valid():
                instance = form.save()
                # Si es AJAX, devolver JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    data = instance.toJSON()
                    return HttpResponse(json.dumps(data), content_type='application/json')
                else:
                    # Si es POST normal, redirigir
                    return super().form_valid(form)
            else:
                # Convertir errores del formulario a diccionario
                errors = {}
                for field, field_errors in form.errors.items():
                    errors[field] = [str(error) for error in field_errors]
                
                # Si es AJAX, devolver JSON con errores
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    data['error'] = errors
                    return HttpResponse(json.dumps(data), content_type='application/json')
                else:
                    # Si es POST normal, renderizar template con errores
                    context = {
                        'form': form,
                        'list_url': self.success_url,
                        'title': 'Asignar Serie de Gastos a Usuario',
                        'action': 'add'
                    }
                    return self.render_to_response(context)
        else:
            data['error'] = 'Acción inválida'
            return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_url'] = self.success_url
        context['title'] = 'Asignar Serie de Gastos a Usuario'
        context['action'] = 'add'
        return context


class UserExpenseSeriesUpdateView(PermissionMixin, UpdateView):
    model = UserExpenseSeries
    template_name = 'admin/user_expense_series/create.html'
    form_class = UserExpenseSeriesForm
    success_url = reverse_lazy('user_expense_series_list')
    permission_required = 'change_userexpenseseries'

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        data = {}
        
        if action == 'edit':
            user_expense_series = self.get_object()
            form = UserExpenseSeriesForm(request.POST, instance=user_expense_series)
            if form.is_valid():
                instance = form.save()
                # Si es AJAX, devolver JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    data = instance.toJSON()
                    return HttpResponse(json.dumps(data), content_type='application/json')
                else:
                    # Si es POST normal, redirigir
                    return super().form_valid(form)
            else:
                # Convertir errores del formulario a diccionario
                errors = {}
                for field, field_errors in form.errors.items():
                    errors[field] = [str(error) for error in field_errors]
                
                # Si es AJAX, devolver JSON con errores
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    data['error'] = errors
                    return HttpResponse(json.dumps(data), content_type='application/json')
                else:
                    # Si es POST normal, renderizar template con errores
                    context = {
                        'form': form,
                        'list_url': self.success_url,
                        'title': 'Editar Asignación de Serie de Gastos',
                        'action': 'edit',
                        'object': user_expense_series
                    }
                    return self.render_to_response(context)
        else:
            data['error'] = 'Acción inválida'
            return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_url'] = self.success_url
        context['title'] = 'Editar Asignación de Serie de Gastos'
        context['action'] = 'edit'
        return context


class UserExpenseSeriesDeleteView(PermissionMixin, DeleteView):
    model = UserExpenseSeries
    template_name = 'admin/user_expense_series/delete.html'
    success_url = reverse_lazy('user_expense_series_list')
    permission_required = 'delete_userexpenseseries'

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.get_object().delete()
            # Si es AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return HttpResponse(json.dumps(data), content_type='application/json')
            else:
                # Si es POST normal, redirigir
                return super().delete(request, *args, **kwargs)
        except Exception as e:
            data['error'] = str(e)
            return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminar Asignación de Serie de Gastos'
        context['list_url'] = self.success_url
        return context
