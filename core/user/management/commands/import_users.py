import csv
import os

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from core.user.models import User


class Command(BaseCommand):
    help = (
        'Importa usuarios desde un CSV (columnas: username, full_name; '
        'opcional: email). Es idempotente: omite los que ya existen por '
        'username o dni, por lo que puede ejecutarse varias veces.'
    )

    def add_arguments(self, parser):
        parser.add_argument('csv_path', help='Ruta del archivo CSV a importar.')
        parser.add_argument(
            '--password',
            default=None,
            help='Contraseña temporal para todos los usuarios creados. '
                 'Si se omite, la cuenta queda sin login (contraseña inutilizable).',
        )
        parser.add_argument(
            '--group',
            default=None,
            help='Nombre del grupo a asignar a los usuarios creados (ej. Cliente).',
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
            rows = list(reader)

        created = 0
        skipped = 0
        errors = []

        for index, row in enumerate(rows, start=2):
            username = (row.get('username') or '').strip()
            full_name = (row.get('full_name') or '').strip()
            email = (row.get('email') or '').strip() or None

            if not username:
                errors.append(f'fila {index}: username vacío, se omite')
                continue

            if len(username) > 13:
                errors.append(
                    f'fila {index}: "{username}" supera 13 caracteres (límite de dni), se omite'
                )
                continue

            exists = (
                User.objects.filter(username=username).exists()
                or User.objects.filter(dni=username).exists()
            )
            if exists:
                skipped += 1
                continue

            if dry_run:
                created += 1
                self.stdout.write(f'[dry-run] crearía: {username} | {full_name}')
                continue

            try:
                with transaction.atomic():
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
                    if group is not None:
                        user.groups.add(group)
                created += 1
            except IntegrityError as exc:
                errors.append(f'fila {index} ({username}): {exc}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Creados: {created} | Omitidos (ya existían): {skipped} | Errores: {len(errors)}'
            )
        )
        for err in errors:
            self.stdout.write(self.style.WARNING(f' - {err}'))
