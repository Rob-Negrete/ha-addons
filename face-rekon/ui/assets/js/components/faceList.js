/**
 * Face List Component - Handles face list UI rendering and interactions
 * Single Responsibility: Only manages the face list display and user interactions
 * Dependency Injection: Accepts faceService and helpers as parameters
 */
class FaceListComponent {
    constructor(faceService, helpers) {
        this.faceService = faceService;
        this.helpers = helpers;
        this.faces = [];
        this.selectedFace = null;
        this.isLoading = false;

        // DOM elements
        this.faceListContainer = document.getElementById('face-list');
        this.emptyState = document.getElementById('empty-state');
        this.faceCountElement = document.getElementById('face-count');
        this.loadingIndicator = document.getElementById('loading-indicator');
        this.modal = document.getElementById('face-modal');

        this.initializeEventListeners();
    }

    /**
     * Initialize event listeners for the component
     */
    initializeEventListeners() {
        // Modal close events
        const closeModal = document.getElementById('close-modal');
        if (closeModal) {
            closeModal.addEventListener('click', () => this.closeModal());
        }

        // Click outside modal to close
        if (this.modal) {
            this.modal.addEventListener('click', (e) => {
                if (e.target === this.modal) {
                    this.closeModal();
                }
            });
        }

        // Face update form
        const updateForm = document.getElementById('face-update-form');
        if (updateForm) {
            updateForm.addEventListener('submit', (e) => this.handleFaceUpdate(e));
        }

        // Cancel update button
        const cancelUpdate = document.getElementById('cancel-update');
        if (cancelUpdate) {
            cancelUpdate.addEventListener('click', () => this.closeModal());
        }

        // Escape key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !this.modal.classList.contains('hidden')) {
                this.closeModal();
            }
        });
    }

    /**
     * Renders the face list UI
     * @param {Array} faces - Array of face objects to render
     */
    render(faces = []) {
        this.faces = faces;

        if (!this.faceListContainer) {
            console.error('Face list container not found');
            return;
        }

        // Update face count
        this.updateFaceCount(faces.length);

        // Clear existing content
        this.faceListContainer.innerHTML = '';

        if (faces.length === 0) {
            this.showEmptyState();
            return;
        }

        this.hideEmptyState();

        // Render face cards
        faces.forEach(face => {
            const faceCard = this.createFaceCard(face);
            this.faceListContainer.appendChild(faceCard);
        });
    }

    /**
     * Creates a face card element
     * @param {object} face - Face object
     * @returns {HTMLElement} Face card element
     */
    createFaceCard(face) {
        const cardElement = this.helpers.createElement('div', {
            className: 'face-card',
            dataset: { faceId: face.id || face.face_id }
        });

        // Create thumbnail
        const thumbnail = this.createFaceThumbnail(face);

        // Create info section
        const info = this.helpers.createElement('div', { className: 'face-info' });

        const faceId = this.helpers.createElement('div', {
            className: 'face-id'
        }, `ID: ${this.helpers.sanitizeHtml(face.id || face.face_id || 'Unknown')}`);

        // Format date with tooltip support
        const dateInfo = this.helpers.formatDate(face.detected_at || face.date || face.timestamp);
        const faceDate = this.helpers.createElement('div', {
            className: 'face-date',
            title: dateInfo.absolute // Add tooltip with absolute time
        }, dateInfo.relative);

        const faceStatus = this.helpers.createElement('span', {
            className: 'face-status'
        }, this.helpers.sanitizeHtml(face.status || 'Unclassified'));

        info.appendChild(faceId);
        info.appendChild(faceDate);
        info.appendChild(faceStatus);

        cardElement.appendChild(thumbnail);
        cardElement.appendChild(info);

        // Add click handler
        cardElement.addEventListener('click', () => this.handleFaceClick(face));

        return cardElement;
    }

    /**
     * Creates a face thumbnail element
     * @param {object} face - Face object
     * @returns {HTMLElement} Thumbnail element
     */
    createFaceThumbnail(face) {
        const thumbnail = this.helpers.createElement('div', {
            className: 'face-thumbnail'
        });

        const imageUrl = this.helpers.createImageUrl(face.id || face.face_id);

        if (imageUrl) {
            const img = this.helpers.createElement('img', {
                src: imageUrl,
                alt: `Face ${face.id || face.face_id}`,
                loading: 'lazy'
            });

            img.addEventListener('error', () => {
                // Fallback to placeholder if image fails to load
                thumbnail.innerHTML = '<div class="placeholder">👤</div>';
            });

            thumbnail.appendChild(img);
        } else {
            // No image available, show placeholder
            thumbnail.innerHTML = '<div class="placeholder">👤</div>';
        }

        // Add source snapshot overlay icon if event_id is available
        if (face.event_id && face.event_id !== 'unknown') {
            const overlay = this.helpers.createElement('div', {
                className: 'source-overlay',
                title: 'View source snapshot'
            });

            // Create camera icon SVG
            overlay.innerHTML = `
                <svg viewBox="0 0 24 24">
                    <path d="M12 7a5 5 0 0 1 5 5 5 5 0 0 1-5 5 5 5 0 0 1-5-5 5 5 0 0 1 5-5m0 2a3 3 0 0 0-3 3 3 3 0 0 0 3 3 3 3 0 0 0 3-3 3 3 0 0 0-3-3zm0-7l2.09 0.75L16.17 1l1.83 1.83L18.25 2.91L19 5H21v2h-2.75l-0.75 2.09L16.17 11l-1.83-1.83L14.09 9.25L12 8.5l-2.09 0.75L8.83 11L7 9.17L7.25 7.91L6.5 5.75L5 5V3h2l0.75-2.09L9.83 1l1.83 1.83L12 2z"/>
                </svg>
            `;

            overlay.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent card click
                this.handleSourceSnapshotClick(face);
            });

            thumbnail.appendChild(overlay);
        }

        return thumbnail;
    }

    /**
     * Handles face card click events
     * @param {object} face - Clicked face object
     */
    async handleFaceClick(face) {
        try {
            this.selectedFace = face;

            // Try to get fresh face data
            const freshFace = await this.faceService.getFace(face.id || face.face_id);
            if (freshFace) {
                this.selectedFace = freshFace;
            }

            this.showFaceModal(this.selectedFace);
        } catch (error) {
            console.error('Error loading face details:', error);
            this.helpers.showNotification(`Error loading face details: ${error.message}`, 'error');
            // Still show modal with available data
            this.showFaceModal(face);
        }
    }

    /**
     * Shows the face details modal
     * @param {object} face - Face object to display
     */
    showFaceModal(face) {
        if (!this.modal) {
            console.error('Modal element not found');
            return;
        }

        // Update modal content
        const modalFaceId = document.getElementById('modal-face-id');
        const modalDetectionDate = document.getElementById('modal-detection-date');
        const modalFaceStatus = document.getElementById('modal-face-status');
        const modalFaceImage = document.getElementById('modal-face-image');
        const faceNameInput = document.getElementById('face-name');
        const faceNotesInput = document.getElementById('face-notes');

        if (modalFaceId) {
            modalFaceId.textContent = face.id || face.face_id || 'Unknown';
        }

        if (modalDetectionDate) {
            const dateInfo = this.helpers.formatDate(face.detected_at || face.date || face.timestamp);
            modalDetectionDate.textContent = dateInfo.relative;
            modalDetectionDate.title = dateInfo.absolute; // Add tooltip to modal date too
        }

        if (modalFaceStatus) {
            modalFaceStatus.textContent = face.status || 'Unclassified';
        }

        if (modalFaceImage) {
            const imageUrl = this.helpers.createImageUrl(face.id || face.face_id);
            if (imageUrl) {
                modalFaceImage.innerHTML = `<img src="${imageUrl}" alt="Face ${face.id || face.face_id}" />`;
            } else {
                modalFaceImage.innerHTML = '<div class="placeholder">👤</div>';
            }
        }

        // Pre-fill form if face already has data
        if (faceNameInput) {
            faceNameInput.value = face.name || '';
        }

        if (faceNotesInput) {
            faceNotesInput.value = face.notes || '';
        }

        // Show modal
        this.helpers.showElement(this.modal);

        // Focus on name input for better UX
        if (faceNameInput) {
            setTimeout(() => faceNameInput.focus(), 100);
        }
    }

    /**
     * Closes the face details modal
     */
    closeModal() {
        this.helpers.hideElement(this.modal);
        this.selectedFace = null;

        // Reset form
        const updateForm = document.getElementById('face-update-form');
        if (updateForm) {
            updateForm.reset();
        }
    }

    /**
     * Handles face update form submission
     * @param {Event} e - Form submit event
     */
    async handleFaceUpdate(e) {
        e.preventDefault();

        if (!this.selectedFace) {
            this.helpers.showNotification('No face selected for update', 'error');
            return;
        }

        const formData = new FormData(e.target);
        const updateData = {
            name: formData.get('name'),
            notes: formData.get('notes')
        };

        const saveButton = document.getElementById('save-update');
        const originalText = saveButton.textContent;

        try {
            // Show loading state
            saveButton.disabled = true;
            saveButton.textContent = 'Saving...';

            await this.faceService.updateFace(
                this.selectedFace.id || this.selectedFace.face_id,
                updateData
            );

            this.helpers.showNotification(
                `Face classified as "${updateData.name}" successfully!`,
                'success'
            );

            this.closeModal();

            // Trigger refresh of the face list
            this.refresh();

        } catch (error) {
            console.error('Error updating face:', error);
            this.helpers.showNotification(`Error updating face: ${error.message}`, 'error');
        } finally {
            // Reset button state
            saveButton.disabled = false;
            saveButton.textContent = originalText;
        }
    }

    /**
     * Refreshes the face list by fetching fresh data
     */
    async refresh() {
        try {
            this.setLoading(true);
            const faces = await this.faceService.fetchUnclassifiedFaces();
            this.render(faces);
        } catch (error) {
            console.error('Error refreshing face list:', error);
            this.helpers.showNotification(`Error refreshing faces: ${error.message}`, 'error');
            this.showEmptyState();
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * Sets the loading state
     * @param {boolean} loading - Whether component is loading
     */
    setLoading(loading) {
        this.isLoading = loading;

        if (this.loadingIndicator) {
            this.helpers.toggleElement(this.loadingIndicator, loading);
        }

        // Disable refresh button during loading
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.disabled = loading;
        }
    }

    /**
     * Shows the empty state
     */
    showEmptyState() {
        this.helpers.showElement(this.emptyState);
    }

    /**
     * Hides the empty state
     */
    hideEmptyState() {
        this.helpers.hideElement(this.emptyState);
    }

    /**
     * Updates the face count display
     * @param {number} count - Number of faces
     */
    updateFaceCount(count) {
        if (this.faceCountElement) {
            const text = count === 1 ? '1 face found' : `${count} faces found`;
            this.faceCountElement.textContent = text;
        }
    }

    /**
     * Gets the current faces array
     * @returns {Array} Current faces
     */
    getFaces() {
        return this.faces;
    }

    /**
     * Gets the currently selected face
     * @returns {object|null} Selected face or null
     */
    getSelectedFace() {
        return this.selectedFace;
    }

    /**
     * Checks if the component is currently loading
     * @returns {boolean} Loading state
     */
    isComponentLoading() {
        return this.isLoading;
    }

    /**
     * Handles source snapshot overlay click
     * @param {object} face - Face object with event_id
     */
    async handleSourceSnapshotClick(face) {
        console.log('Source snapshot clicked for face:', face.face_id);

        if (!face.event_id || face.event_id === 'unknown') {
            this.helpers.showNotification('No source event available', 'error');
            return;
        }

        try {
            // Get Frigate server configuration from localStorage or use defaults
            const frigateConfig = this.getFrigateConfig();
            const snapshotUrl = this.buildSnapshotUrl(face.event_id, frigateConfig);

            // Show source snapshot modal
            this.showSourceSnapshotModal(face, snapshotUrl);
        } catch (error) {
            console.error('Error opening source snapshot:', error);
            this.helpers.showNotification(`Error loading source snapshot: ${error.message}`, 'error');
        }
    }

    /**
     * Gets Frigate server configuration from localStorage or defaults
     * @returns {object} Frigate configuration
     */
    getFrigateConfig() {
        const defaultConfig = {
            host: '192.168.3.124',
            port: 5000,
            protocol: 'http'
        };

        try {
            const stored = localStorage.getItem('frigateConfig');
            return stored ? { ...defaultConfig, ...JSON.parse(stored) } : defaultConfig;
        } catch (error) {
            console.warn('Error loading Frigate config, using defaults:', error);
            return defaultConfig;
        }
    }

    /**
     * Builds the Frigate snapshot URL for an event
     * @param {string} eventId - Event identifier
     * @param {object} config - Frigate configuration
     * @returns {string} Snapshot URL
     */
    buildSnapshotUrl(eventId, config) {
        // Use high-quality snapshot-clean.png instead of thumbnail.jpg
        // This provides the original full-resolution image before cropping
        return `${config.protocol}://${config.host}:${config.port}/api/events/${eventId}/snapshot-clean.png`;
    }

    /**
     * Shows the source snapshot modal
     * @param {object} face - Face object
     * @param {string} snapshotUrl - URL to the source snapshot
     */
    showSourceSnapshotModal(face, snapshotUrl) {
        const modal = this.helpers.createElement('div', {
            className: 'modal source-snapshot-modal'
        });

        const modalContent = this.helpers.createElement('div', {
            className: 'modal-content'
        });

        const header = this.helpers.createElement('div', {
            className: 'modal-header'
        });

        const title = this.helpers.createElement('h2', {}, 'Source Snapshot');
        const closeBtn = this.helpers.createElement('button', {
            className: 'close-btn'
        }, '×');

        closeBtn.addEventListener('click', () => this.closeSourceSnapshotModal(modal));

        header.appendChild(title);
        header.appendChild(closeBtn);

        const body = this.helpers.createElement('div', {
            className: 'modal-body'
        });

        const img = this.helpers.createElement('img', {
            className: 'source-snapshot-image',
            src: snapshotUrl,
            alt: `Source snapshot for event ${face.event_id}`,
            loading: 'lazy'
        });

        img.addEventListener('error', () => {
            // Try fallback to thumbnail.jpg if snapshot-clean.png fails
            const fallbackUrl = snapshotUrl.replace('snapshot-clean.png', 'thumbnail.jpg');
            if (img.src !== fallbackUrl) {
                console.log('snapshot-clean.png failed, trying fallback to thumbnail.jpg');
                img.src = fallbackUrl;
            } else {
                // Both attempts failed
                img.style.display = 'none';
                const errorMsg = this.helpers.createElement('div', {
                    style: 'text-align: center; padding: 40px; color: #718096;'
                }, '❌ Unable to load source snapshot<br><small>Check Frigate server connection and settings</small>');
                body.appendChild(errorMsg);
            }
        });

        const info = this.helpers.createElement('div', {
            className: 'source-snapshot-info'
        });

        const eventInfo = this.helpers.createElement('div', {}, `
            <strong>Event ID:</strong><br>
            ${this.helpers.sanitizeHtml(face.event_id)}
        `);

        const faceInfo = this.helpers.createElement('div', {}, `
            <strong>Face ID:</strong><br>
            ${this.helpers.sanitizeHtml(face.face_id || face.id)}
        `);

        const dateInfo = this.helpers.createElement('div', {}, `
            <strong>Detected:</strong><br>
            ${this.helpers.formatDate(face.timestamp || face.detected_at).absolute}
        `);

        const configBtn = this.helpers.createElement('button', {
            className: 'btn btn-secondary',
            style: 'margin-top: 10px;'
        }, '⚙️ Configure Frigate');

        configBtn.addEventListener('click', () => this.showFrigateConfigModal());

        info.appendChild(eventInfo);
        info.appendChild(faceInfo);
        info.appendChild(dateInfo);
        info.appendChild(configBtn);

        body.appendChild(img);
        body.appendChild(info);

        modalContent.appendChild(header);
        modalContent.appendChild(body);
        modal.appendChild(modalContent);

        // Close on backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeSourceSnapshotModal(modal);
            }
        });

        // Close on Escape key
        const keyHandler = (e) => {
            if (e.key === 'Escape') {
                this.closeSourceSnapshotModal(modal);
                document.removeEventListener('keydown', keyHandler);
            }
        };
        document.addEventListener('keydown', keyHandler);

        document.body.appendChild(modal);
        modal.classList.remove('hidden');
    }

    /**
     * Closes the source snapshot modal
     * @param {HTMLElement} modal - Modal element
     */
    closeSourceSnapshotModal(modal) {
        modal.classList.add('hidden');
        setTimeout(() => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        }, 300);
    }

    /**
     * Shows the Frigate configuration modal
     */
    showFrigateConfigModal() {
        const config = this.getFrigateConfig();

        const modal = this.helpers.createElement('div', {
            className: 'modal'
        });

        const modalContent = this.helpers.createElement('div', {
            className: 'modal-content'
        });

        const header = this.helpers.createElement('div', {
            className: 'modal-header'
        });

        const title = this.helpers.createElement('h2', {}, 'Frigate Server Configuration');
        const closeBtn = this.helpers.createElement('button', {
            className: 'close-btn'
        }, '×');

        closeBtn.addEventListener('click', () => this.closeSourceSnapshotModal(modal));

        header.appendChild(title);
        header.appendChild(closeBtn);

        const body = this.helpers.createElement('div', {
            className: 'modal-body'
        });

        const form = this.helpers.createElement('form', {
            id: 'frigate-config-form'
        });

        const protocolGroup = this.helpers.createElement('div', { className: 'form-group' });
        protocolGroup.innerHTML = `
            <label for="protocol">Protocol:</label>
            <select id="protocol" name="protocol">
                <option value="http" ${config.protocol === 'http' ? 'selected' : ''}>HTTP</option>
                <option value="https" ${config.protocol === 'https' ? 'selected' : ''}>HTTPS</option>
            </select>
        `;

        const hostGroup = this.helpers.createElement('div', { className: 'form-group' });
        hostGroup.innerHTML = `
            <label for="host">Host/IP Address:</label>
            <input type="text" id="host" name="host" value="${this.helpers.sanitizeHtml(config.host)}" placeholder="192.168.1.100" required>
        `;

        const portGroup = this.helpers.createElement('div', { className: 'form-group' });
        portGroup.innerHTML = `
            <label for="port">Port:</label>
            <input type="number" id="port" name="port" value="${config.port}" placeholder="5000" required min="1" max="65535">
        `;

        const actions = this.helpers.createElement('div', {
            className: 'form-actions'
        });

        const saveBtn = this.helpers.createElement('button', {
            className: 'btn btn-primary',
            type: 'submit'
        }, 'Save Configuration');

        const cancelBtn = this.helpers.createElement('button', {
            className: 'btn btn-secondary',
            type: 'button'
        }, 'Cancel');

        cancelBtn.addEventListener('click', () => this.closeSourceSnapshotModal(modal));

        actions.appendChild(cancelBtn);
        actions.appendChild(saveBtn);

        form.appendChild(protocolGroup);
        form.appendChild(hostGroup);
        form.appendChild(portGroup);
        form.appendChild(actions);

        form.addEventListener('submit', (e) => this.handleFrigateConfigSave(e, modal));

        body.appendChild(form);
        modalContent.appendChild(header);
        modalContent.appendChild(body);
        modal.appendChild(modalContent);

        // Close on backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeSourceSnapshotModal(modal);
            }
        });

        document.body.appendChild(modal);
        modal.classList.remove('hidden');
    }

    /**
     * Handles Frigate configuration form save
     * @param {Event} e - Form submit event
     * @param {HTMLElement} modal - Configuration modal
     */
    handleFrigateConfigSave(e, modal) {
        e.preventDefault();

        const formData = new FormData(e.target);
        const config = {
            protocol: formData.get('protocol'),
            host: formData.get('host'),
            port: parseInt(formData.get('port'))
        };

        try {
            localStorage.setItem('frigateConfig', JSON.stringify(config));
            this.helpers.showNotification('Frigate configuration saved successfully!', 'success');
            this.closeSourceSnapshotModal(modal);
        } catch (error) {
            console.error('Error saving Frigate config:', error);
            this.helpers.showNotification(`Error saving configuration: ${error.message}`, 'error');
        }
    }
}

// Export for module systems and global use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FaceListComponent;
} else {
    // Make available globally for browser usage
    window.FaceListComponent = FaceListComponent;
}
