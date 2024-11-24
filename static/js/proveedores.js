function filtrarProveedores() {
    let input = document.getElementById('busqueda');
    let filter = input.value.toLowerCase();
    let table = document.getElementById('tablaProveedores');
    let tr = table.getElementsByTagName('tr');
    
    for (let i = 1; i < tr.length; i++) {
        let td = tr[i].getElementsByTagName('td');
        let visible = false;

        for (let j = 0; j < td.length; j++) {
            if (td[j]) {
                let txtValue = td[j].textContent || td[j].innerText;
                if (txtValue.toLowerCase().indexOf(filter) > -1) {
                    visible = true;
                    break;
                }
            }
        }
        tr[i].style.display = visible ? "" : "none";
    }
}

function modal_editar(url) {
    const $ = jQuery.noConflict();
    $('#edicion_prov').load(url, function () {
        $(this).modal('show');
    });
}
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.btn-borrarProv').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            let form = this.closest('form');
            Swal.fire({
                title: '¿Estás seguro?',
                text: "No podrás deshacer esta acción.",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    form.submit();
                }
            });
        });
    });
});
