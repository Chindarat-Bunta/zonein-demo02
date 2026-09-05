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

    // Mobile drawer toggle
    let isMobileOpen = false;
    if (mobileMenuBtn && mobileDrawer) {
        mobileMenuBtn.addEventListener('click', () => {
            isMobileOpen = !isMobileOpen;
            if (isMobileOpen) {
                mobileDrawer.classList.add('active');
                mobileMenuBtn.innerHTML = `
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                `;
            } else {
                mobileDrawer.classList.remove('active');
                mobileMenuBtn.innerHTML = `
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                        <line x1="3" y1="12" x2="21" y2="12"></line>
                        <line x1="3" y1="6" x2="21" y2="6"></line>
                        <line x1="3" y1="18" x2="21" y2="18"></line>
                    </svg>
                `;
            }
        });
    }

    window.handleMobileTab = function (e, tabId) {
        e.preventDefault();
        if (mobileDrawer) mobileDrawer.classList.remove('active');
        isMobileOpen = false;
        if (mobileMenuBtn) {
            mobileMenuBtn.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                    <line x1="3" y1="12" x2="21" y2="12"></line>
                    <line x1="3" y1="6" x2="21" y2="6"></line>
                    <line x1="3" y1="18" x2="21" y2="18"></line>
                </svg>
            `;
        }
        window.switchTab(tabId);
    };

    window.triggerAuth = function (actionName) {
        alert(`[Zone In]: กำลังเปิดหน้าต่าง ${actionName}`);
    };

    window.addEventListener('resize', () => {
        const currentActive = document.querySelector('.nav-tab-btn.active');
        if (currentActive) {
            moveGliderTo(currentActive, false);
        }
    });
});
