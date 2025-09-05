from typing import Set, Iterable, Dict, Any, List
from datetime import datetime
from django.db import transaction
from django.conf import settings
import contextlib
from django.contrib.auth import get_user_model
from netbox.jobs import JobRunner  # v4 JobRunner API

from tenancy.models import Contact, ContactGroup, ContactAssignment

from .models import Settings as SettingsModel
from .scripts.resolve_contact_entraid import ResolveContactEntraID


class ResolveContactsJob(JobRunner):
    """
    Background job to resolve/update a contact from EntraID.
    Matches by email first, then falls back to fuzzy name matching.
    """

    class Meta:
        name = "Resolve Contacts from EntraID"
        description = "Resolve one or more NetBox contacts against EntraID and optionally write back updated fields."

    def _append_log(self, level: str, message: str) -> None:
        """
        Persist a structured log entry in Job.data (JSON-serializable).
        """
        payload = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "msg": message,
        }
        if not self.job.data:
            self.job.data = [payload]
        elif isinstance(self.job.data, list):
            self.job.data.append(payload)
        self.job.save(update_fields=["data"])

    def log_info(self, message: str) -> None:
        self._append_log("info", message)

    def log_success(self, message: str) -> None:
        self._append_log("success", message)

    def log_warning(self, message: str) -> None:
        self._append_log("warning", message)

    def log_debug(self, message: str) -> None:
        self._append_log("debug", message)

    def run(
        self, contacts: list[int] | None = None, dry_run: bool = True, **kwargs
    ) -> None:
        """
        Run the contact resolution job.

        Args:
            contacts: List of contact PKs to process
            dry_run: If True, don't save changes
        """
        if not contacts:
            self.log_warning("No contacts provided to process")
            return

        self.log_info(
            f"Processing {len(contacts)} contact(s)" + (" (dry run)" if dry_run else "")
        )

        # Log contact details for troubleshooting
        for contact_id in contacts:
            contact = Contact.objects.filter(pk=contact_id).first()
            if contact:
                self.log_debug(
                    f"Contact #{contact_id}: name='{contact.name}', email='{contact.email}', "
                    + f"entra_oid={contact.custom_field_data.get('entra_oid', 'None')}"
                )

        # Reuse existing script logic for consistency
        script = ResolveContactEntraID()

        # Add more detailed logging to help with troubleshooting
        class JobLogger:
            def __init__(self, job):
                self.job = job

            def info(self, message):
                self.job.log_info(message)

            def warning(self, message):
                self.job.log_warning(message)

            def success(self, message):
                self.job.log_success(message)

            def failure(self, message):
                self.job.log_warning(f"FAILURE: {message}")

            # Add explicit debug method for completeness
            def debug(self, message):
                self.job.log_debug(message)

        # Add our logger to capture script logs
        script.logger = JobLogger(self)

        result = script.run(
            data={
                "contacts": contacts,
                "dry_run": dry_run,
                # Don't pass ignore_disabled flag - resolve everything
            },
            commit=not dry_run,
        )

        self.log_success(result or "Job completed")


class DeprecateContactsJob(JobRunner):
    """
    Background job to deprecate contacts whose Entra ID object no longer exists.

    - Looks for contacts with custom_field_data['entra_oid']
    - Queries Microsoft Graph for existence
    - For missing OIDs:
        * Prefixes name with 'Deprecated - '
        * Moves to 'Deprecated' ContactGroup
        * Deletes ContactAssignments (optionally logs them to Azure Table Storage)
    """

    class Meta:
        name = "Tidy inactive contacts"
        description = (
            "Checks custom_field_data['entra_oid'] against Microsoft Graph; "
            "deprecates invalid contacts and logs any associated ContactAssignment "
            "deletions to Azure Table Storage."
        )

    #
    # --- Light-weight logging helpers for JobRunner (stored in job.data) ---
    #
    def _append_log(self, level: str, message: str) -> None:
        """
        Persist a structured log entry in Job.data (JSON-serializable).
        NetBox v4 doesn't expose Script-style log_* helpers on JobRunner yet.
        """
        payload = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "msg": message,
        }
        if not self.job.data:
            self.job.data = [payload]
        elif isinstance(self.job.data, list):
            self.job.data.append(payload)
        else:
            # If someone stored non-list data previously, coerce to list.
            self.job.data = [self.job.data, payload]
        self.job.save(update_fields=["data"])

    def log_info(self, message: str) -> None:
        self._append_log("INFO", message)

    def log_warning(self, message: str) -> None:
        self._append_log("WARNING", message)

    def log_success(self, message: str) -> None:
        self._append_log("SUCCESS", message)

    #
    # --- Config & helpers ---
    #
    def _get_config(self) -> Dict[str, Any]:
        # Source of truth order: DB Settings -> PLUGINS_CONFIG -> code defaults
        cfg_pc = settings.PLUGINS_CONFIG.get("netbox_entraid_tools", {}) or {}
        db = SettingsModel.objects.first()
        return {
            "storage_account_name": (
                db.storage_account_name
                if db and db.storage_account_name
                else cfg_pc.get("storage_account_name", "westeuncnetboxauto")
            ),
            "storage_table_name": (
                db.job1_storage_table_name
                if db
                and hasattr(db, "job1_storage_table_name")
                and db.job1_storage_table_name
                else cfg_pc.get("storage_table_name", "ContactAssignmentDeletions")
            ),
            "treat_disabled_as_missing": (
                db.job1_treat_disabled_as_missing
                if db and hasattr(db, "job1_treat_disabled_as_missing")
                else bool(cfg_pc.get("treat_disabled_as_missing", False))
            ),
        }

    def _contacts_with_oids(self) -> Iterable[Contact]:
        # Using custom_field_data directly is fine; v4 also exposes cf property if you prefer.
        return Contact.objects.exclude(
            custom_field_data__entra_oid__isnull=True
        ).exclude(custom_field_data__entra_oid="")

    def _ensure_deprecated_group(self) -> ContactGroup:
        group, _ = ContactGroup.objects.get_or_create(
            name="Deprecated", defaults={"slug": "deprecated"}
        )
        return group

    def _collect_oids(self, contacts: Iterable[Contact]) -> Set[str]:
        return {
            str((c.custom_field_data or {}).get("entra_oid")).strip()
            for c in contacts
            if (c.custom_field_data or {}).get("entra_oid")
        }

    def _prefix_if_needed(self, contact: Contact) -> bool:
        if not contact.name.startswith("Deprecated - "):
            contact.name = f"Deprecated - {contact.name}"
            return True
        return False

    def _move_group_if_needed(self, contact: Contact, group: ContactGroup) -> bool:
        if contact.group_id != group.id:
            contact.group = group
            return True
        return False

    def _log_and_delete_assignments(
        self,
        contact: Contact,
        commit: bool,
        storage_account: str,
        table_name: str,
    ) -> int:
        from .entra.storage import log_contact_assignment_deletion

        qs = ContactAssignment.objects.filter(contact=contact).select_related(
            "object_type"
        )

        count = 0
        for ca in qs:
            obj_type = ca.object_type
            model_label = f"{obj_type.app_label}.{obj_type.model}"
            if commit:
                try:
                    log_contact_assignment_deletion(
                        account_name=storage_account,
                        table_name=table_name,
                        contact_id=contact.id,
                        contact_name=contact.name,
                        assignment_model=model_label,
                        assignment_id=ca.id,
                        extra={"object_id": ca.object_id},
                    )
                except Exception as e:
                    self.log_warning(
                        f"Azure Table logging failed for assignment {ca.id}: {e}"
                    )
                ca.delete()
                count += 1
            else:
                self.log_info(
                    f"[dry-run] Would delete assignment {ca.id} ({model_label} -> object_id={ca.object_id})"
                )

        return count

    #
    # --- Job entry point for JobRunner (kwargs come from enqueue(...)) ---
    #
    def run(self, dry_run: bool = False, **kwargs) -> None:
        """
        Execute the job. For NetBox JobRunner, signature is arbitrary kwargs.
        Pass dry_run=True at enqueue time to preview changes.
        """
        from .entra.graph import GraphClient

        commit = not dry_run
        cfg = self._get_config()
        storage_account = cfg["storage_account_name"]
        table_name = cfg["storage_table_name"]
        treat_disabled = bool(cfg.get("treat_disabled_as_missing", False))
        contacts = list(self._contacts_with_oids())
        if not contacts:
            self.log_info("No contacts with 'entra_oid' found.")
            return

        # Log only the headline numbers up-front
        self.log_info(f"Evaluating {len(contacts)} contact(s) with Entra OIDs…")

        oids = self._collect_oids(contacts)

        client = GraphClient()
        existing = set(client.existing_object_ids(oids))
        invalid = set(oids) - existing

        # Optionally treat disabled Entra users as "invalid" for pruning
        disabled_users: Set[str] = set()
        if treat_disabled and existing:
            disabled_users = client.disabled_user_ids(existing)
            if disabled_users:
                invalid |= disabled_users
        # Summary logging
        self.log_info(
            f"Graph lookup complete: {len(existing)} existing, {len(invalid)} invalid."
        )
        if treat_disabled:
            self.log_info(f"Disabled users treated as invalid: {len(disabled_users)}")
        elif dry_run:
            # Helpful heads-up while testing with flag off
            maybe_disabled = client.disabled_user_ids(existing) if existing else set()
            if maybe_disabled:
                self.log_info(
                    f"[dry-run] Skipping {len(maybe_disabled)} disabled user(s) (treat_disabled_as_missing=False)"
                )

        deprecated_group = self._ensure_deprecated_group()

        # Only open a transaction when we actually write
        ctx = transaction.atomic() if commit else contextlib.nullcontext()
        with ctx:
            total_changed = 0
            total_deleted = 0

            for c in contacts:
                oid = str((c.custom_field_data or {}).get("entra_oid", "")).strip()

                if not oid or oid not in invalid:
                    continue
                if dry_run and oid in disabled_users:
                    self.log_info(
                        f"[dry-run] Contact id={c.id} OID={oid} user is disabled -> treated as invalid"
                    )

                changed = False
                if self._prefix_if_needed(c):
                    changed = True
                if self._move_group_if_needed(c, deprecated_group):
                    changed = True

                if changed:
                    if commit:
                        c.save()
                    else:
                        # Per-contact details only in dry runs
                        self.log_info(
                            f"[dry-run] Would update contact '{c.name}' (id={c.id})"
                        )
                    total_changed += 1

                deleted = self._log_and_delete_assignments(
                    c, commit, storage_account, table_name
                )
                total_deleted += deleted

                if dry_run:
                    self.log_info(
                        f"[dry-run] Contact id={c.id}, invalid OID={oid}, "
                        f"changed={changed}, assignments_deleted={deleted}"
                    )

            # Single, compact success line per job run
            self.log_success(
                f"Completed. Contacts changed: {total_changed}, "
                f"assignments deleted: {total_deleted}"
            )


class SyncUserStatusJob(JobRunner):
    """
    Background job to synchronize NetBox user statuses with EntraID.

    - Checks all NetBox users against EntraID
    - Updates the `is_active` flag based on EntraID account status
    - Can be run on a regular schedule to maintain consistency
    """

    class Meta:
        name = "Sync User Status with EntraID"
        description = (
            "Checks NetBox users against EntraID account status and updates the "
            "`is_active` flag accordingly. Deactivates accounts that are disabled in EntraID."
        )

    #
    # --- Light-weight logging helpers ---
    #
    def _append_log(self, level: str, message: str) -> None:
        """
        Persist a structured log entry in Job.data (JSON-serializable).
        """
        payload = {
            "ts": datetime.now(datetime.timezone.utc).isoformat() + "Z",
            "level": level,
            "msg": message,
        }
        if not self.job.data:
            self.job.data = [payload]
        elif isinstance(self.job.data, list):
            self.job.data.append(payload)
        else:
            # If someone stored non-list data previously, coerce to list
            self.job.data = [self.job.data, payload]
        self.job.save(update_fields=["data"])

    def log_info(self, message: str) -> None:
        self._append_log("INFO", message)

    def log_warning(self, message: str) -> None:
        self._append_log("WARNING", message)

    def log_success(self, message: str) -> None:
        self._append_log("SUCCESS", message)

    def log_debug(self, message: str) -> None:
        self._append_log("DEBUG", message)

    def _get_config(self) -> Dict[str, Any]:
        """Get configuration from settings"""
        cfg_pc = settings.PLUGINS_CONFIG.get("netbox_entraid_tools", {}) or {}
        db = SettingsModel.objects.first()

        # Default local user accounts to skip if not configured
        default_local_accounts = ["admin", "netbox", "system", "automation"]

        return {
            "debug_mode": db.debug_mode if db else cfg_pc.get("debug_mode", False),
            "local_user_accounts": (
                db.job2_local_user_accounts
                if db
                and hasattr(db, "job2_local_user_accounts")
                and db.job2_local_user_accounts
                else default_local_accounts
            ),
            "storage_table_name": (
                db.job2_storage_table_name
                if db
                and hasattr(db, "job2_storage_table_name")
                and db.job2_storage_table_name
                else "UserStatusChanges"
            ),
        }

    def run(self, dry_run: bool = True, **kwargs) -> None:
        """
        Execute the job to sync user statuses.

        Args:
            dry_run: If True, don't save changes (preview only)
        """
        from .entra.graph import GraphClient
        from .entra.storage import log_user_status_change  # Initialize counters

        users_checked = 0
        users_deactivated = 0
        users_reactivated = 0
        users_skipped = 0
        errors = 0

        # Get configuration
        config = self._get_config()
        debug_mode = config.get("debug_mode", False)
        local_user_accounts = config.get(
            "local_user_accounts", ["admin", "netbox", "system", "automation"]
        )
        storage_table_name = config.get("storage_table_name", "UserStatusChanges")

        # Get the storage account name from settings
        db = SettingsModel.objects.first()
        storage_account_name = (
            db.storage_account_name
            if db and hasattr(db, "storage_account_name")
            else ""
        )

        self.log_info(
            f"Starting user status sync ({'dry run' if dry_run else 'live mode'})"
        )
        if local_user_accounts:
            self.log_info(
                f"Local user accounts to skip: {', '.join(local_user_accounts)}"
            )

        # Initialize Graph API client
        client = GraphClient()
        User = get_user_model()

        # Get all NetBox users with email addresses
        netbox_users = User.objects.exclude(email="").exclude(email__isnull=True)
        total_users = netbox_users.count()

        self.log_info(f"Found {total_users} NetBox users with email addresses to check")

        # Process users in batches to avoid memory issues with large installations
        batch_size = 50
        for i in range(0, total_users, batch_size):
            batch = netbox_users[i : i + batch_size]
            self.log_info(
                f"Processing batch of {len(batch)} users ({i+1}-{min(i+batch_size, total_users)} of {total_users})"
            )

            for netbox_user in batch:
                try:
                    # Skip checking local/system accounts based on configured list
                    if netbox_user.username in local_user_accounts:
                        if debug_mode:
                            self.log_debug(
                                f"Skipping local account: {netbox_user.username}"
                            )
                        users_skipped += 1
                        continue

                    # Check if this is an EntraID user by checking their email
                    if not netbox_user.email or "@" not in netbox_user.email:
                        if debug_mode:
                            self.log_debug(
                                f"Skipping user without valid email: {netbox_user.username}"
                            )
                        users_skipped += 1
                        continue

                    # Look up the user in EntraID by email
                    entra_user = client.get_user_by_email(netbox_user.email)

                    if not entra_user:
                        # User not found in EntraID
                        self.log_warning(
                            f"User '{netbox_user.username}' ({netbox_user.email}) not found in EntraID"
                        )
                        users_skipped += 1
                        continue

                    # Check account status
                    users_checked += 1
                    account_enabled = entra_user.get("accountEnabled", True)

                    # Update the user's active status if needed
                    if not account_enabled and netbox_user.is_active:
                        self.log_warning(
                            f"User '{netbox_user.username}' is disabled in EntraID but active in NetBox"
                        )

                        # Log to Azure Table Storage
                        if storage_account_name:
                            log_user_status_change(
                                account_name=storage_account_name,
                                table_name=storage_table_name,
                                username=netbox_user.username,
                                previous_status=True,  # Active
                                new_status=False,  # Inactive
                                entra_status=False,  # Disabled
                                is_dry_run=dry_run,
                                extra={
                                    "Email": netbox_user.email,
                                    "Action": "Deactivate",
                                    "ObjectId": entra_user.get("id", ""),
                                },
                            )

                        if not dry_run:
                            netbox_user.is_active = False
                            netbox_user.save()
                            self.log_success(
                                f"Deactivated NetBox user '{netbox_user.username}'"
                            )
                        else:
                            self.log_info(
                                f"[dry-run] Would deactivate NetBox user '{netbox_user.username}'"
                            )
                        users_deactivated += 1
                    elif account_enabled and not netbox_user.is_active:
                        self.log_info(
                            f"User '{netbox_user.username}' is enabled in EntraID but inactive in NetBox"
                        )

                        # Log to Azure Table Storage
                        if storage_account_name:
                            log_user_status_change(
                                account_name=storage_account_name,
                                table_name=storage_table_name,
                                username=netbox_user.username,
                                previous_status=False,  # Inactive
                                new_status=True,  # Active
                                entra_status=True,  # Enabled
                                is_dry_run=dry_run,
                                extra={
                                    "Email": netbox_user.email,
                                    "Action": "Activate",
                                    "ObjectId": entra_user.get("id", ""),
                                },
                            )

                        if not dry_run:
                            netbox_user.is_active = True
                            netbox_user.save()
                            self.log_success(
                                f"Reactivated NetBox user '{netbox_user.username}'"
                            )
                        else:
                            self.log_info(
                                f"[dry-run] Would reactivate NetBox user '{netbox_user.username}'"
                            )
                        users_reactivated += 1
                    elif debug_mode:
                        self.log_debug(
                            f"User '{netbox_user.username}' status is in sync (enabled: {account_enabled})"
                        )

                except Exception as e:
                    self.log_warning(
                        f"Error processing user '{netbox_user.username}': {str(e)}"
                    )
                    errors += 1

        # Log summary
        log_msg = (
            f"Completed user status sync. Total users: {total_users}, Checked: {users_checked}, "
            f"Deactivated: {users_deactivated}, Reactivated: {users_reactivated}, "
            f"Skipped: {users_skipped}, Errors: {errors}"
        )

        if storage_account_name:
            log_msg += f", Changes logged to Azure table: {storage_table_name}"

        self.log_success(log_msg)
