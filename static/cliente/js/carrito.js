// ============================================================
// CARRITO - GASTROCTRL
// ============================================================

function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');

        for (let cookie of cookies) {
            cookie = cookie.trim();

            if (cookie.substring(0, name.length + 1) === `${name}=`) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }

    return cookieValue;
}


// ============================================================
// CONFIGURACIÓN DE URLS
// ============================================================

const CARRITO_URLS = window.CARRITO_URLS || {};


// ============================================================
// ELEMENTOS DEL DOM
// ============================================================

let carritoCartBtn;
let carritoCartCount;
let carritoDrawer;


// ============================================================
// ABRIR / CERRAR DRAWER
// ============================================================

function abrirCarrito() {
    if (!carritoDrawer) return;

    carritoDrawer.classList.remove('pointer-events-none');
    carritoDrawer.setAttribute('aria-hidden', 'false');

    const overlay = document.getElementById('cartOverlay');
    const panel = carritoDrawer.querySelector('aside');

    if (overlay) {
        overlay.classList.remove('opacity-0');
        overlay.classList.add('opacity-100');
    }

    if (panel) {
        panel.classList.remove('translate-x-full');
        panel.classList.add('translate-x-0');
    }

    document.body.classList.add('overflow-hidden');

    cargarCarrito();
}


function cerrarCarrito() {
    if (!carritoDrawer) return;

    const overlay = document.getElementById('cartOverlay');
    const panel = carritoDrawer.querySelector('aside');

    if (overlay) {
        overlay.classList.remove('opacity-100');
        overlay.classList.add('opacity-0');
    }

    if (panel) {
        panel.classList.remove('translate-x-0');
        panel.classList.add('translate-x-full');
    }

    setTimeout(() => {
        carritoDrawer.classList.add('pointer-events-none');
        carritoDrawer.setAttribute('aria-hidden', 'true');
    }, 300);

    document.body.classList.remove('overflow-hidden');
}





// ============================================================
// OBTENER CARRITO DESDE DJANGO
// ============================================================

async function cargarCarrito() {
    if (!CARRITO_URLS.api) return;

    try {
        const response = await fetch(CARRITO_URLS.api);

        if (!response.ok) {
            throw new Error('No se pudo obtener el carrito.');
        }

        const data = await response.json();

        if (data.status === 'ok') {
            actualizarContador(data.total_unidades);
            renderizarCarrito(data);
        }

    } catch (error) {
        console.error('Error al cargar el carrito:', error);
    }
}


// ============================================================
// CONTADOR DEL NAVBAR
// ============================================================

function actualizarContador(totalUnidades) {
    if (!carritoCartCount) return;

    carritoCartCount.textContent = totalUnidades;

    if (totalUnidades > 0) {
        carritoCartCount.classList.remove('hidden');
    } else {
        carritoCartCount.classList.add('hidden');
    }
}


// ============================================================
// RENDERIZAR CARRITO
// ============================================================

function renderizarCarrito(data) {
    const container = document.getElementById('cartItems');
    const totalElement = document.getElementById('cartTotal');
    const emptyElement = document.getElementById('cartEmpty');
    const checkoutBtn = document.getElementById('checkoutBtn');

    if (!container) return;

    container.innerHTML = '';

    if (!data.items || data.items.length === 0) {

        if (emptyElement) {
            emptyElement.classList.remove('hidden');
        }

        if (checkoutBtn) {
            checkoutBtn.classList.add('hidden');
        }

        if (totalElement) {
            totalElement.textContent = '$0';
        }

        return;
    }

    if (emptyElement) {
        emptyElement.classList.add('hidden');
    }

    if (checkoutBtn) {
        checkoutBtn.classList.remove('hidden');
    }

    data.items.forEach(item => {

        const itemElement = document.createElement('div');

        itemElement.className =
            'flex gap-3 p-3 rounded-2xl bg-cream-50 border border-cream-200';

        itemElement.innerHTML = `
            <img
                src="${escapeHtml(item.imagen)}"
                alt="${escapeHtml(item.nombre)}"
                class="w-20 h-20 rounded-xl object-cover shrink-0"
            >

            <div class="flex-1 min-w-0">

                <div class="flex items-start justify-between gap-2">

                    <h4 class="font-semibold text-sm text-coffee-900 truncate">
                        ${escapeHtml(item.nombre)}
                    </h4>

                    <button
                        type="button"
                        onclick="eliminarDelCarrito(${item.producto_id})"
                        class="text-gray-400 hover:text-red-500 transition-colors"
                        aria-label="Eliminar ${escapeHtml(item.nombre)}"
                    >
                        <i class="fa-solid fa-trash-can text-xs"></i>
                    </button>

                </div>

                <p class="text-sm font-bold text-coffee-800 mt-1">
                    $${formatearPrecio(item.precio)}
                </p>

                <div class="flex items-center justify-between mt-3">

                    <div class="flex items-center gap-2">

                        <button
                            type="button"
                            onclick="restarDelCarrito(${item.producto_id})"
                            class="w-7 h-7 rounded-full border border-cream-300 bg-white hover:bg-cream-100 text-coffee-800 transition-colors"
                            aria-label="Restar unidad"
                        >
                            <i class="fa-solid fa-minus text-[9px]"></i>
                        </button>

                        <span class="text-sm font-semibold text-coffee-900 min-w-[20px] text-center">
                            ${item.cantidad}
                        </span>

                        <button
                            type="button"
                            onclick="agregarProductoAlCarrito(${item.producto_id})"
                            class="w-7 h-7 rounded-full bg-coffee-600 hover:bg-coffee-700 text-white transition-colors"
                            aria-label="Agregar unidad"
                        >
                            <i class="fa-solid fa-plus text-[9px]"></i>
                        </button>

                    </div>

                    <span class="text-sm font-bold text-coffee-900">
                        $${formatearPrecio(item.subtotal)}
                    </span>

                </div>

            </div>
        `;

        container.appendChild(itemElement);
    });

    if (totalElement) {
        totalElement.textContent =
            `$${formatearPrecio(data.precio_total)}`;
    }
}


// ============================================================
// AGREGAR PRODUCTO
// ============================================================

async function agregarProductoAlCarrito(productoId) {

    if (!CARRITO_URLS.agregar) return;

    const url = CARRITO_URLS.agregar.replace(
        '/0/',
        `/${productoId}/`
    );

    try {

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('No se pudo agregar el producto.');
        }

        const data = await response.json();

        if (data.status === 'ok') {
            actualizarContador(data.total_unidades);
            await cargarCarrito();
        }

    } catch (error) {
        console.error('Error al agregar producto:', error);
    }
}


// ============================================================
// RESTAR PRODUCTO
// ============================================================

async function restarDelCarrito(productoId) {

    if (!CARRITO_URLS.restar) return;

    const url = CARRITO_URLS.restar.replace(
        '/0/',
        `/${productoId}/`
    );

    try {

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('No se pudo restar el producto.');
        }

        const data = await response.json();

        if (data.status === 'ok') {
            actualizarContador(data.total_unidades);
            await cargarCarrito();
        }

    } catch (error) {
        console.error('Error al restar producto:', error);
    }
}


// ============================================================
// ELIMINAR PRODUCTO
// ============================================================

async function eliminarDelCarrito(productoId) {

    if (!CARRITO_URLS.eliminar) return;

    const url = CARRITO_URLS.eliminar.replace(
        '/0/',
        `/${productoId}/`
    );

    try {

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('No se pudo eliminar el producto.');
        }

        const data = await response.json();

        if (data.status === 'ok') {
            actualizarContador(data.total_unidades);
            await cargarCarrito();
        }

    } catch (error) {
        console.error('Error al eliminar producto:', error);
    }
}


// ============================================================
// CAMBIAR A "SEGUIR PEDIDO"
// ============================================================

function mostrarSeguimiento() {

    const carritoView = document.getElementById('cartView');
    const seguimientoView =
        document.getElementById('trackingView');

    const carritoTab = document.getElementById('cartTab');
    const seguimientoTab =
        document.getElementById('trackingTab');

    if (!carritoView || !seguimientoView) return;

    carritoView.classList.add('hidden');
    seguimientoView.classList.remove('hidden');

    carritoTab?.classList.remove('bg-coffee-600', 'text-white');
    seguimientoTab?.classList.add('bg-coffee-600', 'text-white');
}


// ============================================================
// VOLVER A "MI CARRITO"
// ============================================================

function mostrarCarrito() {

    const carritoView = document.getElementById('cartView');
    const seguimientoView =
        document.getElementById('trackingView');

    const carritoTab = document.getElementById('cartTab');
    const seguimientoTab =
        document.getElementById('trackingTab');

    if (!carritoView || !seguimientoView) return;

    seguimientoView.classList.add('hidden');
    carritoView.classList.remove('hidden');

    seguimientoTab?.classList.remove(
        'bg-coffee-600',
        'text-white'
    );

    carritoTab?.classList.add(
        'bg-coffee-600',
        'text-white'
    );

    cargarCarrito();
}


// ============================================================
// BUSCAR ESTADO DEL PEDIDO
// ============================================================

async function buscarEstadoPedido() {

    const input = document.getElementById('trackingCode');
    const result = document.getElementById('trackingResult');

    if (!input || !result) return;

    const codigo = input.value.trim();

    if (!codigo) {
        result.innerHTML = `
            <p class="text-sm text-red-600">
                Ingresá un código de seguimiento.
            </p>
        `;
        return;
    }

    if (!CARRITO_URLS.seguimiento) return;

    const url = CARRITO_URLS.seguimiento.replace(
        '__CODIGO__',
        encodeURIComponent(codigo)
    );

    result.innerHTML = `
        <div class="text-center py-4 text-coffee-600">
            <i class="fa-solid fa-spinner fa-spin"></i>
            <p class="text-sm mt-2">Consultando pedido...</p>
        </div>
    `;

    try {

        const response = await fetch(url);
        const data = await response.json();

        if (data.status !== 'ok') {
            throw new Error(
                data.mensaje || 'Pedido no encontrado.'
            );
        }

        result.innerHTML = `
            <div class="rounded-2xl bg-cream-50 border border-cream-200 p-4">

                <div class="flex items-center justify-between gap-3">

                    <div>
                        <p class="text-[10px] uppercase tracking-wider text-gray-400">
                            Pedido
                        </p>

                        <p class="font-bold text-coffee-900">
                            #${escapeHtml(data.codigo)}
                        </p>
                    </div>

                    <span class="px-3 py-1 rounded-full bg-coffee-100 text-coffee-800 text-xs font-bold">
                        ${escapeHtml(data.estado)}
                    </span>

                </div>

                <div class="mt-4">

                    <p class="text-[10px] uppercase tracking-wider text-gray-400">
                        Total
                    </p>

                    <p class="text-lg font-bold text-coffee-900">
                        $${formatearPrecio(data.monto_total)}
                    </p>

                </div>

                <div class="mt-4">

                    <p class="text-[10px] uppercase tracking-wider text-gray-400 mb-2">
                        Productos
                    </p>

                    <div class="space-y-2">

                        ${data.detalles.map(detalle => `
                            <div class="flex justify-between gap-3 text-sm">
                                <span class="text-coffee-800">
                                    ${escapeHtml(detalle.producto)}
                                </span>

                                <span class="font-semibold text-coffee-900">
                                    x${detalle.cantidad}
                                </span>
                            </div>
                        `).join('')}

                    </div>

                </div>

            </div>
        `;

    } catch (error) {

        result.innerHTML = `
            <div class="rounded-2xl bg-red-50 border border-red-200 p-4 text-sm text-red-700">
                ${escapeHtml(error.message)}
            </div>
        `;
    }
}


// ============================================================
// FORMATEAR PRECIO
// ============================================================

function formatearPrecio(valor) {

    return Number(valor).toLocaleString('es-AR', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    });
}


// ============================================================
// ESCAPAR HTML
// ============================================================

function escapeHtml(value) {

    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}


// ============================================================
// CARGA INICIAL
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
    // El drawer está dentro de base.html, pero se encuentra
    // después de los scripts. Por eso los elementos se obtienen
    // cuando el DOM ya está completamente cargado.
    carritoCartBtn = document.getElementById('cartBtn');
    carritoCartCount = document.getElementById('cartCount');
    carritoDrawer = document.getElementById('drawerCarrito');

    if (carritoCartBtn) {
        carritoCartBtn.addEventListener('click', abrirCarrito);
    }

    cargarCarrito();
});