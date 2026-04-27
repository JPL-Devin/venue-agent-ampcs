# 5.3. Interleague Management View

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [frontend/src/views/interleague/InterleagueView.vue](frontend/src/views/interleague/InterleagueView.vue)

</details>



The `InterleagueView.vue` component [frontend/src/views/interleague/InterleagueView.vue]() provides a comprehensive interface for managing interleague play. It is structured as a three-tab interface, allowing users to designate field slots for interleague games, declare team availability, and search for available teams. This view leverages a `Promise.all` strategy for efficient data loading and employs distinct dialog/form patterns for each entity type, along with a unified deletion workflow.

## Component Structure and Data Flow

The `InterleagueView.vue` component uses Vue 3's Composition API with `<script setup>` [frontend/src/views/interleague/InterleagueView.vue:1-2](). It defines several reactive references to manage the state of the UI and data:
- `tab`: Controls the active tab in the `v-tabs` component [frontend/src/views/interleague/InterleagueView.vue:44]().
- `slots`: Stores a list of `InterleagueSlot` objects [frontend/src/views/interleague/InterleagueView.vue:46]().
- `availabilities`: Stores a list of `TeamAvailability` objects [frontend/src/views/interleague/InterleagueView.vue:47]().
- `searchResults`: Stores the results from the team search functionality [frontend/src/views/interleague/InterleagueView.vue:48]().
- `fieldSlots`, `divisions`, `teams`: Auxiliary data fetched to populate dropdowns and display related information [frontend/src/views/interleague/InterleagueView.vue:49-51]().
- `loading`: A boolean flag to indicate data loading status [frontend/src/views/interleague/InterleagueView.vue:52]().

Dialogs and forms for creating/editing entities are managed by `slotDialog`, `slotForm`, `availDialog`, `availForm`, `searchForm`, `deleteDialog`, and `deleteTarget` [frontend/src/views/interleague/InterleagueView.vue:54-65]().

### Data Loading Strategy

The `load` function [frontend/src/views/interleague/InterleagueView.vue:67-85]() is responsible for fetching all necessary data from the backend. It utilizes `Promise.all` to concurrently fetch interleague slots, team availabilities, field slots, divisions, and teams. This parallel fetching significantly improves the perceived loading time by reducing the total request duration.

```typescript
async function load() {
  loading.value = true
  try {
    const [sRes, aRes, fsRes, dRes, tRes] = await Promise.all([
      api.get('/interleague/slots'),
      api.get('/interleague/availability'),
      api.get('/field-slots'),
      api.get('/divisions'),
      api.get('/teams'),
    ])
    slots.value = sRes.data
    availabilities.value = aRes.data
    fieldSlots.value = fsRes.data
    divisions.value = dRes.data
    teams.value = tRes.data
  } finally {
    loading.value = false
  }
}
```
This `load` function is called once when the component is mounted via `onMounted(load)` [frontend/src/views/interleague/InterleagueView.vue:142](), and again after any successful creation or deletion operation to refresh the displayed data.

### Unbooked Slots Filter

The `unbookedSlots` computed property [frontend/src/views/interleague/InterleagueView.vue:87-89]() filters the `fieldSlots` array to only include those that are not yet booked (`s.is_booked === false`). This is crucial for the "Designate Slot" functionality, ensuring that users can only designate available field slots for interleague play.

Sources:
- [frontend/src/views/interleague/InterleagueView.vue:1-143]()

## Interleague Slots Tab

This tab allows users to designate specific `FieldSlot` entities as `InterleagueSlot` entities, making them available for interleague games.

### Designate Slot Dialog and Form

The "Designate Slot" button [frontend/src/views/interleague/InterleagueView.vue:163-165]() opens a `v-dialog` [frontend/src/views/interleague/InterleagueView.vue:244-274]() where users can select an unbooked field slot and optionally specify a target division.
- The `v-select` for `field_slot_id` [frontend/src/views/interleague/InterleagueView.vue:255-260]() uses the `unbookedSlots()` function to populate its options, ensuring only available slots are presented. The `slotLabel` function [frontend/src/views/interleague/InterleagueView.vue:91-93]() formats the display text for each slot.
- The `v-select` for `division_id` [frontend/src/views/interleague/InterleagueView.vue:262-267]() allows selecting a specific division or leaving it as "Any" (represented by an empty string).
- The `saveSlot` function [frontend/src/views/interleague/InterleagueView.vue:95-102]() sends a `POST` request to `/interleague/slots` with the selected `field_slot_id` and `division_id`. After a successful save, the dialog closes, and the data is reloaded.

### Interleague Slots Table

The table [frontend/src/views/interleague/InterleagueView.vue:167-197]() displays all currently designated interleague slots. It shows the field name, date, time, and the target division. Each row includes a delete button [frontend/src/views/interleague/InterleagueView.vue:184-190]() that triggers the `confirmDelete` function.

Sources:
- [frontend/src/views/interleague/InterleagueView.vue:91-93]()
- [frontend/src/views/interleague/InterleagueView.vue:95-102]()
- [frontend/src/views/interleague/InterleagueView.vue:163-197]()
- [frontend/src/views/interleague/InterleagueView.vue:244-274]()
- [frontend/src/views/interleague/InterleagueView.vue:255-260]()
- [frontend/src/views/interleague/InterleagueView.vue:262-267]()

## Team Availability Tab

This tab allows teams to declare specific time windows when they are available to play interleague games.

### Add Availability Dialog and Form

The "Add Availability" button [frontend/src/views/interleague/InterleagueView.vue:207-209]() opens a `v-dialog` [frontend/src/views/interleague/InterleagueView.vue:276-320]() for declaring team availability.
- The form collects `team_id`, `division_id`, `date`, `start_time`, `end_time`, and optional `notes` [frontend/src/views/interleague/InterleagueView.vue:287-312]().
- The `v-select` for `team_id` [frontend/src/views/interleague/InterleagueView.vue:287-292]() is populated by the `teams` data.
- The `v-select` for `division_id` [frontend/src/views/interleague/InterleagueView.vue:294-299]() is populated by the `divisions` data.
- The `saveAvailability` function [frontend/src/views/interleague/InterleagueView.vue:104-115]() sends a `POST` request to `/interleague/availability`. Upon success, the dialog closes, and data is reloaded.

### Team Availability Table

The table [frontend/src/views/interleague/InterleagueView.vue:211-241]() lists all declared team availabilities, showing the team name, organization, date, time, and notes. Each entry also has a delete button [frontend/src/views/interleague/InterleagueView.vue:230-236]() that uses `confirmDelete`.

Sources:
- [frontend/src/views/interleague/InterleagueView.vue:104-115]()
- [frontend/src/views/interleague/InterleagueView.vue:207-241]()
- [frontend/src/views/interleague/InterleagueView.vue:276-320]()
- [frontend/src/views/interleague/InterleagueView.vue:287-292]()
- [frontend/src/views/interleague/InterleagueView.vue:294-299]()

## Find Teams Tab

This tab allows users to search for teams that have declared availability, based on specific criteria.

### Search Form

The search form [frontend/src/views/interleague/InterleagueView.vue:322-344]() includes fields for:
- `division_id`: To filter by a specific division [frontend/src/views/interleague/InterleagueView.vue:330-335]().
- `date`: To filter by a specific date [frontend/src/views/interleague/InterleagueView.vue:337-339]().
- `region`: A free-text field for regional filtering [frontend/src/views/interleague/InterleagueView.vue:341-343]().
The `search` function [frontend/src/views/interleague/InterleagueView.vue:117-124]() constructs URL parameters from the form data and sends a `GET` request to `/interleague/search/teams`. The results are then stored in `searchResults`.

### Search Results Table

The table [frontend/src/views/interleague/InterleagueView.vue:346-376]() displays the teams found based on the search criteria. It shows the team name, organization, division, date, and time of their declared availability.

Sources:
- [frontend/src/views/interleague/InterleagueView.vue:117-124]()
- [frontend/src/views/interleague/InterleagueView.vue:322-376]()
- [frontend/src/views/interleague/InterleagueView.vue:330-335]()
- [frontend/src/views/interleague/InterleagueView.vue:337-339]()
- [frontend/src/views/interleague/InterleagueView.vue:341-343]()

## Deletion Workflow

A common deletion workflow is implemented for both interleague slots and team availabilities.
- The `confirmDelete` function [frontend/src/views/interleague/InterleagueView.vue:126-130]() is called when a delete button is clicked. It sets the `deleteTarget` with the `type` (either 'slot' or 'availability') and `id` of the item to be deleted, then opens the `deleteDialog` [frontend/src/views/interleague/InterleagueView.vue:378-397]().
- The `deleteDialog` presents a confirmation message.
- The `deleteItem` function [frontend/src/views/interleague/InterleagueView.vue:132-140]() is called when the user confirms deletion. It uses the `deleteTarget.type` to determine the correct API endpoint (`/interleague/slots/:id` or `/interleague/availability/:id`) and sends a `DELETE` request. After deletion, the dialog closes, and the `load` function is called to refresh the data.

### Deletion Workflow Diagram

```mermaid
graph TD
    A[User Clicks Delete Button] --> B{confirmDelete(type, id)};
    B --> C{deleteTarget = {type, id}};
    C --> D{deleteDialog = true};
    D -- User Confirms --> E{deleteItem()};
    E --> F{Get type and id from deleteTarget};
    F -- type == "slot" --> G{api.delete('/interleague/slots/:id')};
    F -- type == "availability" --> H{api.delete('/interleague/availability/:id')};
    G --> I{deleteDialog = false};
    H --> I;
    I --> J{load()};
    J --> K[Data Refreshed];
```
**Deletion Workflow**

Sources:
- [frontend/src/views/interleague/InterleagueView.vue:126-130]()
- [frontend/src/views/interleague/InterleagueView.vue:132-140]()
- [frontend/src/views/interleague/InterleagueView.vue:378-397]()

## Data Models (Frontend)

The component defines several TypeScript interfaces to represent the data structures received from the backend API [frontend/src/views/interleague/InterleagueView.vue:5-42]():
- `InterleagueSlot`: Represents a designated interleague slot, including nested `field_slot` and `field` details.
- `TeamAvailability`: Represents a team's declared availability, including nested `team` and `organization` details.
- `SearchResult`: Represents a team found through the search functionality.
- `FieldSlot`, `Division`, `Team`: Simplified interfaces for auxiliary data used in dropdowns and displays.

These interfaces ensure type safety and provide clear expectations for the data handled within the component.

### Frontend Data Model to Backend API Mapping

```mermaid
erDiagram
    "InterleagueSlot" {
        string id
        string field_slot_id
        string division_id
        string notes
        object field_slot
    }
    "TeamAvailability" {
        string id
        string team_id
        string division_id
        string date
        string start_time
        string end_time
        string notes
        object team
    }
    "SearchResult" {
        string team_id
        string team_name
        string organization_id
        string organization_name
        string division_id
        string division_name
        string date
        string start_time
        string end_time
    }
    "FieldSlot" {
        string id
        string date
        string start_time
        string end_time
        boolean is_booked
        object field
    }
    "Division" {
        string id
        string name
    }
    "Team" {
        string id
        string name
    }

    "InterleagueSlot" }|--|| "FieldSlot" : "field_slot_id"
    "InterleagueSlot" }|--o{ "Division" : "division_id"
    "TeamAvailability" }|--|| "Team" : "team_id"
    "TeamAvailability" }|--o{ "Division" : "division_id"
    "SearchResult" }|--|| "Team" : "team_id"
    "SearchResult" }|--|| "Division" : "division_id"
    "SearchResult" }|--|| "Organization" : "organization_id"

    "GET /interleague/slots" --|> "InterleagueSlot" : returns list
    "POST /interleague/slots" --|> "InterleagueSlot" : creates
    "DELETE /interleague/slots/{id}" --|> "InterleagueSlot" : deletes

    "GET /interleague/availability" --|> "TeamAvailability" : returns list
    "POST /interleague/availability" --|> "TeamAvailability" : creates
    "DELETE /interleague/availability/{id}" --|> "TeamAvailability" : deletes

    "GET /interleague/search/teams" --|> "SearchResult" : returns list

    "GET /field-slots" --|> "FieldSlot" : returns list
    "GET /divisions" --|> "Division" : returns list
    "GET /teams" --|> "Team" : returns list
```
**Frontend Data Models and API Endpoints**

Sources:
- [frontend/src/views/interleague/InterleagueView.vue:5-42]()
