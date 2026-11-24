import json
from pathlib import Path
from urllib.parse import quote

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from catalog.models import Category, Product

CATALOG_FILE = Path(__file__).resolve().parents[2] / "data" / "catalog.json"


def public_image(relative):
    relative = relative.replace("\\", "/").removeprefix("images/").lstrip("/")
    return "/brand-images/" + quote(relative, safe="/")


def unique_slug(base, used):
    slug = slugify(base)[:160] or "item"
    candidate = slug
    number = 2
    while candidate in used:
        candidate = f"{slug}-{number}"
        number += 1
    used.add(candidate)
    return candidate


class Command(BaseCommand):
    help = "Load Impress Seating collections and products, and create the local admin login."

    def handle(self, *args, **options):
        if not CATALOG_FILE.is_file():
            raise CommandError(f"Product file not found: {CATALOG_FILE}")
        collections = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
        used_slugs = set()
        keep = []

        for collection in collections:
            items = collection["products"]
            if not items:
                raise CommandError(f"No products listed for {collection['slug']}")
            cover = collection["image"] or items[0]["img"].removeprefix("images/")
            category, _ = Category.objects.update_or_create(
                slug=collection["slug"],
                defaults={
                    "name": collection["name"],
                    "nav_label": collection["nav_label"],
                    "subtitle": collection["subtitle"],
                    "description": collection["description"],
                    "image_url": public_image(cover),
                    "icon": collection["icon"],
                    "sort_order": collection["sort_order"],
                    "featured_on_home": True,
                },
            )
            for index, item in enumerate(items, start=1):
                file_stem = Path(item["img"]).stem
                slug = unique_slug(file_stem, used_slugs)
                keep.append(slug)
                description = (
                    f"{item['name']} is part of the {category.name} collection. "
                    "Add it to your cart or wishlist, then send an enquiry for a quote."
                )
                Product.objects.update_or_create(
                    slug=slug,
                    defaults={
                        "category": category,
                        "name": item["name"],
                        "image_url": public_image(item["img"]),
                        "size": item["size"],
                        "qty": item["qty"],
                        "style": item["style"],
                        "description": description,
                        "is_active": True,
                        "sort_order": index,
                    },
                )
            self.stdout.write(f"{category.name}: {len(items)} products")

        User = get_user_model()
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={"is_staff": True, "is_superuser": True, "email": "admin@impressseating.local"},
        )
        if created or not admin.is_superuser:
            admin.is_staff = True
            admin.is_superuser = True
            admin.set_password("admin123")
            admin.save()
            self.stdout.write("Admin login created: admin / admin123")
        else:
            self.stdout.write("Admin login already exists.")

        self.stdout.write(self.style.SUCCESS(f"Catalogue ready with {len(keep)} products."))
