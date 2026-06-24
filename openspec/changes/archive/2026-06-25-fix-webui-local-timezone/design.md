## Context

The Sparrow web UI displays LLM request trace timestamps, but the backend serializes them as naive ISO 8601 strings (e.g., `2026-06-25T10:30:00`) without timezone offset information. SQLite's `func.now()` produces UTC timestamps, but `.isoformat()` on naive datetime objects omits the `+00:00` suffix. When the browser receives these strings, `new Date()` treats them as local time — creating a mismatch where UTC timestamps appear as if they were in the user's timezone.

Additionally, the archive "Created" column in the UI renders the raw `archive_timestamp` string instead of using the `formatTime()` helper, leading to inconsistent display.

The frontend uses Alpine.js with no external time libraries. The backend is Python/Flask with SQLAlchemy.

## Goals / Non-Goals

**Goals:**
- All timestamps displayed in the web UI SHALL respect the viewer's local timezone
- Backend SHALL serialize all timestamps as UTC-aware ISO 8601 strings (with `+00:00`)
- All timestamp displays in the UI SHALL use a consistent formatting function
- Date range filters SHALL correctly handle timezone-aware timestamps

**Non-Goals:**
- Adding a timezone selector in the UI (always use browser's local timezone)
- Supporting timezone-aware storage in SQLite (keep naive UTC in DB, add offset only at serialization)
- Adding external time libraries (moment.js, dayjs, etc.) — use native JavaScript `Intl` API
- Changing the database schema or column types

## Decisions

### Decision 1: Serialize as UTC-aware ISO strings at the API boundary

**Choice**: Add `+00:00` suffix when serializing naive UTC timestamps via `.isoformat()`, rather than changing the database column type or adding a timezone-aware column.

**Rationale**: The database stores timestamps as naive UTC via `func.now()`. Making them timezone-aware in SQLAlchemy would require schema changes and affect the async write path. Instead, we append the UTC offset only at the serialization layer (API routes and SSE notifications). This is the minimal change that fixes the browser interpretation issue.

**Alternatives considered**:
- *Change DB column to timezone-aware*: Requires migration, breaks `func.now()` default, more invasive
- *Add offset on frontend*: Fragile, requires knowing the server timezone; moves responsibility to wrong layer

### Decision 2: Use native `Intl.DateTimeFormat` for frontend display

**Choice**: Enhance `formatTime()` to use `Intl.DateTimeFormat` with explicit options for consistent, locale-aware formatting.

**Rationale**: No external dependencies needed. `Intl.DateTimeFormat` is well-supported in all modern browsers and handles timezone conversion automatically when given a timezone-aware ISO string. It also provides locale-appropriate formatting.

**Alternatives considered**:
- *dayjs/moment.js*: Adds external dependency; the project has no npm/build system
- *Manual string construction*: Error-prone, doesn't handle locale or DST

### Decision 3: Apply `formatTime()` to all timestamp displays

**Choice**: Fix the archive "Created" column to use `formatTime()` instead of rendering the raw string.

**Rationale**: Single point of control for timestamp formatting. If format changes are needed later, only `formatTime()` needs updating.

### Decision 4: Make date filter inputs timezone-aware

**Choice**: When the frontend sends date range filter values, send them as ISO strings with the local timezone offset. On the backend, parse them as timezone-aware and convert to UTC for the database query.

**Rationale**: Currently, date filter values are naive strings interpreted as UTC by the backend. If a user in UTC+8 selects "today", they expect traces from their local today, not UTC today.

## Risks / Trade-offs

- [Risk] API consumers relying on naive ISO string format may break → **Mitigation**: Adding `+00:00` is backward-compatible; `datetime.fromisoformat()` in Python and `new Date()` in JS both handle offset-aware strings
- [Risk] SQLite `func.now()` produces naive datetimes; we must remember they are UTC by convention → **Mitigation**: This is already the current convention; the change only makes it explicit at the serialization boundary
- [Risk] Date filter change may shift query results for existing users → **Mitigation**: The current behavior is already incorrect for non-UTC users; fixing it aligns with user expectations
