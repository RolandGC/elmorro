document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('frmForm');
    const csrftoken = getCookie('csrftoken');

    // Campos de Caja Inicial (Soles y Dólares) - EDITABLES
    const initialBoxSoles = document.querySelector('#id_initial_box_soles');
    const initialBoxDolares = document.querySelector('#id_initial_box_dolares');

    // Campos de Efectivo (Soles y Dólares) - NO EDITABLES
    const efectivoSoles = document.querySelector('#id_efectivo_soles');
    const efectivoDolares = document.querySelector('#id_efectivo_dolares');

    // Campos de Yape (Solo Soles) - NO EDITABLE
    const yapeSoles = document.querySelector('#id_yape_soles');

    // Campos de Plin (Solo Soles) - NO EDITABLE
    const plinSoles = document.querySelector('#id_plin_soles');

    // Campos de Transferencia (Soles y Dólares) - NO EDITABLES
    const transferenciaSoles = document.querySelector('#id_transferencia_soles');
    const transferenciaDolares = document.querySelector('#id_transferencia_dolares');

    // Campos de Depósito (Soles y Dólares) - NO EDITABLES
    const depositoSoles = document.querySelector('#id_deposito_soles');
    const depositoDolares = document.querySelector('#id_deposito_dolares');

    // Campo de Gastos (Solo Soles) - NO EDITABLE
    const billsSoles = document.querySelector('#id_bills_soles');

    // Campos de Caja Final (Soles y Dólares)
    const boxFinalSoles = document.querySelector('#id_box_final_soles');
    const boxFinalDolares = document.querySelector('#id_box_final_dolares');

    // Configurar datetime_close con la fecha/hora actual
    const datetimeCloseInput = document.querySelector('#id_datetime_close');
    if (datetimeCloseInput) {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        datetimeCloseInput.value = `${year}-${month}-${day}T${hours}:${minutes}`;
    }

    function getNumericValue(element) {
        if (!element) return 0;
        const value = parseFloat(element.value) || 0;
        return isNaN(value) ? 0 : value;
    }

    function updateBoxFinal() {
        // Calcular caja final en SOLES
        // Fórmula: Caja Inicial + Efectivo + Yape + Plin + Transferencia + Depósito - Gastos
        if (initialBoxSoles && efectivoSoles && transferenciaSoles && depositoSoles && billsSoles && boxFinalSoles) {
            const initialSoles = getNumericValue(initialBoxSoles);
            const efectivoSolesVal = getNumericValue(efectivoSoles);
            const yapeSolesVal = getNumericValue(yapeSoles);
            const plinSolesVal = getNumericValue(plinSoles);
            const transferenciaSolesVal = getNumericValue(transferenciaSoles);
            const depositoSolesVal = getNumericValue(depositoSoles);
            const billsSolesVal = getNumericValue(billsSoles);

            const totalSoles = initialSoles + efectivoSolesVal + yapeSolesVal + plinSolesVal + transferenciaSolesVal + depositoSolesVal - billsSolesVal;
            boxFinalSoles.value = parseFloat(totalSoles.toFixed(2));

            console.log('🔄 Cálculo Caja Final SOLES:', {
                initial: initialSoles,
                efectivo: efectivoSolesVal,
                yape: yapeSolesVal,
                plin: plinSolesVal,
                transferencia: transferenciaSolesVal,
                deposito: depositoSolesVal,
                bills: billsSolesVal,
                total: parseFloat(totalSoles.toFixed(2))
            });
        }

        // Calcular caja final en DÓLARES
        // Fórmula: Caja Inicial + Efectivo + Transferencia + Depósito (SIN restar gastos)
        if (initialBoxDolares && efectivoDolares && transferenciaDolares && depositoDolares && boxFinalDolares) {
            const initialDolares = getNumericValue(initialBoxDolares);
            const efectivoDolaresVal = getNumericValue(efectivoDolares);
            const transferenciaDolaresVal = getNumericValue(transferenciaDolares);
            const depositoDolaresVal = getNumericValue(depositoDolares);

            const totalDolares = initialDolares + efectivoDolaresVal + transferenciaDolaresVal + depositoDolaresVal;
            boxFinalDolares.value = parseFloat(totalDolares.toFixed(2));

            console.log('🔄 Cálculo Caja Final DÓLARES:', {
                initial: initialDolares,
                efectivo: efectivoDolaresVal,
                transferencia: transferenciaDolaresVal,
                deposito: depositoDolaresVal,
                total: parseFloat(totalDolares.toFixed(2))
            });
        }
    }

    // Obtener valores iniciales vía AJAX
    function fetchInitialValues() {
        const formData = new FormData();
        formData.append('action', 'get_initial_values');

        let url = window.getInitialValuesUrl || form.action || window.location.href;

        console.log('📡 Solicitando valores iniciales de caja a:', url);

        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrftoken
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('HTTP error, status = ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log('✅ Datos recibidos del backend:', data);

            if (data.error) {
                console.error('❌ Error en get_initial_values:', data.error);
                return;
            }

            // Llenar campos de Caja Inicial
            if (initialBoxSoles && data.initial_box_soles !== undefined) {
                initialBoxSoles.value = parseFloat(data.initial_box_soles).toFixed(2);
                console.log('✓ Caja Inicial SOLES:', data.initial_box_soles);
            }
            if (initialBoxDolares && data.initial_box_dolares !== undefined) {
                initialBoxDolares.value = parseFloat(data.initial_box_dolares).toFixed(2);
                console.log('✓ Caja Inicial DÓLARES:', data.initial_box_dolares);
            }

            // Llenar campos de Efectivo
            if (efectivoSoles && data.efectivo_soles !== undefined) {
                efectivoSoles.value = parseFloat(data.efectivo_soles).toFixed(2);
                console.log('✓ Efectivo SOLES:', data.efectivo_soles);
            }
            if (efectivoDolares && data.efectivo_dolares !== undefined) {
                efectivoDolares.value = parseFloat(data.efectivo_dolares).toFixed(2);
                console.log('✓ Efectivo DÓLARES:', data.efectivo_dolares);
            }

            // Llenar campo de Yape
            if (yapeSoles && data.yape_soles !== undefined) {
                yapeSoles.value = parseFloat(data.yape_soles).toFixed(2);
                console.log('✓ Yape SOLES:', data.yape_soles);
            }

            // Llenar campo de Plin
            if (plinSoles && data.plin_soles !== undefined) {
                plinSoles.value = parseFloat(data.plin_soles).toFixed(2);
                console.log('✓ Plin SOLES:', data.plin_soles);
            }

            // Llenar campos de Transferencia
            if (transferenciaSoles && data.transferencia_soles !== undefined) {
                transferenciaSoles.value = parseFloat(data.transferencia_soles).toFixed(2);
                console.log('✓ Transferencia SOLES:', data.transferencia_soles);
            }
            if (transferenciaDolares && data.transferencia_dolares !== undefined) {
                transferenciaDolares.value = parseFloat(data.transferencia_dolares).toFixed(2);
                console.log('✓ Transferencia DÓLARES:', data.transferencia_dolares);
            }

            // Llenar campos de Depósito
            if (depositoSoles && data.deposito_soles !== undefined) {
                depositoSoles.value = parseFloat(data.deposito_soles).toFixed(2);
                console.log('✓ Depósito SOLES:', data.deposito_soles);
            }
            if (depositoDolares && data.deposito_dolares !== undefined) {
                depositoDolares.value = parseFloat(data.deposito_dolares).toFixed(2);
                console.log('✓ Depósito DÓLARES:', data.deposito_dolares);
            }

            // Llenar campo de Gastos (siempre en Soles)
            if (billsSoles && data.bills !== undefined) {
                billsSoles.value = parseFloat(data.bills).toFixed(2);
                console.log('✓ Gastos (Soles):', data.bills);
            }

            // Recalcular caja final
            updateBoxFinal();
        })
        .catch(error => {
            console.error('❌ Error al obtener valores iniciales:', error);
        });
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
        return cookieValue || '';
    }

    // Cargar valores iniciales
    fetchInitialValues();

    // Esperar a que los elementos estén listos y recalcular
    setTimeout(() => {
        updateBoxFinal();
    }, 500);

    // Agregar event listeners para recalcular automáticamente
    const campos = [
        initialBoxSoles, initialBoxDolares,
        efectivoSoles, efectivoDolares,
        yapeSoles, plinSoles,
        transferenciaSoles, transferenciaDolares,
        depositoSoles, depositoDolares,
        billsSoles
    ];

    campos.forEach(campo => {
        if (campo) {
            campo.addEventListener('input', updateBoxFinal);
            campo.addEventListener('change', updateBoxFinal);
        }
    });

    // Inicializar validación del formulario con FormValidation
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
            initial_box_soles: {
                validators: {
                    numeric: { message: 'Debe ser un valor numérico' }
                }
            },
            initial_box_dolares: {
                validators: {
                    numeric: { message: 'Debe ser un valor numérico' }
                }
            },
            efectivo_soles: {
                validators: {
                    numeric: { message: 'Debe ser un valor numérico' }
                }
            },
            efectivo_dolares: {
                validators: {
                    numeric: { message: 'Debe ser un valor numérico' }
                }
            },
            yape_soles: {
                validators: {
                    numeric: { message: 'Debe ser un valor numérico' }
                }
            },
            plin_soles: {
                validators: {
                    numeric: { message: 'Debe ser un valor numérico' }
                }
            },
            transferencia_soles: {
                validators: {
                    numeric: { message: 'Debe ser un valor numérico' }
                }
            },
            transferencia_dolares: {
                validators: {
                    numeric: { message: 'Debe ser un valor numérico' }
                }
            },
            deposito_soles: {
                validators: {
                    numeric: { message: 'Debe ser un valor numérico' }
                }
            },
            deposito_dolares: {
                validators: {
                    numeric: { message: 'Debe ser un valor numérico' }
                }
            },
            bills_soles: {
                validators: {
                    numeric: { message: 'Debe ser un valor numérico' }
                }
            },
            box_final_soles: {
                validators: {
                    numeric: { message: 'Debe ser un valor numérico' }
                }
            },
            box_final_dolares: {
                validators: {
                    numeric: { message: 'Debe ser un valor numérico' }
                }
            },
        }
    })
    .on('core.form.valid', function() {
        // Enviar el formulario cuando sea válido
        submit_formdata_with_ajax_form(fv);
    });

    // Evitar envío múltiple del formulario
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        fv.validate();
    });
});