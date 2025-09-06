"""This module contains the base class of all playlist providers."""
import logging
import time
from typing import List, Optional, Type

from django.conf import settings
from django.db import transaction
from django.db.models.expressions import F

from core.models import (
    ArchivedPlaylist,
    ArchivedPlaylistQuery,
    PlaylistEntry,
    RequestLog,
)
from core.musiq import song_utils
from core.musiq.music_provider import MusicProvider, ProviderError
from core.musiq.song_provider import SongProvider
from core.settings import storage


class PlaylistProvider(MusicProvider):
    """The base class for playlist providers."""

    @staticmethod
    def create(
        query: Optional[str] = None, key: Optional[int] = None
    ) -> "PlaylistProvider":
        """Factory method to create a playlist provider.
        Both query and key need to be specified.
        Detects the type of provider needed and returns one of corresponding type."""
        if query is None:
            logging.error(
                "archived playlist requested but no query given (key %s)", key
            )
            raise ValueError
        if key is None:
            logging.error("archived playlist requested but no key given")
            raise ValueError
        try:
            archived_playlist = ArchivedPlaylist.objects.get(id=key)
        except ArchivedPlaylist.DoesNotExist as error:
            logging.error("archived song requested for nonexistent key %s", key)
            raise ValueError from error

        playlist_type = song_utils.determine_playlist_type(archived_playlist)
        provider_class: Optional[Type[PlaylistProvider]] = None
        if playlist_type == "local":
            from core.musiq.local import LocalPlaylistProvider

            provider_class = LocalPlaylistProvider
        elif storage.get("youtube_enabled") and playlist_type == "youtube":
            from core.musiq.youtube import YoutubePlaylistProvider

            provider_class = YoutubePlaylistProvider
        elif storage.get("spotify_enabled") and playlist_type == "spotify":
            from core.musiq.spotify import SpotifyPlaylistProvider

            provider_class = SpotifyPlaylistProvider
        elif storage.get("soundcloud_enabled") and playlist_type == "soundcloud":
            from core.musiq.soundcloud import SoundcloudPlaylistProvider

            provider_class = SoundcloudPlaylistProvider
        elif storage.get("jamendo_enabled") and playlist_type == "jamendo":
            from core.musiq.jamendo import JamendoPlaylistProvider

            provider_class = JamendoPlaylistProvider
        elif playlist_type == "playlog":
            # The playlist may contain various song types, but all of them will be archived.
            # We can use the local playlist provider to enqueue them.
            from core.musiq.local import LocalPlaylistProvider

            provider_class = LocalPlaylistProvider
        if not provider_class:
            raise ProviderError(f"No provider for given playlist: {query}, {key}")
        provider = provider_class(query, key)
        return provider

    @staticmethod
    def get_id_from_external_url(url: str) -> Optional[str]:
        """Constructs and returns the external id based on the given url."""
        raise NotImplementedError()

    def __init__(self, query: Optional[str], key: Optional[int]) -> None:
        super().__init__(query, key)
        self.ok_message = "queueing playlist"
        self.title: Optional[str] = None
        self.urls: List[str] = []

    def check_cached(self) -> bool:
        if self.key is not None:
            archived_playlist = ArchivedPlaylist.objects.get(id=self.key)
        else:
            assert self.query is not None
            try:
                list_id = self.get_id_from_external_url(self.query)
                archived_playlist = ArchivedPlaylist.objects.get(list_id=list_id)
            except (KeyError, ArchivedPlaylist.DoesNotExist):
                return False
        self.id = archived_playlist.list_id
        self.title = archived_playlist.title
        self.key = archived_playlist.id
        self.urls = [entry.url for entry in archived_playlist.entries.all()]
        return True

    def search_id(self) -> Optional[str]:
        """Fetches the id of this playlist from the internet and returns it."""
        raise NotImplementedError()

    def check_available(self) -> bool:
        if self.id is not None:
            return True
        assert self.query
        list_id = self.get_id_from_external_url(self.query)
        if list_id is None:
            list_id = self.search_id()
        if list_id is None:
            return False
        self.id = list_id
        return True

    def is_radio(self) -> bool:
        """Returns whether this playlist is a radio.
        A radio as a playlist that was created for a given song.
        The result can be different if called another time for the same song."""
        # only youtube can have persisted radios
        return False

    def fetch_metadata(self) -> bool:
        """Fetches the title and list of songs for this playlist from the internet."""
        raise NotImplementedError()

    def enqueue_placeholder(self, manually_requested) -> None:
        # Playlists have no placeholder representation.
        pass

    def remove_placeholder(self) -> None:
        pass

    def make_available(self) -> bool:
        queryset = ArchivedPlaylist.objects.filter(list_id=self.id)
        if not self.is_radio() and queryset.exists():
            archived_playlist = queryset.get()
            self.key = archived_playlist.id
            self.urls = [entry.url for entry in archived_playlist.entries.all()]
        else:
            if not self.fetch_metadata():
                return False
        return True

    def was_requested_before(self) -> bool:
        try:
            archived_playlist = ArchivedPlaylist.objects.filter(list_id=self.id).get()
            if archived_playlist.counter > 0:
                return True
        except ArchivedPlaylist.DoesNotExist:
            pass
        return False

    def on_cooldown(self) -> bool:
        # Playlist cooldown is unnecessary because cooldown is checked for each song
        return False

    def persist(self, session_key: str, archive: bool = True) -> None:
        if self.is_radio():
            return

        assert self.id
        if self.title is None:
            logging.warning("Persisting a playlist with no title (id %s)", self.id)
            self.title = ""

        with transaction.atomic():
            queryset = ArchivedPlaylist.objects.filter(list_id=self.id)
            if queryset.count() == 0:
                initial_counter = 1 if archive else 0
                archived_playlist = ArchivedPlaylist.objects.create(
                    list_id=self.id, title=self.title, counter=initial_counter
                )
                for index, url in enumerate(self.urls):
                    PlaylistEntry.objects.create(
                        playlist=archived_playlist, index=index, url=url
                    )
            else:
                if archive:
                    queryset.update(counter=F("counter") + 1)
                archived_playlist = queryset.get()

        if archive:
            ArchivedPlaylistQuery.objects.get_or_create(
                playlist=archived_playlist, query=self.query
            )

        if storage.get("logging_enabled") and session_key:
            RequestLog.objects.create(
                playlist=archived_playlist, session_key=session_key
            )

    def enqueue(self) -> None:
        for index, external_url in enumerate(self.urls):
            if index == storage.get("max_playlist_items"):
                break
            # request every url in the playlist as their own url
            try:
                song_provider = SongProvider.create(external_url=external_url)
                song_provider.request("", archive=False, manually_requested=False)
            except (ProviderError, NotImplementedError) as error:
                logging.warning(
                    "Error while enqueuing url %s to playlist %s: %s",
                    external_url,
                    self.title,
                    self.id,
                )
                logging.exception(error)
                continue

            if settings.DEBUG:
                # the sqlite database has problems if songs are pushed very fast
                # while a new song is taken from the queue. Add a delay to mitigate.
                time.sleep(1)
