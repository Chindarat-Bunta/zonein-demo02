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
        if (actionName && actionName.toLowerCase().includes('in')) {
            window.location.href = '/signin/';
        } else {
            window.location.href = '/signup/';
        }
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
});
