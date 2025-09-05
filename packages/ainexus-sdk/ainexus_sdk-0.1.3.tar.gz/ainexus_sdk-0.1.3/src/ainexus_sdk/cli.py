import json
import os
from pathlib import Path
from dotenv import load_dotenv
import httpx
import typer
from supabase import create_client, Client

# Load variables from .env file
load_dotenv()

app = typer.Typer()

CONFIG_DIR = os.path.expanduser("~/.agenthub")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Edge Function base URL (change according to your deployment)
EDGE_BASE_URL = os.getenv("EDGE_BASE_URL", "https://hncugknujacihsgyrvtd.supabase.co/functions/v1")

def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):  # ✅ works with str path
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

@app.command()
def login(
    email: str = typer.Option(..., prompt=True),
    password: str = typer.Option(..., prompt=True, hide_input=True)
):
    """
    Login with email and password.
    """
    try:
        url = f"{EDGE_BASE_URL}/login"
        payload = {"email": email, "password": password}

        response = httpx.post(url, json=payload, timeout=10)

        if response.status_code != 200:
            typer.secho(f"❌ Login failed: {response.text}", fg=typer.colors.RED)
            raise typer.Exit(1)

        data = response.json()

        os.makedirs(CONFIG_DIR, exist_ok=True)
        Path(CONFIG_FILE).write_text(json.dumps(data, indent=2))
        typer.secho("✅ Congratulations!, Login successful! ", fg=typer.colors.GREEN)
        
    except Exception as e:
        typer.secho(f"⚠️ Error: {str(e)}", fg=typer.colors.RED)
        
@app.command()
def whoami():
    """
    Display stored user session info.
    """
    config = load_config()
    if not config:
        typer.secho("⚠️ Not logged in. Run `agenthub login`.", fg=typer.colors.RED)
        raise typer.Exit(1)

    user = config.get("user", {})
    typer.secho(f"👤 Logged in as: {user.get('email')} (id={user.get('id')})", fg=typer.colors.CYAN)
    typer.echo(f"   Last Sign-in: {user['last_sign_in_at']}")
    
    typer.secho("👤 Current session:", fg=typer.colors.BLUE)
    typer.echo(f"   Provider: {config['provider']}")
    typer.echo(f"   Access Token: {config['access_token'][:15]}...")  # partial for safety

@app.command()
def logout():
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
        print("✅ Logged out successfully")
    else:
        print("⚠️ You are not logged in.")

if __name__ == "__main__":
    app()
