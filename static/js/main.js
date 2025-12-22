var pathname = window.location.pathname;

$(function () {

    $('[data-toggle="tooltip"]').tooltip();

    $('.table')
        .on('draw.dt', function () {
            $('[data-toggle="tooltip"]').tooltip();
        })
        .on('click', 'img', function () {
            var src = $(this).attr('src');
            load_image(src);
        });
});