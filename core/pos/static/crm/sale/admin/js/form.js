var current_date;

var fvSale;
var fvClient;

var select_client;
var input_birthdate;
var select_paymentcondition;
var input_cash;
let input_initial;
var input_cardnumber;
var input_titular;
var input_change;
var input_amount;
var amount_user_edited = false;
var total_user_edited = false;
var paymentBlockCounter = 0;

var tblSearchProducts;
var tblProducts;

var input_searchproducts;
var input_endcredit;
var inputs_vents;

var lastClickedButtonId;

// Company exchange rate provided by template (exposed as window.companyExchangeRate)
var companyExchangeRate = (typeof window.companyExchangeRate !== 'undefined') ? parseFloat(window.companyExchangeRate) : 1.0;

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
                //{data: "subtotal"},
                //{data: "total"},
            ],
            columnDefs: [
                // {
                //     targets: [-1],
                //     class: 'text-center',
                //     render: function (data, type, row) {
                //         return 'S/.' + safeToFixed(data, 2);
                //     }
                // },
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
        var total = parseFloat(vents.details.total);

        if (cash < total) {
            return {valid: false, message: 'El efectivo debe ser mayor o igual al total a pagar'};
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
            var totalVal = parseFloat($('input[name="total"]').val());
            parameters.append('action', $('input[name="action"]').val());
            // Recoger datos de bloques de pago dinámicos
            var paymentsArray = [];
            $('.payment-block').each(function () {
                var block = $(this);
                var rawAmount = block.find('.payment-amount').val();
                var amount = '0.00';
                if (typeof rawAmount !== 'undefined' && rawAmount !== null && String(rawAmount).toLowerCase() !== 'undefined' && String(rawAmount).trim() !== '') {
                    // sanitize numeric string; fallback to 0.00 if invalid
                    var parsed = parseFloat(rawAmount);
                    amount = !isNaN(parsed) ? String(rawAmount) : '0.00';
                }
                var method = block.find('.payment-method-select').val();
                var currency = block.find('.payment-currency-select').val();
                var bank = block.find('.payment-bank-select').val();
                var operation = block.find('.payment-operation').val();
                if (method && currency && parseFloat(amount) > 0) {
                    paymentsArray.push({
                        amount: amount,
                        payment_method: method,
                        currency: currency,
                        bank: bank || '',
                        operation_number: operation || ''
                    });
                }
            });
            parameters.append('payments', JSON.stringify(paymentsArray));
            parameters.append('payment_condition', select_paymentcondition.val());
            parameters.append('end_credit', input_endcredit.val());
            parameters.append('cash', input_cash.val());
            parameters.append('change', input_change.val() || '0.00');
            parameters.append('card_number', input_cardnumber.val());
            parameters.append('titular', input_titular.val());
            parameters.append('initial', input_initial.val());
            parameters.append('dscto', $('input[name="dscto"]').val() || '0.00');

            // Agregar el total ingresado por el usuario
            parameters.set('total', !isNaN(totalVal) ? totalVal.toFixed(2) : '0.00');

            // attach date_joined (supports datetime-local input)
            var date_joined_val = $('input[name="date_joined"]').val() || $('#date_joined').val() || $('#id_date_joined').val() || '';
            parameters.append('date_joined', date_joined_val);
            console.log('date_joined sent:', date_joined_val);
            console.log('total sent:', $('input[name="total"]').val());
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
                //{data: "pvp"},
                //{data: "price_promotion"},
                //{data: "stock"},
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
                // {
                //     targets: [2],
                //     class: 'text-center',
                //     render: function (data, type, row) {
                //         return 'S/.' + parseFloat(data).toFixed(2);
                //     }
                // },
                // {
                //     targets: [3],
                //     class: 'text-center',
                //     render: function (data, type, row) {
                //         return 'S/.' + parseFloat(data).toFixed(2);
                //     }
                // },
                // {
                //     targets: [4],
                //     class: 'text-center',
                //     render: function (data, type, row) {
                //         if (row.category.inventoried) {
                //             if (row.stock > 0) {
                //                 return '<span class="badge badge-success">' + row.stock + '</span>';
                //             }
                //             return '<span class="badge badge-danger">' + row.stock + '</span>';
                //         }
                //         return '<span class="badge badge-secondary">Sin stock</span>';
                //     }
                // },
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
            fvSale.disableValidator('cash');
            fvSale.disableValidator('change');
            switch (id) {
                case "contado":
                    fvSale.disableValidator('end_credit');
                    input_initial.prop('disabled', true)
                    $('.rowInitial').hide();
                    hideRowsVents([{'pos': 0, 'enable': true}]);
                    break;
                case "credito":
                    fvSale.enableValidator('initial');
                    hideRowsVents([{'pos': 2, 'enable': true}]);
                    input_initial.prop('disabled', false)
                    $('.rowInitial').show();
                    break;
            }
        });

    // --- Bloques dinámicos de pago ---
    function addPaymentBlock() {
        paymentBlockCounter++;
        var template = document.getElementById('paymentBlockTemplate');
        var html = template.innerHTML.replace(/__INDEX__/g, paymentBlockCounter);
        $('#paymentsContainer').append(html);

        var block = $('#paymentsContainer .payment-block').last();

        // Poblar select de formas de pago
        var methodSelect = block.find('.payment-method-select');
        if (typeof paymentMethodsData !== 'undefined') {
            $.each(paymentMethodsData, function (i, pm) {
                methodSelect.append('<option value="' + pm.id + '">' + pm.name + '</option>');
            });
        }

        // Poblar select de monedas
        var currencySelect = block.find('.payment-currency-select');
        if (typeof currenciesData !== 'undefined') {
            $.each(currenciesData, function (i, c) {
                currencySelect.append('<option value="' + c.id + '">' + c.name + ' (' + c.symbol + ')</option>');
            });
            // Si solo hay una moneda, seleccionarla por defecto
            if (currenciesData.length === 1) {
                currencySelect.val(currenciesData[0].id);
            }
        }

        // Poblar select de bancos
        var bankSelect = block.find('.payment-bank-select');
        if (typeof paymentBanksData !== 'undefined') {
            $.each(paymentBanksData, function (i, b) {
                bankSelect.append('<option value="' + b.id + '">' + b.name + '</option>');
            });
        }

        // Poblar select de monedas equivalentes (para la entrada visual)
        var eqCurrencySelect = block.find('.payment-eq-currency-select');
        if (typeof currenciesData !== 'undefined') {
            $.each(currenciesData, function (i, c) {
                eqCurrencySelect.append('<option value="' + c.id + '" data-code="' + c.code + '">' + c.name + ' (' + c.symbol + ')</option>');
            });
            if (currenciesData.length === 1) {
                eqCurrencySelect.val(currenciesData[0].id);
            }
        }
        // Si cambia la moneda (primaria o equivalente), poner montos a cero si ya hay números
        // y seleccionar automáticamente la moneda opuesta
        block.find('.payment-currency-select').on('change', function () {
            var selectedCurrencyId = $(this).val();
            var eqCurrencySelect = block.find('.payment-eq-currency-select');
            
            // Si se selecciona una moneda, seleccionar la opuesta automáticamente
            if (selectedCurrencyId && typeof currenciesData !== 'undefined' && currenciesData.length > 1) {
                var selectedCurrency = currenciesData.find(c => String(c.id) === String(selectedCurrencyId));
                if (selectedCurrency) {
                    // Buscar la moneda opuesta
                    var selectedCode = String(selectedCurrency.code).toUpperCase();
                    var isLocal = (selectedCode === 'PEN' || selectedCode === 'SOL' || selectedCode === 'S/');
                    
                    // Buscar una moneda diferente (opuesta)
                    var oppositeCurrency = currenciesData.find(function(c) {
                        var code = String(c.code).toUpperCase();
                        var isOppLocal = (code === 'PEN' || code === 'SOL' || code === 'S/');
                        return isOppLocal !== isLocal;
                    });
                    
                    if (oppositeCurrency) {
                        eqCurrencySelect.val(oppositeCurrency.id);
                    }
                }
            }
            
            var currentAmt = parseFloat(block.find('.payment-amount').val()) || 0;
            var currentEq = parseFloat(block.find('.payment-amount-equiv').val()) || 0;
            if (currentAmt > 0 || currentEq > 0) {
                block.find('.payment-amount').val('0.00');
                block.find('.payment-amount-equiv').val('0.00');
                recalcPaymentsTotal();
            }
        });
        
        block.find('.payment-eq-currency-select').on('change', function () {
            var currentAmt = parseFloat(block.find('.payment-amount').val()) || 0;
            var currentEq = parseFloat(block.find('.payment-amount-equiv').val()) || 0;
            if (currentAmt > 0 || currentEq > 0) {
                block.find('.payment-amount').val('0.00');
                block.find('.payment-amount-equiv').val('0.00');
                recalcPaymentsTotal();
            }
        });
        
        // Listener para mostrar/ocultar campos de Banco y Nro Operación según forma de pago
        block.find('.payment-method-select').on('change', function () {
            var selectedMethodId = $(this).val();
            var optionalFields = block.find('.payment-optional-field');
            
            // Si es efectivo (id=1), ocultar campos de banco y operación
            if (String(selectedMethodId) === '1') {
                optionalFields.hide();
            } else {
                optionalFields.show();
            }
        });

        // Listener para el input visual equivalente: convierte a monto original y actualiza el campo guardado
        block.find('.payment-amount-equiv').on('input change', function () {
            var equivVal = parseFloat($(this).val()) || 0;
            var primaryCurrencyId = block.find('.payment-currency-select').val();
            var eqCurrencyId = block.find('.payment-eq-currency-select').val();
            // Encontrar códigos
            var primary = (typeof currenciesData !== 'undefined') ? currenciesData.find(x => String(x.id) === String(primaryCurrencyId)) : null;
            var equiv = (typeof currenciesData !== 'undefined') ? currenciesData.find(x => String(x.id) === String(eqCurrencyId)) : null;
            var rate = typeof companyExchangeRate !== 'undefined' ? parseFloat(companyExchangeRate) : 1;
            var computed = equivVal;
            console.log('ratessee', rate)
            try {
                // Si no hay moneda primaria seleccionada, asumimos que la entrada equiv es igual a la original
                if (!primary || !equiv) {
                    computed = equivVal;
                } else if (String(primary.code).toUpperCase() === String(equiv.code).toUpperCase()) {
                    computed = equivVal;
                } else {
                    // Si primary es moneda local (p.ej. PEN) y equiv es extranjera (p.ej. USD): original = equiv * rate
                    // Si primary es extranjera y equiv es local: original = equiv / rate
                    // Intentamos inferir con códigos comunes
                    var primaryCode = String(primary.code).toUpperCase();
                    var equivCode = String(equiv.code).toUpperCase();
                    // Heurística: si primary is PEN or S/ treat as local
                    if ((primaryCode === 'PEN' || primaryCode === 'SOL' || primaryCode === 'S/') && equivCode !== primaryCode) {
                        computed = equivVal * rate;
                    } else if ((equivCode === 'PEN' || equivCode === 'SOL' || equivCode === 'S/') && primaryCode !== equivCode) {
                        computed = equivVal / rate;
                    } else {
                        // Fallback: multiply by rate
                        computed = equivVal * rate;
                    }
                }
            } catch (err) {
                computed = equivVal;
            }
            // poner computed en el campo pay_amount (valor exacto sin redondeo)
            block.find('.payment-amount').val(String(computed)).trigger('change');
            recalcPaymentsTotal();
        });

        // También sincronizar cuando cambie el monto original para actualizar el equivalente (inversa)
        block.find('.payment-amount').on('input change', function () {
            var orig = parseFloat($(this).val()) || 0;
            var primaryCurrencyId = block.find('.payment-currency-select').val();
            var eqCurrencyId = block.find('.payment-eq-currency-select').val();
            var primary = (typeof currenciesData !== 'undefined') ? currenciesData.find(x => String(x.id) === String(primaryCurrencyId)) : null;
            var equiv = (typeof currenciesData !== 'undefined') ? currenciesData.find(x => String(x.id) === String(eqCurrencyId)) : null;
            var rate = typeof companyExchangeRate !== 'undefined' ? parseFloat(companyExchangeRate) : 1;
            var computedEq = orig;
            if (!primary || !equiv) {
                computedEq = orig;
            } else if (String(primary.code).toUpperCase() === String(equiv.code).toUpperCase()) {
                computedEq = orig;
            } else {
                var primaryCode = String(primary.code).toUpperCase();
                var equivCode = String(equiv.code).toUpperCase();
                if ((primaryCode === 'PEN' || primaryCode === 'SOL' || primaryCode === 'S/') && equivCode !== primaryCode) {
                    // orig is local, equiv = orig / rate
                    computedEq = orig / rate;
                } else if ((equivCode === 'PEN' || equivCode === 'SOL' || equivCode === 'S/') && primaryCode !== equivCode) {
                    // orig is foreign, equiv = orig * rate
                    computedEq = orig * rate;
                } else {
                    computedEq = orig / rate;
                }
            }
            block.find('.payment-amount-equiv').val(String(computedEq));
            recalcPaymentsTotal();
        });

        // Listener para recalcular total de pagos
        block.find('.payment-amount').on('input change', function () {
            recalcPaymentsTotal();
        });

        return block;
    }

    function recalcPaymentsTotal() {
        var sum = 0;
        $('.payment-block .payment-amount').each(function () {
            var val = parseFloat($(this).val());
            if (!isNaN(val)) sum += val;
        });
        // mantener el valor exacto sin redondear
        $('input[name="total"]').val(String(sum));
        $('input[name="amount"]').val(String(sum));
        $('input[name="subtotal"]').val(String(sum));
        vents.details.subtotal = sum;
        vents.details.total = sum;
        amount_user_edited = true;
        total_user_edited = true;
    }

    $('#btnAddPayment').on('click', function () {
        addPaymentBlock();
    });

    $(document).on('click', '.btnRemovePayment', function () {
        $(this).closest('.payment-block').remove();
        // Renumerar bloques
        $('.payment-block').each(function (i) {
            $(this).find('.payment-number').text(i + 1);
        });
        recalcPaymentsTotal();
    });
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
        fvSale.revalidateField('cash');
        var total = parseFloat(vents.details.total);
        var cash = parseFloat($(this).val());
        var change = cash - total;
        input_change.val(change.toFixed(2));
        try { fvSale.revalidateField('change'); } catch (e) {}
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

    // Precarga de datos para edición
    if (window.saleDataForEdit) {
        var saleData = window.saleDataForEdit;
        console.log('=== PRECARGA EDICIÓN ===');

        // Cargar cliente en select2
        if (saleData.client && saleData.client.id) {
            var clientText = saleData.client.user.full_name + ' / ' + saleData.client.user.dni;
            var newOption = new Option(clientText, saleData.client.id, true, true);
            select_client.append(newOption).trigger('change');
        }

        // Cargar tipo de comprobante (sin trigger para evitar errores de FormValidation)
        if (saleData.type_voucher && saleData.type_voucher.id) {
            $('select[name="type_voucher"]').val(saleData.type_voucher.id);
        }

        // Cargar productos desde sale_details
        if (saleData.sale_details && saleData.sale_details.length > 0) {
            $.each(saleData.sale_details, function (i, det) {
                var product = det.product;
                product.cant = det.cant;
                product.price_current = det.price;
                product.dscto = det.dscto;
                vents.details.products.push(product);
            });
            vents.list_products();
        }

        // Cargar bloques de pago
        if (saleData.payments && saleData.payments.length > 0) {
            $.each(saleData.payments, function (i, payment) {
                var block = addPaymentBlock();
                block.find('.payment-currency-select').val(payment.currency.id).trigger('change');
                block.find('.payment-method-select').val(payment.payment_method.id).trigger('change');
                block.find('.payment-amount').val(payment.amount);
                if (payment.bank && payment.bank.id) {
                    block.find('.payment-bank-select').val(payment.bank.id);
                }
                if (payment.operation_number) {
                    block.find('.payment-operation').val(payment.operation_number);
                }
            });
            recalcPaymentsTotal();
        }

        // Cargar total y amount
        $('input[name="total"]').val(saleData.total);
        $('input[name="amount"]').val(saleData.total);
        total_user_edited = true;
        amount_user_edited = true;

        // Cargar comentario
        $('textarea[name="comment"]').val(saleData.comment || '');

        // Cargar fecha (convertir de DD/MM/YYYY HH:MM a YYYY-MM-DDTHH:MM)
        if (saleData.date_joined) {
            var parts = saleData.date_joined.match(/(\d{2})\/(\d{2})\/(\d{4})\s(\d{2}):(\d{2})/);
            if (parts) {
                var isoDate = parts[3] + '-' + parts[2] + '-' + parts[1] + 'T' + parts[4] + ':' + parts[5];
                $('input[name="date_joined"]').val(isoDate);
            }
        }

        // Cargar campos de crédito si aplica
        if (saleData.payment_condition.id === 'credito') {
            input_endcredit.val(saleData.end_credit);
            input_initial.val(saleData.initial);
        }

        // Cargar condición de pago AL FINAL con setTimeout para que FormValidation ya esté listo
        setTimeout(function () {
            if (saleData.payment_condition && saleData.payment_condition.id) {
                select_paymentcondition.val(saleData.payment_condition.id).trigger('change');
            }
        }, 100);
    }
});