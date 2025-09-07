# src/vezor_sdk/kommoapi.py
import requests


class KommoApiClient:
    def __init__(self, base_url: str, token: str):
        """
        Cliente para a API Kommo v4.

        :param base_url: URL base da conta Kommo (ex: https://minhaempresa.kommo.com)
        :param token: Token Bearer de autenticação (OAuth2)
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "application/json",
            "authorization": f"Bearer {token}"
        })

    def get_pipelines(self):
        """
        Retorna todos os pipelines disponíveis na conta Kommo.

        :return: Lista de dicionários representando os pipelines.
        :raises requests.HTTPError: Se a requisição falhar.
        """
        url = f"{self.base_url}/api/v4/leads/pipelines"
        try:
            resp = self.session.get(url)
            resp.raise_for_status()
            data = resp.json()
            pipelines = data.get('_embedded', {}).get('pipelines', [])
            return pipelines
        except requests.RequestException as e:
            raise RuntimeError(f"Erro ao buscar pipelines: {e}") from e

    def get_pipeline_statuses(self, pipeline_id: int):
        """
        Retorna os status de um pipeline específico.

        :param pipeline_id: ID do pipeline desejado.
        :return: Lista de dicionários representando os status do pipeline.
        :raises requests.HTTPError: Se a requisição falhar.
        """
        url = f"{self.base_url}/api/v4/leads/pipelines/{pipeline_id}/statuses"
        try:
            resp = self.session.get(url)
            resp.raise_for_status()
            data = resp.json()
            statuses = data.get('_embedded', {}).get('statuses', [])
            return statuses
        except requests.RequestException as e:
            raise RuntimeError(f"Erro ao buscar status do pipeline {pipeline_id}: {e}") from e

    def get_lead_tags(self):
        """
        Lista as tags disponíveis para leads.

        :return: Lista de dicionários representando as tags.
        :raises RuntimeError: Se a requisição falhar.
        """
        url = f"{self.base_url}/api/v4/leads/tags"
        try:
            resp = self.session.get(url)
            resp.raise_for_status()
            data = resp.json()
            tags = data.get('_embedded', {}).get('tags', [])
            return tags
        except requests.RequestException as e:
            raise RuntimeError(f"Erro ao buscar tags: {e}") from e

    def create_lead_tag(self, name: str, color: str = "FFCE5A"):
        """Cria uma nova tag para leads."""
        url = f"{self.base_url}/api/v4/leads/tags"
        payload = [{"name": name, "color": color}]
        resp = self.session.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()

    def get_webhooks(self):
        """
        Lista os webhooks configurados.

        :return: Lista de dicionários representando os webhooks.
        :raises RuntimeError: Se a requisição falhar.
        """
        url = f"{self.base_url}/api/v4/webhooks"
        try:
            resp = self.session.get(url)
            resp.raise_for_status()
            data = resp.json()
            webhooks = data.get('_embedded', {}).get('webhooks', [])
            return webhooks
        except requests.RequestException as e:
            raise RuntimeError(f"Erro ao buscar webhooks: {e}") from e

    def create_webhook(self, destination: str, settings: list[str]):
        """Cria um novo webhook."""
        url = f"{self.base_url}/api/v4/webhooks"
        payload = {"destination": destination, "settings": settings}
        resp = self.session.post(url, json=payload, headers={"content-type": "application/json"})
        resp.raise_for_status()
        return resp.json()
