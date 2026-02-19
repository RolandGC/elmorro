#!/usr/bin/env python
import os
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.user.models import User as CustomUser
from core.pos.models import Expenses, TypeExpense

# Crear cliente de prueba
client = Client()

# Obtener o crear un usuario
try:
    user = CustomUser.objects.filter(email='test@test.com').first()
    if not user:
        user = CustomUser.objects.create(
            email='test@test.com',
            full_name='Test User',
            dni='12345678'
        )
        user.set_password('test123')
        user.save()
    print(f"✓ Usuario: {user.full_name} (ID: {user.id})")
except Exception as e:
    print(f"✗ Error creando usuario: {e}")

# Crear algunos gastos de prueba para hoy
try:
    type_exp = TypeExpense.objects.first()
    if not type_exp:
        type_exp = TypeExpense.objects.create(name='Test Expense')
    
    # Limpiar gastos previos de hoy
    Expenses.objects.filter(user=user, date_joined=date.today()).delete()
    
    # Crear nuevos gastos de prueba
    for i in range(3):
        exp = Expenses.objects.create(
            typeexpense=type_exp,
            user=user,
            desc=f'Gasto de prueba {i+1}',
            date_joined=date.today(),
            valor=50.00 + i * 10
        )
    print(f"✓ Gastos de prueba creados")
    
    # Verificar gastos
    total_gastos = Expenses.objects.filter(user=user, date_joined=date.today()).count()
    suma_gastos = sum(e.valor for e in Expenses.objects.filter(user=user, date_joined=date.today()))
    print(f"  - Total gastos de hoy: {total_gastos}")
    print(f"  - Suma total: S/. {suma_gastos}")
    
except Exception as e:
    print(f"✗ Error creando gastos: {e}")
    import traceback
    traceback.print_exc()

# Intentar hacer login
try:
    logged_in = client.login(email='test@test.com', password='test123')
    if not logged_in:
        print("✗ No se pudo hacer login con email/password")
        # Intentar alternativa
        django_user = CustomUser.objects.get(email='test@test.com')
        client.force_login(django_user)
        print("✓ Force login realizado")
    else:
        print("✓ Login exitoso")
except Exception as e:
    print(f"✗ Error en login: {e}")
    import traceback
    traceback.print_exc()

# Hacer POST a box_create con action=get_initial_values
try:
    response = client.post('/pos/frm/box/create/', {
        'action': 'get_initial_values',
    })
    print(f"\n✓ POST a /pos/frm/box/create/")
    print(f"  - Status Code: {response.status_code}")
    print(f"  - Content-Type: {response.get('Content-Type')}")
    print(f"  - Response: {response.content.decode()}")
    
except Exception as e:
    print(f"✗ Error en POST: {e}")
    import traceback
    traceback.print_exc()
