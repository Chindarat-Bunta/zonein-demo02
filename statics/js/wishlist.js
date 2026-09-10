/**
 * ZoneIn - Wishlist & Bookmark Manager (Hybrid LocalStorage + Django API)
 */

class WishlistManager {
    constructor() {
        this.storageKey = 'zonein_wishlist_ids';
        this.wishlistSet = new Set(this.loadFromStorage());

        // DOM Header elements
        this.headerBadge = document.getElementById('wishlist-header-count');
        this.totalDisplay = document.getElementById('wishlist-total-display');
        this.toastContainer = document.getElementById('toast-container');

        this.init();
    }

    init() {
        this.bindEvents();
        this.syncWithServer();
        this.refreshUI();
    }

    loadFromStorage() {
        try {
            const raw = localStorage.getItem(this.storageKey);
            return raw ? JSON.parse(raw) : [];
        } catch (e) {
            console.warn('LocalStorage error:', e);
            return [];
        }
    }

    saveToStorage() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(Array.from(this.wishlistSet)));
        } catch (e) {
            console.warn('LocalStorage save error:', e);
        }
    }

    async syncWithServer() {
        try {
            const res = await fetch('/api/wishlist/', {
                headers: { 'Accept': 'application/json' }
            });
            if (res.ok) {
                const data = await res.json();
                if (data.status === 'success' && Array.isArray(data.place_ids)) {
                    // Merge server items with local items
                    data.place_ids.forEach(id => this.wishlistSet.add(Number(id)));
                    this.saveToStorage();
                    this.refreshUI();
                }
            }
        } catch (err) {
            // Silently fall back to LocalStorage
        }
    }

    bindEvents() {
        // Event delegation for wishlist toggle buttons anywhere on the page
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('.btn-wishlist-toggle');
            if (btn) {
                e.preventDefault();
                e.stopPropagation();
                const placeId = Number(btn.getAttribute('data-place-id'));
                const placeName = btn.getAttribute('data-place-name') || 'สถานที่นี้';
                if (placeId) {
                    this.toggle(placeId, placeName, btn);
                }
            }
        });
    }

    async toggle(placeId, placeName = 'สถานที่นี้', triggeredBtn = null) {
        const currentlySaved = this.wishlistSet.has(placeId);
        let action = '';

        if (currentlySaved) {
            this.wishlistSet.delete(placeId);
            action = 'removed';
            this.showToast(`ลบ "${placeName}" ออกจากรายการโปรดแล้ว`, 'info');
        } else {
            this.wishlistSet.add(placeId);
            action = 'added';
            this.showToast(`บันทึก "${placeName}" ลงในรายการโปรดแล้ว ❤️`, 'success');
        }

        this.saveToStorage();
        this.refreshUI();

        // Animate button if triggered
        if (triggeredBtn) {
            triggeredBtn.classList.add('pop-anim');
            setTimeout(() => triggeredBtn.classList.remove('pop-anim'), 400);
        }

        // If on wishlist page and item was removed, animate card removal
        if (action === 'removed' && window.location.pathname.includes('/wishlist')) {
            const card = document.querySelector(`.place-card[data-place-id="${placeId}"]`);
            if (card) {
                card.style.transition = 'all 0.35s ease';
                card.style.opacity = '0';
                card.style.transform = 'scale(0.9) translateY(10px)';
                setTimeout(() => {
                    card.remove();
                    this.checkWishlistEmptyState();
                }, 350);
            }
        }

        // Asynchronously sync with Backend API
        try {
            await fetch('/api/wishlist/toggle/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ place_id: placeId })
            });
        } catch (e) {
            // LocalStorage already has the state
        }
    }

    isWishlisted(placeId) {
        return this.wishlistSet.has(Number(placeId));
    }

    refreshUI() {
        const count = this.wishlistSet.size;

        // Update header badge
        if (this.headerBadge) {
            this.headerBadge.textContent = count;
            if (count > 0) {
                this.headerBadge.classList.add('visible');
            } else {
                this.headerBadge.classList.remove('visible');
            }
        }

        // Update wishlist page total
        if (this.totalDisplay) {
            this.totalDisplay.textContent = count;
        }

        // Update all toggle buttons on current page
        document.querySelectorAll('.btn-wishlist-toggle').forEach(btn => {
            const id = Number(btn.getAttribute('data-place-id'));
            const isSaved = this.wishlistSet.has(id);
            if (isSaved) {
                btn.classList.add('active');
                btn.setAttribute('title', 'ลบออกจากรายการโปรด');
            } else {
                btn.classList.remove('active');
                btn.setAttribute('title', 'บันทึกสถานที่โปรด');
            }

            // Update text on detail page button if present
            const textSpan = btn.querySelector('.wishlist-btn-text');
            if (textSpan) {
                textSpan.textContent = isSaved ? 'บันทึกแล้วในรายการโปรด' : 'บันทึกเป็นสถานที่โปรด';
            }
        });

        this.checkWishlistEmptyState();
    }

    checkWishlistEmptyState() {
        const wishlistGrid = document.getElementById('wishlist-grid');
        const emptyState = document.getElementById('wishlist-empty-state');
        if (wishlistGrid && emptyState) {
            const remainingCards = wishlistGrid.querySelectorAll('.place-card').length;
            if (remainingCards === 0 || this.wishlistSet.size === 0) {
                emptyState.classList.remove('hidden');
            } else {
                emptyState.classList.add('hidden');
            }
        }
    }

    showToast(message, type = 'success') {
        if (!this.toastContainer) return;

        const toast = document.createElement('div');
        toast.className = `toast-item toast-${type}`;

        const icon = type === 'success' ? 'fa-circle-check' : 'fa-circle-info';
        toast.innerHTML = `
            <i class="fa-solid ${icon} toast-icon"></i>
            <span class="toast-message">${this.escapeHTML(message)}</span>
        `;

        this.toastContainer.appendChild(toast);

        // Auto remove after 3 seconds
        setTimeout(() => {
            toast.classList.add('toast-fade-out');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    escapeHTML(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
}

// Instantiate globally
document.addEventListener('DOMContentLoaded', () => {
    window.wishlistManager = new WishlistManager();
});
