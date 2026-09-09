/**
 * ZoneIn - Google Maps Navigation Helper & Link Generator Module
 */

class MapsNavigator {
    /**
     * Validate whether latitude and longitude are within acceptable geographic bounds.
     * @param {number|string} lat
     * @param {number|string} lng
     * @returns {boolean}
     */
    static isValidCoordinate(lat, lng) {
        if (lat === null || lat === undefined || lat === '' ||
            lng === null || lng === undefined || lng === '') {
            return false;
        }

        const numLat = parseFloat(lat);
        const numLng = parseFloat(lng);

        if (isNaN(numLat) || isNaN(numLng)) {
            return false;
        }

        return numLat >= -90.0 && numLat <= 90.0 && numLng >= -180.0 && numLng <= 180.0;
    }

    /**
     * Generate Google Maps Direction Navigation URL.
     * @param {Object} options
     * @param {number|string} [options.latitude]
     * @param {number|string} [options.longitude]
     * @param {string} [options.destinationName]
     * @param {string} [options.address]
     * @returns {string} Google Maps URL
     */
    static generateGoogleMapsUrl({ latitude, longitude, destinationName, address } = {}) {
        const baseUrl = 'https://www.google.com/maps/dir/?api=1';

        // 1. Check coordinates first
        if (MapsNavigator.isValidCoordinate(latitude, longitude)) {
            const lat = parseFloat(latitude).toFixed(6);
            const lng = parseFloat(longitude).toFixed(6);
            return `${baseUrl}&destination=${lat},${lng}`;
        }

        // 2. Fallback to Destination Name and/or Address
        let query = '';
        if (destinationName && address) {
            query = `${destinationName} ${address}`;
        } else if (destinationName) {
            query = destinationName;
        } else if (address) {
            query = address;
        } else {
            return 'https://www.google.com/maps';
        }

        return `${baseUrl}&destination=${encodeURIComponent(query.trim())}`;
    }

    /**
     * Open Google Maps navigation in a secure new tab.
     * @param {Object} options
     */
    static openNavigation(options = {}) {
        const url = MapsNavigator.generateGoogleMapsUrl(options);
        window.open(url, '_blank', 'noopener,noreferrer');
    }

    /**
     * Attach click handlers to Google Maps buttons.
     */
    static init() {
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('.btn-google-maps');
            if (btn) {
                const lat = btn.getAttribute('data-lat');
                const lng = btn.getAttribute('data-lng');
                const destination = btn.getAttribute('data-destination');
                const address = btn.getAttribute('data-address');

                const generatedUrl = MapsNavigator.generateGoogleMapsUrl({
                    latitude: lat,
                    longitude: lng,
                    destinationName: destination,
                    address: address
                });

                // Update href in case it was modified or dynamic
                btn.setAttribute('href', generatedUrl);
            }
        });
    }
}

// Attach to window & auto-initialize
window.MapsNavigator = MapsNavigator;
document.addEventListener('DOMContentLoaded', () => {
    MapsNavigator.init();
});
