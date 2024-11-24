function filtrarProductos(){
    var input= document.getElementById("busqueda");
    var filtro= input.value.toLowerCase();
    var tabla= document.getElementById("tablaProductos");
    var filas= tabla.getElementsByTagName("tr");

    for (var i = 1; i < filas.length; i++) {
        var celdas = filas[i].getElementsByTagName("td");
        var coincide = false;

        for (var j = 0; j < celdas.length; j++) {
            if (celdas[j]) {
                var texto = celdas[j].textContent || celdas[j].innerText;
                if (texto.toLowerCase().indexOf(filtro) > -1) {
                    coincide = true;
                    break;
                }
            }
        }

        filas[i].style.display = coincide ? "" : "none";
    }
}
function modal_editar_producto(url) {
    const $ = jQuery.noConflict();
    $('#edicion').load(url, function () {
        $(this).modal('show');
    });
}
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#btn-borrarProd').forEach(button => {
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
