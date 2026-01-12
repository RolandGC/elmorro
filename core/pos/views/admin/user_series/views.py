import json

from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, FormView

from core.pos.forms import UserSeriesForm
from core.pos.models import UserSeries, Series
from core.security.mixins import PermissionMixin
from core.user.models import User


class UserSeriesListView(PermissionMixin, FormView):
    template_name = 'admin/user_series/list.html'
    form_class = UserSeriesForm
    permission_required = 'view_userseries'

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action')
        try:
            if action == 'search':
                data = []
                term = request.POST.get('term', '')
                search = UserSeries.objects.all()
                if term:
                    search = search.filter(user__full_name__icontains=term)
                for user_series in search:
                    data.append(user_series.toJSON())
            else:
                data['error'] = 'Acción inválida'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('user_series_create')
        context['title'] = 'Administración de Series'
        return context


class UserSeriesCreateView(PermissionMixin, CreateView):
    model = UserSeries
    template_name = 'admin/user_series/create.html'
    form_class = UserSeriesForm
    success_url = reverse_lazy('user_series_list')
    permission_required = 'add_userseries'

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        data = {}
        
        if action == 'add':
            form = UserSeriesForm(request.POST)
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
                        'title': 'Asignar Serie a Vendedor',
                        'action': 'add'
                    }
                    return self.render_to_response(context)
        else:
            data['error'] = 'Acción inválida'
            return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_url'] = self.success_url
        context['title'] = 'Asignar Serie a Vendedor'
        context['action'] = 'add'
        return context


class UserSeriesUpdateView(PermissionMixin, UpdateView):
    model = UserSeries
    template_name = 'admin/user_series/create.html'
    form_class = UserSeriesForm
    success_url = reverse_lazy('user_series_list')
    permission_required = 'change_userseries'

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        data = {}
        
        if action == 'edit':
            user_series = self.get_object()
            form = UserSeriesForm(request.POST, instance=user_series)
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
                        'title': 'Editar Asignación de Serie',
                        'action': 'edit',
                        'object': user_series
                    }
                    return self.render_to_response(context)
        else:
            data['error'] = 'Acción inválida'
            return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_url'] = self.success_url
        context['title'] = 'Editar Asignación de Serie'
        context['action'] = 'edit'
        return context


class UserSeriesDeleteView(PermissionMixin, DeleteView):
    model = UserSeries
    template_name = 'admin/user_series/delete.html'
    success_url = reverse_lazy('user_series_list')
    permission_required = 'delete_userseries'

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.get_object().delete()
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Notificación de Eliminación'
        context['list_url'] = self.success_url
        return context
