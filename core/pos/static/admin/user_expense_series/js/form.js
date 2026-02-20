$(document).ready(function() {
    const frmUserExpenseSeries = document.getElementById('frmUserExpenseSeries');
    
    if (frmUserExpenseSeries) {
        const form = new FormValidation.FormValidation(frmUserExpenseSeries, {
            fields: {
                user: {
                    validators: {
                        notEmpty: {
                            message: 'El usuario es requerido'
                        }
                    }
                },
                expense_series: {
                    validators: {
                        notEmpty: {
                            message: 'La serie de gastos es requerida'
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
