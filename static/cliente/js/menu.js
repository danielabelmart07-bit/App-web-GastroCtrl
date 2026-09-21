// Comprehensive Menu Items Database
const MENU_PRODUCTS = [
    {
        id: 1,
        name: "Croissant de Almendras",
        category: "pasteleria",
        categoryLabel: "Pastelería",
        price: 3200,
        description: "Croissant artesanal francés relleno de crema frangipane de almendras y espolvoreado con azúcar impalpable.",
        image: "https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&q=80&w=800",
        badge: "Más Vendido"
    },
    {
        id: 2,
        name: "Tarta de Frutillas y Crema",
        category: "pasteleria",
        categoryLabel: "Pastelería",
        price: 4500,
        description: "Masa sablée crocante, suave crema pastelera a la vainilla de Madagascar y frutillas frescas de estación.",
        image: "https://images.unsplash.com/photo-1565958011703-44f9829ba187?auto=format&fit=crop&q=80&w=800",
        badge: "Destacado"
    },
    {
        id: 3,
        name: "Café Latte Especialidad",
        category: "cafeteria",
        categoryLabel: "Cafetería",
        price: 2800,
        description: "Doble shot de espresso de grano colombiano con leche cremada textura terciopelo y delicado latte art.",
        image: "https://images.unsplash.com/photo-1534778101976-62847782c213?auto=format&fit=crop&q=80&w=800",
        badge: "Especialidad"
    },
    {
        id: 4,
        name: "Cheesecake Frutos Rojos",
        category: "pasteleria",
        categoryLabel: "Pastelería",
        price: 4800,
        description: "Textura suave y cremosa al estilo New York, sobre galleta de mantequilla con reducción artesanal de frutos del bosque.",
        image: "https://images.unsplash.com/photo-1533134242443-d4fd215305ad?auto=format&fit=crop&q=80&w=800"
    },
    {
        id: 5,
        name: "Pan de Masa Madre Tradicional",
        category: "panaderia",
        categoryLabel: "Panadería",
        price: 3600,
        description: "Hogaza rústica elaborada con fermentación lenta de 48 horas. Corteza crujiente y miga aireada e hidratada.",
        image: "https://images.unsplash.com/photo-1589367920969-ab8e050bbb04?auto=format&fit=crop&q=80&w=800",
        badge: "48h Fermentación"
    },
    {
        id: 6,
        name: "Box Macarons (6 Unidades)",
        category: "pasteleria",
        categoryLabel: "Pastelería",
        price: 5200,
        description: "Caja regalo con surtido de macarons franceses: pistacho, maracuyá, frambuesa, ganache belga y avellanas.",
        image: "https://images.unsplash.com/photo-1569864358642-9d1684040f43?auto=format&fit=crop&q=80&w=800"
    },
    {
        id: 7,
        name: "Cappuccino Italiano Clásico",
        category: "cafeteria",
        categoryLabel: "Cafetería",
        price: 3000,
        description: "Espresso concentrado con capas equilibradas de leche caliente y espuma densa espolvoreada con cacao amargo.",
        image: "https://images.unsplash.com/photo-1572442388796-11668a67e53d?auto=format&fit=crop&q=80&w=800"
    },
    {
        id: 8,
        name: "Baguette Rústica Francesa",
        category: "panaderia",
        categoryLabel: "Panadería",
        price: 2200,
        description: "Pan de receta tradicional parisina, elaborado con harinas orgánicas y horneado en piso de piedra.",
        image: "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&q=80&w=800"
    },
    {
        id: 9,
        name: "Éclair de Chocolate Belga",
        category: "pasteleria",
        categoryLabel: "Pastelería",
        price: 3400,
        description: "Masa choux ligera rellena de suave crema pastelera de chocolate semi-amargo y glaseado espejado.",
        image: "https://images.unsplash.com/photo-1621236378699-8597faf6a176?auto=format&fit=crop&q=80&w=800"
    },
    {
        id: 10,
        name: "Pan Brioche de Mantequilla",
        category: "panaderia",
        categoryLabel: "Panadería",
        price: 3900,
        description: "Pan tierno de miga dorada e intensa riqueza aromática gracias a manteca purificada de primera calidad.",
        image: "https://images.unsplash.com/photo-1586444248902-2f64eddc13df?auto=format&fit=crop&q=80&w=800"
    },
    {
        id: 11,
        name: "Flat White Doble Shot",
        category: "cafeteria",
        categoryLabel: "Cafetería",
        price: 3100,
        description: "Doble ristretto extraído a precisión de granos Etíopes combinado con una fina capa micro-cremada de leche.",
        image: "https://images.unsplash.com/photo-1517256064527-09c73fc73e38?auto=format&fit=crop&q=80&w=800"
    },
    {
        id: 12,
        name: "Lemon Pie Artesanal",
        category: "pasteleria",
        categoryLabel: "Pastelería",
        price: 4300,
        description: "Base crocante con curd de limones amarillos naturales y un vistoso merengue italiano flameado.",
        image: "https://images.unsplash.com/photo-1519869325930-281384150729?auto=format&fit=crop&q=80&w=800"
    }
];

// State variables
let cart = [];
let lastOrder = null;
let isAdminLoggedIn = false;
let adminName = "Valentina";
let activeCategory = "todos";
let searchQuery = "";
let currentSort = "featured";

// DOM elements
const profileBtn = document.getElementById('profileBtn');
const profileDropdown = document.getElementById('profileDropdown');
const loggedOutView = document.getElementById('loggedOutView');
const loggedInView = document.getElementById('loggedInView');
const adminNameDisplay = document.getElementById('adminNameDisplay');
const openAdminLoginBtn = document.getElementById('openAdminLoginBtn');
const logoutBtn = document.getElementById('logoutBtn');

const loginModal = document.getElementById('loginModal');
const closeLoginModalBtn = document.getElementById('closeLoginModalBtn');

const cartBtn = document.getElementById('cartBtn');
const cartDrawer = document.getElementById('cartDrawer');
const cartBackdrop = document.getElementById('cartBackdrop');
const closeCartBtn = document.getElementById('closeCartBtn');
const cartCount = document.getElementById('cartCount');
const cartItemsContainer = document.getElementById('cartItemsContainer');
const cartSubtotal = document.getElementById('cartSubtotal');
const cartTotal = document.getElementById('cartTotal');

const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const mobileMenu = document.getElementById('mobileMenu');

const searchInput = document.getElementById('searchInput');
const clearSearchBtn = document.getElementById('clearSearchBtn');
const sortSelect = document.getElementById('sortSelect');
const menuProductsGrid = document.getElementById('menuProductsGrid');
const emptyState = document.getElementById('emptyState');
const productsCountText = document.getElementById('productsCountText');
const resetFiltersBtn = document.getElementById('resetFiltersBtn');

// Render & Filter Products Matrix
function renderMenuProducts() {
    let filtered = MENU_PRODUCTS.filter(item => {
        const matchesCategory = (activeCategory === 'todos') || (item.category === activeCategory);
        const query = searchQuery.toLowerCase().trim();
        const matchesSearch = !query || 
                             item.name.toLowerCase().includes(query) || 
                             item.description.toLowerCase().includes(query) ||
                             item.categoryLabel.toLowerCase().includes(query);
        return matchesCategory && matchesSearch;
    });

    // Sorting logic
    if (currentSort === 'price-low') {
        filtered.sort((a, b) => a.price - b.price);
    } else if (currentSort === 'price-high') {
        filtered.sort((a, b) => b.price - a.price);
    } else if (currentSort === 'name-asc') {
        filtered.sort((a, b) => a.name.localeCompare(b.name));
    }

    // Update Counter Text
    productsCountText.textContent = `Mostrando ${filtered.length} de ${MENU_PRODUCTS.length} productos`;

    if (searchQuery || activeCategory !== 'todos') {
        resetFiltersBtn.classList.remove('hidden');
    } else {
        resetFiltersBtn.classList.add('hidden');
    }

    if (filtered.length === 0) {
        menuProductsGrid.innerHTML = '';
        emptyState.classList.remove('hidden');
        return;
    }

    emptyState.classList.add('hidden');

    // Render Product Cards
    menuProductsGrid.innerHTML = filtered.map(item => `
        <div class="product-card bg-white rounded-3xl overflow-hidden border border-cream-200/80 hover-lift flex flex-col justify-between transition-all duration-300">
            <div class="relative overflow-hidden aspect-[4/3] group">
                <img src="${item.image}" 
                     alt="${item.name}" 
                     loading="lazy"
                     class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
                <span class="absolute top-4 left-4 bg-white/90 backdrop-blur-md text-coffee-800 text-[11px] font-bold px-3 py-1 rounded-full uppercase tracking-wider shadow-xs">
                    ${item.categoryLabel}
                </span>
                ${item.badge ? `
                    <span class="absolute top-4 right-4 bg-coffee-600 text-white text-[10px] font-bold px-2.5 py-1 rounded-full uppercase tracking-wider shadow-xs">
                        ${item.badge}
                    </span>
                ` : ''}
            </div>
            <div class="p-6 flex-grow flex flex-col justify-between">
                <div>
                    <h3 class="font-serif-title text-xl font-bold text-coffee-900">${item.name}</h3>
                    <p class="text-xs text-coffee-700/80 mt-2 leading-relaxed">
                        ${item.description}
                    </p>
                </div>
                <div class="mt-6 flex items-center justify-between pt-4 border-t border-cream-100">
                    <div>
                        <span class="text-[11px] text-gray-400 block uppercase tracking-wider">Precio</span>
                        <span class="font-bold text-lg text-coffee-900">$${item.price.toLocaleString('es-AR')}</span>
                    </div>
                    <button onclick="addToCart(${item.id}, '${item.name.replace(/'/g, "\\'")}', ${item.price}, '${item.image}')" 
                            class="px-4 py-2.5 rounded-full bg-cream-100 hover:bg-coffee-600 text-coffee-900 hover:text-white text-xs font-bold transition-all duration-200 flex items-center gap-2 group/btn">
                        <i class="fa-solid fa-plus text-[10px] group-hover/btn:rotate-90 transition-transform"></i>
                        <span>Añadir</span>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Search Input Handlers
searchInput.addEventListener('input', (e) => {
    searchQuery = e.target.value;
    if (searchQuery) {
        clearSearchBtn.classList.remove('hidden');
    } else {
        clearSearchBtn.classList.add('hidden');
    }
    renderMenuProducts();
});

clearSearchBtn.addEventListener('click', () => {
    searchInput.value = '';
    searchQuery = '';
    clearSearchBtn.classList.add('hidden');
    renderMenuProducts();
});

// Sort Handler
sortSelect.addEventListener('change', (e) => {
    currentSort = e.target.value;
    renderMenuProducts();
});

// Filter Category Pill Button Handlers
const categoryBtns = document.querySelectorAll('.category-btn');
categoryBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        categoryBtns.forEach(b => b.classList.remove('filter-btn-active'));
        btn.classList.add('filter-btn-active');
        activeCategory = btn.getAttribute('data-category');
        renderMenuProducts();
    });
});

function resetAllFilters() {
    activeCategory = 'todos';
    searchQuery = '';
    searchInput.value = '';
    clearSearchBtn.classList.add('hidden');
    sortSelect.value = 'featured';
    currentSort = 'featured';
    
    categoryBtns.forEach(b => {
        if(b.getAttribute('data-category') === 'todos') {
            b.classList.add('filter-btn-active');
        } else {
            b.classList.remove('filter-btn-active');
        }
    });

    renderMenuProducts();
}

resetFiltersBtn.addEventListener('click', resetAllFilters);

// Cart Tabs Switcher
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

// Delivery Address Field Toggle
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

// Toggle Profile Dropdown
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

function closeProfileDropdown() {
    profileDropdown.classList.add('opacity-0', 'scale-95');
    setTimeout(() => {
        profileDropdown.classList.add('hidden');
    }, 200);
}

document.addEventListener('click', (e) => {
    if (!profileDropdown.contains(e.target) && !profileBtn.contains(e.target)) {
        closeProfileDropdown();
    }
});

// Admin Login Modal Controls
openAdminLoginBtn.addEventListener('click', () => {
    closeProfileDropdown();
    openModal(loginModal);
});

closeLoginModalBtn.addEventListener('click', () => {
    closeModal(loginModal);
});

function openModal(modal) {
    modal.classList.remove('pointer-events-none', 'opacity-0');
    modal.firstElementChild.classList.remove('scale-95');
}

function closeModal(modal) {
    modal.classList.add('pointer-events-none', 'opacity-0');
    modal.firstElementChild.classList.add('scale-95');
}

// Handle Admin Login Simulation
function handleLogin(e) {
    e.preventDefault();
    const inputVal = document.getElementById('adminUserInput').value.trim();
    if (inputVal) {
        adminName = inputVal;
    }
    isAdminLoggedIn = true;
    adminNameDisplay.textContent = `Admin: ${adminName}`;
    
    loggedOutView.classList.add('hidden');
    loggedInView.classList.remove('hidden');

    closeModal(loginModal);
    showToast(`¡Bienvenida de nuevo, ${adminName}!`);
}

// Handle Logout
logoutBtn.addEventListener('click', () => {
    isAdminLoggedIn = false;
    loggedOutView.classList.remove('hidden');
    loggedInView.classList.add('hidden');
    closeProfileDropdown();
    showToast('Sesión de administración cerrada');
});

// Cart Drawer Controls
cartBtn.addEventListener('click', openCart);
closeCartBtn.addEventListener('click', closeCart);
cartBackdrop.addEventListener('click', closeCart);

function openCart() {
    cartBackdrop.classList.remove('pointer-events-none', 'opacity-0');
    cartDrawer.classList.remove('translate-x-full');
    document.body.classList.add('overflow-hidden');
}

function closeCart() {
    cartBackdrop.classList.add('pointer-events-none', 'opacity-0');
    cartDrawer.classList.add('translate-x-full');
    document.body.classList.remove('overflow-hidden');
}

// Mobile Menu Toggle
mobileMenuBtn.addEventListener('click', () => {
    mobileMenu.classList.toggle('hidden');
});

// Add to Cart Logic
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
    // Update Badge Count
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    cartCount.textContent = totalItems;

    // Render Items
    if (cart.length === 0) {
        cartItemsContainer.innerHTML = `
            <div class="flex flex-col items-center justify-center h-64 text-center text-gray-400">
                <i class="fa-solid fa-basket-shopping text-4xl mb-3 text-cream-300"></i>
                <p class="text-sm font-medium text-coffee-800">Tu carrito está vacío</p>
                <p class="text-xs text-gray-400 mt-1">Elige tus especialidades horneadas e agrégalas aquí.</p>
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

    // Calculate Subtotal & Total
    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const deliveryType = document.querySelector('input[name="deliveryType"]:checked')?.value || 'Retiro en local';
    const shippingFee = (deliveryType === 'Envío a domicilio' && cart.length > 0) ? 800 : 0;
    const grandTotal = subtotal + shippingFee;

    cartSubtotal.textContent = `$${subtotal.toLocaleString('es-AR')}`;
    cartTotal.textContent = `$${grandTotal.toLocaleString('es-AR')}`;
}

// Order Submission Process
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

    // Update tracking view interface
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

    // Reset cart & transition to tracking tab
    cart = [];
    updateCartUI();
    switchCartTab('track');
    showToast('¡Pedido enviado con éxito!');
}

// jsPDF Receipt Generation
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

        // Top Header Bar
        doc.setFillColor(110, 75, 48); // #6e4b30
        doc.rect(0, 0, 210, 28, 'F');

        doc.setTextColor(255, 255, 255);
        doc.setFont("helvetica", "bold");
        doc.setFontSize(20);
        doc.text("Maison Sucrée", 15, 15);

        doc.setFont("helvetica", "normal");
        doc.setFontSize(9);
        doc.text("Café & Pastelería Artesanal", 15, 21);
        doc.text("COMPROBANTE DE COMPRA", 145, 15);

        // Order Particulars
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

        // Table Structure
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

        // Rows
        lastOrder.items.forEach((item) => {
            doc.text(item.name.substring(0, 36), 20, startY);
            doc.text(`${item.quantity}`, 122, startY);
            doc.text(`$${item.price.toLocaleString('es-AR')}`, 145, startY);
            doc.text(`$${(item.price * item.quantity).toLocaleString('es-AR')}`, 175, startY);
            startY += 7;
        });

        // Separator
        doc.setDrawColor(212, 194, 174);
        doc.line(15, startY + 2, 195, startY + 2);
        startY += 10;

        // Total Summary
        if (lastOrder.shippingFee > 0) {
            doc.text(`Subtotal: $${lastOrder.subtotal.toLocaleString('es-AR')}`, 140, startY);
            startY += 6;
            doc.text(`Envío: $${lastOrder.shippingFee.toLocaleString('es-AR')}`, 140, startY);
            startY += 6;
        }

        doc.setFont("helvetica", "bold");
        doc.setFontSize(11);
        doc.text(`TOTAL FINAL: $${lastOrder.total.toLocaleString('es-AR')}`, 140, startY);

        // Footer text
        doc.setFontSize(8);
        doc.setFont("helvetica", "italic");
        doc.setTextColor(120, 120, 120);
        doc.text("¡Gracias por elegir GastroCtrl! Conserva este comprobante.", 105, 275, { align: "center" });

        // Save Document
        doc.save(`Comprobante_${lastOrder.id}.pdf`);
        showToast('Comprobante PDF descargado');
    } catch (error) {
        console.error("Error al generar PDF:", error);
        showToast('Error al generar el comprobante PDF');
    }
}

// Floating Toast Notification System
function showToast(message) {
    const container = document.getElementById('toastContainer');
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

// Initialize App on Page Load
window.addEventListener('DOMContentLoaded', () => {
    renderMenuProducts();
    updateCartUI();
});
