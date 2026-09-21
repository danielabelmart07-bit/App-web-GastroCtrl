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
    const subtotalElement = document.getElementById('cartSubtotal');
    const shippingElement = document.getElementById('cartShipping');
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

        if (subtotalElement) subtotalElement.textContent = '$0';
        if (shippingElement) shippingElement.textContent = '$0';
        if (totalElement) totalElement.textContent = '$0';
        actualizarBotonesModalidad(data.modalidad || 'RETIRO');

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

    if (subtotalElement) {
        subtotalElement.textContent = `${formatearPrecio(data.subtotal ?? data.precio_total)}`;
    }

    if (shippingElement) {
        shippingElement.textContent =
            data.envio > 0 ? `${formatearPrecio(data.envio)}` : 'Gratis';
    }

    if (totalElement) {
        totalElement.textContent =
            `${formatearPrecio(data.precio_total)}`;
    }

    actualizarBotonesModalidad(data.modalidad || 'RETIRO');
}

function actualizarBotonesModalidad(modalidad) {
    const pickup = document.getElementById('deliveryPickupBtn');
    const delivery = document.getElementById('deliveryHomeBtn');

    [pickup, delivery].forEach(btn => {
        if (!btn) return;
        btn.classList.remove('border-coffee-600', 'bg-cream-100', 'ring-1', 'ring-coffee-500');
        btn.classList.add('border-cream-200', 'bg-white');
    });

    const active = modalidad === 'DELIVERY' ? delivery : pickup;
    if (active) {
        active.classList.remove('border-cream-200', 'bg-white');
        active.classList.add('border-coffee-600', 'bg-cream-100', 'ring-1', 'ring-coffee-500');
    }
}

async function seleccionarModalidadEntrega(modalidad) {
    if (!CARRITO_URLS.modalidad) return;

    try {
        const response = await fetch(CARRITO_URLS.modalidad, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': obtenerCsrfToken(),
            },
            body: JSON.stringify({ modalidad }),
        });

        const data = await response.json();

        if (data.status !== 'ok') {
            throw new Error(data.mensaje || 'No se pudo actualizar la modalidad.');
        }

        const subtotalEl = document.getElementById('cartSubtotal');
        const shippingEl = document.getElementById('cartShipping');
        const totalEl = document.getElementById('cartTotal');

        if (subtotalEl) subtotalEl.textContent = `${formatearPrecio(data.subtotal)}`;
        if (shippingEl) shippingEl.textContent = data.envio > 0 ? `${formatearPrecio(data.envio)}` : 'Gratis';
        if (totalEl) totalEl.textContent = `${formatearPrecio(data.total)}`;

        actualizarBotonesModalidad(modalidad);
    } catch (error) {
        console.error('Error al cambiar modalidad:', error);
    }
}

function obtenerCsrfToken() {
    const cookie = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='));

    return cookie ? decodeURIComponent(cookie.split('=')[1]) : '';
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

let ultimoPedidoConsultado = null;

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

        ultimoPedidoConsultado = data;

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

                <div class="mt-4 rounded-xl bg-white border border-cream-200 p-3 space-y-2">

                    <div class="flex justify-between text-xs">
                        <span class="text-coffee-600">Modalidad</span>
                        <span class="font-semibold text-coffee-900">${escapeHtml(data.modalidad_entrega)}</span>
                    </div>

                    <div class="flex justify-between text-xs">
                        <span class="text-coffee-600">Subtotal</span>
                        <span class="font-semibold text-coffee-900">${formatearPrecio(data.subtotal)}</span>
                    </div>

                    <div class="flex justify-between text-xs">
                        <span class="text-coffee-600">Envío</span>
                        <span class="font-semibold text-coffee-900">${data.costo_envio > 0 ? "$" + formatearPrecio(data.costo_envio) : "Gratis"}</span>
                    </div>

                    <div class="flex justify-between items-center pt-2 border-t border-cream-200">
                        <span class="text-sm font-bold text-coffee-700">Total</span>
                        <span class="text-lg font-bold text-coffee-900">${formatearPrecio(data.monto_total)}</span>
                    </div>

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

                <button type="button" onclick="descargarComprobanteUltimoPedido()" class="w-full mt-4 py-3 rounded-2xl bg-white border border-cream-300 hover:bg-cream-100 text-coffee-800 text-sm font-bold transition-colors">
                    <i class="fa-solid fa-file-pdf mr-2"></i>
                    Descargar comprobante
                </button>

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
// ACTUALIZACION AUTOMATICA DEL SEGUIMIENTO
// ============================================================

setInterval(() => {
    const view = document.getElementById('trackingView');
    const input = document.getElementById('trackingCode');

    if (
        view &&
        !view.classList.contains('hidden') &&
        input &&
        input.value.trim()
    ) {
        buscarEstadoPedido();
    }
}, 10000);


// ============================================================
// DESCARGAR COMPROBANTE
// ============================================================

function descargarComprobanteUltimoPedido() {
    if (ultimoPedidoConsultado) {
        descargarComprobante(ultimoPedidoConsultado);
    }
}

function descargarComprobante(pedido) {
    if (!window.jspdf || !window.jspdf.jsPDF) {
        alert('No se pudo cargar el generador de comprobantes.');
        return;
    }

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({ unit: 'mm', format: 'a4' });

    const coffee = [51, 32, 19];
    const brown = [140, 99, 67];
    const cream = [247, 243, 237];
    const light = [252, 250, 247];
    const green = [22, 101, 52];
    const darkGray = [95, 84, 74];
    let y = 22;

    // Encabezado premium
    doc.setFillColor(...coffee);
    doc.roundedRect(15, 12, 180, 38, 5, 5, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(24);
    doc.text('GastroCtrl', 25, 28);
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9);
    doc.text('CAFE & PASTELERIA ARTESANAL', 25, 35);
    doc.setFontSize(10);
    doc.text('COMPROBANTE DE PEDIDO', 182, 28, { align: 'right' });

    y = 64;
    doc.setTextColor(...coffee);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(12);
    doc.text('Pedido #' + String(pedido.codigo || '---'), 20, y);
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9);
    doc.setTextColor(...darkGray);
    doc.text('Conserva este codigo para consultar el estado de tu pedido.', 20, y + 7);

    // Estado
    doc.setFillColor(...cream);
    doc.roundedRect(140, 56, 50, 20, 4, 4, 'F');
    doc.setTextColor(...brown);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(8);
    doc.text('ESTADO', 165, 63, { align: 'center' });
    doc.setTextColor(...coffee);
    doc.setFontSize(10);
    doc.text(String(pedido.estado || 'Pendiente'), 165, 70, { align: 'center' });

    y = 92;
    doc.setFillColor(...light);
    doc.roundedRect(15, y - 8, 180, 18, 3, 3, 'F');
    doc.setTextColor(...darkGray);
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9);
    doc.text('Gracias por elegir GastroCtrl. Este comprobante resume tu compra.', 20, y + 3);

    y = 123;
    doc.setTextColor(...coffee);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(12);
    doc.text('Detalle de la compra', 20, y);
    y += 9;

    // Cabecera de tabla
    doc.setFillColor(...coffee);
    doc.roundedRect(15, y - 6, 180, 10, 2, 2, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(8);
    doc.text('PRODUCTO', 20, y);
    doc.text('CANT.', 145, y);
    doc.text('SUBTOTAL', 188, y, { align: 'right' });
    y += 10;

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9);
    doc.setTextColor(...coffee);

    (pedido.detalles || []).forEach((detalle, index) => {
        if (index % 2 === 0) {
            doc.setFillColor(...light);
            doc.roundedRect(15, y - 6, 180, 10, 2, 2, 'F');
        }

        const nombre = String(detalle.producto || 'Producto');
        const cantidad = String(detalle.cantidad || 1);
        const subtotal = detalle.subtotal !== undefined ? '$' + formatearPrecio(detalle.subtotal) : '';

        doc.text(nombre.substring(0, 55), 20, y);
        doc.text(cantidad, 148, y, { align: 'center' });
        doc.text(subtotal, 188, y, { align: 'right' });
        y += 10;

        if (y > 265) {
            doc.addPage();
            y = 25;
        }
    });

    // Total destacado
    y += 5;
    doc.setFillColor(...brown);
    doc.roundedRect(115, y, 80, 25, 4, 4, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(8);
    doc.text('TOTAL DEL PEDIDO', 155, y + 8, { align: 'center' });
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(15);
    doc.text('$' + formatearPrecio(pedido.monto_total || 0), 155, y + 18, { align: 'center' });

    // Pie
    doc.setTextColor(...darkGray);
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(8);
    doc.text('GastroCtrl | Cafe & Pasteleria Artesanal', 20, 282);
    doc.text('Gracias por tu compra.', 190, 282, { align: 'right' });

    doc.save('comprobante-' + String(pedido.codigo || 'pedido') + '.pdf');
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