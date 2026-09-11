"""
geo.py

Small geography helpers for sorting the "find a dermatologist" list by
proximity (core/views.py -> dermatologists_collection). No external
geocoding API involved anywhere - see the two ways an "origin" point is
obtained:

- Mobile sends real GPS coordinates (?lat=&lng=) - works everywhere,
  since native location permissions don't require HTTPS the way browser
  geolocation does.
- Web has no HTTPS domain yet in this student project, so browser
  geolocation would silently fail on a plain-http origin. Instead it
  sends the user's chosen city (?city=), which we resolve to that city's
  center coordinates below - good enough at Macedonia's scale, and needs
  no permission prompt at all.

Each Dermatologist's own latitude/longitude is filled in by
core/management/commands/scrape_dermatologists.py, pulled straight from
the Google Maps "directions" link on the source page (no extra geocoding
call needed there either).
"""

import math

# Center coordinates for every city scrape_dermatologists.py currently
# has listings for (see zk.mk/dermatoloshki-ordinacii). Add a city here
# whenever the scraper finds listings in a new one - it's just used as a
# fallback "you are roughly here" point for the web city-picker.
MK_CITY_COORDS = {
    "скопје": (41.9981, 21.4254),
    "битола": (41.0297, 21.3347),
    "штип": (41.7420, 22.1958),
    "куманово": (42.1322, 21.7144),
    "прилеп": (41.3466, 21.5540),
    "охрид": (41.1172, 20.8016),
    "струмица": (41.4378, 22.6432),
    "гевгелија": (41.1400, 22.5010),
    "кочани": (41.9169, 22.4097),
    "неготино": (41.4844, 22.0897),
    "радовиш": (41.6386, 22.4644),
}


def city_center(city_name: str):
    """Case-insensitive lookup into MK_CITY_COORDS. Returns None if unknown."""
    if not city_name:
        return None
    return MK_CITY_COORDS.get(city_name.strip().lower())


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two lat/lng points, in kilometers."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
