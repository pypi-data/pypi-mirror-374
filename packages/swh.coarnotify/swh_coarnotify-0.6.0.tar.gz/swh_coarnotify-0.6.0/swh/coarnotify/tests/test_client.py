# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from swh.coarnotify.client import (
    COARNotifyClient,
    ConsoleCOARNotifyClient,
    DevCOARNotifyClient,
    DummyCOARNotifyClient,
)


def test_dummy():
    client = DummyCOARNotifyClient()
    assert client.send({})


def test_dev(requests_mock, settings):
    settings.CN_INBOX_URL_OVERRIDE = "http://overridden/"
    client = DevCOARNotifyClient()
    m = requests_mock.post("http://overridden/")
    payload = {"target": {"inbox": "http://original/"}, "test": "dev"}
    client.send(payload)
    assert m.call_count == 1
    assert m.last_request.method == "POST"
    assert m.last_request.headers["Content-type"] == "application/ld+json"
    assert m.last_request.url == "http://overridden/"
    assert m.last_request.json() == payload


def test_basic(requests_mock, settings):
    settings.CN_INBOX_URL_OVERRIDE = "http://ignored/"
    client = COARNotifyClient()
    m = requests_mock.post("http://original/")
    payload = {"target": {"inbox": "http://original/"}, "test": "dev"}
    client.send(payload)
    assert m.call_count == 1
    assert m.last_request.method == "POST"
    assert m.last_request.headers["Content-type"] == "application/ld+json"
    assert m.last_request.url == "http://original/"
    assert m.last_request.json() == payload
    assert m.last_request.timeout == settings.CN_SEND_TIMEOUT


def test_console(capsys):
    client = ConsoleCOARNotifyClient()
    client.send({"test": True})
    captured = capsys.readouterr()
    assert "{'test': True}\n" in captured.out
