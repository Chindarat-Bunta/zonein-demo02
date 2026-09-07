/**
 * Zone In — Interactive Map Pin Picker Engine
 * Integrates with:
 * 1. Create Post Modal (หน้าสร้างโพสต์)
 * 2. Explore Search Bar (หน้าค้นหา)
 */

(function () {
    let pickerTarget = 'post'; // 'post' or 'search'
    let leafletMap = null;
    let leafletMarker = null;

    // Default: Sisaket Landmark (Huai Nam Kham & Sri Lamduan Tower)
    let currentLat = 15.1186;
    let currentLng = 104.3228;
    let currentPlaceName = 'หอคอยศรีลำดวนเฉลิมพระเกียรติ';
    let currentAddress = 'เกาะห้วยน้ำคำ ต.หนองครก อ.เมืองศรีสะเกษ';

    // Built-in Knowledge Base of Sisaket Key Attractions (Instant 0ms lookup)
    const LANDMARK_DB = [
        {
            name: 'หอคอยศรีลำดวนเฉลิมพระเกียรติ',
            lat: 15.1186,
            lng: 104.3228,
            address: 'เกาะห้วยน้ำคำ ต.หนองครก อ.เมืองศรีสะเกษ จ.ศรีสะเกษ',
            keywords: ['หอคอย', 'ศรีลำดวน', 'เกาะห้วยน้ำคำ', 'หนองครก']
        },
        {
            name: 'ผามออีแดง (อุทยานแห่งชาติเขาพระวิหาร)',
            lat: 14.3912,
            lng: 104.7077,
            address: 'อุทยานแห่งชาติเขาพระวิหาร ต.เสาธงชัย อ.กันทรลักษ์ จ.ศรีสะเกษ',
            keywords: ['ผามออีแดง', 'เขาพระวิหาร', 'กันทรลักษ์', 'เสาธงชัย']
        },
        {
            name: 'ปราสาทหินสระกำแพงใหญ่',
            lat: 15.0116,
            lng: 104.1481,
            address: 'วัดสระกำแพงใหญ่ ต.สระกำแพงใหญ่ อ.อุทุมพรพิสัย จ.ศรีสะเกษ',
            keywords: ['สระกำแพงใหญ่', 'ปราสาทขอม', 'อุทุมพรพิสัย']
        },
        {
            name: 'วัดป่ามหาเจดีย์แก้ว (วัดล้านขวด)',
            lat: 14.6198,
            lng: 104.4262,
            address: 'บ้านดอน ต.สิ อ.ขุนหาญ จ.ศรีสะเกษ',
            keywords: ['วัดล้านขวด', 'เจดีย์แก้ว', 'ขุนหาญ', 'บ้านดอน']
        },
        {
            name: 'สวนสมเด็จพระศรีนครินทร์ ศรีสะเกษ',
            lat: 15.1102,
            lng: 104.3167,
            address: 'วิทยาลัยเกษตรและเทคโนโลยี ต.หนองครก อ.เมืองศรีสะเกษ จ.ศรีสะเกษ',
            keywords: ['สวนสมเด็จ', 'ลำดวน', 'สวนสัตว์', 'สวนสาธารณะ']
        },
        {
            name: 'เขื่อนราษีไศล',
            lat: 15.3411,
            lng: 104.0543,
            address: 'ต.หนองแค อ.ราษีไศล จ.ศรีสะเกษ',
            keywords: ['เขื่อนราษีไศล', 'ราษีไศล', 'แม่น้ำมูล']
        },
        {
            name: 'ปราสาทปรางค์กู่',
            lat: 14.8624,
            lng: 104.0205,
            address: 'ต.กู่ อ.ปรางค์กู่ จ.ศรีสะเกษ',
            keywords: ['ปรางค์กู่', 'ปราสาทกู่']
        },
        {
            name: 'ไก่ย่างไม้มะดัน ห้วยทับทัน',
            lat: 15.0645,
            lng: 104.0150,
            address: 'ริมทางหลวง 226 ต.ห้วยทับทัน อ.ห้วยทับทัน จ.ศรีสะเกษ',
            keywords: ['ไม้มะดัน', 'ห้วยทับทัน', 'ไก่ย่าง']
        },
        {
            name: 'ศาลหลักเมืองศรีสะเกษ',
            lat: 15.1147,
            lng: 104.3283,
            address: 'ต.เมืองใต้ อ.เมืองศรีสะเกษ จ.ศรีสะเกษ',
            keywords: ['ศาลหลักเมือง', 'ใจกลางเมือง']
        },
        {
            name: 'วัดมหาพุทธาราม (วัดพระโต)',
            lat: 15.1158,
            lng: 104.3275,
            address: 'ต.เมืองเหนือ อ.เมืองศรีสะเกษ จ.ศรีสะเกษ',
            keywords: ['วัดพระโต', 'หลวงพ่อโต', 'มหาพุทธาราม']
        }
    ];

    // Custom Red Pin Marker for Leaflet
    function createCustomPinIcon() {
        if (typeof L === 'undefined') return null;
        return L.divIcon({
            className: 'custom-picker-pin',
            html: `
                <svg class="pin-svg-icon" width="36" height="36" viewBox="0 0 24 24" fill="#ef4444" stroke="#ffffff" stroke-width="1.8">
                    <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                </svg>
            `,
            iconSize: [36, 36],
            iconAnchor: [18, 36]
        });
    }

    // Initialize Leaflet Map
    function initLeafletMap() {
        const container = document.getElementById('mapPickerCanvas');
        if (!container || typeof L === 'undefined') return;

        if (leafletMap) {
            leafletMap.invalidateSize();
            return;
        }

        leafletMap = L.map('mapPickerCanvas', {
            center: [currentLat, currentLng],
            zoom: 14,
            zoomControl: true
        });

        // Add CartoDB / OSM Tile Layer (High performance, crisp rendering)
        L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://carto.com/">CARTO</a>, &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
            subdomains: 'abcd',
            maxZoom: 19
        }).addTo(leafletMap);

        // Marker
        const pinIcon = createCustomPinIcon();
        leafletMarker = L.marker([currentLat, currentLng], {
            icon: pinIcon,
            draggable: true
        }).addTo(leafletMap);

        // Marker drag events
        leafletMarker.on('dragend', function (e) {
            const pos = e.target.getLatLng();
            setPinnedCoordinates(pos.lat, pos.lng, true);
        });

        // Map click event
        leafletMap.on('click', function (e) {
            setPinnedCoordinates(e.latlng.lat, e.latlng.lng, true);
        });
    }

    // Update coordinates and reverse geocode
    function setPinnedCoordinates(lat, lng, shouldGeocode = true, customName = null, customAddress = null) {
        currentLat = lat;
        currentLng = lng;

        if (leafletMarker) {
            leafletMarker.setLatLng([lat, lng]);
        }
        if (leafletMap) {
            leafletMap.panTo([lat, lng]);
        }

        // Update Coordinate Badge
        const coordsEl = document.getElementById('pickerCoordsDisplay');
        if (coordsEl) {
            coordsEl.textContent = `พิกัด: ${lat.toFixed(6)}, ${lng.toFixed(6)}`;
        }

        if (customName) {
            currentPlaceName = customName;
            currentAddress = customAddress || `${customName}, จ.ศรีสะเกษ`;
            updateLocationInfoDisplay();
            return;
        }

        // Check against known landmarks database first (instant match)
        const matchedLandmark = findNearbyLandmark(lat, lng);
        if (matchedLandmark) {
            currentPlaceName = matchedLandmark.name;
            currentAddress = matchedLandmark.address;
            updateLocationInfoDisplay();
            return;
        }

        // Otherwise reverse geocode via Nominatim
        if (shouldGeocode) {
            reverseGeocode(lat, lng);
        }
    }

    // Lookup within 400m of known landmarks
    function findNearbyLandmark(lat, lng) {
        const THRESHOLD = 0.005; // approx 500m
        for (const lm of LANDMARK_DB) {
            const dLat = Math.abs(lm.lat - lat);
            const dLng = Math.abs(lm.lng - lng);
            if (dLat < THRESHOLD && dLng < THRESHOLD) {
                return lm;
            }
        }
        return null;
    }

    // Update text in preview footer
    function updateLocationInfoDisplay() {
        const nameEl = document.getElementById('pickerNameDisplay');
        const addrEl = document.getElementById('pickerAddressDisplay');
        if (nameEl) nameEl.textContent = currentPlaceName || 'ตำแหน่งที่ปักหมุด';
        if (addrEl) addrEl.textContent = currentAddress || `${currentLat.toFixed(5)}, ${currentLng.toFixed(5)}`;
    }

    // Reverse Geocoding with fallback
    let geocodeTimer = null;
    function reverseGeocode(lat, lng) {
        const nameEl = document.getElementById('pickerNameDisplay');
        const addrEl = document.getElementById('pickerAddressDisplay');
        if (nameEl) nameEl.textContent = 'กำลังระบุชื่อสถานที่...';
        if (addrEl) addrEl.textContent = `พิกัด: ${lat.toFixed(5)}, ${lng.toFixed(5)}`;

        if (geocodeTimer) clearTimeout(geocodeTimer);
        geocodeTimer = setTimeout(async () => {
            try {
                const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=17&addressdetails=1&accept-language=th`;
                const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
                if (res.ok) {
                    const data = await res.json();
                    if (data && data.address) {
                        const addr = data.address;
                        const place = addr.tourism || addr.amenity || addr.historic || addr.leisure || addr.building || addr.suburb || addr.village || addr.city_district || 'จุดเช็กอิน';
                        const district = addr.county || addr.district || addr.suburb || '';
                        const province = addr.province || addr.state || 'ศรีสะเกษ';

                        currentPlaceName = (data.name && data.name !== data.display_name) ? data.name : place;
                        if (!currentPlaceName || currentPlaceName === 'จุดเช็กอิน') {
                            currentPlaceName = `${place} (${district || province})`;
                        }
                        currentAddress = data.display_name.split(',').slice(0, 4).join(', ');
                        updateLocationInfoDisplay();
                        return;
                    }
                }
            } catch (err) {
                console.warn('[Zone In Reverse Geocode Warning]:', err);
            }

            // Fallback
            currentPlaceName = `จุดเช็กอิน (${lat.toFixed(4)}, ${lng.toFixed(4)})`;
            currentAddress = `จ.ศรีสะเกษ (พิกัด: ${lat.toFixed(5)}, ${lng.toFixed(5)})`;
            updateLocationInfoDisplay();
        }, 300);
    }

    // Quick Pin from Landmark Buttons
    window.quickPinLandmark = function (name, lat, lng, address) {
        setPinnedCoordinates(lat, lng, false, name, address);
        const searchInput = document.getElementById('mapPickerSearchInput');
        if (searchInput) searchInput.value = name;
    };

    // Parse Google Maps Link or Coordinate String
    function parseQueryOrGoogleMapsLink(inputStr) {
        if (!inputStr) return null;
        const s = inputStr.trim();

        // 1. Direct Coordinates "15.1186, 104.3228" or "15.1186 104.3228"
        const coordMatch = s.match(/([+-]?\d+\.?\d*)[,\s]+([+-]?\d+\.?\d*)/);
        if (coordMatch) {
            const lat = parseFloat(coordMatch[1]);
            const lng = parseFloat(coordMatch[2]);
            if (lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180) {
                return { lat, lng, name: `พิกัด GPS (${lat.toFixed(4)}, ${lng.toFixed(4)})` };
            }
        }

        // 2. Google Maps URL with @lat,lng
        const atMatch = s.match(/@([+-]?\d+\.\d+),([+-]?\d+\.\d+)/);
        if (atMatch) {
            return {
                lat: parseFloat(atMatch[1]),
                lng: parseFloat(atMatch[2]),
                name: 'ตำแหน่งจาก Google Maps'
            };
        }

        // 3. Google Maps URL with ?q=lat,lng or &query=lat,lng
        const qMatch = s.match(/[?&](?:q|query|destination)=([+-]?\d+\.\d+),([+-]?\d+\.\d+)/);
        if (qMatch) {
            return {
                lat: parseFloat(qMatch[1]),
                lng: parseFloat(qMatch[2]),
                name: 'ตำแหน่งจาก Google Maps'
            };
        }

        return null;
    }

    // Search Location in Modal
    window.searchPickerLocation = async function () {
        const input = document.getElementById('mapPickerSearchInput');
        if (!input || !input.value.trim()) return;

        const q = input.value.trim();

        // 1. Check if user pasted a Google Maps URL or coordinates
        const parsed = parseQueryOrGoogleMapsLink(q);
        if (parsed) {
            setPinnedCoordinates(parsed.lat, parsed.lng, true, parsed.name);
            return;
        }

        // 2. Search in local Sisaket Landmarks DB
        const lowerQ = q.toLowerCase();
        const found = LANDMARK_DB.find(lm =>
            lm.name.toLowerCase().includes(lowerQ) ||
            lm.keywords.some(k => lowerQ.includes(k.toLowerCase()))
        );
        if (found) {
            setPinnedCoordinates(found.lat, found.lng, false, found.name, found.address);
            return;
        }

        // 3. Online Search via Nominatim Geocoding
        try {
            const searchQuery = q.includes('ศรีสะเกษ') || q.includes('Sisaket') ? q : `${q} ศรีสะเกษ`;
            const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}&countrycodes=th&limit=1&accept-language=th`;
            const res = await fetch(url);
            if (res.ok) {
                const results = await res.json();
                if (results && results.length > 0) {
                    const item = results[0];
                    const lat = parseFloat(item.lat);
                    const lng = parseFloat(item.lon);
                    setPinnedCoordinates(lat, lng, false, item.display_name.split(',')[0], item.display_name);
                    return;
                }
            }
        } catch (e) {
            console.warn('[Zone In Search Geocode Warning]:', e);
        }

        alert(`ไม่พบพิกัดของ "${q}" กรุณาคลิกเลือกจุดบนแผนที่โดยตรง`);
    };

    // Center on User GPS
    window.centerPickerOnUserGPS = function () {
        if (!navigator.geolocation) {
            alert('อุปกรณ์ของคุณไม่รองรับการดึงพิกัด GPS');
            return;
        }

        const btn = document.querySelector('.btn-picker-gps');
        if (btn) btn.style.opacity = '0.6';

        navigator.geolocation.getCurrentPosition(
            (pos) => {
                if (btn) btn.style.opacity = '1';
                const lat = pos.coords.latitude;
                const lng = pos.coords.longitude;
                setPinnedCoordinates(lat, lng, true, 'ตำแหน่งปัจจุบันของฉัน');
                if (window.showToast) window.showToast('ดึงพิกัดปัจจุบันเรียบร้อย 📍');
            },
            (err) => {
                if (btn) btn.style.opacity = '1';
                alert('ไม่สามารถดึงตำแหน่งปัจจุบันได้ กรุณาเปิดการอนุญาต GPS ในเบราว์เซอร์');
            },
            { timeout: 8000, enableHighAccuracy: true }
        );
    };

    // Open Modal
    window.openMapPickerModal = function (target = 'post') {
        pickerTarget = target;
        const modal = document.getElementById('mapPickerModal');
        if (!modal) return;

        // Configure Action Button Label based on target
        const confirmBtnText = document.getElementById('pickerConfirmBtnText');
        if (confirmBtnText) {
            confirmBtnText.textContent = (target === 'search') ? 'ค้นหาตามตำแหน่งนี้' : 'ใช้ตำแหน่งนี้ในโพสต์';
        }

        modal.style.display = 'flex';
        modal.setAttribute('aria-hidden', 'false');

        // Check if caller already has coordinates or location text
        if (target === 'post') {
            const latVal = parseFloat(document.getElementById('postLatitude')?.value);
            const lngVal = parseFloat(document.getElementById('postLongitude')?.value);
            const addrVal = document.getElementById('postAddress')?.value;
            const nameVal = document.getElementById('postPlaceName')?.value;

            if (!isNaN(latVal) && !isNaN(lngVal) && latVal !== 0 && lngVal !== 0) {
                currentLat = latVal;
                currentLng = lngVal;
                currentPlaceName = nameVal || addrVal || currentPlaceName;
                currentAddress = addrVal || currentAddress;
            }
        } else if (target === 'search') {
            const searchVal = document.getElementById('exploreSearchInput')?.value;
            if (searchVal && searchVal.trim()) {
                const searchInput = document.getElementById('mapPickerSearchInput');
                if (searchInput) searchInput.value = searchVal;
            }
        }

        // Initialize or update map
        setTimeout(() => {
            initLeafletMap();
            setPinnedCoordinates(currentLat, currentLng, false, currentPlaceName, currentAddress);
            if (leafletMap) {
                leafletMap.invalidateSize();
                leafletMap.setView([currentLat, currentLng], 14);
            }
        }, 80);

        // Enter key in search box
        const searchInput = document.getElementById('mapPickerSearchInput');
        if (searchInput) {
            searchInput.onkeydown = function (e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    window.searchPickerLocation();
                }
            };
        }
    };

    // Close Modal
    window.closeMapPickerModal = function () {
        const modal = document.getElementById('mapPickerModal');
        if (!modal) return;
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
    };

    // Confirm & Apply Pinned Location back to caller
    window.confirmPickedLocation = function () {
        if (pickerTarget === 'post') {
            // Apply to Create Post Form
            const nameInput = document.getElementById('postPlaceName');
            const addrInput = document.getElementById('postAddress');
            const latInput = document.getElementById('postLatitude');
            const lngInput = document.getElementById('postLongitude');
            const mapFrame = document.getElementById('postMapEmbed');
            const mapStatusBadge = document.getElementById('mapStatusBadge');

            if (addrInput) {
                addrInput.value = currentAddress || currentPlaceName;
            }
            if (nameInput && (!nameInput.value || !nameInput.value.trim())) {
                nameInput.value = currentPlaceName;
            }
            if (latInput) latInput.value = currentLat.toFixed(6);
            if (lngInput) lngInput.value = currentLng.toFixed(6);

            // Update live embed preview
            if (mapFrame) {
                mapFrame.src = `https://maps.google.com/maps?q=${currentLat},${currentLng}&hl=th&z=16&output=embed`;
            }
            if (mapStatusBadge) {
                mapStatusBadge.textContent = `📍 ปักหมุด: ${currentPlaceName}`;
                mapStatusBadge.classList.add('checked-in');
            }

            closeMapPickerModal();

            // Ensure Create Post Modal remains open & in focus
            const createPostModal = document.getElementById('createPostModal');
            if (createPostModal && !createPostModal.classList.contains('active')) {
                createPostModal.classList.add('active');
            }

            if (typeof window.showToast === 'function') {
                window.showToast(`ปักหมุดสำเร็จ: ${currentPlaceName} 📍`);
            }
        } else if (pickerTarget === 'search') {
            // Apply to Search Explore Bar
            const searchInput = document.getElementById('exploreSearchInput');
            if (searchInput) {
                searchInput.value = currentPlaceName;
                searchInput.dispatchEvent(new Event('input', { bubbles: true }));
            }

            closeMapPickerModal();

            // Ensure Search Tab is active
            if (typeof window.switchTab === 'function') {
                window.switchTab('search');
            }

            if (typeof window.showToast === 'function') {
                window.showToast(`ค้นหาตามตำแหน่งที่ปักหมุด: ${currentPlaceName} 🔍`);
            }
        }
    };

    // Close on Escape key
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            const modal = document.getElementById('mapPickerModal');
            if (modal && modal.style.display !== 'none') {
                window.closeMapPickerModal();
            }
        }
    });

    // Make functions globally available
    window.MapPicker = {
        open: window.openMapPickerModal,
        close: window.closeMapPickerModal,
        confirm: window.confirmPickedLocation,
        setCoordinates: setPinnedCoordinates
    };
})();
