# -*- coding: utf-8 -*-
import copy
import poor
import re
import urllib.parse
import html
import itertools
import json
import unicodedata


CLIENT_ID = "AIzaSyCKBeJvGWhpJLjLYos00K13Sfhx0IwacYU"
URL = ("https://maps.googleapis.com/maps/api/geocode/json?address={query}&key={CLIENT_ID}&language={lang}")

cache = {}

def geocode(query, params):
    """Return a list of dictionaries of places matching `query`."""
    query = urllib.parse.quote_plus(query)
    limit = params.get("limit", 10)
    lang = poor.util.get_default_language("en")
    url = URL.format(CLIENT_ID=CLIENT_ID, **locals())
    with poor.util.silent(KeyError):
        return copy.deepcopy(cache[url])
    results = poor.http.get_json(url)["results"]
    results = list(map(poor.AttrDict, results))
    results = [{
        "title": result.formatted_address,
        "description": result.geometry.location_type,
        "x": float(result.geometry.location.lng),
        "y": float(result.geometry.location.lat),
     } for result in results]
    if results and results[0]:
        cache[url] = copy.deepcopy(results)
    return results
