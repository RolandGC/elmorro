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
    
    // Valor inicial predeterminado para boxFinal
    const defaultBoxFinalValue = parseFloat(boxFinal.value) || 0;
    
    function getNumericValue(element) {
        if (!element) return 0;
        const value = parseFloat(element.value) || 0;
        return value;
    }
    
    function updateBoxFinal() {
        const initialBoxValue = getNumericValue(initialBox);
        const billsValue = getNumericValue(bills);
    
        // Calcula el nuevo valor de boxFinal basado en el valor predeterminado
        boxFinal.value = (defaultBoxFinalValue + initialBoxValue - billsValue).toFixed(2);
    }
    
    // Escucha los cambios en los inputs
    initialBox.addEventListener('change', updateBoxFinal);
    bills.addEventListener('change', updateBoxFinal);


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
            date_close: {
                validators: {
                    notEmpty: {
                        message: 'La fecha de cierre es obligatoria'
                    },
                    date: {
                        format: 'YYYY-MM-DD',
                        message: 'La fecha no es válida'
                    }
                },
            },
            hours_close: {
                validators: {
                    notEmpty: {
                        message: 'La hora de cierre es obligatoria'
                    },
                    time: {
                        format: 'HH:mm',
                        message: 'La hora no es válida'
                    }
                },
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

    // Configuración del DateTimePicker
    $('#id_date_close').datetimepicker({
        format: 'YYYY-MM-DD',
        locale: 'es'
    });

    $('#id_hours_close').datetimepicker({
        format: 'HH:mm',
        locale: 'es'
    });


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

    // Configuración del DateTimePicker
    $('#id_date_close').datetimepicker({
        format: 'YYYY-MM-DD',
        locale: 'es'
    });

    $('#id_hours_close').datetimepicker({
        format: 'HH:mm',
        locale: 'es'
    });


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
