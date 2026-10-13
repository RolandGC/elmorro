from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction

from core.pos.models import Expenses, TypeExpense, ExpenseSeries, UserExpenseSeries

# Datos transcritos de los comprobantes de egreso (fotos).
# El vendedor/usuario se deduce del prefijo de la serie (UserExpenseSeries).
EXPENSES = [
    {
        'serie': '021-0010',
        'fecha': '2026-08-17 11:51:06',
        'valor': 6.00,
        'desc': 'PAGO DE FLETE A TRANSPORTE RAQUEL (SR. JUAN ABEL NIETO) SEGUN FT. E001-550 (01 BULTO x S/ 6 = S/ 6.00) MERCADERIA DE BEBIDAS PREMIUM',
    },
    {
        'serie': '021-0011',
        'fecha': '2026-08-24 12:22:40',
        'valor': 420.00,
        'desc': 'PAGO DE FLETE A TRANSPORTES KATHERIN EXPRESS (SR. WENDER JARRO) SEGUN FT. E001-559 (42 BULTO x S/ 10 = S/ 420.00) ESTUCHES DE ROJA 1 LITRO',
    },
    {
        'serie': '021-0012',
        'fecha': '2026-09-05 12:07:32',
        'valor': 272.00,
        'desc': 'PAGO DE FLETE A CONSORCIO TACNA SUR LWM S.A.C (SR. WILDER RIBERA) SEGUN FT. E001-147 (34 BULTOS x S/ 8 = S/ 272.00) ESTUCHES DE RED LABEL 1 LITRO',
    },
    {
        'serie': '021-0014',
        'fecha': '2026-10-03 12:49:47',
        'valor': 150.00,
        'desc': 'PAGO DE FLETE A TRANSPORTE SEÑOR DE MURUHUAY (SR. FERNANDO ROJAS FLORES) SEGUN FT. E001-1135 (50 BULTO X S/ 3 = S/ 150.00) MERCADERIA DE COMPAÑIA PERUANA DE BEBIDAS ESPIRITUOSAS SAC.',
    },
]

DATE_FORMATS = ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d')


class Command(BaseCommand):
    help = 'Registra los gastos (pos_expenses) de los comprobantes de egreso. Idempotente por expense_serie.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Muestra lo que haría sin escribir en la BD.')
        parser.add_argument('--typeexpense', default='1', help='id del tipo de egreso (default: 1 = PAGO FLETE).')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        typeexpense = TypeExpense.objects.filter(pk=int(options['typeexpense'])).first()
        if typeexpense is None:
            self.stderr.write(self.style.ERROR(f'No existe un TypeExpense con id={options["typeexpense"]}'))
            return

        created = skipped = 0
        for row in EXPENSES:
            serie = row['serie']
            if Expenses.objects.filter(expense_serie=serie).exists():
                skipped += 1
                self.stdout.write(f'[omitido] ya existe: {serie}')
                continue

            user = self._user_from_serie(serie)
            fecha = self._parse_date(row['fecha'])
            desc = row['desc']
            valor = row['valor']

            if dry_run:
                created += 1
                self.stdout.write(
                    f'[dry-run] {serie} | {fecha} | S/ {valor:.2f} | '
                    f'tipo={typeexpense.name} | user={user}'
                )
                continue

            with transaction.atomic():
                Expenses.objects.create(
                    typeexpense=typeexpense,
                    user=user,
                    expense_serie=serie,
                    date_joined=fecha,
                    expense_date=fecha.date(),
                    valor=valor,
                    desc=desc,
                )
            created += 1

        self.stdout.write(self.style.SUCCESS(f'Gastos creados: {created} | Omitidos: {skipped}'))

    @staticmethod
    def _user_from_serie(serie):
        prefix = serie.rsplit('-', 1)[0]
        expense_series = ExpenseSeries.objects.filter(name=prefix).first()
        if expense_series is None:
            return None
        assignment = UserExpenseSeries.objects.select_related('user').filter(
            expense_series=expense_series
        ).first()
        return assignment.user if assignment else None

    @staticmethod
    def _parse_date(raw):
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(raw, fmt)
            except ValueError:
                continue
        raise ValueError(f'Fecha inválida: {raw}')
