// Función para obtener el CSRF Token de las cookies de Django
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Agregar producto al carrito sin recargar la página
function agregarAlCarrito(productoId) {
    const url = `/carrito/agregar/${productoId}/`;
    const csrftoken = getCookie('csrftoken');

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'ok') {
            // Actualizar la insignia o número del carrito en el Navbar
            const badge = document.getElementById('cart-badge');
            if (badge) {
                badge.innerText = data.total_unidades;
            }
            alert(data.mensaje);
        }
    })
    .catch(error => console.error('Error al agregar al carrito:', error));
}