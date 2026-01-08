var fvSeries;

document.addEventListener('DOMContentLoaded', function (e) {
    const frmSeries = document.getElementById('frmSeries');
    fvSeries = FormValidation.formValidation(frmSeries, {
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
                name: {
                    validators: {
                        notEmpty: {
                            message: 'El nombre es obligatorio'
                        },
                        stringLength: {
                            min: 3,
                            max: 50,
                            message: 'El nombre debe tener entre 3 y 50 caracteres'
                        }
                    }
                },
            },
        }
    )
        .on('core.form.valid', function () {
            var parameters = new FormData(fvSeries.form);
            parameters.append('action', frmSeries.querySelector('input[name="action"]').value);
            submit_formdata_with_ajax('Notificación', '¿Estás seguro de realizar la siguiente acción?', pathname, parameters, function (request) {
                window.location.href = document.querySelector('a[href*="list"]')?.href || '/pos/frm/series/';
            });
        });
});

