var input_searchproducts;
var tblProducts;
var tblSearchProducts;

var inventory = {
    details: {
        products: []
    },
    add_product: function(item) {
        // var expirationDate = $('#tblProducts tbody tr:eq(' + rowIndex + ') input[name="expiration_date"]').val();
        // // Asignar la fecha de vencimiento al producto
        // item.expiration_date = expirationDate;
        this.details.products.push(item);
        this.list_products();
    },
    list_products: function() {
        tblProducts = $('#tblProducts').DataTable({
            // responsive: true,
            // autoWidth: false,
            destroy: true,
            data: this.details.products,
            ordering: false,
            lengthChange: false,
            searching: false,
            paginate: false,
            scrollX: true,
            scrollCollapse: true,
            columns: [
                { data: "id" },
                { data: "name" },
                { data: "category.name" },
                { data: "newstock" },
                // { data: null },
            ],
            columnDefs: [
                // {
                //     targets: [-1],
                //     class: 'text-center',
                //     render: function(data, type, row) {
                //         return '<input type="date" class="form-control input-sm expiration-date" style="width: 100%; center" name="expiration_date" value="1" min="1">';
                //     }
                // },
                {
                    targets: [3],
                    class: 'text-center',
                    render: function(data, type, row) {
                        return '<input type="number" class="form-control input-sm" style="width: 40%; margin: auto" name="print_qty" value="1" min="1">';
                    }
                },
                {
                    targets: [0],
                    class: 'text-center',
                    render: function(data, type, row) {
                        return '<a rel="remove" class="btn btn-danger btn-flat btn-xs"><i class="fas fa-times"></i></a>';
                    }
                },
            ],
            rowCallback: function(row, data, index) {
                var tr = $(row).closest('tr');
                tr.find('input[name="newstock"]')
                    .TouchSpin({
                        min: 0,
                        max: 10000000,
                        verticalbuttons: true,
                    })
                    .keypress(function(e) {
                        return validate_form_text('numbers', e, null);
                    });
                tr.find('.expiration-date').on('change', function() {
                    inventory.details.products[index].expiration_date = $(this).val();
                });
                tr.find('input[name="print_qty"]').on('change', function() {
                    inventory.details.products[index].print_qty = parseInt($(this).val());
                });
            },
            initComplete: function(settings, json) {

            },
        });
    },
    get_products_ids: function() {
        var ids = [];
        $.each(this.details.products, function(i, item) {
            ids.push(item.id);
        });
        return ids;
    },
};

$(function() {

    input_searchproducts = $('input[name="searchproducts"]');

    input_searchproducts.autocomplete({
        source: function(request, response) {
            $.ajax({
                url: pathname,
                data: {
                    'action': 'search_products',
                    'term': request.term,
                    'ids': JSON.stringify(inventory.get_products_ids()),
                },
                dataType: "json",
                type: "POST",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                beforeSend: function() {

                },
                success: function(data) {
                    response(data);
                }
            });
        },
        min_length: 3,
        delay: 300,
        select: function(event, ui) {
            event.preventDefault();
            $(this).blur();
            ui.item.newstock = ui.item.stock;
            inventory.add_product(ui.item);
            $(this).val('').focus();
        }
    });

    $('.btnClearProducts').on('click', function() {
        input_searchproducts.val('').focus();
    });

    $('#tblProducts tbody')
        .off()
        .on('change', 'input[name="newstock"]', function() {
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            inventory.details.products[tr.row].newstock = parseInt($(this).val());
        })
        .on('click', 'a[rel="remove"]', function() {
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            inventory.details.products.splice(tr.row, 1);
            tblProducts.row(tr.row).remove().draw();
            $('.tooltip').remove();
        });

    $('.btnSearchProducts').on('click', function() {
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
                    'ids': JSON.stringify(inventory.get_products_ids()),
                },
                dataSrc: ""
            },
            //paging: false,
            //ordering: false,
            //info: false,
            scrollX: true,
            scrollCollapse: true,
            columns: [
                { data: "name" },
                { data: "category.name" },
                { data: "stock" },
                { data: "id" },
            ],
            columnDefs: [{
                    targets: [-2],
                    class: 'text-center',
                    render: function(data, type, row) {
                        if (row.stock > 0) {
                            return '<span class="badge badge-success">' + data + '</span>'
                        }
                        return '<span class="badge badge-warning">' + data + '</span>'
                    }
                },
                {
                    targets: [-1],
                    class: 'text-center',
                    render: function(data, type, row) {
                        return '<a rel="add" class="btn btn-success btn-flat btn-xs"><i class="fas fa-plus"></i></a>'
                    }
                }
            ],
            rowCallback: function(row, data, index) {
                var tr = $(row).closest('tr');
                if (data.stock === 0) {
                    $(tr).css({ 'background': '#dc3345', 'color': 'white' });
                }
            },
        });
        $('#myModalSearchProducts').modal('show');
    });

    $('#tblSearchProducts tbody')
        .off()
        .on('click', 'a[rel="add"]', function() {
            var tr = tblSearchProducts.cell($(this).closest('td, li')).index();
            var row = tblSearchProducts.row(tr.row).data();
            console.log(row.codebar);
            row.newstock = row.stock;
            inventory.add_product(row);
            tblSearchProducts.row(tblSearchProducts.row(tr.row).node()).remove().draw();
        });

    $('.btnRemoveAllProducts').on('click', function() {
        if (inventory.details.products.length === 0) return false;
        dialog_action('Notificación', '¿Estas seguro de eliminar todos los items de tu detalle?', function() {
            inventory.details.products = [];
            inventory.list_products();
        }, function() {

        });
    });

    inventory.list_products();

    function formatDate(dateString) {
        const date = new Date(dateString + "T00:00:00"); // Agregar la hora para evitar cambios de zona horaria
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        return `${day}/${month}/${year}`; // Cambia el formato según tu preferencia
    }

    $('.btnSave').on('click', function() {
        if (inventory.details.products.length === 0) {
            message_error('Debe tener al menos un producto en su detalle');
            return false;
        }
    
        // Función para generar el PDF
        function generatePDF() {
            const { jsPDF } = window.jspdf;
    
            const doc = new jsPDF({
                orientation: 'portrait',
                unit: 'mm',
                format: [80, 297] // 80mm de ancho y longitud suficiente para contenido
            });
    
            const pageWidth = doc.internal.pageSize.width;
            const pageHeight = doc.internal.pageSize.height;
            const margin = 10;
            const barcodeWidth = 50;
            const barcodeHeight = 23;
            const textHeight = 3;
            const textMargin = 0.5;
            const columnWidth = pageWidth - 2 * margin;
            let y = margin;
    
            doc.setFontSize(7);
    
            for (const product of inventory.details.products) {
                const printQty = product.print_qty || 1;
                for (let i = 0; i < printQty; i++) {
                    // Crear canvas de alta resolución
                    const canvas = document.createElement('canvas');
                    canvas.width = barcodeWidth * 10;
                    canvas.height = barcodeHeight * 10;
                    JsBarcode(canvas, product.codebar, {
                        format: 'CODE128',
                        displayValue: false,
                        width: 2,
                        height: 100
                    });
    
                    // Convertir canvas a imagen de alta resolución
                    const imgData = canvas.toDataURL('image/png');
                    doc.addImage(imgData, 'PNG', (pageWidth - barcodeWidth) / 2, y, barcodeWidth, barcodeHeight);
    
                    y += barcodeHeight + textMargin;
    
                    // Agregar código de barras como texto antes del nombre del producto
                    const productCodebar = product.codebar;
                    doc.text(productCodebar, pageWidth / 2, y, { align: 'center' });
    
                    y += textHeight + textMargin;
    
                    // Agregar nombre del producto debajo del código de barras
                    const productName = product.name;
                    const productNameLines = doc.splitTextToSize(productName, columnWidth);
                    doc.text(productNameLines, pageWidth / 2, y, { align: 'center' });
    
                    y += productNameLines.length * textHeight + textMargin;
    
                    // Agregar precio del producto
                    const productPrice = `Precio: ${product.pvp}`;
                    const productPriceLines = doc.splitTextToSize(productPrice, columnWidth);
                    doc.text(productPriceLines, pageWidth / 2, y, { align: 'center' });
    
                    y += productPriceLines.length * textHeight + textMargin;
    
                    // Agregar fecha de vencimiento
                    // const expirationDate = product.expiration_date;
                    // const formattedExpirationDate = expirationDate ? formatDate(expirationDate) : "";
                    // const expirationDateLines = doc.splitTextToSize("Vencimiento: " + formattedExpirationDate, columnWidth);
                    // doc.text(expirationDateLines, pageWidth / 2, y, { align: 'center' });
    
                    // y += expirationDateLines.length * textHeight + textMargin;
    
                    // Si la altura supera la página, añadir una nueva página
                    if (y + barcodeHeight + (4 * textHeight) + (4 * textMargin) > pageHeight - margin) {
                        doc.addPage();
                        y = margin;
                    }
                }
            }
    
            const currentDate = new Date();
            const dateString = currentDate.toISOString().slice(0, 10).replace(/-/g, "");
            const timeString = currentDate.toTimeString().slice(0, 5).replace(/:/g, "");
            doc.save(`CódigoBarras_${dateString}_${timeString}.pdf`);
        }
    
        generatePDF();
    });
    
    
    
    

    $('i[data-field="searchproducts"]').hide();
})