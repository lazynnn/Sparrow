## Purpose

Fullscreen JSON viewer dialog for inspecting trace detail data (request/response bodies and headers) in a collapsible tree view with search and copy capabilities.

## Requirements

### Requirement: JSON viewer fullscreen dialog
The system SHALL provide a fullscreen overlay dialog that displays JSON content with a collapsible tree view, accessible from the trace detail panel.

#### Scenario: Open JSON viewer from request body
- **WHEN** a user clicks the expand button on the Request Body section in the trace detail panel
- **THEN** a fullscreen overlay dialog SHALL open displaying the request body JSON in a collapsible tree view with syntax highlighting

#### Scenario: Open JSON viewer from response body
- **WHEN** a user clicks the expand button on the Response Body section in the trace detail panel
- **THEN** a fullscreen overlay dialog SHALL open displaying the response body JSON in a collapsible tree view with syntax highlighting

#### Scenario: Open JSON viewer from headers
- **WHEN** a user clicks the expand button on the Request Headers or Response Headers section in the trace detail panel
- **THEN** a fullscreen overlay dialog SHALL open displaying the headers JSON in a collapsible tree view with syntax highlighting

#### Scenario: Close JSON viewer dialog
- **WHEN** a user clicks the close button, presses the Escape key, or clicks the backdrop overlay
- **THEN** the JSON viewer dialog SHALL close and return focus to the trace detail panel

### Requirement: Collapsible JSON tree rendering
The system SHALL render JSON data as an interactive tree where objects and arrays are collapsible and expandable.

#### Scenario: Collapse a JSON object or array node
- **WHEN** a user clicks on an expanded object or array node in the tree
- **THEN** that node SHALL collapse, hiding its children, and display a summary (e.g., key count or array length)

#### Scenario: Expand a JSON object or array node
- **WHEN** a user clicks on a collapsed object or array node in the tree
- **THEN** that node SHALL expand, revealing its children with proper indentation

#### Scenario: Display leaf values with syntax highlighting
- **WHEN** the tree renders a leaf value (string, number, boolean, null)
- **THEN** the value SHALL be displayed with syntax highlighting matching the existing color scheme (json-key, json-string, json-number, json-boolean, json-null classes)

### Requirement: Copy to clipboard
The system SHALL provide a button to copy the full JSON content to the clipboard.

#### Scenario: Copy JSON to clipboard
- **WHEN** a user clicks the copy button in the JSON viewer dialog
- **THEN** the full formatted JSON content SHALL be copied to the system clipboard
- **AND** the button SHALL show brief visual feedback confirming the copy action

### Requirement: Search within JSON
The system SHALL provide a search input that highlights matching text in the JSON tree and expands parent nodes to reveal matches.

#### Scenario: Search for a key or value
- **WHEN** a user types a search term in the search input
- **THEN** all matching keys and values in the JSON tree SHALL be visually highlighted
- **AND** all ancestor nodes of matching items SHALL be automatically expanded

#### Scenario: No search matches
- **WHEN** a user types a search term that has no matches in the JSON data
- **THEN** the search input SHALL indicate no matches were found

#### Scenario: Clear search
- **WHEN** a user clears the search input
- **THEN** all highlights SHALL be removed and the tree SHALL return to its default expansion state

### Requirement: Expand button on trace detail JSON sections
Each JSON section in the trace detail panel (Request Body, Response Body, Request Headers, Response Headers) SHALL display an expand button that opens the JSON viewer dialog.

#### Scenario: Expand button visible on JSON sections
- **WHEN** a trace detail panel is displayed
- **THEN** each JSON section header (Request Body, Response Body, Request Headers, Response Headers) SHALL show an expand/open button alongside the section title

#### Scenario: Expand button opens dialog for that section
- **WHEN** a user clicks the expand button on a specific JSON section
- **THEN** the JSON viewer dialog SHALL open with the title matching that section and the content from that specific JSON field
