let activeCategory = "todos";
let searchQuery = "";
let currentSort = "featured";

// ============================================================
// DOM ELEMENTS
// ============================================================

const searchInput = document.getElementById('searchInput');
const clearSearchBtn = document.getElementById('clearSearchBtn');
const sortSelect = document.getElementById('sortSelect');
const menuProductsGrid = document.getElementById('menuProductsGrid');
const emptyState = document.getElementById('emptyState');
const productsCountText = document.getElementById('productsCountText');
const resetFiltersBtn = document.getElementById('resetFiltersBtn');
const categoryBtns = document.querySelectorAll('.category-btn');

// ============================================================
// RENDER & FILTER PRODUCTS
// ============================================================

function renderMenuProducts() {

let filtered = MENU_PRODUCTS.filter(item => {

    const matchesCategory =
        activeCategory === 'todos' ||
        item.category === activeCategory;

    const query = searchQuery.toLowerCase().trim();

    const matchesSearch =
        !query ||
        item.name.toLowerCase().includes(query) ||
        item.description.toLowerCase().includes(query) ||
        item.categoryLabel.toLowerCase().includes(query);

    return matchesCategory && matchesSearch;
});


// ========================================================
// SORTING
// ========================================================

if (currentSort === 'price-low') {

    filtered.sort((a, b) => a.price - b.price);

} else if (currentSort === 'price-high') {

    filtered.sort((a, b) => b.price - a.price);

} else if (currentSort === 'name-asc') {

    filtered.sort((a, b) =>
        a.name.localeCompare(b.name, 'es')
    );
}


// ========================================================
// COUNTER
// ========================================================

productsCountText.textContent =
    `Mostrando ${filtered.length} de ${MENU_PRODUCTS.length} productos`;


// ========================================================
// RESET BUTTON
// ========================================================

if (searchQuery || activeCategory !== 'todos') {

    resetFiltersBtn.classList.remove('hidden');

} else {

    resetFiltersBtn.classList.add('hidden');
}


// ========================================================
// EMPTY STATE
// ========================================================

if (filtered.length === 0) {

    menuProductsGrid.innerHTML = '';

    emptyState.classList.remove('hidden');

    return;
}

emptyState.classList.add('hidden');


// ========================================================
// RENDER PRODUCT CARDS
// ========================================================

menuProductsGrid.innerHTML = filtered.map(item => `

    <div
        class="product-card bg-white rounded-3xl overflow-hidden border border-cream-200/80 hover-lift flex flex-col justify-between transition-all duration-300"
    >

        <!-- Product Image -->
        <div class="relative overflow-hidden aspect-[4/3] group">

            <img
                src="${item.image}"
                alt="${escapeHtml(item.name)}"
                loading="lazy"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            >

            <!-- Category -->
            <span
                class="absolute top-4 left-4 bg-white/90 backdrop-blur-md text-coffee-800 text-[11px] font-bold px-3 py-1 rounded-full uppercase tracking-wider shadow-xs"
            >
                ${escapeHtml(item.categoryLabel)}
            </span>

        </div>


        <!-- Product Information -->
        <div class="p-6 flex-grow flex flex-col justify-between">

            <div>

                <h3 class="font-serif-title text-xl font-bold text-coffee-900">
                    ${escapeHtml(item.name)}
                </h3>

                <p class="text-xs text-coffee-700/80 mt-2 leading-relaxed">
                    ${escapeHtml(item.description)}
                </p>

            </div>


            <!-- Price + Cart -->
            <div class="mt-6 flex items-center justify-between pt-4 border-t border-cream-100">

                <div>

                    <span class="text-[11px] text-gray-400 block uppercase tracking-wider">
                        Precio
                    </span>

                    <span class="font-bold text-lg text-coffee-900">
                        $${Number(item.price).toLocaleString('es-AR')}
                    </span>

                </div>


                <button
                    type="button"
                    onclick="addToCart(
                        ${item.id},
                        '${escapeJsString(item.name)}',
                        ${item.price},
                        '${escapeJsString(item.image)}'
                    )"
                    class="px-4 py-2.5 rounded-full bg-cream-100 hover:bg-coffee-600 text-coffee-900 hover:text-white text-xs font-bold transition-all duration-200 flex items-center gap-2 group/btn"
                >

                    <i class="fa-solid fa-plus text-[10px] group-hover/btn:rotate-90 transition-transform"></i>

                    <span>Añadir</span>

                </button>

            </div>

        </div>

    </div>

`).join('');

}

// ============================================================
// HTML ESCAPE
// Evita problemas si un producto contiene caracteres especiales.
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
// JAVASCRIPT STRING ESCAPE
// Evita romper el onclick si el nombre contiene comillas.
// ============================================================

function escapeJsString(value) {

return String(value)
    .replace(/\\/g, '\\\\')
    .replace(/'/g, "\\'")
    .replace(/"/g, '\\"')
    .replace(/\n/g, '\\n')
    .replace(/\r/g, '\\r');

}

// ============================================================
// SEARCH
// ============================================================

searchInput.addEventListener('input', (event) => {

searchQuery = event.target.value;

if (searchQuery) {

    clearSearchBtn.classList.remove('hidden');

} else {

    clearSearchBtn.classList.add('hidden');
}

renderMenuProducts();

});

// ============================================================
// CLEAR SEARCH
// ============================================================

clearSearchBtn.addEventListener('click', () => {

searchInput.value = '';

searchQuery = '';

clearSearchBtn.classList.add('hidden');

renderMenuProducts();

});

// ============================================================
// SORT
// ============================================================

sortSelect.addEventListener('change', (event) => {

currentSort = event.target.value;

renderMenuProducts();

});

// ============================================================
// CATEGORY FILTER
// ============================================================

categoryBtns.forEach(button => {

button.addEventListener('click', () => {

    categoryBtns.forEach(btn => {
        btn.classList.remove('filter-btn-active');
    });

    button.classList.add('filter-btn-active');

    activeCategory =
        button.getAttribute('data-category');

    renderMenuProducts();
});

});

// ============================================================
// RESET ALL FILTERS
// ============================================================

function resetAllFilters() {

activeCategory = 'todos';

searchQuery = '';

currentSort = 'featured';


searchInput.value = '';

clearSearchBtn.classList.add('hidden');

sortSelect.value = 'featured';


categoryBtns.forEach(button => {

    if (
        button.getAttribute('data-category') === 'todos'
    ) {

        button.classList.add('filter-btn-active');

    } else {

        button.classList.remove('filter-btn-active');
    }

});


renderMenuProducts();

}

// ============================================================
// RESET FILTERS BUTTON
// ============================================================

resetFiltersBtn.addEventListener(
'click',
resetAllFilters
);

// ============================================================
// INITIAL RENDER
// ============================================================

window.addEventListener('DOMContentLoaded', () => {

renderMenuProducts();

});