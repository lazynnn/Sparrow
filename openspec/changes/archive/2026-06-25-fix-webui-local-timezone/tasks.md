## 1. Backend: UTC-aware timestamp serialization

- [x] 1.1 Update `sparrow/api/routes.py` — trace list endpoint: replace `t.timestamp.isoformat()` with `t.timestamp.isoformat() + "+00:00"` (or use a helper) so serialized timestamps include UTC offset
- [x] 1.2 Update `sparrow/api/routes.py` — trace detail endpoint: same UTC offset change for `trace.timestamp.isoformat()`
- [x] 1.3 Update `sparrow/tracing/tracer.py` — SSE notification: add `+00:00` offset to timestamp serialization
- [x] 1.4 Update `sparrow/archive/archiver.py` — JSONL export: ensure `trace.timestamp.isoformat()` includes `+00:00` offset (archive_timestamp already uses UTC-aware datetime)
- [x] 1.5 Create a shared helper function `utc_isoformat(dt)` in a utility module to centralize UTC-aware serialization and avoid repeating `+ "+00:00"` across files
- [x] 1.6 Update all backend callers from steps 1.1–1.4 to use the shared `utc_isoformat()` helper

## 2. Frontend: timezone-aware display formatting

- [x] 2.1 Update `formatTime()` in `sparrow/web/static/js/app.js` to use `Intl.DateTimeFormat` with `{ dateStyle: 'short', timeStyle: 'medium' }` for consistent locale-aware formatting
- [x] 2.2 Verify `formatTime()` correctly handles both naive ISO strings (legacy) and UTC-aware strings (`+00:00`) for backward compatibility

## 3. Frontend: consistent timestamp usage

- [x] 3.1 Update `sparrow/web/templates/index.html` line 263 — archive "Created" column: replace `a.archive_timestamp || '-'` with `formatTime(a.archive_timestamp)` so it uses the shared formatter
- [x] 3.2 Audit all timestamp displays in `index.html` to confirm no raw ISO strings remain (lines 91, 155 should already use `formatTime`)

## 4. Date range filter timezone handling

- [x] 4.1 Update frontend date filter inputs to send ISO strings with local timezone offset instead of naive date strings
- [x] 4.2 Update `sparrow/api/routes.py` date filter parsing (`fromisoformat` calls) to handle timezone-aware input and convert to UTC for database queries

## 5. Verification

- [x] 5.1 Manually verify that trace list timestamps display in local timezone
- [x] 5.2 Manually verify that trace detail timestamps display in local timezone
- [x] 5.3 Manually verify that archive "Created" timestamps display formatted (not raw string)
- [x] 5.4 Verify date range filtering returns correct results for non-UTC users
