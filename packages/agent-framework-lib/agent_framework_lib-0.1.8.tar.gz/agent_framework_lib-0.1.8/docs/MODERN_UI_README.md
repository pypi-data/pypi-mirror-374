# Modern UI Implementation

This document describes the enhanced modern UI implementation for the Agent Framework, built according to the Product Requirements Document specifications.

## Overview

The new UI provides a modern, responsive interface that supports both end-user and admin workflows. It's built using:

- **HTMX** for dynamic interactions
- **Alpine.js** for reactive state management  
- **BaseCoat UI** (via Tailwind CSS) for modern styling
- **Marked.js** for markdown rendering
- **DOMPurify** for safe HTML sanitization
- **Pure HTML/CSS/JS** - no React or similar frameworks

## Accessing the UI

The modern UI is available at `/ui` endpoint and coexists with the existing testapp at `/testapp`.

```
http://localhost:8000/ui
```

## Features

### End User Mode (Default)

1. **User ID Management**
   - Auto-detects `user_id` from URL parameter
   - Allows manual entry if not provided
   - Persists for the session duration

2. **Session Management**
   - View list of previous sessions
   - Create new sessions with custom system prompts and data
   - Select sessions to view conversation history
   - Continue conversations in existing sessions

3. **Enhanced Messaging**
   - Beautiful message bubbles with chat-like appearance
   - Full markdown rendering support
   - Toggle streaming mode for real-time responses
   - Real-time message feedback (👍/👎)
   - Auto-scroll to latest messages

4. **Session Creation**
   - Set custom system prompts
   - Provide JSON data for context
   - Template variables support ({{data.key}})

5. **Streaming Features**
   - **Under the Hood** section showing streaming activities
   - Real-time activity tracking
   - Raw stream output display
   - Auto-collapsing when final answer is received

### Admin Mode

1. **Access Control**
   - Password-protected admin access: **admin123** (hardcoded for now)
   - "Go Admin" link in end-user mode
   - Uses simplified authentication system

2. **User Management**
   - View all users in the system
   - Expandable user lists showing sessions
   - Browse any user's sessions

3. **Session Viewing**
   - Read-only access to all conversations
   - View complete interaction history
   - Cannot send messages in other users' sessions
   - Can only interact in their own admin sessions

## Technical Implementation

### Enhanced Message Display

- **Chat bubbles** with proper alignment (user messages on right, assistant on left)
- **Speech bubble tails** for better visual conversation flow
- **Markdown rendering** using marked.js for rich text formatting
- **Code highlighting** for code blocks
- **Safe HTML** rendering with DOMPurify sanitization

### Streaming Implementation

- **Correct endpoint**: Uses `/sessions/{sessionId}/stream` (not `/message_stream`)
- **Under the Hood panel**: Shows real-time streaming activities
- **Activity types**: Different styling for tool requests, results, errors
- **Raw stream output**: Terminal-style display of actual stream data
- **Auto-collapse**: Under the Hood section collapses when final answer is received

### Message Feedback System

- **Immediate UI updates** with local state management
- **Server persistence** via `/feedback/message` endpoint
- **Visual feedback states** with color-coded buttons
- **One-time voting** - buttons disable after feedback is given

### Authentication

The UI works with the existing authentication system:
- Simple password check for admin access
- API key support via Bearer tokens or X-API-Key headers
- Seamless integration with existing security middleware

### API Integration

Uses existing backend endpoints:
- `GET /sessions` - List user sessions
- `GET /sessions/{id}/history` - Get conversation history
- `POST /message` - Send messages (non-streaming)
- `POST /sessions/{id}/stream` - Send messages (streaming)
- `POST /init` - Create new sessions
- `POST /end` - End sessions
- `POST /feedback/message` - Submit feedback

## User Workflows

### Creating a New Session

1. Click the "+" button in the sessions sidebar
2. Enter optional system prompt
3. Add optional JSON data for context
4. Click "Create Session"
5. Start conversing immediately

### Using Streaming Mode

1. Toggle "Enable streaming responses" checkbox
2. Send a message
3. Watch real-time response generation
4. Click "Under the Hood" to see streaming details
5. View raw stream data and activity logs

### Admin Access

1. Click "Go Admin" link
2. Enter admin password: **admin123**
3. Browse all users and their sessions
4. View conversations (read-only for other users)
5. Click "Exit Admin" to return to normal mode

### Message Feedback

1. Wait for assistant response
2. Click thumbs up (👍) or thumbs down (👎)
3. Feedback is stored and buttons become disabled
4. Visual confirmation with color coding

## Configuration

### Environment Variables

The UI respects existing authentication settings:
- `REQUIRE_AUTH` - Enable/disable authentication
- `BASIC_AUTH_USERNAME` - Admin username
- `BASIC_AUTH_PASSWORD` - Admin password
- `API_KEYS` - Valid API keys for authentication

### URL Parameters

- `user_id` - Pre-set the user ID for the session

Example: `http://localhost:8000/ui?user_id=john_doe`

## Styling & Design

### Message Bubbles

- **User messages**: Blue background, aligned right, speech tail on right
- **Assistant messages**: White background, aligned left, speech tail on left
- **Proper spacing**: Consistent padding and margins
- **Responsive design**: Adapts to different screen sizes

### Under the Hood Panel

- **Collapsible header**: Click to expand/collapse
- **Activity timeline**: Chronological list of streaming events
- **Color coding**: Different colors for different activity types
- **Terminal output**: Raw stream data in terminal-style display

### Feedback Buttons

- **Hover effects**: Visual feedback on interaction
- **Active states**: Clear indication when feedback is submitted
- **Disabled states**: Prevents multiple submissions

## Browser Compatibility

- Modern browsers with ES6+ support
- Chrome 60+, Firefox 55+, Safari 12+, Edge 79+
- No Internet Explorer support

## Development Notes

### File Structure

```
agent_framework/
├── modern_ui.html          # Main UI file
├── server.py               # Backend (updated with /ui endpoint)
└── MODERN_UI_README.md     # This documentation
```

### Customization

The UI can be customized by modifying:
- CSS classes for styling (includes many utility classes)
- Alpine.js data and methods for behavior
- HTML structure for layout changes
- Markdown rendering options

### Performance

- **Lightweight**: Single HTML file with CDN dependencies
- **Fast loading**: Minimal JavaScript bundle
- **Efficient streaming**: Proper stream handling with buffering
- **Responsive UI**: Immediate feedback for user interactions

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Check `REQUIRE_AUTH` environment variable
   - Use hardcoded password: **admin123** for admin access

2. **Session Not Loading**
   - Ensure user_id is provided
   - Check browser console for API errors

3. **Messages Not Sending**
   - Verify session is selected
   - Check authentication status
   - Ensure backend is running
   - Try both streaming and non-streaming modes

4. **Messages Not Displaying**
   - Check browser console for API response format
   - Verify the `/sessions/{id}/history` endpoint is working
   - Ensure messages have proper `text_content` or `response_text_main` fields

5. **Streaming Not Working**
   - Verify endpoint is `/sessions/{sessionId}/stream`
   - Check for 404 errors in network tab
   - Ensure streaming is supported by the agent
   - Look for Under the Hood activities

6. **Admin Mode Issues**
   - Use hardcoded password: **admin123**
   - Admin can only send messages in their own sessions
   - Admin mode is local to browser session

### Debug Mode

Enable browser developer tools console for detailed logging:
- **Network tab**: Shows API requests/responses
- **Console tab**: Shows JavaScript errors and debug logs
- **Application tab**: Shows local storage data

### Streaming Debug Information

The Under the Hood panel provides detailed streaming information:
- **Activity timeline**: Shows what the agent is doing
- **Raw stream output**: Actual data received from server
- **Error logging**: Any streaming errors are displayed
- **Timing information**: Timestamps for all activities

## Migration from TestApp

The new UI is designed to replace the existing testapp but coexists during the transition:

1. Both `/testapp` and `/ui` are available
2. Same backend APIs support both interfaces
3. No data migration required
4. Users can switch between interfaces seamlessly
5. Enhanced features only available in new UI

## Future Enhancements

Potential improvements for future versions:
- **WebSocket support** for even better real-time communication
- **File upload support** for multimodal conversations
- **Rich text editor** for message composition
- **Message search** functionality
- **Export conversations** feature
- **Dark mode** theme toggle
- **Advanced admin analytics** and user management
- **Custom themes** and layout options

## Support

For issues or questions about the modern UI:
1. Check this documentation
2. Review browser console for errors
3. Verify backend API responses
4. Check authentication configuration
5. Test both streaming and non-streaming modes
6. Examine Under the Hood data during streaming 