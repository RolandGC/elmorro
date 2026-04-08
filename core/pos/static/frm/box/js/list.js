var tblPaymentsCtasCollect, tblCtasCollect, ctascollect;
var date_current;
var input_daterange;

function getData(all) {
    var parameters = {
        'action': 'search',
        'start_date': input_daterange.data('daterangepicker').startDate.format('YYYY-MM-DD'),
        'end_date': input_daterange.data('daterangepicker').endDate.format('YYYY-MM-DD'),
    };

    if (all) {
        parameters['start_date'] = '';
        parameters['end_date'] = '';
    }

    tblCtasCollect = $('#data').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        ajax: {
            url: pathname,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: parameters,
            dataSrc: ""
        },
        columns: [
            { data: "id" },
            { data: "datetime_close" },
            // { data: "efectivo_soles" },
            // { data: "efectivo_dolares" },
            // { data: "yape" },
            // { data: "plin" },
            // { data: "transferencia_soles" },
            // { data: "transferencia_dolares" },
            // { data: "deposito_soles" },
            { data: "user.full_name" },
            { data: "box_final_soles" },
            { data: "box_final_dolares" },
            { data: "bills" },
            { data: "desc" },
            { data: "options" },
        ],
        columnDefs: [{
                targets: [0],
                class: 'text-center',
                render: function(data, type, row) {
                    return data
                }
            },
            {
                targets: [1],
                class: 'text-center',
                render: function(data, type, row) {
                    return data
                }
            },
            {
                targets: [2],
                class: 'text-center',
                render: function(data, type, row) {
                    return  data
                }
            },
           
            {
                targets: [3],
                class: 'text-center',
                render: function(data, type, row) {
                    return 'S/.' + data
                }
            },
            {
                targets: [4],
                class: 'text-center',
                render: function(data, type, row) {
                    return '$' + data
                }
            },
            {
                targets: [5],
                class: 'text-center',
                render: function(data, type, row) {
                    return 'S/.' + data
                }
            },
            {
                targets: [6],
                render: function(data, type, row) {
                    return data || '-'
                }
            },
            {
                targets: [7],
                class: 'text-center',
                orderable: false,
                render: function(data, type, row) {
                    var buttons = '';
                    // detail / expand button to open payments modal (small screens)
                    buttons += '<a class="btn btn-info btn-xs btn-flat" rel="payments" onclick="showDetails(' + row.id + ')"><i class="fas fa-plus"></i></a> ';
                    buttons += '<a href="/pos/frm/box/print/ticket/' + row.id + '/" target="_blank" class="btn btn-primary btn-xs btn-flat"><i class="fas fa-print"></i></a> ';
                    buttons += '<a href="/pos/frm/box/update/' + row.id + '/" class="btn btn-warning btn-xs btn-flat"><i class="fas fa-edit"></i></a> ';
                    buttons += '<a href="/pos/frm/box/delete/' + row.id + '/" class="btn btn-danger btn-xs btn-flat"><i class="fas fa-trash"></i></a> ';
                    return buttons;
                }
            },


        ],
        rowCallback: function(row, data, index) {

        },
        initComplete: function(settings, json) {

        }
    });
}

$(function() {

    input_daterange = $('input[name="date_range"]');

    input_daterange
        .daterangepicker({
            language: 'auto',
            startDate: new Date(),
            locale: {
                format: 'YYYY-MM-DD',
            }
        })
        .on('apply.daterangepicker', function(ev, picker) {
            getData(false);
        });

    $('.drp-buttons').hide();

    getData(false);

    $('.btnSearch').on('click', function() {
        getData(false);
    });

    $('.btnSearchAll').on('click', function() {
        getData(true);
    });

    $(document).on('click', '#data a[rel="payments"]', function ()  {
            $('.tooltip').remove();
            var tr = tblCtasCollect.cell($(this).closest('td, li')).index(),
                row = tblCtasCollect.row(tr.row).data();
            tblPaymentsCtasCollect = $('#tblPayments').DataTable({
                // responsive: true,
                // autoWidth: false,
                destroy: true,
                searching: false,
                scrollX: true,
                scrollCollapse: true,
                ajax: {
                    url: pathname,
                    type: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    data: function(d) {
                        d.action = 'search_pays';
                        d.id = row.id;
                    },
                    dataSrc: ""
                },
                columns: [
                    { data: "id" },
                    { data: "hours_close" },
                    { data: "date_close" },
                    { data: "cash_sale" },
                    { data: "cash_credit" },
                    { data: "sale_card" },
                    { data: "initial_box" },
                    { data: "box_final" },
                    { data: "desc" },
                ],
                columnDefs: [{
                        targets: [0],
                        class: 'text-center',
                        render: function(data, type, row) {
                            return data
                        }
                    },
                    {
                        targets: [1],
                        class: 'text-center',
                        render: function(data, type, row) {
                            return data
                        }
                    },
                    {
                        targets: [2],
                        class: 'text-center',
                        render: function(data, type, row) {
                            return data
                        }
                    },
                    {
                        targets: [3],
                        class: 'text-center',
                        render: function(data, type, row) {
                            return data
                        }
                    },
                    {
                        targets: [4],
                        class: 'text-center',
                        render: function(data, type, row) {
                            return data
                        }
                    },
                    {
                        targets: [5],
                        class: 'text-center',
                        render: function(data, type, row) {
                            return data
                        }
                    },
                    {
                        targets: [6],
                        class: 'text-center',
                        render: function(data, type, row) {
                            return 'S/.' + data
                        }
                    },
                    {
                        targets: [7],
                        class: 'text-center',
                        render: function(data, type, row) {
                            return 'S/.' + data
                        }
                    },
                    {
                        targets: [-1],
                        class: 'text-center',
                        render: function(data, type, row) {
                            var buttons = '';
                            // print link similar to the expense list
                            buttons += '<a href="/pos/frm/expenses/print/ticket/' + row.id + '/" target="_blank" class="btn btn-primary btn-xs btn-flat"><i class="fas fa-print"></i></a> ';
                            buttons += '<a href="/pos/frm/expenses/update/' + row.id + '/" class="btn btn-warning btn-xs btn-flat"><i class="fas fa-edit"></i></a> ';
                            buttons += '<a href="/pos/frm/expenses/delete/' + row.id + '/" class="btn btn-danger btn-xs btn-flat"><i class="fas fa-trash"></i></a> ';
                            return buttons;
                        }
                    },

                ],
                rowCallback: function(row, data, index) {

                },
                initComplete: function(settings, json) {

                }
            });
            $('#myModalPayments').modal('show');
        });

    $('#tblPayments tbody')
        .off()
        .on('click', 'a[rel="delete"]', function() {
            $('.tooltip').remove();
            var tr = tblPaymentsCtasCollect.cell($(this).closest('td, li')).index(),
                row = tblPaymentsCtasCollect.row(tr.row).data();
            submit_with_ajax('Notificación',
                '¿Estas seguro de eliminar el registro?',
                pathname, {
                    'id': row.id,
                    'action': 'delete_pay'
                },
                function() {
                    tblCtasCollect = tblCtasCollect.ajax.reload();
                    tblPaymentsCtasCollect.ajax.reload();
                }
            );
        });
});

function showDetails(idBox) {
    console.log('showDetails', idBox);
    const miModalDetails = document.getElementById('myModalDetails');
    if (!miModalDetails) return;

    const modal = new bootstrap.Modal(miModalDetails);
    const boxInfo = document.getElementById('boxInfo');
    const boxTotals = document.getElementById('boxTotals');
    boxInfo.innerHTML = '<p>Cargando...</p>';
    boxTotals.innerHTML = '';
    modal.show();

    // Destruir DataTable previa si existe
    if ($.fn.DataTable.isDataTable('#tblBoxSales')) {
        $('#tblBoxSales').DataTable().destroy();
        $('#tblBoxSales tbody').empty();
    }

    fetch(`/pos/frm/box/${idBox}/sales-range/`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    })
        .then(r => { if (!r.ok) throw new Error('Network error'); return r.json(); })
        .then(data => {
            if (data.error) {
                boxInfo.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                return;
            }

            const box = data.box || null;
            const prev = data.previous_box || null;
            const sales = Array.isArray(data.sales) ? data.sales : [];

            const parseNum = v => {
                if (v === null || v === undefined) return 0;
                const n = parseFloat(String(v).replace(/,/g, '').replace(/[^0-9.\-]/g, ''));
                return isNaN(n) ? 0 : n;
            };

            // ── Resumen de caja ──────────────────────────────────────────
            boxInfo.innerHTML = `
            <div class="row mb-2">
                <div class="col-md-6">
                    <p class="mb-1"><strong>Cierre actual:</strong> ${box ? (box.datetime_close || '-') : '-'}</p>
                    <p class="mb-1"><strong>Cierre previo:</strong> ${prev ? (prev.datetime_close || '-') : 'Sin cierre previo'}</p>
                </div>
            </div>`;

            // ── Totales por moneda y resúmenes (efectivo / bancos) ───────
            const totals = {};
            const payments_cash_by_currency = {};
            const payments_non_cash_by_currency = {};
            const cashMethods = ['efectivo']; // solo 'efectivo' se considera efectivo
            const bankMethods = ['yape', 'plin', 'transferencia', 'deposito']; // estos los tratamos como bancos

            sales.forEach(sale => {
                if (Array.isArray(sale.payments)) {
                    sale.payments.forEach(p => {
                        const code = p.currency?.code || 'UNK';
                        const symbol = p.currency?.symbol || '';
                        const amount = parseNum(p.amount);

                        if (!totals[code]) totals[code] = { symbol, total: 0 };
                        totals[code].total += amount;

                        const methodCode = (p.payment_method && p.payment_method.code) ? String(p.payment_method.code).toLowerCase() : (p.payment_method && p.payment_method.name ? String(p.payment_method.name).toLowerCase() : '');
                        let classifiedAsCash = false;
                        let classifiedAsBank = false;
                        if (cashMethods.includes(methodCode) || methodCode === 'efectivo' || methodCode === 'cash') classifiedAsCash = true;
                        if (bankMethods.includes(methodCode) || methodCode === 'yape' || methodCode === 'plin' || methodCode === 'transferencia' || methodCode === 'deposito') classifiedAsBank = true;

                        if (classifiedAsCash) {
                            if (!payments_cash_by_currency[code]) payments_cash_by_currency[code] = { symbol, total: 0 };
                            payments_cash_by_currency[code].total += amount;
                        } else {
                            // cualquier otro medio (incluyendo tarjetas, transferencias, plin, yape, deposito) se considera dentro de 'bancos/non-cash'
                            if (!payments_non_cash_by_currency[code]) payments_non_cash_by_currency[code] = { symbol, total: 0 };
                            payments_non_cash_by_currency[code].total += amount;
                        }
                    });
                }
            });

            const totalsHtml = Object.entries(totals).map(([code, it]) =>
                `<span class="badge bg-secondary me-2">${code}: ${it.symbol}${it.total.toFixed(2)}</span>`
            ).join('');
            boxTotals.innerHTML = `<div class="mb-3"><strong>Totales por moneda:</strong> ${totalsHtml || '-'}</div>`;

            // preparar textos para export
            const resumenEfectivoLines = Object.entries(payments_cash_by_currency).map(([code, info]) => `${info.symbol} ${info.symbol} ${info.total.toFixed(2)}`);
            const resumenBancosLines = Object.entries(payments_non_cash_by_currency).map(([code, info]) => `${info.symbol} ${info.total.toFixed(2)}`);
            const resumenEfectivoText = resumenEfectivoLines.length ? resumenEfectivoLines.join(' — ') : 'S/. 0.00';
            const resumenBancosText = resumenBancosLines.length ? resumenBancosLines.join(' — ') : 'S/. 0.00';

            // ── Filas para DataTable ─────────────────────────────────────
            const tableData = sales.map((s, i) => {
                const clientName = s.client?.user?.full_name || s.client?.user?.fullName || '-';
                const paymentsByCurrency = {};
                if (Array.isArray(s.payments)) {
                    s.payments.forEach(p => {
                        const sym = p.currency?.symbol || p.currency?.code || '';
                        paymentsByCurrency[sym] = (paymentsByCurrency[sym] || 0) + parseNum(p.amount);
                    });
                }
                const paymentsDisplay = Object.entries(paymentsByCurrency)
                    .map(([sym, amt]) => `${sym}${amt.toFixed(2)}`).join(', ') || '-';
                const paymentMethod = s.payment_method?.name || '-';

                return [
                    i + 1,
                    s.serie || '-',
                    clientName,
                    s.date_joined || '-',
                    paymentMethod,
                    paymentsDisplay,
                ];
            });

            // ── Inicializar DataTable con botones Export ─────────────────
            // ── Inicializar DataTable con botones Export ─────────────────
            const logoUrl = document.getElementById('exportLogo')?.src || '';

            // Convertir logo a base64 primero
            function getBase64FromUrl(url) {
                return new Promise((resolve) => {
                    if (!url) return resolve(null);
                    const img = new Image();
                    img.crossOrigin = 'Anonymous';
                    img.onload = function () {
                        const canvas = document.createElement('canvas');
                        canvas.width = img.width;
                        canvas.height = img.height;
                        canvas.getContext('2d').drawImage(img, 0, 0);
                        resolve(canvas.toDataURL('image/png'));
                    };
                    img.onerror = () => resolve(null); // si falla, continuar sin logo
                    img.src = url;
                });
            }

            getBase64FromUrl(logoUrl).then(logoBase64 => {
                $('#tblBoxSales').DataTable({
                    destroy: true,
                    data: tableData,
                    scrollX: true,
                    dom: 'Bfrtip',
                    buttons: [
                        {
                            extend: 'excelHtml5',
                            text: '<i class="fas fa-file-excel"></i> Excel',
                            className: 'btn btn-success btn-sm',
                            title: `Reporte de Caja - ${box?.datetime_close || ''}`,
                            exportOptions: { columns: ':visible' },
                            customize: function(xlsx) {
                                try {
                                    var sheet = xlsx.xl.worksheets['sheet1.xml'];
                                    var downrows = 3; // filas de resumen a insertar
                                    var clRow = $('row', sheet);
                                    clRow.each(function() {
                                        var attr = $(this).attr('r');
                                        var ind = parseInt(attr);
                                        $(this).attr('r', ind + downrows);
                                    });
                                    $('row c', sheet).each(function() {
                                        var r = $(this).attr('r');
                                        var cell = r.replace(/(\d+)/g, function(m) { return parseInt(m) + downrows; });
                                        $(this).attr('r', cell);
                                    });
                                    var summary = '';
                                    summary += '<row r="1"><c t="inlineStr" r="A1"><is><t>Resumen Efectivo: ' + resumenEfectivoText + '</t></is></c></row>';
                                    summary += '<row r="2"><c t="inlineStr" r="A2"><is><t>Resumen Bancos: ' + resumenBancosText + '</t></is></c></row>';
                                    summary += '<row r="3"><c t="inlineStr" r="A3"><is><t></t></is></c></row>';
                                    $(sheet).find('sheetData').prepend(summary);
                                } catch (e) {
                                    console.warn('Excel customize failed', e);
                                }
                            }
                        },
                        {
                            extend: 'pdfHtml5',
                            text: '<i class="fas fa-file-pdf"></i> PDF',
                            className: 'btn btn-danger btn-sm',
                            title: `Reporte de Caja - ${box?.datetime_close || ''}`,
                            orientation: 'landscape',
                            pageSize: 'A4',
                            exportOptions: { columns: ':visible' },
                            customize: function (doc) {
                                if (logoBase64) {
                                    doc.content.unshift({
                                        image: logoBase64,
                                        width: 80,
                                        margin: [0, 0, 0, 6]
                                    });
                                }
                                // insertar resumen arriba de la tabla
                                var tableIndex = -1;
                                for (var i = 0; i < doc.content.length; i++) {
                                    if (doc.content[i] && doc.content[i].table) { tableIndex = i; break; }
                                }
                                function buildResumenLines(obj) {
                                    let lines = [];

                                    Object.entries(obj).forEach(([code, info]) => {
                                        let label = code === 'USD' ? 'Dólares:' : 'Soles:';
                                        lines.push({
                                            text: `${label}    ${info.symbol} ${info.total.toFixed(2)}`,
                                            margin: [10, 0, 0, 2]
                                        });
                                    });

                                    if (lines.length === 0) {
                                        lines.push({
                                            text: 'Soles:    S/ 0.00',
                                            margin: [10, 0, 0, 2]
                                        });
                                    }

                                    return lines;
                                }

                                var resumenBlock = [
                                    { text: 'Resumen Efectivo:', style: 'subheader', margin: [0, 6, 0, 2] },
                                    {
                                        stack: buildResumenLines(payments_cash_by_currency)
                                    },

                                    { text: 'Resumen Bancos:', style: 'subheader', margin: [0, 8, 0, 2] },
                                    {
                                        stack: buildResumenLines(payments_non_cash_by_currency)
                                    }
                                ];
                                if (tableIndex >= 0) {
                                    doc.content.splice(tableIndex, 0, ...resumenBlock);
                                } else {
                                    doc.content.push(...resumenBlock);
                                }
                                doc.styles = doc.styles || {};
                                doc.styles.tableHeader = doc.styles.tableHeader || {};
                                doc.styles.tableHeader.fillColor = '#343a40';
                                doc.styles.tableHeader.color = '#ffffff';
                            }
                        }
                    ],
                    columns: [
                        { title: 'N°' },
                        { title: 'Serie' },
                        { title: 'Cliente' },
                        { title: 'Fecha' },
                        { title: 'Forma de Pago' },
                        { title: 'Total' },
                    ],
                    language: {
                        url: '//cdn.datatables.net/plug-ins/1.10.25/i18n/Spanish.json'
                    }
                });
            });
        })
        .catch(err => {
            console.error('Error:', err);
            boxInfo.innerHTML = '<div class="alert alert-danger">Error al cargar los detalles.</div>';
        });
}