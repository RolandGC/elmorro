var fv;
var input_datejoined;
var select_ctascollect;
var input_valor;
var ctascollect_data = null;

document.addEventListener('DOMContentLoaded', function (e) {
    const form = document.getElementById('frmForm');
    fv = FormValidation.formValidation(form, {
            locale: 'es_ES',
            localization: FormValidation.locales.es_ES,
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
                ctascollect: {
                    validators: {
                        notEmpty: {
                            message: 'Seleccione un cuenta por pagar'
                        }
                    }
                },
                date_joined: {
                    validators: {
                        notEmpty: {
                            message: 'La fecha es obligatoria'
                        },
                        date: {
                            format: 'YYYY-MM-DD',
                            message: 'La fecha no es válida'
                        }
                    }
                },
                valor: {
                    validators: {
                        notEmpty: {
                            message: 'El valor es obligatorio'
                        },
                        numeric: {
                            message: 'El valor no es un número',
                            thousandsSeparator: '',
                            decimalSeparator: '.'
                        }
                    }
                },
                desc: {
                    validators: {}
                },
            },
        }
    )
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
            // Validación adicional para deudas vencidas
            if (ctascollect_data && ctascollect_data.is_overdue) {
                var valor_ingresado = parseFloat(input_valor.val());
                var saldo = parseFloat(ctascollect_data.saldo);
                
                if (valor_ingresado < saldo) {
                    message_error('La deuda está vencida desde el ' + ctascollect_data.end_date + '. Debe pagar el saldo completo de S/. ' + saldo.toFixed(2));
                    fv.disableSubmitButton(true);
                    return false;
                }
            }
            
            var parameters = {};
            $.each($(fv.form).serializeArray(), function (key, item) {
                parameters[item.name] = item.value;
            })
            console.log(parameters);

            submit_with_ajax('Notificación',
                '¿Estas seguro de realizar la siguiente acción?',
                pathname,
                parameters,
                function () {
                    location.href = fv.form.getAttribute('data-url');
                }
            );

        });
});

$(function () {

    input_datejoined = $('input[name="date_joined"]');
    select_ctascollect = $('select[name="ctascollect"]');
    input_valor = $('input[name="valor"]');

    $('.select2').select2({
        theme: 'bootstrap4',
        language: "es"
    });

    select_ctascollect.select2({
        theme: "bootstrap4",
        language: 'es',
        allowClear: true,
        ajax: {
            delay: 250,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            url: pathname,
            data: function (params) {
                var queryParameters = {
                    term: params.term,
                    action: 'search_ctascollect'
                }
                return queryParameters;
            },
            processResults: function (data) {
                return {
                    results: data
                };
            },
        },
        placeholder: 'Ingrese una descripción',
        minimumInputLength: 1,
    })
        .on('select2:select', function (e) {
            fv.revalidateField('ctascollect');
            var data = e.params.data;
            ctascollect_data = data;  // Guardar datos de la cuenta
            
            // Mostrar advertencia si está vencida
            let deuda_html = '<strong>Deuda: S/. ' + parseFloat(data.saldo).toFixed(2) + '</strong>';
            
            if (data.is_overdue) {
                deuda_html = '<div class="alert alert-danger alert-dismissible fade show" style="padding: 10px 15px; margin-bottom: 10px;">';
                deuda_html += '<strong>⚠️ DEUDA VENCIDA</strong><br>';
                deuda_html += '<strong style="font-size: 16px;">S/. ' + parseFloat(data.saldo).toFixed(2) + '</strong><br>';
                deuda_html += '<small>Fecha límite: <strong>' + data.end_date + '</strong></small><br>';
                deuda_html += '<small>(Vencida hace ' + data.days_overdue + ' días)</small><br>';
                deuda_html += '<strong style="color: #721c24; font-size: 13px;">👉 DEBE PAGAR EL SALDO COMPLETO</strong>';
                deuda_html += '</div>';
            } else {
                deuda_html = '<div class="alert alert-info alert-dismissible fade show" style="padding: 10px 15px; margin-bottom: 10px;">';
                deuda_html += '<strong>Saldo Pendiente</strong><br>';
                deuda_html += '<strong style="font-size: 16px;">S/. ' + parseFloat(data.saldo).toFixed(2) + '</strong>';
                deuda_html += '</div>';
            }
            
            $('.deuda').html(deuda_html);
            $('input[name="valor"]').trigger("touchspin.updatesettings", {max: parseFloat(data.saldo)});
        })
        .on('select2:clear', function (e) {
            fv.revalidateField('|');
            $('.deuda').html('');
            ctascollect_data = null;
        });

    $('input[name="valor"]').TouchSpin({
        min: 0.01,
        max: 1000000,
        step: 0.01,
        decimals: 2,
        boostat: 5,
        maxboostedstep: 10,
        prefix: 'S/.',
        verticalbuttons: true,
    }).on('change touchspin.on.min touchspin.on.max', function () {
        fv.revalidateField('valor');
        
        // Validación en tiempo real para deudas vencidas
        if (ctascollect_data && ctascollect_data.is_overdue) {
            var valor_ingresado = parseFloat($(this).val());
            var saldo = parseFloat(ctascollect_data.saldo);
            
            if (valor_ingresado < saldo) {
                fv.enableSubmitButton(false);
                $('.invalid-feedback').text('Debe pagar el saldo completo: S/. ' + saldo.toFixed(2));
                $(this).addClass('is-invalid');
            } else {
                fv.enableSubmitButton(true);
                $(this).removeClass('is-invalid');
            }
        }
    }).keypress(function (e) {
        return validate_decimals($(this), e);
    });

    input_datejoined.datetimepicker({
        format: 'YYYY-MM-DD',
        locale: 'es',
        keepOpen: false,
        // date: new moment().format("YYYY-MM-DD")
    });

    input_datejoined.on('change.datetimepicker', function () {
        fv.revalidateField('date_joined');
    });

    $('.deuda').html('');
});
