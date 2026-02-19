document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('frmForm');

    const boxFinal = document.querySelector('#id_box_final');
    const initialBox = document.querySelector('#id_initial_box');
    const bills = document.querySelector('#id_bills');
    
    const efectivo = document.querySelector('#id_efectivo');
    const yape = document.querySelector('#id_yape');
    const plin = document.querySelector('#id_plin');
    const transferencia = document.querySelector('#id_transferencia');
    const deposito = document.querySelector('#id_deposito');
    
    function getNumericValue(element) {
        if (!element) return 0;
        const value = parseFloat(element.value) || 0;
        return isNaN(value) ? 0 : value;
    }
    
    function updateBoxFinal() {
        if (!boxFinal) return;
        
        const efectivoValue = getNumericValue(efectivo);
        const yapeValue = getNumericValue(yape);
        const plinValue = getNumericValue(plin);
        const transferenciaValue = getNumericValue(transferencia);
        const depositoValue = getNumericValue(deposito);
        const initialBoxValue = getNumericValue(initialBox);
        const billsValue = getNumericValue(bills);
    
        // Fórmula: efectivo + yape + plin + transferencia + deposito + initial_box - bills
        const total = (efectivoValue + yapeValue + plinValue + transferenciaValue + depositoValue + initialBoxValue - billsValue);
        
        // Para campos disabled, se puede cambiar el valor directamente
        boxFinal.value = parseFloat(total.toFixed(2));
        
        console.log('Cálculo BoxFinal:', {efectivoValue, yapeValue, plinValue, transferenciaValue, depositoValue, initialBoxValue, billsValue, total});
    }
    
    // Obtener valores iniciales vía AJAX
    function fetchInitialValues() {
        const formData = new FormData();
        formData.append('action', 'get_initial_values');
        
        // Usar la URL pasada desde el template o construir una
        let url = window.getInitialValuesUrl || form.action || window.location.href;
        
        console.log('Enviando fetch POST a:', url);
        
        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error('HTTP error, status = ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log('Valores iniciales obtenidos:', data);
            
            // Si hay error en la respuesta, mostrarlo
            if (data.error) {
                console.error('Error en get_initial_values:', data.error);
                return;
            }
            
            // Llenar los campos con valores obtenidos
            if (efectivo && data.efectivo !== undefined) {
                efectivo.value = data.efectivo;
                console.log('✓ Efectivo establecido a:', data.efectivo);
            }
            if (yape && data.yape !== undefined) {
                yape.value = data.yape;
                console.log('✓ Yape establecido a:', data.yape);
            }
            if (plin && data.plin !== undefined) {
                plin.value = data.plin;
                console.log('✓ Plin establecido a:', data.plin);
            }
            if (transferencia && data.transferencia !== undefined) {
                transferencia.value = data.transferencia;
                console.log('✓ Transferencia establecida a:', data.transferencia);
            }
            if (deposito && data.deposito !== undefined) {
                deposito.value = data.deposito;
                console.log('✓ Deposito establecido a:', data.deposito);
            }
            if (bills && data.bills !== undefined) {
                bills.value = data.bills;
                console.log('✓ Bills (GASTOS del día) establecido a:', data.bills);
            }
            
            // Recalcular box_final con los nuevos valores
            updateBoxFinal();
        })
        .catch(error => console.error('❌ Error al obtener valores iniciales:', error));
    }
    
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Cargar valores iniciales
    fetchInitialValues();
    
    // Esperar un poco más para asegurar que todos los elementos estén listos
    setTimeout(() => {
        updateBoxFinal();
    }, 200);

    // Inicializar la validación del formulario
    const fv = FormValidation.formValidation(form, {
        locale: 'es_ES',
        plugins: {
            trigger: new FormValidation.plugins.Trigger(),
            submitButton: new FormValidation.plugins.SubmitButton(),
            bootstrap: new FormValidation.plugins.Bootstrap(),
            icon: new FormValidation.plugins.Icon({
                valid: 'fa fa-check',
                invalid: 'fa fa-times',
                validating: 'fa fa-refresh',
            }),
        },
        fields: {
            datetime_close: {
                validators: {
                    notEmpty: {
                        message: 'La fecha y hora de cierre son obligatorias'
                    }
                }
            },
            efectivo: {
                validators: {
                    numeric: {
                        message: 'Debe ser un valor numérico'
                    }
                }
            },
            yape: {
                validators: {
                    numeric: {
                        message: 'Debe ser un valor numérico'
                    }
                }
            },
            plin: {
                validators: {
                    numeric: {
                        message: 'Debe ser un valor numérico'
                    }
                }
            },
            transferencia: {
                validators: {
                    numeric: {
                        message: 'Debe ser un valor numérico'
                    }
                }
            },
            deposito: {
                validators: {
                    numeric: {
                        message: 'Debe ser un valor numérico'
                    }
                }
            },
            initial_box: {
                validators: {
                    notEmpty: {
                        message: 'El monto inicial de caja es obligatorio'
                    },
                    numeric: {
                        message: 'Debe ser un valor numérico'
                    }
                }
            },
            bills: {
                validators: {
                    notEmpty: {
                        message: 'El monto en billetes es obligatorio'
                    },
                    numeric: {
                        message: 'Debe ser un valor numérico'
                    }
                }
            },
            box_final: {
                validators: {
                    notEmpty: {
                        message: 'El monto final de caja es obligatorio'
                    },
                    numeric: {
                        message: 'Debe ser un valor numérico'
                    }
                }
            },
            desc: {
                validators: {
                    stringLength: {
                        min: 4,
                        message: 'La descripción debe tener al menos 4 caracteres'
                    }
                }
            },
        }
    })
    .on('core.element.validated', function (e) {
        if (e.valid) {
            const groupEle = FormValidation.utils.closest(e.element, '.form-group');
            if (groupEle) {
                FormValidation.utils.classSet(groupEle, {
                    'has-success': false,
                });
            }
            FormValidation.utils.classSet(e.element, {
                'is-valid': false,
            });
        }
        const iconPlugin = fv.getPlugin('icon');
        const iconElement = iconPlugin && iconPlugin.icons.has(e.element) ? iconPlugin.icons.get(e.element) : null;
        iconElement && (iconElement.style.display = 'none');
    })
    .on('core.validator.validated', function (e) {
        if (!e.result.valid) {
            const messages = [].slice.call(form.querySelectorAll('[data-field="' + e.field + '"][data-validator]'));
            messages.forEach((messageEle) => {
                const validator = messageEle.getAttribute('data-validator');
                messageEle.style.display = validator === e.validator ? 'block' : 'none';
            });
        }
    })
    .on('core.form.valid', function () {
        submit_formdata_with_ajax_form(fv);
    });

    // Agregar event listeners para recalcular box_final cuando cambien los valores
    if (initialBox) {
        initialBox.addEventListener('input', updateBoxFinal);
        initialBox.addEventListener('change', updateBoxFinal);
    }
    if (bills) {
        bills.addEventListener('input', updateBoxFinal);
        bills.addEventListener('change', updateBoxFinal);
    }

    // El campo datetime_close es un input type="datetime-local" nativo del HTML5, no necesita inicialización adicional


    // Manejo del envío del formulario
    form.addEventListener('submit', function (e) {
        e.preventDefault(); // Evitar el envío por defecto

        fv.validate().then(function (status) {
            if (status === 'Valid') {
                // El formulario es válido, puedes enviarlo usando AJAX
                const formData = new FormData(form);

                $.ajax({
                    url: form.action, // Asegúrate de que `form.action` esté configurado correctamente
                    type: 'POST',
                    data: formData,
                    processData: false,
                    contentType: false,
                    headers: {
                        'X-CSRFToken': csrftoken // Asegúrate de que `csrftoken` esté disponible
                    },
                    success: function (response) {
                        // Maneja la respuesta del servidor
                        console.log('Formulario enviado exitosamente', response);
                        // Opcional: Redirige o muestra un mensaje de éxito
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        // Maneja errores
                        console.error('Error en el envío del formulario', textStatus, errorThrown);
                    }
                });
            } else {
                // El formulario no es válido, muestra errores
                console.log('El formulario no es válido');
            }
        });
    });
});
