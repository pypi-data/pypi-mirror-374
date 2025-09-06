import sys
from pathlib import Path

import tomli_w  # for writing TOML files

CONFIG_DIR = Path.home() / ".sqlai"
CONFIG_FILE = CONFIG_DIR / "config.toml"


def write_config(provider: str, api_key: str, model: str):
    """Write the global config file."""
    CONFIG_DIR.mkdir(exist_ok=True)  # create ~/.sqlai if missing
    config_data = {"ai_provider": provider, "api_key": api_key, "model": model}
    with open(CONFIG_FILE, "wb") as f:
        tomli_w.dump(config_data, f)
    print(f"Config saved to {CONFIG_FILE}")


def read_config():
    """Read the global config file."""
    if not CONFIG_FILE.exists():
        print("⚠️   No global config found. Run `sqlai configure` first.")
        sys.exit(0)
    import tomli

    with open(CONFIG_FILE, "rb") as f:
        return tomli.load(f)


def set_config():
    print("Configure your SQL AI settings (global).")
    provider = input("AI Provider (gemini/openai/...): ").strip()
    api_key = input("API Key: ").strip()
    model = input("Model (e.g., gemini-1.5-flash): ").strip()
    write_config(provider, api_key, model)
