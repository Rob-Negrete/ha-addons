# Face Recognition UI

A clean, well-structured frontend interface for the Face Recognition Home Assistant Add-on, following SOLID principles and clean architecture patterns.

## Overview

This web UI provides a user-friendly interface for managing unclassified faces detected by the face recognition system. It allows users to view, classify, and assign names to detected faces through a modern, responsive web interface.

## Architecture

The UI follows SOLID principles with clear separation of concerns:

### Single Responsibility Principle

- **FaceService**: Only handles API communication
- **FaceListComponent**: Only manages face list UI rendering
- **Helpers**: Only provides utility functions
- **App**: Only manages application initialization and dependency injection

### Dependency Injection

Components accept their dependencies as parameters rather than creating them internally, making testing and maintenance easier.

## Project Structure

```
ui/
├── index.html                 # Main HTML template
├── assets/
│   ├── css/
│   │   └── styles.css         # Main stylesheet with responsive design
│   ├── js/
│   │   ├── services/
│   │   │   ├── faceService.js # API service layer
│   │   │   └── __tests__/     # Service unit tests
│   │   ├── components/
│   │   │   ├── faceList.js    # Face list UI component
│   │   │   └── __tests__/     # Component unit tests
│   │   ├── utils/
│   │   │   ├── helpers.js     # Utility functions
│   │   │   └── __tests__/     # Utility function tests
│   │   └── app.js             # Main application entry point
│   └── images/                # UI assets directory
├── jest.config.js             # Jest testing configuration
├── jest.setup.js              # Jest test setup and mocks
├── package.json               # Dependencies and scripts
└── README.md                  # This file
```

## Key Features

### Face Management

- **Face Listing**: Displays unclassified faces in a responsive grid
- **Face Details**: Modal view showing face information and metadata
- **Face Classification**: Form to assign names and notes to faces
- **Real-time Updates**: Auto-refresh and manual refresh capabilities

### User Experience

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Loading States**: Clear indicators during API operations
- **Error Handling**: User-friendly error messages and fallbacks
- **Keyboard Navigation**: Escape key, Enter key, and other shortcuts

### Technical Features

- **Vanilla JavaScript**: No external frameworks, lightweight and fast
- **ES6+ Features**: Modern JavaScript with classes and async/await
- **Comprehensive Testing**: Unit tests for all components and services
- **Clean Architecture**: SOLID principles and dependency injection

## API Integration

The UI integrates with the following Flask API endpoints:

- `GET /face-rekon/` - List unclassified faces
- `GET /face-rekon/<face_id>` - Get specific face details
- `PATCH /face-rekon/<face_id>` - Update face information
- `GET /face-rekon/ping` - Health check

## Testing

### Running Tests

```bash
cd ui/
npm install
npm test
```

### Test Coverage

```bash
npm run test:coverage
```

The testing setup includes:

- **Unit Tests**: For all services, components, and utilities
- **Mocked API Calls**: Isolated testing without backend dependencies
- **DOM Testing**: Component rendering and interaction testing
- **Edge Cases**: Error handling and validation testing

### Test Structure

- Tests are co-located with source files in `__tests__` directories
- Jest configuration with jsdom environment for DOM testing
- Global test utilities and mocks for consistent testing
- Coverage thresholds set to 70% for all metrics

## Development

### Prerequisites

- Node.js 14+ (for testing)
- Flask app running on port 5001

### Local Development

The UI is served directly by the Flask application. No separate development server is needed.

1. Start the Flask app: `python scripts/app.py`
2. Open browser to: `http://localhost:5001`

### Making Changes

1. Edit files in the `ui/` directory
2. Refresh browser to see changes
3. Run tests: `npm test`

## Home Assistant Integration

The UI is configured for Home Assistant add-on integration:

### Config.json Updates

- **Ingress Support**: `"ingress": true` for HA iframe integration
- **Panel Icon**: `"mdi:face-recognition"` for sidebar icon
- **Web UI**: Automatic link in HA add-on page

### Flask App Updates

- Routes configured to serve UI files from correct paths
- Static assets served via `/assets/` route
- CORS enabled for HA integration

## Error Handling

The UI implements comprehensive error handling:

### API Errors

- Network connectivity issues
- HTTP status errors (404, 500, etc.)
- Invalid response formats

### Validation Errors

- Missing required fields
- Invalid face IDs
- Empty form submissions

### User Feedback

- Toast notifications for success/error states
- Loading indicators during operations
- Fallback content for empty states

## Browser Compatibility

The UI is designed to work with modern browsers:

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

Uses progressive enhancement with graceful degradation for older browsers.

## Performance Considerations

### Optimization Features

- **Lazy Loading**: Images loaded only when needed
- **Debounced Events**: Reduced API calls during user interactions
- **Minimal DOM Manipulation**: Efficient rendering and updates
- **Caching**: Browser caching for static assets

### Auto-refresh Strategy

- Manual refresh button for immediate updates
- Auto-refresh every 30 seconds when page is visible
- Smart refresh on tab visibility change (after 5+ minutes)

## Security

### XSS Prevention

- HTML sanitization for user-generated content
- Safe DOM manipulation practices
- No inline scripts or styles

### Input Validation

- Client-side validation for immediate feedback
- Server-side validation as final authority
- Proper encoding of URL parameters

## Accessibility

The UI includes basic accessibility features:

- Semantic HTML structure
- Keyboard navigation support
- Focus management for modals
- Alt text for images
- Color contrast compliance

## Future Enhancements

Potential improvements for future versions:

- **Image Preview**: Display actual face thumbnails when available
- **Batch Operations**: Select and classify multiple faces at once
- **Search/Filter**: Find specific faces by date, status, etc.
- **Export/Import**: Backup and restore face classifications
- **Real-time Updates**: WebSocket integration for live updates
- **Advanced Analytics**: Face detection statistics and trends
