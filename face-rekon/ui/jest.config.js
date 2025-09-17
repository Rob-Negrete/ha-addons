/**
 * Jest Configuration for Face Rekon UI
 */

module.exports = {
  // Test environment
  testEnvironment: 'jsdom',

  // Setup files
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],

  // Test file patterns
  testMatch: [
    '**/__tests__/**/*.js',
    '**/?(*.)+(spec|test).js'
  ],

  // Coverage collection
  collectCoverageFrom: [
    'assets/js/**/*.js',
    '!assets/js/**/__tests__/**',
    '!**/node_modules/**'
  ],

  // Coverage reporters
  coverageReporters: ['text', 'lcov', 'html'],

  // Coverage directory
  coverageDirectory: 'coverage',

  // Coverage thresholds
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70
    }
  },

  // Module file extensions
  moduleFileExtensions: ['js', 'json'],

  // Transform files
  transform: {
    '^.+\\.js$': 'babel-jest'
  },

  // Module paths
  modulePaths: ['<rootDir>/assets/js'],

  // Clear mocks between tests
  clearMocks: true,

  // Verbose output
  verbose: true,

  // Globals for tests
  globals: {
    'window': {},
    'document': {}
  },

  // Test timeout
  testTimeout: 10000,

  // Error on deprecated features
  errorOnDeprecated: true
};
