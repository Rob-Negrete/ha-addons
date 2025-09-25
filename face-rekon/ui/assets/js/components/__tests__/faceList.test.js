/**
 * Unit tests for FaceListComponent
 */

const FaceListComponent = require('../faceList.js');

describe('FaceListComponent', () => {
  let faceListComponent;
  let mockFaceService;
  let mockHelpers;

  beforeEach(() => {
    // Mock FaceService
    mockFaceService = {
      fetchUnclassifiedFaces: jest.fn(),
      getFace: jest.fn(),
      updateFace: jest.fn(),
      isHealthy: jest.fn()
    };

    // Mock Helpers
    mockHelpers = {
      formatDate: jest.fn().mockImplementation(date => `formatted-${date}`),
      createImageUrl: jest.fn().mockReturnValue(null),
      sanitizeHtml: jest.fn().mockImplementation(str => str),
      createElement: jest.fn().mockImplementation((tag, attrs, content) => {
        const element = document.createElement(tag);
        if (attrs) {
          Object.entries(attrs).forEach(([key, value]) => {
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
        }
        if (content) {
          if (typeof content === 'string') {
            element.innerHTML = content;
          } else if (content instanceof HTMLElement) {
            element.appendChild(content);
          }
        }
        return element;
      }),
      showElement: jest.fn(),
      hideElement: jest.fn(),
      toggleElement: jest.fn(),
      showNotification: jest.fn()
    };

    faceListComponent = new FaceListComponent(mockFaceService, mockHelpers);
  });

  describe('constructor', () => {
    it('should initialize with dependencies', () => {
      expect(faceListComponent.faceService).toBe(mockFaceService);
      expect(faceListComponent.helpers).toBe(mockHelpers);
      expect(faceListComponent.faces).toEqual([]);
      expect(faceListComponent.selectedFace).toBeNull();
      expect(faceListComponent.isLoading).toBe(false);
    });

    it('should find DOM elements', () => {
      expect(faceListComponent.faceListContainer).toBe(document.getElementById('face-list'));
      expect(faceListComponent.emptyState).toBe(document.getElementById('empty-state'));
      expect(faceListComponent.modal).toBe(document.getElementById('face-modal'));
    });
  });

  describe('render', () => {
    it('should render empty state when no faces', () => {
      faceListComponent.render([]);

      expect(faceListComponent.faces).toEqual([]);
      expect(mockHelpers.showElement).toHaveBeenCalledWith(faceListComponent.emptyState);
    });

    it('should render face cards when faces exist', () => {
      const mockFaces = createMockFaces(2);
      faceListComponent.render(mockFaces);

      expect(faceListComponent.faces).toEqual(mockFaces);
      expect(mockHelpers.hideElement).toHaveBeenCalledWith(faceListComponent.emptyState);
      expect(mockHelpers.createElement).toHaveBeenCalledTimes(12); // 2 faces × 6 elements each
    });

    it('should update face count', () => {
      const mockFaces = createMockFaces(3);
      const faceCountElement = document.getElementById('face-count');

      faceListComponent.render(mockFaces);

      expect(faceCountElement.textContent).toBe('3 faces found');
    });

    it('should handle single face count', () => {
      const mockFaces = createMockFaces(1);
      const faceCountElement = document.getElementById('face-count');

      faceListComponent.render(mockFaces);

      expect(faceCountElement.textContent).toBe('1 face found');
    });

    it('should clear existing content', () => {
      const faceListContainer = document.getElementById('face-list');
      faceListContainer.innerHTML = '<div>existing content</div>';

      faceListComponent.render([]);

      expect(faceListContainer.innerHTML).toBe('');
    });
  });

  describe('createFaceCard', () => {
    it('should create face card with correct structure', () => {
      const mockFace = createMockFace();
      const card = faceListComponent.createFaceCard(mockFace);

      expect(card.classList.contains('face-card')).toBe(true);
      expect(card.dataset.faceId).toBe(mockFace.id);
      expect(mockHelpers.createElement).toHaveBeenCalledWith('div', {
        className: 'face-card',
        dataset: { faceId: mockFace.id }
      });
    });

    it('should handle face_id fallback', () => {
      const mockFace = { ...createMockFace(), id: undefined };
      const card = faceListComponent.createFaceCard(mockFace);

      expect(card.dataset.faceId).toBe(mockFace.face_id);
    });

    it('should add click event listener', () => {
      const mockFace = createMockFace();
      jest.spyOn(faceListComponent, 'handleFaceClick').mockImplementation(() => {});

      const card = faceListComponent.createFaceCard(mockFace);
      card.click();

      expect(faceListComponent.handleFaceClick).toHaveBeenCalledWith(mockFace);
    });
  });

  describe('createFaceThumbnail', () => {
    it('should create thumbnail with placeholder when no image URL', () => {
      const mockFace = createMockFace();
      const thumbnail = faceListComponent.createFaceThumbnail(mockFace);

      expect(thumbnail.innerHTML).toBe('<div class="placeholder">👤</div>');
    });

    it('should create thumbnail with image when URL exists', () => {
      const mockFace = createMockFace();
      mockHelpers.createImageUrl.mockReturnValue('http://example.com/image.jpg');

      const thumbnail = faceListComponent.createFaceThumbnail(mockFace);

      expect(mockHelpers.createElement).toHaveBeenCalledWith('img', {
        src: 'http://example.com/image.jpg',
        alt: `Face ${mockFace.id}`,
        loading: 'lazy'
      });
    });
  });

  describe('handleFaceClick', () => {
    it('should show modal with face data', async () => {
      const mockFace = createMockFace();
      jest.spyOn(faceListComponent, 'showFaceModal').mockImplementation(() => {});

      await faceListComponent.handleFaceClick(mockFace);

      expect(faceListComponent.selectedFace).toBe(mockFace);
      expect(faceListComponent.showFaceModal).toHaveBeenCalledWith(mockFace);
    });

    it('should fetch fresh face data if available', async () => {
      const mockFace = createMockFace();
      const freshFace = { ...mockFace, name: 'Updated Name' };
      mockFaceService.getFace.mockResolvedValue(freshFace);
      jest.spyOn(faceListComponent, 'showFaceModal').mockImplementation(() => {});

      await faceListComponent.handleFaceClick(mockFace);

      expect(mockFaceService.getFace).toHaveBeenCalledWith(mockFace.id);
      expect(faceListComponent.selectedFace).toBe(freshFace);
      expect(faceListComponent.showFaceModal).toHaveBeenCalledWith(freshFace);
    });

    it('should handle errors when fetching fresh data', async () => {
      const mockFace = createMockFace();
      mockFaceService.getFace.mockRejectedValue(new Error('Fetch error'));
      jest.spyOn(faceListComponent, 'showFaceModal').mockImplementation(() => {});

      await faceListComponent.handleFaceClick(mockFace);

      expect(mockHelpers.showNotification).toHaveBeenCalledWith(
        'Error loading face details: Fetch error',
        'error'
      );
      expect(faceListComponent.showFaceModal).toHaveBeenCalledWith(mockFace);
    });
  });

  describe('showFaceModal', () => {
    it('should populate modal with face data', () => {
      const mockFace = createMockFace({
        name: 'John Doe',
        notes: 'Test notes'
      });

      faceListComponent.showFaceModal(mockFace);

      const modalFaceId = document.getElementById('modal-face-id');
      const modalDetectionDate = document.getElementById('modal-detection-date');
      const modalFaceStatus = document.getElementById('modal-face-status');
      const faceNameInput = document.getElementById('face-name');
      const faceNotesInput = document.getElementById('face-notes');

      expect(modalFaceId.textContent).toBe(mockFace.id);
      expect(modalDetectionDate.textContent).toBe(`formatted-${mockFace.detected_at}`);
      expect(modalFaceStatus.textContent).toBe(mockFace.status);
      expect(faceNameInput.value).toBe('John Doe');
      expect(faceNotesInput.value).toBe('Test notes');

      expect(mockHelpers.showElement).toHaveBeenCalledWith(faceListComponent.modal);
    });

    it('should handle missing face data', () => {
      const mockFace = createMockFace({
        name: null,
        notes: null
      });

      faceListComponent.showFaceModal(mockFace);

      const faceNameInput = document.getElementById('face-name');
      const faceNotesInput = document.getElementById('face-notes');

      expect(faceNameInput.value).toBe('');
      expect(faceNotesInput.value).toBe('');
    });
  });

  describe('closeModal', () => {
    it('should hide modal and reset state', () => {
      faceListComponent.selectedFace = createMockFace();

      faceListComponent.closeModal();

      expect(mockHelpers.hideElement).toHaveBeenCalledWith(faceListComponent.modal);
      expect(faceListComponent.selectedFace).toBeNull();
    });

    it('should reset form', () => {
      const updateForm = document.getElementById('face-update-form');
      const resetSpy = jest.spyOn(updateForm, 'reset');

      faceListComponent.closeModal();

      expect(resetSpy).toHaveBeenCalled();
    });
  });

  describe('handleFaceUpdate', () => {
    it('should update face successfully', async () => {
      const mockFace = createMockFace();
      faceListComponent.selectedFace = mockFace;

      const mockEvent = {
        preventDefault: jest.fn(),
        target: {
          elements: {
            name: { value: 'John Doe' },
            notes: { value: 'Test notes' }
          }
        }
      };

      // Mock FormData
      global.FormData = jest.fn(() => ({
        get: jest.fn()
          .mockReturnValueOnce('John Doe')
          .mockReturnValueOnce('Test notes')
      }));

      mockFaceService.updateFace.mockResolvedValue({ status: 'success' });
      jest.spyOn(faceListComponent, 'closeModal').mockImplementation(() => {});
      jest.spyOn(faceListComponent, 'refresh').mockImplementation(() => {});

      await faceListComponent.handleFaceUpdate(mockEvent);

      expect(mockEvent.preventDefault).toHaveBeenCalled();
      expect(mockFaceService.updateFace).toHaveBeenCalledWith(
        mockFace.id,
        { name: 'John Doe', notes: 'Test notes' }
      );
      expect(mockHelpers.showNotification).toHaveBeenCalledWith(
        'Face classified as "John Doe" successfully!',
        'success'
      );
      expect(faceListComponent.closeModal).toHaveBeenCalled();
      expect(faceListComponent.refresh).toHaveBeenCalled();
    });

    it('should handle update errors', async () => {
      const mockFace = createMockFace();
      faceListComponent.selectedFace = mockFace;

      const mockEvent = {
        preventDefault: jest.fn(),
        target: {}
      };

      global.FormData = jest.fn(() => ({
        get: jest.fn()
          .mockReturnValueOnce('John Doe')
          .mockReturnValueOnce('Test notes')
      }));

      mockFaceService.updateFace.mockRejectedValue(new Error('Update failed'));

      await faceListComponent.handleFaceUpdate(mockEvent);

      expect(mockHelpers.showNotification).toHaveBeenCalledWith(
        'Error updating face: Update failed',
        'error'
      );
    });

    it('should handle missing selected face', async () => {
      faceListComponent.selectedFace = null;

      const mockEvent = {
        preventDefault: jest.fn(),
        target: {}
      };

      await faceListComponent.handleFaceUpdate(mockEvent);

      expect(mockHelpers.showNotification).toHaveBeenCalledWith(
        'No face selected for update',
        'error'
      );
    });
  });

  describe('refresh', () => {
    it('should fetch and render faces', async () => {
      const mockFaces = createMockFaces(2);
      mockFaceService.fetchUnclassifiedFaces.mockResolvedValue(mockFaces);
      jest.spyOn(faceListComponent, 'render').mockImplementation(() => {});

      await faceListComponent.refresh();

      expect(mockFaceService.fetchUnclassifiedFaces).toHaveBeenCalled();
      expect(faceListComponent.render).toHaveBeenCalledWith(mockFaces);
    });

    it('should handle refresh errors', async () => {
      mockFaceService.fetchUnclassifiedFaces.mockRejectedValue(new Error('Fetch failed'));
      jest.spyOn(faceListComponent, 'showEmptyState').mockImplementation(() => {});

      await faceListComponent.refresh();

      expect(mockHelpers.showNotification).toHaveBeenCalledWith(
        'Error refreshing faces: Fetch failed',
        'error'
      );
      expect(faceListComponent.showEmptyState).toHaveBeenCalled();
    });

    it('should set loading state during refresh', async () => {
      const mockFaces = createMockFaces(1);
      mockFaceService.fetchUnclassifiedFaces.mockResolvedValue(mockFaces);
      jest.spyOn(faceListComponent, 'setLoading').mockImplementation(() => {});
      jest.spyOn(faceListComponent, 'render').mockImplementation(() => {});

      await faceListComponent.refresh();

      expect(faceListComponent.setLoading).toHaveBeenCalledWith(true);
      expect(faceListComponent.setLoading).toHaveBeenCalledWith(false);
    });
  });

  describe('setLoading', () => {
    it('should update loading state and UI', () => {
      faceListComponent.setLoading(true);

      expect(faceListComponent.isLoading).toBe(true);
      expect(mockHelpers.toggleElement).toHaveBeenCalledWith(
        faceListComponent.loadingIndicator,
        true
      );
    });

    it('should disable refresh button during loading', () => {
      const refreshBtn = document.getElementById('refresh-btn');

      faceListComponent.setLoading(true);
      expect(refreshBtn.disabled).toBe(true);

      faceListComponent.setLoading(false);
      expect(refreshBtn.disabled).toBe(false);
    });
  });

  describe('getter methods', () => {
    it('should return current faces', () => {
      const mockFaces = createMockFaces(2);
      faceListComponent.faces = mockFaces;

      expect(faceListComponent.getFaces()).toBe(mockFaces);
    });

    it('should return selected face', () => {
      const mockFace = createMockFace();
      faceListComponent.selectedFace = mockFace;

      expect(faceListComponent.getSelectedFace()).toBe(mockFace);
    });

    it('should return loading state', () => {
      faceListComponent.isLoading = true;

      expect(faceListComponent.isComponentLoading()).toBe(true);
    });
  });

  describe('event listeners', () => {
    it('should close modal on close button click', () => {
      const closeButton = document.getElementById('close-modal');
      jest.spyOn(faceListComponent, 'closeModal').mockImplementation(() => {});

      closeButton.click();

      expect(faceListComponent.closeModal).toHaveBeenCalled();
    });

    it('should close modal on cancel button click', () => {
      const cancelButton = document.getElementById('cancel-update');
      jest.spyOn(faceListComponent, 'closeModal').mockImplementation(() => {});

      cancelButton.click();

      expect(faceListComponent.closeModal).toHaveBeenCalled();
    });

    it('should handle form submission', () => {
      const updateForm = document.getElementById('face-update-form');
      jest.spyOn(faceListComponent, 'handleFaceUpdate').mockImplementation(() => {});

      const submitEvent = new Event('submit');
      updateForm.dispatchEvent(submitEvent);

      expect(faceListComponent.handleFaceUpdate).toHaveBeenCalledWith(submitEvent);
    });

    it('should close modal on escape key', () => {
      jest.spyOn(faceListComponent, 'closeModal').mockImplementation(() => {});
      faceListComponent.modal.classList.remove('hidden');

      const escapeEvent = new KeyboardEvent('keydown', { key: 'Escape' });
      document.dispatchEvent(escapeEvent);

      expect(faceListComponent.closeModal).toHaveBeenCalled();
    });

    it('should not close modal on escape when modal is hidden', () => {
      jest.spyOn(faceListComponent, 'closeModal').mockImplementation(() => {});
      faceListComponent.modal.classList.add('hidden');

      const escapeEvent = new KeyboardEvent('keydown', { key: 'Escape' });
      document.dispatchEvent(escapeEvent);

      expect(faceListComponent.closeModal).not.toHaveBeenCalled();
    });
  });

  describe('Source Snapshot Functionality', () => {

    describe('buildSnapshotUrl', () => {
      it('should build snapshot-clean.png URL correctly', () => {
        const config = {
          protocol: 'http',
          host: '192.168.1.100',
          port: 5000
        };
        const eventId = 'test-event-123';

        const result = faceListComponent.buildSnapshotUrl(eventId, config);

        expect(result).toBe('http://192.168.1.100:5000/api/events/test-event-123/snapshot-clean.png');
      });

      it('should handle HTTPS protocol', () => {
        const config = {
          protocol: 'https',
          host: 'frigate.example.com',
          port: 443
        };
        const eventId = 'secure-event-456';

        const result = faceListComponent.buildSnapshotUrl(eventId, config);

        expect(result).toBe('https://frigate.example.com:443/api/events/secure-event-456/snapshot-clean.png');
      });

      it('should handle custom port numbers', () => {
        const config = {
          protocol: 'http',
          host: 'localhost',
          port: 8080
        };
        const eventId = 'custom-port-789';

        const result = faceListComponent.buildSnapshotUrl(eventId, config);

        expect(result).toBe('http://localhost:8080/api/events/custom-port-789/snapshot-clean.png');
      });
    });

    describe('handleSourceSnapshotClick', () => {
      beforeEach(() => {
        jest.spyOn(faceListComponent, 'getFrigateConfig').mockReturnValue({
          protocol: 'http',
          host: '192.168.1.100',
          port: 5000
        });
        jest.spyOn(faceListComponent, 'buildSnapshotUrl').mockReturnValue('http://test.com/snapshot.png');
        jest.spyOn(faceListComponent, 'showSourceSnapshotModal').mockImplementation(() => {});
      });

      it('should handle valid event_id', async () => {
        const mockFace = {
          face_id: 'face-123',
          event_id: 'event-456'
        };

        await faceListComponent.handleSourceSnapshotClick(mockFace);

        expect(faceListComponent.getFrigateConfig).toHaveBeenCalled();
        expect(faceListComponent.buildSnapshotUrl).toHaveBeenCalledWith('event-456', {
          protocol: 'http',
          host: '192.168.1.100',
          port: 5000
        });
        expect(faceListComponent.showSourceSnapshotModal).toHaveBeenCalledWith(
          mockFace,
          'http://test.com/snapshot.png'
        );
      });

      it('should handle missing event_id', async () => {
        mockHelpers.showNotification = jest.fn();
        const mockFace = {
          face_id: 'face-123',
          event_id: 'unknown'
        };

        await faceListComponent.handleSourceSnapshotClick(mockFace);

        expect(mockHelpers.showNotification).toHaveBeenCalledWith('No source event available', 'error');
        expect(faceListComponent.showSourceSnapshotModal).not.toHaveBeenCalled();
      });

      it('should handle null event_id', async () => {
        mockHelpers.showNotification = jest.fn();
        const mockFace = {
          face_id: 'face-123',
          event_id: null
        };

        await faceListComponent.handleSourceSnapshotClick(mockFace);

        expect(mockHelpers.showNotification).toHaveBeenCalledWith('No source event available', 'error');
        expect(faceListComponent.showSourceSnapshotModal).not.toHaveBeenCalled();
      });

      it('should handle errors gracefully', async () => {
        mockHelpers.showNotification = jest.fn();
        jest.spyOn(faceListComponent, 'getFrigateConfig').mockImplementation(() => {
          throw new Error('Config error');
        });

        const mockFace = {
          face_id: 'face-123',
          event_id: 'event-456'
        };

        await faceListComponent.handleSourceSnapshotClick(mockFace);

        expect(mockHelpers.showNotification).toHaveBeenCalledWith('Error loading source snapshot: Config error', 'error');
        expect(faceListComponent.showSourceSnapshotModal).not.toHaveBeenCalled();
      });
    });
  });
});
