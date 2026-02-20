var tblUserExpenseSeries;

function getData(all) {
    var parameters = {
        'action': 'search',
        'term': $('input[name="term"]').val(),
    };

    if (all) {
        parameters['term'] = '';
    }

    tblUserExpenseSeries = $('#data').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
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
            {data: "user.full_name"},
            {data: "expense_series.name"},
            {data: "id"},
        ],
        columnDefs: [
            {
                targets: [-1],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    var buttons = '<a rel="edit" class="btn btn-warning btn-xs btn-flat" href="#" title="Editar"><i class="fas fa-edit"></i></a> ';
                    buttons += '<a rel="delete" class="btn btn-danger btn-xs btn-flat" href="#" title="Eliminar"><i class="fas fa-trash"></i></a>';
                    return buttons;
                }
            }
        ],
        language: {
            url: '//cdn.datatables.net/plug-ins/1.10.15/i18n/Spanish.json'
        },
        initComplete: function (settings, json) {
        }
    });
}

$(function () {
    getData(true);

    $('input[name="term"]').keyup(function () {
        getData(false);
    }).focus();

    $('#data tbody')
        .off()
        .on('click', 'a[rel="delete"]', function (e) {
            e.preventDefault();
            var tr = tblUserExpenseSeries.cell($(this).closest('td, li')).index();
            var row = tblUserExpenseSeries.row(tr.row).data();
            var deleteUrl = '/pos/frm/user_expense_series/delete/' + row.id + '/';
            
            $.confirm({
                title: 'Notificación de Eliminación',
                icon: 'fas fa-trash',
                content: '¿Estás seguro de realizar la siguiente acción?',
                theme: 'material',
                columnClass: 'small',
                typeAnimated: true,
                cancelButtonClass: 'btn-primary',
                draggable: true,
                dragWindowBorder: false,
                buttons: {
                    info: {
                        text: "Si",
                        btnClass: 'btn-primary',
                        action: function () {
                            $.ajax({
                                type: 'POST',
                                url: deleteUrl,
                                headers: {
                                    'X-CSRFToken': csrftoken
                                },
                                success: function (data) {
                                    getData(true);
                                },
                                error: function (jqXHR, textStatus, errorThrown) {
                                    alert('Error: ' + textStatus);
                                }
                            });
                        }
                    },
                    cancel: {
                        text: 'No',
                        btnClass: 'btn-danger',
                    },
                }
            });
        })
        .on('click', 'a[rel="edit"]', function (e) {
            e.preventDefault();
            var tr = tblUserExpenseSeries.cell($(this).closest('td, li')).index();
            var row = tblUserExpenseSeries.row(tr.row).data();
            window.location.href = '/pos/frm/user_expense_series/update/' + row.id + '/';
        });
});
