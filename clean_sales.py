"""
Script para limpiar todos los registros de ventas de la base de datos.
Borra en orden:
1. PaymentsCtaCollect (pagos de cuentas por cobrar)
2. CtasCollect (cuentas por cobrar)
3. SaleDetail (detalles de venta - se borran automáticamente con Cascade)
4. Sale (ventas)
"""

from config.wsgi import *
from core.pos.models import Sale, SaleDetail, CtasCollect
from django.db.models import Count

print("=" * 80)
print("LIMPIEZA DE REGISTROS DE VENTAS")
print("=" * 80)

# 1. Borrar PaymentsCtaCollect (pagos de cuentas por cobrar)
print("\n1. Eliminando pagos de cuentas por cobrar (PaymentsCtaCollect)...")
try:
    from core.pos.models import PaymentsCtaCollect
    payments_count = PaymentsCtaCollect.objects.count()
    PaymentsCtaCollect.objects.all().delete()
    print(f"   ✓ Eliminados {payments_count} registros de pagos")
except Exception as e:
    print(f"   ✗ Error eliminando pagos: {str(e)}")

# 2. Borrar CtasCollect (cuentas por cobrar)
print("\n2. Eliminando cuentas por cobrar (CtasCollect)...")
try:
    ctas_count = CtasCollect.objects.count()
    CtasCollect.objects.all().delete()
    print(f"   ✓ Eliminadas {ctas_count} cuentas por cobrar")
except Exception as e:
    print(f"   ✗ Error eliminando cuentas: {str(e)}")

# 3. Borrar SaleDetail y Sale
# Nota: SaleDetail se borra automáticamente cuando se elimina Sale (CASCADE)
print("\n3. Eliminando details de ventas y ventas (SaleDetail y Sale)...")
try:
    # Contar SaleDetail antes de borrar
    saledetail_count = SaleDetail.objects.count()
    
    # Borrar todas las ventas (esto también borrará SaleDetail por CASCADE)
    sale_count = Sale.objects.count()
    Sale.objects.all().delete()
    
    print(f"   ✓ Eliminados {sale_count} registros de venta (Sale)")
    print(f"   ✓ Eliminados {saledetail_count} detalles de venta (SaleDetail)")
except Exception as e:
    print(f"   ✗ Error eliminando ventas: {str(e)}")

# Resumen final
print("\n" + "=" * 80)
print("RESUMEN FINAL:")
print("=" * 80)
try:
    from core.pos.models import PaymentsCtaCollect
    payments = PaymentsCtaCollect.objects.count()
except:
    payments = 0
ctas = CtasCollect.objects.count()
sales = Sale.objects.count()
details = SaleDetail.objects.count()

print(f"PaymentsCtaCollect: {payments} registros")
print(f"CtasCollect: {ctas} registros")
print(f"Sale: {sales} registros")
print(f"SaleDetail: {details} registros")
print("=" * 80)
print("✓ LIMPIEZA COMPLETADA\n")
