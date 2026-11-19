import os
import yaml
from pathlib import Path


DEFAULT_CONFIG = {
    "bytebase": {
        "url": "https://bytebase.gz.cvte.cn",
    },
    "defaults": {
        "project": "",
        "change_type": "DDL",
    },
    "session": {
        "token_file": str(Path.home() / ".bytebase-submit" / "session.json"),
        "timeout_seconds": 120,
    },
}


def load_config(config_path: str = None) -> dict:
    config = DEFAULT_CONFIG.copy()

    if config_path and os.path.exists(config_path):
        with open(config_path, "r") as f:
            user_config = yaml.safe_load(f) or {}
        config = _deep_merge(config, user_config)

    default_paths = [
        Path.home() / ".bytebase-submit" / "config.yaml",
        Path("config.yaml"),
    ]
    if not config_path:
        for p in default_paths:
            if p.exists():
                with open(p, "r") as f:
                    user_config = yaml.safe_load(f) or {}
                config = _deep_merge(config, user_config)
                break

    env_url = os.environ.get("BYTEBASE_URL")
    if env_url:
        config["bytebase"]["url"] = env_url

    return config


def _deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def get_session_path(config: dict) -> Path:
    return Path(os.path.expanduser(config["session"]["token_file"]))


def get_bytebase_url(config: dict) -> str:
    url = config["bytebase"]["url"]
    return url.rstrip("/")
