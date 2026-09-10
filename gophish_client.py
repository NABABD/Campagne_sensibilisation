"""
Client léger pour l'API REST de GoPhish (https://getgophish.com), un
framework open source de simulation de phishing destiné à la sensibilisation
interne en entreprise.

GoPhish s'installe et se lance en local ou sur ton propre serveur — aucune
dépendance à Microsoft ni à un fournisseur tiers. Toute campagne doit rester
strictement interne à ton organisation et autorisée par la direction / RSSI.

Doc officielle : https://docs.getgophish.com/api-documentation/
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("GOPHISH_API_URL", "https://localhost:3333")
API_KEY = os.getenv("GOPHISH_API_KEY")
VERIFY_SSL = os.getenv("GOPHISH_VERIFY_SSL", "false").lower() == "true"

if not VERIFY_SSL:
    # GoPhish utilise un certificat auto-signé par défaut en local.
    requests.packages.urllib3.disable_warnings(
        requests.packages.urllib3.exceptions.InsecureRequestWarning
    )


class GoPhishClient:
    def __init__(self, base_url: str = API_URL, api_key: str = API_KEY, verify_ssl: bool = VERIFY_SSL):
        if not api_key:
            raise RuntimeError(
                "GOPHISH_API_KEY manquante. Copie .env.example en .env et "
                "renseigne la clé API (Settings > API Key dans l'interface GoPhish)."
            )
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        self.verify_ssl = verify_ssl

    def _get(self, path: str):
        resp = requests.get(f"{self.base_url}{path}", headers=self.headers, verify=self.verify_ssl, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, payload: dict):
        resp = requests.post(f"{self.base_url}{path}", headers=self.headers, json=payload, verify=self.verify_ssl, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _delete(self, path: str):
        resp = requests.delete(f"{self.base_url}{path}", headers=self.headers, verify=self.verify_ssl, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # ---- Groupes (destinataires internes) ----
    def list_groups(self):
        return self._get("/api/groups/")

    def create_group(self, name: str, targets: list[dict]):
        """
        targets: liste de dicts {email, first_name, last_name, position}
        Ces adresses doivent appartenir à ton organisation, avec accord
        préalable de la direction pour la campagne de sensibilisation.
        """
        return self._post("/api/groups/", {"name": name, "targets": targets})

    # ---- Templates d'email ----
    def list_templates(self):
        return self._get("/api/templates/")

    def create_template(self, name: str, subject: str, html: str, text: str = ""):
        """
        Crée un template d'email. Le contenu (html/text) doit être rédigé
        par l'équipe sécurité en s'inspirant de scénarios réalistes mais
        strictement à but pédagogique (jamais de vraies marques usurpées
        sans autorisation, jamais de contenu trompant sur l'identité légale).
        """
        return self._post("/api/templates/", {
            "name": name,
            "subject": subject,
            "html": html,
            "text": text,
        })

    # ---- Pages d'atterrissage ----
    def list_pages(self):
        return self._get("/api/pages/")

    def create_page(self, name: str, html: str, capture_credentials: bool = False, redirect_url: str = ""):
        """
        Si capture_credentials=True, GoPhish enregistrera ce qui est saisi
        dans le formulaire de la page — à utiliser uniquement pour mesurer
        le taux de vulnérabilité, jamais pour un usage réel des identifiants,
        et avec une politique claire de suppression rapide de ces données.
        """
        return self._post("/api/pages/", {
            "name": name,
            "html": html,
            "capture_credentials": capture_credentials,
            "capture_passwords": False,  # ne jamais stocker les mots de passe en clair
            "redirect_url": redirect_url,
        })

    # ---- Profils d'envoi (SMTP) ----
    def list_sending_profiles(self):
        return self._get("/api/smtp/")

    def create_sending_profile(self, name: str, host: str, from_address: str, username: str = "", password: str = ""):
        return self._post("/api/smtp/", {
            "name": name,
            "host": host,
            "from_address": from_address,
            "username": username,
            "password": password,
            "ignore_cert_errors": True,
        })

    # ---- Campagnes ----
    def list_campaigns(self):
        return self._get("/api/campaigns/")

    def create_campaign(
        self,
        name: str,
        template_name: str,
        page_name: str,
        smtp_name: str,
        group_names: list[str],
        landing_url: str,
        launch_date: str | None = None,
    ):
        payload = {
            "name": name,
            "template": {"name": template_name},
            "page": {"name": page_name},
            "smtp": {"name": smtp_name},
            "groups": [{"name": g} for g in group_names],
            "url": landing_url,
        }
        if launch_date:
            payload["launch_date"] = launch_date  # format ISO8601
        return self._post("/api/campaigns/", payload)

    def get_campaign_results(self, campaign_id: int):
        return self._get(f"/api/campaigns/{campaign_id}/results")

    def get_campaign_summary(self, campaign_id: int):
        return self._get(f"/api/campaigns/{campaign_id}/summary")

    def delete_campaign(self, campaign_id: int):
        return self._delete(f"/api/campaigns/{campaign_id}")
