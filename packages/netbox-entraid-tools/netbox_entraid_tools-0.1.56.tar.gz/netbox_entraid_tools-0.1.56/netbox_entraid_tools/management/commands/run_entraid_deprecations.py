from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run the EntraID deprecation job immediately (bypassing scheduler)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true", help="Run without committing changes"
        )

    def handle(self, *args, **options):
        from netbox_entraid_tools.jobs import DeprecateContactsJob

        job = DeprecateContactsJob()
        dry = bool(options.get("dry_run"))
        job.run(dry_run=dry)
        self.stdout.write(self.style.SUCCESS("DeprecateContactsJob completed."))
