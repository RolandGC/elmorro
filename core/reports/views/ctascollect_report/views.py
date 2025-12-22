import json

from django.http import HttpResponse
from django.views.generic import FormView

from core.pos.models import CtasCollect
from core.reports.forms import ReportForm
from core.security.mixins import ModuleMixin

from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime
from django.http import JsonResponse

class CtasCollectReportView(ModuleMixin, FormView):
    template_name = 'ctascollect_report/report.html'
    form_class = ReportForm

    def post(self, request, *args, **kwargs):
        action = request.POST['action']
        data = []
        try:
            if action == 'search_report':
                start_date = request.POST.get('start_date')
                end_date = request.POST.get('end_date')

                if start_date and end_date:
                    search = CtasCollect.objects.filter(date_joined__range=[start_date, end_date])
                    for collect in search:
                        data.append(collect.toJSON())
                else:
                    # Obtener todos los registros de CtasCollect si no se proporcionan fechas de inicio y fin
                    search = CtasCollect.objects.all()
                    for collect in search:
                        data.append(collect.toJSON())
            else:
                data = {'error': 'Acción no válida.'}
        except ValueError:
            data = {'error': 'Formato de fecha incorrecto. Use el formato YYYY-MM-DD.'}
        except Exception as e:
            data = {'error': str(e)}

        return JsonResponse(data, safe=False, encoder=DjangoJSONEncoder)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reporte de Cuentas por Cobrar'
        return context