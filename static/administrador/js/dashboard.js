console.log("PRODUCTOS DESDE DJANGO:", window.ADMIN_PRODUCTOS);

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
let products = window.ADMIN_PRODUCTOS;

let categories = (window.ADMIN_CATEGORIAS || []).map(cat => ({
    id: cat.id,
    name: cat.name,
    slug: cat.slug,
    icon: cat.icon || 'fa-tag',
    count: cat.count || 0,
    desc: cat.desc || 'Categoría de productos',
}));

let orders = window.ADMIN_PEDIDOS || [];
let archivedOrders = window.ADMIN_PEDIDOS_ARCHIVADOS || [];

let inventoryItems = (window.ADMIN_INSUMOS || []).map(insumo => ({
    id: insumo.id,
    name: insumo.nombre,
    category: "Insumos",
    stock: insumo.cantidad_disponible,
    min: insumo.stock_minimo,
    unit: insumo.unidad_medida,
}));

let customers = [];



let currentActiveOrder = null;
let activeOrderFilter = 'todos';
let activeProductCatFilter = 'todos';
let weeklyChartInstance = null;
let monthlyChartInstance = null;
let pieChartInstance = null;

let trendPeriod = 'weeks';
let piePeriod = 'weeks';

const trendData = window.trendDataReal || {
    days: { labels: [], data: [] },
    weeks: { labels: [], data: [] },
    months: { labels: [], data: [] },
};

const pieData = window.pieDataReal || {
    days: { labels: [], data: [] },
    weeks: { labels: [], data: [] },
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
    loadCustomersFromDatabase();
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
    const prepCount = orders.filter(o => o.status === 'en_preparacion').length;
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
        case 'en_preparacion':
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
        const selected = btn.dataset.status === status;
        btn.className = "order-filter-btn px-4 py-2 rounded-full text-xs font-bold " +
            (selected
                ? "bg-coffee-600 text-white shadow-xs"
                : "bg-cream-100 text-coffee-800 hover:bg-cream-200");
        btn.setAttribute('aria-pressed', selected ? 'true' : 'false');
    });
    renderOrdersWorkflow();
}

function renderOrdersWorkflow() {
    const searchInput = document.getElementById('orderSearchInput');
    const searchVal = (searchInput?.value || '').toLowerCase().trim();
    const grid = document.getElementById('ordersKanbanGrid');
    if (!grid) return;

    const showingArchived = activeOrderFilter === 'archivados';
    const sourceOrders = showingArchived ? archivedOrders : orders;
    let filtered = sourceOrders.filter(o => {
        const matchesFilter = showingArchived || activeOrderFilter === 'todos' || o.status === activeOrderFilter;
        const matchesSearch = (o.customer || '').toLowerCase().includes(searchVal) ||
            (o.id || '').toLowerCase().includes(searchVal);
        return matchesFilter && matchesSearch;
    });

    if (filtered.length === 0) {
        grid.innerHTML = `<div class="col-span-full py-12 text-center text-coffee-500 font-medium">${showingArchived ? 'No hay pedidos archivados.' : 'No se encontraron pedidos en esta sección.'}</div>`;
        return;
    }

    grid.innerHTML = filtered.map(o => `
        <div class="bg-white p-5 rounded-3xl border border-cream-200/80 shadow-sm hover-lift flex flex-col h-full min-w-0">
            <div class="flex items-center justify-between gap-2 min-h-7 mb-3">
                <span class="text-xs font-bold text-coffee-500 uppercase tracking-wider break-all">${o.id}</span>
                ${getStatusBadgeHTML(o.status)}
            </div>

            <div class="mb-4">
                <h3 class="font-serif-title font-bold text-base text-coffee-900 break-words">${o.customer}</h3>
                <p class="text-xs text-coffee-600 mt-1 line-clamp-2 min-h-8">${o.items}</p>
            </div>

            <div class="flex items-center justify-between gap-3 text-xs font-bold text-coffee-800 py-3 border-t border-cream-100 mt-auto">
                <span>$${o.total.toLocaleString()}</span>
                <span class="text-[10px] text-coffee-500 font-normal text-right"><i class="fa-regular fa-clock"></i> ${o.time}</span>
            </div>

            <div class="pt-1 grid grid-cols-1 ${showingArchived ? '' : 'sm:grid-cols-2'} items-stretch gap-2">
                <button onclick="openOrderDetailModal('${o.id}')" class="w-full min-h-10 px-3 py-2 rounded-xl bg-cream-100 hover:bg-coffee-600 hover:text-white text-coffee-800 font-bold text-xs transition-colors inline-flex items-center justify-center gap-1.5">
                    <i class="fa-solid fa-eye text-xs"></i>
                    <span>Ver y Gestionar</span>
                </button>
                ${showingArchived ? `
                <button onclick="restoreOrder('${o.id}')" class="w-full min-h-10 px-3 py-2 rounded-xl bg-emerald-50 hover:bg-emerald-600 hover:text-white text-emerald-800 border border-emerald-200 font-bold text-xs transition-colors inline-flex items-center justify-center gap-1.5">
                    <i class="fa-solid fa-box-open"></i><span>Restaurar</span>
                </button>` : (['entregado', 'cancelado'].includes(o.status) ? `
                <button onclick="archiveOrder('${o.id}')" class="w-full min-h-10 px-3 py-2 rounded-xl bg-amber-50 hover:bg-amber-600 hover:text-white text-amber-800 border border-amber-200 font-bold text-xs transition-colors inline-flex items-center justify-center gap-1.5">
                    <i class="fa-solid fa-box-archive"></i><span>Archivar</span>
                </button>` : '')}
            </div>
        </div>
    `).join('');
}

let pendingOrderAction = null;

function openOrderActionModal(action, orderId) {
    pendingOrderAction = { action, orderId };
    const isArchive = action === 'archive';
    const modal = document.getElementById('orderActionModal');
    document.getElementById('orderActionTitle').textContent = isArchive ? '¿Archivar este pedido?' : '¿Restaurar este pedido?';
    document.getElementById('orderActionCode').textContent = String(orderId);
    document.getElementById('orderActionDescription').textContent = isArchive
        ? 'El pedido dejará de aparecer en la gestión activa. La venta y sus detalles se conservarán en el historial y podrás restaurarlo cuando quieras.'
        : 'El pedido volverá a la gestión activa para que puedas consultarlo junto con los demás pedidos.';
    const icon = document.getElementById('orderActionIcon');
    icon.className = 'fa-solid ' + (isArchive ? 'fa-box-archive' : 'fa-box-open');
    const iconWrap = document.getElementById('orderActionIconWrap');
    iconWrap.className = 'w-14 h-14 rounded-2xl flex items-center justify-center mx-auto text-xl border ' +
        (isArchive ? 'bg-amber-50 text-amber-700 border-amber-200' : 'bg-emerald-50 text-emerald-700 border-emerald-200');
    const button = document.getElementById('confirmOrderActionButton');
    button.className = 'w-full min-h-11 py-2.5 rounded-xl font-bold text-sm text-white transition-colors inline-flex items-center justify-center gap-2 ' +
        (isArchive ? 'bg-coffee-700 hover:bg-coffee-800' : 'bg-emerald-700 hover:bg-emerald-800');
    button.innerHTML = isArchive
        ? '<i class="fa-solid fa-box-archive"></i><span>Sí, archivar pedido</span>'
        : '<i class="fa-solid fa-box-open"></i><span>Sí, restaurar pedido</span>';
    modal.classList.remove('hidden');
}

function archiveOrder(orderId) {
    openOrderActionModal('archive', orderId);
}

function restoreOrder(orderId) {
    openOrderActionModal('restore', orderId);
}

function closeOrderActionModal() {
    const modal = document.getElementById('orderActionModal');
    if (modal) modal.classList.add('hidden');
    pendingOrderAction = null;
}

async function confirmOrderAction() {
    if (!pendingOrderAction) return;
    const { action, orderId } = pendingOrderAction;
    const codigo = String(orderId).replace(/^#/, '');
    const button = document.getElementById('confirmOrderActionButton');
    const isArchive = action === 'archive';
    button.disabled = true;
    button.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i><span>' + (isArchive ? 'Archivando...' : 'Restaurando...') + '</span>';

    try {
        const endpoint = isArchive ? 'archivar' : 'restaurar';
        const response = await fetch('/gestion/api/pedidos/' + encodeURIComponent(codigo) + '/' + endpoint + '/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': obtenerCsrfTokenAdmin(),
                'X-Requested-With': 'XMLHttpRequest',
            },
        });
        const data = await response.json();
        if (!response.ok || data.status !== 'ok') {
            throw new Error(data.mensaje || (isArchive ? 'No se pudo archivar el pedido.' : 'No se pudo restaurar el pedido.'));
        }

        if (isArchive) {
            const order = orders.find(item => item.id === orderId);
            orders = orders.filter(item => item.id !== orderId);
            if (order && !archivedOrders.some(item => item.id === orderId)) archivedOrders.unshift(order);
        } else {
            const order = archivedOrders.find(item => item.id === orderId);
            archivedOrders = archivedOrders.filter(item => item.id !== orderId);
            if (order && !orders.some(item => item.id === orderId)) orders.unshift(order);
        }

        closeOrderActionModal();
        renderOrdersWorkflow();
        showToast(data.mensaje || (isArchive ? 'Pedido archivado.' : 'Pedido restaurado.'));
    } catch (error) {
        showToast(error.message || (isArchive ? 'Error al archivar el pedido.' : 'Error al restaurar el pedido.'), 'error');
    } finally {
        button.disabled = false;
        button.innerHTML = isArchive
            ? '<i class="fa-solid fa-box-archive"></i><span>Sí, archivar pedido</span>'
            : '<i class="fa-solid fa-box-open"></i><span>Sí, restaurar pedido</span>';
    }
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
            document.getElementById('modalProdCategory').value = prod.category_id;
            document.getElementById('modalProdPrice').value = prod.price;
            document.getElementById('modalProdStock').value = prod.stock;
            document.getElementById('modalProdStatus').value =
                prod.status === 'active' ? 'true' : 'false';
            document.getElementById('modalProdFeatured').checked = Boolean(prod.featured);
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


let pendingDelete = null;

function deleteProduct(id) {
    const producto = products.find(p => p.id === id);
    if (!producto) {
        showToast('No se encontró el producto.');
        return;
    }

    openDeleteConfirmModal({
        type: 'producto',
        id,
        name: producto.name,
        description: 'Se eliminará este producto. Los detalles de pedidos anteriores se conservarán en el historial.',
        icon: 'fa-cake-candles',
    });
}

function deleteCategory(id) {
    const categoria = categories.find(cat => cat.id === id);
    if (!categoria) {
        showToast('No se encontró la categoría.');
        return;
    }

    openDeleteConfirmModal({
        type: 'categoria',
        id,
        name: categoria.name,
        description: categoria.count > 0
            ? 'Esta categoría tiene productos asociados y no se podrá eliminar hasta que quede vacía.'
            : 'Esta acción eliminará la categoría de forma permanente.',
        icon: 'fa-tags',
    });
}

function openDeleteConfirmModal(item) {
    pendingDelete = item;
    document.getElementById('deleteConfirmType').textContent = item.type;
    document.getElementById('deleteConfirmName').textContent = item.name;
    document.getElementById('deleteConfirmDescription').textContent = item.description;
    document.getElementById('deleteConfirmIcon').className = `fa-solid ${item.icon}`;
    document.getElementById('deleteConfirmModal').classList.remove('hidden');
}

function closeDeleteConfirmModal() {
    document.getElementById('deleteConfirmModal').classList.add('hidden');
    pendingDelete = null;
}

async function confirmDeleteItem() {
    if (!pendingDelete) return;

    const item = pendingDelete;
    const button = document.getElementById('confirmDeleteItemButton');
    button.disabled = true;
    button.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i><span>Eliminando...</span>';

    const endpoint = item.type === 'producto'
        ? window.ADMIN_ELIMINAR_PRODUCTO_URL
        : window.ADMIN_ELIMINAR_CATEGORIA_URL;
    const formData = new FormData();
    formData.append('id', item.id);

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
            body: formData,
        });
        const data = await response.json();

        if (!response.ok || data.status !== 'ok') {
            throw new Error(data.mensaje || 'No se pudo eliminar. Revisá si tiene elementos asociados.');
        }

        if (item.type === 'producto') {
            products = products.filter(product => product.id !== item.id);
            renderProductsTable();
        } else {
            categories = categories.filter(category => category.id !== item.id);
            renderCategoriesGrid();
        }

        closeDeleteConfirmModal();
        showToast(data.mensaje || 'Elemento eliminado correctamente.');
        setTimeout(() => window.location.reload(), 650);
    } catch (error) {
        showToast(error.message, 'info');
    } finally {
        button.disabled = false;
        button.innerHTML = '<i class="fa-solid fa-trash-can"></i><span>Sí, eliminar</span>';
    }
}

function saveProduct(event) {
    event.preventDefault();
    const id = document.getElementById('modalProductId').value;
        if (!id) {
        const form = document.getElementById('productForm');
        const formData = new FormData(form);

        fetch(window.ADMIN_CREAR_PRODUCTO_URL, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        })
        .then(async response => {
            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.mensaje || 'No se pudo crear el producto. Revisá los datos.'
                );
            }

            return data;
        })
        .then(data => {
            showToast('Producto creado correctamente');
            closeProductModal();

            // Recargar los productos reales que Django entrega al panel.
            setTimeout(() => window.location.reload(), 700);
        })
        .catch(error => {
            showToast(error.message);
        });

        return;
    }


        if (id) {
            const form = document.getElementById('productForm');
            const formData = new FormData(form);

            formData.set('id', id);

            fetch(window.ADMIN_EDITAR_PRODUCTO_URL, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        })
        .then(async response => {
            const data = await response.json();

            if (!response.ok) {
                const errores = data.details
                    ? JSON.stringify(data.details)
                    : data.mensaje || 'No se pudo editar el producto.';

                throw new Error(errores);
            }

            return data;
        })
        .then(data => {
            showToast('Producto actualizado correctamente');
            closeProductModal();
            setTimeout(() => window.location.reload(), 700);
        })
        .catch(error => {
            showToast(error.message);
        });

        return;
    }



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
            <td class="py-3 px-3 font-bold text-coffee-900 whitespace-nowrap">${item.name}</td>
            <td class="py-3 px-3 text-coffee-600 whitespace-nowrap">${item.category}</td>
            <td class="py-3 px-3 font-bold whitespace-nowrap ${item.stock <= item.min ? 'text-rose-600' : 'text-coffee-900'}">
                ${item.stock} ${item.unit}
            </td>
            <td class="py-3 px-3 text-coffee-500 whitespace-nowrap">${item.min} ${item.unit}</td>
            <td class="py-3 px-3">
                <span class="inventory-status-badge inline-flex items-center justify-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] leading-none font-bold ${item.stock <= item.min ? 'bg-rose-50 text-rose-600 border border-rose-200' : 'bg-emerald-50 text-emerald-700 border border-emerald-200'}">
                    <i class="${item.stock <= item.min ? 'fa-solid fa-triangle-exclamation' : 'fa-solid fa-circle-check'} text-[9px] shrink-0"></i>
                    <span>${item.stock <= item.min ? 'Poco Stock' : 'Suficiente'}</span>
                </span>
            </td>
            <td class="py-3 px-3">
                <button onclick="openRestockModal(${item.id})" class="inventory-restock-btn inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-xl bg-coffee-600 hover:bg-coffee-700 text-white font-bold text-xs leading-none transition-colors shadow-2xs">
                    <i class="fa-solid fa-plus-circle text-[11px] shrink-0"></i>
                    <span>Reponer</span>
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

function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^|; )' + name + '=([^;]*)'));
    return match ? decodeURIComponent(match[2]) : null;
}

function openOrderDetailModal(orderId) {
    const order = orders.find(o => o.id === orderId) || archivedOrders.find(o => o.id === orderId);
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

async function updateOrderStatusFromModal() {
    if (!currentActiveOrder || !window.ADMIN_PEDIDOS_URL) return;

    const newStatus = document.getElementById('modalOrderStatusSelect').value;
    const url = window.ADMIN_PEDIDOS_URL.replace('__CODIGO__', encodeURIComponent(currentActiveOrder.codigo));

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ estado: newStatus })
        });

        const data = await response.json();

        if (!response.ok || data.status !== 'ok') {
            throw new Error(data.mensaje || 'No se pudo actualizar el estado.');
        }

        currentActiveOrder.status = data.estado.toLowerCase();
        showToast('Estado actualizado: ' + data.estado_display);
        renderDashboardViews();
        renderOrdersWorkflow();
    } catch (error) {
        showToast(error.message, 'info');
        console.error('Error al actualizar estado:', error);
    }
}

function renderCategoriesGrid() {
    const grid = document.getElementById('categoriesGrid');
    if (!grid) return;

    if (!categories.length) {
        grid.innerHTML = '<div class="col-span-full rounded-2xl border border-dashed border-cream-300 bg-white p-6 text-sm text-coffee-600">Todavía no hay categorías. Usá “Nueva Categoría” para crear la primera.</div>';
        return;
    }

    grid.innerHTML = categories.map(cat => {
        return `
        <div class="bg-white p-5 rounded-3xl border border-cream-200/80 shadow-sm space-y-3 hover-lift flex flex-col justify-between">
            <div>
                <div class="w-10 h-10 rounded-2xl bg-coffee-50 border border-coffee-200 text-coffee-600 flex items-center justify-center text-lg mb-3">
                    <i class="fa-solid ${cat.icon || 'fa-tag'}"></i>
                </div>
                <h3 class="font-serif-title font-bold text-base text-coffee-900">${escapeHtml(cat.name)}</h3>
                <p class="text-xs text-coffee-600 mt-1">${escapeHtml(cat.slug)}</p>
            </div>
            <div class="pt-3 border-t border-cream-100 flex items-center justify-between gap-2">
                <span class="text-xs font-bold text-coffee-800">${cat.count} productos</span>
                <div class="flex items-center gap-2">
                    <button onclick="editCategory(${cat.id})" class="px-2.5 py-1.5 rounded-xl bg-cream-100 hover:bg-coffee-600 hover:text-white text-coffee-800 font-bold text-xs transition-colors">Editar</button>
                    <button type="button" onclick="deleteCategory(${cat.id})" class="px-2.5 py-1.5 rounded-xl bg-rose-50 hover:bg-rose-600 hover:text-white text-rose-700 border border-rose-200 font-bold text-xs transition-colors" aria-label="Eliminar categoría ${escapeHtml(cat.name)}">Eliminar</button>
                </div>
            </div>
        </div>`;
    }).join('');
}

function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, char => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[char]));
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
            const slugField = document.getElementById('modalCatSlug');
            if (slugField) slugField.value = cat.slug;
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

async function saveCategory(event) {
    event.preventDefault();
    const id = document.getElementById('modalCategoryId').value;
    const name = document.getElementById('modalCatName').value.trim();
    const slug = document.getElementById('modalCatSlug')?.value.trim() || '';
    if (!name) {
        showToast('Ingresá el nombre de la categoría.', 'error');
        return;
    }

    const formData = new URLSearchParams({ nombre: name, slug });
    if (id) formData.set('id', id);

    try {
        const response = await fetch(
            id ? window.ADMIN_EDITAR_CATEGORIA_URL : window.ADMIN_CREAR_CATEGORIA_URL,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                    'X-CSRFToken': obtenerCsrfTokenAdmin(),
                },
                body: formData.toString(),
            }
        );
        const data = await response.json();
        if (!response.ok || data.status !== 'ok') {
            const details = data.details ? Object.values(data.details).flat().map(e => e.message).join(' ') : '';
            throw new Error(details || data.mensaje || 'No se pudo guardar la categoría.');
        }

        closeCategoryModal();
        showToast(id ? 'Categoría actualizada.' : 'Categoría creada.');
        // Volvemos a consultar la base de datos para actualizar conteos, slugs y filtros.
        window.location.reload();
    } catch (error) {
        showToast(error.message || 'Error al guardar la categoría.', 'error');
    }
}

async function loadCustomersFromDatabase() {
    try {
        const response = await fetch('/gestion/api/clientes/', {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        const data = await response.json();
        if (!response.ok || data.status !== 'ok') throw new Error('No se pudieron cargar los clientes.');

        customers = (data.clientes || []).map(cliente => ({
            id: cliente.id,
            name: cliente.nombre,
            city: cliente.ciudad || 'Sin ciudad',
            email: cliente.email || 'Sin email',
            phone: cliente.telefono || 'Sin teléfono',
            ordersCount: cliente.total_pedidos || 0,
            spent: Number(cliente.total_gastado || 0),
        }));
        renderCustomersTable();
    } catch (error) {
        console.error('Error cargando clientes reales:', error);
        const tbody = document.getElementById('customersTableBody');
        if (tbody) tbody.innerHTML = '<tr><td colspan="6" class="p-4 text-center text-coffee-600">No se pudieron cargar los clientes.</td></tr>';
    }
}

function renderCustomersTable() {
    const tbody = document.getElementById('customersTableBody');
    if (!tbody) return;
    if (!customers.length) {
        tbody.innerHTML = '<tr><td colspan="6" class="p-4 text-center text-coffee-600">Todavía no hay clientes registrados.</td></tr>';
        return;
    }
    tbody.innerHTML = customers.map(c => `
        <tr class="hover:bg-cream-50/80 transition-colors">
            <td class="py-3 px-4 font-bold text-coffee-900 min-w-[150px]">${escapeHtml(c.name)}</td>
            <td class="py-3 px-4 text-coffee-600 min-w-[220px] break-words">${escapeHtml(c.email)}<span class="block text-[10px] mt-1">${escapeHtml(c.phone)}</span></td>
            <td class="py-3 px-4 text-coffee-600 whitespace-nowrap min-w-[130px]">${escapeHtml(c.city)}</td>
            <td class="py-3 px-4 font-bold whitespace-nowrap min-w-[120px]">${c.ordersCount} pedidos</td>
            <td class="py-3 px-4 font-bold text-coffee-900 whitespace-nowrap min-w-[130px]">${c.spent.toLocaleString('es-AR')}</td>
            <td class="py-3 px-4 whitespace-nowrap min-w-[130px]">
                <button onclick="showToast('El contacto directo se puede integrar más adelante.', 'info')" class="px-3 py-1.5 rounded-xl bg-emerald-50 hover:bg-emerald-600 hover:text-white text-emerald-700 font-bold text-xs transition-colors border border-emerald-200 inline-flex items-center gap-1">
                    <i class="fa-brands fa-whatsapp text-xs"></i> Contactar
                </button>
            </td>
        </tr>
    `).join('');
}

async function guardarCostoEnvioAutomatico() {
    const input = document.getElementById('settingDeliveryFee');
    const costoEnvio = Number(input?.value);

    if (!input || input.value.trim() === '' || !Number.isFinite(costoEnvio) || costoEnvio < 0) {
        showToast('Ingresá un costo de envío válido.', 'error');
        return;
    }

    input.disabled = true;
    try {
        const response = await fetch('/gestion/api/configuracion/envio/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': obtenerCsrfTokenAdmin(),
            },
            body: JSON.stringify({ costo_envio: costoEnvio }),
        });
        const data = await response.json();

        if (!response.ok || data.status !== 'ok') {
            throw new Error(data.mensaje || 'No se pudo guardar la configuración.');
        }

        input.value = Number(data.costo_envio).toFixed(2).replace(/\\.00$/, '');
        showToast('Costo de envío actualizado y guardado.');
    } catch (error) {
        console.error('Error al guardar costo de envío:', error);
        showToast('No se pudo guardar el costo de envío.', 'error');
    } finally {
        input.disabled = false;
    }
}

async function saveSettings(e) {
    e.preventDefault();

    const input = document.getElementById('settingDeliveryFee');
    const costoEnvio = Number(input?.value);

    if (!Number.isFinite(costoEnvio) || costoEnvio < 0) {
        showToast('Ingresá un costo de envío válido.', 'error');
        return;
    }

    try {
        const response = await fetch('/gestion/api/configuracion/envio/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': obtenerCsrfTokenAdmin(),
            },
            body: JSON.stringify({ costo_envio: costoEnvio }),
        });

        const data = await response.json();

        if (data.status !== 'ok') {
            throw new Error(data.mensaje || 'No se pudo guardar la configuración.');
        }

        showToast('Costo de envío guardado correctamente');
    } catch (error) {
        console.error('Error al guardar configuración:', error);
        showToast('No se pudo guardar el costo de envío.', 'error');
    }
}

function obtenerCsrfTokenAdmin() {
    const cookie = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='));

    return cookie ? decodeURIComponent(cookie.split('=')[1]) : '';
}

function goToStore() {
    window.location.href = '/';
}

function openLogoutModal() {
    document.getElementById('logoutModal').classList.remove('hidden');
}

function closeLogoutModal() {
    document.getElementById('logoutModal').classList.add('hidden');
}

function confirmLogout() {
    closeLogoutModal();
    fetch('/gestion/logout/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': obtenerCsrfTokenAdmin(),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json().then(data => ({ok: response.ok, data})))
    .then(({ok, data}) => {
        if (!ok || data.status !== 'ok') {
            showToast(data.mensaje || 'No se pudo cerrar la sesión.', 'error');
            return;
        }
        window.location.href = data.redirect_url || '/gestion/login/';
    })
    .catch(() => showToast('No se pudo cerrar la sesión. Intentá nuevamente.', 'error'));
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
                labels: window.semanaLabels || [],
                datasets: [{
                    label: 'Ventas ($)',
                    data: window.semanaData || [],
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
