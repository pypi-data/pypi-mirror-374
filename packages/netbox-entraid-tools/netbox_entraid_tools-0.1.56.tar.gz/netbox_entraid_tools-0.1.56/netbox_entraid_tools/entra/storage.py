import uuid
from datetime import datetime, timezone
from typing import Dict
from azure.identity import ManagedIdentityCredential
from azure.data.tables import TableServiceClient


def _table_client(account_name: str, table_name: str):
    endpoint = f"https://{account_name}.table.core.windows.net"
    cred = ManagedIdentityCredential()
    svc = TableServiceClient(endpoint=endpoint, credential=cred)
    try:
        svc.create_table_if_not_exists(table_name)
    except Exception:
        pass
    return svc.get_table_client(table_name)


def log_contact_assignment_deletion(
    *,
    account_name: str,
    table_name: str,
    contact_id: int,
    contact_name: str,
    assignment_model: str,
    assignment_id: int,
    extra: Dict = None,
) -> None:
    tc = _table_client(account_name, table_name)
    now = datetime.now(timezone.utc)
    entity = {
        "PartitionKey": now.strftime("%Y%m%d"),
        "RowKey": str(uuid.uuid4()),
        "DeletedAtUtc": now.isoformat(),
        "ContactID": contact_id,
        "ContactName": contact_name,
        "AssignmentModel": assignment_model,
        "AssignmentID": assignment_id,
    }
    if extra:
        for k, v in extra.items():
            entity[str(k)] = str(v)
    tc.upsert_entity(entity)


def log_user_status_change(
    *,
    account_name: str,
    table_name: str,
    username: str,
    previous_status: bool,
    new_status: bool,
    entra_status: bool,
    is_dry_run: bool = False,
    extra: Dict = None,
) -> None:
    """
    Log a user status change to Azure Table Storage

    Args:
        account_name: Azure Storage Account name
        table_name: Azure Table name
        username: NetBox username
        previous_status: Previous is_active status in NetBox
        new_status: New is_active status in NetBox
        entra_status: EntraID account status (accountEnabled)
        is_dry_run: Whether this is a dry run (no actual changes)
        extra: Additional data to log
    """
    if is_dry_run:
        # Don't log dry runs
        return

    tc = _table_client(account_name, table_name)
    now = datetime.now(timezone.utc)

    # Determine action type
    action = "Unknown"
    if previous_status != new_status:
        action = "Deactivated" if not new_status else "Activated"
    else:
        action = "NoChange"

    entity = {
        "PartitionKey": now.strftime("%Y%m%d"),
        "RowKey": str(uuid.uuid4()),
        "Timestamp": now.isoformat(),
        "Username": username,
        "PreviousStatus": "Active" if previous_status else "Inactive",
        "NewStatus": "Active" if new_status else "Inactive",
        "EntraStatus": "Enabled" if entra_status else "Disabled",
        "Action": action,
    }

    if extra:
        for k, v in extra.items():
            entity[str(k)] = str(v)

    tc.upsert_entity(entity)
