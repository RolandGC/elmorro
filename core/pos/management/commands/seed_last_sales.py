from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction

from core.pos.models import Sale, Client, UserSeries

# Datos extraídos de las boletas (última venta de cada vendedor).
# El vendedor se deduce del prefijo de la serie (Series/UserSeries).
LAST_SALES = [
    {
        'serie': '014-0498',
        'fecha': '10/10/2026 12:46',
        'total': 1080.00,
        'cliente_dni': 'D20250009',
        'comment': 'np 005 - 15441',
    },
    {
        'serie': '019-0243',
        'fecha': '10/10/2026 12:31',
        'total': 650.00,
        'cliente_dni': 'D20250046',
        'comment': 'N. P 008 6037',
    },
    {
        'serie': '015-0492',
        'fecha': '09/10/2026 23:37',
        'total': 952.00,
        'cliente_dni': 'D20250014',
        'comment': 'N/P 008-6031',
    },
    {
        'serie': '010-0430',
        'fecha': '09/10/2026 16:47',
        'total': 16826.00,
        'cliente_dni': '20607084964',
        'comment': 'LETRA FDC F004-355 (005-15323)',
    },
    {
        'serie': '012-0498',
        'fecha': '10/10/2026 12:37',
        'total': 2265.43,
        'cliente_dni': '20600798333',
        'comment': '',
    },
    {
        'serie': '020-0301',
        'fecha': '10/10/2026 12:37',
        'total': 2265.43,
        'cliente_dni': '20600798333',
        'comment': '',
    },
    {
        'serie': '011-0378',
        'fecha': '08/10/2026 11:58',
        'total': 7500.00,
        'cliente_dni': 'M20250029',
        'comment': '',
    },
    
]

DATE_FORMATS = (
    '%Y-%m-%d %H:%M',
    '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%d',
    '%d/%m/%Y %H:%M',
    '%d/%m/%Y',
)


class Command(BaseCommand):
    help = (
        'Registra la última venta por vendedor (datos embebidos) para que la '
        'serie de comprobantes continúe desde el último número. Idempotente.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--default-client-dni',
            default='9999999999',
            help='DNI del cliente por defecto si no se encuentra el de la boleta.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra lo que haría sin escribir en la base de datos.',
        )

    def handle(self, *args, **options):
        default_client_dni = options['default_client_dni']
        dry_run = options['dry_run']

        created = skipped = 0
        errors = []

        for row in LAST_SALES:
            serie = (row.get('serie') or '').strip()
            if not serie or '-' not in serie:
                errors.append(f'serie inválida "{serie}"')
                continue

            series_name = serie.rsplit('-', 1)[0]
            user_series = (
                UserSeries.objects
                .select_related('user', 'series')
                .filter(series__name=series_name)
                .first()
            )
            if user_series is None:
                errors.append(f'no hay UserSeries con la serie "{series_name}"')
                continue

            employee = user_series.user

            if Sale.objects.filter(employee=employee, serie=serie).exists():
                skipped += 1
                self.stdout.write(f'[omitido] ya existe: {serie} ({employee.full_name})')
                continue

            client = self._resolve_client(row.get('cliente_dni'), default_client_dni)
            if client is None:
                errors.append(f'{serie}: no hay ningún cliente para asociar')
                continue

            date_joined = self._parse_date(row.get('fecha'))
            total = row.get('total') or 0
            comment = (row.get('comment') or '').strip() or 'Registro de última venta (migración)'

            if dry_run:
                created += 1
                self.stdout.write(
                    f'[dry-run] {serie} | vendedor={employee.full_name} | '
                    f'cliente={client.user.full_name} | fecha={date_joined} | total={total}'
                )
                continue

            try:
                with transaction.atomic():
                    Sale.objects.create(
                        employee=employee,
                        client=client,
                        serie=serie,
                        date_joined=date_joined,
                        total=total,
                        comment=comment,
                        type_voucher='ticket',
                        payment_condition='contado',
                    )
                created += 1
            except Exception as exc:
                errors.append(f'{serie}: {exc}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Ventas semilla creadas: {created} | Omitidas (ya existían): {skipped} | '
                f'Errores: {len(errors)}'
            )
        )
        for err in errors:
            self.stdout.write(self.style.WARNING(f' - {err}'))

    def _resolve_client(self, client_dni, default_client_dni):
        client_dni = (client_dni or '').strip()
        if client_dni:
            client = Client.objects.filter(user__dni=client_dni).first()
            if client is not None:
                return client
        client = Client.objects.filter(user__dni=default_client_dni).first()
        if client is not None:
            return client
        return Client.objects.first()

    @staticmethod
    def _parse_date(raw):
        raw = (raw or '').strip()
        if not raw:
            return datetime.now()
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(raw, fmt)
            except ValueError:
                continue
        return datetime.now()
