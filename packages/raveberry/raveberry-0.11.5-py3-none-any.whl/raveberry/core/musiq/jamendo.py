"""This module contains all Jamendo related code."""

from __future__ import annotations

import logging
from contextlib import closing
from typing import List, Optional
from urllib.parse import urlparse

import requests
from django.http.response import HttpResponse

from core.musiq import song_utils
from core.musiq.playlist_provider import PlaylistProvider
from core.musiq.song_provider import SongProvider
from core.settings import storage


class JamendoClient:
    """Interface with the Jamendo API. Taken from mopidy-jamendo."""

    def __init__(self, client_id: str) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {"user-agent": "Mopidy-Jamendo/0.1.0 Mopidy/3.0.2 CPython/3.7.5"}
        )
        self.client_id = client_id

    def get(self, url: str, params: dict = None) -> dict:
        """Perform the specified API request."""
        url = f"https://api.jamendo.com/v3.0/{url}"
        if not params:
            params = {}
        params["client_id"] = self.client_id
        try:
            with closing(self.session.get(url, params=params)) as res:
                logging.debug("Requested %s", res.url)
                res.raise_for_status()
                return res.json()
        except requests.RequestException as error:
            if (
                isinstance(error, requests.HTTPError)
                and error.response.status_code == 401
            ):
                logging.error('Invalid "client_id" used for Jamendo authentication!')
            else:
                logging.error("Jamendo API request failed: %s", error)
        return {}


class Jamendo:
    """This class contains code for both the song and playlist provider"""

    _web_client: JamendoClient = None  # type: ignore[assignment]

    @staticmethod
    def _get_web_client() -> JamendoClient:
        if Jamendo._web_client is None:
            client_id = storage.get(key="jamendo_client_id")
            Jamendo._web_client = JamendoClient(client_id=client_id)
        return Jamendo._web_client

    @property
    def web_client(self) -> JamendoClient:
        """Returns the web client if it was already created.
        If not, it is created using the client-id from mopidy-jamendo."""
        return Jamendo._get_web_client()

    def get_search_suggestions(self, query: str) -> List[str]:
        """Returns a list of suggested items for the given query."""

        if len(query.strip()) <= 1:
            # query length needs to be at least two characters
            return []

        result = self.web_client.get(
            "autocomplete", params={"prefix": query, "limit": "20"}
        )

        try:
            suggestions = result["results"]["tracks"]
        except (KeyError, TypeError):
            return []

        suggestions = [
            suggestion
            for suggestion in suggestions
            if suggestion != query and not song_utils.is_forbidden(suggestion)
        ]
        return suggestions


class JamendoSongProvider(SongProvider, Jamendo):
    """This class handles songs from Soundcloud."""

    @staticmethod
    def get_id_from_external_url(url: str) -> str:
        return [
            component
            for component in urlparse(url).path.split("/")
            if component.isdigit()
        ][0]

    @staticmethod
    def get_id_from_internal_url(url: str) -> str:
        """Returns the internal id based on the given url."""
        return url.split(":")[-1]

    def __init__(self, query: Optional[str], key: Optional[int]) -> None:
        self.type = "jamendo"
        super().__init__(query, key)

        self.external_url = None

    def check_available(self) -> bool:
        if not self.gather_metadata():
            return False
        # the default bitrate in jamendo is 96kbs
        # estimate the size of a song by multiplying with its duration
        size = self.metadata["duration"] * 96 / 8 * 1000
        return self.check_not_too_large(size)

    def gather_metadata(self) -> bool:
        """Fetches metadata for this song's uri from Jamendo."""
        if not self.id:
            results = self.web_client.get("tracks", {"search": self.query})["results"]

            result = self.first_unfiltered_item(
                results, lambda item: (item["artist_name"], item["name"])
            )
            if not result:
                return False
            self.id = result["id"]
        else:
            try:
                result = self.web_client.get("tracks", {"id": self.id})["results"][0]
            except (KeyError, IndexError):
                self.error = f"id {self.id} not found"
                return False
        assert result
        if not result["audiodownload_allowed"]:
            self.error = "streaming not allowed for this song"
            return False
        self.metadata["artist"] = result["artist_name"]
        self.metadata["title"] = result["name"]
        self.metadata["duration"] = result["duration"]
        self.metadata["internal_url"] = self.get_internal_url()
        self.metadata["external_url"] = result["shareurl"]
        self.metadata["stream_url"] = result["audio"]
        self.metadata["cached"] = False
        return True

    def get_internal_url(self) -> str:
        if not self.id:
            raise ValueError()
        return f"jamendo:track:{self.id}"

    def get_external_url(self) -> str:
        if not self.id:
            raise ValueError()
        return "https://www.jamendo.com/track/" + self.id

    def get_suggestion(self) -> str:
        result = self.web_client.get(
            "tracks/similar", params={"id": self.id, "limit": "1"}
        )

        try:
            external_url = result["results"][0]["shareurl"]
        except (IndexError, KeyError) as error:
            self.error = "no recommendation found"
            raise ValueError("No suggested song") from error

        return external_url

    def request_radio(self, session_key: str) -> HttpResponse:
        result = self.web_client.get(
            "recommendations",
            params={"id": self.id, "limit": storage.get("max_playlist_items")},
        )

        for track in result["results"]:
            external_url = track["shareurl"]
            provider = JamendoSongProvider(external_url, None)
            provider.request("", archive=False, manually_requested=False)

        return HttpResponse("queueing radio")


class JamendoPlaylistProvider(PlaylistProvider, Jamendo):
    """This class handles Jamendo Playlists."""

    @staticmethod
    def get_id_from_external_url(url: str) -> Optional[str]:
        if not url.startswith("https://www.jamendo.com/"):
            return None
        return [
            component
            for component in urlparse(url).path.split("/")
            if component.isdigit()
        ][0]

    def __init__(self, query: Optional[str], key: Optional[int]) -> None:
        self.type = "jamendo"
        super().__init__(query, key)

    def search_id(self) -> Optional[str]:
        results = self.web_client.get(
            "playlists", params={"namesearch": self.query, "limit": 1}
        )

        try:
            playlist = results["results"][0]
        except IndexError:
            self.error = "No playlist found"
            return None

        list_id = playlist["id"]
        self.title = playlist["name"]

        return list_id

    def fetch_metadata(self) -> bool:
        if self.title is None:
            result = self.web_client.get("playlists", params={"id": self.id})
            self.title = result["results"][0]["name"]

        results = self.web_client.get("playlists/tracks", params={"id": self.id})
        tracks = results["results"][0]["tracks"]

        for track in tracks:
            url = "https://www.jamendo.com/track/" + track["id"]
            self.urls.append(url)

        return True
