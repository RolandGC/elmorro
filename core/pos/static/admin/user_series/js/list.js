var tblUserSeries;

function getData(all) {
    var parameters = {
        'action': 'search',
        'term': $('input[name="term"]').val(),
    };

    if (all) {
        parameters['term'] = '';
    }

    tblUserSeries = $('#data').DataTable({
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
            {data: "series.name"},
            {data: "id"},
        ],
        columnDefs: [
            {
                targets: [-1],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    var buttons = '<a href="/pos/frm/user_series/update/' + row.id + '/" class="btn btn-warning btn-flat btn-xs"><i class="fas fa-edit"></i></a> ';
                    buttons += '<a rel="delete" class="btn btn-danger btn-flat btn-xs" href="/pos/frm/user_series/delete/' + row.id + '/"><i class="fas fa-trash-alt"></i></a>';
                    return buttons;
                }
            }
        ],
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
            var tr = tblUserSeries.cell($(this).closest('td, li')).index();
            var row = tblUserSeries.row(tr.row).data();
            var deleteUrl = $(this).attr('href');
            
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
                                url: deleteUrl,
                                type: 'POST',
                                headers: {
                                    'X-CSRFToken': csrftoken,
                                    'X-Requested-With': 'XMLHttpRequest'
                                },
                                dataType: 'json',
                                success: function (response) {
                                    if (!response.hasOwnProperty('error')) {
                                        getData(true);
                                    } else {
                                        Swal.fire('Error', response.error, 'error');
                                    }
                                },
                                error: function () {
                                    Swal.fire('Error', 'Ocurrió un error al eliminar', 'error');
                                }
                            });
                        }
                    },
                    danger: {
                        text: "No",
                        btnClass: 'btn-red',
                        action: function () {
                        }
                    }
                }
            });
        });
});
