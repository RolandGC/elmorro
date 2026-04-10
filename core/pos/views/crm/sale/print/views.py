from multiprocessing import context
import os
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views.generic.base import View
from weasyprint import HTML, CSS

from config import settings
from core.pos.models import Sale, Company
from core.pos.utils.zpl_generator import ZPLGenerator

logger = logging.getLogger(__name__)


class SalePrintVoucherView(LoginRequiredMixin, View):
    success_url = reverse_lazy('sale_admin_list')

    def get_success_url(self):
        if self.request.user.is_client():
            return reverse_lazy('sale_client_list')
        return self.success_url

    def get_height_ticket(self):
        sale = Sale.objects.get(pk=self.kwargs['pk'])
        height = 120
        increment = sale.saledetail_set.all().count() * 5.45
        height += increment
        return round(height)

    def is_android(self, request):
        """Return True if request comes from an Android device."""
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        return 'android' in user_agent

    def is_windows(self, request):
        """Return True if request comes from a Windows device."""
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        return 'windows' in user_agent

    def get_grouped_payments_by_currency(self, sale):
        """Group payments by currency and sum amounts"""
        payments_by_currency = {}
        for payment in sale.payments.all():
            currency_code = payment.currency.code
            if currency_code not in payments_by_currency:
                payments_by_currency[currency_code] = {
                    'symbol': payment.currency.symbol,
                    'name': payment.currency.name,
                    'total': 0
                }
            payments_by_currency[currency_code]['total'] += float(payment.amount)
        return payments_by_currency
    
    def get_grouped_cash_payments_by_currency(self, sale):
        """Group ONLY cash payments by currency and sum amounts"""
        payments_cash_by_currency = {}

        for payment in sale.payments.all():
            if payment.payment_method.code == 'efectivo':
                currency_code = payment.currency.code

                if currency_code not in payments_cash_by_currency:
                    payments_cash_by_currency[currency_code] = {
                        'symbol': payment.currency.symbol,
                        'name': payment.currency.name,
                        'total': 0
                    }

                payments_cash_by_currency[currency_code]['total'] += float(payment.amount)

        return payments_cash_by_currency
    
    def get_grouped_non_cash_payments_by_currency(self, sale):
        """Group all payments except cash by currency and sum amounts"""
        payments_non_cash_by_currency = {}
        for payment in sale.payments.all():
            if payment.payment_method.code != 'efectivo':
                currency_code = payment.currency.code
                if currency_code not in payments_non_cash_by_currency:
                    payments_non_cash_by_currency[currency_code] = {
                        'symbol': payment.currency.symbol,
                        'name': payment.currency.name,
                        'total': 0
                    }
                payments_non_cash_by_currency[currency_code]['total'] += float(payment.amount)
        return payments_non_cash_by_currency
    
    def get(self, request, *args, **kwargs):
        try:
            # Check if ZPL format is requested (for Android/Zebra printer)
            format_type = request.GET.get('format', 'pdf').lower()
            
            sale = Sale.objects.get(pk=self.kwargs['pk'])
            company = Company.objects.first()
            
            if format_type == 'zpl':
                # Generate ZPL for Zebra printer
                zpl_content = ZPLGenerator.generate_from_sale(sale, company)
                response = HttpResponse(zpl_content, content_type='text/plain; charset=utf-8')
                response['Content-Disposition'] = f'inline; filename="ticket_{sale.id}.zpl"'
                return response
            else:
                # Generate PDF (default)
                context = {'sale': sale, 'company': company}
                is_android = self.is_android(request)
                is_windows = self.is_windows(request)
                context['is_android'] = is_android
                context['is_windows'] = is_windows
                
                # Add grouped payments by currency
                context['payments_by_currency'] = self.get_grouped_payments_by_currency(sale)
                context['payments_cash_by_currency'] = self.get_grouped_cash_payments_by_currency(sale)
                context['payments_non_cash_by_currency'] = self.get_grouped_non_cash_payments_by_currency(sale)  
                context['equivalent_total'] = self.get_equivalent_total(sale)              
                if sale.type_voucher == 'ticket':
                    template = get_template('crm/sale/print/ticket.html')
                    # Use fixed height for Android or Windows (12cm = 120mm), dynamic for desktop
                    context['height'] = 120 if (is_android or is_windows) else self.get_height_ticket()
                else:
                    template = get_template('crm/sale/print/invoice.html')
                    
                html_template = template.render(context).encode(encoding="UTF-8")
                url_css = os.path.join(settings.BASE_DIR, 'static/lib/bootstrap-4.6.0/css/bootstrap.min.css')
                pdf_file = HTML(string=html_template, base_url=request.build_absolute_uri()).write_pdf(
                    stylesheets=[CSS(url_css)], presentational_hints=True)
                response = HttpResponse(pdf_file, content_type='application/pdf')
                return response
        except Exception as e:
            logger.error(f"Error generating print: {str(e)}", exc_info=True)
        return HttpResponseRedirect(self.get_success_url())
    
    def get_equivalent_total(self, sale):
    
        base_currency = sale.base_currency  # ajusta al nombre real del campo
        if not base_currency:
            return None

        exchange_rate = float(sale.exchange_rate or 1)
        is_base_pen = base_currency.symbol in ('S/', 'S/.')  # ajusta según tu modelo

        total_equivalent = 0.0
        detail_parts = []

        for payment in sale.payments.all():
            amount = float(payment.amount or 0)
            if amount == 0:
                continue

            sym = payment.currency.symbol or payment.currency.name
            is_same_currency = payment.currency_id == base_currency.id

            if is_same_currency:
                total_equivalent += amount
                detail_parts.append(f"{sym}{amount:.2f}")
            else:
                if is_base_pen:
                    # Base PEN: moneda extranjera × tasa
                    converted = amount * exchange_rate
                    detail_parts.append(f"({sym}{amount:.2f} × {exchange_rate:.2f})")
                else:
                    # Base USD u otra: moneda débil ÷ tasa
                    converted = amount / exchange_rate if exchange_rate else 0
                    detail_parts.append(f"({sym}{amount:.2f} ÷ {exchange_rate:.2f})")
                total_equivalent += converted

        if not detail_parts:
            return None

        base_sym = base_currency.symbol or ''
        detail_str = ' + '.join(detail_parts) + f' = {base_sym}{total_equivalent:.2f}'

        return {
            'currency_name': base_currency.name,
            'symbol': base_sym,
            'total': round(total_equivalent, 2),
        }
