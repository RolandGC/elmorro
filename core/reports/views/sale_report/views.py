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

    def build_payment_row(self, sale, p, base_currency):
        rate = float(sale.exchange_rate or 0) or 1
        base_code = (base_currency.code or '').upper() if base_currency else ''
        amount = float(p.amount or 0)
        # Monto normalizado a la moneda base (se convierte si el pago está en otra moneda)
        if not base_currency or p.currency_id == base_currency.id:
            converted = False
            base_amount = amount
        else:
            converted = True
            base_amount = amount * rate if base_code == 'PEN' else (amount / rate if rate else 0)
        return {
            'fecha': p.date_joined.strftime('%d/%m/%Y') if p.date_joined else '',
            'currency': p.currency.name if p.currency else '',
            'amount': amount,
            'base_amount': base_amount,
            'converted': converted,
            'bank': p.bank.name if p.bank else '',
            'operation': p.operation_number or '',
            'payment_method': p.payment_method.name if p.payment_method else '',
            'transfer_type': p.get_transfer_type_display() if p.transfer_type else '',
        }

    def empty_payment_row(self):
        return {
            'fecha': '', 'currency': '', 'amount': None, 'base_amount': None, 'converted': False,
            'bank': '', 'operation': '', 'payment_method': '', 'transfer_type': '',
        }

    def build_deposit_groups(self, request):
        groups = []
        for sale in self.get_deposits_queryset(request):
            base_currency = sale.base_currency
            payments = list(sale.payments.all())
            payment_rows = [self.build_payment_row(sale, p, base_currency) for p in payments]
            if not payment_rows:
                payment_rows = [self.empty_payment_row()]
            groups.append({
                'fechas': sale.dispatch_date.strftime('%d/%m/%Y') if sale.dispatch_date else '',
                'base_currency': base_currency.name if base_currency else '',
                'base_symbol': base_currency.symbol if base_currency else '',
                'debt_amount': float(sale.debt_amount) if sale.debt_amount is not None else None,
                'order_note': sale.order_note or '',
                'freight_forwarder': sale.freight_forwarder or '',
                'exchange_rate': float(sale.exchange_rate or 0) or 1,
                'payments': payment_rows,
            })
        return groups

    def report_base(self, request, groups):
        """Moneda base del reporte: del filtro o, si no, del primer registro."""
        base_currency_id = request.POST.get('base_currency_id', '')
        if base_currency_id:
            currency = Currency.objects.filter(pk=base_currency_id).first()
            if currency:
                return currency.name, currency.symbol
        names = {g['base_currency'] for g in groups if g['base_currency']}
        symbols = {g['base_symbol'] for g in groups if g['base_symbol']}
        name = names.pop() if len(names) == 1 else ''
        symbol = symbols.pop() if len(symbols) == 1 else ''
        return name, symbol

    def deposit_totals(self, groups):
        # La deuda se suma una sola vez por venta (no por cada fila de pago)
        total_viajes = sum((g['debt_amount'] or 0) for g in groups)
        # Los montos ya están normalizados a la moneda base
        total_monto = sum((p['base_amount'] or 0) for g in groups for p in g['payments'])
        return {
            'total_viajes': total_viajes,
            'total_monto': total_monto,
            'total_general': total_viajes - total_monto,
        }

    def export_deposits_excel(self, request):
        try:
            groups = self.build_deposit_groups(request)
            totals = self.deposit_totals(groups)
            base_name, base_symbol = self.report_base(request, groups)
            sym = f' ({base_symbol})' if base_symbol else ''
            headers = ['FECHAS', 'VIAJES' + sym, 'NOTA P.', 'FLETERO', 'FECHA', 'MONTO' + sym,
                       'BANCO', 'OPERACIÓN', 'FORMA', 'TIPO TRANSF.', 'MONEDA', 'MONTO EQUIV.', 'TIPO C.']
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet('Depósitos')
            title_fmt = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter'})
            header_fmt = workbook.add_format({
                'bold': True, 'bg_color': '#2d4154', 'font_color': 'white',
                'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True
            })
            cell_fmt = workbook.add_format({'border': 1, 'align': 'left', 'valign': 'vcenter'})
            money_fmt = workbook.add_format({'border': 1, 'num_format': '#,##0.00'})
            center_fmt = workbook.add_format({'border': 1, 'align': 'center'})
            # Fila pagada en una moneda distinta a la base (fila resaltada)
            conv_cell_fmt = workbook.add_format({'border': 1, 'align': 'left', 'valign': 'vcenter', 'bg_color': '#fff3b0'})
            conv_money_fmt = workbook.add_format({'border': 1, 'num_format': '#,##0.00', 'bg_color': '#fff3b0'})
            conv_center_fmt = workbook.add_format({'border': 1, 'align': 'center', 'bg_color': '#fff3b0'})
            total_label_fmt = workbook.add_format({
                'bold': True, 'border': 1, 'align': 'left', 'valign': 'vcenter',
                'bg_color': '#d9e1f2'
            })
            total_money_fmt = workbook.add_format({
                'bold': True, 'border': 1, 'num_format': '#,##0.00', 'bg_color': '#d9e1f2'
            })

            title = 'DEPÓSITOS' + (f' EN {base_name.upper()}' if base_name else '')
            worksheet.merge_range(0, 0, 0, 12, title, title_fmt)
            for col, header in enumerate(headers):
                worksheet.write(1, col, header, header_fmt)

            row_idx = 2
            for g in groups:
                n = len(g['payments'])
                first = row_idx
                last = row_idx + n - 1
                if n > 1:
                    # Campos de la venta: combinados verticalmente (agrupación)
                    worksheet.merge_range(first, 0, last, 0, g['fechas'], center_fmt)
                    worksheet.merge_range(
                        first, 1, last, 1,
                        g['debt_amount'] if g['debt_amount'] is not None else '', money_fmt
                    )
                    worksheet.merge_range(first, 2, last, 2, g['order_note'], cell_fmt)
                    worksheet.merge_range(first, 3, last, 3, g['freight_forwarder'], cell_fmt)
                    worksheet.merge_range(first, 12, last, 12, g['exchange_rate'], center_fmt)
                else:
                    p0 = g['payments'][0]
                    use_conv = p0['converted']
                    worksheet.write(first, 0, g['fechas'], conv_center_fmt if use_conv else center_fmt)
                    if g['debt_amount'] is not None:
                        worksheet.write_number(first, 1, g['debt_amount'], conv_money_fmt if use_conv else money_fmt)
                    else:
                        worksheet.write(first, 1, '', conv_money_fmt if use_conv else money_fmt)
                    worksheet.write(first, 2, g['order_note'], conv_cell_fmt if use_conv else cell_fmt)
                    worksheet.write(first, 3, g['freight_forwarder'], conv_cell_fmt if use_conv else cell_fmt)
                    worksheet.write_number(first, 12, g['exchange_rate'], conv_center_fmt if use_conv else center_fmt)
                for i, p in enumerate(g['payments']):
                    r = first + i
                    conv = p['converted']
                    worksheet.write(r, 4, p['fecha'], conv_center_fmt if conv else center_fmt)
                    if p['base_amount'] is not None:
                        worksheet.write_number(r, 5, p['base_amount'], conv_money_fmt if conv else money_fmt)
                    else:
                        worksheet.write(r, 5, '', conv_money_fmt if conv else money_fmt)
                    worksheet.write(r, 6, p['bank'], conv_cell_fmt if conv else cell_fmt)
                    worksheet.write(r, 7, p['operation'], conv_cell_fmt if conv else cell_fmt)
                    worksheet.write(r, 8, p['payment_method'], conv_cell_fmt if conv else cell_fmt)
                    worksheet.write(r, 9, p['transfer_type'], conv_cell_fmt if conv else cell_fmt)
                    worksheet.write(r, 10, p['currency'], conv_center_fmt if conv else center_fmt)
                    # MONTO EQUIV. = monto original solo si se pagó en otra moneda
                    if conv and p['amount'] is not None:
                        worksheet.write_number(r, 11, p['amount'], conv_money_fmt)
                    else:
                        worksheet.write(r, 11, '', money_fmt)
                    if i > 0:
                        worksheet.set_row(r, None, None, {'level': 1})
                row_idx += n

            # Totales al final del listado (en la moneda base)
            label = 'TOTALES' + (f' ({base_name})' if base_name else '')
            worksheet.write(row_idx, 0, label, total_label_fmt)
            worksheet.write_number(row_idx, 1, totals['total_viajes'], total_money_fmt)
            worksheet.write_number(row_idx, 5, totals['total_monto'], total_money_fmt)
            worksheet.write(row_idx + 1, 0, 'TOTAL GENERAL', total_label_fmt)
            worksheet.write_number(row_idx + 1, 5, totals['total_general'], total_money_fmt)

            widths = [12, 14, 18, 16, 12, 14, 14, 16, 14, 14, 14, 14, 10]
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
            groups = self.build_deposit_groups(request)
            totals = self.deposit_totals(groups)
            base_name, base_symbol = self.report_base(request, groups)
            template = get_template('sale_report/deposits_pdf.html')
            html = template.render({
                'groups': groups,
                'company': Company.objects.first(),
                'reference': request.POST.get('client_label', ''),
                'total_records': sum(len(g['payments']) for g in groups),
                'base_name': base_name,
                'base_symbol': base_symbol,
                'total_viajes': totals['total_viajes'],
                'total_monto': totals['total_monto'],
                'total_general': totals['total_general'],
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
