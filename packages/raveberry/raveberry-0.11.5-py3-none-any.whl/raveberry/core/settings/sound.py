"""This module handles all settings related to sound output."""
from __future__ import annotations

import logging
import re
import subprocess
import time
from threading import Thread
from typing import Optional

from django.conf import settings as conf
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse

from core import redis, util
from core.models import CurrentSong
from core.settings import settings, storage, system
from core.settings.settings import control
from core.tasks import app

# to control that only one bluetoothctl process is active at a time
# we use a redis variable instead of a redis lock
# we need to release the lock(=kill the process) in a different request than the one that started it
# this made using the lock complicated, and only one admin should be using the page at once anyway

# bluetooth_devices: List[Dict[str, str]] = []


@control
def set_backup_stream(request: WSGIRequest) -> None:
    """Sets the given internet stream as backup stream."""
    stream = str(request.POST.get("value"))
    storage.put("backup_stream", stream)


def _get_bluetoothctl_line(bluetoothctl: subprocess.Popen) -> str:
    assert bluetoothctl.stdout
    line = bluetoothctl.stdout.readline().decode()
    ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
    line = ansi_escape.sub("", line)
    line = line.strip()
    return line


def _start_bluetoothctl() -> Optional[subprocess.Popen]:
    if redis.get("bluetoothctl_active"):
        return None
    redis.put("bluetoothctl_active", True)
    bluetoothctl = subprocess.Popen(
        ["bluetoothctl"], stdin=subprocess.PIPE, stdout=subprocess.PIPE
    )
    return bluetoothctl


def _stop_bluetoothctl(bluetoothctl: subprocess.Popen) -> None:
    assert bluetoothctl.stdin
    bluetoothctl.stdin.close()
    bluetoothctl.wait()
    redis.put("bluetoothctl_active", False)


@app.task
def _scan_bluetooth() -> None:
    bluetoothctl = _start_bluetoothctl()
    redis.put("bluetooth_devices", [])
    assert bluetoothctl and bluetoothctl.stdin

    bluetoothctl.stdin.write(b"devices\n")
    bluetoothctl.stdin.write(b"scan on\n")
    bluetoothctl.stdin.flush()
    while True:
        line = _get_bluetoothctl_line(bluetoothctl)
        if not line:
            break
        # match old devices
        match = re.match(r"Device (\S*) (.*)", line)
        # match newly scanned devices
        # We need the '.*' at the beginning of the line to account for control sequences
        if not match:
            match = re.match(r".*\[NEW\] Device (\S*) (.*)", line)
        if match:
            address = match.group(1)
            name = match.group(2)
            # filter unnamed devices
            # devices named after their address are no speakers
            if re.match("[A-Z0-9][A-Z0-9](-[A-Z0-9][A-Z0-9]){5}", name):
                continue
            bluetooth_devices = redis.get("bluetooth_devices")
            bluetooth_devices.append({"address": address, "name": name})
            redis.put("bluetooth_devices", bluetooth_devices)
            settings.update_state()


@control
def set_bluetooth_scanning(request: WSGIRequest) -> HttpResponse:
    """Enables scanning of bluetooth devices."""
    enabled = request.POST.get("value") == "true"
    if enabled:
        if redis.get("bluetoothctl_active"):
            return HttpResponseBadRequest("Already Scanning")

        _scan_bluetooth.delay()
        return HttpResponse("Started scanning")

    if not redis.get("bluetoothctl_active"):
        return HttpResponseBadRequest("Currently not scanning")
    # this is another request, so we don't have a handle of the current bluetoothctl process
    # terminate the process by name and release the lock
    subprocess.call("pkill bluetoothctl".split())
    redis.put("bluetoothctl_active", False)
    return HttpResponse("Stopped scanning")


@control
def connect_bluetooth(request: WSGIRequest) -> HttpResponse:
    """Connect to a given bluetooth device."""
    address = request.POST.get("address")
    if address is None or address == "":
        return HttpResponseBadRequest("No device selected")
    bluetoothctl = _start_bluetoothctl()
    if not bluetoothctl:
        return HttpResponseBadRequest("Stop scanning before connecting")

    assert bluetoothctl.stdin
    error = ""

    # A Function that acts as a timeout for unexpected errors (or timeouts)
    def _timeout() -> None:
        nonlocal error
        time.sleep(20)
        error = "Timed out"
        if bluetoothctl is not None:
            _stop_bluetoothctl(bluetoothctl)

    Thread(target=_timeout).start()

    # Sometimes, pairing hangs forever. Since connecting alone is enough, skip pairing.
    # bluetoothctl.stdin.write(b"pair " + address.encode() + b"\n")
    # bluetoothctl.stdin.flush()
    # while True:
    #     line = _get_bluetoothctl_line(bluetoothctl)
    #     if not line:
    #         break
    #     if re.match(".*Device " + address + " not available", line):
    #         error = "Device unavailable"
    #         break
    #     if re.match(".*Failed to pair: org.bluez.Error.AlreadyExists", line):
    #         break
    #     if re.match(".*Pairing successful", line):
    #         break

    # if error:
    #     _stop_bluetoothctl()
    #     return HttpResponseBadRequest(error)

    bluetoothctl.stdin.write(b"connect " + address.encode() + b"\n")
    bluetoothctl.stdin.flush()
    while True:
        line = _get_bluetoothctl_line(bluetoothctl)
        if not line:
            break
        if re.match(".*Device " + address + " not available", line):
            error = "Device unavailable"
            break
        if re.match(".*Failed to connect: org.bluez.Error.Failed", line):
            error = "Connect Failed"
            break
        if re.match(".*Failed to connect: org.bluez.Error.InProgress", line):
            error = "Connect in progress"
            break
        if re.match(".*Connection successful", line):
            break
    # trust the device to automatically reconnect when it is available again
    bluetoothctl.stdin.write(b"trust " + address.encode() + b"\n")
    bluetoothctl.stdin.flush()

    _stop_bluetoothctl(bluetoothctl)
    if error:
        return HttpResponseBadRequest(error)

    return HttpResponse("Connected. Set output device to activate.")


@control
def disconnect_bluetooth(request: WSGIRequest) -> HttpResponse:
    """Untrusts a given bluetooth device to prevent automatic reconnects.
    Does not unpair or remove the device."""
    address = request.POST.get("address")
    if address is None or address == "":
        return HttpResponseBadRequest("No device selected")
    bluetoothctl = _start_bluetoothctl()
    if not bluetoothctl:
        return HttpResponseBadRequest("Stop scanning before disconnecting")
    assert bluetoothctl.stdin
    error = ""

    bluetoothctl.stdin.write(b"untrust " + address.encode() + b"\n")
    bluetoothctl.stdin.flush()
    while True:
        line = _get_bluetoothctl_line(bluetoothctl)
        if not line:
            break
        if re.match(".*Device " + address + " not available", line):
            error = "Device unavailable"
            break
        if re.match(".*untrust succeeded", line):
            break

    _stop_bluetoothctl(bluetoothctl)
    if error:
        return HttpResponseBadRequest(error)
    return HttpResponse("Disconnected")


@control
def set_feed_cava(request: WSGIRequest) -> None:
    """Enables or disables whether mopidy should output to the cava fake device."""
    enabled = request.POST.get("value") == "true"
    storage.put("feed_cava", enabled)
    # update mopidy config to apply the change
    system.update_mopidy_config("pulse")


@control
def list_outputs(_request: WSGIRequest) -> JsonResponse:
    """Returns a list of all sound output devices currently available."""
    fakesink = {"id": "fakesink", "name": "No playback"}
    client = {"id": "client", "name": "Browser playback"}
    icecast = {"id": "icecast", "name": "Icecast"}
    snapcast = {"id": "snapcast", "name": "Snapcast"}

    if conf.DOCKER or not redis.get("mopidy_available"):
        sinks = [fakesink, client]
    else:
        output = subprocess.check_output(
            "pactl list short sinks".split(),
            env={"PULSE_SERVER": conf.PULSE_SERVER},
            universal_newlines=True,
        )
        tokenized_lines = [line.split() for line in output.splitlines()]

        sinks = [fakesink, client, icecast, snapcast]
        for sink in tokenized_lines:
            if len(sink) < 2:
                continue
            sink_id = sink[1]
            try:
                sink_name = sink_id.split(".")[1]
            except IndexError:
                sink_name = sink_id
            sinks.append({"id": f"pulse-{sink_id}", "name": f"[local] {sink_name}"})

    if storage.get("spotify_enabled"):
        from core.musiq.spotify import Spotify

        for device in Spotify.device_api().devices()["devices"]:
            sinks.append(
                {"id": f"spotify-{device['id']}", "name": f"[spotify] {device['name']}"}
            )

    return JsonResponse(sinks, safe=False)


def _set_output(output: str) -> HttpResponse:
    icecast_installed = util.service_installed("icecast2")
    snapcast_installed = util.service_installed("snapserver")

    use_spotify_player = False

    if output == "fakesink" or output == "client":
        mopidy_output = "fakesink"
    elif output == "icecast":
        if not icecast_installed:
            return HttpResponseBadRequest("Please install icecast2")

        subprocess.call(["sudo", "/usr/local/sbin/raveberry/enable_icecast"])
        mopidy_output = "icecast"
    elif output == "snapcast":
        if not snapcast_installed:
            return HttpResponseBadRequest("Please install snapserver")

        subprocess.call(["sudo", "/usr/local/sbin/raveberry/enable_snapcast"])
        mopidy_output = "snapcast"
    elif output.startswith("spotify-") and storage.get("spotify_enabled"):
        output = output[len("spotify-") :]
        from core.musiq.spotify import Spotify

        from spotipy import SpotifyException

        try:
            Spotify.device_api().transfer_playback(output)
        except SpotifyException:
            return HttpResponseBadRequest("Device not available")
        use_spotify_player = True
        mopidy_output = "fakesink"
    elif output.startswith("pulse-"):
        output = output[len("pulse-") :]
        try:
            subprocess.run(
                ["pactl", "set-default-sink", output],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                env={"PULSE_SERVER": conf.PULSE_SERVER},
                check=True,
            )
            mopidy_output = "pulse"
        except subprocess.CalledProcessError as error:
            return HttpResponseBadRequest(error.stderr)
    else:
        logging.warning("Unknown sound output requested. Setting to fakesink.")
        mopidy_output = "fakesink"

    if icecast_installed and output != "icecast":
        subprocess.call(["sudo", "/usr/local/sbin/raveberry/disable_icecast"])
    if snapcast_installed and output != "snapcast":
        subprocess.call(["sudo", "/usr/local/sbin/raveberry/disable_snapcast"])

    system.update_mopidy_config(mopidy_output)

    if use_spotify_player:
        redis.put("active_player", "spotify")
    elif not redis.get("mopidy_available"):
        redis.put("active_player", "fake")
    else:
        redis.put("active_player", "mopidy")

    return HttpResponse(
        "Output was set. Restarting the current song might be necessary."
    )


@control
def set_output(request: WSGIRequest) -> HttpResponse:
    """Sets the given device as default output device."""
    output = request.POST.get("value")
    if not output:
        return HttpResponseBadRequest("No output selected")

    if output == storage.get("output"):
        return HttpResponseBadRequest("Output unchanged")

    storage.put("output", output)

    if conf.DOCKER:
        return HttpResponse()
    else:
        return _set_output(output)


@control
def delete_current_song(_request: WSGIRequest) -> HttpResponse:
    """Force skips the current song by deleting it from the database."""
    try:
        current_song = CurrentSong.objects.get()
        current_song.delete()
        return HttpResponse()
    except CurrentSong.DoesNotExist:
        return HttpResponseBadRequest("No song playing")


@control
def restart_player(_request: WSGIRequest) -> None:
    """Restarts mopidy."""
    system.restart_mopidy()
