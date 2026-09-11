"""
python manage.py scrape_dermatologists

One-off, admin-run command that pulls dermatology practice listings from
zk.mk ("Златна книга" - a public Macedonian business directory) and saves
them as Dermatologist records, so the "find a dermatologist" feature has
real contacts instead of an empty table. Student project - deliberately
no legal/ToS review here, this is a plain public-directory scrape, same
spirit as seed_skin_conditions.py being a one-off data-loading command.

Only uses the standard library + `requests` (already a dependency) - no
BeautifulSoup needed. zk.mk's markup is schema.org-annotated
(itemtype="http://schema.org/LocalBusiness", itemprop="name" etc, used
for their own SEO rich snippets), which is unusually regular and lets a
handful of regexes do the job reliably instead of guessing at CSS
classes that could change.

Coordinates cost nothing extra to grab: each listing's "Оддалеченст"
(distance) line links to Google Maps with the exact destination lat/lng
in the URL's `daddr=` parameter - that becomes Dermatologist.latitude/
longitude, used later to sort "find a dermatologist" results by
proximity (see core/services/geo.py, core/views.py).

Safe to re-run: existing rows (matched by name + phone) are left alone,
so it never clobbers an admin's manual edits (e.g. deactivating a wrong
listing). Re-running just adds any NEW listings zk.mk has gained since
last time.
"""

import re
import time

import requests
from django.core.management.base import BaseCommand

from core.models import Dermatologist

BASE_URL = "https://zk.mk/dermatoloshki-ordinacii"

# Every city zk.mk currently lists dermatology practices under (see the
# "Дерматолошки ординации по градови" sidebar on the site). Add a slug
# here if the site gains a new city later - core/services/geo.py's
# MK_CITY_COORDS should get a matching entry too, for the web city-picker.
CITY_SLUGS = [
    "skopje", "bitola", "gevgelija", "kocani", "kumanovo",
    "negotino", "ohrid", "prilep", "radovis", "strumica", "stip",
]

PAGE_SIZE = 20  # zk.mk's own pagination size (?skip=0, 20, 40, ...)
MAX_PAGES_PER_CITY = 10  # safety cap (200 listings/city) - never expected to hit this
REQUEST_DELAY_SECONDS = 0.6  # be a polite scraper, not a hammer

LISTING_MARKER = 'itemtype="http://schema.org/LocalBusiness"'

NAME_RE = re.compile(r'itemprop="name">([^<]+)<')
TEL_RE = re.compile(r'href="tel:(\d+)"')
STREET_RE = re.compile(r'itemprop="streetAddress">([^<]+)<')
CITY_RE = re.compile(r'itemprop="addressLocality">([^<]+)<')
COORDS_RE = re.compile(r'daddr=(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)')
HOURS_RE = re.compile(r'class="workingtime">([^<]+)<')
WEBSITE_RE = re.compile(r'href="([^"]+)"\s+class="website"')
DESCRIPTION_RE = re.compile(
    r'class="shortdescription sprow[^"]*"[^>]*>\s*<p>([^<]+)</p>'
)


def _unescape(text: str) -> str:
    return (
        text.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&#39;", "'")
        .strip()
    )


def _parse_listing(chunk: str) -> dict | None:
    name_match = NAME_RE.search(chunk)
    if not name_match:
        return None

    tel_match = TEL_RE.search(chunk)
    street_match = STREET_RE.search(chunk)
    city_match = CITY_RE.search(chunk)
    coords_match = COORDS_RE.search(chunk)
    hours_match = HOURS_RE.search(chunk)
    website_match = WEBSITE_RE.search(chunk)
    description_match = DESCRIPTION_RE.search(chunk)

    notes_parts = []
    if hours_match:
        notes_parts.append(f"Работно време: {_unescape(hours_match.group(1))}")
    if description_match:
        notes_parts.append(_unescape(description_match.group(1)))

    return {
        "name": _unescape(name_match.group(1)),
        "phone": _unescape(tel_match.group(1)) if tel_match else None,
        "address": _unescape(street_match.group(1)) if street_match else None,
        "city": _unescape(city_match.group(1)) if city_match else None,
        "latitude": float(coords_match.group(1)) if coords_match else None,
        "longitude": float(coords_match.group(2)) if coords_match else None,
        "website": website_match.group(1) if website_match else None,
        "notes": "\n".join(notes_parts) or None,
    }


def _fetch(url: str) -> str:
    response = requests.get(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (compatible; DermaScanAI-student-project/1.0; "
                "+https://github.com/) dermatologist-directory-scraper"
            )
        },
        timeout=15,
    )
    response.raise_for_status()
    return response.text


def _iter_city_listings(city_slug: str):
    for page in range(MAX_PAGES_PER_CITY):
        skip = page * PAGE_SIZE
        url = f"{BASE_URL}/{city_slug}" + (f"?skip={skip}" if skip else "")

        try:
            html = _fetch(url)
        except requests.RequestException as error:
            print(f"  ! Could not fetch {url}: {error}")
            return

        chunks = html.split(LISTING_MARKER)[1:]
        if not chunks:
            return  # no more listings - stop paginating this city

        for chunk in chunks:
            parsed = _parse_listing(chunk)
            if parsed:
                yield parsed

        if len(chunks) < PAGE_SIZE:
            return  # last page for this city

        time.sleep(REQUEST_DELAY_SECONDS)


class Command(BaseCommand):
    help = (
        "Scrapes dermatology practice listings from zk.mk (public MK business "
        "directory) into the Dermatologist table. Safe to re-run - never "
        "touches an existing row, only adds new ones."
    )

    def handle(self, *args, **options):
        created_count = 0
        skipped_count = 0

        for city_slug in CITY_SLUGS:
            self.stdout.write(f"Scraping {city_slug}...")
            city_created = 0

            for item in _iter_city_listings(city_slug):
                if not item.get("name"):
                    continue

                _, created = Dermatologist.objects.get_or_create(
                    name=item["name"],
                    phone=item.get("phone"),
                    defaults={
                        "city": item.get("city"),
                        "address": item.get("address"),
                        "website": item.get("website"),
                        "notes": item.get("notes"),
                        "latitude": item.get("latitude"),
                        "longitude": item.get("longitude"),
                        "is_active": True,
                    },
                )
                if created:
                    created_count += 1
                    city_created += 1
                else:
                    skipped_count += 1

            self.stdout.write(f"  {city_created} new listing(s) from {city_slug}.")
            time.sleep(REQUEST_DELAY_SECONDS)

        self.stdout.write(
            self.style.SUCCESS(
                f"Готово. Нови записи: {created_count}, веќе постоеле: {skipped_count}."
            )
        )
