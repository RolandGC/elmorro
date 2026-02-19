import math
import os
import re
from datetime import datetime, time, timezone, date

from django.db.models import Q

from django.db import models
from django.db.models import FloatField
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.forms import model_to_dict

from django.utils import timezone

from config import settings
from core.pos.choices import payment_condition, payment_method, voucher, unit
from core.user.models import User

from datetime import datetime

def current_time():
    return datetime.now().time()

class Series(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Nombre')

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Serie de Facturación'
        verbose_name_plural = 'Series de Facturación'
        ordering = ['-id']


class UserSeries(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario')
    series = models.OneToOneField(Series, on_delete=models.CASCADE, verbose_name='Serie Asignada')
    date_assigned = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Asignación')

    def __str__(self):
        return f'{self.user.full_name} - {self.series.name}'

    def toJSON(self):
        item = model_to_dict(self, exclude=['date_assigned'])
        item['user'] = self.user.toJSON()
        item['series'] = self.series.toJSON()
        item['date_assigned'] = self.date_assigned.strftime('%Y-%m-%d %H:%M')
        return item

    class Meta:
        verbose_name = 'Asignación de Serie'
        verbose_name_plural = 'Asignaciones de Series'
        default_permissions = ()
        permissions = (
            ('view_userseries', 'Can view Asignaciones de Series'),
            ('add_userseries', 'Can add Asignaciones de Series'),
            ('change_userseries', 'Can change Asignaciones de Series'),
            ('delete_userseries', 'Can delete Asignaciones de Series'),
        )
        ordering = ['-id']


class PaymentBank(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Nombre del Banco')

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Banco de Pago'
        verbose_name_plural = 'Bancos de Pago'
        default_permissions = ()
        permissions = (
            ('view_paymentbank', 'Can view Bancos de Pago'),
            ('add_paymentbank', 'Can add Bancos de Pago'),
            ('change_paymentbank', 'Can change Bancos de Pago'),
            ('delete_paymentbank', 'Can delete Bancos de Pago'),
        )
        ordering = ['-id']


class Company(models.Model):
    name = models.CharField(max_length=50, verbose_name='Nombre')
    ruc = models.CharField(max_length=13, verbose_name='Ruc')
    address = models.CharField(max_length=200, verbose_name='Dirección')
    mobile = models.CharField(max_length=10, verbose_name='Teléfono celular')
    phone = models.CharField(max_length=9, verbose_name='Teléfono convencional')
    email = models.CharField(max_length=50, verbose_name='Email')
    website = models.CharField(max_length=250, verbose_name='Página web')
    desc = models.CharField(max_length=500, null=True, blank=True, verbose_name='Descripción')
    image = models.ImageField(null=True, blank=True, upload_to='company/%Y/%m/%d', verbose_name='Logo')
    igv = models.DecimalField(default=0.00, decimal_places=2, max_digits=9, verbose_name='Igv')

    def __str__(self):
        return self.name

    def get_image(self):
        if self.image:
            return '{}{}'.format(settings.MEDIA_URL, self.image)
        return '{}{}'.format(settings.STATIC_URL, 'img/default/empty.png')

    def get_igv(self):
        return format(self.igv, '.2f')

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        default_permissions = ()
        permissions = (
            ('view_company', 'Can view Company'),
        )
        ordering = ['-id']

class Provider(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Nombre')
    ruc = models.CharField(max_length=13, unique=True, verbose_name='Ruc')
    mobile = models.CharField(max_length=10, unique=True, verbose_name='Teléfono celular')
    address = models.CharField(max_length=500, null=True, blank=True, verbose_name='Dirección')
    email = models.CharField(max_length=50, unique=True, verbose_name='Email')

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['-id']


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Nombre')
    inventoried = models.BooleanField(default=True, verbose_name='¿Es inventariado?')

    def __str__(self):
        return '{} / {}'.format(self.name, self.get_inventoried())

    def get_inventoried(self):
        if self.inventoried:
            return 'Inventariado'
        return 'No inventariado'

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['-id']


class Product(models.Model):
    codebar = models.CharField(max_length=20, null=True, blank=True, verbose_name='Código')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Categoría')
    name = models.CharField(max_length=150, verbose_name='Nombre')
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Precio de Compra')
    price_min_sale = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Precio mínimo de venta', null=True, blank=True)
    pvp = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Precio de Venta')
    date_into = models.DateField(default=datetime.now, verbose_name='Fecha de Ingreso')
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='product/%Y/%m/%d', verbose_name='Imagen', null=True, blank=True)

    def __str__(self):
        return '{} / {} / {}'.format(self.name, self.category.name, self.codebar)

    def remove_image(self):
        try:
            if self.image:
                os.remove(self.image.path)
        except:
            pass
        finally:
            self.image = None

    def toJSON(self):
        item = {
            'id': self.id,
            'codebar': self.codebar,
            'name': self.name,
            'category': self.category.toJSON(),
            'price': format(self.price, '.2f'),
            'price_promotion': format(self.get_price_promotion(), '.2f'),
            'price_current': format(self.get_price_current(), '.2f'),
            'pvp': format(self.pvp, '.2f'),
            'price_min_sale': format(self.price_min_sale, '.2f'),
            'date_into': self.date_into.strftime('%d/%m/%Y'),
            'image': self.get_image(),
            'stock': self.stock,
        }
        return item

    def get_price_promotion(self):
        promotions = self.promotionsdetail_set.filter(promotion__state=True)
        if promotions.exists():
            return promotions[0].price_final
        return 0.00

    def get_price_current(self):
        price_promotion = self.get_price_promotion()
        if price_promotion > 0:
            return price_promotion
        return self.pvp

    def get_image(self):
        if self.image:
            return '{}{}'.format(settings.MEDIA_URL, self.image)
        return '{}{}'.format(settings.STATIC_URL, 'img/default/empty.png')

    def delete(self, using=None, keep_parents=False):
        try:
            os.remove(self.image.path)
        except:
            pass
        super(Product, self).delete()

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-name']



class Purchase(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.PROTECT)
    payment_condition = models.CharField(choices=payment_condition, max_length=50, default='contado')
    date_joined = models.DateField(default=datetime.now)
    end_credit = models.DateField(default=datetime.now)
    subtotal = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __str__(self):
        return self.provider.name

    def calculate_invoice(self):
        subtotal = 0.00
        for d in self.purchasedetail_set.all():
            subtotal += float(d.price) * int(d.cant)
        self.subtotal = subtotal
        self.save()

    def delete(self, using=None, keep_parents=False):
        try:
            for i in self.purchasedetail_set.all():
                i.product.stock -= i.cant
                i.product.save()
                i.delete()
        except:
            pass
        super(Purchase, self).delete()

    def toJSON(self):
        item = model_to_dict(self)
        item['nro'] = format(self.id, '06d')
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['end_credit'] = self.end_credit.strftime('%Y-%m-%d')
        item['provider'] = self.provider.toJSON()
        item['payment_condition'] = {'id': self.payment_condition, 'name': self.get_payment_condition_display()}
        item['subtotal'] = format(self.subtotal, '.2f')
        return item

    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        default_permissions = ()
        permissions = (
            ('view_purchase', 'Can view Compras'),
            ('add_purchase', 'Can add Compras'),
            ('delete_purchase', 'Can delete Compras'),
        )
        ordering = ['-id']


class PurchaseDetail(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    cant = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    subtotal = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __str__(self):
        return self.product.name

    def toJSON(self):
        item = model_to_dict(self, exclude=['purchase'])
        item['product'] = self.product.toJSON()
        item['price'] = format(self.price, '.2f')
        item['dscto'] = format(self.dscto, '.2f')
        item['subtotal'] = format(self.subtotal, '.2f')
        return item

    class Meta:
        verbose_name = 'Detalle de Compra'
        verbose_name_plural = 'Detalle de Compras'
        permissions = ()
        ordering = ['-id']


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    mobile = models.CharField(max_length=10, unique=True, verbose_name='Teléfono')
    address = models.CharField(max_length=500, null=True, blank=True, verbose_name='Dirección')

    def __str__(self):
        return '{} / {}'.format(self.user.full_name, self.user.dni)

    def toJSON(self):
        item = model_to_dict(self)
        item['user'] = self.user.toJSON()
        return item

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-id']


class Sale(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, null=True, blank=True)
    employee = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    payment_condition = models.CharField(choices=payment_condition, max_length=50, default='contado')
    payment_method = models.CharField(choices=payment_method, max_length=50, default='efectivo')
    type_voucher = models.CharField(choices=voucher, max_length=50, default='ticket')
    date_joined = models.DateTimeField(default=datetime.now)
    end_credit = models.DateField(default=datetime.now)
    serie = models.CharField(max_length=50, null=True, blank=True, verbose_name='Serie de Facturación')
    subtotal = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total_dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    igv = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total_igv = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    cash = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    initial = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    change = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    card_number = models.CharField(max_length=30, null=True, blank=True)
    titular = models.CharField(max_length=30, null=True, blank=True)
    amount_debited = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    operation_number = models.CharField(max_length=50, null=True, blank=True, verbose_name='Nro de Operación (Yape/Plin)')
    operation_date = models.DateField(default=date.today, null=True, blank=True, verbose_name='Fecha de Operación')
    payment_bank = models.ForeignKey('PaymentBank', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Banco de Depósito/Transferencia')
    comment = models.TextField(max_length=600, null=True, blank=True, verbose_name='Comentario')

    def __str__(self):
        return f'{self.client.user.full_name} / {self.nro()}'

    def nro(self):
        return format(self.id, '06d')

    def get_client(self):
        if self.client:
            return self.client.toJSON()
        return {}

    def card_number_format(self):
        if self.card_number:
            cardnumber = self.card_number.split(' ')
            convert = re.sub('[0-9]', 'X', ' '.join(cardnumber[1:]))
            return '{} {}'.format(cardnumber[0], convert)
        return self.card_number

    def toJSON(self):
        item = model_to_dict(self, exclude=[''])
        item['nro'] = format(self.id, '06d')
        item['card_number'] = self.card_number_format()
        try:
            item['date_joined'] = self.date_joined.strftime('%d/%m/%Y %H:%M')
        except:
            item['date_joined'] = ''
        item['end_credit'] = self.end_credit.strftime('%Y-%m-%d')
        item['employee'] = {} if self.employee is None else self.employee.toJSON()
        item['client'] = {} if self.client is None else self.client.toJSON()
        item['payment_condition'] = {'id': self.payment_condition, 'name': self.get_payment_condition_display()}
        item['payment_method'] = {'id': self.payment_method, 'name': self.get_payment_method_display()}
        item['payment_bank'] = {} if self.payment_bank is None else self.payment_bank.toJSON()
        item['type_voucher'] = {'id': self.type_voucher, 'name': self.get_type_voucher_display()}
        item['subtotal'] = format(self.subtotal, '.2f')
        item['dscto'] = format(self.dscto, '.2f')
        item['total_dscto'] = format(self.total_dscto, '.2f')
        item['igv'] = format(self.igv, '.2f')
        item['total_igv'] = format(self.total_igv, '.2f')
        item['total'] = format(self.total, '.2f')
        item['cash'] = format(self.cash, '.2f')
        item['initial'] = format(self.initial, '.2f')
        item['change'] = format(self.change, '.2f')
        item['amount_debited'] = format(self.amount_debited, '.2f')
        # Obtener la cantidad total de productos vendidos en esta venta
        total_productos_vendidos = self.saledetail_set.aggregate(total_cant=Sum('cant'))['total_cant'] or 0
        item['cantidad_productos'] = total_productos_vendidos
        item['sale_details'] = [detail.toJSON() for detail in self.saledetail_set.all()]
        return item

    def calculate_invoice(self):
        subtotal = 0.00
        for d in self.saledetail_set.filter():
            d.subtotal = float(d.price) * int(d.cant)
            d.total_dscto = float(d.dscto)
            d.total = d.subtotal - d.total_dscto
            d.save()
            print(d.total_dscto)
            subtotal += d.total
        self.subtotal = subtotal
        self.total_igv = self.subtotal * float(self.igv)
        self.total_dscto = self.subtotal * float(self.dscto)
        # Solo calcular el total si no fue establecido manualmente (valor por defecto es 0.00)
        # Si el usuario ya ingresó un total diferente, no lo sobrescribir
        if self.total == 0.00:
            self.total = float(self.subtotal) - float(self.total_dscto)
        self.save()

    def calculate_serie(self):
        """
        Calcula automáticamente el número de serie de la venta basado en:
        - La serie asignada al empleado (usuario) que realiza la venta
        - El contador secuencial de ventas para esa serie
        Formato: {NombreSerie}-{número_4_dígitos}
        Ejemplo: PH-500-0001
        """
        if self.employee:
            try:
                user_series = UserSeries.objects.get(user=self.employee)
                series_name = user_series.series.name
                
                # Contar cuántas ventas previas tiene este usuario con esta serie
                # Usamos pk__lt para contar solo ventas guardadas anteriormente
                sales_count = Sale.objects.filter(
                    employee=self.employee,
                    serie__startswith=f'{series_name}-'
                ).count()
                
                # El siguiente número secuencial
                next_number = sales_count + 1
                self.serie = f'{series_name}-{next_number:04d}'
            except UserSeries.DoesNotExist:
                # Si el usuario no tiene serie asignada, dejamos el campo vacío
                self.serie = None
        else:
            self.serie = None

    def save(self, *args, **kwargs):
        """Sobrescribir save para calcular la serie automáticamente"""
        if not self.serie:
            self.calculate_serie()
        super(Sale, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        try:
            for i in self.saledetail_set.filter(product__categoryventoried=True):
                i.product.stock += i.cant
                i.product.save()
                i.delete()
        except:
            pass
        super(Sale, self).delete()

    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        default_permissions = ()
        permissions = (
            ('view_sale', 'Can view Ventas'),
            ('add_sale', 'Can add Ventas'),
            ('delete_sale', 'Can delete Ventas'),
        )
        ordering = ['-id']


class SaleDetail(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    hours_sale = models.TimeField(default='00:00:00', verbose_name='Hora de venta')
    cant = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    subtotal = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total_dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __str__(self):
        return self.product.name

    def toJSON(self):
        return {
            'id': self.id,
            'product': self.product.toJSON(),
            'hours_sale': self.hours_sale.strftime('%H:%M:%S'),
            'cant': self.cant,
            'price': format(self.price, '.2f'),
            'subtotal': format(self.subtotal, '.2f'),
            'dscto': format(self.dscto, '.2f'),
            'total_dscto': format(self.total_dscto, '.2f'),
            'total': format(self.total, '.2f'),
        }

    class Meta:
        verbose_name = 'Detalle de Cobranza'
        verbose_name_plural = 'Detalle de Cobranzas'
        default_permissions = ()
        ordering = ['-id']


class CtasCollect(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, help_text="Usuario que realizó el cobro")
    date_joined = models.DateField(default=datetime.now)
    end_date = models.DateField(default=datetime.now)
    debt = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    saldo = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    state = models.BooleanField(default=True)

    def __str__(self):
        return '{} / {} / S/.{}'.format(self.sale.client.user.full_name, self.date_joined.strftime('%Y-%m-%d'),
                                      format(self.debt, '.2f'))

    def is_overdue(self):
        """Verifica si la deuda está vencida (hoy o después)"""
        from datetime import date
        return date.today() >= self.end_date

    def days_overdue(self):
        """Retorna cuántos días está vencida la deuda"""
        if self.is_overdue():
            from datetime import date
            return (date.today() - self.end_date).days
        return 0

    def validate_debt(self):
        try:
            saldo = self.paymentsctacollect_set.aggregate(
                resp=Coalesce(Sum('valor'), 0.00, output_field=FloatField())).get('resp')
            self.saldo = float(self.debt) - float(saldo)
            self.state = self.saldo > 0.00
            self.save()
        except:
            pass

    def toJSON(self):
        item = model_to_dict(self, exclude=['user', 'sale'])
        item['sale'] = self.sale.toJSON()
        item['user'] = self.user.toJSON() if self.user else None
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['end_date'] = self.end_date.strftime('%Y-%m-%d')
        item['debt'] = format(self.debt, '.2f')
        item['saldo'] = format(self.saldo, '.2f')
        item['is_overdue'] = self.is_overdue()
        item['days_overdue'] = self.days_overdue()
        return item

    class Meta:
        verbose_name = 'Cuenta por cobrar'
        verbose_name_plural = 'Cuentas por cobrar'
        default_permissions = ()
        permissions = (
            ('view_ctascollect', 'Can view Cuentas por cobrar'),
            ('add_ctascollect', 'Can add Cuentas por cobrar'),
            ('delete_ctascollect', 'Can delete Cuentas por cobrar'),
        )
        ordering = ['-id']


class PaymentsCtaCollect(models.Model):
    ctascollect = models.ForeignKey(CtasCollect, on_delete=models.CASCADE)
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de registro')
    desc = models.CharField(max_length=500, null=True, blank=True, verbose_name='Detalles')
    valor = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Valor')

    def __str__(self):
        return 'str'

    def toJSON(self):
        item = model_to_dict(self, exclude=['ctascollect'])
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['valor'] = format(self.valor, '.2f')
        return item

    class Meta:
        verbose_name = 'Pago Cuenta por cobrar'
        verbose_name_plural = 'Pagos Cuentas por cobrar'
        default_permissions = ()
        ordering = ['-id']


class DebtsPay(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.PROTECT)
    date_joined = models.DateField(default=datetime.now)
    end_date = models.DateField(default=datetime.now)
    debt = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    saldo = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    state = models.BooleanField(default=True)

    def __str__(self):
        return '{} / {} / S/.{}'.format(self.purchase.provider.name, self.date_joined.strftime('%Y-%m-%d'),
                                      format(self.debt, '.2f'))

    def validate_debt(self):
        try:
            saldo = self.paymentsdebtspay_set.aggregate(
                resp=Coalesce(Sum('valor'), 0.00, output_field=FloatField())).get('resp')
            self.saldo = float(self.debt) - float(saldo)
            self.state = self.saldo > 0.00
            self.save()
        except:
            pass

    def toJSON(self):
        item = model_to_dict(self)
        item['purchase'] = self.purchase.toJSON()
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['end_date'] = self.end_date.strftime('%Y-%m-%d')
        item['debt'] = format(self.debt, '.2f')
        item['saldo'] = format(self.saldo, '.2f')
        return item

    class Meta:
        verbose_name = 'Cuenta por pagar'
        verbose_name_plural = 'Cuentas por pagar'
        default_permissions = ()
        permissions = (
            ('view_debtspay', 'Can view Cuentas por pagar'),
            ('add_debtspay', 'Can add Cuentas por pagar'),
            ('delete_debtspay', 'Can delete Cuentas por pagar'),
        )
        ordering = ['-id']


class PaymentsDebtsPay(models.Model):
    debtspay = models.ForeignKey(DebtsPay, on_delete=models.CASCADE)
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de registro')
    desc = models.CharField(max_length=500, null=True, blank=True, verbose_name='Detalles')
    valor = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Valor')

    def __str__(self):
        return self.debtspay.id

    def toJSON(self):
        item = model_to_dict(self, exclude=['debtspay'])
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['valor'] = format(self.valor, '.2f')
        return item

    class Meta:
        verbose_name = 'Det. Cuenta por pagar'
        verbose_name_plural = 'Det. Cuentas por pagar'
        default_permissions = ()
        ordering = ['-id']


class TypeExpense(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Nombre')

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Tipo de Gasto'
        verbose_name_plural = 'Tipos de Gastos'
        ordering = ['id']


class Expenses(models.Model):
    typeexpense = models.ForeignKey(TypeExpense, verbose_name='Tipo de Gasto', on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Usuario que registró el gasto')
    desc = models.CharField(max_length=500, null=True, blank=True, verbose_name='Descripción')
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de Registro')
    expense_date = models.DateField(null=True, blank=True, verbose_name='Fecha del Gasto')
    valor = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Valor')

    def __str__(self):
        return self.desc

    def get_desc(self):
        if self.desc:
            return self.desc
        return 'Sin detalles'

    def toJSON(self):
        item = model_to_dict(self, exclude=['user'])
        item['typeexpense'] = self.typeexpense.toJSON()
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['expense_date'] = self.expense_date.strftime('%Y-%m-%d') if self.expense_date else None
        item['valor'] = format(self.valor, '.2f')
        item['desc'] = self.get_desc()
        item['user'] = self.user.toJSON() if self.user else None
        return item

    class Meta:
        verbose_name = 'Gasto'
        verbose_name_plural = 'Gastos'
        ordering = ['id']


class Promotions(models.Model):
    start_date = models.DateField(default=datetime.now)
    end_date = models.DateField(default=datetime.now)
    state = models.BooleanField(default=True)

    def __str__(self):
        return str(self.id)

    def toJSON(self):
        item = model_to_dict(self)
        item['start_date'] = self.start_date.strftime('%Y-%m-%d')
        item['end_date'] = self.end_date.strftime('%Y-%m-%d')
        return item

    class Meta:
        verbose_name = 'Promoción'
        verbose_name_plural = 'Promociones'
        ordering = ['-id']


class PromotionsDetail(models.Model):
    promotion = models.ForeignKey(Promotions, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price_current = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total_dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    price_final = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __str__(self):
        return self.product.name

    def get_dscto_real(self):
        total_dscto = float(self.price_current) * float(self.dscto)
        n = 2
        return math.floor(total_dscto * 10 ** n) / 10 ** n

    def toJSON(self):
        item = model_to_dict(self, exclude=['promotion'])
        item['product'] = self.product.toJSON()
        item['price_current'] = format(self.price_current, '.2f')
        item['dscto'] = format(self.dscto, '.2f')
        item['total_dscto'] = format(self.total_dscto, '.2f')
        item['price_final'] = format(self.price_final, '.2f')
        return item

    class Meta:
        verbose_name = 'Detalle Promoción'
        verbose_name_plural = 'Detalle de Promociones'
        ordering = ['-id']


class Devolution(models.Model):
    saledetail = models.ForeignKey(SaleDetail, on_delete=models.PROTECT)
    date_joined = models.DateField(default=datetime.now)
    cant = models.IntegerField(default=0)
    motive = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.motive

    def toJSON(self):
        item = model_to_dict(self)
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['saledetail'] = self.saledetail.toJSON()
        item['motive'] = 'Sin detalles' if len(self.motive) == 0 else self.motive
        return item

    class Meta:
        verbose_name = 'Devolución'
        verbose_name_plural = 'Devoluciones'
        default_permissions = ()
        permissions = (
            ('view_devolution', 'Can view Devoluciones'),
            ('add_devolution', 'Can add Devoluciones'),
            ('delete_devolution', 'Can delete Devoluciones'),
        )
        ordering = ['-id']


class Box(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Usuario', related_name='boxes', null=True, blank=True)
    date_joined = models.DateField(default=timezone.now) 
    date_close = models.DateField(verbose_name='Fecha de Cierre')
    hours_close = models.TimeField(default=current_time, verbose_name='Hora de Cierre')
    efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Efectivo')
    yape = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Yape')
    plin = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Plin')
    transferencia = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Transferencia')
    deposito = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Depósito')
    initial_box = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Caja inicial')
    bills = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Gastos del Día', null=True, blank=True)
    box_final = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Caja final total')
    desc = models.TextField(blank=True, null=True,verbose_name='Descripción')

    def __str__(self):
        return self.date_close.strftime('%Y-%m-%d')

    def get_efectivo(self):
        fecha_actual = date.today()
        total_efectivo = Sale.objects.filter(
            employee=self.user,
            payment_condition='contado',
            payment_method='efectivo',
            date_joined__date=fecha_actual
        ).aggregate(total=Sum('total'))['total'] or 0
        
        payments = PaymentsCtaCollect.objects.filter(date_joined__date=fecha_actual)
        total_payments = sum(p.valor for p in payments if p.ctascollect.sale.employee == self.user and p.ctascollect.sale.payment_method == 'efectivo')
        
        return float(total_efectivo) + float(total_payments)

    def get_yape(self):
        fecha_actual = date.today()
        total_yape = Sale.objects.filter(
            employee=self.user,
            payment_condition='contado',
            payment_method='yape',
            date_joined__date=fecha_actual
        ).aggregate(total=Sum('total'))['total'] or 0
        
        payments = PaymentsCtaCollect.objects.filter(date_joined__date=fecha_actual)
        total_payments = sum(p.valor for p in payments if p.ctascollect.sale.employee == self.user and p.ctascollect.sale.payment_method == 'yape')
        
        return float(total_yape) + float(total_payments)

    def get_plin(self):
        fecha_actual = date.today()
        total_plin = Sale.objects.filter(
            employee=self.user,
            payment_condition='contado',
            payment_method='plin',
            date_joined__date=fecha_actual
        ).aggregate(total=Sum('total'))['total'] or 0
        
        payments = PaymentsCtaCollect.objects.filter(date_joined__date=fecha_actual)
        total_payments = sum(p.valor for p in payments if p.ctascollect.sale.employee == self.user and p.ctascollect.sale.payment_method == 'plin')
        
        return float(total_plin) + float(total_payments)

    def get_transferencia(self):
        fecha_actual = date.today()
        total_transfer = Sale.objects.filter(
            employee=self.user,
            payment_condition='contado',
            payment_method='tarjeta_debito_credito',
            date_joined__date=fecha_actual
        ).aggregate(total=Sum('total'))['total'] or 0
        
        payments = PaymentsCtaCollect.objects.filter(date_joined__date=fecha_actual)
        total_payments = sum(p.valor for p in payments if p.ctascollect.sale.employee == self.user and p.ctascollect.sale.payment_method == 'tarjeta_debito_credito')
        
        return float(total_transfer) + float(total_payments)

    def get_deposito(self):
        fecha_actual = date.today()
        total_deposito = Sale.objects.filter(
            employee=self.user,
            payment_condition='contado',
            payment_method='efectivo_tarjeta',
            date_joined__date=fecha_actual
        ).aggregate(total=Sum('total'))['total'] or 0
        
        payments = PaymentsCtaCollect.objects.filter(date_joined__date=fecha_actual)
        total_payments = sum(p.valor for p in payments if p.ctascollect.sale.employee == self.user and p.ctascollect.sale.payment_method == 'efectivo_tarjeta')
        
        return float(total_deposito) + float(total_payments)

    
    def toJSON(self):
        item = model_to_dict(self)
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['date_close'] = self.date_close.strftime('%Y-%m-%d')
        item['hours_close'] = self.hours_close.strftime('%H:%M')
        item['efectivo'] = format(self.efectivo, '.2f')
        item['yape'] = format(self.yape, '.2f')
        item['plin'] = format(self.plin, '.2f')
        item['transferencia'] = format(self.transferencia, '.2f')
        item['deposito'] = format(self.deposito, '.2f')
        item['initial_box'] = format(self.initial_box, '.2f')
        item['box_final'] = format(self.box_final, '.2f')
        return item

    class Meta:
        verbose_name = 'Caja chica'
        verbose_name_plural = 'Caja chica'
        ordering = ['-id']
