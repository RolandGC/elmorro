# Resumen de Cambios para Sistema Multisucursal

## 1. Nuevos Modelos a Crear en `core/pos/models.py`

### 1.1 Modelo `Branch` (Sucursal)

```python
class Branch(models.Model):
    WAREHOUSE = 'warehouse'
    BRANCH = 'branch'
    TYPE_CHOICES = [
        (WAREHOUSE, 'Almacén Central'),
        (BRANCH, 'Sucursal'),
    ]

    code = models.CharField(max_length=20, unique=True)  # BR001, BR002
    name = models.CharField(max_length=150)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=BRANCH)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'branch'
        verbose_name = 'Sucursal'
        verbose_name_plural = 'Sucursales'
        ordering = ('code',)

    def __str__(self):
        return f'{self.code} - {self.name}'

    def get_total_inventory_value(self):
        total = 0
        for stock in self.stock_set.all():
            total += stock.quantity * stock.product.pvp
        return total

    def get_low_stock_items(self):
        return self.stock_set.filter(quantity__lte=models.F('min_quantity'))

    def to_json(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'type': self.type,
            'address': self.address,
            'is_active': self.is_active,
        }
```

### 1.2 Modelo `Stock` (Inventario por Sucursal)

```python
class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reserved = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Cantidad reservada para ventas
    damaged = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Dañado/Merma
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stock'
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventarios'
        unique_together = ('product', 'branch')

    def __str__(self):
        return f'{self.product.name} - {self.branch.name}: {self.quantity}'

    @property
    def available(self):
        return self.quantity - self.reserved - self.damaged

    def is_low_stock(self):
        return self.available <= self.min_quantity

    def is_overstocked(self):
        return self.quantity >= self.max_quantity

    def get_stock_value(self):
        return self.available * self.product.pvp

    def to_json(self):
        return {
            'id': self.id,
            'product': self.product.name,
            'branch': self.branch.name,
            'quantity': float(self.quantity),
            'available': float(self.available),
            'reserved': float(self.reserved),
            'damaged': float(self.damaged),
        }
```

### 1.3 Modelo `StockMovement` (Auditoría de Movimientos)

```python
class StockMovement(models.Model):
    PURCHASE = 'compra'
    SALE = 'venta'
    TRANSFER_OUT = 'transfer_out'
    TRANSFER_IN = 'transfer_in'
    ADJUSTMENT = 'ajuste'
    DEVOLUTION = 'devolucion'
    DAMAGE = 'dano'
    COUNT = 'recuento'

    MOVEMENT_CHOICES = [
        (PURCHASE, 'Compra'),
        (SALE, 'Venta'),
        (TRANSFER_OUT, 'Transferencia Salida'),
        (TRANSFER_IN, 'Transferencia Entrada'),
        (ADJUSTMENT, 'Ajuste'),
        (DEVOLUTION, 'Devolución'),
        (DAMAGE, 'Daño/Merma'),
        (COUNT, 'Recuento'),
    ]

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    before_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    after_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    related_doc_type = models.CharField(max_length=30, blank=True)  # 'sale', 'purchase', 'transfer'
    related_doc_id = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reason = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stock_movement'
        verbose_name = 'Movimiento de Stock'
        verbose_name_plural = 'Movimientos de Stock'
        ordering = ('-date_created',)
        indexes = [
            models.Index(fields=['stock', 'date_created']),
            models.Index(fields=['movement_type', 'date_created']),
        ]

    def __str__(self):
        return f'{self.get_movement_type_display()} - {self.stock.product.name}'

    def to_json(self):
        return {
            'id': self.id,
            'movement_type': self.movement_type,
            'quantity': float(self.quantity),
            'date_created': self.date_created.strftime('%Y-%m-%d %H:%M:%S'),
            'user': self.user.username if self.user else 'Sistema',
        }
```

### 1.4 Modelo `Transfer` (Transferencia entre Sucursales)

```python
class Transfer(models.Model):
    DRAFT = 'draft'
    PENDING = 'pending'
    IN_TRANSIT = 'in_transit'
    RECEIVED = 'received'
    CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (DRAFT, 'Borrador'),
        (PENDING, 'Pendiente'),
        (IN_TRANSIT, 'En Tránsito'),
        (RECEIVED, 'Recibido'),
        (CANCELLED, 'Cancelado'),
    ]

    code = models.CharField(max_length=20, unique=True)  # TR001, TR002
    origin_branch = models.ForeignKey(Branch, related_name='transfers_sent', on_delete=models.CASCADE)
    destination_branch = models.ForeignKey(Branch, related_name='transfers_received', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    date_created = models.DateTimeField(auto_now_add=True)
    date_sent = models.DateTimeField(null=True, blank=True)
    date_received = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, related_name='transfers_created', on_delete=models.SET_NULL, null=True)
    received_by = models.ForeignKey(User, related_name='transfers_received_by', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'transfer'
        verbose_name = 'Transferencia'
        verbose_name_plural = 'Transferencias'
        ordering = ('-date_created',)

    def __str__(self):
        return f'{self.code} - {self.origin_branch.name} → {self.destination_branch.name}'

    def get_total_items(self):
        return self.transferdetail_set.aggregate(total=models.Sum('quantity_sent'))['total'] or 0

    def get_total_value(self):
        total = 0
        for detail in self.transferdetail_set.all():
            total += detail.quantity_sent * detail.unit_cost
        return total

    def can_be_sent(self):
        return self.status == self.PENDING

    def send_transfer(self, user):
        if self.can_be_sent():
            self.status = self.IN_TRANSIT
            self.date_sent = timezone.now()
            self.created_by = user
            self.save()
            return True
        return False

    def receive_transfer(self, user):
        if self.status == self.IN_TRANSIT:
            self.status = self.RECEIVED
            self.date_received = timezone.now()
            self.received_by = user

            # Actualizar stock en sucursal destino
            for detail in self.transferdetail_set.all():
                try:
                    stock = Stock.objects.get(product=detail.product, branch=self.destination_branch)
                    stock.quantity += detail.quantity_sent
                    stock.save()

                    # Registrar movimiento
                    StockMovement.objects.create(
                        stock=stock,
                        movement_type=StockMovement.TRANSFER_IN,
                        quantity=detail.quantity_sent,
                        before_quantity=stock.quantity - detail.quantity_sent,
                        after_quantity=stock.quantity,
                        related_doc_type='transfer',
                        related_doc_id=self.id,
                        user=user,
                        reason=f'Recepción de transferencia {self.code}'
                    )
                except Stock.DoesNotExist:
                    Stock.objects.create(
                        product=detail.product,
                        branch=self.destination_branch,
                        quantity=detail.quantity_sent
                    )

            self.save()
            return True
        return False

    def to_json(self):
        return {
            'id': self.id,
            'code': self.code,
            'origin': self.origin_branch.name,
            'destination': self.destination_branch.name,
            'status': self.get_status_display(),
            'total_items': self.get_total_items(),
            'total_value': float(self.get_total_value()),
            'date_created': self.date_created.strftime('%Y-%m-%d %H:%M:%S'),
        }
```

### 1.5 Modelo `TransferDetail` (Detalle de Transferencia)

```python
class TransferDetail(models.Model):
    transfer = models.ForeignKey(Transfer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_sent = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'transfer_detail'
        verbose_name = 'Detalle de Transferencia'
        verbose_name_plural = 'Detalles de Transferencia'

    def __str__(self):
        return f'{self.transfer.code} - {self.product.name}'

    @property
    def total_cost(self):
        return self.quantity_sent * self.unit_cost

    def to_json(self):
        return {
            'id': self.id,
            'product': self.product.name,
            'quantity_sent': float(self.quantity_sent),
            'quantity_received': float(self.quantity_received),
            'unit_cost': float(self.unit_cost),
            'total_cost': float(self.total_cost),
        }
```

---

## 2. Modificaciones a Modelos Existentes

### 2.1 Modelo `Product`

**Cambios:**

- Remover campo `stock` (será reemplazado por tabla `Stock`)
- Remover campo `inventoried` (pasará a `Stock`)
- Agregar método para obtener stock total

```python
# REMOVER:
# stock = models.IntegerField(default=0)
# inventoried = models.BooleanField(default=True)

# AGREGAR:
def get_total_stock(self):
    """Obtiene el stock total disponible en todas las sucursales"""
    return self.stock_set.aggregate(total=models.Sum('available'))['total'] or 0

def get_stock_by_branch(self, branch):
    """Obtiene el stock disponible en una sucursal específica"""
    try:
        stock = Stock.objects.get(product=self, branch=branch)
        return stock.available
    except Stock.DoesNotExist:
        return 0

def get_branches(self):
    """Obtiene todas las sucursales donde hay stock del producto"""
    return self.stock_set.filter(quantity__gt=0).values_list('branch__name', flat=True)
```

### 2.2 Modelo `Purchase`

**Cambios:**

- Agregar campo `branch` para vincular compras a sucursal específica
- Modificar lógica de creación de stock

```python
# AGREGAR:
branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)

# MODIFICAR en save():
def save(self, *args, **kwargs):
    if not self.pk:
        # Asignar automáticamente a almacén central si no se especifica
        if not self.branch:
            self.branch = Branch.objects.filter(type=Branch.WAREHOUSE).first()
    super().save(*args, **kwargs)
```

### 2.3 Modelo `PurchaseDetail`

**Cambios:**

- Modificar save() para actualizar Stock en lugar de Product.stock

```python
# MODIFICAR save():
def save(self, *args, **kwargs):
    super().save(*args, **kwargs)

    # Obtener o crear Stock
    stock, created = Stock.objects.get_or_create(
        product=self.product,
        branch=self.purchase.branch,
        defaults={'quantity': 0}
    )

    # Actualizar cantidad
    stock.quantity = models.F('quantity') + self.cant
    stock.save()

    # Registrar movimiento
    StockMovement.objects.create(
        stock=stock,
        movement_type=StockMovement.PURCHASE,
        quantity=self.cant,
        before_quantity=stock.quantity - self.cant,
        after_quantity=stock.quantity,
        related_doc_type='purchase',
        related_doc_id=self.purchase.id,
        user=self.purchase.employee,
        reason=f'Compra {self.purchase.code}'
    )
```

### 2.4 Modelo `Sale`

**Cambios:**

- Agregar campo `branch` para registrar en qué sucursal se realizó la venta
- Agregar validación de stock disponible

```python
# AGREGAR:
branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)

# MODIFICAR save():
def save(self, *args, **kwargs):
    if not self.pk:
        if not self.branch:
            self.branch = Branch.objects.filter(type=Branch.WAREHOUSE).first()
    super().save(*args, **kwargs)
```

### 2.5 Modelo `SaleDetail`

**Cambios:**

- Modificar save() para actualizar Stock
- Agregar validación de disponibilidad

```python
# MODIFICAR save():
def save(self, *args, **kwargs):
    super().save(*args, **kwargs)

    # Obtener stock en la sucursal de venta
    stock = Stock.objects.get(
        product=self.product,
        branch=self.sale.branch
    )

    # Actualizar cantidad vendida
    stock.quantity -= self.cant
    stock.save()

    # Registrar movimiento
    StockMovement.objects.create(
        stock=stock,
        movement_type=StockMovement.SALE,
        quantity=self.cant,
        before_quantity=stock.quantity + self.cant,
        after_quantity=stock.quantity,
        related_doc_type='sale',
        related_doc_id=self.sale.id,
        user=self.sale.employee,
        reason=f'Venta {self.sale.code}'
    )
```

### 2.6 Modelo `User`

**Cambios:**

- Agregar campo para asignar sucursales accesibles
- Agregar método para obtener sucursales

```python
# AGREGAR:
branches = models.ManyToManyField(Branch, blank=True, verbose_name='Sucursales')

# AGREGAR MÉTODO:
def get_accessible_branches(self):
    """Obtiene las sucursales que el usuario puede acceder"""
    if self.is_superuser:
        return Branch.objects.all()
    return self.branches.all()

def has_branch_access(self, branch):
    """Verifica si el usuario tiene acceso a una sucursal"""
    if self.is_superuser:
        return True
    return self.branches.filter(pk=branch.id).exists()
```

---

## 3. Cambios en Vistas

### 3.1 Filtrado por Sucursal

Todas las vistas deben filtrar datos por sucursal del usuario:

```python
# En class-based views:
def get_queryset(self):
    qs = super().get_queryset()
    user = self.request.user

    if user.is_superuser:
        return qs

    # Filtrar por sucursales accesibles
    accessible_branches = user.get_accessible_branches()
    return qs.filter(branch__in=accessible_branches)

# En function-based views:
def get_branch_from_request(request):
    branch_id = request.GET.get('branch_id')

    if branch_id:
        branch = Branch.objects.get(id=branch_id)
        if request.user.has_branch_access(branch):
            return branch

    # Devolver primera sucursal accesible
    return request.user.get_accessible_branches().first()
```

### 3.2 Validación de Stock

Antes de crear ventas o transferencias:

```python
def validate_stock(product, branch, quantity):
    try:
        stock = Stock.objects.get(product=product, branch=branch)
        if stock.available < quantity:
            raise ValidationError(
                f'Stock insuficiente. Disponible: {stock.available}'
            )
        return True
    except Stock.DoesNotExist:
        raise ValidationError('Producto no disponible en esta sucursal')
```

---

## 4. Cambios en Plantillas

### 4.1 Selector de Sucursal

Agregar en base.html o header:

```html
{% if user.branches.all|length > 1 %}
<div class="branch-selector">
    <form method="GET" class="form-inline">
        <select name="branch_id" class="form-control" onchange="this.form.submit()">
            {% for branch in user.get_accessible_branches %}
                <option value="{{ branch.id }}" {% if branch == current_branch %}selected{% endif %}>
                    {{ branch.name }}
                </option>
            {% endfor %}
        </select>
    </form>
</div>
{% endif %}
```

### 4.2 Validación de Stock en Formularios

En plantillas de ventas:

```html
<script>
  function validateStock() {
    const productId = document.getElementById("product_id").value;
    const quantity = document.getElementById("quantity").value;
    const branchId = document.getElementById("branch_id").value;

    fetch(
      `/api/validate-stock/?product_id=${productId}&branch_id=${branchId}&qty=${quantity}`
    )
      .then((r) => r.json())
      .then((data) => {
        if (!data.valid) {
          alert("Stock insuficiente: " + data.message);
        }
      });
  }
</script>
```

---

## 5. Migraciones de Base de Datos

### 5.1 Crear Migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5.2 Datos Iniciales - Data Migration

```python
# core/pos/migrations/0XXX_create_initial_data.py
from django.db import migrations

def create_branches(apps, schema_editor):
    Branch = apps.get_model('pos', 'Branch')

    # Crear almacén central
    Branch.objects.create(
        code='ALM001',
        name='Almacén Central',
        type='warehouse',
        address='Dirección Central',
        is_active=True
    )

class Migration(migrations.Migration):
    dependencies = [
        ('pos', 'XXXX_add_branches'),
    ]
    operations = [
        migrations.RunPython(create_branches),
    ]
```

### 5.3 Migración de Datos Existentes

```python
# Crear data migration
python manage.py makemigrations --empty pos --name migrate_product_stock_to_branch_stock

# Contenido:
def migrate_stock(apps, schema_editor):
    Product = apps.get_model('pos', 'Product')
    Stock = apps.get_model('pos', 'Stock')
    Branch = apps.get_model('pos', 'Branch')

    # Obtener almacén central
    warehouse = Branch.objects.filter(type='warehouse').first()

    if warehouse:
        for product in Product.objects.all():
            if product.stock > 0:
                Stock.objects.create(
                    product=product,
                    branch=warehouse,
                    quantity=product.stock,
                    min_quantity=0,
                    max_quantity=product.stock * 2
                )

def reverse_stock(apps, schema_editor):
    Stock = apps.get_model('pos', 'Stock')
    Stock.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('pos', 'previous_migration'),
    ]
    operations = [
        migrations.RunPython(migrate_stock, reverse_stock),
    ]
```

---

## 6. Permisos y Seguridad

### 6.1 Nuevos Permisos a Crear

```python
# En tests.py o comando personalizado
Permission.objects.create(
    codename='view_transfers',
    name='Puede ver transferencias',
    content_type=ContentType.objects.get_for_model(Transfer)
)
Permission.objects.create(
    codename='create_transfer',
    name='Puede crear transferencias',
    content_type=ContentType.objects.get_for_model(Transfer)
)
Permission.objects.create(
    codename='receive_transfer',
    name='Puede recibir transferencias',
    content_type=ContentType.objects.get_for_model(Transfer)
)
```

### 6.2 Decoradores de Validación

```python
from django.core.exceptions import PermissionDenied

def branch_access_required(view_func):
    def wrapper(request, *args, **kwargs):
        branch_id = kwargs.get('branch_id')
        if branch_id:
            branch = Branch.objects.get(id=branch_id)
            if not request.user.has_branch_access(branch):
                raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper
```

---

## 7. Reportes Consolidados

### 7.1 Reporte de Inventario por Sucursal

```python
def inventory_by_branch_report(branch=None):
    if branch:
        stocks = Stock.objects.filter(branch=branch).select_related('product')
    else:
        stocks = Stock.objects.all().select_related('product', 'branch')

    report_data = {}
    for stock in stocks:
        branch_name = stock.branch.name
        if branch_name not in report_data:
            report_data[branch_name] = []

        report_data[branch_name].append({
            'product': stock.product.name,
            'quantity': stock.quantity,
            'available': stock.available,
            'value': stock.get_stock_value(),
        })

    return report_data
```

### 7.2 Reporte de Transferencias

```python
def transfer_report(start_date, end_date, branch=None):
    transfers = Transfer.objects.filter(
        date_created__range=[start_date, end_date]
    )

    if branch:
        transfers = transfers.filter(
            models.Q(origin_branch=branch) | models.Q(destination_branch=branch)
        )

    return {
        'total_transfers': transfers.count(),
        'total_value': sum(t.get_total_value() for t in transfers),
        'by_status': transfers.values('status').annotate(count=Count('id')),
        'transfers': [t.to_json() for t in transfers]
    }
```

---

## 8. Checklist de Implementación

- [ ] Crear modelos: Branch, Stock, StockMovement, Transfer, TransferDetail
- [ ] Ejecutar migraciones iniciales
- [ ] Agregar datos iniciales (almacén central)
- [ ] Modificar Product: remover stock, agregar métodos
- [ ] Modificar Purchase/PurchaseDetail: agregar branch, actualizar Stock
- [ ] Modificar Sale/SaleDetail: agregar branch, actualizar Stock
- [ ] Modificar User: agregar ManyToMany a Branch
- [ ] Actualizar todas las vistas con filtros de sucursal
- [ ] Crear data migration para migrar stock existente
- [ ] Agregar nuevos permisos en sistema de seguridad
- [ ] Crear nuevos niveles de usuario (Admin General, Admin Sucursal, etc.)
- [ ] Crear reportes consolidados
- [ ] Pruebas unitarias de Stock y Transfer
- [ ] Pruebas de integración
- [ ] Documentación de API
- [ ] Capacitación de usuarios

---

## 9. Consideraciones Importantes

### Performance

- Agregar índices en campos frecuentemente consultados
- Usar `select_related()` y `prefetch_related()` en queries
- Considerar caché para reportes consolidados

### Rollback

- Mantener backups antes de data migration
- Crear scripts de reversión para emergencias
- Documentar estado previo de datos

### Testing

- Tests unitarios para cada modelo nuevo
- Tests de integración para flujos de transferencia
- Tests de permisos para cada rol

### Seguridad

- Validar acceso a sucursal en cada operación
- Auditar movimientos de stock
- Encriptar datos sensibles de ubicación

---

**Estimado de Esfuerzo:** 8-10 semanas

- Desarrollo e implementación: 5-6 semanas
- Pruebas: 2 semanas
- Capacitación y deployment: 1-2 semanas
