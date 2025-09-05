from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from tenancy.models import Contact
from netbox_entraid_tools.common import contact_payload_from_user, get_debug_mode
from netbox_entraid_tools.entra.graph import GraphClient
from django.conf import settings
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import PermissionRequiredMixin
from netbox_entraid_tools.jobs import ResolveContactsJob
from netbox_entraid_tools.forms import ResolveContactJobForm


# View to update a contact from EntraID
class ResolveContactJobView(PermissionRequiredMixin, View):
    permission_required = "netbox_entraid_tools.contact_admin"

    def get(self, request, pk):
        contact = get_object_or_404(Contact, pk=pk)
        form = ResolveContactJobForm(initial={"dry_run": True})

        # Get debug mode from utility function
        debug_mode = get_debug_mode()

        return render(
            request,
            "netbox_entraid_tools/resolve_contact_confirm.html",
            {"contact": contact, "form": form, "debug_mode": debug_mode},
        )

    def post(self, request, pk):
        contact = get_object_or_404(Contact, pk=pk)
        form = ResolveContactJobForm(request.POST)

        if form.is_valid():
            dry_run = form.cleaned_data.get("dry_run", False)

            # Enqueue the job
            job = ResolveContactsJob.enqueue(contacts=[pk], dry_run=dry_run)

            messages.success(
                request, f"Job #{job.pk} enqueued to resolve contact '{contact.name}'."
            )

            # In NetBox 4.2.x, the job URL might be different
            try:
                # Try the standard NetBox 4.x job URL first
                return redirect(reverse("extras:job_result", args=[job.pk]))
            except:
                try:
                    # Fall back to older pattern if the first one fails
                    return redirect(reverse("extras:job", args=[job.pk]))
                except:
                    # If all else fails, just go back to the contact detail page
                    messages.info(
                        request,
                        f"Job #{job.pk} started. Check the Jobs list for status.",
                    )
                    return redirect(reverse("tenancy:contact", args=[contact.pk]))

        # If form is invalid, render the page again with errors
        # Get debug mode from utility function
        debug_mode = get_debug_mode()

        return render(
            request,
            "netbox_entraid_tools/resolve_contact_confirm.html",
            {"contact": contact, "form": form, "debug_mode": debug_mode},
        )


class UpdateContactFromEntraIDView(View):
    template_name = "netbox_entraid_tools/update_contact_entraid.html"

    def get(self, request, pk):
        contact = get_object_or_404(Contact, pk=pk)
        client = GraphClient()
        email = contact.email
        name = contact.name
        entra_user = None
        if email:
            entra_user = client.get_user_by_email(email)
        if not entra_user:
            all_users = client.list_users()
            from difflib import get_close_matches

            names = [u["displayName"] for u in all_users]
            matches = get_close_matches(name, names, n=5, cutoff=0.7)
            if matches:
                match_name = matches[0]
                entra_user = next(
                    u for u in all_users if u["displayName"] == match_name
                )
        fields = []
        if entra_user:
            payload = contact_payload_from_user(entra_user)
            # List of fields to compare
            compare_fields = [
                "name",
                "title",
                "phone",
                "email",
                "address",
                "link",
                "description",
            ]
            for field in compare_fields:
                current = getattr(contact, field, "")
                proposed = payload.get(field, "")
                fields.append((field, current, proposed))
            # Custom field entra_oid
            current_oid = contact.custom_field_data.get("entra_oid", "")
            proposed_oid = payload.get("entra_oid", "")
            fields.append(("entra_oid", current_oid, proposed_oid))
        else:
            # No match, show only current
            compare_fields = [
                "name",
                "title",
                "phone",
                "email",
                "address",
                "link",
                "description",
                "entra_oid",
            ]
            for field in compare_fields:
                current = (
                    getattr(contact, field, "")
                    if field != "entra_oid"
                    else contact.custom_field_data.get("entra_oid", "")
                )
                fields.append((field, current, ""))
        return render(
            request, self.template_name, {"contact": contact, "fields": fields}
        )

    def post(self, request, pk):
        contact = get_object_or_404(Contact, pk=pk)
        client = GraphClient()
        email = contact.email
        name = contact.name
        entra_user = None
        if email:
            entra_user = client.get_user_by_email(email)
        if not entra_user:
            all_users = client.list_users()
            from difflib import get_close_matches

            names = [u["displayName"] for u in all_users]
            matches = get_close_matches(name, names, n=5, cutoff=0.7)
            if matches:
                match_name = matches[0]
                entra_user = next(
                    u for u in all_users if u["displayName"] == match_name
                )
        if entra_user:
            payload = contact_payload_from_user(entra_user)
            updated_fields = []
            for field in [
                "name",
                "title",
                "phone",
                "email",
                "address",
                "link",
                "description",
            ]:
                if request.POST.get(f"update_{field}"):
                    setattr(
                        contact, field, payload.get(field, getattr(contact, field, ""))
                    )
                    updated_fields.append(field)
            # Custom field entra_oid
            if request.POST.get("update_entra_oid"):
                contact.custom_field_data["entra_oid"] = payload.get(
                    "entra_oid", contact.custom_field_data.get("entra_oid", "")
                )
                updated_fields.append("entra_oid")
            contact.save()
            if updated_fields:
                messages.success(
                    request,
                    f"Contact '{contact.name}' updated fields: {', '.join(updated_fields)}.",
                )
            else:
                messages.info(request, f"No fields were selected for update.")
        else:
            messages.error(
                request, f"No EntraID match found for contact '{contact.name}'."
            )
        return redirect(reverse("tenancy:contact", args=[contact.pk]))


# netbox_entraid_tools/views.py
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView, View
from django.contrib.auth.mixins import PermissionRequiredMixin
from netbox_entraid_tools.models import Settings
from netbox_entraid_tools.forms import SettingsForm

from .forms import SettingsForm
from .models import Settings
from .jobs import DeprecateContactsJob


class ConfigView(FormView):
    template_name = "netbox_entraid_tools/config.html"
    form_class = SettingsForm

    def get_form(self, form_class=None):
        """
        Return an instance of the form.
        This is overridden to pass the model instance to the form.
        """
        obj, _ = Settings.objects.get_or_create(pk=1)
        return self.form_class(instance=obj, **self.get_form_kwargs())

    def form_valid(self, form):
        form.save()
        return redirect(reverse("plugins:netbox_entraid_tools:config"))


class RunNowView(PermissionRequiredMixin, View):
    permission_required = "netbox_entraid_tools.contact_admin"

    def get(self, request):
        return redirect(reverse("plugins:netbox_entraid_tools:config"))

    def post(self, request):
        from django.contrib import messages
        from netbox_entraid_tools.jobs import DeprecateContactsJob, SyncUserStatusJob

        settings = Settings.objects.first()
        if not settings:
            messages.error(
                request,
                "Configuration is incomplete: Settings not found.",
            )
            return redirect(reverse("plugins:netbox_entraid_tools:config"))

        # Determine which job to run based on the button clicked
        if "run_job1" in request.POST:
            # Job 1: Deprecate Contacts
            if not settings.report_sender or not settings.job1_report_recipients:
                messages.error(
                    request,
                    "Job 1 Configuration is incomplete: Missing report sender or recipients.",
                )
                return redirect(reverse("plugins:netbox_entraid_tools:config"))

            dry = request.POST.get("job1_dry_run") == "on"
            try:
                job = DeprecateContactsJob.enqueue(dry_run=dry)
                messages.success(
                    request,
                    f"Job 1 successfully enqueued (ID: {job.pk}) with dry_run={dry}",
                )
            except Exception as e:
                messages.error(request, f"Failed to enqueue Job 1: {str(e)}")

        elif "run_job2" in request.POST:
            # Job 2: Sync User Status
            dry = request.POST.get("job2_dry_run") == "on"
            try:
                job = SyncUserStatusJob.enqueue(dry_run=dry)
                messages.success(
                    request,
                    f"Job 2 successfully enqueued (ID: {job.pk}) with dry_run={dry}",
                )
            except Exception as e:
                messages.error(request, f"Failed to enqueue Job 2: {str(e)}")

        return redirect(reverse("plugins:netbox_entraid_tools:config"))


class BulkResolveContactsView(PermissionRequiredMixin, View):
    """
    View for bulk resolving contacts from EntraID.
    This view allows admins to run the resolve job for selected contacts.
    """

    permission_required = "netbox_entraid_tools.contact_admin"

    def get(self, request):
        # Get selected contact IDs from the request
        import logging
        import traceback
        import json
        from django.contrib import messages
        from netbox_entraid_tools.models import Settings
        from netbox_entraid_tools.common import ensure_plugin_logger

        # Use our enhanced logger
        logger = ensure_plugin_logger()

        # Always log at DEBUG level for troubleshooting
        logger.info("=" * 80)
        logger.info("BulkResolveContactsView GET method called")
        logger.info(f"Request path: {request.path}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Query params: {dict(request.GET)}")
        logger.info(f"POST params: {dict(request.POST)}")
        logger.info(f"Headers: {json.dumps(dict(request.headers), indent=2)}")

        # Also log to standard NetBox logger
        std_logger = logging.getLogger(__name__)
        std_logger.info("BulkResolveContactsView GET called")

        try:
            # Look for pk parameters first - these are the selected contact IDs
            if "pk" in request.GET:
                selected_contacts = request.GET.getlist("pk")
                if debug_mode:
                    logger.info(
                        f"Found pk in GET params, selected contacts: {selected_contacts}"
                    )
            # Check for our custom _resolve parameter
            elif "_resolve" in request.GET:
                selected_contacts = request.GET.getlist("pk")
                if debug_mode:
                    logger.info(
                        f"Found _resolve in GET params, selected contacts: {selected_contacts}"
                    )
            # Fall back to standard NetBox patterns
            elif "_apply" in request.GET:
                selected_contacts = request.GET.getlist("pk")
                if debug_mode:
                    logger.info(
                        f"Found _apply in GET params, selected contacts: {selected_contacts}"
                    )
            else:
                if debug_mode:
                    logger.warning("No recognized parameters in GET request")
                selected_contacts = []
        except Exception as e:
            logger.error(f"Exception in GET parameter processing: {str(e)}")
            logger.error(traceback.format_exc())
            selected_contacts = []

        if not selected_contacts:
            messages.warning(request, "No contacts were selected for bulk resolution.")
            return redirect(reverse("tenancy:contact_list"))

        form = ResolveContactJobForm(initial={"dry_run": True})

        # Log relevant information about the contact selection
        if debug_mode:
            logger.info(f"Processing {len(selected_contacts)} selected contacts")
            logger.info(f"Selected contact IDs: {selected_contacts}")

        # Check if all selected contacts are valid IDs
        valid_contacts = []
        invalid_contacts = []

        for pk in selected_contacts:
            try:
                if pk.isdigit():
                    valid_contacts.append(pk)
                else:
                    invalid_contacts.append(pk)
            except (ValueError, AttributeError):
                invalid_contacts.append(pk)

        if invalid_contacts and debug_mode:
            logger.warning(
                f"Found invalid contact IDs in selection: {invalid_contacts}"
            )

        if not valid_contacts:
            messages.warning(
                request, "No valid contact IDs were found in the selection."
            )
            return redirect(reverse("tenancy:contact_list"))

        # Get debug mode from utility function
        debug_mode = get_debug_mode()

        return render(
            request,
            "netbox_entraid_tools/resolve_contact_confirm.html",
            {
                "bulk": True,
                "form": form,
                "selected_count": len(selected_contacts),
                "selected_contacts": selected_contacts,
                "debug_mode": debug_mode,
            },
        )

    def post(self, request):
        # Get selected contact IDs from request - handling multiple possible sources
        import logging
        import traceback
        import json
        from django.contrib import messages
        from netbox_entraid_tools.models import Settings
        from netbox_entraid_tools.common import ensure_plugin_logger

        # Use our enhanced logger
        logger = ensure_plugin_logger()

        # Always log everything during troubleshooting
        logger.info("=" * 80)
        logger.info("BulkResolveContactsView POST method called")
        logger.info(f"Request path: {request.path}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Query params: {dict(request.GET)}")
        logger.info(f"POST params: {dict(request.POST)}")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(
            f"Request body: {request.body[:1000].decode('utf-8', errors='replace') if request.body else 'Empty'}"
        )  # First 1000 chars
        logger.info(f"Headers: {json.dumps(dict(request.headers), indent=2)}")
        logger.info(f"Referer: {request.META.get('HTTP_REFERER', 'None')}")

        # Also log to standard NetBox logger
        std_logger = logging.getLogger(__name__)
        std_logger.info("BulkResolveContactsView POST called")

        # Log all available data sources for troubleshooting
        logger.info("Available data sources:")
        logger.info(f"POST data keys: {list(request.POST.keys())}")
        logger.info(f"GET data keys: {list(request.GET.keys())}")
        try:
            # Initialize selected_contacts list
            selected_contacts = []

            # Look for selection in any possible parameter names across both POST and GET
            possible_param_names = [
                "pk",
                "id",
                "object_id",
                "object_pk",
                "contact",
                "contact_id",
                "object",
            ]

            # Check all possible parameter names in POST first
            for param_name in possible_param_names:
                if param_name in request.POST:
                    selected_contacts = request.POST.getlist(param_name)
                    logger.info(
                        f"Found selection in POST[{param_name}]: {selected_contacts}"
                    )
                    break

            # If still empty, check GET parameters
            if not selected_contacts:
                for param_name in possible_param_names:
                    if param_name in request.GET:
                        selected_contacts = request.GET.getlist(param_name)
                        logger.info(
                            f"Found selection in GET[{param_name}]: {selected_contacts}"
                        )
                        break

            # Next strategy: Look for form input elements with name="pk" in the POST data
            if not selected_contacts:
                for key in request.POST.keys():
                    if key.startswith("pk_") or key.endswith("_pk"):
                        selected_contacts.append(
                            key.replace("pk_", "").replace("_pk", "")
                        )
                        logger.info(f"Found potential contact ID in key: {key}")

            # Try parsing any arrays or JSON in the request body
            if not selected_contacts and "_resolve" in request.POST:
                # In this case, we need to look for pk in both POST and GET
                if "pk" in request.POST:
                    selected_contacts = request.POST.getlist("pk")
                elif "pk" in request.GET:
                    selected_contacts = request.GET.getlist("pk")
                logger.info(
                    f"Found _resolve in POST params, selected contacts: {selected_contacts}"
                )

            # If still no contacts, check for NetBox's standard bulk form structure
            if not selected_contacts and "_apply" in request.POST:
                # In this case, we need to look for pk in both POST and GET
                if "pk" in request.POST:
                    selected_contacts = request.POST.getlist("pk")
                elif "pk" in request.GET:
                    selected_contacts = request.GET.getlist("pk")
                if debug_mode:
                    logger.info(
                        f"Found _apply in POST params, selected contacts: {selected_contacts}"
                    )

            # If still no contacts, try to parse the body as form data
            if not selected_contacts and request.body:
                from urllib.parse import parse_qs
                import json

                try:
                    # Attempt to parse the request body manually
                    body_str = request.body.decode("utf-8")
                    logger.info(f"Attempting to parse body: {body_str[:200]}")

                    # Try form-urlencoded parsing
                    parsed_body = parse_qs(body_str)
                    logger.info(f"Parsed body keys: {list(parsed_body.keys())}")

                    # Check all possible parameter names in the parsed body
                    for param_name in ["pk", "id", "object_id", "contact_id"]:
                        if param_name in parsed_body:
                            selected_contacts = parsed_body[param_name]
                            logger.info(
                                f"Found {param_name} in parsed body: {selected_contacts}"
                            )
                            break

                    # If still no contacts, try JSON parsing
                    if not selected_contacts and (
                        body_str.startswith("{") or body_str.startswith("[")
                    ):
                        try:
                            json_data = json.loads(body_str)
                            logger.info(f"Parsed JSON: {json_data}")

                            # Handle array of IDs
                            if isinstance(json_data, list):
                                selected_contacts = [str(item) for item in json_data]
                                logger.info(
                                    f"Found array of IDs in JSON: {selected_contacts}"
                                )
                            # Handle object with selection property
                            elif isinstance(json_data, dict):
                                for key in ["selected", "ids", "pk", "contacts"]:
                                    if key in json_data:
                                        items = json_data[key]
                                        if isinstance(items, list):
                                            selected_contacts = [
                                                str(item) for item in items
                                            ]
                                            logger.info(
                                                f"Found {key} in JSON: {selected_contacts}"
                                            )
                                            break
                        except json.JSONDecodeError:
                            logger.info("Body is not valid JSON")
                except Exception as e:
                    logger.error(f"Error parsing request body: {str(e)}")
                    logger.error(traceback.format_exc())

        except Exception as e:
            logger.error(f"Exception in POST parameter processing: {str(e)}")
            logger.error(traceback.format_exc())
            selected_contacts = []
        if not selected_contacts and "selected" in request.POST:
            try:
                import json

                selected_json = request.POST.get("selected")
                if selected_json:
                    selected_data = json.loads(selected_json)
                    if isinstance(selected_data, list):
                        selected_contacts = selected_data
            except:
                pass

        if not selected_contacts:
            messages.warning(request, "No contacts were selected for bulk resolution.")
            return redirect(reverse("tenancy:contact_list"))

        form = ResolveContactJobForm(request.POST)

        if form.is_valid():
            dry_run = form.cleaned_data.get("dry_run", False)

            # Filter out non-digit values and log them for debugging
            valid_contacts = []
            invalid_contacts = []

            for pk in selected_contacts:
                try:
                    if pk.isdigit():
                        valid_contacts.append(int(pk))
                    else:
                        invalid_contacts.append(pk)
                except (ValueError, AttributeError):
                    invalid_contacts.append(pk)

            if invalid_contacts:
                import logging

                logger = logging.getLogger(__name__)
                logger.warning(f"Invalid contact IDs received: {invalid_contacts}")

            # Use only valid contact IDs
            contact_ids = valid_contacts

            if not contact_ids:
                messages.warning(
                    request, "No valid contact IDs were found in the selection."
                )
                return redirect(reverse("tenancy:contact_list"))

            # Enqueue the job with selected contacts
            job = ResolveContactsJob.enqueue(contacts=contact_ids, dry_run=dry_run)

            messages.success(
                request,
                f"Job #{job.pk} enqueued to resolve {len(contact_ids)} selected contacts.",
            )

            # In NetBox 4.2.x, the job URL might be different
            try:
                # Try the standard NetBox 4.x job URL first
                return redirect(reverse("extras:job_result", args=[job.pk]))
            except:
                try:
                    # Fall back to older pattern if the first one fails
                    return redirect(reverse("extras:job", args=[job.pk]))
                except:
                    # If all else fails, just go back to the contacts list page
                    messages.info(
                        request,
                        f"Job #{job.pk} started. Check the Jobs list for status.",
                    )
                    return redirect(reverse("tenancy:contact_list"))

        # Handle the case where there's no form submission (form validation can fail if the form is missing)
        if not hasattr(form, "is_valid") or not hasattr(form, "cleaned_data"):
            logger.warning(
                "Form object appears to be invalid or missing proper attributes"
            )
            # Create a new form with defaults
            form = ResolveContactJobForm(initial={"dry_run": True})

        # If form is invalid or we had to create a new one, render the page again
        # Get debug mode from utility function
        debug_mode = get_debug_mode()

        return render(
            request,
            "netbox_entraid_tools/resolve_contact_confirm.html",
            {
                "bulk": True,
                "form": form,
                "selected_count": len(selected_contacts),
                "selected_contacts": selected_contacts,
                "debug_mode": debug_mode,
            },
        )
