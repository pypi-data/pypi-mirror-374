from vezor_sdk.cliente import VzrClient

def test_ping(requests_mock):
    sdk = VzrClient("http://api.exemplo.com")
    requests_mock.get("http://api.exemplo.com/ping", json={"status": "ok"})
    assert sdk.ping() == {"status": "ok"}
