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
    const yapeSoles = document.querySelector('#id_yape');

    // Campos de Plin (Solo Soles) - NO EDITABLE
    const plinSoles = document.querySelector('#id_plin');

    // Campos de Transferencia (Soles y Dólares) - NO EDITABLES
    const transferenciaSoles = document.querySelector('#id_transferencia_soles');
    const transferenciaDolares = document.querySelector('#id_transferencia_dolares');

    // Campos de Depósito (Soles y Dólares) - NO EDITABLES
    const depositoSoles = document.querySelector('#id_deposito_soles');
    const depositoDolares = document.querySelector('#id_deposito_dolares');

    // Campo de Gastos (Solo Soles) - NO EDITABLE
    const billsSoles = document.querySelector('#id_bills');

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
    //fetchInitialValues();

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