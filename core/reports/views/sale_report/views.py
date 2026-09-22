import json
from datetime import datetime, timedelta
from io import BytesIO

import xlsxwriter
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import get_template
from django.views.generic import FormView
from weasyprint import HTML

from core.pos.models import Sale, Client, SalePayment, Company
from core.reports.forms import ReportForm
from core.security.mixins import ModuleMixin


class SaleReportView(ModuleMixin, FormView):
    template_name = 'sale_report/report.html'
    form_class = ReportForm

    def get_deposits_queryset(self, request):
        start_date = request.POST.get('start_date', '')
        end_date = request.POST.get('end_date', '')
        client_id = request.POST.get('client_id', '')
        payments = SalePayment.objects.select_related(
            'sale', 'sale__client', 'sale__client__user',
            'payment_method', 'currency', 'bank'
        ).all()
        if client_id:
            payments = payments.filter(sale__client_id=client_id)
        if start_date and end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                payments = payments.filter(sale__date_joined__range=[start_date, end_date_obj.date()])
            except Exception:
                payments = payments.filter(sale__date_joined__range=[start_date, end_date])
        return payments.order_by('sale__date_joined', 'sale_id', 'id')

    def build_deposits(self, request):
        rows = []
        for p in self.get_deposits_queryset(request):
            sale = p.sale
            rate = float(sale.exchange_rate or 0) or 1
            amount = float(p.amount or 0)
            currency_code = (p.currency.code or '').upper() if p.currency else ''
            monto_soles = amount if currency_code == 'PEN' else amount * rate
            rows.append({
                'fechas': sale.date_joined.strftime('%d/%m/%Y') if sale.date_joined else '',
                'order_note': sale.order_note or '',
                'freight_forwarder': sale.freight_forwarder or '',
                'fecha': p.date_joined.strftime('%d/%m/%Y') if p.date_joined else '',
                'amount': amount,
                'bank': p.bank.name if p.bank else '',
                'operation': p.operation_number or sale.operation or '',
                'payment_method': p.payment_method.name if p.payment_method else '',
                'transfer_type': sale.get_transfer_type_display() if sale.transfer_type else '',
                'currency': p.currency.name if p.currency else '',
                'monto_soles': monto_soles,
                'exchange_rate': rate,
            })
        return rows

    def export_deposits_excel(self, request):
        try:
            rows = self.build_deposits(request)
            headers = ['FECHAS', 'NOTA P.', 'FLETERO', 'FECHA', 'MONTO', 'BANCO',
                       'OPERACIÓN', 'FORMA', 'TIPO TRANSF.', 'MONEDA', 'MONTO S/', 'TIPO C.']
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet('Depósitos')
            header_fmt = workbook.add_format({
                'bold': True, 'bg_color': '#2d4154', 'font_color': 'white',
                'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True
            })
            cell_fmt = workbook.add_format({'border': 1, 'align': 'left', 'valign': 'vcenter'})
            money_fmt = workbook.add_format({'border': 1, 'num_format': '#,##0.00'})
            center_fmt = workbook.add_format({'border': 1, 'align': 'center'})
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_fmt)
            for r, row in enumerate(rows, start=1):
                worksheet.write(r, 0, row['fechas'], center_fmt)
                worksheet.write(r, 1, row['order_note'], cell_fmt)
                worksheet.write(r, 2, row['freight_forwarder'], cell_fmt)
                worksheet.write(r, 3, row['fecha'], center_fmt)
                worksheet.write_number(r, 4, row['amount'], money_fmt)
                worksheet.write(r, 5, row['bank'], cell_fmt)
                worksheet.write(r, 6, row['operation'], cell_fmt)
                worksheet.write(r, 7, row['payment_method'], cell_fmt)
                worksheet.write(r, 8, row['transfer_type'], cell_fmt)
                worksheet.write(r, 9, row['currency'], center_fmt)
                worksheet.write_number(r, 10, row['monto_soles'], money_fmt)
                worksheet.write_number(r, 11, row['exchange_rate'], center_fmt)
            widths = [12, 18, 16, 12, 12, 14, 16, 14, 14, 10, 14, 10]
            for col, width in enumerate(widths):
                worksheet.set_column(col, col, width)
            workbook.close()
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="depositos.xlsx"'
            return response
        except Exception as e:
            return HttpResponse(json.dumps({'error': str(e)}), status=500, content_type='application/json')

    def export_deposits_pdf(self, request):
        try:
            rows = self.build_deposits(request)
            template = get_template('sale_report/deposits_pdf.html')
            html = template.render({
                'rows': rows,
                'company': Company.objects.first(),
                'reference': request.POST.get('client_label', ''),
            })
            pdf = HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf()
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="depositos.pdf"'
            return response
        except Exception as e:
            return HttpResponse(json.dumps({'error': str(e)}), status=500, content_type='application/json')

    def post(self, request, *args, **kwargs):
        action = request.POST['action']
        data = {}
        try:
            if action == 'search_report':
                data = []
                start_date = request.POST['start_date']
                end_date = request.POST['end_date']
                client_id = request.POST.get('client_id', '')
                search = Sale.objects.all()
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
            elif action == 'export_deposits_excel':
                return self.export_deposits_excel(request)
            elif action == 'export_deposits_pdf':
                return self.export_deposits_pdf(request)
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
