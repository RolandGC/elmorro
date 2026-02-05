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
                if sale.type_voucher == 'ticket':
                    template = get_template('crm/sale/print/ticket.html')
                    context['height'] = self.get_height_ticket()
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
