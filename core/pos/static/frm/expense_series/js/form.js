$(document).ready(function() {
    const frmExpenseSeries = document.getElementById('frmExpenseSeries');
    
    if (frmExpenseSeries) {
        const form = new FormValidation.FormValidation(frmExpenseSeries, {
            fields: {
                name: {
                    validators: {
                        notEmpty: {
                            message: 'El nombre de la serie es requerido'
                        },
                        stringLength: {
                            min: 2,
                            max: 100,
                            message: 'El nombre debe tener entre 2 y 100 caracteres'
                        }
                    }
                }
            },
            plugins: {
                trigger: new FormValidation.plugins.Trigger(),
                bootstrap: new FormValidation.plugins.Bootstrap(),
                submitButton: new FormValidation.plugins.SubmitButton(),
                defaultSubmit: new FormValidation.plugins.DefaultSubmit()
            }
        });
    }
});
