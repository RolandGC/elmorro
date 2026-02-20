from config.wsgi import *
from core.security.models import *
from django.contrib.auth.models import Permission
from core.pos.models import *

# Crear o actualizar Dashboard
dashboard, created = Dashboard.objects.update_or_create(name='El Morro SAC')
dashboard.icon = 'fas fa-shopping-cart'
dashboard.layout = 1
dashboard.card = ' '
dashboard.navbar = 'navbar-dark navbar-primary'
dashboard.brand_logo = ' '
dashboard.sidebar = 'sidebar-light-primary'
dashboard.save()
print('Dashboard: {} {}'.format(dashboard.name, '(creado)' if created else '(actualizado)'))

# Crear o actualizar Company
company, created = Company.objects.update_or_create(name='El Morro S.A.C.')
company.ruc = '20532482683'
company.email = 'area.ti@elmorro.com.pe'
company.phone = '46200233'
company.mobile = '913364475'
company.desc = 'Software'
company.website = 'elmorro.com.pe'
company.address = 'Parque ind. Mz: I Lt: 13'
company.save()
print('Company: {} {}'.format(company.name, '(creada)' if created else '(actualizada)'))

# ===================== MODULE TYPES =====================

type_security, created = ModuleType.objects.get_or_create(name='Seguridad')
print('{} {}'.format(type_security.name, '(creado)' if created else '(actualizado)'))

type_bodega, created = ModuleType.objects.get_or_create(name='Almacén')
print('{} {}'.format(type_bodega.name, '(creado)' if created else '(actualizado)'))

type_administrativo, created = ModuleType.objects.get_or_create(name='Administrativo')
print('{} {}'.format(type_administrativo.name, '(creado)' if created else '(actualizado)'))

type_facturacion, created = ModuleType.objects.get_or_create(name='Facturación')
print('{} {}'.format(type_facturacion.name, '(creado)' if created else '(actualizado)'))

type_reportes, created = ModuleType.objects.get_or_create(name='Reportes')
print('{} {}'.format(type_reportes.name, '(creado)' if created else '(actualizado)'))

# ===================== SEGURIDAD MODULES =====================

module, created = Module.objects.get_or_create(url='/security/module/type/')
module.moduletype_id = type_security.id
module.name = 'Tipos de Módulos'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-door-open'
module.description = 'Permite administrar los tipos de módulos del sistema'
module.save()
for p in Permission.objects.filter(content_type__model=ModuleType._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/security/module/')
module.moduletype_id = type_security.id
module.name = 'Módulos'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-th-large'
module.description = 'Permite administrar los módulos del sistema'
module.save()
for p in Permission.objects.filter(content_type__model=Module._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/security/group/')
module.moduletype_id = type_security.id
module.name = 'Grupos'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-users'
module.description = 'Permite administrar los grupos de usuarios del sistema'
module.save()
for p in Permission.objects.filter(content_type__model=Group._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/security/database/backups/')
module.moduletype_id = type_security.id
module.name = 'Respaldos'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-database'
module.description = 'Permite administrar los respaldos de base de datos'
module.save()
for p in Permission.objects.filter(content_type__model=DatabaseBackups._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/security/dashboard/update/')
module.moduletype_id = type_security.id
module.name = 'Conf. Dashboard'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-tools'
module.description = 'Permite configurar los datos de la plantilla'
module.save()
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/security/access/users/')
module.moduletype_id = type_security.id
module.name = 'Accesos'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-user-secret'
module.description = 'Permite administrar los accesos de los usuarios'
module.save()
for p in Permission.objects.filter(content_type__model=AccessUsers._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/user/')
module.moduletype_id = type_security.id
module.name = 'Usuarios'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-user'
module.description = 'Permite administrar a los administradores del sistema'
module.save()
for p in Permission.objects.filter(content_type__model=User._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

# ===================== BODEGA MODULES =====================

module, created = Module.objects.get_or_create(url='/pos/scm/provider/')
module.moduletype_id = type_bodega.id
module.name = 'Proveedores'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-truck'
module.description = 'Permite administrar a los proveedores de las compras'
module.save()
for p in Permission.objects.filter(content_type__model=Provider._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/pos/scm/category/')
module.moduletype_id = type_bodega.id
module.name = 'Categorías'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-truck-loading'
module.description = 'Permite administrar las categorías de los productos'
module.save()
for p in Permission.objects.filter(content_type__model=Category._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/pos/scm/product/')
module.moduletype_id = type_bodega.id
module.name = 'Productos'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-box'
module.description = 'Permite administrar los productos del sistema'
module.save()
for p in Permission.objects.filter(content_type__model=Product._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/pos/scm/purchase/')
module.moduletype_id = type_bodega.id
module.name = 'Compras'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-dolly-flatbed'
module.description = 'Permite administrar las compras de los productos'
module.save()
for p in Permission.objects.filter(content_type__model=Purchase._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/pos/scm/product/stock/adjustment/')
module.moduletype_id = type_bodega.id
module.name = 'Ajuste de Stock'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-sliders-h'
module.description = 'Permite administrar los ajustes de stock de productos'
module.save()
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/pos/scm/product/generadorqr/')
module.moduletype_id = type_bodega.id
module.name = 'Código barra'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-barcode'
module.description = 'Permite administrar la impresión de códigos de barra'
module.save()
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

# ===================== ADMINISTRATIVO MODULES =====================

module, created = Module.objects.get_or_create(url='/pos/frm/type/expense/')
module.moduletype_id = type_administrativo.id
module.name = 'Tipos de Gastos'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-comments-dollar'
module.description = 'Permite administrar los tipos de gastos'
module.save()
for p in Permission.objects.filter(content_type__model=TypeExpense._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/pos/frm/expenses/')
module.moduletype_id = type_administrativo.id
module.name = 'Gastos'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-file-invoice-dollar'
module.description = 'Permite administrar los gastos de la compañia'
module.save()
for p in Permission.objects.filter(content_type__model=Expenses._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/pos/frm/ctas/collect/')
module.moduletype_id = type_administrativo.id
module.name = 'Cuentas por cobrar'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-funnel-dollar'
module.description = 'Permite administrar las cuentas por cobrar de los clientes'
module.save()
for p in Permission.objects.filter(content_type__model=CtasCollect._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/pos/frm/debts/pay/')
module.moduletype_id = type_administrativo.id
module.name = 'Cuentas por pagar'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-money-check-alt'
module.description = 'Permite administrar las cuentas por pagar de los proveedores'
module.save()
for p in Permission.objects.filter(content_type__model=DebtsPay._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/pos/frm/box/')
module.moduletype_id = type_administrativo.id
module.name = 'Cierre caja'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-money-check-alt'
module.description = 'Permite administrar los cierres de caja'
module.save()
for p in Permission.objects.filter(content_type__model=Box._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/pos/frm/series/')
module.moduletype_id = type_administrativo.id
module.name = 'Invoice Series'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-receipt'
module.description = 'Permite administrar las series de facturación'
module.save()
for p in Permission.objects.filter(content_type__model=Series._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/pos/frm/user_series/')
module.moduletype_id = type_administrativo.id
module.name = 'Administración de Series'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-user-tie'
module.description = 'Permite asignar series a vendedores'
module.save()
for p in Permission.objects.filter(content_type__model=UserSeries._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/pos/frm/expense_series/')
module.moduletype_id = type_administrativo.id
module.name = 'Series de Gastos'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-receipt'
module.description = 'Permite administrar las series de gastos'
module.save()
for p in Permission.objects.filter(content_type__model=ExpenseSeries._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/pos/frm/user_expense_series/')
module.moduletype_id = type_administrativo.id
module.name = 'Administración de Series de Gastos'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-user-tie'
module.description = 'Permite asignar series de gastos a usuarios'
module.save()
for p in Permission.objects.filter(content_type__model=UserExpenseSeries._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/pos/frm/user/sales/report/')
module.moduletype_id = type_administrativo.id
module.name = 'Reprt Cobranzas por Usuario'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-chart-line'
module.description = 'Permite ver los reportes de Cobranzas detallados por usuario y método de pago'
module.save()
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

# ===================== FACTURACION MODULES =====================

module, created = Module.objects.get_or_create(url='/pos/crm/client/')
module.moduletype_id = type_facturacion.id
module.name = 'Clientes'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-user-friends'
module.description = 'Permite administrar los clientes del sistema'
module.save()
for p in Permission.objects.filter(content_type__model=Client._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/pos/crm/sale/admin/')
module.moduletype_id = type_facturacion.id
module.name = 'Cobranzas'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-shopping-cart'
module.description = 'Permite administrar las cobranzas'
module.save()
for p in Permission.objects.filter(content_type__model=Sale._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/pos/crm/sale/client/')
module.name = 'Cobranzas'
module.is_active = True
module.is_vertical = False
module.is_visible = True
module.icon = 'fas fa-shopping-cart'
module.description = 'Permite administrar las cobranzas de los clientes'
module.save()
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/pos/crm/promotions/')
module.moduletype_id = type_facturacion.id
module.name = 'Promociones'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'far fa-calendar-check'
module.description = 'Permite administrar las promociones de los productos'
module.save()
for p in Permission.objects.filter(content_type__model=Promotions._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/pos/crm/devolution/')
module.moduletype_id = type_facturacion.id
module.name = 'Devoluciones'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-exchange-alt'
module.description = 'Permite administrar las devoluciones de los productos'
module.save()
for p in Permission.objects.filter(content_type__model=Devolution._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/pos/frm/paymentbank/')
module.moduletype_id = type_facturacion.id
module.name = 'Bancos de Pago'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-university'
module.description = 'Permite administrar los bancos de pago'
module.save()
for p in Permission.objects.filter(content_type__model=PaymentBank._meta.label.split('.')[1].lower()):
    module.permits.add(p)
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

# ===================== REPORTES MODULES =====================

module, created = Module.objects.get_or_create(url='/reports/sale/')
module.moduletype_id = type_reportes.id
module.name = 'Cobranzas'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-chart-bar'
module.description = 'Permite ver los reportes de las cobranzas realizadas'
module.save()
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/reports/purchase/')
module.moduletype_id = type_reportes.id
module.name = 'Compras'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-chart-bar'
module.description = 'Permite ver los reportes de las compras'
module.save()
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/reports/expenses/')
module.moduletype_id = type_reportes.id
module.name = 'Gastos'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-chart-bar'
module.description = 'Permite ver los reportes de los gastos'
module.save()
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/reports/debts/pay/')
module.moduletype_id = type_reportes.id
module.name = 'Cuentas por Pagar'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-chart-bar'
module.description = 'Permite ver los reportes de las cuentas por pagar'
module.save()
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/reports/ctas/collect/')
module.moduletype_id = type_reportes.id
module.name = 'Cuentas por Cobrar'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-chart-bar'
module.description = 'Permite ver los reportes de las cuentas por cobrar'
module.save()
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/reports/results/')
module.moduletype_id = type_reportes.id
module.name = 'Perdidas y Ganancias'
module.is_active = True
module.is_vertical = True
module.is_visible = True
module.icon = 'fas fa-chart-bar'
module.description = 'Permite ver los reportes de perdidas y ganancias'
module.save()
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

# ===================== UTILITY MODULES =====================

module, created = Module.objects.get_or_create(url='/user/update/password/')
module.name = 'Cambiar password'
module.is_active = True
module.is_vertical = False
module.is_visible = True
module.icon = 'fas fa-key'
module.description = 'Permite cambiar tu password de tu cuenta'
module.save()
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/user/update/profile/')
module.name = 'Editar perfil'
module.is_active = True
module.is_vertical = False
module.is_visible = True
module.icon = 'fas fa-user'
module.description = 'Permite cambiar la información de tu cuenta'
module.save()
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/pos/crm/client/update/profile/')
module.name = 'Editar perfil Cliente'
module.is_active = True
module.is_vertical = False
module.is_visible = True
module.icon = 'fas fa-user'
module.description = 'Permite cambiar la información de tu cuenta'
module.save()
print('{} {}'.format(module.name, '(creado)' if created else '(actualizado)'))

module, created = Module.objects.get_or_create(url='/pos/crm/company/update/')
module.name = 'Compañia'
module.is_active = True
module.is_vertical = False
module.is_visible = True
module.icon = 'fa fa-cogs'
module.description = 'Permite gestionar la información de la compañia'
module.save()
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

vendedor_group, createdVendedor = Group.objects.get_or_create(name='Vendedor')
print('Grupo {}: {}'.format(vendedor_group.name, '(creado)' if createdVendedor else '(actualizado)'))

# ===================== USUARIO ADMINISTRADOR =====================

user, created = User.objects.get_or_create(username='Administrador')
if created:
    user.full_name = 'Admin'
    user.dni = '00112233'
    user.email = 'area.ti@elmorro.com.pe'
    user.is_active = True
    user.is_superuser = True
    user.is_staff = True
    user.set_password('12345678')
    user.save()
    user.groups.add(admin_group)
    print('Usuario {}: (creado)'.format(user.username))
else:
    print('Usuario {}: (actualizado)'.format(user.username))
