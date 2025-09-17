/**
 * Unit tests for Helper Functions
 */

const helpers = require('../helpers.js');

describe('Helper Functions', () => {
  describe('formatDate', () => {
    beforeEach(() => {
      // Mock Date.now() to return a consistent time for testing
      jest.spyOn(Date, 'now').mockReturnValue(new Date('2023-01-01T12:00:00Z').getTime());
    });

    afterEach(() => {
      Date.now.mockRestore();
    });

    it('should format recent dates as relative time', () => {
      const fiveMinutesAgo = new Date('2023-01-01T11:55:00Z').toISOString();
      expect(helpers.formatDate(fiveMinutesAgo)).toBe('5 minutes ago');

      const oneMinuteAgo = new Date('2023-01-01T11:59:00Z').toISOString();
      expect(helpers.formatDate(oneMinuteAgo)).toBe('1 minute ago');

      const twoHoursAgo = new Date('2023-01-01T10:00:00Z').toISOString();
      expect(helpers.formatDate(twoHoursAgo)).toBe('2 hours ago');

      const threeDaysAgo = new Date('2022-12-29T12:00:00Z').toISOString();
      expect(helpers.formatDate(threeDaysAgo)).toBe('3 days ago');
    });

    it('should return "Just now" for very recent dates', () => {
      const now = new Date('2023-01-01T12:00:00Z').toISOString();
      expect(helpers.formatDate(now)).toBe('Just now');

      const thirtySecondsAgo = new Date('2023-01-01T11:59:30Z').toISOString();
      expect(helpers.formatDate(thirtySecondsAgo)).toBe('Just now');
    });

    it('should format older dates as absolute dates', () => {
      const twoWeeksAgo = new Date('2022-12-18T12:00:00Z').toISOString();
      const result = helpers.formatDate(twoWeeksAgo);
      expect(result).toMatch(/Dec 18, 2022/);
    });

    it('should handle invalid dates', () => {
      expect(helpers.formatDate('invalid-date')).toBe('Invalid date');
      expect(helpers.formatDate(null)).toBe('Unknown date');
      expect(helpers.formatDate(undefined)).toBe('Unknown date');
      expect(helpers.formatDate('')).toBe('Unknown date');
    });

    it('should handle Date objects', () => {
      const date = new Date('2023-01-01T11:55:00Z');
      expect(helpers.formatDate(date)).toBe('5 minutes ago');
    });

    it('should handle timestamps', () => {
      const timestamp = new Date('2023-01-01T11:55:00Z').getTime();
      expect(helpers.formatDate(timestamp)).toBe('5 minutes ago');
    });
  });

  describe('createImageUrl', () => {
    it('should return null for missing face ID', () => {
      expect(helpers.createImageUrl(null)).toBeNull();
      expect(helpers.createImageUrl(undefined)).toBeNull();
      expect(helpers.createImageUrl('')).toBeNull();
    });

    it('should return proper URL for valid face ID', () => {
      // Test that the function now returns proper image URLs
      expect(helpers.createImageUrl('test-face-123')).toBe('/images/test-face-123');
      expect(helpers.createImageUrl('another-id', 'http://localhost:5001')).toBe('http://localhost:5001/images/another-id');
    });

    it('should encode face ID in URL', () => {
      // Test URL encoding for special characters
      const faceIdWithSpecialChars = 'face-id with spaces';
      const result = helpers.createImageUrl(faceIdWithSpecialChars);
      expect(result).toBe('/images/face-id%20with%20spaces');
    });
  });

  describe('truncateText', () => {
    it('should truncate text longer than maxLength', () => {
      const longText = 'This is a very long text that should be truncated';
      expect(helpers.truncateText(longText, 20)).toBe('This is a very lo...');
    });

    it('should not truncate text shorter than maxLength', () => {
      const shortText = 'Short text';
      expect(helpers.truncateText(shortText, 20)).toBe('Short text');
    });

    it('should handle empty or null text', () => {
      expect(helpers.truncateText(null)).toBe('');
      expect(helpers.truncateText(undefined)).toBe('');
      expect(helpers.truncateText('')).toBe('');
    });

    it('should handle non-string input', () => {
      expect(helpers.truncateText(123)).toBe('');
      expect(helpers.truncateText({})).toBe('');
    });

    it('should use default maxLength of 50', () => {
      const text = 'A'.repeat(60);
      expect(helpers.truncateText(text)).toBe('A'.repeat(47) + '...');
    });
  });

  describe('sanitizeHtml', () => {
    it('should escape HTML special characters', () => {
      expect(helpers.sanitizeHtml('<script>alert("xss")</script>'))
        .toBe('&lt;script&gt;alert("xss")&lt;/script&gt;');

      expect(helpers.sanitizeHtml('Hello & goodbye'))
        .toBe('Hello &amp; goodbye');

      expect(helpers.sanitizeHtml('"quoted text"'))
        .toBe('"quoted text"');
    });

    it('should handle empty or null input', () => {
      expect(helpers.sanitizeHtml(null)).toBe('');
      expect(helpers.sanitizeHtml(undefined)).toBe('');
      expect(helpers.sanitizeHtml('')).toBe('');
    });

    it('should handle non-string input', () => {
      expect(helpers.sanitizeHtml(123)).toBe('');
      expect(helpers.sanitizeHtml({})).toBe('');
    });

    it('should preserve safe text', () => {
      expect(helpers.sanitizeHtml('Safe text without HTML')).toBe('Safe text without HTML');
    });
  });

  describe('isValidFaceId', () => {
    it('should validate correct face IDs', () => {
      expect(helpers.isValidFaceId('test-face-123')).toBe(true);
      expect(helpers.isValidFaceId('a')).toBe(true);
      expect(helpers.isValidFaceId('face_id_with_underscores')).toBe(true);
    });

    it('should reject invalid face IDs', () => {
      expect(helpers.isValidFaceId(null)).toBe(false);
      expect(helpers.isValidFaceId(undefined)).toBe(false);
      expect(helpers.isValidFaceId('')).toBe(false);
      expect(helpers.isValidFaceId('   ')).toBe(false);
      expect(helpers.isValidFaceId(123)).toBe(false);
      expect(helpers.isValidFaceId({})).toBe(false);
    });

    it('should reject very long face IDs', () => {
      const longId = 'a'.repeat(101);
      expect(helpers.isValidFaceId(longId)).toBe(false);
    });
  });

  describe('debounce', () => {
    jest.useFakeTimers();

    it('should debounce function calls', () => {
      const mockFn = jest.fn();
      const debouncedFn = helpers.debounce(mockFn, 100);

      debouncedFn('arg1');
      debouncedFn('arg2');
      debouncedFn('arg3');

      expect(mockFn).not.toHaveBeenCalled();

      jest.advanceTimersByTime(100);

      expect(mockFn).toHaveBeenCalledTimes(1);
      expect(mockFn).toHaveBeenCalledWith('arg3');
    });

    it('should reset timer on subsequent calls', () => {
      const mockFn = jest.fn();
      const debouncedFn = helpers.debounce(mockFn, 100);

      debouncedFn('arg1');
      jest.advanceTimersByTime(50);
      debouncedFn('arg2');
      jest.advanceTimersByTime(50);

      expect(mockFn).not.toHaveBeenCalled();

      jest.advanceTimersByTime(50);

      expect(mockFn).toHaveBeenCalledTimes(1);
      expect(mockFn).toHaveBeenCalledWith('arg2');
    });
  });

  describe('DOM manipulation functions', () => {
    let testElement;

    beforeEach(() => {
      testElement = document.createElement('div');
      testElement.id = 'test-element';
      testElement.classList.add('hidden');
      document.body.appendChild(testElement);
    });

    afterEach(() => {
      document.body.removeChild(testElement);
    });

    describe('showElement', () => {
      it('should remove hidden class from element', () => {
        helpers.showElement(testElement);
        expect(testElement.classList.contains('hidden')).toBe(false);
      });

      it('should work with selector string', () => {
        helpers.showElement('#test-element');
        expect(testElement.classList.contains('hidden')).toBe(false);
      });

      it('should handle non-existent elements', () => {
        expect(() => helpers.showElement('#non-existent')).not.toThrow();
      });
    });

    describe('hideElement', () => {
      beforeEach(() => {
        testElement.classList.remove('hidden');
      });

      it('should add hidden class to element', () => {
        helpers.hideElement(testElement);
        expect(testElement.classList.contains('hidden')).toBe(true);
      });

      it('should work with selector string', () => {
        helpers.hideElement('#test-element');
        expect(testElement.classList.contains('hidden')).toBe(true);
      });
    });

    describe('toggleElement', () => {
      it('should toggle hidden class', () => {
        expect(testElement.classList.contains('hidden')).toBe(true);
        helpers.toggleElement(testElement);
        expect(testElement.classList.contains('hidden')).toBe(false);
        helpers.toggleElement(testElement);
        expect(testElement.classList.contains('hidden')).toBe(true);
      });

      it('should force show when show=true', () => {
        helpers.toggleElement(testElement, true);
        expect(testElement.classList.contains('hidden')).toBe(false);
      });

      it('should force hide when show=false', () => {
        testElement.classList.remove('hidden');
        helpers.toggleElement(testElement, false);
        expect(testElement.classList.contains('hidden')).toBe(true);
      });
    });
  });

  describe('createElement', () => {
    it('should create element with tag name', () => {
      const element = helpers.createElement('div');
      expect(element.tagName).toBe('DIV');
    });

    it('should set attributes', () => {
      const element = helpers.createElement('div', {
        id: 'test-id',
        'data-value': '123'
      });
      expect(element.id).toBe('test-id');
      expect(element.getAttribute('data-value')).toBe('123');
    });

    it('should set className', () => {
      const element = helpers.createElement('div', {
        className: 'test-class another-class'
      });
      expect(element.className).toBe('test-class another-class');
    });

    it('should set dataset', () => {
      const element = helpers.createElement('div', {
        dataset: {
          faceId: '123',
          status: 'active'
        }
      });
      expect(element.dataset.faceId).toBe('123');
      expect(element.dataset.status).toBe('active');
    });

    it('should set string content', () => {
      const element = helpers.createElement('div', {}, 'Hello World');
      expect(element.innerHTML).toBe('Hello World');
    });

    it('should append element content', () => {
      const child = document.createElement('span');
      const element = helpers.createElement('div', {}, child);
      expect(element.children).toHaveLength(1);
      expect(element.children[0]).toBe(child);
    });

    it('should handle array content', () => {
      const child = document.createElement('span');
      const element = helpers.createElement('div', {}, [
        'Text content',
        child
      ]);
      expect(element.innerHTML).toContain('Text content');
      expect(element.children).toHaveLength(1);
      expect(element.children[0]).toBe(child);
    });
  });

  describe('showNotification', () => {
    it('should show error notification', () => {
      const errorElement = document.getElementById('error-message');
      helpers.showNotification('Error message', 'error');

      expect(errorElement.textContent).toBe('Error message');
      expect(errorElement.classList.contains('hidden')).toBe(false);
    });

    it('should show success notification', () => {
      const successElement = document.getElementById('success-message');
      helpers.showNotification('Success message', 'success');

      expect(successElement.textContent).toBe('Success message');
      expect(successElement.classList.contains('hidden')).toBe(false);
    });

    it('should handle unknown notification type', () => {
      expect(() => helpers.showNotification('Test', 'unknown')).not.toThrow();
      expect(console.warn).toHaveBeenCalledWith('Unknown notification type: unknown');
    });

    it('should auto-hide notification after duration', (done) => {
      jest.useFakeTimers();
      const errorElement = document.getElementById('error-message');
      helpers.showNotification('Error message', 'error', 10);

      expect(errorElement.classList.contains('hidden')).toBe(false);

      // Fast-forward time by 15ms
      jest.advanceTimersByTime(15);

      expect(errorElement.classList.contains('hidden')).toBe(true);
      jest.useRealTimers();
      done();
    });

    it('should not auto-hide when duration is 0', () => {
      const errorElement = document.getElementById('error-message');
      helpers.showNotification('Error message', 'error', 0);

      expect(errorElement.classList.contains('hidden')).toBe(false);
      // No timeout set, so it should remain visible
    });
  });

  describe('withLoading', () => {
    let loadingElement;

    beforeEach(() => {
      loadingElement = document.createElement('div');
      loadingElement.classList.add('hidden');
      document.body.appendChild(loadingElement);
    });

    afterEach(() => {
      document.body.removeChild(loadingElement);
    });

    it('should show loading during async operation', async () => {
      const asyncFn = jest.fn().mockResolvedValue('result');

      const promise = helpers.withLoading(asyncFn, loadingElement);

      // Loading should be visible during operation
      expect(loadingElement.classList.contains('hidden')).toBe(false);

      const result = await promise;

      // Loading should be hidden after operation
      expect(loadingElement.classList.contains('hidden')).toBe(true);
      expect(result).toBe('result');
    });

    it('should hide loading even when async operation fails', async () => {
      const asyncFn = jest.fn().mockRejectedValue(new Error('Test error'));

      try {
        await helpers.withLoading(asyncFn, loadingElement);
      } catch (error) {
        expect(error.message).toBe('Test error');
      }

      expect(loadingElement.classList.contains('hidden')).toBe(true);
    });

    it('should work with selector string', async () => {
      loadingElement.id = 'loading-test';
      const asyncFn = jest.fn().mockResolvedValue('result');

      await helpers.withLoading(asyncFn, '#loading-test');

      expect(loadingElement.classList.contains('hidden')).toBe(true);
    });
  });
});
