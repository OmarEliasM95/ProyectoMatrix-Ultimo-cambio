document.addEventListener("DOMContentLoaded", function() {
    const btnCambiar = document.querySelector('#btn-cambiar');

    if (btnCambiar) {
        btnCambiar.addEventListener('click', function(event) {
            event.preventDefault();
            const form = document.getElementById('formulario-perfil');
            const passwordActual = form.querySelector('[name="password_actual"]').value;
            const passwordNueva = form.querySelector('[name="password"]').value;
            const passwordConfirm = form.querySelector('[name="password_confirm"]').value;
            const errores = [];

            if (passwordNueva !== passwordConfirm) {
                errores.push("Las contraseñas no coinciden.");
            }
            if (passwordNueva.length < 8) {
                errores.push("La nueva contraseña debe tener al menos 8 caracteres.");
            }
            if (!/\d/.test(passwordNueva)) {
                errores.push("La nueva contraseña debe contener al menos un número.");
            }
            if (!/[a-zA-Z]/.test(passwordNueva)) {
                errores.push("La nueva contraseña debe contener al menos una letra.");
            }
            if (passwordNueva === passwordActual) {
                errores.push("La nueva contraseña no puede ser igual a la contraseña actual.");
            }
            const username = form.querySelector('[name="username"]').value; 
            if (passwordNueva === username) {
                errores.push("La nueva contraseña no puede ser igual al nombre de usuario.");
            }

            if (errores.length > 0) {
                notificacionSwal('Error', errores.join('<br>'), 'error', 'Ok');
            } else {
                Swal.fire({
                    title: "¿Está seguro?",
                    text: "Si acepta, se cerrará la sesión y se pedirá que inicie con la nueva contraseña.",
                    icon: 'question',
                    showCancelButton: true,
                    confirmButtonText: 'Aceptar',
                    cancelButtonText: 'Cancelar',
                }).then((result) => {
                    if (result.isConfirmed) {
                        const data = new FormData(form);
                        fetch(form.action, {
                            method: 'POST',
                            body: data,
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                window.location.href = '/';  
                            } else {
                                notificacionSwal('Error', data.error, 'error', 'Ok');
                            }
                        })
                        .catch(error => {
                            console.error('Error al cambiar la contraseña:', error);
                            notificacionSwal('Error', 'Ocurrió un error inesperado.', 'error', 'Ok');
                        });
                    }
                });
            }
        });
    }

    function notificacionSwal(titulo, texto, icono, boton) {
        return Swal.fire({
            title: titulo,
            html: texto,  
            icon: icono,
            confirmButtonText: boton
        });
    }
});
