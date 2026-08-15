/* ═══════════════════════════════════════════════════════════════
   JANATHA SYRUP — MAIN JAVASCRIPT
   ═══════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
    initNavbarScroll();
    initAnimateOnScroll();
    initCounterAnimation();
    initHeroParticles();
    initAjaxCartForms();
    initAutoCloseAlerts();
});


/* ─── Navbar Scroll Effect ────────────────────────────────────── */
function initNavbarScroll() {
    const navbar = document.getElementById('mainNavbar');
    if (!navbar) return;

    const handleScroll = () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
}


/* ─── Animate on Scroll (Intersection Observer) ──────────────── */
function initAnimateOnScroll() {
    const elements = document.querySelectorAll('[data-animate]');
    if (!elements.length) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const delay = el.getAttribute('data-delay') || 0;
                setTimeout(() => {
                    el.classList.add('animated');
                }, delay * 100);
                observer.unobserve(el);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px',
    });

    elements.forEach(el => observer.observe(el));
}


/* ─── Counter Animation ──────────────────────────────────────── */
function initCounterAnimation() {
    const counters = document.querySelectorAll('[data-count]');
    if (!counters.length) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(el => observer.observe(el));
}

function animateCounter(el) {
    const target = parseInt(el.getAttribute('data-count'));
    const duration = 2000;
    const start = performance.now();

    function update(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);

        // Ease out cubic
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.floor(eased * target);

        el.textContent = current;

        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            el.textContent = target;
        }
    }

    requestAnimationFrame(update);
}


/* ─── Hero Particles ─────────────────────────────────────────── */
function initHeroParticles() {
    const container = document.getElementById('heroParticles');
    if (!container) return;

    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.style.cssText = `
            position: absolute;
            width: ${Math.random() * 6 + 2}px;
            height: ${Math.random() * 6 + 2}px;
            background: rgba(212, 168, 67, ${Math.random() * 0.3 + 0.05});
            border-radius: 50%;
            top: ${Math.random() * 100}%;
            left: ${Math.random() * 100}%;
            animation: floatParticle ${Math.random() * 8 + 6}s ease-in-out infinite;
            animation-delay: ${Math.random() * 5}s;
        `;
        container.appendChild(particle);
    }

    // Add particle animation CSS
    if (!document.getElementById('particleStyles')) {
        const style = document.createElement('style');
        style.id = 'particleStyles';
        style.textContent = `
            @keyframes floatParticle {
                0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.5; }
                25% { transform: translate(${randomRange(-30, 30)}px, ${randomRange(-30, 30)}px) scale(1.2); opacity: 0.8; }
                50% { transform: translate(${randomRange(-50, 50)}px, ${randomRange(-50, 50)}px) scale(0.8); opacity: 0.3; }
                75% { transform: translate(${randomRange(-20, 20)}px, ${randomRange(-20, 20)}px) scale(1.1); opacity: 0.6; }
            }
        `;
        document.head.appendChild(style);
    }
}

function randomRange(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}


/* ─── AJAX Add to Cart ───────────────────────────────────────── */
function initAjaxCartForms() {
    const forms = document.querySelectorAll('.add-to-cart-form');

    forms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(form);
            const url = form.action;

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                });

                const data = await response.json();

                if (data.success) {
                    // Update cart badge
                    const badge = document.getElementById('cartBadge');
                    if (badge) {
                        badge.textContent = data.cart_count;
                        badge.style.animation = 'bounceIn 0.5s ease';
                        setTimeout(() => {
                            badge.style.animation = '';
                        }, 500);
                    }

                    // Show toast notification
                    showToast(data.message, 'success');

                    // Animate button
                    const btn = form.querySelector('button[type="submit"]');
                    if (btn) {
                        const originalHTML = btn.innerHTML;
                        btn.innerHTML = '<i class="bi bi-check2"></i>';
                        btn.style.background = '#2dbe5c';
                        setTimeout(() => {
                            btn.innerHTML = originalHTML;
                            btn.style.background = '';
                        }, 1500);
                    }
                }
            } catch (error) {
                // Fallback to normal form submission
                form.submit();
            }
        });
    });
}


/* ─── Toast Notifications ────────────────────────────────────── */
function showToast(message, type = 'success') {
    // Remove existing toasts
    const existing = document.querySelector('.toast-notification');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.innerHTML = `
        <div style="
            position: fixed;
            top: 100px;
            right: 20px;
            z-index: 9999;
            background: ${type === 'success' ? '#fff' : '#fff'};
            color: #333;
            padding: 16px 24px;
            border-radius: 12px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.15);
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 500;
            font-size: 0.95rem;
            animation: slideInRight 0.4s ease;
            border-left: 4px solid ${type === 'success' ? '#2dbe5c' : '#D41920'};
            max-width: 350px;
        ">
            <i class="bi ${type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-circle-fill'}" 
               style="color: ${type === 'success' ? '#2dbe5c' : '#D41920'}; font-size: 1.2rem;"></i>
            ${message}
        </div>
    `;

    // Add animation keyframes if not present
    if (!document.getElementById('toastStyles')) {
        const style = document.createElement('style');
        style.id = 'toastStyles';
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOutRight {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }

    document.body.appendChild(toast);

    // Auto remove after 3 seconds
    setTimeout(() => {
        const inner = toast.querySelector('div');
        if (inner) {
            inner.style.animation = 'slideOutRight 0.3s ease forwards';
        }
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}


/* ─── Auto-Close Alerts ──────────────────────────────────────── */
function initAutoCloseAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });
}


/* ─── Smooth Scroll ──────────────────────────────────────────── */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href === '#') return;

        const target = document.querySelector(href);
        if (target) {
            e.preventDefault();
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start',
            });
        }
    });
});
