import requests

class VzrClient:
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def ping(self):
        """Teste simples de conexão"""
        resp = self.session.get(f"{self.base_url}/ping")
        resp.raise_for_status()
        return resp.json()

    def get_data(self, resource: str):
        """Busca dados em um recurso da API"""
        url = f"{self.base_url}/{resource}"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()
