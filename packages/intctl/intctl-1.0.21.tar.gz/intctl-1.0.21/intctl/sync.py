# intctl/commands/sync.py

import os
import typer
import requests

from intctl.config import load_config, save_config, apply_env
from intctl.login import get_valid_access_token
from dotenv import load_dotenv
load_dotenv()

API_BASE_URL = os.getenv("INTELLITHING_API_BASE_URL", "https://intellithing-5e80f679-0b36-4a61-a643-eafeae0db479.intellithing.io/workspace")

def _handle_api_error(response: requests.Response):
    """A helper to parse and display API errors."""
    try:
        error_detail = response.json().get("detail", response.text)
    except requests.exceptions.JSONDecodeError:
        error_detail = response.text
    
    typer.secho(f"\n❌ API Error ({response.status_code}): {error_detail}", fg=typer.colors.RED)
    raise typer.Exit(code=1)

def sync_from_api():
    """
    Pulls initial configuration from the /sync endpoint using a setup_uuid.
    Updates and saves the local config file.
    """
    typer.secho("🔄 Syncing initial configuration from the INTELLITHING...", fg=typer.colors.CYAN)
    
    setup_uuid = typer.prompt("Enter your Setup UUID")
    if not setup_uuid:
        typer.secho("Setup UUID cannot be empty.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    endpoint = f"{API_BASE_URL}/sync"
    payload = {"setup_uuid": setup_uuid}
    headers = {
    "Authorization": f"Bearer {get_valid_access_token()}",
    "Content-Type": "application/json"
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            cfg = load_config()
            cfg["setup_uuid"] = setup_uuid
            cfg.update(data)
            cfg["setup_uuid"] = setup_uuid

            typer.secho("\n Successfully synced and updated configuration:", fg=typer.colors.GREEN)
            for key, value in data.items():
                typer.echo(f"  - {key}: {value}")
            
            save_config(cfg)
            apply_env(cfg)
            
        else:
            _handle_api_error(response)

    except requests.exceptions.RequestException as e:
        typer.secho(f"\n❌ Network Error: Could not connect to the API at {API_BASE_URL}", fg=typer.colors.RED)
        raise typer.Exit(code=1)