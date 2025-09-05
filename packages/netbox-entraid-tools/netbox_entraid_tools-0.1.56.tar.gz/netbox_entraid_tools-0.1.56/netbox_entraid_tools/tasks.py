# netbox_entraid_tools/tasks.py
"""Lightweight tasks callable via django_rq.enqueue."""


def run_entraid_deprecations(commit: bool = True):
    from .jobs import DeprecateContactsJob

    DeprecateContactsJob().run(dry_run=not commit)
