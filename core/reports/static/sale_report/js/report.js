var input_daterange;
var input_client;
var current_date;
var tblReport;
var columns = [];

function initTable() {
    tblReport = $('#tblReport').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
    });

    $.each(tblReport.settings()[0].aoColumns, function(key, value) {
        columns.push(value.sWidthOrig);
    });
}

function generateReport(all) {
    var parameters = {
        'action': 'search_report',
        'start_date': input_daterange.data('daterangepicker').startDate.format('YYYY-MM-DD'),
        'end_date': input_daterange.data('daterangepicker').endDate.format('YYYY-MM-DD'),
        'client_id': input_client.val() || '',
    };

    if (all) {
        parameters['start_date'] = '';
        parameters['end_date'] = '';
    }

    tblReport = $('#tblReport').DataTable({
        destroy: true,
        responsive: true,
        autoWidth: false,
        ajax: {
            url: pathname,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: parameters,
            dataSrc: ''
        },
        order: [
            [0, 'asc']
        ],
        paging: false,
        ordering: true,
        searching: false,
        dom: 'Bfrtip',
        buttons: [{
                extend: 'excelHtml5',
                text: 'Descargar Excel <i class="fas fa-file-excel"></i>',
                titleAttr: 'Excel',
                className: 'btn btn-success btn-flat btn-xs'
            },
            {
                extend: 'pdfHtml5',
                text: 'Descargar Pdf <i class="fas fa-file-pdf"></i>',
                titleAttr: 'PDF',
                className: 'btn btn-danger btn-flat btn-xs',
                download: 'open',
                orientation: 'landscape',
                pageSize: 'LEGAL',
                customize: function(doc) {
                    doc.styles = {
                        header: {
                            fontSize: 18,
                            bold: true,
                            alignment: 'center'
                        },
                        subheader: {
                            fontSize: 13,
                            bold: true
                        },
                        quote: {
                            italics: true
                        },
                        small: {
                            fontSize: 8
                        },
                        tableHeader: {
                            bold: true,
                            fontSize: 11,
                            color: 'white',
                            fillColor: '#2d4154',
                            alignment: 'center'
                        }
                    };
                    doc.content[1].table.widths = columns;
                    doc.content[1].margin = [0, 35, 0, 0];
                    doc.content[1].layout = {};
                    doc['footer'] = (function(page, pages) {
                        return {
                            columns: [{
                                    alignment: 'left',
                                    text: ['Fecha de creación: ', { text: current_date }]
                                },
                                {
                                    alignment: 'right',
                                    text: ['página ', { text: page.toString() }, ' de ', { text: pages.toString() }]
                                }
                            ],
                            margin: 20
                        }
                    });

                }
            },
            {
                text: 'Depósitos Excel <i class="fas fa-file-excel"></i>',
                titleAttr: 'Exportar depósitos a Excel',
                className: 'btn btn-success btn-flat btn-xs',
                action: function(e, dt, node, config) {
                    exportDeposits('excel');
                }
            },
            {
                text: 'Depósitos PDF <i class="fas fa-file-pdf"></i>',
                titleAttr: 'Exportar depósitos a PDF',
                className: 'btn btn-danger btn-flat btn-xs',
                action: function(e, dt, node, config) {
                    exportDeposits('pdf');
                }
            }
        ],
        columns: [
            { data: "serie" },
            { data: "client.user.full_name" },
            { data: "date_joined" },
            //{data: "payment_condition.name"},
            { data: "payment_method.name" },
            // {data: "subtotal"},
            //{data: "total_dscto"},
            //{data: "cantidad_productos"},
            {
                data: null,
                render: function(data, type, row) {
                    var productsList = row.sale_details.map(function(detail) {
                        return detail.product.name;
                    }).join(', ');
                    return productsList;
                }
            },
            { data: "comment" },
            { data: "total" },
        ],
        columnDefs: [{
            targets: [1, 2, 3, 4, 5],
            class: 'text-center',
            render: function(data, type, row) {
                return data;
            }
        }, {
            targets: [-1],
            orderable: false,
            class: 'text-center',
            render: function(data, type, row) {
                // Agrupar pagos por moneda
                var montosPorMoneda = {};
                if (row.payments && Array.isArray(row.payments)) {
                    $.each(row.payments, function(index, payment) {
                        var symbol = payment.currency.symbol;
                        var amount = parseFloat(payment.amount) || 0;
                        
                        if (!montosPorMoneda[symbol]) {
                            montosPorMoneda[symbol] = 0;
                        }
                        montosPorMoneda[symbol] += amount;
                    });
                }
                
                // Formatear como "S/ 20.00, $100.00"
                var resultado = [];
                $.each(montosPorMoneda, function(symbol, total) {
                    resultado.push(symbol + ' ' + parseFloat(total).toFixed(2));
                });
                
                return resultado.length > 0 ? resultado.join(', ') : 'S/. 0.00';
            }
        }],
        rowCallback: function(row, data, index) {

        },
        initComplete: function(settings, json) {

        },
    });
}

function exportDeposits(format) {
    var parameters = new FormData();
    parameters.append('action', 'export_deposits_' + format);
    parameters.append('start_date', input_daterange.data('daterangepicker').startDate.format('YYYY-MM-DD'));
    parameters.append('end_date', input_daterange.data('daterangepicker').endDate.format('YYYY-MM-DD'));
    parameters.append('client_id', input_client.val() || '');
    var selectedClient = input_client.select2('data');
    parameters.append('client_label', selectedClient.length ? selectedClient[0].text : '');

    $.ajax({
        url: pathname,
        type: 'POST',
        data: parameters,
        processData: false,
        contentType: false,
        headers: {
            'X-CSRFToken': csrftoken
        },
        xhrFields: {
            responseType: 'blob'
        },
        success: function(blob) {
            var url = URL.createObjectURL(blob);
            if (format === 'excel') {
                var a = document.createElement('a');
                a.href = url;
                a.download = 'depositos_' + moment().format('YYYYMMDD') + '.xlsx';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            } else {
                window.open(url, '_blank');
            }
            setTimeout(function() {
                URL.revokeObjectURL(url);
            }, 60000);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            message_error(errorThrown + ' ' + textStatus);
        }
    });
}

$(function() {

    current_date = new moment().format('YYYY-MM-DD');
    input_daterange = $('input[name="date_range"]');

    input_daterange
        .daterangepicker({
            language: 'auto',
            startDate: new Date(),
            locale: {
                format: 'YYYY-MM-DD',
            },
        });

    $('.drp-buttons').hide();

    input_client = $('select[name="client_id"]');
    input_client.select2({
        theme: 'bootstrap4',
        language: 'es',
        allowClear: true,
        placeholder: 'Todos los clientes',
        ajax: {
            delay: 250,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            url: pathname,
            data: function(params) {
                return {
                    term: params.term,
                    action: 'search_clients'
                };
            },
            processResults: function(data) {
                return {
                    results: data
                };
            },
            cache: true
        },
        minimumInputLength: 0,
    }).on('select2:select select2:clear', function() {
        generateReport(false);
    });

    initTable();

    generateReport(false);

    $('.btnSearchReport').on('click', function() {
        generateReport(false);
    });

    $('.btnSearchAll').on('click', function() {
        generateReport(true);
    });
});