import csv
import os
import re

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction
from django.db.models import Q

from core.pos.models import Client
from core.user.models import User


class Command(BaseCommand):
    help = (
        'Importa/actualiza usuarios desde un CSV (columnas: username, full_name; '
        'opcional: email). Usa username/dni como llave. Con --update actualiza '
        'los usuarios existentes; con --as-client crea/asegura el Client.'
    )

    def add_arguments(self, parser):
        parser.add_argument('csv_path', help='Ruta del archivo CSV a importar.')
        parser.add_argument(
            '--password',
            default=None,
            help='Contraseña temporal para los usuarios nuevos. '
                 'Si se omite, la cuenta queda sin login (contraseña inutilizable).',
        )
        parser.add_argument(
            '--group',
            default=None,
            help='Nombre del grupo a asignar a los usuarios (ej. Cliente).',
        )
        parser.add_argument(
            '--as-client',
            action='store_true',
            help='Crea/asegura el registro Client (pos_client) de cada usuario.',
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Actualiza full_name/email de usuarios existentes y mobile/address '
                 'de clientes existentes (si --as-client).',
        )
        parser.add_argument(
            '--mobile-column',
            default='mobile',
            help='Columna del CSV para el celular (default: mobile; usa "fono" si aplica).',
        )
        parser.add_argument(
            '--address-column',
            default='address',
            help='Columna del CSV para la dirección (default: address; usa "direccion" si aplica).',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra lo que haría sin escribir en la base de datos.',
        )

    def handle(self, *args, **options):
        path = options['csv_path']
        password = options['password']
        group_name = options['group']
        as_client = options['as_client']
        update = options['update']
        dry_run = options['dry_run']

        if not os.path.exists(path):
            raise CommandError(f'No existe el archivo: {path}')

        group = None
        if group_name:
            group = Group.objects.filter(name=group_name).first()
            if group is None:
                raise CommandError(f'No existe el grupo "{group_name}".')

        with open(path, newline='', encoding='utf-8-sig') as fh:
            reader = csv.DictReader(fh)
            fieldnames = reader.fieldnames or []
            if 'username' not in fieldnames or 'full_name' not in fieldnames:
                raise CommandError(
                    'El CSV debe tener al menos las columnas: username, full_name.'
                )
            mobile_col = options['mobile_column']
            address_col = options['address_column']
            if mobile_col not in fieldnames and 'fono' in fieldnames:
                mobile_col = 'fono'
            if address_col not in fieldnames and 'direccion' in fieldnames:
                address_col = 'direccion'
            rows = list(reader)

        used_mobiles = set(
            Client.objects.exclude(mobile__isnull=True).values_list('mobile', flat=True)
        )

        created = updated = skipped = 0
        clients_created = clients_updated = 0
        errors = []

        for index, row in enumerate(rows, start=2):
            username = (row.get('username') or '').strip()
            full_name = (row.get('full_name') or '').strip()
            email = (row.get('email') or '').strip() or None
            raw_mobile = (row.get(mobile_col) or '').strip()
            raw_address = (row.get(address_col) or '').strip()

            if not username:
                errors.append(f'fila {index}: username vacío, se omite')
                continue
            if len(username) > 13:
                errors.append(
                    f'fila {index}: "{username}" supera 13 caracteres (límite de dni), se omite'
                )
                continue

            user = User.objects.filter(
                Q(username=username) | Q(dni=username)
            ).first()

            if dry_run:
                if user is None:
                    created += 1
                    extra = ' (+ cliente)' if as_client else ''
                    self.stdout.write(f'[dry-run] crearía usuario: {username} | {full_name}{extra}')
                else:
                    if update:
                        updated += 1
                        self.stdout.write(f'[dry-run] actualizaría usuario: {username} | {full_name}')
                    else:
                        skipped += 1
                    if as_client:
                        client = Client.objects.filter(user=user).first()
                        if client is None:
                            self.stdout.write(f'[dry-run] crearía cliente para: {username}')
                        elif update:
                            self.stdout.write(f'[dry-run] actualizaría cliente de: {username}')
                continue

            try:
                with transaction.atomic():
                    if user is None:
                        user = User(
                            username=username,
                            dni=username,
                            full_name=full_name,
                            email=email,
                            is_active=True,
                            is_staff=False,
                            is_superuser=False,
                            is_change_password=bool(password),
                        )
                        if password:
                            user.set_password(password)
                        else:
                            user.set_unusable_password()
                        user.save()
                        created += 1
                    elif update:
                        changed = False
                        if full_name and user.full_name != full_name:
                            user.full_name = full_name
                            changed = True
                        if email and user.email != email:
                            user.email = email
                            changed = True
                        if changed:
                            user.save()
                            updated += 1
                        else:
                            skipped += 1
                    else:
                        skipped += 1

                    if group is not None and not user.groups.filter(id=group.id).exists():
                        user.groups.add(group)

                    if as_client:
                        c_created, c_updated = self._sync_client(
                            user, raw_mobile, raw_address, used_mobiles,
                            update, index, username, errors,
                        )
                        clients_created += c_created
                        clients_updated += c_updated
            except IntegrityError as exc:
                errors.append(f'fila {index} ({username}): {exc}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Usuarios creados: {created} | Actualizados: {updated} | '
                f'Omitidos: {skipped} | Clientes creados: {clients_created} | '
                f'Clientes actualizados: {clients_updated} | Errores: {len(errors)}'
            )
        )
        for err in errors:
            self.stdout.write(self.style.WARNING(f' - {err}'))

    def _sync_client(
        self, user, raw_mobile, raw_address, used_mobiles,
        update, index, username, errors,
    ):
        """Devuelve (clientes_creados, clientes_actualizados)."""
        client = Client.objects.filter(user=user).first()

        if client is None:
            mobile = self._pick_mobile(raw_mobile, user.id, used_mobiles)
            Client.objects.create(
                user=user, mobile=mobile, address=raw_address or None
            )
            return 1, 0

        if not update:
            return 0, 0

        changed = False
        new_mobile = re.sub(r'\D', '', raw_mobile or '')
        if new_mobile and len(new_mobile) <= 10 and new_mobile != client.mobile:
            if Client.objects.filter(mobile=new_mobile).exclude(id=client.id).exists():
                errors.append(
                    f'fila {index} ({username}): celular "{new_mobile}" ya está en uso; '
                    f'se conserva el actual'
                )
            else:
                used_mobiles.discard(client.mobile)
                client.mobile = new_mobile
                used_mobiles.add(new_mobile)
                changed = True
        if raw_address and raw_address != (client.address or ''):
            client.address = raw_address
            changed = True

        if changed:
            client.save()
            return 0, 1
        return 0, 0

    @staticmethod
    def _pick_mobile(raw, user_id, used_mobiles):
        digits = re.sub(r'\D', '', raw or '')
        if digits and len(digits) <= 10 and digits not in used_mobiles:
            used_mobiles.add(digits)
            return digits

        candidate_id = user_id
        while True:
            candidate = '9{:09d}'.format(candidate_id)
            if candidate not in used_mobiles:
                used_mobiles.add(candidate)
                return candidate
            candidate_id += 1
