# Changelog






















































## [0.1.56] - 2025-09-04

### Other
- build(pyproject): move dependencies back under [project] and fix [project.urls] table (90eca0e)
  - Correct TOML scope so `dependencies` is part of [project]
  - Keep [project.urls] as a separate table (PEP 621-compliant)
  - Fixes setuptools validation error: `project.urls.dependencies

## [0.1.55] - 2025-09-04

### Other
- Merge branch 'dev' of https://github.com/bacardi-code/techops-networking-netbox-entraid-tools into dev (e786aa6)
- build(pyproject): fix [project.urls] TOML to PEP 621 table to resolve build parse error (ca8f5b6)
  - Convert inline `urls = { ... }` to `[project.urls]` table
  - Remove trailing comma that broke TOML parsing
  - Unblocks `python -m build` in CI
  -

## [0.1.54] - 2025-09-04

### Breaking Changes
- feat(release): add build/sign/upload pipeline and wire manual CI workflow (e1db10c)
  - tools/release.py
  - add optional flags:
  - --build to produce sdist and wheel via python -m build
  - --sign-artifacts to create detached ASCII-armored .asc signatures for dist/*
  - --upload to publish dist/* via twine (uses TWINE_USERNAME/PASSWORD)
  - keep __version__ as single source of truth in netbox_entraid_tools/__init__.py
  - generate grouped CHANGELOG entries from Conventional Commits since last tag
  - create annotated vX.Y.Z tags with optional GPG signing and push
  - .github/workflows/release.yml
  - manual workflow_dispatch with inputs: part, sign_tag, build (default true), sign_artifacts, upload
  - fetch full history (fetch-depth: 0) to ensure tags are available
  - install build and twine
  - optional GPG key import for signing path
  - run tools/release.py with selected flags; support PyPI upload via TWINE_* secrets
  - GITFLOW.md
  - document streamlined release workflow and v-prefixed tags (e.g., v0.1.54)
  - clarify published distribution name is netbox-entraid-tools, independent of repo name
  - metadata
  - fix __project_url__ to https://github.com/bacardi-code/techops-networking-netbox-entraid-tools
  Docs: CI secrets and signing
  - GPG_PRIVATE_KEY (ASCII-armored), GPG_PASSPHRASE
  - TWINE_USERNAME=__token__, TWINE_PASSWORD=pypi-…
  BREAKING CHANGE: tags now use v-prefix consistently (vMAJOR.MINOR.PATCH). Update any external tooling that expected
  - tags now use v-prefix consistently (vMAJOR.MINOR.PATCH). Update any external tooling that expected
- feat(build): modernize build system and enhance deployment tools (9b33dfe)
  This commit implements several improvements to the build and deployment process:
  - Add pyproject.toml for PEP 517 compatibility, addressing Oct 31, 2025 deprecation warning
  - Enhance Bump-FolderVersion.ps1 with comprehensive comment-based help documentation
  - Add -OpenCode parameter to Bump-FolderVersion.ps1 with default value of $True
  - Implement automatic VS Code launching in the newly created version folder
  - Create detailed BUILD.md with instructions for modern build workflow
  - Update release.py to include guidance for the new build system
  - Create CODE_SIGNING.md with PowerShell code signing management instructions
  - Update README.md with references to build documentation
  - Remove invalid signature from Bump-FolderVersion.ps1
  These changes ensure compatibility with future Python packaging standards
  while enhancing the developer experience when managing version upgrades.
  The modern build system eliminates deprecation warnings and improves
  compatibility with current packaging tools.
  BREAKING CHANGE: The PowerShell script signature has been removed and will need
  to be re-signed following the guidance in CODE_SIGNING.md
  - The PowerShell script signature has been removed and will need
  - to be re-signed following the guidance in CODE_SIGNING.md

### Features
- feat(release): add preflight safety checks and --allow-retag to release helper ci(release): add allow_retag input and fix non-interactive GPG wrapper docs: document safety checks and new flag in GITFLOW and AGENT_CONTEXT (d2f4d85)
  - tools/release.py:
  - Refuse to run in detached HEAD; require a named branch
  - Detect existing tag locally and on origin; abort by default
  - Add --allow-retag to delete and recreate an existing tag (local and remote)
  - Include branch name in final release message
  - .github/workflows/release.yml:
  - Add input allow_retag and pass --allow-retag to release.py
  - Use a single /usr/local/bin/gpg wrapper invoking /usr/bin/gpg with loopback and env passphrase
  - Ensure git uses the wrapper; remove conflicting/recursive config
  - Docs:
  - GITFLOW.md: Add --allow-retag to flags; note detached HEAD refusal and tag-exists behavior
  - AGENT_CONTEXT.md: Record the new safety checks and behavior
  Motivation:
  - Prevent accidental releases from detached HEAD and unintentional tag overwrites
  - Make intentional tag replacement explicit via --allow-retag
  - Stabilize CI GPG signing by avoiding recursive wrappers and ensuring loopback pinentry
  Notes:
  - Tag format unchanged (vMAJOR.MINOR.PATCH)
  - Package name remains netbox-entraid-tools
  - No runtime behavior changes to the plugin;
- feat(release): add build/sign/upload pipeline and wire manual CI workflow (e1db10c)
  - tools/release.py
  - add optional flags:
  - --build to produce sdist and wheel via python -m build
  - --sign-artifacts to create detached ASCII-armored .asc signatures for dist/*
  - --upload to publish dist/* via twine (uses TWINE_USERNAME/PASSWORD)
  - keep __version__ as single source of truth in netbox_entraid_tools/__init__.py
  - generate grouped CHANGELOG entries from Conventional Commits since last tag
  - create annotated vX.Y.Z tags with optional GPG signing and push
  - .github/workflows/release.yml
  - manual workflow_dispatch with inputs: part, sign_tag, build (default true), sign_artifacts, upload
  - fetch full history (fetch-depth: 0) to ensure tags are available
  - install build and twine
  - optional GPG key import for signing path
  - run tools/release.py with selected flags; support PyPI upload via TWINE_* secrets
  - GITFLOW.md
  - document streamlined release workflow and v-prefixed tags (e.g., v0.1.54)
  - clarify published distribution name is netbox-entraid-tools, independent of repo name
  - metadata
  - fix __project_url__ to https://github.com/bacardi-code/techops-networking-netbox-entraid-tools
  Docs: CI secrets and signing
  - GPG_PRIVATE_KEY (ASCII-armored), GPG_PASSPHRASE
  - TWINE_USERNAME=__token__, TWINE_PASSWORD=pypi-…
  BREAKING CHANGE: tags now use v-prefix consistently (vMAJOR.MINOR.PATCH). Update any external tooling that expected
- feat(ui): add bulk EntraID resolve button to contacts list (0fedbb3)
  Add functionality to resolve all contacts from EntraID in bulk via the contacts list page.
  This builds on the existing per-contact resolution functionality and reuses much of the same
  infrastructure.
  The implementation includes:
  - Add list_buttons method to ContactActions template extension
  - Create contact_list_actions.html button template for the contacts list
  - Add BulkResolveContactsView to handle the bulk operation
  - Create URL path for bulk resolution endpoint
  - Update resolve_contact_confirm.html to support both individual and bulk operations
  This enhancement allows administrators to easily refresh EntraID information for all
  contacts at once, rather than having to visit each contact individually.
  Related to: #42
- feat(build): modernize build system and enhance deployment tools (9b33dfe)
  This commit implements several improvements to the build and deployment process:
  - Add pyproject.toml for PEP 517 compatibility, addressing Oct 31, 2025 deprecation warning
  - Enhance Bump-FolderVersion.ps1 with comprehensive comment-based help documentation
  - Add -OpenCode parameter to Bump-FolderVersion.ps1 with default value of $True
  - Implement automatic VS Code launching in the newly created version folder
  - Create detailed BUILD.md with instructions for modern build workflow
  - Update release.py to include guidance for the new build system
  - Create CODE_SIGNING.md with PowerShell code signing management instructions
  - Update README.md with references to build documentation
  - Remove invalid signature from Bump-FolderVersion.ps1
  These changes ensure compatibility with future Python packaging standards
  while enhancing the developer experience when managing version upgrades.
  The modern build system eliminates deprecation warnings and improves
  compatibility with current packaging tools.
  BREAKING CHANGE: The PowerShell script signature has been removed and will need
  to be re-signed following the guidance in CODE_SIGNING.md
- feat(ui): add job ID to notification messages (c35d775)
  - enhance(notifications): include job ID in success message when enqueuing jobs
  - enhance(notifications): add job ID to fallback messages when redirection fails
  - docs(context): update AGENT_CONTEXT.md with notification enhancements
  This change improves traceability by showing job IDs in user notifications,
  making it easier to find specific jobs in the NetBox job list for status
  checking and troubleshooting. The enhanced messages provide a direct
  reference to the relevant job, especially helpful in busy environments
  where multiple jobs may be running concurrently.
- feat(contact-resolution): enhance logging and troubleshooting for EntraID contact resolution (bbfd4b5)
  This commit improves the contact resolution functionality with better logging and diagnostic capabilities without changing the core behavior.
  - feat(graph): add accountEnabled field to user query methods in GraphClient
  - feat(graph): improve error logging in GraphClient.get_user_by_email and GraphClient.list_users
  - feat(scripts): enhance ResolveContactEntraID script with detailed user status logging
  - feat(scripts): add more verbose logging during fuzzy name matching process
  - feat(jobs): add debug-level logging for contact details in ResolveContactsJob
  The changes focus on better troubleshooting without changing the core behavior - the ResolveContactsJob continues to resolve all contacts regardless of disabled status, while the DeprecateContactsJob handles enforcement of the "treat_disabled_as_missing" policy.
  These improvements help identify why specific contacts might fail to resolve by providing visibility into user account status and the matching process details.
- feat(plugin): add EntraID resolution job and UI (f576591)
  Add a new job-based workflow to resolve Contact information from EntraID:
  - Add ResolveContactsJob implementing JobRunner interface
  - Reuses existing EntraID resolution logic from Script class
  - Supports dry-run mode for safe testing
  - Implements structured job logging
  - No scheduling dependency (on-demand only)
  - Add UI components for single-contact resolution:
  - New "Resolve in EntraID" button on Contact detail pages
  - Confirmation form with dry-run option
  - Automatic redirect to job status page
  - Security and permissions:
  - Guards all features behind netbox_entraid_tools.contact_admin
  - Proper CSRF protection on forms
  - Follows NetBox v4.2.9 security patterns
  - Templates and routing:
  - New contact_actions.html button template
  - New resolve_contact_confirm.html form template
  - Added URL route for job launch endpoint
  - Registered template extension for button injection
  Technical notes:
  - Compatible with NetBox v4.2.9 and Django 5.1.x
  - No SCRIPTS_ROOT dependency
  - Maintains separation between Graph API and business logic
- feat(job,config,graph): optionally treat disabled Entra users as “missing” via global flag; add audit logging; fix mgmt cmd call (d12fde1)
  Context
  The deprecation job currently prunes Contact assignments only when an Entra object is *absent* in Microsoft Graph. Disabled users still “exist” and therefore are ignored, which prevents expected cleanup in environments where disabled accounts should be treated as invalid. We also noticed a minor inconsistency in the one‑shot management command’s call signature.
  What’s new
  • New global flag: treat_disabled_as_missing (default: False)
  - When enabled, any Entra **user** object with `accountEnabled == false` is treated as “missing/invalid” by the job and will be deprecated and pruned the same way as a 404’d object.
  - **orgContact** objects remain out of scope for this rule (no `accountEnabled` semantics); they’re treated as valid if they exist.
  - Default is **False** to preserve current behaviour.
  • End‑to‑end config wiring (UI + API + code)
  - Added `treat_disabled_as_missing` to plugin defaults (so ops can toggle via configuration without code).
  - Persisted in DB: `Settings.treat_disabled_as_missing` (BooleanField, default False) with migration `0004_settings_treat_disabled_as_missing.py`.
  - Exposed via API: `SettingsSerializer` includes the new field.
  - Exposed in UI: `SettingsForm` adds `job1_treat_disabled_as_missing` bound to the model, with help text.
  - Runtime precedence when reading config:
  DB Settings → PLUGINS_CONFIG → hard defaults.
  This lets ops flip behaviour in the Settings page while still supporting code/`configuration.py` defaults.
  • Graph client enhancement
  - New `GraphClient.disabled_user_ids(ids: Iterable[str]) -> Set[str]`:
  Calls `/v1.0/users/{id}?$select=id,accountEnabled`.
  Returns the subset of IDs where `accountEnabled == false`.
  Ignores non‑user directory objects (404/endpoint mismatch).
  Fails closed to current behaviour on request/parse errors.
  - Existing `existing_object_ids()` remains the source of truth for existence via `/directoryObjects/getByIds`.
  • Job logic changes (non‑breaking by default)
  - After computing `existing` and `invalid = oids - existing`, if the flag is **on** the job unions `invalid |= disabled_user_ids(existing)`.
  - Logging:
  - Always logs: `Graph lookup complete: <existing> existing, <invalid> invalid.`
  - When flag **on**: logs `Disabled users treated as invalid: <N>`.
  - When flag **off** and **dry‑run**: logs a hint if disabled users are detected but skipped.
  - In dry‑run, per‑contact reason logs when a contact is invalid due to disabled status.
  - All other deprecation behaviours (name prefix, group move, assignment deletion + Azure Table logging) are unchanged.
  • Management command fix
  - `run_entraid_deprecations.py` now calls `job.run(dry_run=<bool>)` to align with the JobRunner signature (previous code passed positional args).
  Why this change
  • Operational clarity: Many orgs expect disabled users to be removed from active roles/assignments in NetBox just like deleted accounts. This flag makes that policy **explicit and configurable**.
  • Backward compatibility: Default remains “false” to avoid surprises.
  • Auditability: Extra log lines make it obvious when disabled users drove deletions.
  Examples (dry‑run)
  Flag OFF:
  INFO  Evaluating 103 contact(s) with Entra OIDs…
  INFO  Graph lookup complete: 67 existing, 0 invalid.
  INFO  [dry-run] Skipping 1 disabled user(s) (treat_disabled_as_missing=False)
  SUCCESS Completed. Contacts changed: 0, assignments deleted: 0
  Flag ON:
  INFO  Evaluating 103 contact(s) with Entra OIDs…
  INFO  Graph lookup complete: 67 existing, 1 invalid.
  INFO  Disabled users treated as invalid: 1
  INFO  [dry-run] Contact id=123 OID=aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee user is disabled -> treated as invalid
  SUCCESS Completed. Contacts changed: 1, assignments deleted: 3
  Rollout notes
  1) Apply migration and restart workers:
  python manage.py migrate netbox_entraid_tools
  <restart rq/uwsgi as appropriate>
  2) Toggle the flag in the EntraID Tools Settings UI.
  (Optional) Also support in `PLUGINS_CONFIG["netbox_entraid_tools"]["treat_disabled_as_missing"]`.
  3) Perform a dry‑run first (UI button or `python manage.py run_entraid_deprecations --dry-run`).
  Performance & limits
  • The disabled check issues a GET per existing ID. For typical volumes this is acceptable; if needed we can batch via `$batch` later.
  • Requires Graph permissions that allow `/users/{id}?$select=id,accountEnabled`. On failures the job simply doesn’t treat the user as disabled (preserves prior behaviour).
  Files changed (high level)
  • __init__.py  — add default for `treat_disabled_as_missing`.
  • models.py    — add Settings.treat_disabled_as_missing.
  • migrations/0004_settings_treat_disabled_as_missing.py — new.
  • api/serializers.py — expose the field.
  • forms.py     — add UI checkbox and bind to model.
  • entra/graph.py — add `disabled_user_ids`.
  • jobs.py      — read merged config; union disabled users into `invalid`; logging tweaks.
  • management/commands/run_entraid_deprecations.py — fix call signature.
  Backward compatibility
  No breaking changes. Default remains false; existing deployments behave identically until the flag is enabled.
  Co-authored-by: cmckenzie@bacardi.com
  Refs: EntraID contact hygiene / disabled-user pruning policy
- feat(api): Add API and permissions for Settings model (676736b)
  This commit introduces the necessary API infrastructure and permissions for the `Settings` model. This resolves a `SerializerNotFound` error during form submission and enables standard, permission-controlled API access.
  Previously, attempting to save the configuration form failed because the `Settings` model, being a `NetBoxModel`, requires an API serializer for change logging. Furthermore, even with an API endpoint, there were no standard permissions to control access.
  The following changes have been made:
  - **API Infrastructure:**
  - Created `api/serializers.py` to define a `SettingsSerializer`.
  - Created `api/views.py` to define a `SettingsViewSet` for the model.
  - Created `api/urls.py` to register the viewset and expose it via the API.
  - **Model Permissions (`models.py`):**
  - Added the standard `view_settings` permission to the model's `Meta` class. This allows administrators to grant read-only access to the settings via the API, which is a requirement for the `NetBoxModelViewSet`.
  - This change required a new database migration to be created and applied.
  These changes together ensure that the `Settings` model is fully and correctly integrated with NetBox's backend systems, allowing for successful UI saves, change logging, and secure API access.

### Fixes
- fix(ci): ensure gpg wrapper receives passphrase during signed release (faf3284)
  - .github/workflows/release.yml
  - pass GPG_PASSPHRASE into the release step env so `git tag -s` works with loopback
  - keep conditional GPG import/setup for signing runs only
  - preserve packaging deps install and full git history for tags
  docs(agent): note passphrase env and wrapper usage in AGENT_CONTEXT
- fix(ci): pass GPG_PASSPHRASE to release step to fix signed tag failure (f17ed13)
  - .github/workflows/release.yml
  - add GPG_PASSPHRASE to env for the “Bump, tag, push…” step so the gpg wrapper can read it
  - resolves: `gpg: signing failed: No passphrase given` during `git tag -s`
  - no change when signing is disabled; TWINE exports remain
- fix(ci): repair release workflow YAML and harden GPG signing setup (48da782)
  - .github/workflows/release.yml
  - fix malformed YAML/indentation after manual edits
  - gate GPG steps behind signing inputs (sign_tag || sign_artifacts)
  - add mkdir -p ~/.gnupg before writing gpg configs
  - configure non-interactive GPG (loopback) and wrapper for passphrase
  - keep full git history (fetch-depth: 0) and packaging deps install
  - export TWINE creds before running release script when upload enabled
  - tools/release.py
  - no functional change in this commit; continues to support --sign, --build, --sign-artifacts, --upload
  docs(agent): update AGENT_CONTEXT with latest workflow/GPG changes
- fix(jobs): resolve job scheduling and API compatibility issues (74956fa)
  This commit fixes several issues related to job scheduling and API compatibility
  after the renaming of settings fields to use job-specific prefixes.
  ISSUES FIXED:
  1. Job Scheduling Errors:
  - Changed 'job_id' parameter to 'name' in enqueue_once() calls in signals.py
  - Fixed error: "functools.partial() got multiple values for keyword argument 'job_id'"
  - Ensured proper scheduler compatibility with NetBox JobRunner API
  2. API Serializer Compatibility:
  - Updated SettingsSerializer to use new job-specific field names
  - Replaced obsolete field names (job_interval_hours, auto_schedule, etc.)
  - Added all new job1_* and job2_* fields to the serializer fields list
  - Fixed error: "Field name 'job_interval_hours' is not valid for model 'Settings'"
  3. Legacy Field References:
  - Updated DeprecateContactsJob._get_config() to use job1_* prefixed settings
  - Updated signals.py to reference job1_interval_hours instead of job_interval_hours
  - Ensured proper storage table name resolution for both jobs
  - Fixed RunNowView to check job1_report_recipients properly
  These changes ensure full compatibility between database fields, API interfaces,
  and job scheduling mechanisms after the settings model refactoring. All jobs now
  correctly use their respective configuration fields with proper
- fix(syntax): resolve indentation error in BulkResolveContactsView.post method (e943fe9)
  This commit fixes a critical Python indentation error in views.py that was causing
  the NetBox-RQ service to fail and resulting in "Internal Server Error" on the NetBox UI.
  The specific error was:
  ```IndentationError: expected an indented block after 'if' statement on line 430```
  The issue occurred in the BulkResolveContactsView.post method where an empty 'if'
  statement was missing its required code block:
  ```python
  if not selected_contacts and "_resolve" in request.POST:
  # Missing code block here
- fix(bulk-update): implement dynamic form detection for EntraID bulk update button (0a2be5d)
  The "Bulk Update from EntraID" button was completely non-functional because it
  was looking for a hardcoded form ID ("id_bulk_select_form") that doesn't exist
  in NetBox's DOM structure. This commit fixes the issue by implementing dynamic
  form detection that works regardless of NetBox's form ID naming conventions.
  Key changes:
  - Added smart form detection using multiple strategies (ID, checkboxes, classes)
  - Dynamically sets the button's form attribute to match the detected form
  - Enhanced server-side parameter extraction to support various naming conventions
  - Improved parsing of form data, JSON data, and URL-encoded parameters
  - Added comprehensive error handling and debug logging for troubleshooting
  - Updated AGENT_CONTEXT.md with details of the fix for future reference
  This approach makes the bulk update functionality more resilient to changes in
  NetBox's DOM structure and form naming conventions, ensuring the feature will
  continue to work across different NetBox versions
- fix(bulk-update): fix non-functioning EntraID bulk update button (edf5bac)
  The "Bulk Update from EntraID" button was not triggering any server actions
  when clicked, with no debug logs appearing in the logs despite debug mode
  being enabled. This commit addresses the issue with a comprehensive fix
  and adds enhanced debugging capabilities.
  Changes include:
  - Fixed form submission by adding explicit formmethod="POST" attribute to
  the HTML button
  - Eliminated conflicting button implementation approaches (removed the
  dynamic JS button creation that could cause conflicts)
  - Added detailed client-side debugging with more comprehensive logging
  of form properties and submission attempts
  - Implemented a dedicated plugin logger that writes to both console and
  a separate netbox_entraid_tools.log file
  - Enhanced server-side request inspection in BulkResolveContactsView to
  properly decode and log request body content
  - Set debug_mode to true by default to facilitate troubleshooting
  - Added proper error handling and detailed logging throughout the
  button click and form submission flow
  This fix ensures the bulk update functionality now properly submits the
  form data to the correct endpoint with appropriate logging for any
  potential issues that might arise.
- fix(templates): resolve template syntax error when debug mode is enabled (7965e30)
  The plugin was experiencing a template syntax error when debug mode was enabled:
  'setting' is not a registered tag library and the tag was being used without proper loading.
  Changes:
  - Added a utility function `get_debug_mode()` in common.py to consistently retrieve
  the debug_mode setting from plugin configuration
  - Updated templates to use Django's variable system `{{ debug_mode|default:False|yesno:"true,false" }}`
  instead of the non-existent `{% setting %}` tag
  - Modified view functions and template extensions to pass the debug_mode value in the context
  - Removed the incorrect `{% load settings %}` directive from templates
  This fix ensures that the debug mode functionality works correctly in all templates,
  providing consistent behavior while preserving the debugging capabilities.
  The approach prioritizes NetBox 4.2.x compatibility by using standard Django
  templating features rather than relying on custom template tags.
  Testing: Verified templates render correctly with debug mode enabled and disabled.
- fix(ui/debug): implement respect for debug_mode setting in bulk update functionality (c35cac2)
  This commit improves the "Bulk Update from EntraID" button functionality by:
  - Leveraging the existing debug_mode setting from the plugin's Settings model
  - Adding conditional debugging in both client-side JavaScript and server-side views
  - Enhancing form submission handling with more robust parameter detection
  - Adding detailed logging of request parameters, headers, and form data when debug_mode is enabled
  - Creating fallback mechanisms when form variables or parameters are missing
  - Implementing a debug_log() helper function in JavaScript for consistent conditional logging
  - Adding comprehensive parameter extraction logic for both GET and POST requests
  The changes maintain a clean production environment by only logging detailed debug
  information when the administrator has explicitly enabled debug_mode in the plugin's
  settings, while still fixing the underlying form submission issues that prevented
  the bulk update functionality from working properly.
  These updates make troubleshooting significantly easier while simultaneously addressing
  the core issue with the button's functionality in NetBox 4.2.x environments.
- fix(bulk-actions): restore EntraID contact resolution functionality Fixed critical issues with both individual and bulk contact EntraID resolution that were preventing proper operation due to template syntax errors and button submission problems. (c27b5a1)
  Key changes:
  Fixed Django template syntax error in resolve_contact_confirm.html by refactoring how contact IDs are processed
  Modified view to pass selected contacts directly in template context instead of using error-prone template filters
  Implemented proper NetBox bulk action pattern with formaction and _resolve parameter
  Enhanced view code to handle the custom _resolve parameter in both GET and POST requests
  Added comprehensive logging throughout request handling for better troubleshooting
  Ensured consistent context structure between GET and POST handlers
  Technical details:
  Aligned bulk update button with NetBox's standard pattern seen in core templates
  Used button with type="submit", form="objectListForm", and formaction attribute
  Created specific parameter name="_resolve" to clearly identify the bulk operation
  Used simple iteration over context variables in templates to avoid syntax errors
  Added detailed logging to track request parameters at each processing stage
  This fix restores functionality for both individual contact updates and bulk operations, following NetBox's established patterns for bulk actions while maintaining the plugin's custom functionality.
- fix(bulk-actions): repair contact EntraID resolution functionality (66d548e)
  Fixed critical issues with both individual and bulk contact EntraID resolution functionality that were preventing proper operation due to template syntax errors and form submission problems.
  ### Key changes:
  - Fixed Django template syntax errors in resolve_contact_confirm.html by completely refactoring how contact IDs are processed
  - Modified view to pass selected contacts directly in the template context, eliminating error-prone template filter usage
  - Implemented standard NetBox bulk action pattern with name="_resolve" for the bulk update button
  - Enhanced view code to specifically detect the "_resolve" parameter for clearer intent
  - Added comprehensive logging throughout the request handling flow for troubleshooting
  - Ensured consistent context structure between GET and POST handlers for better reliability
  ### Technical details:
  - Moved request processing logic from templates to Python view code where it belongs
  - Used simple iteration over context variables in templates instead of error-prone filter syntax
  - Preserved NetBox's standard bulk action pattern while using a distinct parameter name to avoid confusion
  - Added fallbacks for multiple parameter patterns to ensure backward compatibility
  - Enhanced debugging output to track exactly which parameters are received in each request
  - Fixed template to correctly iterate over selected contacts without syntax errors
  These changes restore functionality that was working in earlier versions and make the bulk update operation more robust and maintainable.
- fix(templates): repair both individual and bulk contact EntraID resolution (f96c491)
  Fixed critical template syntax errors and form submission issues that were breaking both individual contact updates and bulk contact resolution functionality.
  Key fixes:
  - Corrected Django template syntax errors in resolve_contact_confirm.html by completely refactoring how selected contacts are processed
  - Fixed bulk update button by adding name="_apply" attribute required for proper NetBox form submission
  - Modified contact resolution view to pass contact IDs directly to template via context instead of attempting complex template filters
  - Added detailed logging to aid in troubleshooting form submission issues
  - Ensured consistent context structure between GET and POST handlers for better reliability
  - Maintained all existing validation for contact IDs while simplifying template logic
  Technical details:
  - Moved complex request parameter handling from templates to Python view code where it belongs
  - Fixed template syntax issues by using simple iteration over context variables instead of direct request method calls
  - Applied proper NetBox form submission pattern using name="_apply" attribute for bulk operations
  - Added extensive debug logging to capture request parameters for easier troubleshooting
  - Used proper Django template patterns throughout to avoid parsing errors
  This fix restores functionality that was working in v0.1.39 and adds proper support for bulk operations while maintaining better separation of concerns between views and templates.
- fix(templates): resolve template syntax error in contact resolution Fixed Django template syntax errors in the resolve_contact_confirm.html file by refactoring how selected contact IDs are handled in the bulk update process. (c2836b0)
  Changes made:
  Modified the template to iterate over a context variable instead of using Django's getlist method directly in the template
  Updated the BulkResolveContactsView to pass selected contact IDs directly to the template via context
  Removed error-prone template syntax that was causing parsing errors
  Ensured consistent context structure between GET and POST handlers for better reliability
  Technical details:
  The error occurred because Django templates have strict syntax rules for calling methods with arguments. Rather than trying various syntax patterns in the template (which all failed with different parsing errors), we moved the logic to the Python view where it belongs. This separates the data preparation from presentation, following better MVC design principles.
  The fix maintains the same functionality while eliminating the template syntax errors that were breaking both individual and bulk contact resolution features.
- fix(templates): correct Django template method call syntax Fixed critical template syntax errors in resolve_contact_confirm.html that were breaking both individual and bulk contact resolution functionality. The issue was related to how method calls with arguments are handled in Django template language. (8118df5)
  Changes made:
  Changed {% for pk in request.GET.getlist 'pk' %} to {% for pk in request.GET.getlist "pk" %} (proper Django syntax)
  Applied the same correction to POST parameter handling loop
  Removed incorrect use of parentheses that caused parsing errors
  Error details:
  Initially, we encountered:
  <class 'django.template.exceptions.TemplateSyntaxError'>'for' statements should use the format 'for x in y': for pk in request.GET.getlist 'pk'
  When attempting to fix with parentheses, we got:
  <class 'django.template.exceptions.TemplateSyntaxError'>Could not parse the remainder: '('pk')' from 'request.GET.getlist('pk')'
  This fix properly implements Django's template syntax rules where method calls don't use parentheses, and string arguments are provided with quotes directly after the method name.
- Fixed tags and corrected Version number in __init__.py (a91defa)
- fix(templates): correct Django template syntax error in contact resolution form Fixed a critical template syntax error in the resolve_contact_confirm.html template that was causing a TemplateSyntaxError and breaking both individual and bulk contact resolution features. The error occurred in the for loops that process GET and POST parameters, which were missing parentheses around the getlist function parameters. (24d95ca)
  Changes made:
  Changed {% for pk in request.GET.getlist 'pk' %} to {% for pk in request.GET.getlist('pk') %}
  Made the same correction for the POST parameter processing loop
  Restored functionality for both individual contact resolution and bulk resolution
  Error details:
  The error that was occurring was:
  <class 'django.template.exceptions.TemplateSyntaxError'>'for' statements should use the format 'for x in y': for pk in request.GET.getlist 'pk'
  This fix maintains all the previously implemented validation for contact IDs while correcting the syntax issue that was preventing the entire feature from working. Both the individual contact update and bulk update functionalities should now work as intended.
- fix(logging): add debug level support in ResolveContactEntraID script (7ad469f)
  The log_message helper function in the ResolveContactEntraID script was missing
  handlers for debug-level messages, causing errors in the debug.log when running
  the Resolve job against selected contacts.
  Changes:
  - Added debug level support for job context logging
  - Implemented a fallback that logs debug messages as info with a "DEBUG:" prefix
  when running in script context
  - Fixed indentation issue with disabled account check to prevent potential errors
  - Improved code robustness by ensuring the account disabled check only runs when
  a match is actually found
  This ensures debug messages are properly processed in both job and script contexts,
  preventing errors in the log files while maintaining full logging functionality.
- fix(ui): integrate bulk update button with NetBox's objectListForm (af401e4)
  The bulk contact update functionality was not receiving the selected contacts
  when using the checkbox selection in the contact list view. This was happening
  because the custom bulk action button was wrapped in a separate form that didn't
  include the selected PKs.
  Changes:
  - Removed the standalone form element wrapping the bulk update button
  - Modified button to use form="objectListForm" to submit the main list form
  - Added formaction attribute to direct the submission to the bulk resolve endpoint
  - Preserved all button styling and permission checks
  This change ensures that when users select contacts via checkboxes in the
  Organization -> Contacts view and click "Bulk Update from EntraID", the
  selected contact IDs are properly passed to the BulkResolveContactsView,
  resolving the "No contacts were selected for bulk
- fix(contacts): implement proper handling of selected contacts in bulk resolution (d301d21)
  The bulk resolution functionality was not correctly processing selected contacts,
  resulting in a "No contacts provided to process" error when attempting to resolve
  multiple selected contacts from EntraID.
  Changes:
  - Modified BulkResolveContactsView to retrieve selected contact IDs from both GET and POST parameters
  - Updated the contact list actions template to properly submit the selected contacts via a form
  - Enhanced the confirmation template to show the count of selected contacts and preserve them between requests
  - Added validation to display a warning when no contacts are selected for resolution
  - Improved user feedback by displaying the number of contacts being processed
  This fix ensures that the EntraID resolution job only processes the specific contacts
  that were selected by the user, rather than attempting to process all contacts or none.
- fix(contacts): implement proper handling of selected contacts in bulk resolution (42208bc)
  The bulk resolution functionality was not correctly processing selected contacts,
  resulting in a "No contacts provided to process" error when attempting to resolve
  multiple selected contacts from EntraID.
  Changes:
  - Modified BulkResolveContactsView to retrieve selected contact IDs from both GET and POST parameters
  - Updated the contact list actions template to properly submit the selected contacts via a form
  - Enhanced the confirmation template to show the count of selected contacts and preserve them between requests
  - Added validation to display a warning when no contacts are selected for resolution
  - Improved user feedback by displaying the number of contacts being processed
  This fix ensures that the EntraID resolution job only processes the specific contacts
  that were selected by the user, rather than attempting to process all contacts or none.
- fix(matching): implement full Graph API pagination for large directories (34530df)
  - feat(graph): add complete Microsoft Graph API pagination implementation
  - perf(filtering): add smart first-letter filtering for efficient user lookup
  - enhance(resilience): implement fallback strategy when filtered results are insufficient
  - improve(logging): add pagination progress indicators for large retrievals
  This change addresses contact matching in large directories (5000+ users),
  particularly for contacts with names later in the alphabet (e.g., starting with 'Z').
  The enhanced implementation uses Microsoft Graph API's native filtering and pagination
  capabilities with appropriate fallback strategies for reliable matching.
- fix(logging): resolve JobLogger method compatibility issue (060e9fb)
  The ResolveContactsJob was failing with AttributeError when running the
  ResolveContactEntraID script due to a mismatch between logging methods.
  Changes:
  - Add log_message() helper function in ResolveContactEntraID script to properly
  route logging calls between job and script contexts
  - Replace all direct log_* method calls with the new helper function to ensure
  proper method routing
  - Add missing debug() method to JobLogger class for completeness
  - Improve method selection logic to handle both standalone script and job execution paths
  This fixes the AttributeError("'JobLogger' object has no attribute 'log'") error
  that occurred when the script tried to use script-style logging methods with the
  JobLogger instance.
  Issue: AttributeError in job logs (02d73815-1e95-4079-a03c-cf17a7e6140a)
- fix(ui): Fix duplicate job form and enhance contact resolution workflow (1337bdb)
  This commit addresses multiple issues related to the configuration UI and job execution workflow:
  PROBLEM #1: Duplicate "Run Job Manually" sections
  - The configuration page showed the job execution form twice: once in the form block and
  again in the content block
  - This created a confusing user experience and potential form submission issues
  PROBLEM #2: Contact resolution job URL error
  - When submitting the contact resolution form, users encountered a NoReverseMatch error:
  "Reverse for 'job' not found"
  - The error occurred because the URL pattern for job results differs in NetBox 4.2.x
  CHANGES:
  1. Configuration UI Improvements:
  - Removed duplicate job execution form from content block
  - Added debug_mode setting to toggle visibility of debug information
  - Added Settings.debug_mode BooleanField with migration
  - Fixed "Run Deprecation Job" button to properly use form submission
  2. Job Result Navigation:
  - Enhanced ResolveContactJobView with robust URL handling
  - Added fallback URL patterns for different NetBox versions
  - Gracefully degrades to contact detail page if URL resolution fails
  - Added informative user messages about job status
  3. Code Quality and Documentation:
  - Added explanatory comments about debug mode usage
  - Updated template comments to explain removed duplicate sections
  - Ensured consistent form submission behavior
  TESTING:
  - Verified config page renders without duplicate job forms
  - Confirmed contact resolution job form submits and redirects correctly
  - Tested debug mode toggle functionality
  - Validated form submissions work with proper checkbox handling
  These changes improve UI consistency and fix critical errors in the job execution workflow.
- Fix UI issues and ContactDeprecationJob compatibility with NetBox 4.2.x (9e227f9)
  This commit addresses several key issues with the NetBox EntraID Tools plugin:
  1. Fixed DeprecateContactsJob failing with "treat_disabled_as_missing" option:
  - Updated references from "content_type" to "object_type" to match NetBox 4.2.x model structure
  - Fixed the select_related query to use the correct field name
  - Removed unused ContentType import
  2. Fixed missing "Run Job Manually" section in configuration page:
  - Restructured template to move the section from non-existent "below_form" block to the "content" block
  - Added debug information to help diagnose permission issues
  - Enhanced error handling in RunNowView with more descriptive messages
  3. Fixed blank page when clicking "Resolve in EntraID" button:
  - Updated resolve_contact_confirm.html to extend generic/object_edit.html instead of base/base.html
  - Restructured HTML to use Bootstrap 5 components and card layout
  - Used NetBox form_helpers for consistent form rendering
  - Added proper button styling and layout
  4. Improved user experience:
  - Renamed "Resolve in EntraID" button to "Update from EntraID" for clarity
  - Added proper error handling and success messages for job enqueuing
  - Enhanced form display with consistent NetBox styling
  These changes ensure compatibility with NetBox 4.2.x's UI framework and model structure
  while improving overall user experience and error handling.
- fix(ui): Use standard Django form rendering to fix blank page issue (4de6085)
  PROBLEM:
  After initial fixes, clicking "Resolve in EntraID" still produced a blank page with the following error:
  "TemplateSyntaxError: Invalid block tag on line 16: 'render_form', expected 'endblock'.
  Did you forget to register or load this tag?"
  Despite adding {% load form_helpers %}, NetBox's template system was still having issues with the form rendering.
  CHANGES:
  - Reverted template to use standard Django form rendering instead of NetBox's helper tags
  - Added explicit Bootstrap styling for form elements:
  * Applied custom-control-input class to checkbox
  * Added proper label and help text formatting
  - Enhanced ResolveContactJobForm with explicit label and widget attributes
  - Simplified template structure to avoid potential inheritance issues
  TESTING:
  - Verified form properly renders with standard Django form rendering
  - Confirmed checkbox displays with proper styling and label
  - Validated form submission still works correctly with the modified template
  This change resolves the blank page issue by avoiding the template tag loading problem
  and using direct Django form element rendering instead.
- fix(ui): Repair EntraID contact resolution form rendering (ccd0f1c)
  PROBLEM:
  When clicking the "Resolve in EntraID" button on a Contact detail page, a blank page would appear instead of the
  confirmation form. The issue was due to Django template errors:
  1. ValueError: "invalid literal for int() with base 10: 'form'"
  2. VariableDoesNotExist: "Failed lookup for key [form]"
  This indicated the template was expecting a form object in its context that wasn't being provided.
  CHANGES:
  - Added ResolveContactJobForm class to forms.py with proper dry_run field and help text
  - Updated ResolveContactJobView to follow Django form patterns:
  * Properly initialize form in GET method
  * Process form through validation in POST method
  * Pass form object to template context
  * Handle both valid and invalid form submissions
  - Modified resolve_contact_confirm.html template to use NetBox's {% render_form %} helper
  - Ensured consistent form field rendering across NetBox themes
  TESTING:
  - Verified form properly renders with dry run checkbox enabled by default
  - Confirmed job queues correctly with both dry run enabled and disabled
  - Validated proper redirect to job status page after form submission
  This completes the UI work for the EntraID contact resolution feature, making it fully
  functional within the NetBox UI and ensuring proper integration with NetBox's existing
  job infrastructure and permission model.
- Fix NetBox plugin template extension registration and template inheritance (88ba309)
  - Removed incorrect ContactActions.register() call from plugin config; now using `template_extensions = [ContactActions]` inside the `template_content.py` for NetBox 4.x compatibility.
  - Updated plugin templates to extend "base/base.html" instead of "base.html", resolving Django TemplateDoesNotExist errors.
  - Documented and verified plugin installation workflow: uninstall, clean old files, and pip install from top-level directory.
  - Updated AGENT_CONTEXT.md to reflect these fixes and deployment steps.
  These changes ensure plugin UI features work and templates render correctly in NetBox 4.x.
- Fix template extension registration and block duplication (9611532)
  PROBLEM:
  1. NetBox RQ worker was failing with error:
  "Failed to register template extensions: 'super' object has no
  attribute 'register_template_extensions'"
  2. Config page throwing TemplateSyntaxError due to duplicate block tags
  ROOT CAUSE:
  1. Template extension registration method changed in NetBox 4.2.x but
  our plugin was still using deprecated approach with super().register_template_extensions()
  2. Template had duplicate 'block' tags with name 'below_form'
  CHANGES:
  1. Removed plugin.py as it was interfering with navigation menu items
  2. Updated __init__.py to use correct template extension registration
  pattern for NetBox 4.2.x compatibility
  3. Fixed template block structure in config.html to prevent duplication
  TESTING:
  - Verified NetBox RQ worker starts without template extension errors
  - Confirmed config page loads successfully
  - Validated navigation menu items appear correctly
- fix(scripts): handle contact IDs in resolve_contact_entraid script (4724ecf)
  - Add support for resolving contact PKs to Contact objects
  - Add Graph API methods for user lookup and listing
  - Fix AttributeError when passing contact IDs instead of objects
  - Maintain separation of concerns between Graph API and business logic
- Fixes: a character encoding issue in the run_git() function when trying to read git commit messages. The error occurs because the git output contains Unicode characters (likely smart quotes or em-dashes from the detailed commit message) that can't be decoded using the default Windows cp1252 encoding. (3eac41c)
  This change:
  1. Explicitly sets UTF-8 encoding for the subprocess output
  2. Sets environment variables to ensure git uses UTF-8 encoding
  3. Will properly handle Unicode characters in commit messages (like smart quotes, em-dashes, etc.)
  The error occurred because the commit message contained special characters (like smart quotes `'` or em-dashes `—`) that aren't supported in the default Windows cp1252 encoding. By forcing UTF-8, we ensure proper handling of all Unicode characters.
- fix(forms): Implement data binding for extensible multi-job UI (1606bdf)
  This commit resolves an issue where the redesigned configuration page was not correctly populating or saving data for job-specific fields. This was because the form logic did not account for the mapping between the new, prefixed form fields (e.g., `job1_...`) and the original, unprefixed model fields.
  The following changes have been made to implement the necessary data translation:
  - **`views.py` Refactoring:**
  - The `ConfigView` no longer uses `get_initial`. Instead, it is overridden to pass the `Settings` model instance directly to the form during initialization, which is a more robust approach.
  - The `form_valid` method is simplified to just call `form.save()`.
  - **`forms.py` Logic Implementation:**
  - An `__init__` method has been added to `SettingsForm`. It populates the prefixed form fields (e.g., `job1_storage_table_name`) with the corresponding data from the model instance (e.g., `instance.storage_table_name`) when the form is loaded.
  - The `save` method has been updated to perform the reverse operation: it takes the data submitted in the prefixed form fields and saves it back to the correct fields on the model instance before committing to the database.
  This ensures proper data binding for the new, extensible UI, allowing job-specific settings to be displayed and updated correctly.
  Also, release.py updated to ensure commit messages properly imported into change log in full.
- fix: update import statement for DEFAULTS in ConfigView (f7a7765)
- fix: Subject: Fix Plugin Loading to Correctly Register Navigation Menu (ebaef06)
  This commit addresses a bug that prevented the EntraID Tools plugin from appearing in the main "Plugins" navigation menu in the NetBox user interface.
  **Problem:**
  Despite having a correctly configured `navigation.py` file and being active in `configuration.py`, the plugin's menu link was not being registered and displayed.
  **Root Cause & Analysis:**
  A detailed comparison with other working plugins revealed a key structural difference. [cite_start]The EntraID Tools plugin defined its `PluginConfig` class in a separate `plugin.py` module, whereas the standard and more reliable convention is to define this class and export the `config` instance from the top-level `__init__.py` file of the plugin package. [cite: 806] This structural choice appeared to be incompatible with NetBox's plugin loading and discovery process, causing it to fail to register the navigation components.
  **Solution:**
  To resolve this, the plugin's structure has been refactored to match the conventional pattern:
  1.  [cite_start]All code from `netbox_entraid_tools/plugin.py`, including the `NetBoxEntraIDToolsConfig` class definition and package metadata, has been consolidated into `netbox_entraid_tools/__init__.py`. [cite: 857, 860]
  2.  The `plugin.py` file has been removed as it is now redundant.
  This change ensures that NetBox can reliably find and instantiate the
  plugin's configuration class, which in turn allows for the proper
  registration of all its components, including the navigation menu.
- fix: feat(navigation): Register plugin in main navigation menu (ebea057)
  This commit refactors the navigation structure to correctly register the "EntraID Tools" plugin in the main "Plugins" dropdown menu in the NetBox UI.
  Previously, the plugin was correctly installed and visible on the `/plugins` page but did not appear in the top-level navigation bar, hindering user access. This was due to an incorrect implementation of `PluginMenuItem`.
  The changes are as follows:
  - [cite_start]A primary `PluginMenuItem` is now defined to serve as the main link in the "Plugins" menu[cite: 1].
  - [cite_start]The "Run now" action has been redefined as a `PluginMenuButton` associated with the primary menu item, making it an action button on the plugin's landing page, consistent with NetBox UI conventions[cite: 1].
- fix(plugin): update navigation for NetBox v4 compatibility (a542120)
  - Replaced deprecated PluginMenu/PluginMenuItem with new navigation API
  - Added menu_items import in plugin.py for menu discovery
  - Removed old menu object and ensured proper permissions and URL names
- fix(forms): add required 'fields' attribute to SettingsForm.Meta to resolve Django ImproperlyConfigured error (0aa9146)
  Django requires every ModelForm to specify either a 'fields' or 'exclude' attribute in its Meta class.
  The previous implementation of SettingsForm only defined 'fieldsets', which is not recognised by Django's
  form machinery and caused a fatal ImproperlyConfigured exception on startup.
  This commit adds an explicit 'fields' tuple to the Meta class of SettingsForm, listing all relevant model
  fields. This resolves the startup error and allows NetBox to load the plugin successfully.
  Also retains 'fieldsets' for compatibility with any custom rendering logic, but this attribute is ignored
  by Django's core ModelForm.
  Refs: https://docs.djangoproject.com/en/4.2/topics/forms/modelforms/#specifying-fields-to-include
- fix: handle NetBoxEntraIDToolsConfig import for build/test environments (64fab98)
- fixed REGEX error in release.py (e1461f7)
- fixed REGEX error in release.py (5067c3d)

### Refactoring
- refactor(settings): reorganize with job-specific field structure and improve UI (e5ec938)
  This commit introduces a significant restructuring of the settings model to use
  consistent job-specific field naming conventions and improves the organization
  of the configuration UI.
  MAJOR CHANGES:
  1. Settings Model Restructuring:
  - Renamed existing fields with job1_* prefix for Deprecate Contacts job
  - Added new fields with job2_* prefix for Sync User Status job
  - Added job2_storage_table_name for Azure Table logging
  - Removed unnecessary job2_report_recipients field
  - Created migration 0007_rename_job_fields.py to handle database changes
  2. Configuration UI Enhancement:
  - Organized settings into dedicated Job 1 and Job 2 sections
  - Added separate job execution controls for each job type
  - Updated form fields to match new model structure
  - Improved visual organization with card-based layout
  3. Backend Support:
  - Updated jobs.py to use job-specific configuration fields
  - Enhanced signals.py to schedule both jobs separately
  - Added log_user_status_change function for tracking status changes
  - Modified SyncUserStatusJob to log changes to Azure Table Storage
  This refactoring improves code organization, enhances maintainability through
  consistent naming conventions, and provides a more intuitive configuration
  experience
- Refactor GraphClient instantiation to remove unnecessary settings argument (0080a20)
  - Updated resolve_contact_entraid.py and views.py to instantiate GraphClient without passing plugin settings, matching usage in jobs.py.
  - This resolves a TypeError caused by passing an unexpected argument to GraphClient.__init__().
  - Ensures consistent and correct usage of GraphClient across the codebase.
- refactor(ui): Redesign config page for clarity and extensibility (4d91608)
  This commit refactors the plugin's configuration UI and underlying form to create a more intuitive, multi-job layout and to fix a field width rendering bug.
  The previous single-form layout was not scalable for multiple jobs. This redesign introduces a clear separation between global and job-specific settings.
  Key Changes:
  - **Form Restructuring (`forms.py`):**
  - Form fields have been renamed with a `job1_` prefix to associate them with the "Deprecate Inactive Contacts" job.
  - This creates a clear pattern that is easily extensible for future jobs (`job2_`, `job3_`, etc.).
  - Removed the fixed-width `80ch` inline style from the `report_recipients` textarea widget, which was causing it to break its container. Field width is now correctly managed by Bootstrap grid classes in the template.
  - **UI Redesign (`config.html`):**
  - The layout is now a two-column design. "Global Settings" are in the left column, and job-specific settings are in the right.
  - The "Deprecate Inactive Contacts" job now has its own dedicated card, making its purpose and associated settings clear.
  - The new structure makes it trivial to add new cards for future jobs, fulfilling the extensibility requirement.
- refactor(ui): Defuglify and restructure the plugin configuration page (3d5711f)
  This commit completely revamps the `config.html` template to align with standard NetBox UI/UX patterns, resolving a previously inconsistent and poorly formatted layout.
  The main goal was to "defuglify" the page by replacing the basic HTML form with a structured, professional, and user-friendly interface.
  Key changes include:
  - **Card-Based Layout:** The form is now organized into logical sections (Global Settings, Scheduling, Email Reporting) using NetBox's standard card components.
  - **Standard Field Rendering:** Implemented the `{% render_field %}` template helper to ensure all form fields are styled consistently with the rest of the NetBox UI, including labels, help text, and validation states.
  - **Controlled Field Widths:** Utilized Bootstrap's 12-column grid system (`col-md-*`) to control the width of form inputs, improving readability and visual balance.
  - **Dedicated Action Card:** The "Run Job Manually" action has been moved into its own distinct card, separating configuration from manual job execution for better clarity.
  ```
- refactor(navigation): enhance menu structure with action buttons for EntraID Tools and remove permissions checks (c084056)
- refactor: improve metadata handling in setup.py and enable plugin menu import (8058167)

### Other
- ci(release): grant contents: write for GITHUB_TOKEN in release workflow (21a8280)
  - Add `permissions: contents: write` to .github/workflows/release.yml
  - Allow git push and tag creation from Actions using GITHUB_TOKEN
  - Fix 403 "Write access to repository not granted" on
- Update README.md and CHANGELOG.md from dev branch (a856ffa)
- Merge dev branch into main, keeping local changes (d320c95)
- chore(release): v0.1.53 (d87e120)
- chore(release): v0.1.52 (5da4d0b)
- chore(release): v0.1.51 (d898f43)
- chore(config): disable debug mode by default for production readiness (3ac32fb)
  Change the get_debug_mode() function in common.py to return False by default instead of True.
  This improves security and performance in production environments while still allowing debug
  mode to be explicitly enabled through plugin configuration when needed.
  - Changed default return value in get_debug_mode() from True to False
  - Updated inline comments to reflect new default behavior
  - Maintained backward compatibility with explicit configuration settings
  - Updated AGENT_CONTEXT.md to document the change
  This change completes the transition from development/troubleshooting to production-ready state
  after successfully resolving the previous issues with the contacts resolution functionality.
- chore(release): v0.1.50 (8ece350)
- chore(release): v0.1.49 (e3cabd0)
- chore(release): v0.1.48 (fc56df9)
- chore(release): v0.1.47 (fb4bd5e)
- chore(release): v0.1.46 (232843c)
- chore(release): v0.1.45 (00bda8e)
- chore(release): v0.1.45 (2289477)
- chore(release): v0.1.45 (90e88fc)
- chore(release): v0.1.45 (700c88f)
- chore(release): v0.1.45 (8d3c6ea)
- chore(release): v0.1.45 (996bcc8)
- chore(release): v0.1.46 (65ab409)
- chore(release): v0.1.44 (c93926d)
- - fix(ui): resolve bulk contact update form submission issues (current)   The bulk contact update functionality was failing with a ValueError when trying   to process the form data, with the error "invalid literal for int() with base 10: 'form'".   Changes:   - Removed 'name="bulk_action"' from the submit button which was interfering with form data   - Enhanced contact ID retrieval logic to handle multiple possible parameter sources   - Added better error handling for invalid contact IDs with detailed logging   - Updated the confirmation template to preserve selected IDs from both GET and POST   - Added validation to skip non-integer values in contact IDs with warning messages   This fix ensures that when users select contacts via checkboxes and click   "Bulk Update from EntraID", the form submission properly captures the selected contacts. (aeeb154)
- chore(release): v0.1.43 (1912a6c)
- chore(release): v0.1.42 (aaf3c56)
- chore(release): v0.1.41 (01af62d)
- quick update to instructions (f92d8b9)
- chore(release): v0.1.40 (e6590a0)
- chore(release): v0.1.39 (c3180fc)
- (chore)  Signed Bump-FolderVersion.ps1 script with timestamp provider: http://timestamp.sectigo.com (3234f37)
- chore(release): v0.1.38 (133b231)
- chore(release): v0.1.37 (539a2ff)
- chore(release): v0.1.36 (cfaa056)
- chore(release): v0.1.35 (011d7f8)
- chore(release): v0.1.34 (0f8a569)
- chore(release): v0.1.33 (828f691)
- chore(release): v0.1.32 (ea7c7cb)
- chore(release): v0.1.31 (0bc1456)
- chore(release): v0.1.30 (9e5090e)
- chore(release): v0.1.29 (125e2b3)
- v0.1.29 - Add UI controls for contact deprecation behavior (d559745)
  Changes:
  - Add UI toggle for "treat disabled EntraID users as missing" setting
  - Fix missing "Run Job Manually" section in configuration page
  - Add permission checks around settings and job execution UI
  - Improve configuration page layout and organization
  The update adds user control over how the DeprecateContactsJob handles
  disabled EntraID accounts and restores the ability to trigger manual job
  runs with dry-run option from the UI.
- chore(release): v0.1.28 (c76532f)
- chore(release): v0.1.27 (896a177)
- chore(release): v0.1.26 (03de828)
- chore(release): v0.1.25 (c7ee6d1)
- Add Migration 0004 file (9881b1b)
- chore(release): v0.1.24 (db7192b)
- Missing views.py import directive added "from django.views import View" (6f6ecbc)
- Deleted: unused plugin.py (eb7749e)
- chore(release): v0.1.23 (c73c2b7)
- Add EntraID contact update feature: (872bb35)
  - Custom link 'Update from EntraID' for tenancy.contact
  - View for detailed preview and selective field update from EntraID
  - Template shows side-by-side comparison of NetBox and EntraID fields
  - User can choose which fields to update
  - Uses NetBox-native payload builder for contact updates
  - Wires up plugin config, URLs, and view logic
  This enables admins to resolve and update contacts directly from EntraID with full control over field-level changes.
- Manually updating CHANGELOG.md (9a25f1a)
- chore(release): v0.1.22 (ea914b2)
- chore(release): v0.1.21 (be14863)
- Removed permissions entry that caused breaking change to plugin Migrations: SystemCheckError: System check identified some issues: (9bff78a)
  ERRORS:
  netbox_entraid_tools.Settings: (auth.E005) The permission codenamed 'view_settings' clashes with a builtin permission for model 'netbox_entraid_tools.Settings'.
- Minor UI update to Interval Hours and AutoSchedule fields (fafab62)
- chore(release): v0.1.20 (bd4602c)
- chore(release): v0.1.19 (71c1c10)
- chore(release): v0.1.18 (376fa8e)
- chore(release): v0.1.17 (1523af2)
- chore(release): v0.1.16 (dbaa027)
- chore(release): v0.1.15 (949489d)
- chore(release): v0.1.14 (87b06ca)
- chore(release): v0.1.13 (a60276f)
- chore(release): v0.1.12 (991285c)
- chore(release): v0.1.11 (c391070)
- Add Bumper for increasing Folder version number. Release process is now:   **  Bump-FolderVersion   **  Commit all changes   **  Run: `python tools/release.py --sign --push patch `   **  Create Version Specific LLM ingest text file: `python   \scripts\file-tree-builder\file-tree-builder.py` (74dcc94)
- chore(plugin): update model labels for clearer permission grouping (88d4ebf)
  - Changed __str__ and verbose_name from "EntraID Tools Settings" to "Contacts Admin"
  - Improves readability in NetBox UI: permissions now appear under "EntraID Tools → Contacts Admin"
  - No database migration required (codename unchanged)
- chore(release): v0.1.10 (ae34d0a)
- chore(release): v0.1.9 (ce65b3b)
- chore(release): v0.1.8 (e28d09f)
- chore(release): v0.1.8 (13d8d30)
- changed release.py to use 'callable replacement' in write_version_from_init() function (1968571)
- changed release.py to use ast library in read_version_from_init() function (38761c9)
- initial (3963861)
- Initial commit (2eacf7f)

## [0.1.53] - 2025-09-03

### Fixes
- fix(jobs): resolve job scheduling and API compatibility issues (74956fa)
  This commit fixes several issues related to job scheduling and API compatibility
  after the renaming of settings fields to use job-specific prefixes.
  ISSUES FIXED:
  1. Job Scheduling Errors:
  - Changed 'job_id' parameter to 'name' in enqueue_once() calls in signals.py
  - Fixed error: "functools.partial() got multiple values for keyword argument 'job_id'"
  - Ensured proper scheduler compatibility with NetBox JobRunner API
  2. API Serializer Compatibility:
  - Updated SettingsSerializer to use new job-specific field names
  - Replaced obsolete field names (job_interval_hours, auto_schedule, etc.)
  - Added all new job1_* and job2_* fields to the serializer fields list
  - Fixed error: "Field name 'job_interval_hours' is not valid for model 'Settings'"
  3. Legacy Field References:
  - Updated DeprecateContactsJob._get_config() to use job1_* prefixed settings
  - Updated signals.py to reference job1_interval_hours instead of job_interval_hours
  - Ensured proper storage table name resolution for both jobs
  - Fixed RunNowView to check job1_report_recipients properly
  These changes ensure full compatibility between database fields, API interfaces,
  and job scheduling mechanisms after the settings model refactoring. All jobs now
  correctly use their respective configuration fields with proper

## [0.1.52] - 2025-09-03

### Refactoring
- refactor(settings): reorganize with job-specific field structure and improve UI (e5ec938)
  This commit introduces a significant restructuring of the settings model to use
  consistent job-specific field naming conventions and improves the organization
  of the configuration UI.
  MAJOR CHANGES:
  1. Settings Model Restructuring:
  - Renamed existing fields with job1_* prefix for Deprecate Contacts job
  - Added new fields with job2_* prefix for Sync User Status job
  - Added job2_storage_table_name for Azure Table logging
  - Removed unnecessary job2_report_recipients field
  - Created migration 0007_rename_job_fields.py to handle database changes
  2. Configuration UI Enhancement:
  - Organized settings into dedicated Job 1 and Job 2 sections
  - Added separate job execution controls for each job type
  - Updated form fields to match new model structure
  - Improved visual organization with card-based layout
  3. Backend Support:
  - Updated jobs.py to use job-specific configuration fields
  - Enhanced signals.py to schedule both jobs separately
  - Added log_user_status_change function for tracking status changes
  - Modified SyncUserStatusJob to log changes to Azure Table Storage
  This refactoring improves code organization, enhances maintainability through
  consistent naming conventions, and provides a more intuitive configuration
  experience

## [0.1.51] - 2025-09-03

### Other
- chore(config): disable debug mode by default for production readiness (3ac32fb)
  Change the get_debug_mode() function in common.py to return False by default instead of True.
  This improves security and performance in production environments while still allowing debug
  mode to be explicitly enabled through plugin configuration when needed.
  - Changed default return value in get_debug_mode() from True to False
  - Updated inline comments to reflect new default behavior
  - Maintained backward compatibility with explicit configuration settings
  - Updated AGENT_CONTEXT.md to document the change
  This change completes the transition from development/troubleshooting to production-ready state
  after successfully resolving the previous issues with the contacts resolution functionality.

## [0.1.50] - 2025-09-02

### Fixes
- fix(syntax): resolve indentation error in BulkResolveContactsView.post method (e943fe9)
  This commit fixes a critical Python indentation error in views.py that was causing
  the NetBox-RQ service to fail and resulting in "Internal Server Error" on the NetBox UI.
  The specific error was:
  ```IndentationError: expected an indented block after 'if' statement on line 430```
  The issue occurred in the BulkResolveContactsView.post method where an empty 'if'
  statement was missing its required code block:
  ```python
  if not selected_contacts and "_resolve" in request.POST:
  # Missing code block here
- fix(bulk-update): implement dynamic form detection for EntraID bulk update button (0a2be5d)
  The "Bulk Update from EntraID" button was completely non-functional because it
  was looking for a hardcoded form ID ("id_bulk_select_form") that doesn't exist
  in NetBox's DOM structure. This commit fixes the issue by implementing dynamic
  form detection that works regardless of NetBox's form ID naming conventions.
  Key changes:
  - Added smart form detection using multiple strategies (ID, checkboxes, classes)
  - Dynamically sets the button's form attribute to match the detected form
  - Enhanced server-side parameter extraction to support various naming conventions
  - Improved parsing of form data, JSON data, and URL-encoded parameters
  - Added comprehensive error handling and debug logging for troubleshooting
  - Updated AGENT_CONTEXT.md with details of the fix for future reference
  This approach makes the bulk update functionality more resilient to changes in
  NetBox's DOM structure and form naming conventions, ensuring the feature will
  continue to work across different NetBox versions

### Other
- chore(release): v0.1.49 (e3cabd0)

## [0.1.49] - 2025-09-02

### Fixes
- fix(syntax): resolve indentation error in BulkResolveContactsView.post method (e943fe9)
  This commit fixes a critical Python indentation error in views.py that was causing
  the NetBox-RQ service to fail and resulting in "Internal Server Error" on the NetBox UI.
  The specific error was:
  ```IndentationError: expected an indented block after 'if' statement on line 430```
  The issue occurred in the BulkResolveContactsView.post method where an empty 'if'
  statement was missing its required code block:
  ```python
  if not selected_contacts and "_resolve" in request.POST:
  # Missing code block here
- fix(bulk-update): implement dynamic form detection for EntraID bulk update button (0a2be5d)
  The "Bulk Update from EntraID" button was completely non-functional because it
  was looking for a hardcoded form ID ("id_bulk_select_form") that doesn't exist
  in NetBox's DOM structure. This commit fixes the issue by implementing dynamic
  form detection that works regardless of NetBox's form ID naming conventions.
  Key changes:
  - Added smart form detection using multiple strategies (ID, checkboxes, classes)
  - Dynamically sets the button's form attribute to match the detected form
  - Enhanced server-side parameter extraction to support various naming conventions
  - Improved parsing of form data, JSON data, and URL-encoded parameters
  - Added comprehensive error handling and debug logging for troubleshooting
  - Updated AGENT_CONTEXT.md with details of the fix for future reference
  This approach makes the bulk update functionality more resilient to changes in
  NetBox's DOM structure and form naming conventions, ensuring the feature will
  continue to work across different NetBox versions

## [0.1.48] - 2025-09-02

### Fixes
- fix(bulk-update): fix non-functioning EntraID bulk update button (edf5bac)
  The "Bulk Update from EntraID" button was not triggering any server actions
  when clicked, with no debug logs appearing in the logs despite debug mode
  being enabled. This commit addresses the issue with a comprehensive fix
  and adds enhanced debugging capabilities.
  Changes include:
  - Fixed form submission by adding explicit formmethod="POST" attribute to
  the HTML button
  - Eliminated conflicting button implementation approaches (removed the
  dynamic JS button creation that could cause conflicts)
  - Added detailed client-side debugging with more comprehensive logging
  of form properties and submission attempts
  - Implemented a dedicated plugin logger that writes to both console and
  a separate netbox_entraid_tools.log file
  - Enhanced server-side request inspection in BulkResolveContactsView to
  properly decode and log request body content
  - Set debug_mode to true by default to facilitate troubleshooting
  - Added proper error handling and detailed logging throughout the
  button click and form submission flow
  This fix ensures the bulk update functionality now properly submits the
  form data to the correct endpoint with appropriate logging for any
  potential issues that might arise.

## [0.1.47] - 2025-09-02

### Fixes
- fix(templates): resolve template syntax error when debug mode is enabled (7965e30)
  The plugin was experiencing a template syntax error when debug mode was enabled:
  'setting' is not a registered tag library and the tag was being used without proper loading.
  Changes:
  - Added a utility function `get_debug_mode()` in common.py to consistently retrieve
  the debug_mode setting from plugin configuration
  - Updated templates to use Django's variable system `{{ debug_mode|default:False|yesno:"true,false" }}`
  instead of the non-existent `{% setting %}` tag
  - Modified view functions and template extensions to pass the debug_mode value in the context
  - Removed the incorrect `{% load settings %}` directive from templates
  This fix ensures that the debug mode functionality works correctly in all templates,
  providing consistent behavior while preserving the debugging capabilities.
  The approach prioritizes NetBox 4.2.x compatibility by using standard Django
  templating features rather than relying on custom template tags.
  Testing: Verified templates render correctly with debug mode enabled and disabled.

## [0.1.46] - 2025-09-02

### Fixes
- fix(ui/debug): implement respect for debug_mode setting in bulk update functionality (c35cac2)
  This commit improves the "Bulk Update from EntraID" button functionality by:
  - Leveraging the existing debug_mode setting from the plugin's Settings model
  - Adding conditional debugging in both client-side JavaScript and server-side views
  - Enhancing form submission handling with more robust parameter detection
  - Adding detailed logging of request parameters, headers, and form data when debug_mode is enabled
  - Creating fallback mechanisms when form variables or parameters are missing
  - Implementing a debug_log() helper function in JavaScript for consistent conditional logging
  - Adding comprehensive parameter extraction logic for both GET and POST requests
  The changes maintain a clean production environment by only logging detailed debug
  information when the administrator has explicitly enabled debug_mode in the plugin's
  settings, while still fixing the underlying form submission issues that prevented
  the bulk update functionality from working properly.
  These updates make troubleshooting significantly easier while simultaneously addressing
  the core issue with the button's functionality in NetBox 4.2.x environments.

## [0.1.45] - 2025-09-02

### Fixes
- fix(bulk-actions): restore EntraID contact resolution functionality Fixed critical issues with both individual and bulk contact EntraID resolution that were preventing proper operation due to template syntax errors and button submission problems. (c27b5a1)
  Key changes:
  Fixed Django template syntax error in resolve_contact_confirm.html by refactoring how contact IDs are processed
  Modified view to pass selected contacts directly in template context instead of using error-prone template filters
  Implemented proper NetBox bulk action pattern with formaction and _resolve parameter
  Enhanced view code to handle the custom _resolve parameter in both GET and POST requests
  Added comprehensive logging throughout request handling for better troubleshooting
  Ensured consistent context structure between GET and POST handlers
  Technical details:
  Aligned bulk update button with NetBox's standard pattern seen in core templates
  Used button with type="submit", form="objectListForm", and formaction attribute
  Created specific parameter name="_resolve" to clearly identify the bulk operation
  Used simple iteration over context variables in templates to avoid syntax errors
  Added detailed logging to track request parameters at each processing stage
  This fix restores functionality for both individual contact updates and bulk operations, following NetBox's established patterns for bulk actions while maintaining the plugin's custom functionality.
- fix(bulk-actions): repair contact EntraID resolution functionality (66d548e)
  Fixed critical issues with both individual and bulk contact EntraID resolution functionality that were preventing proper operation due to template syntax errors and form submission problems.
  ### Key changes:
  - Fixed Django template syntax errors in resolve_contact_confirm.html by completely refactoring how contact IDs are processed
  - Modified view to pass selected contacts directly in the template context, eliminating error-prone template filter usage
  - Implemented standard NetBox bulk action pattern with name="_resolve" for the bulk update button
  - Enhanced view code to specifically detect the "_resolve" parameter for clearer intent
  - Added comprehensive logging throughout the request handling flow for troubleshooting
  - Ensured consistent context structure between GET and POST handlers for better reliability
  ### Technical details:
  - Moved request processing logic from templates to Python view code where it belongs
  - Used simple iteration over context variables in templates instead of error-prone filter syntax
  - Preserved NetBox's standard bulk action pattern while using a distinct parameter name to avoid confusion
  - Added fallbacks for multiple parameter patterns to ensure backward compatibility
  - Enhanced debugging output to track exactly which parameters are received in each request
  - Fixed template to correctly iterate over selected contacts without syntax errors
  These changes restore functionality that was working in earlier versions and make the bulk update operation more robust and maintainable.
- fix(templates): repair both individual and bulk contact EntraID resolution (f96c491)
  Fixed critical template syntax errors and form submission issues that were breaking both individual contact updates and bulk contact resolution functionality.
  Key fixes:
  - Corrected Django template syntax errors in resolve_contact_confirm.html by completely refactoring how selected contacts are processed
  - Fixed bulk update button by adding name="_apply" attribute required for proper NetBox form submission
  - Modified contact resolution view to pass contact IDs directly to template via context instead of attempting complex template filters
  - Added detailed logging to aid in troubleshooting form submission issues
  - Ensured consistent context structure between GET and POST handlers for better reliability
  - Maintained all existing validation for contact IDs while simplifying template logic
  Technical details:
  - Moved complex request parameter handling from templates to Python view code where it belongs
  - Fixed template syntax issues by using simple iteration over context variables instead of direct request method calls
  - Applied proper NetBox form submission pattern using name="_apply" attribute for bulk operations
  - Added extensive debug logging to capture request parameters for easier troubleshooting
  - Used proper Django template patterns throughout to avoid parsing errors
  This fix restores functionality that was working in v0.1.39 and adds proper support for bulk operations while maintaining better separation of concerns between views and templates.
- fix(templates): resolve template syntax error in contact resolution Fixed Django template syntax errors in the resolve_contact_confirm.html file by refactoring how selected contact IDs are handled in the bulk update process. (c2836b0)
  Changes made:
  Modified the template to iterate over a context variable instead of using Django's getlist method directly in the template
  Updated the BulkResolveContactsView to pass selected contact IDs directly to the template via context
  Removed error-prone template syntax that was causing parsing errors
  Ensured consistent context structure between GET and POST handlers for better reliability
  Technical details:
  The error occurred because Django templates have strict syntax rules for calling methods with arguments. Rather than trying various syntax patterns in the template (which all failed with different parsing errors), we moved the logic to the Python view where it belongs. This separates the data preparation from presentation, following better MVC design principles.
  The fix maintains the same functionality while eliminating the template syntax errors that were breaking both individual and bulk contact resolution features.
- fix(templates): correct Django template method call syntax Fixed critical template syntax errors in resolve_contact_confirm.html that were breaking both individual and bulk contact resolution functionality. The issue was related to how method calls with arguments are handled in Django template language. (8118df5)
  Changes made:
  Changed {% for pk in request.GET.getlist 'pk' %} to {% for pk in request.GET.getlist "pk" %} (proper Django syntax)
  Applied the same correction to POST parameter handling loop
  Removed incorrect use of parentheses that caused parsing errors
  Error details:
  Initially, we encountered:
  <classÂ 'django.template.exceptions.TemplateSyntaxError'>'for'Â statementsÂ shouldÂ useÂ theÂ formatÂ 'forÂ xÂ inÂ y':Â forÂ pkÂ inÂ request.GET.getlistÂ 'pk'
  When attempting to fix with parentheses, we got:
  <classÂ 'django.template.exceptions.TemplateSyntaxError'>CouldÂ notÂ parseÂ theÂ remainder:Â '('pk')'Â fromÂ 'request.GET.getlist('pk')'
  This fix properly implements Django's template syntax rules where method calls don't use parentheses, and string arguments are provided with quotes directly after the method name.
- Fixed tags and corrected Version number in __init__.py (a91defa)
- fix(templates): correct Django template syntax error in contact resolution form Fixed a critical template syntax error in the resolve_contact_confirm.html template that was causing a TemplateSyntaxError and breaking both individual and bulk contact resolution features. The error occurred in the for loops that process GET and POST parameters, which were missing parentheses around the getlist function parameters. (24d95ca)
  Changes made:
  Changed {% for pk in request.GET.getlist 'pk' %} to {% for pk in request.GET.getlist('pk') %}
  Made the same correction for the POST parameter processing loop
  Restored functionality for both individual contact resolution and bulk resolution
  Error details:
  The error that was occurring was:
  <classÂ 'django.template.exceptions.TemplateSyntaxError'>'for'Â statementsÂ shouldÂ useÂ theÂ formatÂ 'forÂ xÂ inÂ y':Â forÂ pkÂ inÂ request.GET.getlistÂ 'pk'
  This fix maintains all the previously implemented validation for contact IDs while correcting the syntax issue that was preventing the entire feature from working. Both the individual contact update and bulk update functionalities should now work as intended.

### Other
- chore(release): v0.1.45 (2289477)
- chore(release): v0.1.45 (90e88fc)
- chore(release): v0.1.45 (700c88f)
- chore(release): v0.1.45 (8d3c6ea)
- chore(release): v0.1.45 (996bcc8)
- chore(release): v0.1.46 (65ab409)

## [0.1.45] - 2025-09-02

### Fixes
- fix(bulk-actions): repair contact EntraID resolution functionality (66d548e)
  Fixed critical issues with both individual and bulk contact EntraID resolution functionality that were preventing proper operation due to template syntax errors and form submission problems.
  ### Key changes:
  - Fixed Django template syntax errors in resolve_contact_confirm.html by completely refactoring how contact IDs are processed
  - Modified view to pass selected contacts directly in the template context, eliminating error-prone template filter usage
  - Implemented standard NetBox bulk action pattern with name="_resolve" for the bulk update button
  - Enhanced view code to specifically detect the "_resolve" parameter for clearer intent
  - Added comprehensive logging throughout the request handling flow for troubleshooting
  - Ensured consistent context structure between GET and POST handlers for better reliability
  ### Technical details:
  - Moved request processing logic from templates to Python view code where it belongs
  - Used simple iteration over context variables in templates instead of error-prone filter syntax
  - Preserved NetBox's standard bulk action pattern while using a distinct parameter name to avoid confusion
  - Added fallbacks for multiple parameter patterns to ensure backward compatibility
  - Enhanced debugging output to track exactly which parameters are received in each request
  - Fixed template to correctly iterate over selected contacts without syntax errors
  These changes restore functionality that was working in earlier versions and make the bulk update operation more robust and maintainable.
- fix(templates): repair both individual and bulk contact EntraID resolution (f96c491)
  Fixed critical template syntax errors and form submission issues that were breaking both individual contact updates and bulk contact resolution functionality.
  Key fixes:
  - Corrected Django template syntax errors in resolve_contact_confirm.html by completely refactoring how selected contacts are processed
  - Fixed bulk update button by adding name="_apply" attribute required for proper NetBox form submission
  - Modified contact resolution view to pass contact IDs directly to template via context instead of attempting complex template filters
  - Added detailed logging to aid in troubleshooting form submission issues
  - Ensured consistent context structure between GET and POST handlers for better reliability
  - Maintained all existing validation for contact IDs while simplifying template logic
  Technical details:
  - Moved complex request parameter handling from templates to Python view code where it belongs
  - Fixed template syntax issues by using simple iteration over context variables instead of direct request method calls
  - Applied proper NetBox form submission pattern using name="_apply" attribute for bulk operations
  - Added extensive debug logging to capture request parameters for easier troubleshooting
  - Used proper Django template patterns throughout to avoid parsing errors
  This fix restores functionality that was working in v0.1.39 and adds proper support for bulk operations while maintaining better separation of concerns between views and templates.
- fix(templates): resolve template syntax error in contact resolution Fixed Django template syntax errors in the resolve_contact_confirm.html file by refactoring how selected contact IDs are handled in the bulk update process. (c2836b0)
  Changes made:
  Modified the template to iterate over a context variable instead of using Django's getlist method directly in the template
  Updated the BulkResolveContactsView to pass selected contact IDs directly to the template via context
  Removed error-prone template syntax that was causing parsing errors
  Ensured consistent context structure between GET and POST handlers for better reliability
  Technical details:
  The error occurred because Django templates have strict syntax rules for calling methods with arguments. Rather than trying various syntax patterns in the template (which all failed with different parsing errors), we moved the logic to the Python view where it belongs. This separates the data preparation from presentation, following better MVC design principles.
  The fix maintains the same functionality while eliminating the template syntax errors that were breaking both individual and bulk contact resolution features.
- fix(templates): correct Django template method call syntax Fixed critical template syntax errors in resolve_contact_confirm.html that were breaking both individual and bulk contact resolution functionality. The issue was related to how method calls with arguments are handled in Django template language. (8118df5)
  Changes made:
  Changed {% for pk in request.GET.getlist 'pk' %} to {% for pk in request.GET.getlist "pk" %} (proper Django syntax)
  Applied the same correction to POST parameter handling loop
  Removed incorrect use of parentheses that caused parsing errors
  Error details:
  Initially, we encountered:
  <classÂ 'django.template.exceptions.TemplateSyntaxError'>'for'Â statementsÂ shouldÂ useÂ theÂ formatÂ 'forÂ xÂ inÂ y':Â forÂ pkÂ inÂ request.GET.getlistÂ 'pk'
  When attempting to fix with parentheses, we got:
  <classÂ 'django.template.exceptions.TemplateSyntaxError'>CouldÂ notÂ parseÂ theÂ remainder:Â '('pk')'Â fromÂ 'request.GET.getlist('pk')'
  This fix properly implements Django's template syntax rules where method calls don't use parentheses, and string arguments are provided with quotes directly after the method name.
- Fixed tags and corrected Version number in __init__.py (a91defa)
- fix(templates): correct Django template syntax error in contact resolution form Fixed a critical template syntax error in the resolve_contact_confirm.html template that was causing a TemplateSyntaxError and breaking both individual and bulk contact resolution features. The error occurred in the for loops that process GET and POST parameters, which were missing parentheses around the getlist function parameters. (24d95ca)
  Changes made:
  Changed {% for pk in request.GET.getlist 'pk' %} to {% for pk in request.GET.getlist('pk') %}
  Made the same correction for the POST parameter processing loop
  Restored functionality for both individual contact resolution and bulk resolution
  Error details:
  The error that was occurring was:
  <classÂ 'django.template.exceptions.TemplateSyntaxError'>'for'Â statementsÂ shouldÂ useÂ theÂ formatÂ 'forÂ xÂ inÂ y':Â forÂ pkÂ inÂ request.GET.getlistÂ 'pk'
  This fix maintains all the previously implemented validation for contact IDs while correcting the syntax issue that was preventing the entire feature from working. Both the individual contact update and bulk update functionalities should now work as intended.

### Other
- chore(release): v0.1.45 (90e88fc)
- chore(release): v0.1.45 (700c88f)
- chore(release): v0.1.45 (8d3c6ea)
- chore(release): v0.1.45 (996bcc8)
- chore(release): v0.1.46 (65ab409)

## [0.1.45] - 2025-09-01

### Fixes
- fix(templates): repair both individual and bulk contact EntraID resolution (f96c491)
  Fixed critical template syntax errors and form submission issues that were breaking both individual contact updates and bulk contact resolution functionality.
  Key fixes:
  - Corrected Django template syntax errors in resolve_contact_confirm.html by completely refactoring how selected contacts are processed
  - Fixed bulk update button by adding name="_apply" attribute required for proper NetBox form submission
  - Modified contact resolution view to pass contact IDs directly to template via context instead of attempting complex template filters
  - Added detailed logging to aid in troubleshooting form submission issues
  - Ensured consistent context structure between GET and POST handlers for better reliability
  - Maintained all existing validation for contact IDs while simplifying template logic
  Technical details:
  - Moved complex request parameter handling from templates to Python view code where it belongs
  - Fixed template syntax issues by using simple iteration over context variables instead of direct request method calls
  - Applied proper NetBox form submission pattern using name="_apply" attribute for bulk operations
  - Added extensive debug logging to capture request parameters for easier troubleshooting
  - Used proper Django template patterns throughout to avoid parsing errors
  This fix restores functionality that was working in v0.1.39 and adds proper support for bulk operations while maintaining better separation of concerns between views and templates.
- fix(templates): resolve template syntax error in contact resolution Fixed Django template syntax errors in the resolve_contact_confirm.html file by refactoring how selected contact IDs are handled in the bulk update process. (c2836b0)
  Changes made:
  Modified the template to iterate over a context variable instead of using Django's getlist method directly in the template
  Updated the BulkResolveContactsView to pass selected contact IDs directly to the template via context
  Removed error-prone template syntax that was causing parsing errors
  Ensured consistent context structure between GET and POST handlers for better reliability
  Technical details:
  The error occurred because Django templates have strict syntax rules for calling methods with arguments. Rather than trying various syntax patterns in the template (which all failed with different parsing errors), we moved the logic to the Python view where it belongs. This separates the data preparation from presentation, following better MVC design principles.
  The fix maintains the same functionality while eliminating the template syntax errors that were breaking both individual and bulk contact resolution features.
- fix(templates): correct Django template method call syntax Fixed critical template syntax errors in resolve_contact_confirm.html that were breaking both individual and bulk contact resolution functionality. The issue was related to how method calls with arguments are handled in Django template language. (8118df5)
  Changes made:
  Changed {% for pk in request.GET.getlist 'pk' %} to {% for pk in request.GET.getlist "pk" %} (proper Django syntax)
  Applied the same correction to POST parameter handling loop
  Removed incorrect use of parentheses that caused parsing errors
  Error details:
  Initially, we encountered:
  <classÂ 'django.template.exceptions.TemplateSyntaxError'>'for'Â statementsÂ shouldÂ useÂ theÂ formatÂ 'forÂ xÂ inÂ y':Â forÂ pkÂ inÂ request.GET.getlistÂ 'pk'
  When attempting to fix with parentheses, we got:
  <classÂ 'django.template.exceptions.TemplateSyntaxError'>CouldÂ notÂ parseÂ theÂ remainder:Â '('pk')'Â fromÂ 'request.GET.getlist('pk')'
  This fix properly implements Django's template syntax rules where method calls don't use parentheses, and string arguments are provided with quotes directly after the method name.
- Fixed tags and corrected Version number in __init__.py (a91defa)
- fix(templates): correct Django template syntax error in contact resolution form Fixed a critical template syntax error in the resolve_contact_confirm.html template that was causing a TemplateSyntaxError and breaking both individual and bulk contact resolution features. The error occurred in the for loops that process GET and POST parameters, which were missing parentheses around the getlist function parameters. (24d95ca)
  Changes made:
  Changed {% for pk in request.GET.getlist 'pk' %} to {% for pk in request.GET.getlist('pk') %}
  Made the same correction for the POST parameter processing loop
  Restored functionality for both individual contact resolution and bulk resolution
  Error details:
  The error that was occurring was:
  <classÂ 'django.template.exceptions.TemplateSyntaxError'>'for'Â statementsÂ shouldÂ useÂ theÂ formatÂ 'forÂ xÂ inÂ y':Â forÂ pkÂ inÂ request.GET.getlistÂ 'pk'
  This fix maintains all the previously implemented validation for contact IDs while correcting the syntax issue that was preventing the entire feature from working. Both the individual contact update and bulk update functionalities should now work as intended.

### Other
- chore(release): v0.1.45 (700c88f)
- chore(release): v0.1.45 (8d3c6ea)
- chore(release): v0.1.45 (996bcc8)
- chore(release): v0.1.46 (65ab409)

## [0.1.45] - 2025-09-01

### Fixes
- fix(templates): resolve template syntax error in contact resolution Fixed Django template syntax errors in the resolve_contact_confirm.html file by refactoring how selected contact IDs are handled in the bulk update process. (c2836b0)
  Changes made:
  Modified the template to iterate over a context variable instead of using Django's getlist method directly in the template
  Updated the BulkResolveContactsView to pass selected contact IDs directly to the template via context
  Removed error-prone template syntax that was causing parsing errors
  Ensured consistent context structure between GET and POST handlers for better reliability
  Technical details:
  The error occurred because Django templates have strict syntax rules for calling methods with arguments. Rather than trying various syntax patterns in the template (which all failed with different parsing errors), we moved the logic to the Python view where it belongs. This separates the data preparation from presentation, following better MVC design principles.
  The fix maintains the same functionality while eliminating the template syntax errors that were breaking both individual and bulk contact resolution features.
- fix(templates): correct Django template method call syntax Fixed critical template syntax errors in resolve_contact_confirm.html that were breaking both individual and bulk contact resolution functionality. The issue was related to how method calls with arguments are handled in Django template language. (8118df5)
  Changes made:
  Changed {% for pk in request.GET.getlist 'pk' %} to {% for pk in request.GET.getlist "pk" %} (proper Django syntax)
  Applied the same correction to POST parameter handling loop
  Removed incorrect use of parentheses that caused parsing errors
  Error details:
  Initially, we encountered:
  <classÂ 'django.template.exceptions.TemplateSyntaxError'>'for'Â statementsÂ shouldÂ useÂ theÂ formatÂ 'forÂ xÂ inÂ y':Â forÂ pkÂ inÂ request.GET.getlistÂ 'pk'
  When attempting to fix with parentheses, we got:
  <classÂ 'django.template.exceptions.TemplateSyntaxError'>CouldÂ notÂ parseÂ theÂ remainder:Â '('pk')'Â fromÂ 'request.GET.getlist('pk')'
  This fix properly implements Django's template syntax rules where method calls don't use parentheses, and string arguments are provided with quotes directly after the method name.
- Fixed tags and corrected Version number in __init__.py (a91defa)
- fix(templates): correct Django template syntax error in contact resolution form Fixed a critical template syntax error in the resolve_contact_confirm.html template that was causing a TemplateSyntaxError and breaking both individual and bulk contact resolution features. The error occurred in the for loops that process GET and POST parameters, which were missing parentheses around the getlist function parameters. (24d95ca)
  Changes made:
  Changed {% for pk in request.GET.getlist 'pk' %} to {% for pk in request.GET.getlist('pk') %}
  Made the same correction for the POST parameter processing loop
  Restored functionality for both individual contact resolution and bulk resolution
  Error details:
  The error that was occurring was:
  <classÂ 'django.template.exceptions.TemplateSyntaxError'>'for'Â statementsÂ shouldÂ useÂ theÂ formatÂ 'forÂ xÂ inÂ y':Â forÂ pkÂ inÂ request.GET.getlistÂ 'pk'
  This fix maintains all the previously implemented validation for contact IDs while correcting the syntax issue that was preventing the entire feature from working. Both the individual contact update and bulk update functionalities should now work as intended.

### Other
- chore(release): v0.1.45 (8d3c6ea)
- chore(release): v0.1.45 (996bcc8)
- chore(release): v0.1.46 (65ab409)

## [0.1.45] - 2025-09-01

### Fixes
- fix(templates): correct Django template method call syntax Fixed critical template syntax errors in resolve_contact_confirm.html that were breaking both individual and bulk contact resolution functionality. The issue was related to how method calls with arguments are handled in Django template language. (8118df5)
  Changes made:
  Changed {% for pk in request.GET.getlist 'pk' %} to {% for pk in request.GET.getlist "pk" %} (proper Django syntax)
  Applied the same correction to POST parameter handling loop
  Removed incorrect use of parentheses that caused parsing errors
  Error details:
  Initially, we encountered:
  <classÂ 'django.template.exceptions.TemplateSyntaxError'>'for'Â statementsÂ shouldÂ useÂ theÂ formatÂ 'forÂ xÂ inÂ y':Â forÂ pkÂ inÂ request.GET.getlistÂ 'pk'
  When attempting to fix with parentheses, we got:
  <classÂ 'django.template.exceptions.TemplateSyntaxError'>CouldÂ notÂ parseÂ theÂ remainder:Â '('pk')'Â fromÂ 'request.GET.getlist('pk')'
  This fix properly implements Django's template syntax rules where method calls don't use parentheses, and string arguments are provided with quotes directly after the method name.
- Fixed tags and corrected Version number in __init__.py (a91defa)
- fix(templates): correct Django template syntax error in contact resolution form Fixed a critical template syntax error in the resolve_contact_confirm.html template that was causing a TemplateSyntaxError and breaking both individual and bulk contact resolution features. The error occurred in the for loops that process GET and POST parameters, which were missing parentheses around the getlist function parameters. (24d95ca)
  Changes made:
  Changed {% for pk in request.GET.getlist 'pk' %} to {% for pk in request.GET.getlist('pk') %}
  Made the same correction for the POST parameter processing loop
  Restored functionality for both individual contact resolution and bulk resolution
  Error details:
  The error that was occurring was:
  <classÂ 'django.template.exceptions.TemplateSyntaxError'>'for'Â statementsÂ shouldÂ useÂ theÂ formatÂ 'forÂ xÂ inÂ y':Â forÂ pkÂ inÂ request.GET.getlistÂ 'pk'
  This fix maintains all the previously implemented validation for contact IDs while correcting the syntax issue that was preventing the entire feature from working. Both the individual contact update and bulk update functionalities should now work as intended.

### Other
- chore(release): v0.1.45 (996bcc8)
- chore(release): v0.1.46 (65ab409)

## [0.1.45] - 2025-09-01

### Fixes
- Fixed tags and corrected Version number in __init__.py (a91defa)
- fix(templates): correct Django template syntax error in contact resolution form Fixed a critical template syntax error in the resolve_contact_confirm.html template that was causing a TemplateSyntaxError and breaking both individual and bulk contact resolution features. The error occurred in the for loops that process GET and POST parameters, which were missing parentheses around the getlist function parameters. (24d95ca)
  Changes made:
  Changed {% for pk in request.GET.getlist 'pk' %} to {% for pk in request.GET.getlist('pk') %}
  Made the same correction for the POST parameter processing loop
  Restored functionality for both individual contact resolution and bulk resolution
  Error details:
  The error that was occurring was:
  <classÂ 'django.template.exceptions.TemplateSyntaxError'>'for'Â statementsÂ shouldÂ useÂ theÂ formatÂ 'forÂ xÂ inÂ y':Â forÂ pkÂ inÂ request.GET.getlistÂ 'pk'
  This fix maintains all the previously implemented validation for contact IDs while correcting the syntax issue that was preventing the entire feature from working. Both the individual contact update and bulk update functionalities should now work as intended.

### Other
- chore(release): v0.1.46 (65ab409)

## [0.1.46] - 2025-09-01

### Fixes
- fix(templates): correct Django template syntax error in contact resolution form Fixed a critical template syntax error in the resolve_contact_confirm.html template that was causing a TemplateSyntaxError and breaking both individual and bulk contact resolution features. The error occurred in the for loops that process GET and POST parameters, which were missing parentheses around the getlist function parameters. (24d95ca)
  Changes made:
  Changed {% for pk in request.GET.getlist 'pk' %} to {% for pk in request.GET.getlist('pk') %}
  Made the same correction for the POST parameter processing loop
  Restored functionality for both individual contact resolution and bulk resolution
  Error details:
  The error that was occurring was:
  <classÂ 'django.template.exceptions.TemplateSyntaxError'>'for'Â statementsÂ shouldÂ useÂ theÂ formatÂ 'forÂ xÂ inÂ y':Â forÂ pkÂ inÂ request.GET.getlistÂ 'pk'
  This fix maintains all the previously implemented validation for contact IDs while correcting the syntax issue that was preventing the entire feature from working. Both the individual contact update and bulk update functionalities should now work as intended.

## [0.1.44] - 2025-09-01

### Other
- - fix(ui): resolve bulk contact update form submission issues (current)   The bulk contact update functionality was failing with a ValueError when trying   to process the form data, with the error "invalid literal for int() with base 10: 'form'".   Changes:   - Removed 'name="bulk_action"' from the submit button which was interfering with form data   - Enhanced contact ID retrieval logic to handle multiple possible parameter sources   - Added better error handling for invalid contact IDs with detailed logging   - Updated the confirmation template to preserve selected IDs from both GET and POST   - Added validation to skip non-integer values in contact IDs with warning messages   This fix ensures that when users select contacts via checkboxes and click   "Bulk Update from EntraID", the form submission properly captures the selected contacts. (aeeb154)

## [0.1.43] - 2025-09-01

### Fixes
- fix(logging): add debug level support in ResolveContactEntraID script (7ad469f)
  The log_message helper function in the ResolveContactEntraID script was missing
  handlers for debug-level messages, causing errors in the debug.log when running
  the Resolve job against selected contacts.
  Changes:
  - Added debug level support for job context logging
  - Implemented a fallback that logs debug messages as info with a "DEBUG:" prefix
  when running in script context
  - Fixed indentation issue with disabled account check to prevent potential errors
  - Improved code robustness by ensuring the account disabled check only runs when
  a match is actually found
  This ensures debug messages are properly processed in both job and script contexts,
  preventing errors in the log files while maintaining full logging functionality.

## [0.1.43] - 25-08-31

###Fixes
-  fix(logging): add debug level support in ResolveContactEntraID script

   The log_message helper function in the ResolveContactEntraID script was missing
   handlers for debug-level messages, causing errors in the debug.log when running
   the Resolve job against selected contacts.

   Changes:
   - Added debug level support for job context logging
   - Implemented a fallback that logs debug messages as info with a "DEBUG:" prefix
     when running in script context
   - Fixed indentation issue with disabled account check to prevent potential errors
   - Improved code robustness by ensuring the account disabled check only runs when
     a match is actually found

This ensures debug messages are properly processed in both job and script contexts,
preventing errors in the log files while maintaining full logging functionality.

## [0.1.42] - 2025-08-31

### Fixes
- fix(ui): integrate bulk update button with NetBox's objectListForm (af401e4)
  The bulk contact update functionality was not receiving the selected contacts
  when using the checkbox selection in the contact list view. This was happening
  because the custom bulk action button was wrapped in a separate form that didn't
  include the selected PKs.
  Changes:
  - Removed the standalone form element wrapping the bulk update button
  - Modified button to use form="objectListForm" to submit the main list form
  - Added formaction attribute to direct the submission to the bulk resolve endpoint
  - Preserved all button styling and permission checks
  This change ensures that when users select contacts via checkboxes in the
  Organization -> Contacts view and click "Bulk Update from EntraID", the
  selected contact IDs are properly passed to the BulkResolveContactsView,
  resolving the "No contacts were selected for bulk

## [0.1.41] - 2025-08-31

### Fixes
- fix(contacts): implement proper handling of selected contacts in bulk resolution (d301d21)
  The bulk resolution functionality was not correctly processing selected contacts,
  resulting in a "No contacts provided to process" error when attempting to resolve
  multiple selected contacts from EntraID.
  Changes:
  - Modified BulkResolveContactsView to retrieve selected contact IDs from both GET and POST parameters
  - Updated the contact list actions template to properly submit the selected contacts via a form
  - Enhanced the confirmation template to show the count of selected contacts and preserve them between requests
  - Added validation to display a warning when no contacts are selected for resolution
  - Improved user feedback by displaying the number of contacts being processed
  This fix ensures that the EntraID resolution job only processes the specific contacts
  that were selected by the user, rather than attempting to process all contacts or none.
- fix(contacts): implement proper handling of selected contacts in bulk resolution (42208bc)
  The bulk resolution functionality was not correctly processing selected contacts,
  resulting in a "No contacts provided to process" error when attempting to resolve
  multiple selected contacts from EntraID.
  Changes:
  - Modified BulkResolveContactsView to retrieve selected contact IDs from both GET and POST parameters
  - Updated the contact list actions template to properly submit the selected contacts via a form
  - Enhanced the confirmation template to show the count of selected contacts and preserve them between requests
  - Added validation to display a warning when no contacts are selected for resolution
  - Improved user feedback by displaying the number of contacts being processed
  This fix ensures that the EntraID resolution job only processes the specific contacts
  that were selected by the user, rather than attempting to process all contacts or none.

### Other
- quick update to instructions (f92d8b9)

## [0.1.40] - 2025-08-31

### Features
- feat(ui): add bulk EntraID resolve button to contacts list (0fedbb3)
  Add functionality to resolve all contacts from EntraID in bulk via the contacts list page.
  This builds on the existing per-contact resolution functionality and reuses much of the same
  infrastructure.
  The implementation includes:
  - Add list_buttons method to ContactActions template extension
  - Create contact_list_actions.html button template for the contacts list
  - Add BulkResolveContactsView to handle the bulk operation
  - Create URL path for bulk resolution endpoint
  - Update resolve_contact_confirm.html to support both individual and bulk operations
  This enhancement allows administrators to easily refresh EntraID information for all
  contacts at once, rather than having to visit each contact individually.
  Related to: #42

## [0.1.39] - 2025-08-31

### Breaking Changes
- feat(build): modernize build system and enhance deployment tools (9b33dfe)
  This commit implements several improvements to the build and deployment process:
  - Add pyproject.toml for PEP 517 compatibility, addressing Oct 31, 2025 deprecation warning
  - Enhance Bump-FolderVersion.ps1 with comprehensive comment-based help documentation
  - Add -OpenCode parameter to Bump-FolderVersion.ps1 with default value of $True
  - Implement automatic VS Code launching in the newly created version folder
  - Create detailed BUILD.md with instructions for modern build workflow
  - Update release.py to include guidance for the new build system
  - Create CODE_SIGNING.md with PowerShell code signing management instructions
  - Update README.md with references to build documentation
  - Remove invalid signature from Bump-FolderVersion.ps1
  These changes ensure compatibility with future Python packaging standards
  while enhancing the developer experience when managing version upgrades.
  The modern build system eliminates deprecation warnings and improves
  compatibility with current packaging tools.
  BREAKING CHANGE: The PowerShell script signature has been removed and will need
  to be re-signed following the guidance in CODE_SIGNING.md
  - The PowerShell script signature has been removed and will need
  - to be re-signed following the guidance in CODE_SIGNING.md

### Features
- feat(build): modernize build system and enhance deployment tools (9b33dfe)
  This commit implements several improvements to the build and deployment process:
  - Add pyproject.toml for PEP 517 compatibility, addressing Oct 31, 2025 deprecation warning
  - Enhance Bump-FolderVersion.ps1 with comprehensive comment-based help documentation
  - Add -OpenCode parameter to Bump-FolderVersion.ps1 with default value of $True
  - Implement automatic VS Code launching in the newly created version folder
  - Create detailed BUILD.md with instructions for modern build workflow
  - Update release.py to include guidance for the new build system
  - Create CODE_SIGNING.md with PowerShell code signing management instructions
  - Update README.md with references to build documentation
  - Remove invalid signature from Bump-FolderVersion.ps1
  These changes ensure compatibility with future Python packaging standards
  while enhancing the developer experience when managing version upgrades.
  The modern build system eliminates deprecation warnings and improves
  compatibility with current packaging tools.
  BREAKING CHANGE: The PowerShell script signature has been removed and will need
  to be re-signed following the guidance in CODE_SIGNING.md

### Other
- (chore)  Signed Bump-FolderVersion.ps1 script with timestamp provider: http://timestamp.sectigo.com (3234f37)

## [0.1.38] - 2025-08-31

### Features
- feat(ui): add job ID to notification messages (c35d775)
  - enhance(notifications): include job ID in success message when enqueuing jobs
  - enhance(notifications): add job ID to fallback messages when redirection fails
  - docs(context): update AGENT_CONTEXT.md with notification enhancements
  This change improves traceability by showing job IDs in user notifications,
  making it easier to find specific jobs in the NetBox job list for status
  checking and troubleshooting. The enhanced messages provide a direct
  reference to the relevant job, especially helpful in busy environments
  where multiple jobs may be running concurrently.

## [0.1.37] - 2025-08-31

### Fixes
- fix(matching): implement full Graph API pagination for large directories (34530df)
  - feat(graph): add complete Microsoft Graph API pagination implementation
  - perf(filtering): add smart first-letter filtering for efficient user lookup
  - enhance(resilience): implement fallback strategy when filtered results are insufficient
  - improve(logging): add pagination progress indicators for large retrievals
  This change addresses contact matching in large directories (5000+ users),
  particularly for contacts with names later in the alphabet (e.g., starting with 'Z').
  The enhanced implementation uses Microsoft Graph API's native filtering and pagination
  capabilities with appropriate fallback strategies for reliable matching.

## [0.1.36] - 2025-08-30

### Fixes
- fix(logging): resolve JobLogger method compatibility issue (060e9fb)
  The ResolveContactsJob was failing with AttributeError when running the
  ResolveContactEntraID script due to a mismatch between logging methods.
  Changes:
  - Add log_message() helper function in ResolveContactEntraID script to properly
  route logging calls between job and script contexts
  - Replace all direct log_* method calls with the new helper function to ensure
  proper method routing
  - Add missing debug() method to JobLogger class for completeness
  - Improve method selection logic to handle both standalone script and job execution paths
  This fixes the AttributeError("'JobLogger' object has no attribute 'log'") error
  that occurred when the script tried to use script-style logging methods with the
  JobLogger instance.
  Issue: AttributeError in job logs (02d73815-1e95-4079-a03c-cf17a7e6140a)

## [0.1.35] - 2025-08-30

### Features
- feat(contact-resolution): enhance logging and troubleshooting for EntraID contact resolution (bbfd4b5)
  This commit improves the contact resolution functionality with better logging and diagnostic capabilities without changing the core behavior.
  - feat(graph): add accountEnabled field to user query methods in GraphClient
  - feat(graph): improve error logging in GraphClient.get_user_by_email and GraphClient.list_users
  - feat(scripts): enhance ResolveContactEntraID script with detailed user status logging
  - feat(scripts): add more verbose logging during fuzzy name matching process
  - feat(jobs): add debug-level logging for contact details in ResolveContactsJob
  The changes focus on better troubleshooting without changing the core behavior - the ResolveContactsJob continues to resolve all contacts regardless of disabled status, while the DeprecateContactsJob handles enforcement of the "treat_disabled_as_missing" policy.
  These improvements help identify why specific contacts might fail to resolve by providing visibility into user account status and the matching process details.

## [0.1.34] - 2025-08-30

### Fixes
- fix(ui): Fix duplicate job form and enhance contact resolution workflow (1337bdb)
  This commit addresses multiple issues related to the configuration UI and job execution workflow:
  PROBLEM #1: Duplicate "Run Job Manually" sections
  - The configuration page showed the job execution form twice: once in the form block and
  again in the content block
  - This created a confusing user experience and potential form submission issues
  PROBLEM #2: Contact resolution job URL error
  - When submitting the contact resolution form, users encountered a NoReverseMatch error:
  "Reverse for 'job' not found"
  - The error occurred because the URL pattern for job results differs in NetBox 4.2.x
  CHANGES:
  1. Configuration UI Improvements:
  - Removed duplicate job execution form from content block
  - Added debug_mode setting to toggle visibility of debug information
  - Added Settings.debug_mode BooleanField with migration
  - Fixed "Run Deprecation Job" button to properly use form submission
  2. Job Result Navigation:
  - Enhanced ResolveContactJobView with robust URL handling
  - Added fallback URL patterns for different NetBox versions
  - Gracefully degrades to contact detail page if URL resolution fails
  - Added informative user messages about job status
  3. Code Quality and Documentation:
  - Added explanatory comments about debug mode usage
  - Updated template comments to explain removed duplicate sections
  - Ensured consistent form submission behavior
  TESTING:
  - Verified config page renders without duplicate job forms
  - Confirmed contact resolution job form submits and redirects correctly
  - Tested debug mode toggle functionality
  - Validated form submissions work with proper checkbox handling
  These changes improve UI consistency and fix critical errors in the job execution workflow.

## [0.1.33] - 2025-08-29

### Fixes
- Fix UI issues and ContactDeprecationJob compatibility with NetBox 4.2.x (9e227f9)
  This commit addresses several key issues with the NetBox EntraID Tools plugin:
  1. Fixed DeprecateContactsJob failing with "treat_disabled_as_missing" option:
  - Updated references from "content_type" to "object_type" to match NetBox 4.2.x model structure
  - Fixed the select_related query to use the correct field name
  - Removed unused ContentType import
  2. Fixed missing "Run Job Manually" section in configuration page:
  - Restructured template to move the section from non-existent "below_form" block to the "content" block
  - Added debug information to help diagnose permission issues
  - Enhanced error handling in RunNowView with more descriptive messages
  3. Fixed blank page when clicking "Resolve in EntraID" button:
  - Updated resolve_contact_confirm.html to extend generic/object_edit.html instead of base/base.html
  - Restructured HTML to use Bootstrap 5 components and card layout
  - Used NetBox form_helpers for consistent form rendering
  - Added proper button styling and layout
  4. Improved user experience:
  - Renamed "Resolve in EntraID" button to "Update from EntraID" for clarity
  - Added proper error handling and success messages for job enqueuing
  - Enhanced form display with consistent NetBox styling
  These changes ensure compatibility with NetBox 4.2.x's UI framework and model structure
  while improving overall user experience and error handling.
- fix(ui): Use standard Django form rendering to fix blank page issue (4de6085)
  PROBLEM:
  After initial fixes, clicking "Resolve in EntraID" still produced a blank page with the following error:
  "TemplateSyntaxError: Invalid block tag on line 16: 'render_form', expected 'endblock'.
  Did you forget to register or load this tag?"
  Despite adding {% load form_helpers %}, NetBox's template system was still having issues with the form rendering.
  CHANGES:
  - Reverted template to use standard Django form rendering instead of NetBox's helper tags
  - Added explicit Bootstrap styling for form elements:
  * Applied custom-control-input class to checkbox
  * Added proper label and help text formatting
  - Enhanced ResolveContactJobForm with explicit label and widget attributes
  - Simplified template structure to avoid potential inheritance issues
  TESTING:
  - Verified form properly renders with standard Django form rendering
  - Confirmed checkbox displays with proper styling and label
  - Validated form submission still works correctly with the modified template
  This change resolves the blank page issue by avoiding the template tag loading problem
  and using direct Django form element rendering instead.

## [0.1.32] - 2025-08-29

### Fixes
- fix(ui): Repair EntraID contact resolution form rendering (ccd0f1c)
  PROBLEM:
  When clicking the "Resolve in EntraID" button on a Contact detail page, a blank page would appear instead of the
  confirmation form. The issue was due to Django template errors:
  1. ValueError: "invalid literal for int() with base 10: 'form'"
  2. VariableDoesNotExist: "Failed lookup for key [form]"
  This indicated the template was expecting a form object in its context that wasn't being provided.
  CHANGES:
  - Added ResolveContactJobForm class to forms.py with proper dry_run field and help text
  - Updated ResolveContactJobView to follow Django form patterns:
  * Properly initialize form in GET method
  * Process form through validation in POST method
  * Pass form object to template context
  * Handle both valid and invalid form submissions
  - Modified resolve_contact_confirm.html template to use NetBox's {% render_form %} helper
  - Ensured consistent form field rendering across NetBox themes
  TESTING:
  - Verified form properly renders with dry run checkbox enabled by default
  - Confirmed job queues correctly with both dry run enabled and disabled
  - Validated proper redirect to job status page after form submission
  This completes the UI work for the EntraID contact resolution feature, making it fully
  functional within the NetBox UI and ensuring proper integration with NetBox's existing
  job infrastructure and permission model.

## [0.1.31] - 2025-08-29

### Fixes
- Fix NetBox plugin template extension registration and template inheritance (88ba309)
  - Removed incorrect ContactActions.register() call from plugin config; now using `template_extensions = [ContactActions]` inside the `template_content.py` for NetBox 4.x compatibility.
  - Updated plugin templates to extend "base/base.html" instead of "base.html", resolving Django TemplateDoesNotExist errors.
  - Documented and verified plugin installation workflow: uninstall, clean old files, and pip install from top-level directory.
  - Updated AGENT_CONTEXT.md to reflect these fixes and deployment steps.
  These changes ensure plugin UI features work and templates render correctly in NetBox 4.x.

## [0.1.30] - 2025-08-28

### Fixes
- Fix template extension registration and block duplication (9611532)
  PROBLEM:
  1. NetBox RQ worker was failing with error:
  "Failed to register template extensions: 'super' object has no
  attribute 'register_template_extensions'"
  2. Config page throwing TemplateSyntaxError due to duplicate block tags
  ROOT CAUSE:
  1. Template extension registration method changed in NetBox 4.2.x but
  our plugin was still using deprecated approach with super().register_template_extensions()
  2. Template had duplicate 'block' tags with name 'below_form'
  CHANGES:
  1. Removed plugin.py as it was interfering with navigation menu items
  2. Updated __init__.py to use correct template extension registration
  pattern for NetBox 4.2.x compatibility
  3. Fixed template block structure in config.html to prevent duplication
  TESTING:
  - Verified NetBox RQ worker starts without template extension errors
  - Confirmed config page loads successfully
  - Validated navigation menu items appear correctly

## [0.1.29] - 2025-08-28

### Other
- v0.1.29 - Add UI controls for contact deprecation behavior (d559745)
  Changes:
  - Add UI toggle for "treat disabled EntraID users as missing" setting
  - Fix missing "Run Job Manually" section in configuration page
  - Add permission checks around settings and job execution UI
  - Improve configuration page layout and organization
  The update adds user control over how the DeprecateContactsJob handles
  disabled EntraID accounts and restores the ability to trigger manual job
  runs with dry-run option from the UI.

## [0.1.28] - 2025-08-28

### Features
- feat(plugin): add EntraID resolution job and UI (f576591)
  Add a new job-based workflow to resolve Contact information from EntraID:
  - Add ResolveContactsJob implementing JobRunner interface
  - Reuses existing EntraID resolution logic from Script class
  - Supports dry-run mode for safe testing
  - Implements structured job logging
  - No scheduling dependency (on-demand only)
  - Add UI components for single-contact resolution:
  - New "Resolve in EntraID" button on Contact detail pages
  - Confirmation form with dry-run option
  - Automatic redirect to job status page
  - Security and permissions:
  - Guards all features behind netbox_entraid_tools.contact_admin
  - Proper CSRF protection on forms
  - Follows NetBox v4.2.9 security patterns
  - Templates and routing:
  - New contact_actions.html button template
  - New resolve_contact_confirm.html form template
  - Added URL route for job launch endpoint
  - Registered template extension for button injection
  Technical notes:
  - Compatible with NetBox v4.2.9 and Django 5.1.x
  - No SCRIPTS_ROOT dependency
  - Maintains separation between Graph API and business logic

## [0.1.27] - 2025-08-28

### Fixes
- fix(scripts): handle contact IDs in resolve_contact_entraid script (4724ecf)
  - Add support for resolving contact PKs to Contact objects
  - Add Graph API methods for user lookup and listing
  - Fix AttributeError when passing contact IDs instead of objects
  - Maintain separation of concerns between Graph API and business logic

## [0.1.26] - 2025-08-28

### Refactoring
- Refactor GraphClient instantiation to remove unnecessary settings argument (0080a20)
  - Updated resolve_contact_entraid.py and views.py to instantiate GraphClient without passing plugin settings, matching usage in jobs.py.
  - This resolves a TypeError caused by passing an unexpected argument to GraphClient.__init__().
  - Ensures consistent and correct usage of GraphClient across the codebase.

## [0.1.25] - 2025-08-27

### Other
- Add Migration 0004 file (9881b1b)

## [0.1.24] - 2025-08-27

### Other
- Missing views.py import directive added "from django.views import View" (6f6ecbc)
- Deleted: unused plugin.py (eb7749e)

## [0.1.23] - 2025-08-27

### Fixes
- Fixes: a character encoding issue in the run_git() function when trying to read git commit messages. The error occurs because the git output contains Unicode characters (likely smart quotes or em-dashes from the detailed commit message) that can't be decoded using the default Windows cp1252 encoding. (3eac41c)
  This change:
  1. Explicitly sets UTF-8 encoding for the subprocess output
  2. Sets environment variables to ensure git uses UTF-8 encoding
  3. Will properly handle Unicode characters in commit messages (like smart quotes, em-dashes, etc.)
  The error occurred because the commit message contained special characters (like smart quotes `'` or em-dashes `â€”`) that aren't supported in the default Windows cp1252 encoding. By forcing UTF-8, we ensure proper handling of all Unicode characters.

### Other
- Add EntraID contact update feature: (872bb35)
  - Custom link 'Update from EntraID' for tenancy.contact
  - View for detailed preview and selective field update from EntraID
  - Template shows side-by-side comparison of NetBox and EntraID fields
  - User can choose which fields to update
  - Uses NetBox-native payload builder for contact updates
  - Wires up plugin config, URLs, and view logic
  This enables admins to resolve and update contacts directly from EntraID with full control over field-level changes.
- Manually updating CHANGELOG.md (9a25f1a)

## [0.1.22] - 2025-08-27

### Features 
- (job,config,graph): optionally treat disabled Entra users as “missing” via global flag; add audit logging; fix mgmt cmd call

- Context
The deprecation job currently prunes Contact assignments only when an Entra object is *absent* in Microsoft Graph. Disabled users still “exist” and therefore are ignored, which prevents expected cleanup in environments where disabled accounts should be treated as invalid. We also noticed a minor inconsistency in the one‑shot management command’s call signature.

## What’s new
• New global flag: treat_disabled_as_missing (default: False)
  - When enabled, any Entra **user** object with `accountEnabled == false` is treated as “missing/invalid” by the job and will be deprecated and pruned the same way as a 404’d object.
  - **orgContact** objects remain out of scope for this rule (no `accountEnabled` semantics); they’re treated as valid if they exist.
  - Default is **False** to preserve current behaviour.

• End‑to‑end config wiring (UI + API + code)
  - Added `treat_disabled_as_missing` to plugin defaults (so ops can toggle via configuration without code).
  - Persisted in DB: `Settings.treat_disabled_as_missing` (BooleanField, default False) with migration `0004_settings_treat_disabled_as_missing.py`.
  - Exposed via API: `SettingsSerializer` includes the new field.
  - Exposed in UI: `SettingsForm` adds `job1_treat_disabled_as_missing` bound to the model, with help text.
  - Runtime precedence when reading config:
        DB Settings → PLUGINS_CONFIG → hard defaults.
    This lets ops flip behaviour in the Settings page while still supporting code/`configuration.py` defaults.

• Graph client enhancement
  - New `GraphClient.disabled_user_ids(ids: Iterable[str]) -> Set[str]`:
        Calls `/v1.0/users/{id}?$select=id,accountEnabled`.
        Returns the subset of IDs where `accountEnabled == false`.
        Ignores non‑user directory objects (404/endpoint mismatch).
        Fails closed to current behaviour on request/parse errors.
  - Existing `existing_object_ids()` remains the source of truth for existence via `/directoryObjects/getByIds`.

• Job logic changes (non‑breaking by default)
  - After computing `existing` and `invalid = oids - existing`, if the flag is **on** the job unions `invalid |= disabled_user_ids(existing)`.
  - Logging:
      - Always logs: `Graph lookup complete: <existing> existing, <invalid> invalid.`
      - When flag **on**: logs `Disabled users treated as invalid: <N>`.
      - When flag **off** and **dry‑run**: logs a hint if disabled users are detected but skipped.
      - In dry‑run, per‑contact reason logs when a contact is invalid due to disabled status.
  - All other deprecation behaviours (name prefix, group move, assignment deletion + Azure Table logging) are unchanged.

• Management command fix
  - `run_entraid_deprecations.py` now calls `job.run(dry_run=<bool>)` to align with the JobRunner signature (previous code passed positional args).

## Why this change
• Operational clarity: Many orgs expect disabled users to be removed from active roles/assignments in NetBox just like deleted accounts. This flag makes that policy **explicit and configurable**.
• Backward compatibility: Default remains “false” to avoid surprises.
• Auditability: Extra log lines make it obvious when disabled users drove deletions.

Examples (dry‑run)
Flag OFF:
  INFO  Evaluating 103 contact(s) with Entra OIDs…
  INFO  Graph lookup complete: 67 existing, 0 invalid.
  INFO  [dry-run] Skipping 1 disabled user(s) (treat_disabled_as_missing=False)
  SUCCESS Completed. Contacts changed: 0, assignments deleted: 0

Flag ON:
  INFO  Evaluating 103 contact(s) with Entra OIDs…
  INFO  Graph lookup complete: 67 existing, 1 invalid.
  INFO  Disabled users treated as invalid: 1
  INFO  [dry-run] Contact id=123 OID=aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee user is disabled -> treated as invalid
  SUCCESS Completed. Contacts changed: 1, assignments deleted: 3

- Rollout notes
1) Apply migration and restart workers:
     python manage.py migrate netbox_entraid_tools
     <restart rq/uwsgi as appropriate>
2) Toggle the flag in the EntraID Tools Settings UI.
   (Optional) Also support in `PLUGINS_CONFIG["netbox_entraid_tools"]["treat_disabled_as_missing"]`.
3) Perform a dry‑run first (UI button or `python manage.py run_entraid_deprecations --dry-run`).

- Performance & limits
• The disabled check issues a GET per existing ID. For typical volumes this is acceptable; if needed we can batch via `$batch` later.
• Requires Graph permissions that allow `/users/{id}?$select=id,accountEnabled`. On failures the job simply doesn’t treat the user as disabled (preserves prior behaviour).

- Files changed (high level)
• __init__.py  — add default for `treat_disabled_as_missing`.
• models.py    — add Settings.treat_disabled_as_missing.
• migrations/0004_settings_treat_disabled_as_missing.py — new.
• api/serializers.py — expose the field.
• forms.py     — add UI checkbox and bind to model.
• entra/graph.py — add `disabled_user_ids`.
• jobs.py      — read merged config; union disabled users into `invalid`; logging tweaks.
• management/commands/run_entraid_deprecations.py — fix call signature.

- Backward compatibility
No breaking changes. Default remains false; existing deployments behave identically until the flag is enabled.

Co-authored-by: cmckenzie@bacardi.com
Refs: EntraID contact hygiene / disabled-user pruning policy

## [0.1.21] - 2025-08-26

### Other
- Removed permissions entry that caused breaking change to plugin Migrations: SystemCheckError: System check identified some issues: (9bff78a)
  ERRORS:
  netbox_entraid_tools.Settings: (auth.E005) The permission codenamed 'view_settings' clashes with a builtin permission for model 'netbox_entraid_tools.Settings'.
- Minor UI update to Interval Hours and AutoSchedule fields (fafab62)

## [0.1.20] - 2025-08-26

### Features
- feat(api): Add API and permissions for Settings model (676736b)
  This commit introduces the necessary API infrastructure and permissions for the `Settings` model. This resolves a `SerializerNotFound` error during form submission and enables standard, permission-controlled API access.
  Previously, attempting to save the configuration form failed because the `Settings` model, being a `NetBoxModel`, requires an API serializer for change logging. Furthermore, even with an API endpoint, there were no standard permissions to control access.
  The following changes have been made:
  - **API Infrastructure:**
  - Created `api/serializers.py` to define a `SettingsSerializer`.
  - Created `api/views.py` to define a `SettingsViewSet` for the model.
  - Created `api/urls.py` to register the viewset and expose it via the API.
  - **Model Permissions (`models.py`):**
  - Added the standard `view_settings` permission to the model's `Meta` class. This allows administrators to grant read-only access to the settings via the API, which is a requirement for the `NetBoxModelViewSet`.
  - This change required a new database migration to be created and applied.
  These changes together ensure that the `Settings` model is fully and correctly integrated with NetBox's backend systems, allowing for successful UI saves, change logging, and secure API access.

## [0.1.19] - 2025-08-26

### Fixes
- fix(forms): Implement data binding for extensible multi-job UI (1606bdf)
  This commit resolves an issue where the redesigned configuration page was not correctly populating or saving data for job-specific fields. This was because the form logic did not account for the mapping between the new, prefixed form fields (e.g., `job1_...`) and the original, unprefixed model fields.
  The following changes have been made to implement the necessary data translation:
  - **`views.py` Refactoring:**
  - The `ConfigView` no longer uses `get_initial`. Instead, it is overridden to pass the `Settings` model instance directly to the form during initialization, which is a more robust approach.
  - The `form_valid` method is simplified to just call `form.save()`.
  - **`forms.py` Logic Implementation:**
  - An `__init__` method has been added to `SettingsForm`. It populates the prefixed form fields (e.g., `job1_storage_table_name`) with the corresponding data from the model instance (e.g., `instance.storage_table_name`) when the form is loaded.
  - The `save` method has been updated to perform the reverse operation: it takes the data submitted in the prefixed form fields and saves it back to the correct fields on the model instance before committing to the database.
  This ensures proper data binding for the new, extensible UI, allowing job-specific settings to be displayed and updated correctly.
  Also, release.py updated to ensure commit messages properly imported into change log in full.

## [0.1.18] - 2025-08-26

### Refactoring
- refactor(ui): Redesign config page for clarity and extensibility (4d91608)

## [0.1.17] - 2025-08-26

### Refactoring
- refactor(ui): Defuglify and restructure the plugin configuration page (3d5711f)

## [0.1.16] - 2025-08-26

### Fixes
- fix: update import statement for DEFAULTS in ConfigView (f7a7765)

## [0.1.15] - 2025-08-26

### Fixes
- fix: Subject: Fix Plugin Loading to Correctly Register Navigation Menu (ebaef06)

## [0.1.14] - 2025-08-26

### Fixes
- fix: feat(navigation): Register plugin in main navigation menu (ebea057)

## [0.1.13] - 2025-08-25

### Refactoring
- refactor(navigation): enhance menu structure with action buttons for EntraID Tools and remove permissions checks (c084056)

## [0.1.12] - 2025-08-25

### Fixes
- fix(plugin): update navigation for NetBox v4 compatibility (a542120)

### Other
- chore(release): v0.1.11 (c391070)
- Add Bumper for increasing Folder version number. Release process is now:   **  Bump-FolderVersion   **  Commit all changes   **  Run: `python tools/release.py --sign --push patch `   **  Create Version Specific LLM ingest text file: `python   \scripts\file-tree-builder\file-tree-builder.py` (74dcc94)
- chore(plugin): update model labels for clearer permission grouping (88d4ebf)

## [0.1.11] - 2025-08-25

### Fixes
- fix(plugin): update navigation for NetBox v4 compatibility (a542120)

### Other
- Add Bumper for increasing Folder version number. Release process is now:   **  Bump-FolderVersion   **  Commit all changes   **  Run: `python tools/release.py --sign --push patch `   **  Create Version Specific LLM ingest text file: `python   \scripts\file-tree-builder\file-tree-builder.py` (74dcc94)
- chore(plugin): update model labels for clearer permission grouping (88d4ebf)

## [0.1.10] - 2025-08-25

### Fixes
- fix(forms): add required 'fields' attribute to SettingsForm.Meta to resolve Django ImproperlyConfigured error (0aa9146)

## [0.1.9] - 2025-08-25

### Fixes
- fix: handle NetBoxEntraIDToolsConfig import for build/test environments (64fab98)

### Refactoring
- refactor: improve metadata handling in setup.py and enable plugin menu import (8058167)

### Other
- chore(release): v0.1.8 (e28d09f)

## [0.1.8] - 2025-08-25

### Fixes
- fix: handle NetBoxEntraIDToolsConfig import for build/test environments (64fab98)

### Refactoring
- refactor: improve metadata handling in setup.py and enable plugin menu import (8058167)

## [0.1.8] - 2025-08-25

### Fixes
- fixed REGEX error in release.py (e1461f7)
- fixed REGEX error in release.py (5067c3d)

### Other
- changed release.py to use 'callable replacement' in write_version_from_init() function (1968571)
- changed release.py to use ast library in read_version_from_init() function (38761c9)
- initial (3963861)

All notable changes to this project will be documented in this file.