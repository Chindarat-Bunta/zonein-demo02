/**
 * Zone In — Navigation & Tabs Interactive Engine
 * Controls: Sliding Glider Pill, Tab Switching, Mobile Drawer
 */

document.addEventListener('DOMContentLoaded', () => {
    const tabsContainer = document.getElementById('navTabsContainer');
    const tabGlider = document.getElementById('tabGlider');
    const tabButtons = document.querySelectorAll('.nav-tab-btn');
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileDrawer = document.getElementById('mobileDrawer');

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

        // Update mobile drawer links
        document.querySelectorAll('.mobile-tab-btn').forEach(mb => {
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

    // Mobile drawer toggle & backdrop controls
    const mobileDrawerBackdrop = document.getElementById('mobileDrawerBackdrop');
    const drawerCloseBtn = document.getElementById('drawerCloseBtn');

    function openMobileDrawer() {
        if (!mobileDrawer) return;
        mobileDrawer.classList.add('active');
        if (mobileDrawerBackdrop) mobileDrawerBackdrop.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeMobileDrawer() {
        if (!mobileDrawer) return;
        mobileDrawer.classList.remove('active');
        if (mobileDrawerBackdrop) mobileDrawerBackdrop.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (mobileDrawer && mobileDrawer.classList.contains('active')) {
                closeMobileDrawer();
            } else {
                openMobileDrawer();
            }
        });
    }

    if (drawerCloseBtn) {
        drawerCloseBtn.addEventListener('click', closeMobileDrawer);
    }

    if (mobileDrawerBackdrop) {
        mobileDrawerBackdrop.addEventListener('click', closeMobileDrawer);
    }

    // Close drawer on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && mobileDrawer && mobileDrawer.classList.contains('active')) {
            closeMobileDrawer();
        }
    });

    window.handleMobileTab = function (e, tabId) {
        e.preventDefault();
        closeMobileDrawer();
        window.switchTab(tabId);
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
});
