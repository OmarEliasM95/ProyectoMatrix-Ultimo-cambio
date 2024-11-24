const notificacionSwal = (titleText, text, icon, confirmButtonText) => {
    return Swal.fire({
        titleText: titleText,
        text: text,
        icon: icon,
        confirmButtonText: confirmButtonText,
        allowOutsideClick: false,
        allowEscapeKey: false,
        showConfirmButton: true,
        allowOutsideClick:false,
        allowEscapeKey: false,
    });
};

document.getElementById('cerrar-form').addEventListener('submit', function (event) {
    event.preventDefault()
    notificacionSwal('Éxito', 'Caja cerrada correctamente', 'success', 'Ok!').then((result) => {
        if (result.isConfirmed) {
            event.target.submit()
        }
    });
})

$(document).ready(function() {
    const rowsPerPage = 7; 
    const rows = $('.venta-row');
    const totalRows = rows.length;
    const totalPages = Math.ceil(totalRows / rowsPerPage);

    function showPage(page) {
        rows.hide(); 
        const start = (page - 1) * rowsPerPage;
        const end = start + rowsPerPage;
        rows.slice(start, end).show();
    }

    function buildPagination() {
        const pagination = $('#pagination');
        pagination.empty();

        for (let i = 1; i <= totalPages; i++) {
            pagination.append(`<li class="page-item"><a class="page-link" href="#">${i}</a></li>`);
        }

        pagination.find('.page-link').click(function(e) {
            e.preventDefault();
            const page = parseInt($(this).text());
            showPage(page); 
        });
    }

    buildPagination();
    showPage(1); 
});
