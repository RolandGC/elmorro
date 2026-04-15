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

    // ── Destruir DataTable previa ────────────────────────────────────────
    if ($.fn.DataTable.isDataTable('#tblBoxSales')) {
        $('#tblBoxSales').DataTable().destroy();
        $('#tblBoxSales tbody').empty();
    }

    // ── Reconstruir thead y tfoot con las 11 columnas correctas ─────────
    // Esto resuelve el error "Cannot read properties of undefined (reading 'style')"
    // que ocurre cuando el thead/tfoot no coincide con las columnas del JS
    (function rebuildTableStructure() {
        const $tbl = $('#tblBoxSales');
        if (!$tbl.length) return;

        $tbl.find('thead').remove();
        $tbl.find('tfoot').remove();
        $tbl.find('tbody').empty();

        const cols = ['N°', 'Serie', 'Cliente', 'Fecha', 'Efectivo', 'Yape', 'Plin', 'Transferencia', 'Depósito', 'Total S/', 'Total $'];

        let thead = '<thead><tr>';
        cols.forEach(c => { thead += `<th>${c}</th>`; });
        thead += '</tr></thead>';

        let tfoot = '<tfoot><tr>';
        cols.forEach(() => { tfoot += '<th></th>'; });
        tfoot += '</tr></tfoot>';

        $tbl.append(thead).append('<tbody></tbody>').append(tfoot);
    })();

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

            // ── Helper: parsear número ────────────────────────────────────────
            const parseNum = v => {
                if (v === null || v === undefined) return 0;
                const n = parseFloat(String(v).replace(/,/g, '').replace(/[^0-9.\-]/g, ''));
                return isNaN(n) ? 0 : n;
            };

            // ── Resumen de caja ───────────────────────────────────────────────
            boxInfo.innerHTML = `
        <div class="row mb-2">
            <div class="col-md-6">
                <p class="mb-1"><strong>Cierre actual:</strong> ${box ? (box.datetime_close || '-') : '-'}</p>
                <p class="mb-1"><strong>Cierre previo:</strong> ${prev ? (prev.datetime_close || '-') : 'Sin cierre previo'}</p>
            </div>
        </div>`;

            // ── Claves y etiquetas de métodos ─────────────────────────────────
            const methodKeys = ['efectivo', 'yape', 'plin', 'transferencia', 'deposito'];
            const methodLabels = {
                efectivo: 'Efectivo',
                yape: 'Yape',
                plin: 'Plin',
                transferencia: 'Transferencia',
                deposito: 'Depósito'
            };

            // ── Acumuladores globales ─────────────────────────────────────────
            const methodTotals = {};
            const totals = {};
            const payments_cash_by_currency = {};
            const payments_non_cash_by_currency = {};

            methodKeys.forEach(k => methodTotals[k] = {});

            // ── Resolver a cuál método pertenece un pago ──────────────────────
            function resolveMethodKey(p) {
                const raw = (
                    p.payment_method?.code ||
                    p.payment_method?.name ||
                    ''
                ).toLowerCase().trim()
                    .normalize('NFD').replace(/[\u0300-\u036f]/g, '');

                if (raw === 'efectivo' || raw === 'cash') return 'efectivo';
                if (raw === 'yape') return 'yape';
                if (raw === 'plin') return 'plin';
                if (raw === 'transferencia' || raw === 'transfer') return 'transferencia';
                if (raw === 'deposito' || raw === 'deposit') return 'deposito';
                for (const key of methodKeys) {
                    if (raw.includes(key)) return key;
                }
                console.warn('resolveMethodKey: método desconocido →', p.payment_method);
                return 'deposito';
            }

            // ── Helper formato objeto moneda → texto ──────────────────────────
            const formatCurrencyObj = (obj, emptyText = '-') =>
                Object.keys(obj).length
                    ? Object.values(obj).map(i => `${i.symbol}${i.total.toFixed(2)}`).join('  |  ')
                    : emptyText;

            const formatSingleCurrencyTotal = (obj, codes) => {
                const key = Object.keys(obj).find(k => codes.includes(String(k || '').toUpperCase()));
                if (!key || !obj[key]) {
                    return '-';
                }
                return `${obj[key].symbol}${obj[key].total.toFixed(2)}`;
            };

            // ── Construir filas ───────────────────────────────────────────────
            const tableData = sales.map((s, idx) => {
                const clientName = s.client?.user?.full_name || s.client?.user?.fullName || '-';

                const perMethod = {};
                methodKeys.forEach(k => perMethod[k] = {});
                const saleCurrencyTotals = {};

                if (Array.isArray(s.payments)) {
                    s.payments.forEach(p => {
                        const amount = parseNum(p.amount);
                        const code = p.currency?.code || 'UNK';
                        const symbol = p.currency?.symbol || '';
                        const methodKey = resolveMethodKey(p);

                        if (!perMethod[methodKey][code])
                            perMethod[methodKey][code] = { symbol, total: 0 };
                        perMethod[methodKey][code].total += amount;

                        if (!saleCurrencyTotals[code])
                            saleCurrencyTotals[code] = { symbol, total: 0 };
                        saleCurrencyTotals[code].total += amount;

                        if (!methodTotals[methodKey][code])
                            methodTotals[methodKey][code] = { symbol, total: 0 };
                        methodTotals[methodKey][code].total += amount;

                        if (!totals[code]) totals[code] = { symbol, total: 0 };
                        totals[code].total += amount;

                        if (methodKey === 'efectivo') {
                            if (!payments_cash_by_currency[code])
                                payments_cash_by_currency[code] = { symbol, total: 0 };
                            payments_cash_by_currency[code].total += amount;
                        } else {
                            if (!payments_non_cash_by_currency[code])
                                payments_non_cash_by_currency[code] = { symbol, total: 0 };
                            payments_non_cash_by_currency[code].total += amount;
                        }
                    });
                }

                return [
                    idx + 1,
                    s.serie || '-',
                    clientName,
                    s.date_joined || '-',
                    formatCurrencyObj(perMethod['efectivo']),
                    formatCurrencyObj(perMethod['yape']),
                    formatCurrencyObj(perMethod['plin']),
                    formatCurrencyObj(perMethod['transferencia']),
                    formatCurrencyObj(perMethod['deposito']),
                    formatSingleCurrencyTotal(saleCurrencyTotals, ['PEN', 'SOL']),
                    formatSingleCurrencyTotal(saleCurrencyTotals, ['USD', 'DOL']),
                ];
            });

            // ── Badges totales globales ───────────────────────────────────────
            const totalsHtml = Object.entries(totals)
                .map(([code, it]) =>
                    `<span class="badge bg-secondary me-2">${code}: ${it.symbol}${it.total.toFixed(2)}</span>`)
                .join('');
            boxTotals.innerHTML = `<div class="mb-3"><strong>Totales por moneda:</strong> ${totalsHtml || '-'}</div>`;

            // ── Textos resumen para exports ───────────────────────────────────
            const resumenMethodsText = methodKeys
                .map(k => `${methodLabels[k]}: ${formatCurrencyObj(methodTotals[k], 'S/0.00')}`)
                .join('   |   ');
            const resumenEfectivoText = formatCurrencyObj(payments_cash_by_currency, 'S/0.00');
            const resumenBancosText = formatCurrencyObj(payments_non_cash_by_currency, 'S/0.00');

            // ── Logo → base64 ─────────────────────────────────────────────────
            const logoUrl = document.getElementById('exportLogo')?.src || '';
            function getBase64FromUrl(url) {
                return new Promise(resolve => {
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
                    img.onerror = () => resolve(null);
                    img.src = url;
                });
            }

            // ── Fila de totales para el PDF ───────────────────────────────────
            function buildPdfFooterRow(numCols) {
                const grandTotal = Object.values(methodTotals).reduce((acc, obj) => {
                    Object.entries(obj).forEach(([code, info]) => {
                        if (!acc[code]) acc[code] = { symbol: info.symbol, total: 0 };
                        acc[code].total += info.total;
                    });
                    return acc;
                }, {});

                const totalSoles = formatSingleCurrencyTotal(grandTotal, ['PEN', 'SOL']);
                const totalDolares = formatSingleCurrencyTotal(grandTotal, ['USD', 'DOL']);

                const valueMap = {
                    3: 'TOTALES',
                    4: formatCurrencyObj(methodTotals['efectivo'], ''),
                    5: formatCurrencyObj(methodTotals['yape'], ''),
                    6: formatCurrencyObj(methodTotals['plin'], ''),
                    7: formatCurrencyObj(methodTotals['transferencia'], ''),
                    8: formatCurrencyObj(methodTotals['deposito'], ''),
                    9: totalSoles,
                    10: totalDolares,
                };

                const cells = [];
                for (let i = 0; i < numCols; i++) {
                    cells.push({
                        text: valueMap[i] || '',
                        bold: true,
                        alignment: i >= 3 ? 'right' : 'left',
                        fillColor: '#d4edda',
                        color: '#155724',
                        fontSize: 8
                    });
                }
                return cells;
            }

            // ── Inicializar DataTable ─────────────────────────────────────────
            getBase64FromUrl(logoUrl).then(logoBase64 => {

                $('#tblBoxSales').DataTable({
                    destroy: true,
                    data: tableData,
                    scrollX: true,
                    dom: 'Bfrtip',
                    buttons: [
                        // ── Excel ──────────────────────────────────────────────
                        {
                            extend: 'excelHtml5',
                            text: '<i class="fas fa-file-excel"></i> Excel',
                            className: 'btn btn-success btn-sm',
                            title: `Reporte de Caja - ${box?.datetime_close || ''}`,
                            exportOptions: { columns: ':visible' },
                            customize: function (xlsx) {
                                try {
                                    const sheet = xlsx.xl.worksheets['sheet1.xml'];
                                    const downrows = 5;
                                    $('row', sheet).each(function () {
                                        $(this).attr('r', parseInt($(this).attr('r')) + downrows);
                                    });
                                    $('row c', sheet).each(function () {
                                        $(this).attr('r', $(this).attr('r').replace(/(\d+)/g, m => parseInt(m) + downrows));
                                    });
                                    const summary =
                                        `<row r="1"><c t="inlineStr" r="A1"><is><t>Resumen por Métodos: ${resumenMethodsText}</t></is></c></row>` +
                                        `<row r="2"><c t="inlineStr" r="A2"><is><t>Efectivo: ${resumenEfectivoText}</t></is></c></row>` +
                                        `<row r="3"><c t="inlineStr" r="A3"><is><t>Bancos / Digital: ${resumenBancosText}</t></is></c></row>` +
                                        `<row r="4"><c t="inlineStr" r="A4"><is><t></t></is></c></row>` +
                                        `<row r="5"><c t="inlineStr" r="A5"><is><t></t></is></c></row>`;
                                    $(sheet).find('sheetData').prepend(summary);
                                } catch (e) {
                                    console.warn('Excel customize failed', e);
                                }
                            }
                        },

                        // ── PDF ────────────────────────────────────────────────
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

                                function buildResumenLines(obj) {
                                    if (!Object.keys(obj).length)
                                        return [{ text: 'S/ 0.00', margin: [10, 0, 0, 2] }];
                                    return Object.values(obj).map(info => ({
                                        text: `${info.symbol} ${info.total.toFixed(2)}`,
                                        margin: [10, 0, 0, 2]
                                    }));
                                }

                                const resumenBlock = [
                                    //{ text: 'Resumen por Métodos:', style: 'subheader', margin: [0, 6, 0, 2] },
                                    //{ text: resumenMethodsText, margin: [10, 0, 0, 6] },
                                    //{ text: 'Efectivo:', style: 'subheader', margin: [0, 4, 0, 2] },
                                    //{ stack: buildResumenLines(payments_cash_by_currency) },
                                    //{ text: 'Bancos / Digital:', style: 'subheader', margin: [0, 4, 0, 2] },
                                    //{ stack: buildResumenLines(payments_non_cash_by_currency) },
                                    { text: ' ', margin: [0, 6, 0, 0] }
                                ];

                                const tableIndex = doc.content.findIndex(c => c && c.table);
                                if (tableIndex >= 0)
                                    doc.content.splice(tableIndex, 0, ...resumenBlock);
                                else
                                    doc.content.push(...resumenBlock);

                                // Fila de totales al pie de la tabla PDF
                                const tIdx = doc.content.findIndex(c => c && c.table);
                                if (tIdx >= 0) {
                                    const tableNode = doc.content[tIdx];
                                    const colCount = tableNode.table.body?.[0]?.length || 11;
                                    tableNode.table.body.push(buildPdfFooterRow(colCount));
                                    tableNode.table.widths = ['auto', 'auto', '*', 'auto', 'auto', 'auto', 'auto', 'auto', 'auto', 'auto', 'auto'];
                                    tableNode.layout = {
                                        hLineWidth: function (i, node) {
                                            return 0.5; // grosor horizontal
                                        },
                                        vLineWidth: function (i, node) {
                                            return 0.5; // grosor vertical
                                        },
                                        hLineColor: function (i, node) {
                                            return '#cccccc'; // color gris claro
                                        },
                                        vLineColor: function (i, node) {
                                            return '#cccccc'; // color gris claro
                                        },
                                        paddingLeft: function () { return 4; },
                                        paddingRight: function () { return 4; },
                                        paddingTop: function () { return 2; },
                                        paddingBottom: function () { return 2; }
                                    };
                                    // --- Resumen final: efectivo (Soles) - gastos (bills) y línea de firma ---
                                    try {
                                        // calcular efectivo en soles (todas las monedas que no sean USD)
                                        var cashObj = payments_cash_by_currency || {};
                                        var solesCash = 0;
                                        var usdCash = 0;
                                        Object.entries(cashObj).forEach(function(ent) {
                                            var code = ent[0];
                                            var info = ent[1];
                                            if (String(code).toUpperCase() === 'USD') usdCash += info.total;
                                            else solesCash += info.total;
                                        });
                                        var billsVal = 0;
                                        try { billsVal = parseFloat(box?.bills) || 0; } catch (e) { billsVal = 0; }
                                        var entregableSoles = solesCash - billsVal;

                                        var finalBlock = [
                                            { text: 'Resumen Final', style: 'subheader', margin: [0, 8, 0, 4] },
                                            { text: `Efectivo (Soles): S/ ${solesCash.toFixed(2)}`, margin: [0, 0, 0, 4] },
                                            
                                        ];
                                        if (usdCash > 0) {
                                            finalBlock.push({ text: `Egresos: S/ ${billsVal.toFixed(2)}`, margin: [0, 0, 0, 4] },)
                                        }
                                       
                                        finalBlock.push({ text: `TOTAL A ENTREGAR: S/ ${entregableSoles.toFixed(2)}`, bold: true, margin: [0, 0, 0, 8] },
                                            {
                                                columns: [
                                                    {
                                                        stack: [
                                                            { canvas: [{ type: 'line', x1: 250, y1: 0, x2: 100, y2: 0, lineWidth: 0.5 }], margin: [0, 10, 0, 6] },
                                                            { text: 'Firma Supervisor', alignment: 'center', margin: [0, 0, 0, 0] }
                                                        ],
                                                        width: '50%'
                                                    },
                                                    {
                                                        stack: [
                                                            { canvas: [{ type: 'line', x1: 250, y1: 0, x2: 100, y2: 0, lineWidth: 0.5 }], margin: [0, 10, 0, 6] },
                                                            { text: 'Firma Usuario', alignment: 'center', margin: [0, 0, 0, 0] }
                                                        ],
                                                        width: '50%'
                                                    }
                                                ],
                                                columnGap: 40,
                                                margin: [0, 40, 0, 10]
                                            })

                                        // insertar después de la tabla
                                        doc.content.splice(tIdx + 1, 0, ...finalBlock);
                                    } catch (e) {
                                        console.warn('No se pudo generar resumen final en PDF', e);
                                    }
                                }

                                doc.styles = doc.styles || {};
                                doc.styles.tableHeader = {
                                    ...(doc.styles.tableHeader || {}),
                                    fillColor: '#343a40',
                                    color: '#ffffff',
                                    fontSize: 8,
                                    bold: true
                                };
                                doc.defaultStyle = doc.defaultStyle || {};
                                doc.defaultStyle.fontSize = 7;
                            }
                        }
                    ],

                    columns: [
                        { title: 'N°' },
                        { title: 'Serie' },
                        { title: 'Cliente' },
                        { title: 'Fecha' },
                        { title: 'Efectivo' },
                        { title: 'Yape' },
                        { title: 'Plin' },
                        { title: 'Transferencia' },
                        { title: 'Depósito' },
                        { title: 'Total Soles' },
                        { title: 'Total Dólares' },
                    ],

                    // ── Footer HTML (sumatoria visible en pantalla) ───────────
                    footerCallback: function (row, data, start, end, display) {
                        try {
                            const api = this.api();
                            methodKeys.forEach((k, i) => {
                                $(api.column(4 + i).footer())
                                    .html(`<strong>${formatCurrencyObj(methodTotals[k], '-')}</strong>`);
                            });
                            const grand = Object.values(methodTotals).reduce((acc, obj) => {
                                Object.entries(obj).forEach(([code, info]) => {
                                    if (!acc[code]) acc[code] = { symbol: info.symbol, total: 0 };
                                    acc[code].total += info.total;
                                });
                                return acc;
                            }, {});
                            $(api.column(9).footer()).html(`<strong>${formatSingleCurrencyTotal(grand, ['PEN', 'SOL'])}</strong>`);
                            $(api.column(10).footer()).html(`<strong>${formatSingleCurrencyTotal(grand, ['USD', 'DOL'])}</strong>`);
                            $(api.column(3).footer()).html('<strong>TOTALES</strong>');
                        } catch (e) {
                            console.warn('footerCallback error', e);
                        }
                    },

                    // ── Idioma inline (evita error CORS del JSON externo) ─────
                    language: {
                        sProcessing: "Procesando...",
                        sLengthMenu: "Mostrar _MENU_ registros",
                        sZeroRecords: "No se encontraron resultados",
                        sEmptyTable: "Ningún dato disponible en esta tabla",
                        sInfo: "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
                        sInfoEmpty: "Mostrando registros del 0 al 0 de un total de 0 registros",
                        sInfoFiltered: "(filtrado de un total de _MAX_ registros)",
                        sSearch: "Buscar:",
                        sUrl: "",
                        oPaginate: {
                            sFirst: "Primero",
                            sLast: "Último",
                            sNext: "Siguiente",
                            sPrevious: "Anterior"
                        },
                        oAria: {
                            sSortAscending: ": Activar para ordenar de manera ascendente",
                            sSortDescending: ": Activar para ordenar de manera descendente"
                        }
                    }
                });
            });
        })
        .catch(err => {
            console.error('Error:', err);
            boxInfo.innerHTML = '<div class="alert alert-danger">Error al cargar los detalles.</div>';
        });
}