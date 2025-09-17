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

        const faceDate = this.helpers.createElement('div', {
            className: 'face-date'
        }, this.helpers.formatDate(face.detected_at || face.date || face.timestamp));

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
            modalDetectionDate.textContent = this.helpers.formatDate(
                face.detected_at || face.date || face.timestamp
            );
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
}

// Export for module systems and global use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FaceListComponent;
} else {
    // Make available globally for browser usage
    window.FaceListComponent = FaceListComponent;
}
