/**
 * Zone In — Navigation & Tabs Interactive Engine
 * Controls: Sliding Glider Pill, Tab Switching, Mobile Drawer
 */

document.addEventListener('DOMContentLoaded', () => {
    const tabsContainer = document.getElementById('navTabsContainer');
    const tabGlider = document.getElementById('tabGlider');
    const tabButtons = document.querySelectorAll('.nav-tab-btn');
    const mobileProfileBtn = document.getElementById('mobileProfileBtn');
    const mobileProfileDropdown = document.getElementById('mobileProfileDropdown');

    // Function: Position the sliding pill glider behind the target tab
    function moveGliderTo(button, animate = true) {
        if (!button || !tabGlider || !tabsContainer) return;

        const btnRect = button.getBoundingClientRect();
        const containerRect = tabsContainer.getBoundingClientRect();

        const leftOffset = btnRect.left - containerRect.left;
        const width = btnRect.width;

        if (!animate) {
            tabGlider.style.transition = 'none';
        } else {
            tabGlider.style.transition = 'all 0.45s cubic-bezier(0.34, 1.56, 0.64, 1)';
        }

        tabGlider.style.left = `${leftOffset}px`;
        tabGlider.style.width = `${width}px`;
        tabGlider.style.opacity = '1';

        if (!animate) {
            // Force reflow
            tabGlider.offsetHeight;
            tabGlider.style.transition = 'all 0.45s cubic-bezier(0.34, 1.56, 0.64, 1)';
        }
    }

    // Initialize Glider on the active tab
    const activeTab = document.querySelector('.nav-tab-btn.active');
    if (activeTab) {
        setTimeout(() => moveGliderTo(activeTab, false), 80);
    }

    // Tab click & hover events
    tabButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const targetTab = btn.getAttribute('data-tab');
            e.preventDefault();
            switchTab(targetTab);
        });

        // Hover preview effect
        btn.addEventListener('mouseenter', () => {
            moveGliderTo(btn, true);
        });
    });

    // Reset glider back to active tab when mouse leaves
    if (tabsContainer) {
        tabsContainer.addEventListener('mouseleave', () => {
            const currentActive = document.querySelector('.nav-tab-btn.active');
            if (currentActive) {
                moveGliderTo(currentActive, true);
            }
        });
    }

    // Function: Switch active tab & content panel
    window.switchTab = function (tabId) {
        tabButtons.forEach(b => {
            if (b.getAttribute('data-tab') === tabId) {
                b.classList.add('active');
                moveGliderTo(b, true);
            } else {
                b.classList.remove('active');
            }
        });

        // Update mobile nav icon buttons
        document.querySelectorAll('.mobile-nav-icon-btn').forEach(mb => {
            if (mb.getAttribute('data-tab') === tabId) {
                mb.classList.add('active');
            } else {
                mb.classList.remove('active');
            }
        });

        // Switch active display panel
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        const activePanel = document.getElementById(`panel-${tabId}`);
        if (activePanel) {
            activePanel.classList.add('active');
        }
    };

    // Mobile Profile Dropdown controls
    function openProfileDropdown() {
        if (!mobileProfileDropdown) return;
        mobileProfileDropdown.classList.add('open');
        if (mobileProfileBtn) {
            mobileProfileBtn.classList.add('active');
            mobileProfileBtn.setAttribute('aria-expanded', 'true');
        }
    }

    function closeProfileDropdown() {
        if (!mobileProfileDropdown) return;
        mobileProfileDropdown.classList.remove('open');
        if (mobileProfileBtn) {
            mobileProfileBtn.classList.remove('active');
            mobileProfileBtn.setAttribute('aria-expanded', 'false');
        }
    }

    function toggleProfileDropdown(e) {
        if (e) {
            e.stopPropagation();
            e.preventDefault();
        }
        if (!mobileProfileDropdown) return;
        if (mobileProfileDropdown.classList.contains('open')) {
            closeProfileDropdown();
        } else {
            openProfileDropdown();
        }
    }

    if (mobileProfileBtn) {
        mobileProfileBtn.addEventListener('click', toggleProfileDropdown);
    }

    // Close dropdown on click outside
    document.addEventListener('click', (e) => {
        if (mobileProfileDropdown && mobileProfileDropdown.classList.contains('open')) {
            if (!mobileProfileDropdown.contains(e.target) && !mobileProfileBtn.contains(e.target)) {
                closeProfileDropdown();
            }
        }
    });

    // Close dropdown on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && mobileProfileDropdown && mobileProfileDropdown.classList.contains('open')) {
            closeProfileDropdown();
        }
    });

    window.handleMobileAuth = function (actionName) {
        closeProfileDropdown();
        window.triggerAuth(actionName);
    };

    window.triggerAuth = function (actionName) {
        alert(`[Zone In]: กำลังเปิดหน้าต่าง ${actionName}`);
    };

    // Handler for Floating Action Button (Post)
    let toastTimeout = null;
    window.handlePostClick = function (e) {
        if (e) e.preventDefault();
        console.log("[Zone In]: Floating Post button clicked — ready for post creation feature integration");

        const toast = document.getElementById('zoneinToast');
        if (toast) {
            toast.classList.add('show');
            if (toastTimeout) clearTimeout(toastTimeout);
            toastTimeout = setTimeout(() => {
                toast.classList.remove('show');
            }, 3200);
        }
    };

    window.addEventListener('resize', () => {
        const currentActive = document.querySelector('.nav-tab-btn.active');
        if (currentActive) {
            moveGliderTo(currentActive, false);
        }
    });

    // =========================================================================
    // SEARCH & EXPLORE FEED INTERACTIVE ENGINE
    // =========================================================================
    const searchInput = document.getElementById('exploreSearchInput');
    const btnClearSearch = document.getElementById('btnClearSearch');
    const btnSideFilterToggle = document.getElementById('btnSideFilterToggle');
    const sideFilterPanel = document.getElementById('sideFilterPanel');
    const filterCountBadge = document.getElementById('filterCountBadge');
    const quickChips = document.querySelectorAll('.filter-quick-chip');
    const filterCatSelect = document.getElementById('filterCategorySelect');
    const filterLocSelect = document.getElementById('filterLocationSelect');
    const filterRatingSelect = document.getElementById('filterRatingSelect');
    const filterSortSelect = document.getElementById('filterSortSelect');
    const btnResetFilters = document.getElementById('btnResetFilters');
    const btnApplyFilters = document.getElementById('btnApplyFilters');
    const exploreCards = document.querySelectorAll('.explore-card');
    const exploreGrid = document.getElementById('exploreMediaGrid');

    // Auto-switch to search tab if URL has #search
    function checkHashAndSwitch() {
        const hash = window.location.hash.replace('#', '').toLowerCase();
        if (hash === 'search' || hash === 'notifications' || hash === 'home') {
            window.switchTab(hash);
        }
    }
    checkHashAndSwitch();
    window.addEventListener('hashchange', checkHashAndSwitch);

    // Filter state
    const filterState = {
        query: '',
        category: 'all',
        location: 'all',
        minRating: 0,
        sort: 'recommended',
    };

    function applyExploreFilters() {
        let visibleCount = 0;

        exploreCards.forEach(card => {
            const title = (card.getAttribute('data-title') || '').toLowerCase();
            const category = card.getAttribute('data-category') || '';
            const location = card.getAttribute('data-location') || '';
            const rating = parseFloat(card.getAttribute('data-rating') || '0');

            // 1. Text Query Match
            const matchesQuery = !filterState.query || title.includes(filterState.query.toLowerCase());

            // 2. Category Match
            const matchesCat = filterState.category === 'all' || category === filterState.category;

            // 3. Location Match
            const matchesLoc = filterState.category === 'all' || filterState.location === 'all' || location.includes(filterState.location);

            // 4. Rating Match
            const matchesRating = filterState.minRating === 0 || rating >= filterState.minRating;

            if (matchesQuery && matchesCat && matchesLoc && matchesRating) {
                card.style.display = '';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        // Update active filter badge
        let activeFilterCount = 0;
        if (filterState.category !== 'all') activeFilterCount++;
        if (filterState.location !== 'all') activeFilterCount++;
        if (filterState.minRating > 0) activeFilterCount++;

        if (filterCountBadge) {
            if (activeFilterCount > 0) {
                filterCountBadge.innerText = activeFilterCount;
                filterCountBadge.style.display = 'inline-flex';
                if (btnSideFilterToggle) btnSideFilterToggle.classList.add('active');
            } else {
                filterCountBadge.style.display = 'none';
                if (btnSideFilterToggle && (!sideFilterPanel || !sideFilterPanel.classList.contains('open'))) {
                    btnSideFilterToggle.classList.remove('active');
                }
            }
        }
    }

    // Live search input listener
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            filterState.query = e.target.value.trim();
            if (btnClearSearch) {
                if (filterState.query.length > 0) {
                    btnClearSearch.classList.add('visible');
                } else {
                    btnClearSearch.classList.remove('visible');
                }
            }
            applyExploreFilters();
        });
    }

    if (btnClearSearch) {
        btnClearSearch.addEventListener('click', () => {
            if (searchInput) {
                searchInput.value = '';
                searchInput.focus();
            }
            btnClearSearch.classList.remove('visible');
            filterState.query = '';
            applyExploreFilters();
        });
    }

    // Toggle Side Filter Panel ("ซึ่งตรงค้นหาจะมีการกรองข้างๆ")
    if (btnSideFilterToggle && sideFilterPanel) {
        btnSideFilterToggle.addEventListener('click', (e) => {
            e.preventDefault();
            const isOpen = sideFilterPanel.classList.toggle('open');
            btnSideFilterToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
            if (isOpen) {
                btnSideFilterToggle.classList.add('active');
            } else {
                let activeFilterCount = 0;
                if (filterState.category !== 'all') activeFilterCount++;
                if (filterState.location !== 'all') activeFilterCount++;
                if (filterState.minRating > 0) activeFilterCount++;
                if (activeFilterCount === 0) {
                    btnSideFilterToggle.classList.remove('active');
                }
            }
        });
    }

    // Category Quick Chips
    quickChips.forEach(chip => {
        chip.addEventListener('click', () => {
            quickChips.forEach(c => c.classList.remove('active'));
            chip.classList.add('active');

            const cat = chip.getAttribute('data-category') || 'all';
            filterState.category = cat;

            if (filterCatSelect) {
                filterCatSelect.value = cat;
            }

            applyExploreFilters();
        });
    });

    // Dropdown Selects in Filter Panel
    if (filterCatSelect) {
        filterCatSelect.addEventListener('change', (e) => {
            const cat = e.target.value;
            filterState.category = cat;
            quickChips.forEach(c => {
                if (c.getAttribute('data-category') === cat) {
                    c.classList.add('active');
                } else {
                    c.classList.remove('active');
                }
            });
            applyExploreFilters();
        });
    }

    if (filterLocSelect) {
        filterLocSelect.addEventListener('change', (e) => {
            filterState.location = e.target.value;
            applyExploreFilters();
        });
    }

    if (filterRatingSelect) {
        filterRatingSelect.addEventListener('change', (e) => {
            filterState.minRating = parseFloat(e.target.value) || 0;
            applyExploreFilters();
        });
    }

    if (btnResetFilters) {
        btnResetFilters.addEventListener('click', () => {
            filterState.category = 'all';
            filterState.location = 'all';
            filterState.minRating = 0;
            filterState.query = '';
            if (searchInput) searchInput.value = '';
            if (btnClearSearch) btnClearSearch.classList.remove('visible');
            if (filterCatSelect) filterCatSelect.value = 'all';
            if (filterLocSelect) filterLocSelect.value = 'all';
            if (filterRatingSelect) filterRatingSelect.value = '0';
            quickChips.forEach(c => {
                if (c.getAttribute('data-category') === 'all') c.classList.add('active');
                else c.classList.remove('active');
            });
            applyExploreFilters();
        });
    }

    if (btnApplyFilters && sideFilterPanel) {
        btnApplyFilters.addEventListener('click', () => {
            applyExploreFilters();
            sideFilterPanel.classList.remove('open');
            if (btnSideFilterToggle) btnSideFilterToggle.setAttribute('aria-expanded', 'false');
        });
    }
});

