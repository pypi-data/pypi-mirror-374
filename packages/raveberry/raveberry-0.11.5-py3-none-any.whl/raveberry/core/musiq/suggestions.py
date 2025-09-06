"""This module handles the suggestions when starting to
type into the input field on the musiq page."""

from __future__ import annotations

import random
import threading
from typing import Any, Dict, Iterable, List, Mapping, TypedDict, Union, cast

from django.core.handlers.wsgi import WSGIRequest
from django.db.models import F, Q
from django.db.models.functions import Greatest
from django.http import HttpResponseBadRequest
from django.http.response import HttpResponse, JsonResponse

from core import redis
from core.models import ArchivedPlaylist, ArchivedQuery, ArchivedSong
from core.musiq import song_utils
from core.settings import storage
from core.settings.storage import PlatformEnabled, PlatformSuggestions
from main import settings

u_values_list = [
    "u_id",
    "u_url",
    "u_artist",
    "u_title",
    "u_duration",
    "u_counter",
    "u_cached",
]


class SuggestionResult(TypedDict, total=False):
    """Type that encapsulates a suggestion for a query."""

    key: Union[int, str]
    value: str
    type: str
    counter: int  # optional, not in online suggestions
    durationFormatted: str  # optional, not in online or playlist suggestions
    confusable: bool  # optional, only in song results


def random_suggestion(request: WSGIRequest) -> HttpResponse:
    """This method returns a random suggestion from the database.
    Depending on the value of :param playlist:,
    either a previously pushed playlist or song is returned."""
    suggest_playlist = request.GET["playlist"] == "true"
    if not suggest_playlist:
        if ArchivedSong.objects.count() == 0:
            return HttpResponseBadRequest("No songs to suggest from")
        index = random.randint(0, ArchivedSong.objects.count() - 1)
        song = ArchivedSong.objects.all()[index]
        return JsonResponse({"suggestion": song.displayname(), "key": song.id})

    # exclude radios from suggestions
    remaining_playlists = (
        ArchivedPlaylist.objects.all()
        .exclude(list_id__startswith="RD")
        .exclude(list_id__contains="&list=RD")
    )
    if remaining_playlists.count() == 0:
        return HttpResponseBadRequest("No playlists to suggest from")
    index = random.randint(0, remaining_playlists.count() - 1)
    playlist = remaining_playlists.all()[index]
    return JsonResponse({"suggestion": playlist.title, "key": playlist.id})


def online_suggestions(request: WSGIRequest) -> JsonResponse:
    """Returns online suggestions for a given query."""
    query = request.GET["term"]
    suggest_playlist = request.GET["playlist"] == "true"

    if storage.get("new_music_only"):
        return JsonResponse([], safe=False)

    results: List[SuggestionResult] = []
    if storage.get("online_suggestions") and redis.get("has_internet"):
        threads = []
        results_lock = threading.Lock()

        def fetch_youtube() -> None:
            from core.musiq.youtube import Youtube

            youtube_suggestions = Youtube().get_search_suggestions(query)
            youtube_suggestions = youtube_suggestions[
                : storage.get("youtube_suggestions")
            ]
            with results_lock:
                for suggestion in youtube_suggestions:
                    results.append(
                        {"key": -1, "value": suggestion, "type": "youtube-online"}
                    )

        def fetch_spotify() -> None:
            from core.musiq.spotify import Spotify

            spotify_suggestions = Spotify().get_search_suggestions(
                query, suggest_playlist
            )
            spotify_suggestions = spotify_suggestions[
                : storage.get("spotify_suggestions")
            ]
            with results_lock:
                for suggestion, external_url in spotify_suggestions:
                    results.append(
                        {
                            "key": external_url,
                            "value": suggestion,
                            "type": "spotify-online",
                        }
                    )

        def fetch_soundcloud() -> None:
            from core.musiq.soundcloud import Soundcloud

            soundcloud_suggestions = Soundcloud().get_search_suggestions(query)
            soundcloud_suggestions = soundcloud_suggestions[
                : storage.get("soundcloud_suggestions")
            ]
            with results_lock:
                for suggestion in soundcloud_suggestions:
                    results.append(
                        {"key": -1, "value": suggestion, "type": "soundcloud-online"}
                    )

        def fetch_jamendo() -> None:
            from core.musiq.jamendo import Jamendo

            jamendo_suggestions = Jamendo().get_search_suggestions(query)
            jamendo_suggestions = jamendo_suggestions[
                : storage.get("jamendo_suggestions")
            ]
            with results_lock:
                for suggestion in jamendo_suggestions:
                    results.append(
                        {"key": -1, "value": suggestion, "type": "jamendo-online"}
                    )

        suggestion_fetchers = {
            "youtube": fetch_youtube,
            "spotify": fetch_spotify,
            "soundcloud": fetch_soundcloud,
            "jamendo": fetch_jamendo,
        }

        for platform in ["youtube", "spotify", "soundcloud", "jamendo"]:
            if (
                storage.get(cast(PlatformEnabled, f"{platform}_enabled"))
                and storage.get(cast(PlatformSuggestions, f"{platform}_suggestions"))
                > 0
            ):
                thread = threading.Thread(target=suggestion_fetchers[platform])
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()

    return JsonResponse(results, safe=False)


def _offline_playlist_suggestions(query: str) -> List[SuggestionResult]:
    results: List[SuggestionResult] = []
    terms = query.split()
    remaining_playlists = ArchivedPlaylist.objects.prefetch_related("queries")
    # exclude radios from suggestions
    remaining_playlists = remaining_playlists.exclude(list_id__startswith="RD").exclude(
        list_id__contains="&list=RD"
    )

    # we could have more strict types with TypedDicts,
    # but massaging both QuerySets into a single Type would require asserts/casts,
    # which have little performance impact but should be avoided in this critical codepath
    playlist_results: Iterable[Mapping[str, Any]]
    if settings.DEBUG:
        matching_playlists = remaining_playlists
        for term in terms:
            matching_playlists = matching_playlists.filter(
                Q(title__icontains=term) | Q(queries__query__icontains=term)
            )

        playlist_results = (
            matching_playlists.order_by("-counter")
            .values("id", "title", "counter")
            .distinct()[: storage.get("number_of_suggestions")]
        )
    else:
        from django.contrib.postgres.search import TrigramWordSimilarity

        similar_playlists = remaining_playlists.annotate(
            title_similarity=TrigramWordSimilarity(query, "title"),
            query_similarity=TrigramWordSimilarity(query, "queries__query"),
            max_similarity=Greatest("title_similarity", "query_similarity"),
        )

        playlist_results = (
            similar_playlists.order_by("-max_similarity")
            .values("id", "title", "counter")
            .distinct()[: storage.get("number_of_suggestions")]
        )
    for playlist in playlist_results:
        archived_playlist = ArchivedPlaylist.objects.get(id=playlist["id"])
        platform = song_utils.determine_playlist_type(archived_playlist)
        result_dict: SuggestionResult = {
            "key": playlist["id"],
            "value": playlist["title"],
            "counter": playlist["counter"],
            "type": platform,
        }
        first_entry = archived_playlist.entries.first()
        if first_entry and platform == "local":
            # don't suggest local playlists if their first song is not cached
            # i.e. not at the expected location
            try:
                first_song = ArchivedSong.objects.filter(url=first_entry.url).get()
                if not first_song.cached:
                    continue
            except ArchivedSong.DoesNotExist:
                continue
        else:
            # don't suggest songs if the respective platform is disabled
            assert platform in ["youtube", "spotify", "soundcloud", "jamendo"]
            if not storage.get(cast(PlatformEnabled, f"{platform}_enabled")):
                continue
        results.append(result_dict)
    return results


def _postgres_song_results(query: str) -> List[Dict[str, Union[int, str, float]]]:
    from django.contrib.postgres.search import TrigramWordSimilarity

    # Songs and queries that lead to the songs should both be searched.
    # However, they are stored in two different tables.
    # We first filter for similarity in each table separately (query <> artist, title).
    # Then, we union the subqueries and order the result.

    # We calculate the similarity for the respective other table as well.
    # (query for ArchivedSong and artist,title for ArchivedQuery).
    # This can't happen after the union, union-querysets are limited in functionality.
    # https://docs.djangoproject.com/en/3.2/ref/models/querysets/#union

    # In the select statement of a query,
    # django first lists all values and then all aliases.
    # This is problematic during a union which only cares about the order of the values.
    # To make sure that the right values are combined, annotate all values with an alias.
    # https://stackoverflow.com/questions/60562759/incorrect-results-with-annotate-values-union-in-django

    # The Greatest function of postgres returns the greatest non-null value.
    # For other backends, the similarity values would need to be coalesced to 0
    # otherwise the max_similarity would be null if one of the fields is null

    similar_queries = (
        ArchivedQuery.objects.filter(Q(query__trigram_word_similar=query))
        .annotate(u_id=F("song__id"))
        .annotate(u_url=F("song__url"))
        .annotate(u_artist=F("song__artist"))
        .annotate(u_title=F("song__title"))
        .annotate(u_duration=F("song__duration"))
        .annotate(u_counter=F("song__counter"))
        .annotate(u_cached=F("song__cached"))
        .annotate(u_query=F("query"))
        .annotate(artist_similarity=TrigramWordSimilarity(query, "u_artist"))
        .annotate(title_similarity=TrigramWordSimilarity(query, "u_title"))
        .annotate(query_similarity=TrigramWordSimilarity(query, "u_query"))
        .annotate(
            max_similarity=Greatest(
                "artist_similarity", "title_similarity", "query_similarity"
            )
        )
        .values(*u_values_list, "u_query", "max_similarity")
    )

    similar_songs = (
        ArchivedSong.objects.filter(
            Q(artist__trigram_word_similar=query) | Q(title__trigram_word_similar=query)
        )
        .annotate(u_id=F("id"))
        .annotate(u_url=F("url"))
        .annotate(u_artist=F("artist"))
        .annotate(u_title=F("title"))
        .annotate(u_duration=F("duration"))
        .annotate(u_counter=F("counter"))
        .annotate(u_cached=F("cached"))
        .annotate(u_query=F("queries__query"))
        .annotate(artist_similarity=TrigramWordSimilarity(query, "u_artist"))
        .annotate(title_similarity=TrigramWordSimilarity(query, "u_title"))
        .annotate(query_similarity=TrigramWordSimilarity(query, "u_query"))
        .annotate(
            max_similarity=Greatest(
                "artist_similarity", "title_similarity", "query_similarity"
            )
        )
        .values(*u_values_list, "u_query", "max_similarity")
    )

    query_result = similar_songs.union(similar_queries)

    query_result = query_result.order_by("-max_similarity", "u_artist", "u_title")[
        : storage.get("number_of_suggestions")
    ]

    # The selected values need to contain the field by which the set is ordered.
    # Some entries are duplicated if they have different (but high) similarities.
    # Distinct is not allowed after a union.
    # Thus, duplicates need to be eliminated in python separately.
    song_results = list({song["u_id"]: song for song in query_result}.values())

    # This is the same query without using union.
    # It does not use indexes and is thus a lot slower.
    # similar_songs = (
    #   ArchivedSong.objects.select_related()
    #   .filter(
    #       Q(artist__trigram_word_similar=query)
    #       | Q(title__trigram_word_similar=query)
    #       | Q(queries__query__trigram_word_similar=query)
    #   )
    #   .annotate(artist_similarity=TrigramWordSimilarity(query, "artist"))
    #   .annotate(title_similarity=TrigramWordSimilarity(query, "title"))
    #   .annotate(
    #       query_similarity=Coalesce(
    #           TrigramWordSimilarity(query, "queries__query"), 0
    #       )
    #   )
    #   .annotate(
    #       max_similarity=Greatest(
    #           "artist_similarity", "title_similarity", "query_similarity"
    #       )
    #   )
    #   .values(*values_list, "max_similarity")
    #   .order_by("-max_similarity", "artist", "title")[:20]
    # )

    return song_results


def _offline_song_suggestions(query: str) -> List[SuggestionResult]:
    results: List[SuggestionResult] = []
    terms = query.split()
    song_results: Iterable[Mapping[str, Any]]
    if settings.DEBUG:
        # Testing the whole table whether it contains any term is quite costly.
        # Used for sqlite3 which does not have a similarity function.
        matching_songs = ArchivedSong.objects.prefetch_related("queries")
        for term in terms:
            matching_songs = matching_songs.filter(
                Q(title__icontains=term)
                | Q(artist__icontains=term)
                | Q(queries__query__icontains=term)
            )

        song_results = (
            matching_songs.order_by("-counter")
            # annotate with same values as in the postgres case to have a consistent interface
            .annotate(
                u_id=F("id"),
                u_url=F("url"),
                u_artist=F("artist"),
                u_title=F("title"),
                u_duration=F("duration"),
                u_counter=F("counter"),
                u_cached=F("cached"),
            )
            .values(*u_values_list)
            .distinct()[: storage.get("number_of_suggestions")]
        )

        # Perhaps this could be combined with the similarity search
        # to improve usability with the right weighting.
        # matching_songs = matching_songs.annotate(
        #    artist_similarity=Coalesce(TrigramWordSimilarity(query, "artist"), 0),
        #    title_similarity=Coalesce(TrigramWordSimilarity(query, "title"), 0),
        #    query_similarity=Coalesce(TrigramWordSimilarity(query, "queries__query"), 0),
        #    max_similarity=Greatest(
        #        "artist_similarity", "title_similarity", "query_similarity"
        #    ),
        # )

        # To combine, use union instead of | (or) in order to access the annotated values
        # similar_songs = union(matching_songs)
    else:
        song_results = _postgres_song_results(query)

    has_internet = redis.get("has_internet")
    for song in song_results:
        if song_utils.is_forbidden(song["u_artist"]) or song_utils.is_forbidden(
            song["u_title"]
        ):
            continue

        platform = song_utils.determine_url_type(song["u_url"])
        # don't suggest online songs when we don't have internet
        if not has_internet and not song["u_cached"]:
            continue
        if platform == "local":
            # don't suggest local songs if they are not cached (=not at expected location)
            if not song["u_cached"]:
                continue
        else:
            # don't suggest songs if the respective platform is disabled
            assert platform in ["youtube", "spotify", "soundcloud", "jamendo"]
            if not storage.get(cast(PlatformEnabled, f"{platform}_enabled")):
                continue
        result_dict: SuggestionResult = {
            "key": song["u_id"],
            "value": song_utils.displayname(song["u_artist"], song["u_title"]),
            "counter": song["u_counter"],
            "type": platform,
            "durationFormatted": song_utils.format_seconds(song["u_duration"]),
        }
        results.append(result_dict)
    # mark suggestions whose displayname is identical
    seen_values: Dict[str, int] = {}
    for index, result in enumerate(results):
        if result["value"] in seen_values:
            result["confusable"] = True
            results[seen_values[result["value"]]]["confusable"] = True
        seen_values[result["value"]] = index
    return results


def offline_suggestions(request: WSGIRequest) -> JsonResponse:
    """Returns offline suggestions for a given query."""
    query = request.GET["term"]
    suggest_playlist = request.GET["playlist"] == "true"

    if storage.get("new_music_only"):
        return JsonResponse([], safe=False)

    if suggest_playlist:
        results = _offline_playlist_suggestions(query)
    else:
        results = _offline_song_suggestions(query)

    return JsonResponse(results, safe=False)
