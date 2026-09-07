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
    } else if (tabGlider) {
        tabGlider.style.opacity = '0';
    }

    // Tab click & hover events
    tabButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const targetTab = btn.getAttribute('data-tab');
            const targetPanel = document.getElementById(`panel-${targetTab}`);
            if (!targetPanel) {
                // Not on home page or tab panel does not exist - navigate directly
                e.preventDefault();
                window.location.href = (targetTab === 'home' ? '/' : `/#${targetTab}`);
                return;
            }
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
            } else if (tabGlider) {
                tabGlider.style.opacity = '0';
            }
        });
    }

    // Function: Switch active tab & content panel
    window.switchTab = function (tabId) {
        if (typeof window.switchProfileTab === 'function' && (tabId === 'reviews' || tabId === 'wishlist')) {
            window.switchProfileTab(tabId);
            return;
        }

        const activePanel = document.getElementById(`panel-${tabId}`);
        if (!activePanel) {
            window.location.href = (tabId === 'home' ? '/' : `/#${tabId}`);
            return;
        }

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
        activePanel.classList.add('active');

        // Keep URL hash in sync cleanly
        if (window.history && window.history.replaceState) {
            window.history.replaceState(null, null, `#${tabId}`);
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

    // Desktop Profile Dropdown controls
    window.toggleDesktopProfileMenu = function(e) {
        if (e) {
            e.stopPropagation();
            if (e.preventDefault) e.preventDefault();
        }
        const menu = document.getElementById('desktopDropdownMenu');
        if (!menu) return;
        const isHidden = (menu.style.display === 'none' || menu.style.display === '' || !menu.classList.contains('show'));
        if (isHidden) {
            menu.style.display = 'block';
            menu.classList.add('show');
        } else {
            menu.style.display = 'none';
            menu.classList.remove('show');
        }
    };

    // Close dropdown on click outside
    document.addEventListener('click', (e) => {
        const desktopMenu = document.getElementById('desktopDropdownMenu');
        const desktopBtn = document.getElementById('desktopProfileBtn');
        if (desktopMenu && (desktopMenu.style.display === 'block' || desktopMenu.classList.contains('show'))) {
            if (!desktopMenu.contains(e.target) && (!desktopBtn || !desktopBtn.contains(e.target))) {
                desktopMenu.style.display = 'none';
                desktopMenu.classList.remove('show');
            }
        }
        if (mobileProfileDropdown && mobileProfileDropdown.classList.contains('open')) {
            if (!mobileProfileDropdown.contains(e.target) && !mobileProfileBtn.contains(e.target)) {
                closeProfileDropdown();
            }
        }
    });

    // Close dropdown on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            if (mobileProfileDropdown && mobileProfileDropdown.classList.contains('open')) {
                closeProfileDropdown();
            }
            const desktopMenu = document.getElementById('desktopDropdownMenu');
            if (desktopMenu) desktopMenu.style.display = 'none';
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

    // =========================================================================
    // CREATE POST MODAL & MAP CHECK-IN ENGINE
    // =========================================================================
    window.handlePostClick = function (e) {
        if (e) e.preventDefault();
        if (typeof window.IS_AUTHENTICATED !== 'undefined' && !window.IS_AUTHENTICATED) {
            if (typeof window.showToast === 'function') {
                window.showToast('กรุณาเข้าสู่ระบบก่อนสร้างโพสต์ใหม่ ✍️');
            } else {
                alert('กรุณาเข้าสู่ระบบก่อนสร้างโพสต์ใหม่ ✍️');
            }
            setTimeout(() => {
                window.location.href = '/signin/?next=/';
            }, 800);
            return;
        }
        window.openCreatePostModal();
    };

    window.openCreatePostModal = function () {
        if (typeof window.IS_AUTHENTICATED !== 'undefined' && !window.IS_AUTHENTICATED) {
            if (typeof window.showToast === 'function') {
                window.showToast('กรุณาเข้าสู่ระบบก่อนสร้างโพสต์ใหม่ ✍️');
            } else {
                alert('กรุณาเข้าสู่ระบบก่อนสร้างโพสต์ใหม่ ✍️');
            }
            setTimeout(() => {
                window.location.href = '/signin/?next=/';
            }, 800);
            return;
        }
        const modal = document.getElementById('createPostModal');
        if (!modal) return;
        modal.classList.add('active');
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';

        setTimeout(() => {
            const nameInput = document.getElementById('postPlaceName');
            if (nameInput) nameInput.focus();
        }, 120);
    };

    window.closeCreatePostModal = function () {
        const modal = document.getElementById('createPostModal');
        if (!modal) return;
        modal.classList.remove('active');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';

        // Reset error box
        const errorBox = document.getElementById('postErrorBox');
        if (errorBox) errorBox.style.display = 'none';
    };

    window.handlePostBackdropClick = function (e) {
        if (e && e.target && e.target.id === 'createPostModal') {
            window.closeCreatePostModal();
        }
    };

    // Category pill selection
    window.selectPostCategory = function (categoryVal, btnElem) {
        const input = document.getElementById('postCategoryInput');
        if (input) input.value = categoryVal;

        const allPills = document.querySelectorAll('#postCategoryGrid .category-pill');
        allPills.forEach(pill => pill.classList.remove('active'));
        if (btnElem) btnElem.classList.add('active');
    };

    // Quick location chips
    window.applyLocationChip = function (locText) {
        const addrInput = document.getElementById('postAddress');
        if (addrInput) {
            addrInput.value = locText;
            addrInput.focus();
            window.updatePostMapLocation(locText);
        }
    };

    // Live Map Check-in & Search Updates
    let mapUpdateTimer = null;
    window.updatePostMapLocation = function (query) {
        if (mapUpdateTimer) clearTimeout(mapUpdateTimer);
        mapUpdateTimer = setTimeout(() => {
            const mapFrame = document.getElementById('postMapEmbed');
            const mapStatusBadge = document.getElementById('mapStatusBadge');
            const placeName = document.getElementById('postPlaceName')?.value || '';
            const searchQuery = query || placeName || 'ศรีสะเกษ';

            if (mapFrame) {
                mapFrame.src = `https://maps.google.com/maps?q=${encodeURIComponent(searchQuery)}&hl=th&z=15&output=embed`;
            }
            if (mapStatusBadge) {
                mapStatusBadge.textContent = query ? `📍 ปักหมุด: ${query}` : 'พร้อมปักหมุด';
            }
        }, 350);
    };

    window.handlePlaceNameInput = function (placeName) {
        const addrInput = document.getElementById('postAddress');
        if (!addrInput || !addrInput.value.trim()) {
            window.updatePostMapLocation(placeName);
        }
    };

    // GPS Current Location Check-in
    window.getCurrentLocationCheckIn = function () {
        const btn = document.getElementById('btnCheckInGPS');
        const badge = document.getElementById('mapStatusBadge');
        const addrInput = document.getElementById('postAddress');
        const latInput = document.getElementById('postLatitude');
        const lngInput = document.getElementById('postLongitude');
        const mapFrame = document.getElementById('postMapEmbed');

        if (!navigator.geolocation) {
            alert('เบราว์เซอร์ของคุณไม่รองรับการดึงพิกัด GPS');
            return;
        }

        if (btn) btn.classList.add('loading');
        if (badge) badge.textContent = '🛰️ กำลังค้นหาพิกัด...';

        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const lat = pos.coords.latitude;
                const lng = pos.coords.longitude;

                if (latInput) latInput.value = lat.toFixed(6);
                if (lngInput) lngInput.value = lng.toFixed(6);

                if (addrInput) {
                    addrInput.value = `พิกัดเช็กอิน: ${lat.toFixed(5)}, ${lng.toFixed(5)}`;
                }

                if (mapFrame) {
                    mapFrame.src = `https://maps.google.com/maps?q=${lat},${lng}&hl=th&z=16&output=embed`;
                }

                if (badge) {
                    badge.textContent = `📍 เช็กอินแล้ว (${lat.toFixed(4)}, ${lng.toFixed(4)})`;
                    badge.classList.add('checked-in');
                }

                if (btn) btn.classList.remove('loading');
            },
            (err) => {
                console.warn("[Zone In GPS Error]:", err);
                if (badge) badge.textContent = '⚠️ ไม่สามารถดึง GPS ได้';
                if (btn) btn.classList.remove('loading');
                alert('ไม่สามารถระบุพิกัดตำแหน่งปัจจุบันได้ กรุณาอนุญาตการเข้าถึงตำแหน่งในเบราว์เซอร์ของคุณ');
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
        );
    };

    // Photo Dropzone and File selection
    window.triggerPostFileInput = function () {
        const fileInput = document.getElementById('postImageInput');
        if (fileInput) fileInput.click();
    };

    window.handlePostFileSelect = function (e) {
        const file = e.target.files ? e.target.files[0] : null;
        if (!file) return;

        if (!file.type.startsWith('image/')) {
            alert('กรุณาเลือกไฟล์รูปภาพ (JPG, PNG, WEBP, GIF)');
            return;
        }

        const reader = new FileReader();
        reader.onload = function (event) {
            const previewImg = document.getElementById('postImagePreview');
            const previewContainer = document.getElementById('postPreviewContainer');
            const dropzone = document.getElementById('postDropzone');

            if (previewImg && previewContainer && dropzone) {
                previewImg.src = event.target.result;
                previewContainer.style.display = 'block';
                dropzone.style.display = 'none';
            }
        };
        reader.readAsDataURL(file);
    };

    window.removePostImage = function () {
        const fileInput = document.getElementById('postImageInput');
        const urlInput = document.getElementById('postImageUrlInput');
        const previewImg = document.getElementById('postImagePreview');
        const previewContainer = document.getElementById('postPreviewContainer');
        const dropzone = document.getElementById('postDropzone');

        if (fileInput) fileInput.value = '';
        if (urlInput) urlInput.value = '';
        if (previewImg) previewImg.src = '';
        if (previewContainer) previewContainer.style.display = 'none';
        if (dropzone) dropzone.style.display = 'block';
    };

    window.togglePostUrlInput = function () {
        const wrap = document.getElementById('postUrlInputWrap');
        if (!wrap) return;
        const isHidden = wrap.style.display === 'none' || wrap.style.display === '';
        wrap.style.display = isHidden ? 'block' : 'none';
        if (isHidden) {
            const input = document.getElementById('postImageUrlInput');
            if (input) input.focus();
        }
    };

    window.handlePostUrlInput = function (urlVal) {
        if (!urlVal || !urlVal.trim()) return;
        const cleanUrl = urlVal.trim();
        if (cleanUrl.startsWith('http://') || cleanUrl.startsWith('https://')) {
            const previewImg = document.getElementById('postImagePreview');
            const previewContainer = document.getElementById('postPreviewContainer');
            const dropzone = document.getElementById('postDropzone');

            if (previewImg && previewContainer && dropzone) {
                previewImg.src = cleanUrl;
                previewContainer.style.display = 'block';
                dropzone.style.display = 'none';
            }
        }
    };

    // Star Rating
    const ratingLabels = {
        1: "⭐ 1.0 ต้องปรับปรุง",
        2: "⭐ 2.0 พอใช้",
        3: "⭐ 3.0 ปานกลาง",
        4: "⭐ 4.0 ดีมาก",
        5: "⭐ 5.0 ยอดเยี่ยมมาก!"
    };

    window.setPostRating = function (ratingVal) {
        const ratingInput = document.getElementById('postRatingInput');
        if (ratingInput) ratingInput.value = ratingVal;

        const starBtns = document.querySelectorAll('#postStarRating .star-btn');
        starBtns.forEach(btn => {
            const r = parseInt(btn.getAttribute('data-rating'), 10);
            if (r <= ratingVal) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        const badge = document.getElementById('postRatingBadge');
        if (badge && ratingLabels[ratingVal]) {
            badge.textContent = ratingLabels[ratingVal];
        }
    };

    // Character Counter
    window.updatePostCharCount = function (textarea) {
        const counter = document.getElementById('postCharCount');
        if (counter && textarea) {
            counter.textContent = `${textarea.value.length} / 800`;
        }
    };

    // Form submission via AJAX
    window.handleCreatePostSubmit = async function (e) {
        e.preventDefault();

        const nameInput = document.getElementById('postPlaceName');
        const errorBox = document.getElementById('postErrorBox');
        const errorText = document.getElementById('postErrorText');
        const submitBtn = document.getElementById('btnSubmitPost');
        const btnText = submitBtn ? submitBtn.querySelector('.btn-text') : null;
        const btnSpinner = submitBtn ? submitBtn.querySelector('.btn-spinner') : null;

        if (!nameInput || !nameInput.value.trim()) {
            if (errorBox && errorText) {
                errorText.textContent = "กรุณากรอกชื่อสถานที่หรือหัวข้อโพสต์";
                errorBox.style.display = 'flex';
            }
            if (nameInput) nameInput.focus();
            return;
        }

        if (errorBox) errorBox.style.display = 'none';

        // Set Loading state
        if (submitBtn) submitBtn.disabled = true;
        if (btnText) btnText.textContent = "กำลังเผยแพร่...";
        if (btnSpinner) btnSpinner.style.display = 'inline-block';

        const form = document.getElementById('createPostForm');
        const formData = new FormData(form);

        try {
            const response = await fetch('/api/places/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Success Toast
                const toast = document.getElementById('toast') || document.getElementById('zoneinToast');
                if (toast) {
                    toast.innerHTML = `<span style="font-size: 1.1rem;">🎉</span> <span>โพสต์สถานที่ของคุณสำเร็จแล้ว!</span>`;
                    toast.classList.add('show');
                    toast.style.display = 'block';
                    setTimeout(() => {
                        toast.classList.remove('show');
                        toast.style.display = 'none';
                    }, 4000);
                }

                // Reset form & preview
                form.reset();
                window.removePostImage();
                window.closeCreatePostModal();

                // If detail URL provided, navigate smoothly
                if (data.place && data.place.detail_url) {
                    setTimeout(() => {
                        window.location.href = data.place.detail_url;
                    }, 650);
                } else {
                    setTimeout(() => {
                        window.location.reload();
                    }, 800);
                }
            } else {
                const errMsg = data.error || (data.message ? data.message : "เกิดข้อผิดพลาดในการบันทึกโพสต์ กรุณาลองใหม่อีกครั้ง");
                if (errorBox && errorText) {
                    errorText.textContent = errMsg;
                    errorBox.style.display = 'flex';
                }
            }
        } catch (err) {
            console.error("[Zone In] Post submit error:", err);
            if (errorBox && errorText) {
                errorText.textContent = "เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์ กรุณาลองใหม่อีกครั้ง";
                errorBox.style.display = 'flex';
            }
        } finally {
            if (submitBtn) submitBtn.disabled = false;
            if (btnText) btnText.textContent = "เผยแพร่โพสต์";
            if (btnSpinner) btnSpinner.style.display = 'none';
        }
    };

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const modal = document.getElementById('createPostModal');
            if (modal && modal.classList.contains('active')) {
                window.closeCreatePostModal();
            }
        }
    });

    // Setup drag and drop listeners for post dropzone
    document.addEventListener('DOMContentLoaded', () => {
        const dropzone = document.getElementById('postDropzone');
        if (dropzone) {
            ['dragenter', 'dragover'].forEach(eventName => {
                dropzone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    dropzone.classList.add('dragover');
                });
            });

            ['dragleave', 'drop'].forEach(eventName => {
                dropzone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    dropzone.classList.remove('dragover');
                });
            });

            dropzone.addEventListener('drop', (e) => {
                const dt = e.dataTransfer;
                const files = dt.files;
                if (files && files.length > 0) {
                    const input = document.getElementById('postImageInput');
                    if (input) {
                        input.files = files;
                        window.handlePostFileSelect({ target: { files: files } });
                    }
                }
            });
        }
    });

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

    // Auto-switch to search tab if URL has #search and panel exists on page
    function checkHashAndSwitch() {
        const hash = window.location.hash.replace('#', '').toLowerCase();
        if (hash === 'search' || hash === 'notifications' || hash === 'home') {
            const targetPanel = document.getElementById(`panel-${hash}`);
            if (targetPanel) {
                window.switchTab(hash);
            }
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

            // 1. Text Query Match (matches Place Title, Location, and District)
            const q = filterState.query.toLowerCase();
            const matchesQuery = !filterState.query || title.includes(q) || location.toLowerCase().includes(q);

            // 2. Category Match
            const matchesCat = filterState.category === 'all' || category === filterState.category;

            // 3. Location Match
            const matchesLoc = filterState.location === 'all' || location.includes(filterState.location);

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

// Global Wishlist Quick Toggle function for cards across all pages
window.quickToggleWishlist = async function (event, placeId, btn) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    if (typeof window.IS_AUTHENTICATED !== 'undefined' && !window.IS_AUTHENTICATED) {
        if (typeof showToast === 'function') {
            showToast('กรุณาเข้าสู่ระบบเพื่อบันทึกรายการโปรด 🔖');
        } else if (typeof showDetailToast === 'function') {
            showDetailToast('กรุณาเข้าสู่ระบบเพื่อบันทึกรายการโปรด 🔖');
        } else {
            alert('กรุณาเข้าสู่ระบบเพื่อบันทึกรายการโปรด');
        }
        return;
    }
    if (!placeId) return;

    if (btn) btn.disabled = true;
    try {
        const res = await fetch('/api/wishlist/toggle/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({ place_id: placeId })
        });
        const data = await res.json();
        if (data.status === 'success' || data.success) {
            const isSaved = (typeof data.is_wishlisted !== 'undefined') ? data.is_wishlisted : data.is_saved;
            // Synchronize all buttons targeting this place_id on the active page
            document.querySelectorAll(`[data-wishlist-place-id="${placeId}"]`).forEach(b => {
                b.classList.toggle('active', isSaved);
                b.setAttribute('title', isSaved ? 'นำออกจากรายการโปรด' : 'บันทึกในรายการโปรด');
                const svg = b.querySelector('svg');
                if (svg) svg.setAttribute('fill', isSaved ? '#e05d5d' : 'none');
            });
            if (btn) {
                btn.classList.toggle('active', isSaved);
                btn.setAttribute('title', isSaved ? 'นำออกจากรายการโปรด' : 'บันทึกในรายการโปรด');
                const svg = btn.querySelector('svg');
                if (svg) svg.setAttribute('fill', isSaved ? '#e05d5d' : 'none');
            }

            const msg = isSaved ? 'บันทึกในรายการโปรดเรียบร้อยแล้ว ❤️' : 'นำออกจากรายการโปรดแล้ว';
            if (typeof showToast === 'function') {
                showToast(msg);
            } else if (typeof showDetailToast === 'function') {
                showDetailToast(msg);
            }
        } else {
            const err = data.message || 'เกิดข้อผิดพลาด กรุณาลองใหม่';
            if (typeof showToast === 'function') showToast(err);
            else if (typeof showDetailToast === 'function') showDetailToast(err);
        }
    } catch (err) {
        console.error('quickToggleWishlist error:', err);
    } finally {
        if (btn) btn.disabled = false;
    }
};
