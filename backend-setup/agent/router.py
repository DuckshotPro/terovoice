"""
Multi-tenant router.
Routes incoming calls to the correct client's agent + profession.
"""
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger("router")


class ClientRouter:
    """Routes incoming calls to correct client configuration."""

    def __init__(self, clients_db_path: str = "./data/clients.json"):
        """
        Initialize router with clients database.

        Args:
            clients_db_path: Path to clients.json
        """
        self.db_path = Path(clients_db_path)
        self.clients = self._load_clients()

    def _load_clients(self) -> Dict[str, Any]:
        """Load clients from JSON database."""
        if not self.db_path.exists():
            logger.warning(f"Clients DB not found: {self.db_path}")
            return {}

        try:
            with open(self.db_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading clients DB: {e}")
            return {}

    def get_client_by_phone(self, incoming_number: str) -> Optional[Dict[str, Any]]:
        """
        Get client config by incoming phone number.

        Args:
            incoming_number: E.164 format phone number (+1234567890)

        Returns:
            Client config dict or None
        """
        for client_name, config in self.clients.items():
            if incoming_number in config.get("phone_numbers", []):
                logger.info(f"Routed call to client: {client_name}")
                return config

        logger.warning(f"No client found for number: {incoming_number}")
        return None

    def get_profession_prompt(self, profession: str) -> str:
        """
        Load profession-specific system prompt.

        Args:
            profession: Profession name (dentist, plumber, etc)

        Returns:
            System prompt string
        """
        config = self.get_profession_config(profession)
        return config.get("system_prompt", "You are a helpful AI assistant.")

    def get_profession_config(self, profession: str) -> Dict[str, Any]:
        """
        Load full profession configuration.

        Args:
            profession: Profession name (dentist, plumber, etc)

        Returns:
            Dict containing system_prompt, emergency_keywords, etc.
        """
        prompt_path = Path(__file__).parent / "professions" / f"{profession}.json"

        if not prompt_path.exists():
            logger.warning(f"Profession config not found: {profession}")
            return {}

        try:
            with open(prompt_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading profession config: {e}")
            return {}

    def add_client(
        self,
        name: str,
        phone_numbers: list,
        profession: str,
        voice_id: str,
        dashboard_url: str,
    ) -> bool:
        """
        Add new client to database.

        Args:
            name: Client name
            phone_numbers: List of phone numbers (E.164)
            profession: Profession type
            voice_id: Voice clone ID
            dashboard_url: Client dashboard URL

        Returns:
            True if successful
        """
        try:
            self.clients[name] = {
                "phone_numbers": phone_numbers,
                "profession": profession,
                "voice_id": voice_id,
                "dashboard_url": dashboard_url,
                "revenue_total": 0,
                "created_at": str(Path.cwd()),
            }

            # Write back to DB
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.db_path, "w") as f:
                json.dump(self.clients, f, indent=2)

            logger.info(f"Added client: {name}")
            return True

        except Exception as e:
            logger.error(f"Error adding client: {e}")
            return False

    def get_all_clients(self) -> Dict[str, Any]:
        """Get all clients."""
        return self.clients
