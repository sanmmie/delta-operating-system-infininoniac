import os
import re
from pathlib import Path
from typing import Any, Dict

import yaml

ENV_VALUE = re.compile(r"^\$\{([A-Z0-9_]+)(?::([^}]*))?\}$")


class Config:
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.config_data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        config_path = Path(__file__).with_name(f"{self.environment}.yaml")
        if not config_path.is_file():
            raise RuntimeError(f"Configuration file does not exist: {config_path}")
        with config_path.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
        if not isinstance(config, dict):
            raise RuntimeError(f"Configuration must be a mapping: {config_path}")

        config = self._resolve_environment_values(config)
        # Override with environment variables
        self._override_with_env(config)
        return config

    def _resolve_environment_values(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {key: self._resolve_environment_values(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._resolve_environment_values(item) for item in value]
        if isinstance(value, str):
            match = ENV_VALUE.fullmatch(value)
            if match:
                name, default = match.groups()
                return os.getenv(name, default or "")
        return value

    def _override_with_env(self, config: Dict[str, Any], prefix: str = "") -> None:
        for key, value in config.items():
            full_key = f"{prefix}_{key}".upper() if prefix else key.upper()
            if isinstance(value, dict):
                self._override_with_env(value, full_key)
            else:
                env_value = os.getenv(full_key)
                if env_value is not None:
                    if isinstance(value, bool):
                        config[key] = env_value.lower() == "true"
                    elif isinstance(value, int):
                        config[key] = int(env_value)
                    elif isinstance(value, float):
                        config[key] = float(env_value)
                    else:
                        config[key] = env_value

    def get(self, key: str, default=None):
        keys = key.split(".")
        value = self.config_data
        for k in keys:
            if not isinstance(value, dict) or k not in value:
                return default
            value = value[k]
        return value


config = Config()
