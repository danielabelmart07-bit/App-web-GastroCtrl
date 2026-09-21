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


let activeCategory = "todos";
let searchQuery = "";
let currentSort = "featured";

// DOM elements


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

window.addEventListener('DOMContentLoaded', () => {
    renderMenuProducts();
});

