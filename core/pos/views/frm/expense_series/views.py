import json

from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, FormView

from core.pos.forms import ExpenseSeriesForm
from core.pos.models import ExpenseSeries
from core.security.mixins import PermissionMixin


class ExpenseSeriesListView(PermissionMixin, FormView):
    template_name = 'frm/expense_series/list.html'
    form_class = ExpenseSeriesForm
    permission_required = 'view_expenseseries'

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action')
        try:
            if action == 'search':
                data = []
                term = request.POST.get('term', '')
                search = ExpenseSeries.objects.all()
                if term:
                    search = search.filter(name__icontains=term)
                for expense_series in search:
                    data.append(expense_series.toJSON())
            else:
                data['error'] = 'Acción inválida'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('expense_series_create')
        context['title'] = 'Series de Gastos'
        return context


class ExpenseSeriesCreateView(PermissionMixin, CreateView):
    model = ExpenseSeries
    template_name = 'frm/expense_series/create.html'
    form_class = ExpenseSeriesForm
    success_url = reverse_lazy('expense_series_list')
    permission_required = 'add_expenseseries'

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        data = {}
        
        if action == 'add':
            form = ExpenseSeriesForm(request.POST)
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
                        'title': 'Nueva Serie de Gastos',
                        'action': 'add'
                    }
                    return self.render_to_response(context)
        else:
            data['error'] = 'Acción inválida'
            return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_url'] = self.success_url
        context['title'] = 'Nueva Serie de Gastos'
        context['action'] = 'add'
        return context


class ExpenseSeriesUpdateView(PermissionMixin, UpdateView):
    model = ExpenseSeries
    template_name = 'frm/expense_series/create.html'
    form_class = ExpenseSeriesForm
    success_url = reverse_lazy('expense_series_list')
    permission_required = 'change_expenseseries'

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        data = {}
        
        if action == 'edit':
            expense_series = self.get_object()
            form = ExpenseSeriesForm(request.POST, instance=expense_series)
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
                        'title': 'Editar Serie de Gastos',
                        'action': 'edit',
                        'object': expense_series
                    }
                    return self.render_to_response(context)
        else:
            data['error'] = 'Acción inválida'
            return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_url'] = self.success_url
        context['title'] = 'Editar Serie de Gastos'
        context['action'] = 'edit'
        return context


class ExpenseSeriesDeleteView(PermissionMixin, DeleteView):
    model = ExpenseSeries
    template_name = 'frm/expense_series/delete.html'
    success_url = reverse_lazy('expense_series_list')
    permission_required = 'delete_expenseseries'

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
        context['title'] = 'Eliminar Serie de Gastos'
        context['list_url'] = self.success_url
        return context
