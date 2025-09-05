# netbox_entraid_tools/signals.py
import logging
from datetime import timedelta, datetime, timezone

from django.conf import settings as dj_settings
from django.core.cache import cache
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .jobs import DeprecateContactsJob, SyncUserStatusJob
from .models import Settings

log = logging.getLogger(__name__)

# A stable unique ID for the scheduled jobs; used for idempotency.
JOB1_SCHEDULED_ID = "netbox_entraid_tools:deprecate_contacts:scheduled"
JOB2_SCHEDULED_ID = "netbox_entraid_tools:sync_user_status:scheduled"
# A short-lived lock key to ensure only one process schedules after migrations.
SCHEDULE_LOCK_KEY = "netbox_entraid_tools:schedule_lock"
SCHEDULE_LOCK_TTL = 120  # seconds


@receiver(post_migrate, dispatch_uid="netbox_entraid_tools_post_migrate_scheduler")
def schedule_jobs(sender, **kwargs):
    """
    Schedule recurring jobs after migrations, once per deployment.
    The Redis-backed cache `add()` is atomic: exactly one worker wins the lock.
    """
    # Only react to our own app's migrations
    app_label = getattr(sender, "name", None) or getattr(sender, "__name__", "")
    if not app_label.endswith("netbox_entraid_tools"):
        return

    # Single-worker guard (atomic add)
    if not cache.add(SCHEDULE_LOCK_KEY, "1", timeout=SCHEDULE_LOCK_TTL):
        # Another worker/process already took responsibility
        return

    try:
        # Get settings from database
        settings_obj = Settings.objects.first()

        # Schedule Job 1: Deprecate Contacts
        schedule_deprecate_contacts_job(settings_obj)

        # Schedule Job 2: Sync User Status
        schedule_sync_user_status_job(settings_obj)

    except Exception as exc:
        # Never fail migrations due to scheduling
        log.warning("netbox_entraid_tools: post_migrate scheduling failed: %s", exc)


def schedule_deprecate_contacts_job(settings_obj):
    """Schedule the DeprecateContactsJob based on settings"""
    if (
        settings_obj
        and hasattr(settings_obj, "job1_auto_schedule")
        and not settings_obj.job1_auto_schedule
    ):
        log.debug("netbox_entraid_tools: job1_auto_schedule disabled; skipping.")
        return

    try:
        # Get interval from settings
        if settings_obj and hasattr(settings_obj, "job1_interval_hours"):
            interval_minutes = max(1, settings_obj.job1_interval_hours * 60)
        else:
            # Fall back to configuration or default
            cfg = dj_settings.PLUGINS_CONFIG.get("netbox_entraid_tools", {}) or {}
            hours = int(
                cfg.get("job1_interval_hours", 6)
            )  # Updated to use job1_interval_hours
            interval_minutes = max(1, hours * 60)

        # Align to the next 5-minute boundary
        now = datetime.now(timezone.utc)
        minute = (now.minute // 5 + 1) * 5
        align = now.replace(second=0, microsecond=0)
        if minute >= 60:
            align = align.replace(minute=0) + timedelta(hours=1)
        else:
            align = align.replace(minute=minute)

        DeprecateContactsJob.enqueue_once(
            name=JOB1_SCHEDULED_ID,  # Use consistent name for idempotency
            schedule_at=align,  # stable-ish first run time
            interval=interval_minutes,  # minutes
        )
        log.info(
            "netbox_entraid_tools: scheduled DeprecateContactsJob every %d minute(s) starting %s",
            interval_minutes,
            align.isoformat(),
        )
    except Exception as exc:
        log.warning(
            "netbox_entraid_tools: scheduling DeprecateContactsJob failed: %s", exc
        )


def schedule_sync_user_status_job(settings_obj):
    """Schedule the SyncUserStatusJob based on settings"""
    if (
        settings_obj
        and hasattr(settings_obj, "job2_auto_schedule")
        and not settings_obj.job2_auto_schedule
    ):
        log.debug("netbox_entraid_tools: job2_auto_schedule disabled; skipping.")
        return

    try:
        # Get interval from settings
        if settings_obj and hasattr(settings_obj, "job2_interval_hours"):
            interval_minutes = max(1, settings_obj.job2_interval_hours * 60)
        else:
            # Default to 24 hours (1440 minutes)
            interval_minutes = 1440

        # Align to the next 5-minute boundary
        now = datetime.now(timezone.utc)
        minute = (now.minute // 5 + 1) * 5
        align = now.replace(second=0, microsecond=0)
        if minute >= 60:
            align = align.replace(minute=0) + timedelta(hours=1)
        else:
            align = align.replace(minute=minute)

        SyncUserStatusJob.enqueue_once(
            name=JOB2_SCHEDULED_ID,  # Use consistent name for idempotency
            schedule_at=align,  # stable-ish first run time
            interval=interval_minutes,  # minutes
        )
        log.info(
            "netbox_entraid_tools: scheduled SyncUserStatusJob every %d minute(s) starting %s",
            interval_minutes,
            align.isoformat(),
        )
    except Exception as exc:
        log.warning(
            "netbox_entraid_tools: scheduling SyncUserStatusJob failed: %s", exc
        )
