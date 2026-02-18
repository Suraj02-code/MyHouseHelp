import os
from pathlib import Path
import re

from django.core.management.base import BaseCommand
from django.core.files import File
from django.utils.text import slugify
from services.models import Service


class Command(BaseCommand):
    help = "Link images from a folder to Service.service_image by matching filenames to service titles"

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            type=str,
            default="images",
            help="Folder containing images to link (relative to project root)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Do not write changes, only show matches",
        )

    def handle(self, *args, **options):
        source = options["source"]
        dry_run = options["dry_run"]
        source_path = Path(source).resolve()

        if not source_path.exists() or not source_path.is_dir():
            self.stderr.write(self.style.ERROR(f"Source folder not found: {source_path}"))
            return

        # Build filename index
        exts = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
        files = [p for p in source_path.glob("**/*") if p.is_file() and p.suffix.lower() in exts]
        if not files:
            self.stdout.write("No image files found in source folder.")
            return

        def norms(s: str) -> set[str]:
            base = s.strip().lower()
            variants = {
                base,
                base.replace("_", " "),
                base.replace("-", " "),
                slugify(base),
                slugify(base).replace("-", " "),
            }
            # Strip any parenthetical content, e.g., "Full-time Maid (Monthly)" -> "Full-time Maid"
            paren_stripped = re.sub(r"\([^)]*\)", "", base).strip()
            if paren_stripped and paren_stripped != base:
                variants.update({
                    paren_stripped,
                    paren_stripped.replace("_", " "),
                    paren_stripped.replace("-", " "),
                    slugify(paren_stripped),
                    slugify(paren_stripped).replace("-", " "),
                })
            # Collapse spaces/hyphens to handle cases like "touchup painting" vs "touch up painting"
            collapse = base.replace(" ", "").replace("-", "")
            variants.add(collapse)
            variants.add(slugify(base).replace("-", ""))
            if paren_stripped:
                collapse2 = paren_stripped.replace(" ", "").replace("-", "")
                variants.add(collapse2)
                variants.add(slugify(paren_stripped).replace("-", ""))
            return variants

        file_index = {}
        for f in files:
            stem = f.stem
            for k in norms(stem):
                file_index.setdefault(k, []).append(f)

        linked = 0
        skipped = 0
        duplicates = 0

        for svc in Service.objects.all():
            if svc.service_image:  # already has image
                skipped += 1
                continue

            candidates = []
            keys = set()
            keys |= norms(svc.title)
            # Also try category+title combinations
            if svc.category and svc.category.name:
                keys |= norms(f"{svc.category.name} {svc.title}")
                keys |= norms(svc.category.name)

            for k in keys:
                if k in file_index:
                    candidates.extend(file_index[k])

            # Deduplicate preserving order
            seen = set()
            unique_candidates = []
            for c in candidates:
                if c not in seen:
                    unique_candidates.append(c)
                    seen.add(c)

            if not unique_candidates:
                continue

            # Prefer files whose stem matches slug of title exactly
            preferred_slug = slugify(svc.title)
            preferred = [p for p in unique_candidates if slugify(p.stem) == preferred_slug]
            chosen = preferred[0] if preferred else unique_candidates[0]

            if dry_run:
                self.stdout.write(f"Would link: {svc.title} <- {chosen.name}")
                linked += 1
                continue

            try:
                with chosen.open("rb") as fh:
                    django_file = File(fh)
                    target_name = f"{slugify(svc.title)}{chosen.suffix.lower()}"
                    svc.service_image.save(target_name, django_file, save=True)
                linked += 1
                self.stdout.write(self.style.SUCCESS(f"Linked image for '{svc.title}': {chosen.name}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Failed to link '{svc.title}': {e}"))

        self.stdout.write(self.style.SUCCESS(
            f"Done. Linked: {linked}, Skipped (already had image): {skipped}, Images scanned: {len(files)}"
        ))
