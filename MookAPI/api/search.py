from flask import Blueprint, request

import re

from MookAPI.services import tracks, skills, lessons, resources, user_credentials

from . import route

bp = Blueprint('search', __name__, url_prefix="/search")

@route(bp, "/user")
def search_users():
    username = request.args.get('username')

    from MookAPI.helpers import current_local_server
    local_server = current_local_server()
    credentials = user_credentials.find(username=username, local_server=local_server)

    return [creds.user for creds in credentials]

@route(bp, "")
def search():
    search_string_var = request.args.get('searched_string')
    search_words = search_string_var.split()
    filtered_search_words = []
    regex_start = re.compile("^[^\"a-zA-Z]+")
    regex_end = re.compile("[^\"a-zA-Z]+$")
    i = 0
    while i < len(search_words):
        word = search_words[i]
        word = regex_start.sub("", word)
        word = regex_end.sub("", word)
        if word.startswith("\""):
            j = i+1
            next_word = search_words[j]
            while j < len(search_words)-1 and not next_word.endswith("\""):
                word = word + " " + next_word
                j += 1
                next_word = search_words[j]
            if next_word.endswith("\""):
                word = word + " " + next_word
                i = j
            else:
                word = search_words[i]
        filtered_search_words.append(word)
        i += 1

    results = []

    # search through tracks
    for track in tracks.queryset():
        score = 0
        for search_word in filtered_search_words:
            factor = 1
            search_word = search_word.lower()
            if search_word.startswith("\""):
                factor = len(search_word.split())
                search_word = search_word.replace("\"", "")
            if search_word in track.title.lower():
                score += 2 * factor
            if search_word in track.description.lower():
                score += 1 * factor
        if score > 0:
            results.append({"type": "track", "score": score, "document": track.to_json_dbref()})

    # search through skills
    for skill in skills.queryset():
        score = 0
        for search_word in filtered_search_words:
            factor = 1
            search_word = search_word.lower()
            if search_word.startswith("\""):
                factor = len(search_word.split())
                search_word = search_word.replace("\"", "")
            if search_word in skill.title.lower():
                score += 2 * factor
            if search_word in skill.description.lower():
                score += 1 * factor
        if score > 0:
            results.append({"type": "skill", "score": score, "document": skill.to_json_dbref()})

    # search through lessons
    for lesson in lessons.queryset():
        score = 0
        for search_word in filtered_search_words:
            factor = 1
            search_word = search_word.lower()
            if search_word.startswith("\""):
                factor = len(search_word.split())
                search_word = search_word.replace("\"", "")
            if search_word in lesson.title.lower():
                score += 2 * factor
            if search_word in lesson.description.lower():
                score += 1 * factor
        if score > 0:
            results.append({"type": "lesson", "score": score, "document": lesson.to_json_dbref()})

    # search through resources
    for resource in resources.queryset():
        score = 0
        for search_word in filtered_search_words:
            factor = 1
            search_word = search_word.lower()
            if search_word.startswith("\""):
                factor = len(search_word.split())
                search_word = search_word.replace("\"", "")
            if search_word in resource.title.lower():
                score += 2 * factor
            if search_word in resource.description.lower():
                score += 1 * factor
        if score > 0:
            results.append({"type": "resource", "score": score, "document": resource.to_json_dbref()})

    return results
