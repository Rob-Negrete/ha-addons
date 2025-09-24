/**
 * Utility Helper Functions
 * Small, focused functions for common operations
 */

/**
 * Formats a date string or timestamp into a human-readable format
 * @param {string|number|Date} dateInput - Date to format
 * @returns {object} Object with relative time and absolute formatted date for tooltips
 */
function formatDate(dateInput) {
    if (!dateInput) {
        return { relative: 'Unknown date', absolute: 'Unknown date' };
    }

    try {
        const date = new Date(dateInput);

        if (isNaN(date.getTime())) {
            return { relative: 'Invalid date', absolute: 'Invalid date' };
        }

        // Create absolute formatted date (YYYY-MMM-DD HH:MI format)
        const year = date.getFullYear();
        const month = date.toLocaleDateString('en-US', { month: 'short' });
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const absolute = `${year}-${month}-${day} ${hours}:${minutes}`;

        const now = Date.now();
        const diffMs = now - date.getTime();
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffMinutes = Math.floor(diffMs / (1000 * 60));

        let relative;

        // Relative time for recent dates
        if (diffMinutes < 1) {
            relative = 'Just now';
        } else if (diffMinutes < 60) {
            relative = `${diffMinutes} minute${diffMinutes !== 1 ? 's' : ''} ago`;
        } else if (diffHours < 24) {
            relative = `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
        } else if (diffDays < 7) {
            relative = `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
        } else {
            // For older dates, use the absolute format as relative too
            relative = absolute;
        }

        return { relative, absolute };
    } catch (error) {
        console.error('Error formatting date:', error);
        return { relative: 'Invalid date', absolute: 'Invalid date' };
    }
}

/**
 * Creates a URL for face image thumbnails
 * @param {string} faceId - The face identifier
 * @param {string} baseUrl - Base URL for the service
 * @returns {string} Image URL or null if no faceId
 */
function createImageUrl(faceId, baseUrl = '') {
    if (!faceId) {
        return null;
    }

    // Return URL to the new image serving endpoint
    return `${baseUrl}/images/${encodeURIComponent(faceId)}`;
}

/**
 * Truncates text to a specified length with ellipsis
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text
 */
function truncateText(text, maxLength = 50) {
    if (!text || typeof text !== 'string') {
        return '';
    }

    if (text.length <= maxLength) {
        return text;
    }

    return text.substring(0, maxLength - 3) + '...';
}

/**
 * Sanitizes HTML to prevent XSS attacks
 * @param {string} str - String to sanitize
 * @returns {string} Sanitized string
 */
function sanitizeHtml(str) {
    if (!str || typeof str !== 'string') {
        return '';
    }

    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/**
 * Validates if a string is a valid face ID format
 * @param {string} faceId - Face ID to validate
 * @returns {boolean} True if valid
 */
function isValidFaceId(faceId) {
    if (!faceId || typeof faceId !== 'string') {
        return false;
    }

    // Basic validation - can be enhanced based on actual ID format
    return faceId.trim().length > 0 && faceId.trim().length <= 100;
}

/**
 * Debounces function calls to limit execution frequency
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Shows an element by removing the 'hidden' class
 * @param {HTMLElement|string} element - Element or selector
 */
function showElement(element) {
    const el = typeof element === 'string' ? document.querySelector(element) : element;
    if (el) {
        el.classList.remove('hidden');
    }
}

/**
 * Hides an element by adding the 'hidden' class
 * @param {HTMLElement|string} element - Element or selector
 */
function hideElement(element) {
    const el = typeof element === 'string' ? document.querySelector(element) : element;
    if (el) {
        el.classList.add('hidden');
    }
}

/**
 * Toggles element visibility
 * @param {HTMLElement|string} element - Element or selector
 * @param {boolean} show - Force show (true) or hide (false), auto-toggle if undefined
 */
function toggleElement(element, show) {
    const el = typeof element === 'string' ? document.querySelector(element) : element;
    if (!el) return;

    if (show === undefined) {
        el.classList.toggle('hidden');
    } else if (show) {
        showElement(el);
    } else {
        hideElement(el);
    }
}

/**
 * Creates a DOM element with attributes and content
 * @param {string} tag - HTML tag name
 * @param {object} attributes - Element attributes
 * @param {string|HTMLElement|Array} content - Element content
 * @returns {HTMLElement} Created element
 */
function createElement(tag, attributes = {}, content = '') {
    const element = document.createElement(tag);

    // Set attributes
    Object.entries(attributes).forEach(([key, value]) => {
        if (key === 'className') {
            element.className = value;
        } else if (key === 'dataset') {
            Object.entries(value).forEach(([dataKey, dataValue]) => {
                element.dataset[dataKey] = dataValue;
            });
        } else {
            element.setAttribute(key, value);
        }
    });

    // Set content
    if (typeof content === 'string') {
        element.innerHTML = content;
    } else if (content instanceof HTMLElement) {
        element.appendChild(content);
    } else if (Array.isArray(content)) {
        content.forEach(item => {
            if (typeof item === 'string') {
                element.insertAdjacentHTML('beforeend', item);
            } else if (item instanceof HTMLElement) {
                element.appendChild(item);
            }
        });
    }

    return element;
}

/**
 * Displays a notification message
 * @param {string} message - Message to display
 * @param {string} type - Type of message ('error', 'success', 'info')
 * @param {number} duration - Auto-hide duration in ms (0 = no auto-hide)
 */
function showNotification(message, type = 'info', duration = 5000) {
    const containers = {
        error: document.getElementById('error-message'),
        success: document.getElementById('success-message'),
        info: document.getElementById('status-container')
    };

    const container = containers[type];
    if (!container) {
        console.warn(`Unknown notification type: ${type}`);
        return;
    }

    // Hide other notifications
    Object.values(containers).forEach(c => c && hideElement(c));

    container.textContent = message;
    showElement(container);

    if (duration > 0) {
        setTimeout(() => hideElement(container), duration);
    }
}

/**
 * Handles async operations with loading states
 * @param {Function} asyncFn - Async function to execute
 * @param {HTMLElement|string} loadingElement - Loading indicator element
 * @returns {Promise} Result of the async function
 */
async function withLoading(asyncFn, loadingElement) {
    const loader = typeof loadingElement === 'string'
        ? document.querySelector(loadingElement)
        : loadingElement;

    try {
        if (loader) showElement(loader);
        return await asyncFn();
    } finally {
        if (loader) hideElement(loader);
    }
}

// Export for module systems and global use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatDate,
        createImageUrl,
        truncateText,
        sanitizeHtml,
        isValidFaceId,
        debounce,
        showElement,
        hideElement,
        toggleElement,
        createElement,
        showNotification,
        withLoading
    };
} else {
    // Make available globally for browser usage
    window.FaceHelpers = {
        formatDate,
        createImageUrl,
        truncateText,
        sanitizeHtml,
        isValidFaceId,
        debounce,
        showElement,
        hideElement,
        toggleElement,
        createElement,
        showNotification,
        withLoading
    };
}
