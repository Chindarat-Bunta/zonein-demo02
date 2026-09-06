/**
 * ZoneIn - Place Review Search & Filter Engine (ES6 Modular Pattern)
 */

class PlaceFilterEngine {
    constructor() {
        // DOM Elements
        this.form = document.getElementById('filter-form');
        this.searchInput = document.getElementById('search-input');
        this.btnClearSearch = document.getElementById('btn-clear-search');
        this.categoryChips = document.querySelectorAll('#category-chips .filter-chip');
        this.selectedCategoryInput = document.getElementById('selected-category');
        this.locationSelect = document.getElementById('location-select');
        this.ratingSelect = document.getElementById('rating-select');
        this.sortSelect = document.getElementById('sort-select');
        this.btnResetFilter = document.getElementById('btn-reset-filter');
        this.btnEmptyReset = document.getElementById('btn-empty-reset');
        this.activeFiltersBadge = document.getElementById('active-filters-badge');

        // Output Views
        this.placesGrid = document.getElementById('places-grid');
        this.emptyStateView = document.getElementById('empty-state-view');
        this.countNumber = document.getElementById('count-number');
        this.loadingIndicator = document.getElementById('filter-loading');

        // State & Timers
        this.debounceTimer = null;
        this.abortController = null;

        this.init();
    }

    init() {
        if (!this.form) return;

        this.bindEvents();
        this.updateActiveFilterCount();
    }

    bindEvents() {
        // 1. Keyword search typing (Debounced Real-time)
        if (this.searchInput) {
            this.searchInput.addEventListener('input', () => {
                this.toggleClearButton();
                this.handleSearchDebounce();
            });

            // Shortcut: '/' key focuses search bar
            window.addEventListener('keydown', (e) => {
                if (e.key === '/' && document.activeElement !== this.searchInput && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
                    e.preventDefault();
                    this.searchInput.focus();
                }
            });
        }

        // 2. Clear search input button
        if (this.btnClearSearch) {
            this.btnClearSearch.addEventListener('click', () => {
                this.searchInput.value = '';
                this.toggleClearButton();
                this.applyFilters();
                this.searchInput.focus();
            });
        }

        // 3. Category Chip Click
        this.categoryChips.forEach(chip => {
            chip.addEventListener('click', (e) => {
                const category = chip.getAttribute('data-category');
                this.setCategory(category);
                this.applyFilters();
            });
        });

        // 4. Select Dropdowns (Location, Rating, Sort)
        [this.locationSelect, this.ratingSelect, this.sortSelect].forEach(select => {
            if (select) {
                select.addEventListener('change', () => {
                    this.applyFilters();
                });
            }
        });

        // 5. Reset Filter Buttons (Search bar reset + Empty state reset)
        if (this.btnResetFilter) {
            this.btnResetFilter.addEventListener('click', () => this.resetAllFilters());
        }
        if (this.btnEmptyReset) {
            this.btnEmptyReset.addEventListener('click', () => this.resetAllFilters());
        }

        // 6. Form Submission (Enter key / Search button)
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.applyFilters();
        });

        // 7. Popstate (Browser Back/Forward)
        window.addEventListener('popstate', () => {
            this.loadFiltersFromURL();
            this.applyFilters(false);
        });
    }

    toggleClearButton() {
        if (!this.btnClearSearch || !this.searchInput) return;
        if (this.searchInput.value.trim().length > 0) {
            this.btnClearSearch.classList.remove('hidden');
        } else {
            this.btnClearSearch.classList.add('hidden');
        }
    }

    setCategory(categorySlug) {
        this.categoryChips.forEach(chip => {
            if (chip.getAttribute('data-category') === categorySlug) {
                chip.classList.add('active');
            } else {
                chip.classList.remove('active');
            }
        });
        if (this.selectedCategoryInput) {
            this.selectedCategoryInput.value = categorySlug;
        }
    }

    handleSearchDebounce() {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.applyFilters();
        }, 280);
    }

    getFilterParams() {
        const q = this.searchInput ? this.searchInput.value.trim() : '';
        const category = this.selectedCategoryInput ? this.selectedCategoryInput.value : 'all';
        const location = this.locationSelect ? this.locationSelect.value : 'all';
        const minRating = this.ratingSelect ? this.ratingSelect.value : '';
        const sort = this.sortSelect ? this.sortSelect.value : 'rating';

        const params = new URLSearchParams();
        if (q) params.set('q', q);
        if (category && category !== 'all') params.set('category', category);
        if (location && location !== 'all') params.set('location', location);
        if (minRating) params.set('min_rating', minRating);
        if (sort && sort !== 'rating') params.set('sort', sort);

        return params;
    }

    updateActiveFilterCount() {
        let count = 0;
        if (this.searchInput && this.searchInput.value.trim().length > 0) count++;
        if (this.selectedCategoryInput && this.selectedCategoryInput.value && this.selectedCategoryInput.value !== 'all') count++;
        if (this.locationSelect && this.locationSelect.value && this.locationSelect.value !== 'all') count++;
        if (this.ratingSelect && this.ratingSelect.value) count++;

        if (this.activeFiltersBadge) {
            if (count > 0) {
                this.activeFiltersBadge.textContent = count;
                this.activeFiltersBadge.classList.remove('hidden');
            } else {
                this.activeFiltersBadge.classList.add('hidden');
            }
        }
    }

    async applyFilters(updateURL = true) {
        this.updateActiveFilterCount();
        const params = this.getFilterParams();

        if (updateURL) {
            const queryStr = params.toString();
            const newRelativePathQuery = window.location.pathname + (queryStr ? '?' + queryStr : '');
            window.history.pushState(null, '', newRelativePathQuery);
        }

        // Cancel pending request if any
        if (this.abortController) {
            this.abortController.abort();
        }
        this.abortController = new AbortController();

        // Show loading state
        if (this.loadingIndicator) this.loadingIndicator.classList.remove('hidden');

        try {
            const response = await fetch(`/api/places/?${params.toString()}`, {
                signal: this.abortController.signal,
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const data = await response.json();
            this.renderResults(data);
        } catch (error) {
            if (error.name !== 'AbortError') {
                console.error('Filter fetch error:', error);
            }
        } finally {
            if (this.loadingIndicator) this.loadingIndicator.classList.add('hidden');
        }
    }

    renderResults(data) {
        const places = data.places || [];
        const count = data.count || 0;

        // Update Counter
        if (this.countNumber) {
            this.countNumber.textContent = count;
        }

        // Handle Empty State
        if (count === 0) {
            if (this.placesGrid) this.placesGrid.innerHTML = '';
            if (this.emptyStateView) this.emptyStateView.classList.remove('hidden');
            return;
        }

        // Hide Empty State and render cards
        if (this.emptyStateView) this.emptyStateView.classList.add('hidden');

        if (this.placesGrid) {
            this.placesGrid.innerHTML = places.map(place => this.buildPlaceCardHTML(place)).join('');
            if (window.wishlistManager) {
                window.wishlistManager.refreshUI();
            }
        }
    }

    buildPlaceCardHTML(place) {
        const categoryBadge = place.category ? `
            <span class="place-category-badge" style="background: ${place.category.color};">
                <i class="fa-solid ${place.category.icon}"></i> ${this.escapeHTML(place.category.name)}
            </span>
        ` : '';

        const featuredBadge = place.is_featured ? `
            <span class="place-featured-badge">
                <i class="fa-solid fa-crown"></i> แนะนำ
            </span>
        ` : '';

        const locationTag = place.location ? `
            <span class="place-location-tag">
                <i class="fa-solid fa-location-dot"></i> ${this.escapeHTML(place.location.zone || '')}${place.location.city ? ', ' + this.escapeHTML(place.location.city) : ''}
            </span>
        ` : '';

        const tagsHTML = (place.tags && place.tags.length > 0) ? `
            <div class="place-card-tags">
                ${place.tags.map(tag => `<span class="tag-chip">#${this.escapeHTML(tag)}</span>`).join('')}
            </div>
        ` : '';

        return `
            <article class="place-card" data-place-id="${place.id}">
                <div class="place-card-image-wrap">
                    <img 
                        src="${this.escapeHTML(place.image_url)}" 
                        alt="${this.escapeHTML(place.name)}" 
                        class="place-card-img"
                        loading="lazy"
                    >
                    ${categoryBadge}
                    ${featuredBadge}
                    <div class="place-rating-badge">
                        <i class="fa-solid fa-star star-icon"></i> ${place.rating.toFixed(1)}
                        <span class="review-count">(${place.review_count})</span>
                    </div>
                </div>

                <div class="place-card-content">
                    <div class="place-meta-header">
                        ${locationTag}
                        <span class="place-price-tag">${this.escapeHTML(place.price_display)}</span>
                    </div>

                    <h3 class="place-card-title">
                        <a href="/places/${place.slug}/">${this.escapeHTML(place.name)}</a>
                    </h3>

                    <p class="place-card-desc">
                        ${this.escapeHTML(this.truncateWords(place.description, 18))}
                    </p>

                    ${tagsHTML}

                    <div class="place-card-footer">
                        <span class="place-address-snippet" title="${this.escapeHTML(place.address)}">
                            <i class="fa-regular fa-map"></i> ${this.escapeHTML(this.truncateChars(place.address, 28))}
                        </span>
                        <a href="/places/${place.slug}/" class="btn-card-view">
                            ดูรีวิว <i class="fa-solid fa-arrow-right"></i>
                        </a>
                    </div>
                </div>
            </article>
        `;
    }

    resetAllFilters() {
        if (this.searchInput) {
            this.searchInput.value = '';
            this.toggleClearButton();
        }
        this.setCategory('all');
        if (this.locationSelect) this.locationSelect.value = 'all';
        if (this.ratingSelect) this.ratingSelect.value = '';
        if (this.sortSelect) this.sortSelect.value = 'rating';

        this.applyFilters();
    }

    loadFiltersFromURL() {
        const params = new URLSearchParams(window.location.search);
        if (this.searchInput) {
            this.searchInput.value = params.get('q') || '';
            this.toggleClearButton();
        }
        const cat = params.get('category') || 'all';
        this.setCategory(cat);

        if (this.locationSelect) this.locationSelect.value = params.get('location') || 'all';
        if (this.ratingSelect) this.ratingSelect.value = params.get('min_rating') || '';
        if (this.sortSelect) this.sortSelect.value = params.get('sort') || 'rating';
    }

    truncateWords(str, numWords) {
        if (!str) return '';
        const words = str.split(/\s+/);
        if (words.length <= numWords) return str;
        return words.slice(0, numWords).join(' ') + '...';
    }

    truncateChars(str, numChars) {
        if (!str) return '';
        if (str.length <= numChars) return str;
        return str.slice(0, numChars) + '...';
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

// Auto-initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.placeFilter = new PlaceFilterEngine();
});
