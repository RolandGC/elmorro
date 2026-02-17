var current_date;

var fvSale;
var fvClient;

var select_client;
var input_birthdate;
var select_paymentcondition;
var select_paymentmethod;
var select_paymentbank;
var original_bank_options;
var input_cash;
let input_initial;
var input_cardnumber;
var input_amountdebited;
var input_titular;
var input_change;
var input_amount;
var amount_user_edited = false;
var total_user_edited = false;

var tblSearchProducts;
var tblProducts;

var input_searchproducts;
var input_endcredit;
var inputs_vents;

var lastClickedButtonId;

// Helper function to safely format numbers and avoid NaN
function safeToFixed(value, decimals = 2) {
    var num = parseFloat(value);
    if (isNaN(num)) {
        num = 0;
    }
    return num.toFixed(decimals);
}

$(document).ready(function() {
    $('.btnCollect').on('click', function() {
        lastClickedButtonId = $(this).attr('id');
    });
});

var vents = {
    details: {
        subtotal: 0.00,
        igv: 0.00,
        total_igv: 0.00,
        dscto: 0.00,
        total_dscto: 0.00,
        total: 0.00,
        cash: 0.00,
        initial:0.00,
        change: 0.00,
        products: [],
    },
    calculate_invoice: function () {
        var total = 0.00;
        $.each(this.details.products, function (i, item) {
            item.cant = parseInt(item.cant) || 0;
            item.subtotal = item.cant * parseFloat(item.price_current || 0);
            item.total_dscto = parseFloat(item.dscto || 0);

            item.total = item.subtotal - item.total_dscto;
            total += item.total;
        });

        vents.details.subtotal = total;
        var dscto_val = parseFloat($('input[name="dscto"]').val()) || 0;
        vents.details.dscto = isNaN(dscto_val) ? 0 : dscto_val;
        vents.details.total_dscto = vents.details.dscto;
        vents.details.total_igv = vents.details.subtotal * (vents.details.igv / 100);
        vents.details.total = vents.details.subtotal - vents.details.total_dscto;
        vents.details.total = parseFloat(vents.details.total.toFixed(2));
        
        $('input[name="cash"]').val(safeToFixed(vents.details.subtotal, 2));
        $('input[name="subtotal"]').val(safeToFixed(vents.details.subtotal, 2));
        $('input[name="igv"]').val(safeToFixed(vents.details.igv, 2));
        $('input[name="total_igv"]').val(safeToFixed(vents.details.total_igv, 2));
        $('input[name="total_dscto"]').val(safeToFixed(vents.details.total_dscto, 2));
        
        // Only overwrite the total if the user hasn't modified it
        if (!total_user_edited) {
            $('input[name="total"]').val(safeToFixed(vents.details.total, 2));
            // keep internal total in sync
            vents.details.total = parseFloat($('input[name="total"]').val()) || vents.details.total;
        } else {
            // if user edited total, respect it and update internal total
            var manual = parseFloat($('input[name="total"]').val());
            if (!isNaN(manual)) {
                vents.details.total = manual;
            }
        }
        
        // Only overwrite the editable amount if the user hasn't modified it
        if (!amount_user_edited) {
            $('input[name="amount"]').val(safeToFixed(vents.details.total, 2));
            // keep internal total in sync
            vents.details.total = parseFloat($('input[name="amount"]').val()) || vents.details.total;
        } else {
            // if user edited amount, respect it and update internal total
            var manual = parseFloat($('input[name="amount"]').val());
            if (!isNaN(manual)) {
                vents.details.total = manual;
            }
        }
    },
    list_products: function () {
        this.calculate_invoice();
        tblProducts = $('#tblProducts').DataTable({
            //responsive: true,
            autoWidth: false,
            destroy: true,
            data: this.details.products,
            ordering: false,
            lengthChange: false,
            searching: false,
            paginate: false,
            scrollX: true,
            scrollCollapse: true,
            columns: [
                {data: "id"},
                {data: "name"},
                {data: "subtotal"},
                {data: "total"},
            ],
            columnDefs: [
                {
                    targets: [-2, -1],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return 'S/.' + safeToFixed(data, 2);
                    }
                },
                {
                    targets: [0],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return '<a rel="remove" class="btn btn-danger btn-flat btn-xs"><i class="fas fa-times"></i></a>';
                    }
                },
            ],
            rowCallback: function (row, data, index) {
                var tr = $(row).closest('tr');
                var stock = data.category.inventoried ? data.stock : 1000000;
                tr.find('input[name="cant"]')
                    .TouchSpin({
                        min: 1,
                        max: stock,
                        verticalbuttons: true
                    })
                    .keypress(function (e) {
                        return validate_form_text('numbers', e, null);
                    });

                tr.find('input[name="dscto_unitary"]')
                    .TouchSpin({
                        min: 0.00,
                        max: 100,
                        step: 1.00,
                        decimals: 2,
                        boostat: 5,
                        verticalbuttons: true,
                        maxboostedstep: 10,
                    })
                    .keypress(function (e) {
                        return validate_decimals($(this), e);
                    });
            },
            initComplete: function (settings, json) {

            },
        });
    },
    get_products_ids: function () {
        return this.details.products.map(value => value.id);
    },
    add_product: function (item) {
        this.details.products.push(item);
        this.list_products();
    },
};

document.addEventListener('DOMContentLoaded', function (e) {
    const frmClient = document.getElementById('frmClient');
    fvClient = FormValidation.formValidation(frmClient, {
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
                full_name: {
                    validators: {
                        notEmpty: {},
                        stringLength: {
                            min: 2,
                        },
                    }
                },
                dni: {
                    validators: {
                        notEmpty: {},
                        stringLength: {
                            min: 8
                        },
                        digits: {},
                        remote: {
                            url: pathname,
                            data: function () {
                                return {
                                    obj: frmClient.querySelector('[name="dni"]').value,
                                    type: 'dni',
                                    action: 'validate_client'
                                };
                            },
                            message: 'El número de cedula ya se encuentra registrado',
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': csrftoken
                            },
                        }
                    }
                },
                mobile: {
                    validators: {
                        notEmpty: {},
                        stringLength: {
                            min: 6
                        },
                        digits: {},
                        remote: {
                            url: pathname,
                            data: function () {
                                return {
                                    obj: frmClient.querySelector('[name="mobile"]').value,
                                    type: 'mobile',
                                    action: 'validate_client'
                                };
                            },
                            message: 'El número de teléfono ya se encuentra registrado',
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': csrftoken
                            },
                        }
                    }
                },
                email: {
                    validators: {

                        stringLength: {
                            min: 5
                        },
                        regexp: {
                            regexp: /^([a-z0-9_\.-]+)@([\da-z\.-]+)\.([a-z\.]{2,6})$/i,
                            message: 'El formato email no es correcto'
                        },
                        remote: {
                            url: pathname,
                            data: function () {
                                return {
                                    obj: frmClient.querySelector('[name="email"]').value,
                                    type: 'email',
                                    action: 'validate_client'
                                };
                            },
                            message: 'El email ya se encuentra registrado',
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': csrftoken
                            },
                        }
                    }
                },
                address: {
                    validators: {
                        stringLength: {
                            min: 4,
                        }
                    }
                },
                image: {
                    validators: {
                        file: {
                            extension: 'jpeg,jpg,png',
                            type: 'image/jpeg,image/png',
                            maxFiles: 1,
                            message: 'Introduce una imagen válida'
                        }
                    }
                },
                birthdate: {
                    validators: {
                        notEmpty: {
                            message: 'La fecha es obligatoria'
                        },
                        date: {
                            format: 'YYYY-MM-DD',
                            message: 'La fecha no es válida'
                        }
                    },
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
            const iconPlugin = fvClient.getPlugin('icon');
            const iconElement = iconPlugin && iconPlugin.icons.has(e.element) ? iconPlugin.icons.get(e.element) : null;
            iconElement && (iconElement.style.display = 'none');
        })
        .on('core.validator.validated', function (e) {
            if (!e.result.valid) {
                const messages = [].slice.call(frmClient.querySelectorAll('[data-field="' + e.field + '"][data-validator]'));
                messages.forEach((messageEle) => {
                    const validator = messageEle.getAttribute('data-validator');
                    messageEle.style.display = validator === e.validator ? 'block' : 'none';
                });
            }
        })
        .on('core.form.valid', function () {
            var parameters = new FormData(fvClient.form);
            parameters.append('action', 'create_client');
            submit_formdata_with_ajax('Notificación', '¿Estas seguro de realizar la siguiente acción?', pathname,
                parameters,
                function (request) {
                    var newOption = new Option(request.user.full_name + ' / ' + request.user.dni, request.id, false, true);
                    select_client.append(newOption).trigger('change');
                    fvSale.revalidateField('client');
                    $('#myModalClient').modal('hide');
                }
            );
        });
});

document.addEventListener('DOMContentLoaded', function (e) {
    function validateChange() {
        var cash = parseFloat(input_cash.val())
        var method_payment = select_paymentmethod.val();
        var total = parseFloat(vents.details.total);

        if (method_payment === 'efectivo') {
            if (cash < total) {
                return {valid: false, message: 'El efectivo debe ser mayor o igual al total a pagar'};
            }
        } else if (method_payment === 'efectivo_tarjeta') {
            var amount_debited = (total - cash);
            input_amountdebited.val(amount_debited.toFixed(2));
        }
        return {valid: true};
    }
    function validateChange2() {
        var initial = parseFloat(input_initial.val())
        var paymentcondition = select_paymentcondition.val()

        if (paymentcondition=== 'credito') {
            if (initial<=0) {
                return {valid: false, message: 'El inicial debe de ser mayor a 0'};
            }
        }
        return {valid: true};
    }

    const frmSale = document.getElementById('frmSale');
    fvSale = FormValidation.formValidation(frmSale, {
            locale: 'es_ES',
            localization: FormValidation.locales.es_ES,
            plugins: {
                trigger: new FormValidation.plugins.Trigger(),
                submitButton: new FormValidation.plugins.SubmitButton(),
                bootstrap: new FormValidation.plugins.Bootstrap(),
                // excluded: new FormValidation.plugins.Excluded(),
                icon: new FormValidation.plugins.Icon({
                    valid: 'fa fa-check',
                    invalid: 'fa fa-times',
                    validating: 'fa fa-refresh',
                }),
            },
            fields: {
                client: {
                    validators: {
                        notEmpty: {
                            message: 'Seleccione un cliente'
                        },
                    }
                },
                end_credit: {
                    validators: {
                        notEmpty: {
                            enabled: false,
                            message: 'La fecha es obligatoria'
                        },
                        date: {
                            format: 'YYYY-MM-DD',
                            message: 'La fecha no es válida'
                        }
                    }
                },
                initial: {
                    validators: {
                        notEmpty: {},
                        callback: {
                            //message: 'El cambio no puede ser negativo',
                            callback: function (input) {
                                return validateChange2();
                            }
                        }
                    }
                },
                payment_condition: {
                    validators: {
                        notEmpty: {
                            message: 'Seleccione una forma de pago'
                        },
                    }
                },
                payment_method: {
                    validators: {
                        notEmpty: {
                            message: 'Seleccione un método de pago'
                        },
                    }
                },
                payment_bank: {
                    validators: {
                        notEmpty: {
                            enabled: false,
                            message: 'Seleccione un banco'
                        },
                    }
                },
                operation_number: {
                    validators: {
                        notEmpty: {
                            enabled: false,
                            message: 'Ingrese el número de operación'
                        },
                    }
                },
                operation_date: {
                    validators: {
                        notEmpty: {
                            enabled: false,
                            message: 'La fecha de operación es obligatoria'
                        },
                        date: {
                            format: 'YYYY-MM-DD',
                            message: 'La fecha no es válida'
                        }
                    }
                },
                type_voucher: {
                    validators: {
                        notEmpty: {
                            message: 'Seleccione un tipo de comprobante'
                        },
                    }
                },
                card_number: {
                    validators: {
                        notEmpty: {
                            enabled: false,
                        },
                        regexp: {
                            regexp: /^\d{4}\s\d{4}\s\d{4}\s\d{4}$/,
                            message: 'Debe ingresar un numéro de tarjeta en el siguiente formato 1234 5678 9103 2247'
                        },
                        stringLength: {
                            min: 2,
                            max: 19,
                        },
                    }
                },
                titular: {
                    validators: {
                        notEmpty: {
                            enabled: false,
                        },
                        stringLength: {
                            min: 3,
                        },
                    }
                },
                amount_debited: {
                    validators: {
                        notEmpty: {
                            enabled: false,
                        },
                        numeric: {
                            message: 'El valor no es un número',
                            thousandsSeparator: '',
                            decimalSeparator: '.'
                        },
                    }
                },
                cash: {
                    validators: {
                        notEmpty: {
                            enabled: false
                        },
                        numeric: {
                            enabled: false
                        }
                    }
                },
                change: {
                    validators: {
                        notEmpty: {
                            enabled: false
                        },
                        callback: {
                            enabled: false
                        }
                    }
                },
                total: {
                    validators: {
                        notEmpty: {
                            message: 'El monto total es obligatorio'
                        },
                        numeric: {
                            message: 'El monto debe ser un número válido',
                            thousandsSeparator: '',
                            decimalSeparator: '.'
                        },
                        greaterThanOrEqual: {
                            value: 0,
                            message: 'El monto total no puede ser negativo'
                        }
                    }
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
            const iconPlugin = fvSale.getPlugin('icon');
            const iconElement = iconPlugin && iconPlugin.icons.has(e.element) ? iconPlugin.icons.get(e.element) : null;
            iconElement && (iconElement.style.display = 'none');
        })
        .on('core.validator.validated', function (e) {
            if (!e.result.valid) {
                const messages = [].slice.call(frmSale.querySelectorAll('[data-field="' + e.field + '"][data-validator]'));
                messages.forEach((messageEle) => {
                    const validator = messageEle.getAttribute('data-validator');
                    messageEle.style.display = validator === e.validator ? 'block' : 'none';
                });
            }
        })
        .on('core.form.valid', function () {
            var parameters = new FormData($(fvSale.form)[0]);
            parameters.append('action', $('input[name="action"]').val());
            parameters.append('payment_method', select_paymentmethod.val());
            parameters.append('payment_condition', select_paymentcondition.val());
            parameters.append('end_credit', input_endcredit.val());
            parameters.append('cash', input_cash.val());
            parameters.append('change', input_change.val() || '0.00');
            parameters.append('card_number', input_cardnumber.val());
            parameters.append('titular', input_titular.val());
            parameters.append('initial', input_initial.val());
            parameters.append('dscto', $('input[name="dscto"]').val() || '0.00');
            parameters.append('amount_debited', input_amountdebited.val());
            // Agregar el total ingresado por el usuario
            parameters.set('total', $('input[name="total"]').val());
            // attach date_joined (supports datetime-local input)
            var date_joined_val = $('input[name="date_joined"]').val() || $('#date_joined').val() || $('#id_date_joined').val() || '';
            parameters.append('date_joined', date_joined_val);
            console.log('date_joined sent:', date_joined_val);
            console.log('total sent:', $('input[name="total"]').val());
            // attach operation_number for Yape/Plin/Transferencia/Depósito
            parameters.append('operation_number', $('input[name="operation_number"]').val() || '');
            parameters.append('comment', $('textarea[name="comment"]').val());
            console.log(parameters)
            if (vents.details.products.length === 0) {
                message_error('Debe tener al menos un item en el detalle de la venta');
                $('.nav-tabs a[href="#menu1"]').tab('show');
                return false;
            }
            parameters.append('products', JSON.stringify(vents.details.products));
            let urlrefresh = fvSale.form.getAttribute('data-url');
            console.log('Buton:', lastClickedButtonId)
            submit_formdata_with_ajax('Notificación',
                '¿Estas seguro de realizar la siguiente acción?',
                pathname,
                parameters,

                function (request) {
                    console.log()
                    dialog_action('Notificación', '¿Desea Imprimir el Comprobante?', function () {
                        window.open('/pos/crm/sale/print/voucher/' + request.id + '/', '_blank');
                        location.href = urlrefresh;
                    }, function () {
                        location.href = urlrefresh;
                    });

                },
            );
            // fetch(pathname, {
            //     method: 'POST',
            //     body: parameters,
            //     headers: {
            //         'X-CSRFToken': csrftoken
            //     }
            // })
            // .then(response => response.json())
            // .then(request => {
            //     console.log(request);
            //     // Ejecutar las acciones necesarias después de recibir la respuesta del servidor
            //     window.open('/pos/crm/sale/print/voucher/' + request.id + '/', '_blank');
            //     location.href = urlrefresh;
            // })
            // .catch(error => {
            //     console.error('Error:', {error});
            //     // Manejar errores aquí si es necesario
            // });
        });
});

function printInvoice(id) {
    var printWindow = window.open("/pos/crm/sale/print/voucher/" + id + "/", 'Print', 'left=200, top=200, width=950, height=500, toolbar=0, resizable=0');
    printWindow.addEventListener('load', function () {
        printWindow.print();
    }, true);
}

function hideRowsVents(values) {
    $.each(values, function (key, value) {
        if (value.enable) {
            $(inputs_vents[value.pos]).show();
        } else {
            $(inputs_vents[value.pos]).hide();
        }
    });
}

$(function () {

    current_date = new moment().format("YYYY-MM-DD");
    input_searchproducts = $('input[name="searchproducts"]');
    select_client = $('select[name="client"]');
    input_birthdate = $('input[name="birthdate"]');
    input_endcredit = $('input[name="end_credit"]');
    input_initial = $('input[name="initial"]');
    select_paymentcondition = $('select[name="payment_condition"]');
    select_paymentmethod = $('select[name="payment_method"]');
    select_paymentbank = $('select[name="payment_bank"]');
    // Cache original bank options so we can restore/filter reliably (works with Select2)
    original_bank_options = select_paymentbank.find('option').clone();
    input_amount = $('input[name="amount"]');
    // When user edits the amount manually, respect it and stop auto-overwriting
    input_amount.on('input change', function () {
        amount_user_edited = true;
        var manual = parseFloat($(this).val());
        if (!isNaN(manual)) {
            vents.details.total = manual;
        }
        // Revalidate dependent validators
        try { fvSale.revalidateField('change'); } catch (e) {}
    });
    
    // Add listener for total field
    var input_total = $('input[name="total"]');
    input_total.on('input change', function () {
        total_user_edited = true;
        var manual = parseFloat($(this).val());
        if (!isNaN(manual)) {
            vents.details.total = manual;
        }
        // Also update amount field to keep them in sync
        $('input[name="amount"]').val(manual.toFixed(2));
        amount_user_edited = true;
    });
    
    input_cardnumber = $('input[name="card_number"]');
    input_amountdebited = $('input[name="amount_debited"]');
    input_cash = $('input[name="cash"]');
    input_change = $('input[name="change"]').length > 0 ? $('input[name="change"]') : {val: () => '0.00'};
    input_titular = $('input[name="titular"]');
    inputs_vents = $('.rowVents');
    console.log(inputs_vents)

    $('.select2').select2({
        theme: 'bootstrap4',
        language: "es",
    });
    // if(client_default) {
    //     client_default = JSON.parse(client_default)
    //     select_client.append(`<option value="${client_default.id}">${client_default.user.full_name} / ${client_default.user.dni}</option>`);
    //     select_client.select2();
    //     select_client.val(`${client_default.id}`).trigger('change');
    // }
    /* Product */
    console.log(vents.get_products_ids())
    input_searchproducts.autocomplete({
        source: function (request, response) {
            $.ajax({
                url: pathname,
                data: {
                    'action': 'search_products',
                    'term': request.term,
                    'ids': JSON.stringify(vents.get_products_ids()),
                },
                dataType: "json",
                type: "POST",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                beforeSend: function () {

                },
                success: function (data) {
                    response(data);
                }
            });
        },
        min_length: 3,
        delay: 300,
        select: function (event, ui) {
            event.preventDefault();
            $(this).blur();
            if (ui.item.stock === 0 && ui.item.category.inventoried) {
                message_error('El stock de este producto esta en 0');
                return false;
            }
            ui.item.cant = 1;
            vents.add_product(ui.item);
            $(this).val('').focus();
        }
    });

    $('.btnClearProducts').on('click', function () {
        input_searchproducts.val('').focus();
    });

    $('#tblProducts tbody')
        .off()
        .on('click', 'a[rel="remove"]', function () {
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            vents.details.subtotal = vents.details.subtotal - vents.details.products[tr.row].subtotal;
            vents.details.products.splice(tr.row, 1);
            vents.details.total_igv = vents.details.subtotal * (vents.details.igv / 100);
            vents.details.total = vents.details.subtotal - vents.details.total_dscto;
            vents.details.total = parseFloat(vents.details.total.toFixed(2));
            $('input[name="cash"]').val(safeToFixed(vents.details.subtotal, 2));
            $('input[name="subtotal"]').val(safeToFixed(vents.details.subtotal, 2));
            $('input[name="total_igv"]').val(safeToFixed(vents.details.total_igv, 2));
            $('input[name="total"]').val(safeToFixed(vents.details.total, 2));
            $('input[name="amount"]').val(vents.details.total.toFixed(2));
            tblProducts.row(tr.row).remove().draw();
        });

    $('.btnSearchProducts').on('click', function () {
        tblSearchProducts = $('#tblSearchProducts').DataTable({
            // responsive: true,
            // autoWidth: false,
            destroy: true,
            ajax: {
                url: pathname,
                type: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: {
                    'action': 'search_products',
                    'term': input_searchproducts.val(),
                    'ids': JSON.stringify(vents.get_products_ids()),
                },
                dataSrc: ""
            },
            scrollX: true,
            scrollCollapse: true,
            columns: [
                {data: "name"},
                {data: "category.name"},
                {data: "pvp"},
                {data: "price_promotion"},
                {data: "stock"},
                {data: "id"},
            ],
            columnDefs: [
                {
                    targets: [0],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return data
                    }
                },
                {
                    targets: [1],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return data
                    }
                },
                {
                    targets: [2],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return 'S/.' + parseFloat(data).toFixed(2);
                    }
                },
                {
                    targets: [3],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return 'S/.' + parseFloat(data).toFixed(2);
                    }
                },
                {
                    targets: [4],
                    class: 'text-center',
                    render: function (data, type, row) {
                        if (row.category.inventoried) {
                            if (row.stock > 0) {
                                return '<span class="badge badge-success">' + row.stock + '</span>';
                            }
                            return '<span class="badge badge-danger">' + row.stock + '</span>';
                        }
                        return '<span class="badge badge-secondary">Sin stock</span>';
                    }
                },
                {
                    targets: [-1],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return '<a rel="add" class="btn btn-success btn-flat btn-xs"><i class="fas fa-plus"></i></a>';
                    }
                }
            ],
            rowCallback: function (row, data, index) {

            },
        });
        $('#myModalSearchProducts').modal('show');
    });

    $('#tblSearchProducts tbody')
        .off()
        .on('click', 'a[rel="add"]', function () {
            var row = tblSearchProducts.row($(this).parents('tr')).data();
            row.cant = 1;
            vents.add_product(row);
            tblSearchProducts.row($(this).parents('tr')).remove().draw();
        });

    $('.btnRemoveAllProducts').on('click', function () {
        if (vents.details.products.length === 0) return false;
        dialog_action('Notificación', '¿Estas seguro de eliminar todos los items de tu detalle?', function () {
            vents.details.products = [];
            vents.list_products();
        });
    });

    /* Client */

    select_client.select2({
        theme: "bootstrap4",
        language: 'es',
        allowClear: true,
        // dropdownParent: modal_sale,
        ajax: {
            delay: 5,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            url: pathname,
            data: function (params) {
                var queryParameters = {
                    term: params.term,
                    action: 'search_client'
                }
                return queryParameters;
            },
            processResults: function (data) {
            // Verificar si "NN NN" está presente en los resultados
            //     var hasNN = data.some(function(client) {
            //         return client.user.full_name === 'NN NN'; // Ajusta según la estructura real de tus datos de cliente
            //     });

            // // Establecer un valor predeterminado si "NN NN" está presente
            //     if (hasNN) {
            //         data.unshift({ id: 'NN NN', text: 'Valor Predeterminado' }); // Ajusta el texto según tus necesidades
            //     }

                return {
                    results: data
                };
            },
        },
        placeholder: 'Ingrese una descripción',
        minimumInputLength: 1,

    })
    .on('select2:select', function (e) {
        fvSale.revalidateField('client');
    })
    .on('select2:clear', function (e) {
        fvSale.revalidateField('client');
    });

    $('.btnAddClient').on('click', function () {
        input_birthdate.datetimepicker('date', new Date());
        $('#myModalClient').modal('show');
    });

    $('#myModalClient').on('hidden.bs.modal', function () {
        fvClient.resetForm(true);
    });

    $('input[name="dni"]').keypress(function (e) {
        return validate_form_text('numbers', e, null);
    });

    $('input[name="mobile"]').keypress(function (e) {
        return validate_form_text('numbers', e, null);
    });

    input_birthdate.datetimepicker({
        useCurrent: false,
        format: 'YYYY-MM-DD',
        locale: 'es',
        keepOpen: false,
        maxDate: current_date
    });

    input_birthdate.on('change.datetimepicker', function (e) {
        fvClient.revalidateField('birthdate');
    });

    /* Sale */

    select_paymentcondition
        .on('change', function () {
            var id = $(this).val();
            hideRowsVents([{'pos': 0, 'enable': false}, {'pos': 1, 'enable': false}, {'pos': 2, 'enable': false}]);
            fvSale.disableValidator('card_number');
            fvSale.disableValidator('titular');
            fvSale.disableValidator('amount_debited');
            fvSale.disableValidator('cash');
            fvSale.disableValidator('change');
            switch (id) {
                case "contado":
                    fvSale.disableValidator('end_credit');
                    select_paymentmethod.prop('disabled', false).val('efectivo').trigger('change');
                    input_initial.prop('disabled', true)
                    $('.rowInitial').hide();
                    break;
                case "credito":
                    fvSale.enableValidator('initial');
                    hideRowsVents([{'pos': 2, 'enable': true}]);
                select_paymentmethod.find('option[value="tarjeta_debito_credito"]').remove();
                    input_initial.prop('disabled', false)
                    $('.rowInitial').show();
                    break;
            }
        });

    select_paymentmethod.on('change', function () {
        updateOperationNumberVisibility();
    }).on('select2:select', function () {
        updateOperationNumberVisibility();
    }).on('select2:unselect', function () {
        updateOperationNumberVisibility();
    });

    function updateOperationNumberVisibility() {
        var id = select_paymentmethod.val();
        var isCredit = select_paymentcondition.val() === "credito";
        hideRowsVents([{'pos': 0, 'enable': false}, {'pos': 1, 'enable': false}, {'pos': 2, 'enable': isCredit}]);
        input_cash.val(input_cash.val());
        input_amountdebited.val('0.00');
        
        // Show/hide operation number and operation date fields for Yape, Plin, Transferencia and Depósito
        if (id === 'yape' || id === 'plin' || id === 'transferencia' || id === 'deposito') {
            $('#rowOperationNumber').show();
            fvSale.enableValidator('operation_number');
            $('#rowOperationDate').show();
            fvSale.enableValidator('operation_date');
        } else {
            $('#rowOperationNumber').hide();
            fvSale.disableValidator('operation_number');
            $('#rowOperationDate').hide();
            fvSale.disableValidator('operation_date');
        }

        // Show/hide payment bank field only for Transferencia and Depósito
        if (id === 'transferencia' || id === 'deposito' || id === 'yape') {
            $('#rowPaymentBank').show();
            fvSale.enableValidator('payment_bank');
            
            // Filter banks based on payment method
            filterBanksByMethod(id);
        } else {
            $('#rowPaymentBank').hide();
            fvSale.disableValidator('payment_bank');
            // Reset filter to show all banks when hiding
            resetBankFilter();
        }

        switch (id) {
            case "efectivo":
                fvSale.enableValidator('change');
                fvSale.disableValidator('card_number');
                fvSale.disableValidator('titular');
                fvSale.disableValidator('amount_debited');
                input_cash.trigger("touchspin.updatesettings", {max: 100000000});
                hideRowsVents([{'pos': 0, 'enable': true}]);
                
                break;
            case "yape":
            case "plin":
            case "transferencia":
            case "deposito":
                fvSale.disableValidator('change');
                fvSale.disableValidator('card_number');
                fvSale.disableValidator('titular');
                fvSale.disableValidator('amount_debited');
                break;
        }
    }

    function filterBanksByMethod(method) {
        console.log('Filtering banks for method:', method);
        // Keep the current selected bank value (if any)
        var currentValue = select_paymentbank.val();
        // Rebuild options from the cached original options to avoid Select2 inconsistencies
        var placeholder = original_bank_options.filter(function() { return $(this).val() === ''; });
        select_paymentbank.empty();
        if (placeholder.length) {
            select_paymentbank.append(placeholder.clone());
        }

        original_bank_options.each(function() {
            var opt = $(this);
            var val = opt.val();
            if (val === '') return; // skip placeholder (already added)
            var text = opt.text().toLowerCase();
            var keep = false;
            if (method === 'yape') {
                // Require both 'yape' and 'qr' present in the name (case-insensitive)
                keep = (text.indexOf('yape') !== -1 || text.indexOf('qr') !== -1);
            } else if (method === 'plin') {
                keep = (text.indexOf('plin') !== -1);
            } else if (method === 'transferencia' || method === 'deposito') {
                // Show all banks except those that are specific to Yape (contain 'yape' or 'qr')
                keep = !(text.indexOf('yape') !== -1 || text.indexOf('qr') !== -1);
            }
            if (keep) {
                select_paymentbank.append(opt.clone());
            }
        });

        // If the previously selected value is no longer present, clear selection
        if (currentValue && select_paymentbank.find('option[value="' + currentValue + '"]').length === 0) {
            select_paymentbank.val('').trigger('change');
        } else {
            // re-apply current value to keep it if still present
            select_paymentbank.val(currentValue).trigger('change');
        }
    }

    function resetBankFilter() {
        /**
         * Reset bank filter to show all options
         */
        // Restore original options and refresh Select2
        if (original_bank_options) {
            select_paymentbank.empty().append(original_bank_options.clone());
            select_paymentbank.val(select_paymentbank.find('option[value="' + select_paymentbank.val() + '"]').length ? select_paymentbank.val() : '').trigger('change');
        }
    }
    
    // Initial visibility check when page loads
    updateOperationNumberVisibility();
    input_initial.on('change', function() {
        console.log('Change event detected for input_initial');
    });
    input_cash
        .TouchSpin({
            min: 0.00,
            max: 100000000,
            step: 0.01,
            decimals: 2,
            boostat: 5,
            verticalbuttons: true,
            maxboostedstep: 10,
        })
        .off('change').on('change touchspin.on.min touchspin.on.max', function () {
        var paymentmethod = select_paymentmethod.val();
        fvSale.revalidateField('cash');
        var total = parseFloat(vents.details.total);
        switch (paymentmethod) {
            case "efectivo_tarjeta":
                fvSale.revalidateField('amount_debited');
                fvSale.revalidateField('change');
                //input_change.val('0.00');
                break;
            case "efectivo":
                var cash = parseFloat($(this).val());
                var change = cash - total;
                input_change.val(change.toFixed(2));
                fvSale.revalidateField('change');
                break;
        }
        return false;
    })
        .keypress(function (e) {
            return validate_decimals($(this), e);
        });

    input_cardnumber
        .on('keypress', function (e) {
            fvSale.revalidateField('card_number');
            return validate_form_text('numbers_spaceless', e, null);
        })
        .on('keyup', function (e) {
            var number = $(this).val();
            var number_nospaces = number.replace(/ /g, "");
            if (number_nospaces.length % 4 === 0 && number_nospaces.length > 0 && number_nospaces.length < 16) {
                number += ' ';
            }
            $(this).val(number);
        });

    input_titular.on('keypress', function (e) {
        return validate_form_text('letters', e, null);
    });

    input_endcredit.datetimepicker({
        useCurrent: false,
        format: 'YYYY-MM-DD',
        locale: 'es',
        keepOpen: false,
        minDate: current_date
    });

    input_endcredit.datetimepicker('date', input_endcredit.val());

    input_endcredit.on('change.datetimepicker', function (e) {
        fvSale.revalidateField('end_credit');
    });


    $('input[name="dscto"]')
        .TouchSpin({
            min: 0.00,
            max: 100,
            step: 0.01,
            decimals: 2,
            boostat: 5,
            verticalbuttons: true,
            maxboostedstep: 10,
        })
        .on('change touchspin.on.min touchspin.on.max', function () {
            var dscto = $(this).val();
            if (dscto === '') {
                $(this).val('0.00');
            }
            vents.calculate_invoice();
        })
        .keypress(function (e) {
            return validate_decimals($(this), e);
        });

    $('.btnProforma').on('click', function () {
        if (vents.details.products.length === 0) {
            message_error('Debe tener al menos un item en el detalle para poder crear una proforma');
            return false;
        }

        var parameters = {
            'action': 'create_proforma',
            'vents': JSON.stringify(vents.details)
        };

        $.ajax({
            url: pathname,
            data: parameters,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            xhrFields: {
                responseType: 'blob'
            },
            success: function (request) {
                if (!request.hasOwnProperty('error')) {
                    var d = new Date();
                    var date_now = d.getFullYear() + "_" + d.getMonth() + "_" + d.getDay();
                    var a = document.createElement("a");
                    document.body.appendChild(a);
                    a.style = "display: none";
                    const blob = new Blob([request], {type: 'application/pdf'});
                    const url = URL.createObjectURL(blob);
                    a.href = url;
                    a.download = "download_pdf_" + date_now + ".pdf";
                    a.click();
                    window.URL.revokeObjectURL(url);
                    return false;
                }
                message_error(request.error);
            },
            error: function (jqXHR, textStatus, errorThrown) {
                message_error(errorThrown + ' ' + textStatus);
            }
        });
    });

    hideRowsVents([{'pos': 0, 'enable': true}, {'pos': 1, 'enable': false}, {'pos': 2, 'enable': false}]);

    $('i[data-field="client"]').hide();
    $('i[data-field="searchproducts"]').hide();
});