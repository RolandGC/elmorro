"""
Script para limpiar todos los registros de gastos de la base de datos.
Borra todos los registros del modelo Expenses.
"""

from config.wsgi import *
from core.pos.models import Expenses

print("=" * 80)
print("LIMPIEZA DE REGISTROS DE GASTOS")
print("=" * 80)

# Contar registros antes de borrar
try:
    initial_count = Expenses.objects.count()
    print(f"\nRegistros a eliminar: {initial_count}")
except Exception as e:
    print(f"Error contando registros: {str(e)}")
    initial_count = 0

# Borrar todos los gastos
print("\nEliminando gastos (Expenses)...")
try:
    expenses_count = Expenses.objects.count()
    Expenses.objects.all().delete()
    print(f"✓ Eliminados {expenses_count} registros de gastos")
except Exception as e:
    print(f"✗ Error eliminando gastos: {str(e)}")

# Resumen final
print("\n" + "=" * 80)
print("RESUMEN FINAL:")
print("=" * 80)
remaining = Expenses.objects.count()
print(f"Expenses: {remaining} registros")
print("=" * 80)
if remaining == 0:
    print("✓ LIMPIEZA COMPLETADA - Todos los gastos fueron eliminados\n")
else:
    print(f"⚠ Quedan {remaining} registros\n")
