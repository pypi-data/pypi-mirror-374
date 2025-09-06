# Features

## Auto-registration
- Registers all concrete models in the selected app(s)
- Skips models whose names contain configured exclusion terms (e.g. `Historical`)
- Supports explicit apps, multiple apps, or full auto-discovery

## Smart changelist defaults
- `list_display` built from model fields, with exclusions from `DEFAULT_EXCLUDED_TERMS`
- Relation fields are displayed with clickable links via `linkify()`
- GenericForeignKeys displayed via `linkify_gfk()`
- Many-to-many fields rendered as comma-separated, linkified items with clipping (see below)
- Common filters auto-added for booleans, datetimes, and chars
- Properties on the model are appended if safe and unique
- Created/updated timestamp fields moved to end
- Optional reordering to ensure the first column is not a linkify field

## Performance and UX defaults
- Uses `TimeLimitedPaginator` to avoid slow count queries
- `show_full_result_count = False` to prevent expensive COUNT(*)
- `list_select_related = True` by default to reduce N+1 queries

## Polymorphic model support
- Detects `django-polymorphic` and uses:
  - `PolymorphicParentListAdmin` for parent models (with discovered children)
  - `PolymorphicChildListAdmin` for child models

## CSV export action
- Built-in `ExportCsvMixin` adds an "Export Selected to CSV" action

## Runtime customization API
- Retrieve the live `ModelAdmin` instance for a model and adjust:
  - `append_list_display`, `prepend_list_display`, `remove_list_display`
  - `append_filter_display`, `add_search_fields`
  - `update_list_select_related`
  - `append_inline`
  - `add_admin_method` (actions and display functions)

See Usage for examples.

## Many-to-many handling
- Detail view uses Django's default M2M form widget; nothing custom to learn
- Changelist shows M2M fields as a comma-separated list of related objects
  - Each item links to the related object's admin change page (when registered)
  - Displays up to a configurable limit (default: 10); extra items are clipped with `...`
  - Works with explicit `through` tables; the end objects are shown
