// Configuración Personalizada de Tailwind CSS
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
                    50: '#fdfbf7',
                    100: '#f7f1e8',
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

// Estructuras de Datos / Estado de la App
let products = [
    { id: 1, name: "Croissant de Almendras", category: "pasteleria", price: 3200, stock: 12, status: "active", image: "https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&q=80&w=200" },
    { id: 2, name: "Café Flat White 8oz", category: "cafeteria", price: 2800, stock: 45, status: "active", image: "https://images.unsplash.com/photo-1577968897966-3d4325b36b61?auto=format&fit=crop&q=80&w=200" },
    { id: 3, name: "Tarta de Frutos Rojos", category: "pasteleria", price: 4500, stock: 3, status: "active", image: "https://images.unsplash.com/photo-1565958011703-44f9829ba187?auto=format&fit=crop&q=80&w=200" },
    { id: 4, name: "Pan de Masa Madre", category: "panaderia", price: 3800, stock: 2, status: "active", image: "https://images.unsplash.com/photo-1589367920969-ab8e050bbb04?auto=format&fit=crop&q=80&w=200" },
    { id: 5, name: "Cheesecake Dulce de Leche", category: "pasteleria", price: 4900, stock: 8, status: "active", image: "https://images.unsplash.com/photo-1533134242443-d4fd215305ad?auto=format&fit=crop&q=80&w=200" }
];

let categories = [
    { id: 1, name: "Pastelería", slug: "pasteleria", icon: "fa-cake-candles", count: 18, desc: "Tortas, tartas y alfajores artesanales" },
    { id: 2, name: "Cafetería", slug: "cafeteria", icon: "fa-mug-hot", count: 12, desc: "Espresso, lattes y preparaciones filtradas" },
    { id: 3, name: "Panadería", slug: "panaderia", icon: "fa-bread-slice", count: 8, desc: "Panes de masa madre, baguettes y brioches" },
    { id: 4, name: "Bebidas Frías", slug: "bebidas", icon: "fa-glass-water", count: 6, desc: "Cold brew, limonadas y smoothies" }
];

let orders = [
    { id: "#ORD-8942", customer: "Camila Torres", items: "2x Flat White, 1x Croissant Almendras", total: 8800, type: "Takeaway", status: "preparacion", time: "Hace 5 min" },
    { id: "#ORD-8941", customer: "Lucas Benítez", items: "1x Cheesecake Dulce de Leche, 1x Capuchino", total: 7700, type: "Mesa 4", status: "pendiente", time: "Hace 12 min" },
    { id: "#ORD-8940", customer: "Martín Gómez", items: "1x Pan Masa Madre, 2x Medialunas", total: 5400, type: "Delivery", status: "listo", time: "Hace 18 min" },
    { id: "#ORD-8939", customer: "Sofía Rossi", items: "1x Tarta Frutos Rojos", total: 4500, type: "Mesa 2", status: "preparacion", time: "Hace 22 min" },
    { id: "#ORD-8938", customer: "Diego Fernández", items: "2x Espresso Doble, 2x Scone de Queso", total: 6800, type: "Takeaway", status: "entregado", time: "Hace 35 min" }
];

let inventoryItems = [
    { id: 1, name: "Café en Grano Specialty (kg)", category: "Materia Prima", stock: 4.5, min: 10, unit: "kg" },
    { id: 2, name: "Harina 0000 Pastelera (kg)", category: "Insumos Pastelería", stock: 8.0, min: 15, unit: "kg" },
    { id: 3, name: "Manteca Extra Fina (kg)", category: "Lácteos", stock: 22.0, min: 10, unit: "kg" },
    { id: 4, name: "Leche Entera (L)", category: "Lácteos", stock: 48.0, min: 20, unit: "L" },
    { id: 5, name: "Frutos Rojos Congelados (kg)", category: "Frutas", stock: 3.2, min: 5, unit: "kg" }
];

let customers = [
    { id: 1, name: "Camila Torres", email: "camila.t@gmail.com", phone: "+54 9 11 4521-8899", ordersCount: 14, spent: 48200 },
    { id: 2, name: "Lucas Benítez", email: "lucas.b@hotmail.com", phone: "+54 9 11 6320-1122", ordersCount: 8, spent: 29400 },
    { id: 3, name: "Martín Gómez", email: "mgomez@yahoo.com", phone: "+54 9 11 5544-3322", ordersCount: 22, spent: 84000 }
];

let currentActiveOrder = null;
let activeOrderFilter = 'todos';
let activeProductCatFilter = 'todos';
let weeklyChartInstance = null;
let monthlyChartInstance = null;
let pieChartInstance = null;

let trendPeriod = 'weeks';
let piePeriod = 'weeks';

const trendData = {
    days: {
        labels: ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
        data: [110000, 125000, 105000, 140000, 180000, 210000, 114000]
    },
    weeks: {
        labels: ['Semana 1', 'Semana 2', 'Semana 3', 'Semana 4'],
        data: [890000, 940000, 1020000, 990000]
    },
    months: {
        labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
        data: [3100000, 3400000, 3200000, 3600000, 3900000, 4100000, 3800000, 4200000, 3840000, 4300000, 4500000, 4900000]
    }
};

const pieData = {
    days: {
        labels: ['Pastelería', 'Cafetería', 'Panadería', 'Bebidas Frías'],
        data: [42, 35, 15, 8]
    },
    weeks: {
        labels: ['Pastelería', 'Cafetería', 'Panadería', 'Bebidas Frías'],
        data: [45, 30, 15, 10]
    },
    months: {
        labels: ['Pastelería', 'Cafetería', 'Panadería', 'Bebidas Frías'],
        data: [48, 28, 14, 10]
    }
};

function updateSalesTrendChart(period) {
    trendPeriod = period;
    ['days', 'weeks', 'months'].forEach(p => {
        const btn = document.getElementById(`btn-trend-${p}`);
        if (btn) {
            if (p === period) {
                btn.className = "px-3 py-1 rounded-full text-xs font-bold bg-coffee-600 text-white shadow-xs transition-all";
            } else {
                btn.className = "px-3 py-1 rounded-full text-xs font-bold bg-cream-100 text-coffee-800 hover:bg-cream-200 transition-all";
            }
        }
    });

    if (monthlyChartInstance) {
        monthlyChartInstance.data.labels = trendData[period].labels;
        monthlyChartInstance.data.datasets[0].data = trendData[period].data;
        monthlyChartInstance.update();
    }
}

function updateCategoryPieChart(period) {
    piePeriod = period;
    ['days', 'weeks', 'months'].forEach(p => {
        const btn = document.getElementById(`btn-pie-${p}`);
        if (btn) {
            if (p === period) {
                btn.className = "px-3 py-1 rounded-full text-xs font-bold bg-coffee-600 text-white shadow-xs transition-all";
            } else {
                btn.className = "px-3 py-1 rounded-full text-xs font-bold bg-cream-100 text-coffee-800 hover:bg-cream-200 transition-all";
            }
        }
    });

    if (pieChartInstance) {
        pieChartInstance.data.labels = pieData[period].labels;
        pieChartInstance.data.datasets[0].data = pieData[period].data;
        pieChartInstance.update();
    }
}

// Inicialización de la aplicación al cargar
window.onload = function() {
    renderDashboardViews();
    renderOrdersWorkflow();
    renderProductsTable();
    renderInventoryTable();
    renderCustomersTable();
    renderCategoriesGrid();
    initCharts();
};

function switchTab(tabId) {
    // Ocultar todas las pestañas
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    
    // Desmarcar elementos de navegación
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('nav-item-active'));

    // Mostrar pestaña actual y activar ítem en el menú
    const targetTab = document.getElementById(`section-${tabId}`);
    const targetNav = document.getElementById(`nav-${tabId}`);

    if (targetTab) targetTab.classList.remove('hidden');
    if (targetNav) targetNav.classList.add('nav-item-active');

    // Actualizar Título
    const titles = {
        dashboard: "Dashboard Principal",
        orders: "Gestión de Pedidos",
        products: "Catálogo de Productos",
        inventory: "Stock e Inventario",
        analytics: "Estadísticas y Ventas",
        customers: "Clientes Registrados",
        categories: "Categorías del Menú",
        settings: "Configuración del Sistema"
    };
    document.getElementById('pageTitle').innerText = titles[tabId] || "Dashboard";

    // Visibilidad del botón "+ Nuevo Producto" en el encabezado
    const newProdBtn = document.getElementById('headerNewProductBtn');
    if (newProdBtn) {
        if (tabId === 'products') {
            newProdBtn.classList.remove('hidden');
        } else {
            newProdBtn.classList.add('hidden');
        }
    }

    // Cierre automático del menú móvil
    document.getElementById('sidebarDrawer').classList.add('-translate-x-full');
    document.getElementById('sidebarBackdrop').classList.add('hidden');
}

function toggleMobileSidebar() {
    const sidebar = document.getElementById('sidebarDrawer');
    const backdrop = document.getElementById('sidebarBackdrop');
    sidebar.classList.toggle('-translate-x-full');
    backdrop.classList.toggle('hidden');
}

function renderDashboardViews() {
    // Actualizar contadores
    const pendingCount = orders.filter(o => o.status === 'pendiente').length;
    const prepCount = orders.filter(o => o.status === 'preparacion').length;
    const readyCount = orders.filter(o => o.status === 'listo').length;

    document.getElementById('dashPendingOrders').innerText = pendingCount;
    document.getElementById('dashPrepOrders').innerText = prepCount;
    document.getElementById('dashReadyOrders').innerText = readyCount;

    // Renderizar lista de Poco Stock
    const lowStockItems = inventoryItems.filter(i => i.stock <= i.min);
    
    const lowStockContainer = document.getElementById('dashLowStockList');
    if (lowStockItems.length === 0) {
        lowStockContainer.innerHTML = `<p class="text-xs text-emerald-600 font-bold"><i class="fa-solid fa-circle-check"></i> Stock de insumos normal.</p>`;
    } else {
        lowStockContainer.innerHTML = lowStockItems.map(item => `
            <div class="p-3 bg-rose-50/60 rounded-2xl border border-rose-100 flex items-center justify-between">
                <div class="min-w-0 pr-2">
                    <h4 class="font-bold text-xs text-coffee-900 truncate">${item.name}</h4>
                    <p class="text-[10px] text-rose-700 font-bold mt-0.5">Quedan ${item.stock} ${item.unit} (Mín: ${item.min})</p>
                </div>
                <button onclick="openRestockModal(${item.id})" class="px-2.5 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-[10px] transition-all shrink-0 flex items-center gap-1 shadow-2xs">
                    <i class="fa-solid fa-plus-circle"></i> Reponer
                </button>
            </div>
        `).join('');
    }

    // Tabla de Pedidos Recientes
    const recentTable = document.getElementById('dashRecentOrdersTable');
    recentTable.innerHTML = orders.slice(0, 5).map(o => `
        <tr class="hover:bg-cream-50/80 transition-colors">
            <td class="py-3 px-3 font-bold text-coffee-900">${o.id}</td>
            <td class="py-3 px-3 font-semibold">${o.customer}</td>
            <td class="py-3 px-3 text-coffee-600 truncate max-w-xs">${o.items}</td>
            <td class="py-3 px-3 font-bold">$${o.total.toLocaleString()}</td>
            <td class="py-3 px-3">
                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-cream-100 text-coffee-800 border border-cream-200">${o.type}</span>
            </td>
            <td class="py-3 px-3">
                ${getStatusBadgeHTML(o.status)}
            </td>
            <td class="py-3 px-3 text-right">
                <button onclick="openOrderDetailModal('${o.id}')" class="px-3 py-1.5 rounded-xl bg-coffee-50 hover:bg-coffee-600 hover:text-white text-coffee-800 font-bold text-[11px] transition-all border border-coffee-200/70 inline-flex items-center gap-1.5 shadow-2xs">
                    <i class="fa-solid fa-eye text-[11px]"></i>
                    <span>Ver Detalle</span>
                </button>
            </td>
        </tr>
    `).join('');
}

// Generador de insignias de estado
function getStatusBadgeHTML(status) {
    switch(status) {
        case 'pendiente':
            return `<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200 whitespace-nowrap"><i class="fa-regular fa-clock text-[10px]"></i> Pendiente</span>`;
        case 'preparacion':
            return `<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200 whitespace-nowrap"><i class="fa-solid fa-fire-burner text-[10px]"></i> En preparación</span>`;
        case 'listo':
            return `<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 whitespace-nowrap"><i class="fa-solid fa-circle-check text-[10px]"></i> Listo</span>`;
        case 'entregado':
            return `<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-700 border border-gray-200 whitespace-nowrap"><i class="fa-solid fa-check-double text-[10px]"></i> Entregado</span>`;
        default:
            return `<span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-800">${status}</span>`;
    }
}

function filterOrders(status) {
    activeOrderFilter = status;
    document.querySelectorAll('.order-filter-btn').forEach(btn => {
        if (btn.dataset.status === status) {
            btn.className = "order-filter-btn px-4 py-2 rounded-full text-xs font-bold bg-coffee-600 text-white shadow-xs";
        } else {
            btn.className = "order-filter-btn px-4 py-2 rounded-full text-xs font-bold bg-cream-100 text-coffee-800 hover:bg-cream-200";
        }
    });
    renderOrdersWorkflow();
}

function renderOrdersWorkflow() {
    const searchVal = document.getElementById('orderSearchInput').value.toLowerCase();
    const grid = document.getElementById('ordersKanbanGrid');

    let filtered = orders.filter(o => {
        const matchesFilter = activeOrderFilter === 'todos' || o.status === activeOrderFilter;
        const matchesSearch = o.customer.toLowerCase().includes(searchVal) || o.id.toLowerCase().includes(searchVal);
        return matchesFilter && matchesSearch;
    });

    if (filtered.length === 0) {
        grid.innerHTML = `<div class="col-span-full py-12 text-center text-coffee-500 font-medium">No se encontraron pedidos en esta sección.</div>`;
        return;
    }

    grid.innerHTML = filtered.map(o => `
        <div class="bg-white p-5 rounded-3xl border border-cream-200/80 shadow-sm space-y-3 hover-lift">
            <div class="flex items-center justify-between">
                <span class="text-xs font-bold text-coffee-500 uppercase tracking-wider">${o.id}</span>
                ${getStatusBadgeHTML(o.status)}
            </div>
            
            <div>
                <h3 class="font-serif-title font-bold text-base text-coffee-900">${o.customer}</h3>
                <p class="text-xs text-coffee-600 mt-0.5 line-clamp-2">${o.items}</p>
            </div>

            <div class="flex items-center justify-between text-xs font-bold text-coffee-800 pt-2 border-t border-cream-100">
                <span>$${o.total.toLocaleString()}</span>
                <span class="text-[10px] text-coffee-500 font-normal"><i class="fa-regular fa-clock"></i> ${o.time}</span>
            </div>

            <div class="pt-1 flex items-center justify-between gap-2">
                <button onclick="openOrderDetailModal('${o.id}')" class="w-full py-2 rounded-xl bg-cream-100 hover:bg-coffee-600 hover:text-white text-coffee-800 font-bold text-xs transition-colors flex items-center justify-center gap-1.5">
                    <i class="fa-solid fa-eye text-xs"></i>
                    <span>Ver y Gestionar</span>
                </button>
            </div>
        </div>
    `).join('');
}

function filterProductsCategory(cat) {
    activeProductCatFilter = cat;
    document.querySelectorAll('.prod-cat-btn').forEach(btn => {
        if (btn.dataset.cat === cat) {
            btn.className = "prod-cat-btn px-4 py-2 rounded-full text-xs font-bold bg-coffee-600 text-white";
        } else {
            btn.className = "prod-cat-btn px-4 py-2 rounded-full text-xs font-bold bg-cream-100 text-coffee-800";
        }
    });
    renderProductsTable();
}

function renderProductsTable() {
    const searchVal = (document.getElementById('productSearchInput')?.value || '').toLowerCase();
    const tbody = document.getElementById('productsTableBody');

    let filtered = products.filter(p => {
        const matchesCat = activeProductCatFilter === 'todos' || p.category === activeProductCatFilter;
        const matchesSearch = p.name.toLowerCase().includes(searchVal);
        return matchesCat && matchesSearch;
    });

    tbody.innerHTML = filtered.map(p => `
        <tr class="hover:bg-cream-50/80 transition-colors">
            <td class="py-3 px-3">
                <div class="flex items-center gap-3">
                    <img src="${p.image}" class="w-10 h-10 rounded-xl object-cover border border-cream-200" alt="${p.name}" onerror="this.src='https://placehold.co/100x100/efe6d8/4e3320?text=Café'">
                    <span class="font-bold text-coffee-900">${p.name}</span>
                </div>
            </td>
            <td class="py-3 px-3 uppercase text-[10px] font-bold tracking-wider text-coffee-600">${p.category}</td>
            <td class="py-3 px-3 font-bold text-coffee-900">$${p.price.toLocaleString()}</td>
            <td class="py-3 px-3">
                <span class="font-bold ${p.stock <= 5 ? 'text-rose-600' : 'text-coffee-800'}">${p.stock} un.</span>
            </td>
            <td class="py-3 px-3">
                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold ${p.status === 'active' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-gray-100 text-gray-600'}">
                    ${p.status === 'active' ? 'Activo' : 'Oculto'}
                </span>
            </td>
            <td class="py-3 px-3 text-right">
                <div class="flex items-center justify-end gap-2">
                    <button onclick="editProduct(${p.id})" class="px-3 py-1.5 rounded-xl bg-amber-50 hover:bg-amber-500 hover:text-white text-amber-800 font-bold text-xs transition-colors border border-amber-200/80 flex items-center gap-1">
                        <i class="fa-solid fa-pen-to-square text-xs"></i>
                        <span>Editar</span>
                    </button>
                    <button onclick="deleteProduct(${p.id})" class="p-1.5 rounded-xl bg-rose-50 hover:bg-rose-600 hover:text-white text-rose-600 font-bold text-xs transition-colors border border-rose-200">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function openProductModal(productId = null) {
    const modal = document.getElementById('productModal');
    const form = document.getElementById('productForm');
    form.reset();

    if (productId) {
        const prod = products.find(p => p.id === productId);
        if (prod) {
            document.getElementById('productModalTitle').innerText = "Editar Producto";
            document.getElementById('modalProductId').value = prod.id;
            document.getElementById('modalProdName').value = prod.name;
            document.getElementById('modalProdCategory').value = prod.category;
            document.getElementById('modalProdPrice').value = prod.price;
            document.getElementById('modalProdStock').value = prod.stock;
            document.getElementById('modalProdStatus').value = prod.status;
            document.getElementById('modalProdImage').value = prod.image;
        }
    } else {
        document.getElementById('productModalTitle').innerText = "Nuevo Producto";
        document.getElementById('modalProductId').value = "";
    }

    modal.classList.remove('hidden');
}

function closeProductModal() {
    document.getElementById('productModal').classList.add('hidden');
}

function editProduct(id) {
    openProductModal(id);
}

function deleteProduct(id) {
    products = products.filter(p => p.id !== id);
    renderProductsTable();
    showToast('Producto eliminado correctamente', 'info');
}

function saveProduct(event) {
    event.preventDefault();
    const id = document.getElementById('modalProductId').value;
    const name = document.getElementById('modalProdName').value;
    const category = document.getElementById('modalProdCategory').value;
    const price = parseFloat(document.getElementById('modalProdPrice').value);
    const stock = parseInt(document.getElementById('modalProdStock').value);
    const status = document.getElementById('modalProdStatus').value;
    const image = document.getElementById('modalProdImage').value || 'https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&q=80&w=200';

    if (id) {
        const index = products.findIndex(p => p.id == id);
        if (index !== -1) {
            products[index] = { id: parseInt(id), name, category, price, stock, status, image };
        }
        showToast('Producto actualizado con éxito');
    } else {
        const newProd = {
            id: Date.now(),
            name, category, price, stock, status, image
        };
        products.push(newProd);
        showToast('Producto creado con éxito');
    }

    closeProductModal();
    renderProductsTable();
}

function renderInventoryTable() {
    const searchVal = (document.getElementById('inventorySearchInput')?.value || '').toLowerCase();
    const tbody = document.getElementById('inventoryTableBody');

    let filtered = inventoryItems.filter(i => i.name.toLowerCase().includes(searchVal));

    tbody.innerHTML = filtered.map(item => `
        <tr class="hover:bg-cream-50/80 transition-colors">
            <td class="py-3 px-3 font-bold text-coffee-900">${item.name}</td>
            <td class="py-3 px-3 text-coffee-600">${item.category}</td>
            <td class="py-3 px-3 font-bold ${item.stock <= item.min ? 'text-rose-600' : 'text-coffee-900'}">
                ${item.stock} ${item.unit}
            </td>
            <td class="py-3 px-3 text-coffee-500">${item.min} ${item.unit}</td>
            <td class="py-3 px-3">
                ${item.stock <= item.min ? 
                    `<span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-50 text-rose-600 border border-rose-200">Poco Stock</span>` : 
                    `<span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">Suficiente</span>`}
            </td>
            <td class="py-3 px-3">
                <button onclick="openRestockModal(${item.id})" class="px-3 py-1.5 rounded-xl bg-coffee-600 hover:bg-coffee-700 text-white font-bold text-xs transition-colors shadow-2xs inline-flex items-center gap-1">
                    <i class="fa-solid fa-plus-circle"></i> Reponer
                </button>
            </td>
        </tr>
    `).join('');
}

function openRestockModal(itemId = null) {
    const modal = document.getElementById('restockModal');
    const select = document.getElementById('modalRestockItemSelect');
    
    select.innerHTML = inventoryItems.map(i => `<option value="${i.id}">${i.name} (Actual: ${i.stock} ${i.unit})</option>`).join('');
    
    if (itemId) {
        select.value = itemId;
    }

    modal.classList.remove('hidden');
}

function closeRestockModal() {
    document.getElementById('restockModal').classList.add('hidden');
}

function saveRestock(event) {
    event.preventDefault();
    const itemId = parseInt(document.getElementById('modalRestockItemSelect').value);
    const amount = parseFloat(document.getElementById('modalRestockAmount').value);

    const item = inventoryItems.find(i => i.id === itemId);
    if (item) {
        item.stock = parseFloat((item.stock + amount).toFixed(1));
        showToast(`Se agregaron ${amount} ${item.unit} a ${item.name}`);
    }

    closeRestockModal();
    renderInventoryTable();
    renderDashboardViews();
}

function openOrderDetailModal(orderId) {
    const order = orders.find(o => o.id === orderId);
    if (!order) return;

    currentActiveOrder = order;
    document.getElementById('modalOrderId').innerText = order.id;
    document.getElementById('modalOrderCustomer').innerText = order.customer;
    document.getElementById('modalOrderItems').innerText = order.items;
    document.getElementById('modalOrderTotal').innerText = `$${order.total.toLocaleString()}`;
    document.getElementById('modalOrderStatusSelect').value = order.status;

    document.getElementById('orderDetailModal').classList.remove('hidden');
}

function closeOrderDetailModal() {
    document.getElementById('orderDetailModal').classList.add('hidden');
}

function updateOrderStatusFromModal() {
    if (!currentActiveOrder) return;
    const newStatus = document.getElementById('modalOrderStatusSelect').value;
    currentActiveOrder.status = newStatus;
    
    showToast(`Estado de ${currentActiveOrder.id} cambiado a ${newStatus}`);
    renderDashboardViews();
    renderOrdersWorkflow();
}

function renderCategoriesGrid() {
    const grid = document.getElementById('categoriesGrid');
    grid.innerHTML = categories.map(cat => `
        <div class="bg-white p-5 rounded-3xl border border-cream-200/80 shadow-sm space-y-3 hover-lift flex flex-col justify-between">
            <div>
                <div class="w-10 h-10 rounded-2xl bg-coffee-50 border border-coffee-200 text-coffee-600 flex items-center justify-center text-lg mb-3">
                    <i class="fa-solid ${cat.icon}"></i>
                </div>
                <h3 class="font-serif-title font-bold text-base text-coffee-900">${cat.name}</h3>
                <p class="text-xs text-coffee-600 mt-1">${cat.desc}</p>
            </div>

            <div class="pt-3 border-t border-cream-100 flex items-center justify-between">
                <span class="text-xs font-bold text-coffee-800">${cat.count} Productos</span>
                <button onclick="editCategory(${cat.id})" class="px-2.5 py-1.5 rounded-xl bg-cream-100 hover:bg-coffee-600 hover:text-white text-coffee-800 font-bold text-xs transition-colors">
                    Editar
                </button>
            </div>
        </div>
    `).join('');
}

function openCategoryModal(catId = null) {
    const modal = document.getElementById('categoryModal');
    document.getElementById('categoryForm').reset();

    if (catId) {
        const cat = categories.find(c => c.id === catId);
        if (cat) {
            document.getElementById('categoryModalTitle').innerText = "Editar Categoría";
            document.getElementById('modalCategoryId').value = cat.id;
            document.getElementById('modalCatName').value = cat.name;
            document.getElementById('modalCatDesc').value = cat.desc;
            document.getElementById('modalCatIcon').value = cat.icon;
        }
    } else {
        document.getElementById('categoryModalTitle').innerText = "Nueva Categoría";
        document.getElementById('modalCategoryId').value = "";
    }

    modal.classList.remove('hidden');
}

function closeCategoryModal() {
    document.getElementById('categoryModal').classList.add('hidden');
}

function editCategory(id) {
    openCategoryModal(id);
}

function saveCategory(event) {
    event.preventDefault();
    const id = document.getElementById('modalCategoryId').value;
    const name = document.getElementById('modalCatName').value;
    const desc = document.getElementById('modalCatDesc').value;
    const icon = document.getElementById('modalCatIcon').value || 'fa-tag';

    if (id) {
        const idx = categories.findIndex(c => c.id == id);
        if (idx !== -1) {
            categories[idx] = { ...categories[idx], name, desc, icon };
        }
        showToast('Categoría actualizada');
    } else {
        categories.push({
            id: Date.now(),
            name, desc, icon, count: 0, slug: name.toLowerCase().replace(/\s+/g, '')
        });
        showToast('Categoría creada');
    }

    closeCategoryModal();
    renderCategoriesGrid();
}

function renderCustomersTable() {
    const tbody = document.getElementById('customersTableBody');
    tbody.innerHTML = customers.map(c => `
        <tr class="hover:bg-cream-50/80 transition-colors">
            <td class="py-3 px-3 font-bold text-coffee-900">${c.name}</td>
            <td class="py-3 px-3 text-coffee-600">${c.email} <br> <span class="text-[10px]">${c.phone}</span></td>
            <td class="py-3 px-3 font-bold">${c.ordersCount} pedidos</td>
            <td class="py-3 px-3 font-bold text-coffee-900">$${c.spent.toLocaleString()}</td>
            <td class="py-3 px-3 text-right">
                <button onclick="showToast('Mensaje enviado a ${c.name}', 'info')" class="px-3 py-1.5 rounded-xl bg-emerald-50 hover:bg-emerald-600 hover:text-white text-emerald-700 font-bold text-xs transition-colors border border-emerald-200 inline-flex items-center gap-1">
                    <i class="fa-brands fa-whatsapp text-xs"></i> Contactar
                </button>
            </td>
        </tr>
    `).join('');
}

function saveSettings(e) {
    e.preventDefault();
    showToast('Configuración guardada correctamente');
}

function openLogoutModal() {
    document.getElementById('logoutModal').classList.remove('hidden');
}

function closeLogoutModal() {
    document.getElementById('logoutModal').classList.add('hidden');
}

function confirmLogout() {
    closeLogoutModal();
    showToast('Sesión cerrada correctamente', 'info');
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toastNotification');
    const msgEl = document.getElementById('toastMessage');
    const iconEl = document.getElementById('toastIcon');

    msgEl.innerText = message;
    
    if (type === 'info') {
        iconEl.className = "fa-solid fa-circle-info text-amber-400 text-base";
    } else {
        iconEl.className = "fa-solid fa-circle-check text-emerald-400 text-base";
    }

    toast.classList.remove('translate-y-20', 'opacity-0');
    
    setTimeout(() => {
        toast.classList.add('translate-y-20', 'opacity-0');
    }, 3000);
}

function initCharts() {
    // 1. Gráfico de Ventas Semanales
    const ctxWeekly = document.getElementById('weeklySalesChart')?.getContext('2d');
    if (ctxWeekly) {
        if (weeklyChartInstance) weeklyChartInstance.destroy();
        weeklyChartInstance = new Chart(ctxWeekly, {
            type: 'line',
            data: {
                labels: ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
                datasets: [{
                    label: 'Ventas ($)',
                    data: [110000, 125000, 105000, 140000, 180000, 210000, 114000],
                    borderColor: '#8c6343',
                    backgroundColor: 'rgba(140, 99, 67, 0.12)',
                    fill: true,
                    tension: 0.35,
                    borderWidth: 3,
                    pointBackgroundColor: '#4e3320',
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { grid: { color: '#f7f3ed' }, ticks: { font: { family: 'Plus Jakarta Sans', size: 10 } } },
                    x: { grid: { display: false }, ticks: { font: { family: 'Plus Jakarta Sans', size: 11 } } }
                }
            }
        });
    }

    // 2. Gráfico Mensual / Tendencias
    const ctxMonthly = document.getElementById('monthlySalesChart')?.getContext('2d');
    if (ctxMonthly) {
        if (monthlyChartInstance) monthlyChartInstance.destroy();
        monthlyChartInstance = new Chart(ctxMonthly, {
            type: 'bar',
            data: {
                labels: trendData.weeks.labels,
                datasets: [{
                    label: 'Ingresos ($)',
                    data: trendData.weeks.data,
                    backgroundColor: '#a67c52',
                    borderRadius: 12
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { grid: { color: '#f7f3ed' }, ticks: { font: { family: 'Plus Jakarta Sans', size: 10 } } },
                    x: { grid: { display: false }, ticks: { font: { family: 'Plus Jakarta Sans', size: 11 } } }
                }
            }
        });
    }

    // 3. Gráfico de Torta / Categorías
    const ctxPie = document.getElementById('categoryPieChart')?.getContext('2d');
    if (ctxPie) {
        if (pieChartInstance) pieChartInstance.destroy();
        pieChartInstance = new Chart(ctxPie, {
            type: 'doughnut',
            data: {
                labels: pieData.weeks.labels,
                datasets: [{
                    data: pieData.weeks.data,
                    backgroundColor: ['#8c6343', '#b87d4b', '#d4c2ae', '#4e3320'],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: { family: 'Plus Jakarta Sans', size: 11 },
                            usePointStyle: true,
                            padding: 14
                        }
                    }
                }
            }
        });
    }
}
