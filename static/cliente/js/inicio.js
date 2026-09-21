/* ==========================================================================
   Lógica JavaScript - GastroCtrl
   ========================================================================== */

// Configuración de Tailwind CSS
tailwind.config = {
    theme: {
        extend: {
            colors: {
                cream: {
                    50: '#fcfaf7',
                    100: '#f7f3ed',
                    200: '#efe6d8',
                    300: '#e3d2be',
                },
                coffee: {
                    500: '#a67c52',
                    600: '#8c6343',
                    700: '#6e4b30',
                    800: '#4e3320',
                    900: '#332013',
                },
                warmbrown: '#947153',
                terracotta: '#b87d4b',
            },
            fontFamily: {
                serif: ['"Playfair Display"', 'serif'],
                sans: ['"Plus Jakarta Sans"', 'sans-serif'],
            }
        }
    }
};

// Variables de Estado
let cart = [];
let lastOrder = null;
let isAdminLoggedIn = false;
let adminName = "Valentina";

// Referencias DOM
let profileBtn, profileDropdown, loggedOutView, loggedInView, adminNameDisplay;
let openAdminLoginBtn, logoutBtn, loginModal, closeLoginModalBtn;
let cartBtn, cartDrawer, cartBackdrop, closeCartBtn, cartCount;
let cartItemsContainer, cartSubtotal, cartTotal, mobileMenuBtn, mobileMenu;

// Inicialización cuando el DOM está completamente cargado
document.addEventListener('DOMContentLoaded', () => {
    // Captura de elementos DOM
    profileBtn = document.getElementById('profileBtn');
    profileDropdown = document.getElementById('profileDropdown');
    loggedOutView = document.getElementById('loggedOutView');
    loggedInView = document.getElementById('loggedInView');
    adminNameDisplay = document.getElementById('adminNameDisplay');
    openAdminLoginBtn = document.getElementById('openAdminLoginBtn');
    logoutBtn = document.getElementById('logoutBtn');
    
    loginModal = document.getElementById('loginModal');
    closeLoginModalBtn = document.getElementById('closeLoginModalBtn');

    cartBtn = document.getElementById('cartBtn');
    cartDrawer = document.getElementById('cartDrawer');
    cartBackdrop = document.getElementById('cartBackdrop');
    closeCartBtn = document.getElementById('closeCartBtn');
    cartCount = document.getElementById('cartCount');
    cartItemsContainer = document.getElementById('cartItemsContainer');
    cartSubtotal = document.getElementById('cartSubtotal');
    cartTotal = document.getElementById('cartTotal');

    mobileMenuBtn = document.getElementById('mobileMenuBtn');
    mobileMenu = document.getElementById('mobileMenu');

        // Event Listeners del Perfil
    if (profileBtn && profileDropdown) {
        profileBtn.addEventListener('click', (e) => {
            e.stopPropagation();

            const isHidden = profileDropdown.classList.contains('hidden');

            if (isHidden) {
                profileDropdown.classList.remove('hidden');

                setTimeout(() => {
                    profileDropdown.classList.remove('opacity-0', 'scale-95');
                }, 10);
            } else {
                closeProfileDropdown();
            }
        });

        document.addEventListener('click', (e) => {
            if (!profileDropdown.contains(e.target) && !profileBtn.contains(e.target)) {
                closeProfileDropdown();
            }
        });
    }

    // Modal de Login Admin
    if (openAdminLoginBtn && loginModal) {
        openAdminLoginBtn.addEventListener('click', () => {
            closeProfileDropdown();
            openModal(loginModal);
        });
    }

    if (closeLoginModalBtn && loginModal) {
        closeLoginModalBtn.addEventListener('click', () => {
            closeModal(loginModal);
        });
    }

    // Logout
    if (logoutBtn && loggedOutView && loggedInView) {
        logoutBtn.addEventListener('click', () => {
            isAdminLoggedIn = false;
            loggedOutView.classList.remove('hidden');
            loggedInView.classList.add('hidden');
            closeProfileDropdown();
            showToast('Sesión de administración cerrada');
        });
    }

    // Controles del Carrito Drawer
    if (cartBtn) {
        cartBtn.addEventListener('click', openCart);
    }

    if (closeCartBtn) {
        closeCartBtn.addEventListener('click', closeCart);
    }

    if (cartBackdrop) {
        cartBackdrop.addEventListener('click', closeCart);
    }

    // Menú Mobile
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }

        // Filtros de Categorías
    const filterBtns = document.querySelectorAll('.filter-btn');
    const productCards = document.querySelectorAll('.product-card');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {

            // Cambiar estado visual del botón seleccionado
            filterBtns.forEach(b => {
                b.classList.remove('active', 'bg-coffee-600', 'text-white');
                b.classList.add('bg-white', 'text-coffee-800');
            });

            btn.classList.add('active', 'bg-coffee-600', 'text-white');
            btn.classList.remove('bg-white', 'text-coffee-800');

            // Obtener categoría seleccionada
            const category = btn.getAttribute('data-category');

            // Mostrar u ocultar productos
            productCards.forEach(card => {
                const productCategory = card.getAttribute('data-category');

                if (category === 'todos' || productCategory === category) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });

    // Renderizado inicial del carrito
    updateCartUI();
});   


/* ==========================================================================
   Funciones Auxiliares y Globales
   ========================================================================== */

function closeProfileDropdown() {
    if (!profileDropdown) return;
    profileDropdown.classList.add('opacity-0', 'scale-95');
    setTimeout(() => {
        profileDropdown.classList.add('hidden');
    }, 200);
}

function openModal(modal) {
    if (!modal) return;
    modal.classList.remove('pointer-events-none', 'opacity-0');
    modal.firstElementChild.classList.remove('scale-95');
}

function closeModal(modal) {
    if (!modal) return;
    modal.classList.add('pointer-events-none', 'opacity-0');
    modal.firstElementChild.classList.add('scale-95');
}

function handleLogin(e) {
    e.preventDefault();

    const usernameInput = document.getElementById('adminUserInput');
    const passwordInput = document.getElementById('adminPasswordInput');
    const errorMessage = document.getElementById('adminLoginError');

    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();

    if (!username || !password) {
        errorMessage.textContent = 'Completá usuario y contraseña para continuar.';
        errorMessage.classList.remove('hidden');
        return;
    }

    errorMessage.classList.add('hidden');

    adminName = username;
    isAdminLoggedIn = true;

    if (adminNameDisplay) {
        adminNameDisplay.textContent = `Admin: ${adminName}`;
    }

    loggedOutView.classList.add('hidden');
    loggedInView.classList.remove('hidden');

    closeModal(loginModal);

    const adminUrl = loginModal.dataset.adminUrl;

    if (adminUrl) {
        window.location.href = adminUrl;
    }
}

function openCart() {
    if (!cartBackdrop || !cartDrawer) return;
    cartBackdrop.classList.remove('pointer-events-none', 'opacity-0');
    cartDrawer.classList.remove('translate-x-full');
    document.body.classList.add('overflow-hidden');
}

function closeCart() {
    if (!cartBackdrop || !cartDrawer) return;
    cartBackdrop.classList.add('pointer-events-none', 'opacity-0');
    cartDrawer.classList.add('translate-x-full');
    document.body.classList.remove('overflow-hidden');
}

function switchCartTab(tab) {
    const tabCartBtn = document.getElementById('tabCartBtn');
    const tabTrackBtn = document.getElementById('tabTrackBtn');
    const cartView = document.getElementById('cartView');
    const trackView = document.getElementById('trackView');

    if (tab === 'cart') {
        cartView.classList.remove('hidden');
        trackView.classList.add('hidden');
        tabCartBtn.classList.add('bg-white', 'text-coffee-900', 'shadow-xs');
        tabCartBtn.classList.remove('text-coffee-700');
        tabTrackBtn.classList.remove('bg-white', 'text-coffee-900', 'shadow-xs');
        tabTrackBtn.classList.add('text-coffee-700');
    } else {
        cartView.classList.add('hidden');
        trackView.classList.remove('hidden');
        tabTrackBtn.classList.add('bg-white', 'text-coffee-900', 'shadow-xs');
        tabTrackBtn.classList.remove('text-coffee-700');
        tabCartBtn.classList.remove('bg-white', 'text-coffee-900', 'shadow-xs');
        tabCartBtn.classList.add('text-coffee-700');
    }
}

function toggleAddressInput() {
    const deliveryType = document.querySelector('input[name="deliveryType"]:checked').value;
    const addressField = document.getElementById('addressField');
    const shippingCost = document.getElementById('shippingCost');

    if (deliveryType === 'Envío a domicilio') {
        addressField.classList.remove('hidden');
        shippingCost.textContent = '$800';
        shippingCost.className = 'font-medium text-coffee-900';
    } else {
        addressField.classList.add('hidden');
        shippingCost.textContent = 'Gratis (Retiro)';
        shippingCost.className = 'font-medium text-emerald-700';
    }
    updateCartUI();
}

function addToCart(id, name, price, image) {
    const existingItem = cart.find(item => item.id === id);
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({ id, name, price, image, quantity: 1 });
    }
    updateCartUI();
    showToast(`${name} añadido al carrito`);
}

function changeQuantity(id, delta) {
    const item = cart.find(item => item.id === id);
    if (item) {
        item.quantity += delta;
        if (item.quantity <= 0) {
            cart = cart.filter(i => i.id !== id);
        }
    }
    updateCartUI();
}

function removeFromCart(id) {
    cart = cart.filter(item => item.id !== id);
    updateCartUI();
    showToast('Producto eliminado del carrito');
}

function updateCartUI() {
    if (!cartCount || !cartItemsContainer || !cartSubtotal || !cartTotal) return;

    // Actualizar Contador
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    cartCount.textContent = totalItems;

    // Renderizar Productos
    if (cart.length === 0) {
        cartItemsContainer.innerHTML = `
            <div class="flex flex-col items-center justify-center h-64 text-center text-gray-400">
                <i class="fa-solid fa-basket-shopping text-4xl mb-3 text-cream-300"></i>
                <p class="text-sm font-medium text-coffee-800">Tu carrito está vacío</p>
                <p class="text-xs text-gray-400 mt-1">Descubre nuestros productos horneados e agrégalos aquí.</p>
            </div>
        `;
    } else {
        cartItemsContainer.innerHTML = cart.map(item => `
            <div class="flex items-center gap-3.5 bg-cream-50/80 p-3 rounded-2xl border border-cream-200/80 shadow-2xs">
                <img src="${item.image}" alt="${item.name}" class="w-14 h-14 rounded-xl object-cover shrink-0">
                <div class="flex-grow min-w-0">
                    <h4 class="text-xs font-bold text-coffee-900 truncate">${item.name}</h4>
                    <p class="text-xs font-bold text-coffee-600 mt-0.5">$${(item.price * item.quantity).toLocaleString('es-AR')}</p>
                    <div class="flex items-center gap-2 mt-1.5">
                        <button onclick="changeQuantity(${item.id}, -1)" class="w-5 h-5 rounded-md bg-white border border-cream-300 text-coffee-800 text-[10px] flex items-center justify-center hover:bg-cream-100">
                            <i class="fa-solid fa-minus"></i>
                        </button>
                        <span class="text-xs font-semibold text-coffee-900 w-4 text-center">${item.quantity}</span>
                        <button onclick="changeQuantity(${item.id}, 1)" class="w-5 h-5 rounded-md bg-white border border-cream-300 text-coffee-800 text-[10px] flex items-center justify-center hover:bg-cream-100">
                            <i class="fa-solid fa-plus"></i>
                        </button>
                    </div>
                </div>
                <button onclick="removeFromCart(${item.id})" class="text-gray-400 hover:text-rose-500 p-1.5 transition-colors">
                    <i class="fa-regular fa-trash-can text-sm"></i>
                </button>
            </div>
        `).join('');
    }

    // Calcular Subtotal y Total
    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const deliveryType = document.querySelector('input[name="deliveryType"]:checked')?.value || 'Retiro en local';
    const shippingFee = (deliveryType === 'Envío a domicilio' && cart.length > 0) ? 800 : 0;
    const grandTotal = subtotal + shippingFee;

    cartSubtotal.textContent = `$${subtotal.toLocaleString('es-AR')}`;
    cartTotal.textContent = `$${grandTotal.toLocaleString('es-AR')}`;
}

function submitOrder() {
    if (cart.length === 0) {
        showToast('Tu carrito está vacío');
        return;
    }

    const deliveryType = document.querySelector('input[name="deliveryType"]:checked').value;
    const addressInput = document.getElementById('deliveryAddress').value.trim();

    if (deliveryType === 'Envío a domicilio' && !addressInput) {
        showToast('Ingresa la dirección para el envío');
        document.getElementById('deliveryAddress').focus();
        return;
    }

    const orderNum = 'MS-' + Math.floor(1000 + Math.random() * 9000);
    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const shippingFee = (deliveryType === 'Envío a domicilio') ? 800 : 0;
    const total = subtotal + shippingFee;

    const now = new Date();
    const timeString = now.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' });
    const dateString = now.toLocaleDateString('es-AR');

    lastOrder = {
        id: orderNum,
        date: `${dateString} ${timeString}`,
        items: [...cart],
        subtotal: subtotal,
        shippingFee: shippingFee,
        total: total,
        deliveryType: deliveryType,
        address: deliveryType === 'Envío a domicilio' ? addressInput : null
    };

    // Renderizar detalles de seguimiento
    document.getElementById('orderIdTag').textContent = `#${lastOrder.id}`;
    document.getElementById('orderTimeText').textContent = `Enviado hoy a las ${timeString}`;
    
    const summaryContainer = document.getElementById('orderSummaryItems');
    const shippingText = lastOrder.shippingFee > 0 
        ? `$${lastOrder.shippingFee.toLocaleString('es-AR')}` 
        : 'Gratis (Retiro en local)';

    summaryContainer.innerHTML = `
        <div class="space-y-3 border-b border-cream-200/80 pb-3.5">
            ${lastOrder.items.map(item => `
                <div class="flex justify-between items-center gap-3 text-xs">
                    <div class="flex items-center gap-2 min-w-0">
                        <span class="bg-cream-200/80 text-coffee-900 font-bold px-2 py-0.5 rounded-md text-[11px] shrink-0">${item.quantity}x</span>
                        <span class="text-coffee-900 font-medium truncate">${item.name}</span>                     </div>                     <span class="font-bold text-coffee-900 shrink-0">$${(item.price * item.quantity).toLocaleString('es-AR')}</span>
                </div>
            `).join('')}
        </div>
        <div class="space-y-2.5 pt-1 text-xs">
            <div class="flex justify-between items-center text-coffee-800">
                <span class="font-medium">Subtotal de productos</span>
                <span class="font-semibold text-coffee-900">$${lastOrder.subtotal.toLocaleString('es-AR')}</span>
            </div>
            <div class="flex justify-between items-center text-coffee-800">
                <span class="font-medium">Costo de envío / Modalidad</span>
                <span class="font-semibold ${lastOrder.shippingFee > 0 ? 'text-coffee-900' : 'text-emerald-700'}">${shippingText}</span>
            </div>
            <div class="flex justify-between items-center font-bold text-coffee-900 pt-3 border-t border-cream-300 text-sm">
                <span>Total Pagado</span>
                <span class="text-base font-serif-title text-coffee-900">$${lastOrder.total.toLocaleString('es-AR')}</span>
            </div>
        </div>
    `;

    document.getElementById('noActiveOrder').classList.add('hidden');
    document.getElementById('activeOrderDetails').classList.remove('hidden');

    // Limpiar carrito y cambiar de pestaña
    cart = [];
    updateCartUI();
    switchCartTab('track');
    showToast('¡Pedido enviado con éxito!');
}

function downloadPDFReceipt() {
    if (!lastOrder) {
        showToast('No hay pedido registrado');
        return;
    }

    try {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF({
            unit: 'mm',
            format: 'a4'
        });

        // Banner de encabezado
        doc.setFillColor(110, 75, 48);
        doc.rect(0, 0, 210, 28, 'F');

        doc.setTextColor(255, 255, 255);
        doc.setFont("helvetica", "bold");
        doc.setFontSize(20);
        doc.text("GastroCtrl", 15, 15);

        doc.setFont("helvetica", "normal");
        doc.setFontSize(9);
        doc.text("Café & Pastelería Artesanal", 15, 21);
        doc.text("COMPROBANTE DE COMPRA", 145, 15);

        // Información del pedido
        doc.setTextColor(51, 32, 19);
        doc.setFontSize(10);
        doc.setFont("helvetica", "bold");
        doc.text(`N° de Pedido: #${lastOrder.id}`, 15, 38);

        doc.setFont("helvetica", "normal");
        doc.text(`Fecha y Hora: ${lastOrder.date}`, 15, 44);
        doc.text(`Modalidad: ${lastOrder.deliveryType}`, 15, 50);
        if (lastOrder.address) {
            doc.text(`Dirección: ${lastOrder.address}`, 15, 56);
        }

        // Encabezados de la tabla
        let startY = lastOrder.address ? 64 : 58;
        doc.setFillColor(247, 243, 237);
        doc.rect(15, startY, 180, 8, 'F');

        doc.setFont("helvetica", "bold");
        doc.setFontSize(9);
        doc.text("Producto", 20, startY + 5.5);
        doc.text("Cant.", 120, startY + 5.5);
        doc.text("Precio Unit.", 145, startY + 5.5);
        doc.text("Subtotal", 175, startY + 5.5);

        startY += 13;
        doc.setFont("helvetica", "normal");

        // Filas de la tabla
        lastOrder.items.forEach((item) => {
            doc.text(item.name.substring(0, 36), 20, startY);
            doc.text(`${item.quantity}`, 122, startY);
            doc.text(`$${item.price.toLocaleString('es-AR')}`, 145, startY);
            doc.text(`$${(item.price * item.quantity).toLocaleString('es-AR')}`, 175, startY);
            startY += 7;
        });

        // Línea divisoria
        doc.setDrawColor(212, 194, 174);
        doc.line(15, startY + 2, 195, startY + 2);
        startY += 10;

        // Subtotal y Total
        if (lastOrder.shippingFee > 0) {
            doc.text(`Subtotal: $${lastOrder.subtotal.toLocaleString('es-AR')}`, 140, startY);
            startY += 6;
            doc.text(`Envío: $${lastOrder.shippingFee.toLocaleString('es-AR')}`, 140, startY);
            startY += 6;
        }

        doc.setFont("helvetica", "bold");
        doc.setFontSize(11);
        doc.text(`TOTAL FINAL: $${lastOrder.total.toLocaleString('es-AR')}`, 140, startY);

        // Pie de página
        doc.setFontSize(8);
        doc.setFont("helvetica", "italic");
        doc.setTextColor(120, 120, 120);
        doc.text("¡Gracias por elegir GastroCtrl! Conserva este comprobante.", 105, 275, { align: "center" });

        // Guardar archivo PDF
        doc.save(`Comprobante_${lastOrder.id}.pdf`);
        showToast('Comprobante PDF descargado');
    } catch (error) {
        console.error("Error al generar PDF:", error);
        showToast('Error al generar el comprobante PDF');
    }
}

function showToast(message) {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = 'pointer-events-auto bg-coffee-900 text-white text-xs font-medium px-4 py-3 rounded-2xl shadow-xl flex items-center gap-3 animate-toast border border-coffee-700';
    toast.innerHTML = `
        <i class="fa-solid fa-circle-check text-emerald-400 text-sm"></i>
        <span>${message}</span>
    `;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 2500);
}