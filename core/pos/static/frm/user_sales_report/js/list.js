let currentUser = null;
let allUsers = [];

// Cargar lista de usuarios al iniciar
function loadUsers() {
    var parameters = {
        'action': 'search_users',
    };

    $.ajax({
        url: window.location.pathname,
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: parameters,
        dataType: 'json',
        success: function(data) {
            console.log('Usuarios cargados:', data);
            allUsers = data;
            var select = $('#selectUser');
            select.empty();
            select.append('<option value="">-- Seleccionar Usuario --</option>');
            
            $.each(data, function (index, user) {
                // Mostrar full_name - dni
                var displayName = user.full_name || 'Sin nombre';
                select.append(`<option value="${user.id}">${displayName} - ${user.dni}</option>`);
            });
            
            // Inicializar Select2 después de agregar opciones
            select.select2({
                placeholder: '-- Seleccionar Usuario --',
                allowClear: true,
                language: 'es',
                width: '100%'
            });
            
            console.log('Usuarios agregados al dropdown:', data.length);
        },
        error: function(xhr, status, error) {
            console.error('Error al cargar usuarios:', error);
            console.error('Response:', xhr.responseText);
        }
    });
}

// Buscar ventas por usuario
function searchUserSales() {
    var userId = $('#selectUser').val();
    var dateFrom = $('#dateFrom').val();
    var dateTo = $('#dateTo').val();
    
    if (!userId) {
        alert_sweetalert('warning', 'Alerta', 'Por favor selecciona un usuario', null, 2000);
        return;
    }
    
    var parameters = {
        'action': 'get_user_sales',
        'user_id': userId,
        'date_from': dateFrom,
        'date_to': dateTo,
    };
    
    $.ajax({
        url: window.location.pathname,
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: parameters,
        dataType: 'json',
        success: function(data) {
            if (data.error) {
                alert_sweetalert('error', 'Error', data.error, null, 3000);
                return;
            }
            
            currentUser = data.user;
            $('#detailContainer').show();
            $('#summaryContainer').hide();
            
            // Actualizar título
            $('#userTitle').html(`Detalle de Cobranzas - <strong>${data.user.full_name}</strong> (DNI: ${data.user.dni})`);
            
            // Mostrar resumen por método de pago
            showPaymentMethodsSummary(data.sales_by_method, data.total_general, data.total_cantidad);
            
            // Llenar tabla de ventas
            fillSalesTable(data.sales_by_method);
        },
        error: function(xhr, status, error) {
            console.error('Error:', error, xhr.responseText);
            alert_sweetalert('error', 'Error', 'Error al buscar cobranzas', null, 3000);
        }
    });
}

// Mostrar resumen por método de pago
function showPaymentMethodsSummary(methodsData, totalGeneral, totalCantidad) {
    var container = $('#methodsContainer');
    container.empty();
    
    var colors = {
        'efectivo': 'success',
        'yape': 'warning',
        'plin': 'info',
        'transferencia': 'primary',
        'deposito': 'danger'
    };
    
    $.each(methodsData, function (method, data) {
        if (data.count > 0) {
            var color = colors[method] || 'secondary';
            container.append(`
                <div class="col-lg-4 col-md-6">
                    <div class="card card-payment-method border-left-${color}">
                        <div class="card-header bg-gradient-${color}">
                            <h6 class="payment-method-title text-white m-0">
                                <i class="fas fa-money-bill"></i> ${data.name.toUpperCase()}
                            </h6>
                        </div>
                        <div class="card-body">
                            <div class="payment-method-info">
                                <span>Nro Transacciones:</span>
                                <span><strong>${data.count}</strong></span>
                            </div>
                            <div class="payment-method-info">
                                <span>Productos Vendidos:</span>
                                <span><strong>${data.cantidad}</strong></span>
                            </div>
                            <hr style="margin: 8px 0;">
                            <div class="payment-method-info">
                                <span style="font-weight: 600;">Total Vendido:</span>
                                <span class="payment-method-total" style="font-size: 16px;">S/. ${parseFloat(data.total).toFixed(2)}</span>
                            </div>
                        </div>
                    </div>
                </div>
            `);
        }
    });
    
    // Agregar tarjeta de totales generales
    container.append(`
        <div class="col-lg-4 col-md-6">
            <div class="card card-payment-method border-left-dark">
                <div class="card-header bg-dark">
                    <h6 class="payment-method-title text-white m-0">
                        <i class="fas fa-calculator"></i> TOTALES
                    </h6>
                </div>
                <div class="card-body">
                    <div class="payment-method-info">
                        <span>Total Transacciones:</span>
                        <span><strong>${getTotalCount(methodsData)}</strong></span>
                    </div>
                    <div class="payment-method-info">
                        <span>Total Productos:</span>
                        <span><strong>${totalCantidad}</strong></span>
                    </div>
                    <hr style="margin: 8px 0;">
                    <div class="payment-method-info">
                        <span style="font-weight: 600; font-size: 15px;">TOTAL GENERAL:</span>
                        <span class="payment-method-total" style="font-size: 18px; color: #2ecc71;">S/. ${parseFloat(totalGeneral).toFixed(2)}</span>
                    </div>
                </div>
            </div>
        </div>
    `);
}

// Contar total de transacciones
function getTotalCount(methodsData) {
    var total = 0;
    $.each(methodsData, function (method, data) {
        total += data.count;
    });
    return total;
}

// Llenar tabla de ventas
function fillSalesTable(methodsData) {
    var tbody = $('#tblSales tbody');
    tbody.empty();
    
    $.each(methodsData, function (method, methodData) {
        $.each(methodData.sales, function (index, sale) {
            tbody.append(`
                <tr>
                    <td class="text-center">#${sale.nro}</td>
                    <td class="text-center">${sale.date}</td>
                    <td class="text-center"><span class="badge badge-info">${sale.type_voucher}</span></td>
                    <td>${sale.client}</td>
                    <td class="text-center"><strong>${sale.cantidad}</strong></td>
                    <td class="text-right">S/. ${parseFloat(sale.subtotal).toFixed(2)}</td>
                    <td class="text-right">S/. ${parseFloat(sale.total_dscto).toFixed(2)}</td>
                    <td class="text-right"><strong>S/. ${parseFloat(sale.total).toFixed(2)}</strong></td>
                </tr>
            `);
        });
    });
    
    if ($('#tblSales tbody tr').length === 0) {
        tbody.append('<tr><td colspan="8" class="text-center text-muted">No hay ventas registradas</td></tr>');
    }
}

// Mostrar resumen general
function loadSummary() {
    var dateFrom = $('#dateFrom').val();
    var dateTo = $('#dateTo').val();
    
    var parameters = {
        'action': 'get_summary',
        'date_from': dateFrom,
        'date_to': dateTo,
    };
    
    $.ajax({
        url: window.location.pathname,
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: parameters,
        dataType: 'json',
        success: function(data) {
            if (data.error) {
                alert_sweetalert('error', 'Error', data.error, null, 3000);
                return;
            }
            
            $('#summaryContainer').show();
            $('#detailContainer').hide();
            
            fillSummaryTable(data.summary);
        },
        error: function(xhr, status, error) {
            console.error('Error:', error, xhr.responseText);
            alert_sweetalert('error', 'Error', 'Error al cargar resumen', null, 3000);
        }
    });
}

// Llenar tabla de resumen
function fillSummaryTable(summary) {
    var tbody = $('#tblSummary tbody');
    tbody.empty();
    
    $.each(summary, function (index, user) {
        var efectivo = user.metodos.efectivo ? user.metodos.efectivo.total : 0;
        var yape = user.metodos.yape ? user.metodos.yape.total : 0;
        var plin = user.metodos.plin ? user.metodos.plin.total : 0;
        var transferencia = user.metodos.transferencia ? user.metodos.transferencia.total : 0;
        var deposito = user.metodos.deposito ? user.metodos.deposito.total : 0;
        
        tbody.append(`
            <tr>
                <td><strong>${user.user_name}</strong></td>
                <td class="text-center">${user.total_transacciones}</td>
                <td class="text-right">S/. ${parseFloat(efectivo).toFixed(2)}</td>
                <td class="text-right">S/. ${parseFloat(yape).toFixed(2)}</td>
                <td class="text-right">S/. ${parseFloat(plin).toFixed(2)}</td>
                <td class="text-right">S/. ${parseFloat(transferencia).toFixed(2)}</td>
                <td class="text-right">S/. ${parseFloat(deposito).toFixed(2)}</td>
                <td class="text-right"><strong>S/. ${parseFloat(user.total_vendido).toFixed(2)}</strong></td>
            </tr>
        `);
    });
    
    if (summary.length === 0) {
        tbody.append('<tr><td colspan="8" class="text-center text-muted">No hay datos disponibles</td></tr>');
    }
}

// Event listeners
$(function () {
    // Inicializar Select2 (será reinicializado después de cargar usuarios)
    $('#selectUser').select2({
        placeholder: '-- Seleccionar Usuario --',
        allowClear: true,
        language: 'es',
        width: '100%'
    });
    
    loadUsers();
    
    $('#btnSearch').on('click', function () {
        searchUserSales();
    });
    
    $('#btnSummary').on('click', function () {
        loadSummary();
    });
    
    $('#selectUser').on('change', function () {
        if ($(this).val()) {
            currentUser = allUsers.find(u => u.id == $(this).val());
            console.log('Usuario seleccionado:', currentUser);
        }
    });
    
    // Permitir búsqueda con Enter
    $('#dateFrom, #dateTo').on('keypress', function (e) {
        if (e.which == 13) {
            searchUserSales();
            return false;
        }
    });
});
