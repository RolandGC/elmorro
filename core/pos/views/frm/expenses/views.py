import json

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, FormView

from core.pos.forms import ExpensesForm, Expenses
from core.reports.forms import ReportForm
from core.security.mixins import PermissionMixin


class ExpensesListView(PermissionMixin, FormView):
    template_name = 'frm/expenses/list.html'
    permission_required = 'view_expenses'
    form_class = ReportForm

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'search':
                data = []
                search = Expenses.objects.filter(user=request.user)
                start_date = request.POST['start_date']
                end_date = request.POST['end_date']
                if len(start_date) and len(end_date):
                    search = search.filter(date_joined__range=[start_date, end_date])
                for a in search:
                    data.append(a.toJSON())
            else:
                data['error'] = 'No ha ingresado una opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('expenses_create')
        context['title'] = 'Listado de Gastos'
        return context


class ExpensesCreateView(PermissionMixin, CreateView):
    model = Expenses
    template_name = 'frm/expenses/create.html'
    form_class = ExpensesForm
    success_url = reverse_lazy('expenses_list')
    permission_required = 'add_expenses'

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'add':
                form = self.get_form()
                if form.is_valid():
                    expense = form.save(commit=False)
                    expense.user = request.user
                    expense.save()
                    data = expense.toJSON()
                else:
                    error_messages = []
                    for field, errors in form.errors.items():
                        for error in errors:
                            error_messages.append(f"{field}: {error}")
                    data['error'] = ' | '.join(error_messages) if error_messages else 'Errores en el formulario'
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            import traceback
            traceback.print_exc()
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['title'] = 'Nuevo registro de un Gasto'
        context['action'] = 'add'
        return context


class ExpensesUpdateView(PermissionMixin, UpdateView):
    model = Expenses
    template_name = 'frm/expenses/create.html'
    form_class = ExpensesForm
    success_url = reverse_lazy('expenses_list')
    permission_required = 'change_expenses'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'edit':
                form = self.get_form()
                if form.is_valid():
                    expense = form.save(commit=False)
                    # Mantener el usuario original si no fue establecido, o asignar el actual
                    if not expense.user:
                        expense.user = request.user
                    expense.save()
                    data = expense.toJSON()
                else:
                    error_messages = []
                    for field, errors in form.errors.items():
                        for error in errors:
                            error_messages.append(f"{field}: {error}")
                    data['error'] = ' | '.join(error_messages) if error_messages else 'Errores en el formulario'
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            import traceback
            traceback.print_exc()
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['title'] = 'Edición de un Gasto'
        context['action'] = 'edit'
        return context


class ExpensesDeleteView(PermissionMixin, DeleteView):
    model = Expenses
    template_name = 'frm/expenses/delete.html'
    success_url = reverse_lazy('expenses_list')
    permission_required = 'delete_expenses'

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
