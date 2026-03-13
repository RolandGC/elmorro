from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import Group
from django.db.models import Sum
from datetime import datetime, date

from .models import *


class SeriesForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Series
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ingrese el nombre de la serie'}),
        }


class UserSeriesForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar usuarios excluyendo el grupo "Cliente"
        try:
            client_group = Group.objects.get(name='Cliente')
            self.fields['user'].queryset = User.objects.exclude(groups__in=[client_group]).distinct()
        except Group.DoesNotExist:
            self.fields['user'].queryset = User.objects.all()
        
        self.fields['user'].widget.attrs['autofocus'] = True

    class Meta:
        model = UserSeries
        fields = ('user', 'series')
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control select2'}),
            'series': forms.Select(attrs={'class': 'form-control select2'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        series = cleaned_data.get('series')
        
        if user and series:
            # Verificar que el usuario no tenga otra serie asignada
            if UserSeries.objects.exclude(pk=self.instance.pk).filter(user=user).exists():
                raise forms.ValidationError('Este usuario ya tiene una serie asignada.')
            # Verificar que la serie no esté asignada a otro usuario
            if UserSeries.objects.exclude(pk=self.instance.pk).filter(series=series).exists():
                raise forms.ValidationError('Esta serie ya está asignada a otro usuario.')
        
        return cleaned_data


class ExpenseSeriesForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = ExpenseSeries
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ingrese el nombre de la serie de gastos'}),
        }


class UserExpenseSeriesForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar usuarios excluyendo el grupo "Cliente"
        try:
            client_group = Group.objects.get(name='Cliente')
            self.fields['user'].queryset = User.objects.exclude(groups__in=[client_group]).distinct()
        except Group.DoesNotExist:
            self.fields['user'].queryset = User.objects.all()
        
        self.fields['user'].widget.attrs['autofocus'] = True

    class Meta:
        model = UserExpenseSeries
        fields = ('user', 'expense_series')
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control select2'}),
            'expense_series': forms.Select(attrs={'class': 'form-control select2'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        expense_series = cleaned_data.get('expense_series')
        
        if user and expense_series:
            # Verificar que el usuario no tenga otra serie de gastos asignada
            if UserExpenseSeries.objects.exclude(pk=self.instance.pk).filter(user=user).exists():
                raise forms.ValidationError('Este usuario ya tiene una serie de gastos asignada.')
            # Verificar que la serie no esté asignada a otro usuario
            if UserExpenseSeries.objects.exclude(pk=self.instance.pk).filter(expense_series=expense_series).exists():
                raise forms.ValidationError('Esta serie de gastos ya está asignada a otro usuario.')
        
        return cleaned_data


class ProviderForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Provider
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ingrese un nombre'}),
            'ruc': forms.TextInput(attrs={'placeholder': 'Ingrese un número de ruc'}),
            'mobile': forms.TextInput(attrs={'placeholder': 'Ingrese un teléfono celular'}),
            'address': forms.TextInput(attrs={'placeholder': 'Ingrese una dirección'}),
            'email': forms.TextInput(attrs={'placeholder': 'Ingrese un email'}),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                instace = super().save()
                data = instace.toJSON()
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class CategoryForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Category
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ingrese un nombre'}),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class ProductForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ingrese un nombre'}),
            'codebar': forms.TextInput(attrs={'placeholder': 'Ingrese código'}),
            #'unit': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'date_into': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control datetimepicker-input',
                'id': 'date_joined',
                'value': datetime.now().strftime('%Y-%m-%d'),
                'data-toggle': 'datetimepicker',
                'data-target': '#date_joined'
             }),
            'category': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'price': forms.TextInput(),
            'price_min_sale': forms.TextInput(),
            'pvp': forms.TextInput(),
        }
        exclude = ['stock']

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class PurchaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['provider'].queryset = Provider.objects.none()

    class Meta:
        model = Purchase
        fields = '__all__'
        widgets = {
            'provider': forms.Select(attrs={'class': 'custom-select select2'}),
            'payment_condition': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'date_joined': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control datetimepicker-input',
                'id': 'date_joined',
                'value': datetime.now().strftime('%Y-%m-%d'),
                'data-toggle': 'datetimepicker',
                'data-target': '#date_joined'
            }),
            'end_credit': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control datetimepicker-input',
                'id': 'end_credit',
                'value': datetime.now().strftime('%Y-%m-%d'),
                'data-toggle': 'datetimepicker',
                'data-target': '#end_credit'
            }),
            'subtotal': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off'
            }),
        }


class TypeExpenseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = TypeExpense
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ingrese un nombre'}),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class ExpensesForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['typeexpense'].widget.attrs['autofocus'] = True

    class Meta:
        model = Expenses
        fields = ['typeexpense', 'desc', 'valor']
        widgets = {
            'typeexpense': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'desc': forms.Textarea(attrs={'placeholder': 'Ingrese una descripción', 'rows': 3, 'cols': '3'}),
            'valor': forms.TextInput()
        }

    def save(self, commit=True):
        try:
            if self.is_valid():
                return super().save(commit=commit)
            else:
                raise ValueError(str(self.errors))
        except Exception as e:
            raise


class PaymentsDebtsPayForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['valor'].widget.attrs['autofocus'] = True
        self.fields['debtspay'].queryset = DebtsPay.objects.none()

    class Meta:
        model = PaymentsDebtsPay
        fields = '__all__'
        widgets = {
            'debtspay': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'date_joined': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control datetimepicker-input',
                'id': 'date_joined',
                'value': datetime.now().strftime('%Y-%m-%d'),
                'data-toggle': 'datetimepicker',
                'data-target': '#date_joined'
            }),
            'valor': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off',
            }),
            'desc': forms.Textarea(attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'rows': 3,
                'cols': 3,
                'placeholder': 'Ingrese una descripción'
            }),
        }

class BoxForm(ModelForm):


    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    class Meta:
        model = Box
        fields = ['datetime_close', 'desc']
        widgets = {
            'datetime_close': forms.DateTimeInput(format='%Y-%m-%d %H:%M', attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'value': datetime.now().strftime('%Y-%m-%dT%H:%M'),
                'required': 'required'
            }),
            'desc': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Notas adicionales sobre el cierre de caja'
            })
        }
    
    def save(self, commit=True, **kwargs):
        """Guardar el Box mapeando valores desde el POST request"""
        box = self.instance
        
        # Obtener el request desde kwargs para acceder al POST
        request = kwargs.get('request')
        
        if request:
            # Mapear los campos personalizados desde POST a los campos del modelo
            box.initial_box = float(request.POST.get('initial_box_soles', 0)) + float(request.POST.get('initial_box_dolares', 0))
            box.efectivo = float(request.POST.get('efectivo_soles', 0)) + float(request.POST.get('efectivo_dolares', 0))
            box.yape = float(request.POST.get('yape_soles', 0))
            box.plin = float(request.POST.get('plin_soles', 0))
            box.transferencia = float(request.POST.get('transferencia_soles', 0)) + float(request.POST.get('transferencia_dolares', 0))
            box.deposito = float(request.POST.get('deposito_soles', 0)) + float(request.POST.get('deposito_dolares', 0))
            box.bills = float(request.POST.get('bills_soles', 0))
            box.box_final = float(request.POST.get('box_final_soles', 0)) + float(request.POST.get('box_final_dolares', 0))
        
        if commit:
            box.save()
        return box

class BoxFormListView(forms.Form):
 date_range = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off'
    }))

class ClientForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Client
        fields = 'dni', 'email', 'mobile', 'address'
        widgets = {
            'mobile': forms.TextInput(
                attrs={
                    'placeholder': 'Ingrese su número celular',
                    'class': 'form-control',
                    'autocomplete': 'off'
                }
            ),
            'address': forms.TextInput(
                attrs={
                    'placeholder': 'Ingrese una dirección',
                    'class': 'form-control',
                    'autocomplete': 'off',
                }
            ),
        }
        exclude = ['user']

    full_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',
        'placeholder': 'Ingrese sus nombres completos'
    }), label='Nombre completo o Razón Social', max_length=50)

    dni = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',
        'placeholder': 'Ingrese su número Dni o Ruc'
    }), label='Número de Identidad', max_length=10)

    email = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',
        'placeholder': 'Ingrese su email'
    }), label='Email', max_length=50)

    image = forms.ImageField(widget=forms.FileInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off'
    }), label='Imagen')

# class CustomSelect(forms.Select):
#     def render(self, name, value, attrs=None, choices=()):
#         output = super().render(name, value, attrs, choices)
#         icon_mapping = {
#             'yape': 'fas fa-userst',
#             'plin': 'fas fa-users',
#         }
#         icon_class = icon_mapping.get(value, '')
#         if icon_class:
#             output += f'<i class="{icon_class}"></i>'  # Agrega el icono al final del campo de selección
#         return output
class SaleForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.none()
        # Hacer los campos total y amount opcionales
        self.fields['total'].required = False
        self.fields['amount'].required = False
        # self.initial['client'] = '2'

    class Meta:
        model = Sale
        fields = '__all__'
        widgets = {
            'client': forms.Select(attrs={'class': 'custom-select select2'}),
            'payment_condition': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'type_voucher': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'date_joined': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'id': 'date_joined',
                'value': datetime.now().strftime('%Y-%m-%dT%H:%M')
            }),
            'end_credit': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control datetimepicker-input',
                'id': 'end_credit',
                'value': datetime.now().strftime('%Y-%m-%d'),
                'data-toggle': 'datetimepicker',
                'data-target': '#end_credit'
            }),
            'subtotal': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'disabled': True
            }),
            'igv': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'disabled': True
            }),
            'total_igv': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'disabled': True
            }),
            'dscto': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'autocomplete': 'off'
            }),
            'total_dscto': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'disabled': True
            }),
            'total': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'autocomplete': 'off',
                'placeholder': 'Ingrese el monto total S/.',
            }),
            'cash': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'disabled': True
            }),
            'initial': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'id':'initial',
            }),
            'change': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'card_number': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'placeholder': 'Ingrese el número de la tarjeta'
            }),
            'titular': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'placeholder': 'Ingrese el nombre del titular'
            }),
            'amount_debited': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'readonly': True
            }),
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Escribe un comentario...'
            }),
        }

    amount = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',
        'disabled': True
    }))


class PaymentsCtaCollectForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['valor'].widget.attrs['autofocus'] = True
        self.fields['ctascollect'].queryset = PaymentsCtaCollect.objects.none()

    class Meta:
        model = PaymentsCtaCollect
        fields = '__all__'
        widgets = {
            'ctascollect': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'date_joined': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control datetimepicker-input',
                'id': 'date_joined',
                'value': datetime.now().strftime('%Y-%m-%d'),
                'data-toggle': 'datetimepicker',
                'data-target': '#date_joined'
            }),
            'valor': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off',
            }),
            'desc': forms.Textarea(attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'rows': 3,
                'cols': 3,
                'placeholder': 'Ingrese una descripción'
            }),
        }


class CompanyForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True
        for form in self.visible_fields():
            form.field.widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })

    class Meta:
        model = Company
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ingrese un nombre'}),
            'ruc': forms.TextInput(attrs={'placeholder': 'Ingrese un ruc'}),
            'mobile': forms.TextInput(attrs={'placeholder': 'Ingrese un teléfono celular'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Ingrese un teléfono convencional'}),
            'email': forms.TextInput(attrs={'placeholder': 'Ingrese un email'}),
            'address': forms.TextInput(attrs={'placeholder': 'Ingrese una dirección'}),
            'website': forms.TextInput(attrs={'placeholder': 'Ingrese una dirección web'}),
            'desc': forms.Textarea(attrs={'placeholder': 'Ingrese una descripción', 'rows': 3, 'cols': 3}),
            'igv': forms.TextInput(),
            'exchange_rate': forms.TextInput(attrs={'placeholder': 'Tasa de cambio (ej: 3.95)'}),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class PromotionsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['end_date'].widget.attrs['autofocus'] = True

    class Meta:
        model = Promotions
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control datetimepicker-input',
                'id': 'start_date',
                'value': datetime.now().strftime('%Y-%m-%d'),
                'data-toggle': 'datetimepicker',
                'data-target': '#start_date'
            }),
            'end_date': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control datetimepicker-input',
                'id': 'end_date',
                'value': datetime.now().strftime('%Y-%m-%d'),
                'data-toggle': 'datetimepicker',
                'data-target': '#end_date'
            }),
        }
        exclude = ['state']

    date_range = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off'
    }))


class DevolutionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_joined'].widget.attrs['autofocus'] = True

    class Meta:
        model = Devolution
        fields = '__all__'
        widgets = {
            'date_joined': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control datetimepicker-input',
                'id': 'start_date',
                'value': datetime.now().strftime('%Y-%m-%d'),
                'data-toggle': 'datetimepicker',
                'data-target': '#start_date'
            }),
        }

    sale = forms.ChoiceField(widget=forms.Select(attrs={
        'class': 'form-control select2',
        'style': 'width: 100%;'
    }))


class PaymentBankForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = PaymentBank
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ingrese el nombre del banco'}),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class CurrencyForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Currency
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ingrese el nombre de la moneda'}),
            'code': forms.TextInput(attrs={'placeholder': 'Ej: PEN, USD'}),
            'symbol': forms.TextInput(attrs={'placeholder': 'Ej: S/, $'}),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class PaymentMethodForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = PaymentMethodModel
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ingrese el nombre de la forma de pago'}),
            'code': forms.TextInput(attrs={'placeholder': 'Ej: efectivo, yape, plin'}),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data
