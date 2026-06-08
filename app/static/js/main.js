// VetLândia - JavaScript Premium App-like

document.addEventListener('DOMContentLoaded', function() {
    // ========================================
    // Mobile Menu Premium
    // ========================================
    const menuToggle = document.getElementById('menuToggle');
    const mobileMenu = document.getElementById('mobileMenu');
    const mobileMenuOverlay = document.getElementById('mobileMenuOverlay');
    const mobileMenuClose = document.getElementById('mobileMenuClose');

    function openMobileMenu() {
        mobileMenu.classList.add('active');
        mobileMenuOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeMobileMenu() {
        mobileMenu.classList.remove('active');
        mobileMenuOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (menuToggle) {
        menuToggle.addEventListener('click', openMobileMenu);
    }

    if (mobileMenuClose) {
        mobileMenuClose.addEventListener('click', closeMobileMenu);
    }

    if (mobileMenuOverlay) {
        mobileMenuOverlay.addEventListener('click', closeMobileMenu);
    }

    // Fechar menu ao clicar em link
    const mobileMenuLinks = document.querySelectorAll('.mobile-menu-link');
    mobileMenuLinks.forEach(link => {
        link.addEventListener('click', closeMobileMenu);
    });

    // Fechar menu com ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && mobileMenu && mobileMenu.classList.contains('active')) {
            closeMobileMenu();
        }
    });

    // ========================================
    // Alerts Auto-hide
    // ========================================
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        // Add close button
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '✕';
        closeBtn.style.cssText = 'background: none; border: none; font-size: 1.25rem; cursor: pointer; margin-left: auto; padding: 0 0 0 16px; opacity: 0.7;';
        closeBtn.addEventListener('click', () => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 200);
        });
        alert.appendChild(closeBtn);

        // Auto-hide after 5 seconds
        setTimeout(() => {
            alert.style.transition = 'opacity 0.3s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // ========================================
    // Smooth Scroll
    // ========================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // ========================================
    // Active Nav Link + Bottom Nav
    // ========================================
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
        }
    });

    const bnavItems = document.querySelectorAll('.bnav-item');
    bnavItems.forEach(item => {
        const href = item.getAttribute('href');
        if (!href) return;
        if (href === '/' ? currentPath === '/' : currentPath.startsWith(href)) {
            item.classList.add('active');
        }
    });

    // ========================================
    // Loading State for Buttons
    // ========================================
    function setButtonLoading(button, loading) {
        if (loading) {
            button.disabled = true;
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = '<div class="spinner" style="width: 20px; height: 20px; border-width: 2px;"></div>';
        } else {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText || button.innerHTML;
        }
    }

    // Export for forms
    window.setButtonLoading = setButtonLoading;

    // ========================================
    // Touch Feedback (App-like)
    // ========================================
    const interactiveElements = document.querySelectorAll('.card-interactive, .btn, .mobile-menu-link, .nav-link');

    interactiveElements.forEach(el => {
        el.addEventListener('touchstart', function() {
            this.style.opacity = '0.7';
        });

        el.addEventListener('touchend', function() {
            this.style.opacity = '1';
        });
    });
});

// ========================================
// API Helpers
// ========================================
async function apiRequest(url, options = {}) {
    const token = localStorage.getItem('access_token');

    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` }),
        },
    };

    const response = await fetch(url, { ...defaultOptions, ...options });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Erro na requisição' }));
        throw new Error(error.detail || 'Erro na requisição');
    }

    return response.json();
}

function saveToken(token) {
    localStorage.setItem('access_token', token);
}

function clearToken() {
    localStorage.removeItem('access_token');
}

function isAuthenticated() {
    return !!localStorage.getItem('access_token');
}

// ========================================
// Intersection Observer (Lazy animations)
// ========================================
if ('IntersectionObserver' in window) {
    const animateOnScroll = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.card, .feature-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.4s, transform 0.4s';
        animateOnScroll.observe(el);
    });
}
