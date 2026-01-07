$(function () {
    var options = {
        locale: 'es_ES',
        fields: {
            user: {
                validators: {
                    notEmpty: {
                        message: 'Selecciona un vendedor'
                    }
                }
            },
            series: {
                validators: {
                    notEmpty: {
                        message: 'Selecciona una serie'
                    }
                }
            }
        },
        plugins: {
            submitButton: new FormValidation.plugins.SubmitButton(),
            bootstrap: new FormValidation.plugins.Bootstrap(),
            icon: new FormValidation.plugins.Icon({
                valid: 'fa fa-check',
                invalid: 'fa fa-times',
                validating: 'fa fa-refresh',
            }),
        },
        core: {
            focusInvalid: false,
        }
    };

    var fv = FormValidation.formValidation(
        document.getElementById('frmUserSeries'),
        options
    );

    $('#frmUserSeries').submit(function (e) {
        e.preventDefault();

        fv.validate().then(function (status) {
            if (status === 'Valid') {
                var form = $('#frmUserSeries')[0];
                var formData = new FormData(form);
                var action = $('button[type="submit"]').attr('value');
                formData.append('action', action);

                $.ajax({
                    url: pathname,
                    type: 'POST',
                    data: formData,
                    processData: false,
                    contentType: false,
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    success: function (request, status, xhr) {
                        if (request.hasOwnProperty('error')) {
                            var errorObj = request.error;
                            
                            // Si el error es un diccionario (errores de campos específicos)
                            if (typeof errorObj === 'object' && !Array.isArray(errorObj)) {
                                var errorMessage = '';
                                
                                // Procesar errores globales (__all__)
                                if (errorObj.__all__) {
                                    errorMessage += errorObj.__all__.join('<br>') + '<br>';
                                }
                                
                                // Procesar errores de campos específicos
                                for (var field in errorObj) {
                                    if (field !== '__all__') {
                                        errorMessage += errorObj[field].join('<br>') + '<br>';
                                    }
                                }
                                
                                Swal.fire('Error', errorMessage, 'error');
                            } else {
                                // Si es un string simple
                                Swal.fire('Error', errorObj, 'error');
                            }
                        } else {
                            location.href = '/pos/admin/user_series/';
                        }
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        Swal.fire('Error', 'Ocurrió un error al guardar los datos', 'error');
                    }
                });
            }
        });
    });
});
