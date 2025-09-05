import os
import json
from pathlib import Path
from typing import Optional, Tuple, Union, List

import httpx
from a2a.types import AgentCard
from ainexus_sdk.model import AgentMetadata 
from supabase import create_client, Client

# Cache directory
CACHE_DIR = Path.home() / ".cache" / "agenthub" / "agents_metadata"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
BASE_URL = "https://hncugknujacihsgyrvtd.supabase.co/functions/v1/get-installed-agent"

class AgentSDK:
    def __init__(
        self, 
        auth_token: Optional[str] = None,
        api_key: Optional[str] = None, 
        base_url: str = BASE_URL,  
        timeout: int = 30
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.user_id, self.access_token = self._load_user_credentials()
        self.auth_token = auth_token or self.access_token
        
    @property
    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}

    # ---------- Sync Methods ----------
    def discover(
        self, agent_id: Optional[Union[str, List[str]]] = None, refresh: bool = False
    ) -> List[AgentMetadata]:
        """
        Discover agent(s).
        - agent_id = str   -> single agent
        - agent_id = list  -> multiple agents
        - agent_id = None  -> all agents
        """
        
        # --- Case 1: Single agent ---
        if isinstance(agent_id, str):
            results: List[AgentMetadata] = []
            cache_file = CACHE_DIR / f"{agent_id}_metadata.json"

            if not refresh and cache_file.exists():
                card = AgentMetadata.model_validate_json(cache_file.read_text())
                results.append(card)
                return results

            params = {"user_id": self.user_id, "agent_id": agent_id }
            response = httpx.get(self.base_url, headers=self._headers, params=params, timeout=self.timeout)
            
            if response.status_code != 200:
                raise Exception(f"Error {response.status_code}: {response.text}")

            payload = response.json()
            agent = payload.get("agents", [])
            if not agent:
                raise ValueError(f"Agent with id {agent_id} not found in Supabase.")
            
            
            data = agent[0]
            card = AgentMetadata.model_validate(data)
            cache_file.write_text(card.model_dump_json(indent=2))
            results.append(card)
            return results
            
        # --- Case 2: Multiple agents or all agents ---
        elif isinstance(agent_id, list) or agent_id is None:
            # --- Normalize agent_ids ---
            if agent_id is None:
                agent_ids = []  # empty means fetch all
            else:
                agent_ids = agent_id

            # Try cache first
            cached_results, missing_ids = self._load_cached_agents(agent_ids, refresh)

            # If no agent_ids given (fetch all), skip cache filtering
            if agent_id is None:
                missing_ids = None  

            if missing_ids or agent_id is None:
                # Prepare params
                params = {"user_id": self.user_id}
                if agent_id is not None:  # multiple specific agents
                    for idx, aid in enumerate(missing_ids):
                        params[f"agent_ids[{idx}]"] = aid  

                # Call Edge Function
                response = httpx.get(
                    self.base_url,
                    headers=self._headers,
                    params=params,
                    timeout=self.timeout,
                )

                if response.status_code != 200:
                    raise Exception(f"Error {response.status_code}: {response.text}")

                payload = response.json()
                agents = payload.get("agents", [])

                if not agents:
                    raise ValueError("No agents found in Supabase.")

                for data in agents:
                    card = AgentMetadata.model_validate(data)
                    cache_file = CACHE_DIR / f"{card.id}_metadata.json"
                    cache_file.write_text(card.model_dump_json(indent=2))
                    cached_results.append(card)

            return cached_results

        else:
            raise TypeError("agent_id must be str, list[str], or None")

    def _load_cached_agents(self, agent_ids: List[str], refresh: bool):
        cached_results: List[AgentMetadata] = [] 
        missing_ids = []

        for aid in agent_ids:
            cache_file = CACHE_DIR / f"{aid}_metadata.json"
            if not refresh and cache_file.exists():
                card = AgentMetadata.model_validate_json(cache_file.read_text())
                cached_results.append(card)
            else:
                missing_ids.append(aid)

        return cached_results, missing_ids

    def _load_user_credentials(self) -> Tuple[str, str]:
        """
        Load user_id and access_token from ~/.agenthub/config.json
        Returns:
            user_id (str): The authenticated user's ID
            access_token (str): The Supabase access token
        Raises:
            ValueError: If the config file or required fields are missing
        """
        token_path = Path.home() / ".agenthub" / "config.json"

        if not token_path.exists():
            raise ValueError("Auth token not found. Run `agent login`")

        with open(token_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        if "user" not in config or "id" not in config["user"]:
            raise ValueError("Config file found but no user_id present")

        if "access_token" not in config:
            raise ValueError("Config file found but no access_token present")

        user_id = config["user"]["id"]
        access_token = config["access_token"]

        return user_id, access_token