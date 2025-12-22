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
            {data: "id"},
            {data: "hours_close"},
            {data: "date_close"},
            {data: "cash_sale"},
            // {data: "cash_credit"},
            {data: "sale_card"},
            {data: "initial_box"},
            {data: "box_final"},
            {data: "desc"},
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
                    return data
                }
            },
            {
                targets: [3],
                class: 'text-center',
                render: function (data, type, row) {
                    return data
                }
            },
            {
                targets: [4],
                class: 'text-center',
                render: function (data, type, row) {
                    return data
                }
            },
            {
                targets: [5],
                class: 'text-center',
                render: function (data, type, row) {
                    return data
                }
            },
            {
                targets: [6],
                class: 'text-center',
                render: function (data, type, row) {
                    return 'S/.' + data
                }
            },
            {
                targets: [-1],
                class: 'text-center',
                render: function (data, type, row) {
                    var buttons = '';
                    buttons += '<a href="/pos/frm/box/update/' + row.id + '/" class="btn btn-warning btn-xs btn-flat"><i class="fas fa-edit"></i></a> ';
                    buttons += '<a href="/pos/frm/box/delete/' + row.id + '/" class="btn btn-danger btn-xs btn-flat"><i class="fas fa-trash"></i></a> ';
                    return buttons;
                }
            },
            
        ],
        rowCallback: function (row, data, index) {
            
        },
        initComplete: function (settings, json) {
            
        }
    });
}

$(function () {

    input_daterange = $('input[name="date_range"]');

    input_daterange
        .daterangepicker({
            language: 'auto',
            startDate: new Date(),
            locale: {
                format: 'YYYY-MM-DD',
            }
        })
        .on('apply.daterangepicker', function (ev, picker) {
            getData(false);
        });

    $('.drp-buttons').hide();

    getData(false);

    $('.btnSearch').on('click', function () {
        getData(false);
    });

    $('.btnSearchAll').on('click', function () {
        getData(true);
    });

    $('#data tbody')
        .off()
        .on('click', 'a[rel="payments"]', function () {
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
                    data: function (d) {
                        d.action = 'search_pays';
                        d.id = row.id;
                    },
                    dataSrc: ""
                },
                columns: [
                    {data: "id"},
                    {data: "hours_close"},
                    {data: "date_close"},
                    {data: "cash_sale"},
                    {data: "cash_credit"},
                    {data: "sale_card"},
                    {data: "initial_box"},
                    {data: "box_final"},
                    {data: "desc"},
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
                            return data
                        }
                    },
                    {
                        targets: [3],
                        class: 'text-center',
                        render: function (data, type, row) {
                            return data
                        }
                    },
                    {
                        targets: [4],
                        class: 'text-center',
                        render: function (data, type, row) {
                            return data
                        }
                    },
                    {
                        targets: [5],
                        class: 'text-center',
                        render: function (data, type, row) {
                            return data
                        }
                    },
                    {
                        targets: [6],
                        class: 'text-center',
                        render: function (data, type, row) {
                            return 'S/.' + data
                        }
                    },
                    {
                        targets: [7],
                        class: 'text-center',
                        render: function (data, type, row) {
                            return 'S/.' + data
                        }
                    },
                    {
                        targets: [-1],
                        class: 'text-center',
                        render: function (data, type, row) {
                            var buttons = '';
                            buttons += '<a href="/pos/frm/expenses/update/' + row.id + '/" class="btn btn-warning btn-xs btn-flat"><i class="fas fa-edit"></i></a> ';
                            buttons += '<a href="/pos/frm/expenses/delete/' + row.id + '/" class="btn btn-danger btn-xs btn-flat"><i class="fas fa-trash"></i></a> ';
                            return buttons;
                        }
                    },
                ],
                rowCallback: function (row, data, index) {
                   
                },
                initComplete: function (settings, json) {
                   
                }
            });
            $('#myModalPayments').modal('show');
        });

    $('#tblPayments tbody')
        .off()
        .on('click', 'a[rel="delete"]', function () {
            $('.tooltip').remove();
            var tr = tblPaymentsCtasCollect.cell($(this).closest('td, li')).index(),
                row = tblPaymentsCtasCollect.row(tr.row).data();
            submit_with_ajax('Notificación',
                '¿Estas seguro de eliminar el registro?',
                pathname,
                {
                    'id': row.id,
                    'action': 'delete_pay'
                },
                function () {
                    tblCtasCollect = tblCtasCollect.ajax.reload();
                    tblPaymentsCtasCollect.ajax.reload();
                }
            );
        });
});
