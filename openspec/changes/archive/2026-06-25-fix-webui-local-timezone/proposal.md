## Why

Timestamps in the web UI are displayed in UTC+0 without respecting the user's local timezone. The backend serializes trace timestamps as naive ISO strings (no timezone offset), so the browser misinterprets them as local time — but they are actually UTC. This makes it confusing for users in non-UTC timezones to correlate request times with their own clock.

## What Changes

- Ensure all timestamp serialization on the backend includes UTC timezone information (e.g., `+00:00` suffix) so the browser can correctly convert to local time
- Apply the existing `formatTime()` helper consistently to all timestamp displays (archive "Created" column currently renders raw strings)
- Improve `formatTime()` to display a user-friendly format with relative time or explicit timezone indicator

## Capabilities

### New Capabilities

- `timezone-aware-display`: Ensures all timestamps shown in the web UI are correctly converted from UTC to the viewer's local timezone, with consistent formatting across all timestamp fields

### Modified Capabilities

- `log-viewer`: Timestamp display requirement changes from naive UTC strings to timezone-aware local display
- `trace-storage`: Serialization contract changes from naive ISO strings to UTC-aware ISO strings

## Impact

- Backend API responses: timestamp fields will include `+00:00` offset — backward compatible for most JSON consumers
- Frontend `formatTime()` in `app.js`: logic change to handle timezone-aware strings
- `index.html`: archive "Created" column must use `formatTime()` instead of raw string
- Date filter inputs in the API may need timezone awareness for correct range queries
