import json

from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, FormView

from core.pos.forms import SeriesForm
from core.pos.models import Series
from core.security.mixins import PermissionMixin


class SeriesListView(PermissionMixin, FormView):
    template_name = 'frm/series/list.html'
    form_class = SeriesForm
    permission_required = 'view_series'

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action')
        try:
            if action == 'search':
                data = []
                term = request.POST.get('term', '')
                search = Series.objects.all()
                if term:
                    search = search.filter(name__icontains=term)
                for series in search:
                    data.append(series.toJSON())
            else:
                data['error'] = 'Acción inválida'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('series_create')
        context['title'] = 'Series de Facturación'
        return context


class SeriesCreateView(PermissionMixin, CreateView):
    model = Series
    template_name = 'frm/series/create.html'
    form_class = SeriesForm
    success_url = reverse_lazy('series_list')
    permission_required = 'add_series'

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        data = {}
        try:
            if action == 'add':
                form = SeriesForm(request.POST)
                if form.is_valid():
                    instance = form.save()
                    data = instance.toJSON()
                else:
                    data['error'] = form.errors
            else:
                data['error'] = 'Acción inválida'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['title'] = 'Nueva Serie de Facturación'
        context['action'] = 'add'
        return context


class SeriesUpdateView(PermissionMixin, UpdateView):
    model = Series
    template_name = 'frm/series/create.html'
    form_class = SeriesForm
    success_url = reverse_lazy('series_list')
    permission_required = 'change_series'

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        data = {}
        try:
            if action == 'edit':
                series = self.get_object()
                form = SeriesForm(request.POST, instance=series)
                if form.is_valid():
                    instance = form.save()
                    data = instance.toJSON()
                else:
                    data['error'] = form.errors
            else:
                data['error'] = 'Acción inválida'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_url'] = self.success_url
        context['title'] = 'Editar Serie de Facturación'
        context['action'] = 'edit'
        return context


class SeriesDeleteView(PermissionMixin, DeleteView):
    model = Series
    template_name = 'frm/series/delete.html'
    success_url = reverse_lazy('series_list')
    permission_required = 'delete_series'

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
