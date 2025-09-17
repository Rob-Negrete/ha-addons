/**
 * Jest Setup File
 * Global setup for all tests
 */

// Mock global fetch for all tests
global.fetch = jest.fn();

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  log: jest.fn(),
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
};

// Setup DOM globals
Object.defineProperty(window, 'location', {
  value: {
    href: 'http://localhost:5001',
    origin: 'http://localhost:5001',
    pathname: '/',
    search: '',
    hash: ''
  },
  writable: true
});

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock sessionStorage
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.sessionStorage = sessionStorageMock;

// Setup common DOM elements that components expect
beforeEach(() => {
  // Reset fetch mock
  fetch.mockClear();

  // Reset console mocks
  console.log.mockClear();
  console.warn.mockClear();
  console.error.mockClear();

  // Reset storage mocks
  localStorage.clear();
  sessionStorage.clear();

  // Create basic DOM structure for tests
  document.body.innerHTML = `
    <div class="container">
      <div id="loading-indicator" class="hidden"></div>
      <div id="error-message" class="hidden"></div>
      <div id="success-message" class="hidden"></div>
      <div id="status-container"></div>
      <div id="face-count">0 faces found</div>
      <div id="face-list"></div>
      <div id="empty-state" class="hidden"></div>
      <div id="face-modal" class="hidden">
        <div class="modal-content">
          <div id="modal-face-id"></div>
          <div id="modal-detection-date"></div>
          <div id="modal-face-status"></div>
          <div id="modal-face-image"></div>
          <form id="face-update-form">
            <input id="face-name" name="name" />
            <textarea id="face-notes" name="notes"></textarea>
            <button id="save-update" type="submit">Save</button>
            <button id="cancel-update" type="button">Cancel</button>
          </form>
          <button id="close-modal">&times;</button>
        </div>
      </div>
      <button id="refresh-btn">Refresh</button>
    </div>
  `;
});

// Cleanup after each test
afterEach(() => {
  document.body.innerHTML = '';
  jest.clearAllMocks();
});

// Global test utilities
global.createMockFace = (overrides = {}) => ({
  id: 'test-face-123',
  face_id: 'test-face-123',
  detected_at: '2023-01-01T12:00:00Z',
  status: 'unclassified',
  name: null,
  notes: null,
  ...overrides
});

global.createMockFaces = (count = 3) => {
  return Array.from({ length: count }, (_, i) =>
    createMockFace({
      id: `test-face-${i + 1}`,
      face_id: `test-face-${i + 1}`,
      detected_at: new Date(Date.now() - i * 3600000).toISOString() // 1 hour apart
    })
  );
};

// Mock successful API responses
global.mockSuccessfulFetch = (data) => {
  fetch.mockResolvedValueOnce({
    ok: true,
    status: 200,
    headers: {
      get: jest.fn().mockReturnValue('application/json')
    },
    json: jest.fn().mockResolvedValue(data)
  });
};

// Mock failed API responses
global.mockFailedFetch = (status = 500, statusText = 'Internal Server Error') => {
  fetch.mockResolvedValueOnce({
    ok: false,
    status,
    statusText,
    headers: {
      get: jest.fn().mockReturnValue('application/json')
    }
  });
};

// Mock network error
global.mockNetworkError = () => {
  fetch.mockRejectedValueOnce(new TypeError('Failed to fetch'));
};
