document.addEventListener("DOMContentLoaded", function() {
    const cerrarSesionBtn = document.querySelector('#cerrar-sesion-btn');
    const cerrarCajaBtn = document.querySelector('#btn-cerrar');

    if (cerrarSesionBtn) {
        cerrarSesionBtn.addEventListener('click', function(event) {
            event.preventDefault(); 
            Swal.fire({
                title: "¿Está seguro de cerrar la sesión?",
                text: "",
                icon: "question",
                showCancelButton: true,
                confirmButtonText: "Ok",
                cancelButtonText: "Cancelar",
                confirmButtonColor: "#d33",
                cancelButtonColor: "#3085d6",
                showLoaderOnConfirm: true,
                preConfirm: () => {
                    document.getElementById('logout-form').submit();
                },
                allowOutsideClick: false,
                allowEscapeKey: false,
            });
        });
    }

    if (cerrarCajaBtn) {
        cerrarCajaBtn.addEventListener('click', function(event) {
            event.preventDefault(); 
            Swal.fire({
                title: "¿Confirma cerrar la caja?",
                text: "Tiene una caja abierta, la cual se cerrará con la sesión.",
                icon: "question",
                showCancelButton: true,
                confirmButtonText: "Cerrar caja",
                cancelButtonText: "Cancelar",
                confirmButtonColor: "#d33",
                cancelButtonColor: "#3085d6",
                showLoaderOnConfirm: true,
                preConfirm: () => {
                    return fetch('/cierre/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCsrfToken(),
                        },
                        body: JSON.stringify({ action: 'cerrar_caja' })
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Error al cerrar la caja');
                        }
                        return Swal.fire({
                            title: "Caja cerrada con éxito",
                            icon: "success",
                        });
                    });
                },
                allowOutsideClick: false,
                allowEscapeKey: false,
            }).then((result) => {
                if (result.isConfirmed) {
                    document.getElementById('logout-form').submit();
                }
            });
        });
    }

    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
});
