/**
 * Unit tests for FaceService
 */

const FaceService = require('../faceService.js');

describe('FaceService', () => {
  let faceService;

  beforeEach(() => {
    faceService = new FaceService();
  });

  describe('constructor', () => {
    it('should initialize with default baseUrl', () => {
      expect(faceService.baseUrl).toBe('');
      expect(faceService.apiPath).toBe('/api/face-rekon');
    });

    it('should initialize with custom baseUrl', () => {
      const customService = new FaceService('http://localhost:5001');
      expect(customService.baseUrl).toBe('http://localhost:5001');
    });
  });

  describe('_buildUrl', () => {
    it('should build correct URL with default baseUrl', () => {
      const url = faceService._buildUrl('/test');
      expect(url).toBe('/api/face-rekon/test');
    });

    it('should build correct URL with custom baseUrl', () => {
      const customService = new FaceService('http://localhost:5001');
      const url = customService._buildUrl('/test');
      expect(url).toBe('http://localhost:5001/api/face-rekon/test');
    });
  });

  describe('fetchUnclassifiedFaces', () => {
    it('should fetch unclassified faces successfully', async () => {
      const mockFaces = createMockFaces(2);
      mockSuccessfulFetch(mockFaces);

      const result = await faceService.fetchUnclassifiedFaces();

      expect(fetch).toHaveBeenCalledWith('/api/face-rekon/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      expect(result).toEqual(mockFaces);
    });

    it('should handle HTTP errors', async () => {
      mockFailedFetch(404, 'Not Found');

      await expect(faceService.fetchUnclassifiedFaces())
        .rejects.toThrow('HTTP 404: Not Found');
    });

    it('should handle network errors', async () => {
      mockNetworkError();

      await expect(faceService.fetchUnclassifiedFaces())
        .rejects.toThrow('Network error: Unable to connect to the face recognition service');
    });
  });

  describe('getFace', () => {
    it('should fetch face details successfully', async () => {
      const mockFace = createMockFace();
      mockSuccessfulFetch(mockFace);

      const result = await faceService.getFace('test-face-123');

      expect(fetch).toHaveBeenCalledWith('/api/face-rekon/test-face-123', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      expect(result).toEqual(mockFace);
    });

    it('should URL encode face ID', async () => {
      const mockFace = createMockFace();
      mockSuccessfulFetch(mockFace);

      await faceService.getFace('test face with spaces');

      expect(fetch).toHaveBeenCalledWith('/api/face-rekon/test%20face%20with%20spaces', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
    });

    it('should validate face ID parameter', async () => {
      await expect(faceService.getFace(null))
        .rejects.toThrow('Face ID is required and must be a string');

      await expect(faceService.getFace(''))
        .rejects.toThrow('Face ID is required and must be a string');

      await expect(faceService.getFace(123))
        .rejects.toThrow('Face ID is required and must be a string');
    });
  });

  describe('updateFace', () => {
    it('should update face successfully', async () => {
      const mockResponse = { status: 'success', message: 'Face updated' };
      mockSuccessfulFetch(mockResponse);

      const updateData = { name: 'John Doe', notes: 'Test person' };
      const result = await faceService.updateFace('test-face-123', updateData);

      expect(fetch).toHaveBeenCalledWith('/api/face-rekon/test-face-123', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: 'John Doe', notes: 'Test person' })
      });
      expect(result).toEqual(mockResponse);
    });

    it('should clean update data', async () => {
      const mockResponse = { status: 'success' };
      mockSuccessfulFetch(mockResponse);

      const updateData = {
        name: '  John Doe  ',
        notes: '  Test notes  '
      };

      await faceService.updateFace('test-face-123', updateData);

      expect(fetch).toHaveBeenCalledWith('/api/face-rekon/test-face-123', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: 'John Doe', notes: 'Test notes' })
      });
    });

    it('should handle empty notes', async () => {
      const mockResponse = { status: 'success' };
      mockSuccessfulFetch(mockResponse);

      const updateData = { name: 'John Doe' };
      await faceService.updateFace('test-face-123', updateData);

      expect(fetch).toHaveBeenCalledWith('/api/face-rekon/test-face-123', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: 'John Doe', notes: '' })
      });
    });

    it('should validate face ID parameter', async () => {
      const updateData = { name: 'John Doe' };

      await expect(faceService.updateFace(null, updateData))
        .rejects.toThrow('Face ID is required and must be a string');

      await expect(faceService.updateFace('', updateData))
        .rejects.toThrow('Face ID is required and must be a string');
    });

    it('should validate update data parameter', async () => {
      await expect(faceService.updateFace('test-face-123', null))
        .rejects.toThrow('Update data is required and must be an object');

      await expect(faceService.updateFace('test-face-123', 'invalid'))
        .rejects.toThrow('Update data is required and must be an object');
    });

    it('should validate name field', async () => {
      await expect(faceService.updateFace('test-face-123', {}))
        .rejects.toThrow('Name is required and must be a non-empty string');

      await expect(faceService.updateFace('test-face-123', { name: '' }))
        .rejects.toThrow('Name is required and must be a non-empty string');

      await expect(faceService.updateFace('test-face-123', { name: '   ' }))
        .rejects.toThrow('Name is required and must be a non-empty string');

      await expect(faceService.updateFace('test-face-123', { name: 123 }))
        .rejects.toThrow('Name is required and must be a non-empty string');
    });
  });

  describe('ping', () => {
    it('should ping service successfully', async () => {
      const mockResponse = { pong: true };
      mockSuccessfulFetch(mockResponse);

      const result = await faceService.ping();

      expect(fetch).toHaveBeenCalledWith('/api/face-rekon/ping', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      expect(result).toEqual(mockResponse);
    });

    it('should handle ping failures', async () => {
      mockFailedFetch(503, 'Service Unavailable');

      await expect(faceService.ping())
        .rejects.toThrow('HTTP 503: Service Unavailable');
    });
  });

  describe('isHealthy', () => {
    it('should return true when service is healthy', async () => {
      mockSuccessfulFetch({ pong: true });

      const result = await faceService.isHealthy();

      expect(result).toBe(true);
    });

    it('should return false when ping fails', async () => {
      mockFailedFetch(500);

      const result = await faceService.isHealthy();

      expect(result).toBe(false);
      expect(console.warn).toHaveBeenCalledWith(
        'Face service health check failed:',
        'HTTP 500: Internal Server Error'
      );
    });

    it('should return false when response is invalid', async () => {
      mockSuccessfulFetch({ pong: false });

      const result = await faceService.isHealthy();

      expect(result).toBe(false);
    });

    it('should return false on network error', async () => {
      mockNetworkError();

      const result = await faceService.isHealthy();

      expect(result).toBe(false);
      expect(console.warn).toHaveBeenCalledWith(
        'Face service health check failed:',
        'Network error: Unable to connect to the face recognition service'
      );
    });
  });

  describe('_makeRequest', () => {
    it('should handle non-JSON responses', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: {
          get: jest.fn().mockReturnValue('text/plain')
        },
        text: jest.fn().mockResolvedValue('Plain text response')
      });

      const result = await faceService._makeRequest('/test');

      expect(result).toBe('Plain text response');
    });

    it('should merge custom headers', async () => {
      mockSuccessfulFetch({});

      await faceService._makeRequest('/test', {
        headers: {
          'Custom-Header': 'value'
        }
      });

      expect(fetch).toHaveBeenCalledWith('/test', {
        headers: {
          'Custom-Header': 'value'
        }
      });
    });
  });
});
