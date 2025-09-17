/**
 * Face Service - Handles all API communication with the face-rekon backend
 * Single Responsibility: Only manages API calls and data transformation
 */
class FaceService {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
        this.apiPath = '/api/face-rekon';
    }

    /**
     * Constructs the full API URL
     * @param {string} endpoint - The API endpoint path
     * @returns {string} Full URL
     */
    _buildUrl(endpoint) {
        return `${this.baseUrl}${this.apiPath}${endpoint}`;
    }

    /**
     * Makes an HTTP request with error handling
     * @param {string} url - Request URL
     * @param {object} options - Fetch options
     * @returns {Promise<object>} Response data
     * @throws {Error} If request fails
     */
    async _makeRequest(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, defaultOptions);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new Error('Network error: Unable to connect to the face recognition service');
            }
            throw error;
        }
    }

    /**
     * Fetches all unclassified faces from the API
     * @returns {Promise<Array>} Array of unclassified face objects
     * @throws {Error} If the request fails
     */
    async fetchUnclassifiedFaces() {
        const url = this._buildUrl('/');
        return await this._makeRequest(url, {
            method: 'GET'
        });
    }

    /**
     * Fetches details of a specific face by ID
     * @param {string} faceId - The unique face identifier
     * @returns {Promise<object>} Face object with details
     * @throws {Error} If the request fails or face not found
     */
    async getFace(faceId) {
        if (!faceId || typeof faceId !== 'string') {
            throw new Error('Face ID is required and must be a string');
        }

        const url = this._buildUrl(`/${encodeURIComponent(faceId)}`);
        return await this._makeRequest(url, {
            method: 'GET'
        });
    }

    /**
     * Updates face information (name, notes, etc.)
     * @param {string} faceId - The unique face identifier
     * @param {object} data - Update data containing name, notes, etc.
     * @returns {Promise<object>} Update response
     * @throws {Error} If the request fails or validation fails
     */
    async updateFace(faceId, data) {
        if (!faceId || typeof faceId !== 'string') {
            throw new Error('Face ID is required and must be a string');
        }

        if (!data || typeof data !== 'object') {
            throw new Error('Update data is required and must be an object');
        }

        if (!data.name || typeof data.name !== 'string' || data.name.trim() === '') {
            throw new Error('Name is required and must be a non-empty string');
        }

        // Clean the data
        const cleanData = {
            name: data.name.trim(),
            notes: data.notes ? data.notes.trim() : ''
        };

        const url = this._buildUrl(`/${encodeURIComponent(faceId)}`);
        return await this._makeRequest(url, {
            method: 'PATCH',
            body: JSON.stringify(cleanData)
        });
    }

    /**
     * Health check endpoint to verify service availability
     * @returns {Promise<object>} Ping response
     * @throws {Error} If the service is unavailable
     */
    async ping() {
        const url = this._buildUrl('/ping');
        return await this._makeRequest(url, {
            method: 'GET'
        });
    }

    /**
     * Validates if the face service is accessible
     * @returns {Promise<boolean>} True if service is healthy
     */
    async isHealthy() {
        try {
            const response = await this.ping();
            return response && response.pong === true;
        } catch (error) {
            console.warn('Face service health check failed:', error.message);
            return false;
        }
    }
}

// Export for module systems and global use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FaceService;
} else {
    // Make available globally for browser usage
    window.FaceService = FaceService;
}
