from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import Group
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
        super().__init__(*args, **kwargs)
        
        # Redondear valores a 2 decimales
        self.initial['cash_sale'] = round(Box.total_efectivo() + Box.total_payments_ctas_collect_efectivo(), 2)
        self.initial['sale_card'] = round(Box.total_tarjeta_yape_plin() + Box.total_payments_ctas_collect_credito(), 2)
        self.initial['box_final'] = round(
            Box.total_efectivo() + 
            Box.total_payments_ctas_collect_efectivo() + 
            Box.total_tarjeta_yape_plin() + 
            Box.total_payments_ctas_collect_credito(), 2
        )
    class Meta:
        model = Box
        fields = '__all__'
        widgets = {
            'date_close': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control datetimepicker-input',
                'id': 'date_joined',
                'value': datetime.now().strftime('%Y-%m-%d'),
                'data-toggle': 'datetimepicker',
                'data-target': '#date_joined'
            }),
            'hours_close': forms.TimeInput(format='%H:%M', attrs={
                'type': 'time',
                'value': datetime.now().strftime('%H:%M')
            }),
            'cash_sale': forms.TextInput(
                attrs = {
                    'type': 'number',
                }
            ),
            # 'cash_credit': forms.TextInput(
            #     attrs = {
            #         'type': 'number',
            #     }
            # ),
            'sale_card': forms.TextInput(
                attrs = {
                    'type': 'number',
                }
            ),
            'initial_box': forms.TextInput(
               attrs = {
                   'type': 'number',
                    'value': '0'
                }
            ),
            'bills': forms.TextInput(
               attrs = {
                   'type': 'number',
                    'value': '0'
                }
            ),
            'box_final': forms.TextInput(
                attrs = {
                    'type': 'number',
                }
            ),
            'desc': forms.TextInput(attrs={'placeholder': 'Ingrese descripción'})
        }
        exclude=['date_joined']
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
        # Establecer la fecha actual como valor inicial para operation_date
        self.fields['operation_date'].initial = date.today()
        # Hacer el campo total obligatorio
        self.fields['total'].required = True
        # self.initial['client'] = '2'

    class Meta:
        model = Sale
        fields = '__all__'
        widgets = {
            'client': forms.Select(attrs={'class': 'custom-select select2'}),
            'payment_condition': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'payment_method': forms.Select(attrs={'class': 'form-control select2 custom-select', 'style': 'width: 100%;'}),
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
            'operation_date': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control',
                'id': 'operation_date',
                'type': 'date',
                'data-toggle': 'datetimepicker',
                'data-target': '#operation_date'
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
            'operation_number': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'placeholder': 'Ingrese el número de operación'
            }),
            'payment_bank': forms.Select(attrs={
                'class': 'form-control select2',
                'style': 'width: 100%;'
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
