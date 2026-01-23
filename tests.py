from config.wsgi import *
from core.security.models import *
from django.contrib.auth.models import Permission
from core.pos.models import *

# Crear o actualizar Dashboard
dashboard, created = Dashboard.objects.get_or_create(name='El Morro SAC')
dashboard.icon = 'fas fa-shopping-cart'
dashboard.layout = 1
dashboard.card = ' '
dashboard.navbar = 'navbar-dark navbar-primary'
dashboard.brand_logo = ' '
dashboard.sidebar = 'sidebar-light-primary'
dashboard.save()
print('Dashboard: {} {}'.format(dashboard.name, '(creado)' if created else '(actualizado)'))

# Crear o actualizar Company
company, created = Company.objects.get_or_create(name='El Morro S.A.C.')
company.ruc = '10462002039'
company.email = 'seo.roland@gamil.com'
company.phone = '462002'
company.mobile = '921047681'
company.desc = 'Software'
company.website = 'elmorro.com.pe'
company.address = 'av. industrial S/N '
company.igv = 18.00
company.save()
print('Company: {} {}'.format(company.name, '(creada)' if created else '(actualizada)'))

# ===================== MODULE TYPES =====================

type_security, created = ModuleType.objects.get_or_create(
    name='Seguridad',
    defaults={'icon': 'fa fa-key'}
)
print('{} {}'.format(type_security.name, '(creado)' if created else '(actualizado)'))

type_bodega, created = ModuleType.objects.get_or_create(
    name='Bodega',
    defaults={'icon': 'fa fa-box-open'}
)
print('{} {}'.format(type_bodega.name, '(creado)' if created else '(actualizado)'))

type_administrativo, created = ModuleType.objects.get_or_create(
    name='Administrativo',
    defaults={'icon': 'fa fa-briefcase'}
)
print('{} {}'.format(type_administrativo.name, '(creado)' if created else '(actualizado)'))

type_facturacion, created = ModuleType.objects.get_or_create(
    name='Facturación',
    defaults={'icon': 'fa fa-receipt'}
)
print('{} {}'.format(type_facturacion.name, '(creado)' if created else '(actualizado)'))

type_reportes, created = ModuleType.objects.get_or_create(
    name='Reportes',
    defaults={'icon': 'fa fa-list-alt'}
)
print('{} {}'.format(type_reportes.name, '(creado)' if created else '(actualizado)'))

# ===================== SEGURIDAD MODULES =====================

module, created = Module.objects.get_or_create(
    moduletype_id=type_security.id,
    url='/security/module/type/',
    defaults={
        'name': 'Tipos de Módulos',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-door-open',
        'description': 'Permite administrar los tipos de módulos del sistema'
    }
)
for p in Permission.objects.filter(content_type__model=ModuleType._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_security.id,
    url='/security/module/',
    defaults={
        'name': 'Módulos',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-th-large',
        'description': 'Permite administrar los módulos del sistema'
    }
)
for p in Permission.objects.filter(content_type__model=Module._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_security.id,
    url='/security/group/',
    defaults={
        'name': 'Grupos',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-users',
        'description': 'Permite administrar los grupos de usuarios del sistema'
    }
)
for p in Permission.objects.filter(content_type__model=Group._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_security.id,
    url='/security/database/backups/',
    defaults={
        'name': 'Respaldos',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-database',
        'description': 'Permite administrar los respaldos de base de datos'
    }
)
for p in Permission.objects.filter(content_type__model=DatabaseBackups._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_security.id,
    url='/security/dashboard/update/',
    defaults={
        'name': 'Conf. Dashboard',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-tools',
        'description': 'Permite configurar los datos de la plantilla'
    }
)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_security.id,
    url='/security/access/users/',
    defaults={
        'name': 'Accesos',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-user-secret',
        'description': 'Permite administrar los accesos de los usuarios'
    }
)
for p in Permission.objects.filter(content_type__model=AccessUsers._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_security.id,
    url='/user/',
    defaults={
        'name': 'Usuarios',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-user',
        'description': 'Permite administrar a los administradores del sistema'
    }
)
for p in Permission.objects.filter(content_type__model=User._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

# ===================== BODEGA MODULES =====================

module, created = Module.objects.get_or_create(
    moduletype_id=type_bodega.id,
    url='/pos/scm/provider/',
    defaults={
        'name': 'Proveedores',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-truck',
        'description': 'Permite administrar a los proveedores de las compras'
    }
)
for p in Permission.objects.filter(content_type__model=Provider._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_bodega.id,
    url='/pos/scm/category/',
    defaults={
        'name': 'Categorías',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-truck-loading',
        'description': 'Permite administrar las categorías de los productos'
    }
)
for p in Permission.objects.filter(content_type__model=Category._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_bodega.id,
    url='/pos/scm/product/',
    defaults={
        'name': 'Productos',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-box',
        'description': 'Permite administrar los productos del sistema'
    }
)
for p in Permission.objects.filter(content_type__model=Product._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_bodega.id,
    url='/pos/scm/purchase/',
    defaults={
        'name': 'Compras',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-dolly-flatbed',
        'description': 'Permite administrar las compras de los productos'
    }
)
for p in Permission.objects.filter(content_type__model=Purchase._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_bodega.id,
    url='/pos/scm/product/stock/adjustment/',
    defaults={
        'name': 'Ajuste de Stock',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-sliders-h',
        'description': 'Permite administrar los ajustes de stock de productos'
    }
)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_bodega.id,
    url='/pos/scm/product/generadorqr/',
    defaults={
        'name': 'Código barra',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-barcode',
        'description': 'Permite administrar la impresión de códigos de barra'
    }
)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

# ===================== ADMINISTRATIVO MODULES =====================

module, created = Module.objects.get_or_create(
    moduletype_id=type_administrativo.id,
    url='/pos/frm/type/expense/',
    defaults={
        'name': 'Tipos de Gastos',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-comments-dollar',
        'description': 'Permite administrar los tipos de gastos'
    }
)
for p in Permission.objects.filter(content_type__model=TypeExpense._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_administrativo.id,
    url='/pos/frm/expenses/',
    defaults={
        'name': 'Gastos',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-file-invoice-dollar',
        'description': 'Permite administrar los gastos de la compañia'
    }
)
for p in Permission.objects.filter(content_type__model=Expenses._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_administrativo.id,
    url='/pos/frm/ctas/collect/',
    defaults={
        'name': 'Cuentas por cobrar',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-funnel-dollar',
        'description': 'Permite administrar las cuentas por cobrar de los clientes'
    }
)
for p in Permission.objects.filter(content_type__model=CtasCollect._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_administrativo.id,
    url='/pos/frm/debts/pay/',
    defaults={
        'name': 'Cuentas por pagar',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-money-check-alt',
        'description': 'Permite administrar las cuentas por pagar de los proveedores'
    }
)
for p in Permission.objects.filter(content_type__model=DebtsPay._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_administrativo.id,
    url='/pos/frm/box/',
    defaults={
        'name': 'Cierre caja',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-money-check-alt',
        'description': 'Permite administrar los cierres de caja'
    }
)
for p in Permission.objects.filter(content_type__model=Box._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_administrativo.id,
    url='/pos/frm/series/',
    defaults={
        'name': 'Invoice Series',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-receipt',
        'description': 'Permite administrar las series de facturación'
    }
)
for p in Permission.objects.filter(content_type__model=Series._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_administrativo.id,
    url='/pos/frm/user_series/',
    defaults={
        'name': 'Administración de Series',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-user-tie',
        'description': 'Permite asignar series a vendedores'
    }
)
for p in Permission.objects.filter(content_type__model=UserSeries._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_administrativo.id,
    url='/pos/frm/user/sales/report/',
    defaults={
        'name': 'Reporte de Ventas por Usuario',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-chart-line',
        'description': 'Permite ver los reportes de ventas detallados por usuario y método de pago'
    }
)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

# ===================== FACTURACION MODULES =====================

module, created = Module.objects.get_or_create(
    moduletype_id=type_facturacion.id,
    url='/pos/crm/client/',
    defaults={
        'name': 'Clientes',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-user-friends',
        'description': 'Permite administrar los clientes del sistema'
    }
)
for p in Permission.objects.filter(content_type__model=Client._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_facturacion.id,
    url='/pos/crm/sale/admin/',
    defaults={
        'name': 'Ventas',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-shopping-cart',
        'description': 'Permite administrar las ventas de los productos'
    }
)
for p in Permission.objects.filter(content_type__model=Sale._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    url='/pos/crm/sale/client/',
    defaults={
        'name': 'Ventas',
        'is_active': True,
        'is_vertical': False,
        'is_visible': True,
        'icon': 'fas fa-shopping-cart',
        'description': 'Permite administrar las ventas de los productos'
    }
)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_facturacion.id,
    url='/pos/crm/promotions/',
    defaults={
        'name': 'Promociones',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'far fa-calendar-check',
        'description': 'Permite administrar las promociones de los productos'
    }
)
for p in Permission.objects.filter(content_type__model=Promotions._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_facturacion.id,
    url='/pos/crm/devolution/',
    defaults={
        'name': 'Devoluciones',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-exchange-alt',
        'description': 'Permite administrar las devoluciones de los productos'
    }
)
for p in Permission.objects.filter(content_type__model=Devolution._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_facturacion.id,
    url='/pos/frm/paymentbank/',
    defaults={
        'name': 'Bancos de Pago',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-university',
        'description': 'Permite administrar los bancos de pago'
    }
)
for p in Permission.objects.filter(content_type__model=PaymentBank._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

# ===================== REPORTES MODULES =====================

module, created = Module.objects.get_or_create(
    moduletype_id=type_reportes.id,
    url='/reports/sale/',
    defaults={
        'name': 'Ventas',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-chart-bar',
        'description': 'Permite ver los reportes de las ventas'
    }
)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_reportes.id,
    url='/reports/purchase/',
    defaults={
        'name': 'Compras',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-chart-bar',
        'description': 'Permite ver los reportes de las compras'
    }
)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_reportes.id,
    url='/reports/expenses/',
    defaults={
        'name': 'Gastos',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-chart-bar',
        'description': 'Permite ver los reportes de los gastos'
    }
)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_reportes.id,
    url='/reports/debts/pay/',
    defaults={
        'name': 'Cuentas por Pagar',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-chart-bar',
        'description': 'Permite ver los reportes de las cuentas por pagar'
    }
)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_reportes.id,
    url='/reports/ctas/collect/',
    defaults={
        'name': 'Cuentas por Cobrar',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-chart-bar',
        'description': 'Permite ver los reportes de las cuentas por cobrar'
    }
)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    moduletype_id=type_reportes.id,
    url='/reports/results/',
    defaults={
        'name': 'Perdidas y Ganancias',
        'is_active': True,
        'is_vertical': True,
        'is_visible': True,
        'icon': 'fas fa-chart-bar',
        'description': 'Permite ver los reportes de perdidas y ganancias'
    }
)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

# ===================== UTILITY MODULES =====================

module, created = Module.objects.get_or_create(
    url='/user/update/password/',
    defaults={
        'name': 'Cambiar password',
        'is_active': True,
        'is_vertical': False,
        'is_visible': True,
        'icon': 'fas fa-key',
        'description': 'Permite cambiar tu password de tu cuenta'
    }
)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    url='/user/update/profile/',
    defaults={
        'name': 'Editar perfil',
        'is_active': True,
        'is_vertical': False,
        'is_visible': True,
        'icon': 'fas fa-user',
        'description': 'Permite cambiar la información de tu cuenta'
    }
)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    url='/pos/crm/client/update/profile/',
    defaults={
        'name': 'Editar perfil Cliente',
        'is_active': True,
        'is_vertical': False,
        'is_visible': True,
        'icon': 'fas fa-user',
        'description': 'Permite cambiar la información de tu cuenta'
    }
)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(
    url='/pos/crm/company/update/',
    defaults={
        'name': 'Compañia',
        'is_active': True,
        'is_vertical': False,
        'is_visible': True,
        'icon': 'fa fa-cogs',
        'description': 'Permite gestionar la información de la compañia'
    }
)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

# ===================== GROUPS =====================

admin_group, created = Group.objects.get_or_create(name='Administrador')
print('Grupo {}: {}'.format(admin_group.name, '(creado)' if created else '(actualizado)'))

# Siempre agregar módulos al grupo administrador (para nuevos módulos)
for m in Module.objects.filter().exclude(url__in=['/pos/crm/client/update/profile/', '/pos/crm/sale/client/']):
    gm, _ = GroupModule.objects.get_or_create(module=m, group=admin_group)
    for perm in m.permits.all():
        admin_group.permissions.add(perm)
        _, _ = GroupPermission.objects.get_or_create(
            module_id=m.id,
            group_id=admin_group.id,
            permission_id=perm.id
        )

client_group, created = Group.objects.get_or_create(name='Cliente')
print('Grupo {}: {}'.format(client_group.name, '(creado)' if created else '(actualizado)'))

# Siempre agregar módulos al grupo cliente (para nuevos módulos)
for m in Module.objects.filter(url__in=['/pos/crm/client/update/profile/', '/pos/crm/sale/client/', '/user/update/password/']):
    gm, _ = GroupModule.objects.get_or_create(module=m, group=client_group)

# ===================== USUARIO ADMINISTRADOR =====================

user, created = User.objects.get_or_create(username='Neo')
if created:
    user.full_name = 'Roland Gutierrez'
    user.dni = '462002039'
    user.email = 'seo.cristhian@gmail.com'
    user.is_active = True
    user.is_superuser = True
    user.is_staff = True
    user.set_password('Enyaeslamejor12')
    user.save()
    user.groups.add(admin_group)
    print('Usuario {}: (creado)'.format(user.username))
else:
    print('Usuario {}: (actualizado)'.format(user.username))
