from vzr_pybridge.cliente import VzrPyBridge

def test_ping(requests_mock):
    sdk = VzrPyBridge("http://api.exemplo.com")
    requests_mock.get("http://api.exemplo.com/ping", json={"status": "ok"})
    assert sdk.ping() == {"status": "ok"}
