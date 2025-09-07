"""
Módulo EvoApiClient para integração com a API de contatos, clientes e mensagens.
"""

import json
import requests
from typing import Optional, Union


class EvoApiClient:
    """
    Cliente oficial para integração com a EvoAPI.
    """

    def __init__(self, base_url: str, instance: str, api_key: str):
        """
        Inicializa o cliente EvoApiClient.

        Parâmetros:
        - base_url: URL base da API (ex: 'https://evoapi.vezor.cloud')
        - instance: ID da instância
        - api_key: chave de API para autenticação
        """
        self.base_url = base_url.rstrip("/")
        self.instance = instance
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "apikey": self.api_key
        })

    def _post(self, endpoint: str, payload: dict) -> Union[dict, list]:
        """
        Realiza uma requisição POST genérica para a EvoAPI.
        """
        url = f"{self.base_url}/{endpoint}/{self.instance}"
        resp = self.session.post(url, data=json.dumps(payload))
        resp.raise_for_status()
        return resp.json()

    def get_contacts(self, save_path: Optional[str] = None) -> dict:
        """
        Obtém contatos da instância e, opcionalmente, salva em arquivo JSON.
        """
        contatos = self._post("chat/findContacts", {"where": {}})
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(contatos, f, ensure_ascii=False, indent=2)
        return contatos

    def get_clients(self, filters: Optional[dict] = None, save_path: Optional[str] = None) -> dict:
        """
        Obtém clientes da instância com filtros opcionais.
        """
        payload = {"where": filters or {}}
        clientes = self._post("crm/findClients", payload)
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(clientes, f, ensure_ascii=False, indent=2)
        return clientes

    def get_messages(self, save_path: Optional[str] = None, offset: int = 10000) -> list:
        """
        Obtém todas as mensagens em lotes e retorna uma lista consolidada.
        """
        todas = []
        pagina = 1

        while True:
            payload = {"page": pagina, "offset": offset}
            resposta = self._post("chat/findMessages", payload)

            mensagens_lote = []
            if isinstance(resposta, dict):
                mensagens_lote = resposta.get("records") or resposta.get("messages", {}).get("records", [])
            elif isinstance(resposta, list):
                mensagens_lote = resposta

            if not mensagens_lote:
                break

            todas.extend(mensagens_lote)
            if len(mensagens_lote) < offset:
                break

            pagina += 1

        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(todas, f, ensure_ascii=False, indent=2)

        return todas
