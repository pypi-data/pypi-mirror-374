from typing import Iterable, Set
import requests
from azure.identity import ManagedIdentityCredential

GRAPH_SCOPE = "https://graph.microsoft.com/.default"
GRAPH_BASE = "https://graph.microsoft.com/v1.0"


class GraphClient:
    def __init__(self):
        self._cred = ManagedIdentityCredential()

    def _headers(self) -> dict:
        token = self._cred.get_token(GRAPH_SCOPE).token
        return {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    def existing_object_ids(
        self, ids: Iterable[str], batch_size: int = 1000
    ) -> Set[str]:
        ids = [i for i in ids if i]
        existing: Set[str] = set()
        for i in range(0, len(ids), batch_size):
            batch = ids[i : i + batch_size]
            if not batch:
                continue
            resp = requests.post(
                f"{GRAPH_BASE}/directoryObjects/getByIds",
                json={"ids": batch, "types": []},
                headers=self._headers(),
                timeout=30,
            )
            resp.raise_for_status()
            payload = resp.json() or {}
            existing |= {
                obj.get("id") for obj in payload.get("value", []) if obj.get("id")
            }
        return existing

    def disabled_user_ids(self, ids: Iterable[str]) -> Set[str]:
        """
        Return the subset of ids that are 'user' objects with accountEnabled == false.
        Ignores orgContact and other directoryObject types.
        """
        disabled: Set[str] = set()
        for oid in {i for i in ids if i}:
            try:
                resp = requests.get(
                    f"{GRAPH_BASE}/users/{oid}?$select=id,accountEnabled",
                    headers=self._headers(),
                    timeout=15,
                )
                if resp.status_code == 404:
                    continue  # not a user (or missing entirely)
                resp.raise_for_status()
                data = resp.json() or {}
                # Only when the endpoint is /users/{id} and returns accountEnabled
                if data.get("id") == oid and data.get("accountEnabled") is False:
                    disabled.add(oid)
            except Exception:
                # Fail closed to current behaviour: if we can't tell, don't mark disabled
                continue
        return disabled

    def get_user_by_email(self, email: str) -> dict:
        """
        Get a user by their email address.
        Returns None if no user is found.
        """
        try:
            resp = requests.get(
                f"{GRAPH_BASE}/users?$filter=mail eq '{email}' or userPrincipalName eq '{email}'&$select=id,displayName,mail,userPrincipalName,jobTitle,mobilePhone,streetAddress,city,state,postalCode,country,department,accountEnabled",
                headers=self._headers(),
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json() or {}
            users = data.get("value", [])
            return users[0] if users else None
        except Exception as e:
            # For debugging, log the exception but still return None
            print(f"Error in get_user_by_email for '{email}': {str(e)}")
            return None

    def list_users(self, full_retrieval: bool = False, name_filter: str = None) -> list:
        """
        List users in the directory with complete pagination support.

        Args:
            full_retrieval: If True, retrieves ALL users in the directory (can be thousands)
            name_filter: Optional filter string to search by displayName (e.g., 'startswith(displayName,\'Z\')')

        Returns:
            A list of user objects.
        """
        try:
            users = []

            # Build the initial URL with appropriate filters
            base_query = f"{GRAPH_BASE}/users?$select=id,displayName,mail,userPrincipalName,jobTitle,mobilePhone,streetAddress,city,state,postalCode,country,department,accountEnabled"

            # Add name filter if provided
            if name_filter:
                base_query += f"&$filter={name_filter}"

            # Set page size
            base_query += "&$top=100"

            # For non-full retrieval, we'll optimize with ordering that might help with common name searches
            if not full_retrieval and not name_filter:
                base_query += "&$orderby=displayName"

            next_link = base_query
            page_count = 0

            while next_link:
                page_count += 1

                # Log pagination progress for large retrievals
                if page_count > 1 and page_count % 5 == 0:
                    print(
                        f"Retrieving page {page_count} of users ({len(users)} users so far)"
                    )

                resp = requests.get(
                    next_link,
                    headers=self._headers(),
                    timeout=60,  # Further increased timeout for very large directories
                )
                resp.raise_for_status()
                data = resp.json() or {}
                batch = data.get("value", [])
                users.extend(batch)

                # If not doing full retrieval and we have a reasonable number of users, stop
                if not full_retrieval and not name_filter and len(users) >= 1000:
                    print(
                        f"Reached 1000 users, stopping pagination for performance. Use name_filter or full_retrieval=True for more specific results."
                    )
                    break

                # Get the next page link if available
                next_link = data.get("@odata.nextLink")

            print(f"Retrieved {len(users)} users from {page_count} page(s)")
            return users
        except Exception as e:
            # For debugging, log the exception but still return empty list
            print(f"Error in list_users: {str(e)}")
            return []
