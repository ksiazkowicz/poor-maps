# -*- coding: utf-8 -*-
import copy
import html
import itertools
import poor
import urllib.parse
import json
import unicodedata

CLIENT_ID = "AIzaSyBuG3AmYTqb_JoPa6Wa5CKzbUT3tg_OuxE"
URL = ("https://maps.googleapis.com/maps/api/place/textsearch/json?{key}={query}&location={y:.5f},{x:.5f}&radius={radius:.0f}&key={CLIENT_ID}&language={language}")
GOOGLE_TYPES = {
    "Restaurant": "restaurant",
    "Grocery store": "store",
    "ATM": "atm",
    "Café": "cafe",
    "Gas station": "gas_station",
    "Hotel": None,
    "Pub": "bar"
}

cache = {}

def result_to_item(result):
    description = []
    with poor.util.silent(Exception):
        rating = float(result["rating"])
        description.append("⭐ {:.1f}/5".format(rating))
    with poor.util.silent(Exception):
        description.append(result["formatted_address"])
    with poor.util.silent(Exception):
        open_now = result["opening_hours"]["open_now"]
        description.append("\nOpen now" if open_now else "\nClosed now")
    description = ", ".join(description) + "\n"

    return {
        "title": unicodedata.normalize("NFKD", result["name"]),
        "description": description,
        "text": result.get("formatted_address", result.get("name", "")),
        "link": "http://google.com",
        "x": float(result["geometry"]["location"]["lng"]),
        "y": float(result["geometry"]["location"]["lat"])
    }

def nearby(query, near, radius, params):
    x, y = prepare_point(near)
    query_type = GOOGLE_TYPES.get(query, None)

    if not query_type:
        key = "query"
        query = urllib.parse.quote_plus(query)
    else:
        key = "type"
        query = query_type
    url = URL.format(CLIENT_ID=CLIENT_ID, language=poor.util.get_default_language("en"), **locals())

    with poor.util.silent(KeyError):
        return copy.deepcopy(cache[url])
    
    results = poor.http.get_json(url)

    guides = [result_to_item(x) for x in results["results"]]
    while results.get("next_page_token", None):
        results = poor.http.get_json(url + "&pagetoken=" + results.get("next_page_token", ""))
        guides += [result_to_item(x) for x in results["results"]]

    if results and guides[0]:
        cache[url] = copy.deepcopy((x, y, results))

    return x, y, guides


def prepare_point(point):
    """Return geocoded coordinates for `point`."""
    if isinstance(point, (list, tuple)):
        return point[0], point[1]
    geocoder = poor.Geocoder("default")
    results = geocoder.geocode(point, dict(limit=1))
    return results[0]["x"], results[0]["y"]