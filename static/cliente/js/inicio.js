/* ==========================================================================
   Lógica JavaScript - GastroCtrl
   ========================================================================== */

/*
 * IMPORTANTE:
 * El carrito NO se maneja en este archivo.
 * Su lógica está en carrito.js y funciona mediante el drawer
 * integrado en base.html, compartido por Inicio y Menú.
 */

let isAdminLoggedIn = false;
let adminName = "Valentina";

let profileBtn, profileDropdown, loggedOutView, loggedInView, adminNameDisplay;
let openAdminLoginBtn, logoutBtn, loginModal, closeLoginModalBtn;
let mobileMenuBtn, mobileMenu;

document.addEventListener('DOMContentLoaded', () => {
    profileBtn = document.getElementById('profileBtn');
    profileDropdown = document.getElementById('profileDropdown');
    loggedOutView = document.getElementById('loggedOutView');
    loggedInView = document.getElementById('loggedInView');
    adminNameDisplay = document.getElementById('adminNameDisplay');
    openAdminLoginBtn = document.getElementById('openAdminLoginBtn');
    logoutBtn = document.getElementById('logoutBtn');

    loginModal = document.getElementById('loginModal');
    closeLoginModalBtn = document.getElementById('closeLoginModalBtn');

    mobileMenuBtn = document.getElementById('mobileMenuBtn');
    mobileMenu = document.getElementById('mobileMenu');

    // Perfil
    if (profileBtn && profileDropdown) {
        profileBtn.addEventListener('click', (event) => {
            event.stopPropagation();

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

        document.addEventListener('click', (event) => {
            if (
                !profileDropdown.contains(event.target) &&
                !profileBtn.contains(event.target)
            ) {
                closeProfileDropdown();
            }
        });
    }

    // Login administrativo
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

    // Menú móvil
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // Filtros de productos destacados de Inicio
    const filterBtns = document.querySelectorAll('.filter-btn');
    const productCards = document.querySelectorAll('.product-card');

    if (filterBtns.length && productCards.length) {
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                filterBtns.forEach(button => {
                    button.classList.remove(
                        'active',
                        'bg-coffee-600',
                        'text-white'
                    );
                    button.classList.add(
                        'bg-white',
                        'text-coffee-800'
                    );
                });

                btn.classList.add(
                    'active',
                    'bg-coffee-600',
                    'text-white'
                );
                btn.classList.remove(
                    'bg-white',
                    'text-coffee-800'
                );

                const category = btn.getAttribute('data-category');

                productCards.forEach(card => {
                    const productCategory =
                        card.getAttribute('data-category');

                    card.style.display =
                        category === 'todos' ||
                        productCategory === category
                            ? 'flex'
                            : 'none';
                });
            });
        });
    }
});

/* ==========================================================================
   Funciones auxiliares
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

    modal.classList.remove(
        'pointer-events-none',
        'opacity-0'
    );

    if (modal.firstElementChild) {
        modal.firstElementChild.classList.remove('scale-95');
    }
}

function closeModal(modal) {
    if (!modal) return;

    modal.classList.add(
        'pointer-events-none',
        'opacity-0'
    );

    if (modal.firstElementChild) {
        modal.firstElementChild.classList.add('scale-95');
    }
}

function handleLogin(event) {
    event.preventDefault();

    const input = document.getElementById('adminUserInput');

    if (input && input.value.trim()) {
        adminName = input.value.trim();
    }

    isAdminLoggedIn = true;

    if (adminNameDisplay) {
        adminNameDisplay.textContent = `Admin: ${adminName}`;
    }

    if (loggedOutView) {
        loggedOutView.classList.add('hidden');
    }

    if (loggedInView) {
        loggedInView.classList.remove('hidden');
    }

    closeModal(loginModal);
    showToast(`¡Bienvenida de nuevo, ${adminName}!`);
}
