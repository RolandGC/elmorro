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

from core.pos.models import Sale, Client, Company, Currency
from core.reports.forms import ReportForm
from core.security.mixins import ModuleMixin


class SaleReportView(ModuleMixin, FormView):
    template_name = 'sale_report/report.html'
    form_class = ReportForm

    def get_deposits_queryset(self, request):
        start_date = request.POST.get('start_date', '')
        end_date = request.POST.get('end_date', '')
        client_id = request.POST.get('client_id', '')
        base_currency_id = request.POST.get('base_currency_id', '')
        sales = Sale.objects.select_related(
            'client', 'client__user', 'base_currency'
        ).prefetch_related(
            'payments', 'payments__payment_method', 'payments__currency', 'payments__bank'
        ).all()
        if client_id:
            sales = sales.filter(client_id=client_id)
        if base_currency_id:
            sales = sales.filter(base_currency_id=base_currency_id)
        if start_date and end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                sales = sales.filter(date_joined__range=[start_date, end_date_obj.date()])
            except Exception:
                sales = sales.filter(date_joined__range=[start_date, end_date])
        return sales.order_by('date_joined', 'id')

    def build_deposit_row(self, sale, p, pen, usd):
        base_row = {
            'fechas': sale.dispatch_date.strftime('%d/%m/%Y') if sale.dispatch_date else '',
            'base_currency': sale.base_currency.name if sale.base_currency else '',
            'debt_amount': float(sale.debt_amount) if sale.debt_amount is not None else None,
            'order_note': sale.order_note or '',
            'freight_forwarder': sale.freight_forwarder or '',
            'exchange_rate': float(sale.exchange_rate or 0) or 1,
        }
        if p is None:
            # Venta sin pagos: se conserva la fila con los campos de pago vacíos
            base_row.update({
                'fecha': '',
                'amount': None,
                'currency': '',
                'bank': '',
                'operation': '',
                'payment_method': '',
                'transfer_type': '',
                'equivalent_currency': '',
                'equivalent_amount': None,
            })
            return base_row

        rate = base_row['exchange_rate']
        amount = float(p.amount or 0)
        currency_code = (p.currency.code or '').upper() if p.currency else ''
        # Moneda equivalente = la contraria a la moneda del pago
        if currency_code == 'PEN':
            equivalent_currency = usd
            computed_equivalent = amount / rate if rate else 0
        else:
            equivalent_currency = pen
            computed_equivalent = amount * rate
        # Reutiliza el monto equivalente ya persistido; si no existe, usa la conversión
        if p.equivalent_amount is not None:
            equivalent_amount = float(p.equivalent_amount)
        else:
            equivalent_amount = computed_equivalent
        base_row.update({
            'fecha': p.date_joined.strftime('%d/%m/%Y') if p.date_joined else '',
            'amount': amount,
            'currency': p.currency.name if p.currency else '',
            'bank': p.bank.name if p.bank else '',
            'operation': p.operation_number or '',
            'payment_method': p.payment_method.name if p.payment_method else '',
            'transfer_type': p.get_transfer_type_display() if p.transfer_type else '',
            'equivalent_currency': equivalent_currency.name if equivalent_currency else '',
            'equivalent_amount': equivalent_amount,
        })
        return base_row

    def build_deposits(self, request):
        currencies = list(Currency.objects.all())
        pen = next((c for c in currencies if (c.code or '').upper() == 'PEN'), None)
        usd = next((c for c in currencies if (c.code or '').upper() == 'USD'), None)
        rows = []
        for sale in self.get_deposits_queryset(request):
            payments = list(sale.payments.all())
            if not payments:
                rows.append(self.build_deposit_row(sale, None, pen, usd))
            else:
                for p in payments:
                    rows.append(self.build_deposit_row(sale, p, pen, usd))
        return rows

    def export_deposits_excel(self, request):
        try:
            rows = self.build_deposits(request)
            headers = ['FECHAS', 'MONEDA BASE', 'VIAJES', 'NOTA P.', 'FLETERO', 'FECHA', 'MONEDA',
                       'MONTO', 'BANCO', 'OPERACIÓN', 'FORMA', 'TIPO TRANSF.', 'MONEDA EQ.',
                       'MONTO EQ.', 'TIPO C.']
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
            total_label_fmt = workbook.add_format({
                'bold': True, 'border': 1, 'align': 'left', 'valign': 'vcenter',
                'bg_color': '#d9e1f2'
            })
            total_money_fmt = workbook.add_format({
                'bold': True, 'border': 1, 'num_format': '#,##0.00', 'bg_color': '#d9e1f2'
            })
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_fmt)
            for r, row in enumerate(rows, start=1):
                worksheet.write(r, 0, row['fechas'], center_fmt)
                worksheet.write(r, 1, row['base_currency'], center_fmt)
                if row['debt_amount'] is not None:
                    worksheet.write_number(r, 2, row['debt_amount'], money_fmt)
                else:
                    worksheet.write(r, 2, '', money_fmt)
                worksheet.write(r, 3, row['order_note'], cell_fmt)
                worksheet.write(r, 4, row['freight_forwarder'], cell_fmt)
                worksheet.write(r, 5, row['fecha'], center_fmt)
                worksheet.write(r, 6, row['currency'], center_fmt)
                if row['amount'] is not None:
                    worksheet.write_number(r, 7, row['amount'], money_fmt)
                else:
                    worksheet.write(r, 7, '', money_fmt)
                worksheet.write(r, 8, row['bank'], cell_fmt)
                worksheet.write(r, 9, row['operation'], cell_fmt)
                worksheet.write(r, 10, row['payment_method'], cell_fmt)
                worksheet.write(r, 11, row['transfer_type'], cell_fmt)
                worksheet.write(r, 12, row['equivalent_currency'], center_fmt)
                if row['equivalent_amount'] is not None:
                    worksheet.write_number(r, 13, row['equivalent_amount'], money_fmt)
                else:
                    worksheet.write(r, 13, '', money_fmt)
                worksheet.write_number(r, 14, row['exchange_rate'], center_fmt)

            # Totales al final del listado
            total_viajes = sum((row['debt_amount'] or 0) for row in rows)
            total_monto = sum((row['amount'] or 0) for row in rows)
            total_general = total_viajes - total_monto
            totals_row = len(rows) + 1
            worksheet.write(totals_row, 0, 'TOTALES', total_label_fmt)
            worksheet.write_number(totals_row, 2, total_viajes, total_money_fmt)
            worksheet.write_number(totals_row, 7, total_monto, total_money_fmt)
            worksheet.write(totals_row + 1, 0, 'TOTAL GENERAL', total_label_fmt)
            worksheet.write_number(totals_row + 1, 7, total_general, total_money_fmt)

            widths = [12, 14, 14, 18, 16, 12, 12, 12, 14, 16, 14, 14, 12, 14, 10]
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
            total_viajes = sum((row['debt_amount'] or 0) for row in rows)
            total_monto = sum((row['amount'] or 0) for row in rows)
            template = get_template('sale_report/deposits_pdf.html')
            html = template.render({
                'rows': rows,
                'company': Company.objects.first(),
                'reference': request.POST.get('client_label', ''),
                'total_viajes': total_viajes,
                'total_monto': total_monto,
                'total_general': total_viajes - total_monto,
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
                base_currency_id = request.POST.get('base_currency_id', '')
                search = Sale.objects.all()
                if client_id:
                    search = search.filter(client_id=client_id)
                if base_currency_id:
                    search = search.filter(base_currency_id=base_currency_id)
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
        context['base_currencies'] = Currency.objects.filter(is_active=True)
        return context
