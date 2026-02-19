import os
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views.generic.base import View
from weasyprint import HTML, CSS

from config import settings
from core.pos.models import Expenses, Company

logger = logging.getLogger(__name__)


class ExpensePrintTicketView(LoginRequiredMixin, View):
    success_url = reverse_lazy('expenses_list')

    def get(self, request, *args, **kwargs):
        try:
            expense = Expenses.objects.get(pk=self.kwargs['pk'])
            company = Company.objects.first()
            
            context = {
                'expense': expense,
                'company': company
            }
            
            template = get_template('frm/expenses/print/ticket.html')
            html_template = template.render(context).encode(encoding="UTF-8")
            url_css = os.path.join(settings.BASE_DIR, 'static/lib/bootstrap-4.6.0/css/bootstrap.min.css')
            pdf_file = HTML(string=html_template, base_url=request.build_absolute_uri()).write_pdf(
                stylesheets=[CSS(url_css)], presentational_hints=True)
            response = HttpResponse(pdf_file, content_type='application/pdf')
            return response
        except Exception as e:
            logger.error(f"Error generating expense print: {str(e)}", exc_info=True)
        return HttpResponseRedirect(self.success_url)
