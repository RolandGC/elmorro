import json
from datetime import datetime, timedelta
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.http import HttpResponse
from django.views.generic import FormView

from core.pos.models import Sale, Client
from core.reports.forms import ReportForm
from core.security.mixins import ModuleMixin


class SaleReportView(ModuleMixin, FormView):
    template_name = 'sale_report/report.html'
    form_class = ReportForm

    def post(self, request, *args, **kwargs):
        print(request.POST)
        action = request.POST['action']
        data = {}
        try:
            if action == 'search_report':
                data = []
                start_date = request.POST['start_date']
                end_date = request.POST['end_date']
                client_id = request.POST.get('client_id', '')
                search = Sale.objects.filter(employee=request.user)
                if client_id:
                    search = search.filter(client_id=client_id)
                if len(start_date) and len(end_date):
                    try:
                        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                        # Agregar 1 día para incluir todo el día final
                        end_date_obj = end_date_obj + timedelta(days=1)
                        search = search.filter(date_joined__range=[start_date, end_date_obj.date()])
                    except:
                        search = search.filter(date_joined__range=[start_date, end_date])
                for sale in search:
                    data.append(sale.toJSON())
            elif action == 'search_clients':
                data = []
                term = request.POST.get('term', '')
                clients = Client.objects.filter(
                    Q(user__full_name__icontains=term) | Q(user__dni__icontains=term)
                ).order_by('user__full_name')[0:10]
                for c in clients:
                    data.append({
                        'id': c.id,
                        'text': '{} / {}'.format(c.user.full_name, c.user.dni),
                    })
            else:
                data['error'] = 'No ha ingresado una opción'
        except Exception as e:
            data['error'] = str(e)
        # Serializar datos a una cadena JSON usando DjangoJSONEncoder
        json_data = json.dumps(data, cls=DjangoJSONEncoder)
        # Devolver respuesta JSON
        return HttpResponse(json_data, content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reporte de Cobranzas'
        return context
