from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from services.models import Service

class Command(BaseCommand):
    help = "Report which services lack images and which image files are unused in the source folder"

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            type=str,
            default="images",
            help="Folder containing images to link (relative to project root)",
        )

    def handle(self, *args, **options):
        source = options["source"]
        source_path = Path(source).resolve()

        self.stdout.write(f"Source folder: {source_path}")
        if not source_path.exists():
            self.stdout.write(self.style.ERROR("Source folder does not exist."))
            return

        exts = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
        files = [p for p in source_path.glob("**/*") if p.is_file() and p.suffix.lower() in exts]
        self.stdout.write(f"Found {len(files)} image files in source.")

        # Services without images
        missing = list(Service.objects.filter(service_image="")) + list(Service.objects.filter(service_image__isnull=True))
        missing_titles = sorted({s.title for s in missing})
        if missing_titles:
            self.stdout.write(self.style.WARNING("Services without images:"))
            for t in missing_titles:
                self.stdout.write(f" - {t}")
        else:
            self.stdout.write(self.style.SUCCESS("All services have images set."))

        # Images already used in media
        used_files = set()
        for s in Service.objects.exclude(service_image="").exclude(service_image__isnull=True):
            try:
                used_files.add(Path(s.service_image.path).name)
            except Exception:
                pass

        unused = []
        for f in files:
            if f.name not in used_files:
                unused.append(f)

        if unused:
            self.stdout.write(self.style.WARNING("Unused image files in source:"))
            for f in sorted(unused):
                self.stdout.write(f" - {f.name}")
        else:
            self.stdout.write(self.style.SUCCESS("No unused images in source (all matched or set already)."))
