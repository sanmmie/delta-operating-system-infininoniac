import os
import yaml
from typing import Dict, Any

class Config:
    def __init__(self):
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.config_data = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        config_path = f"config/{self.environment}.yaml"
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        # Override with environment variables
        self._override_with_env(config)
        return config
    
    def _override_with_env(self, config: Dict[str, Any], prefix: str = ""):
        for key, value in config.items():
            full_key = f"{prefix}_{key}".upper() if prefix else key.upper()
            if isinstance(value, dict):
                self._override_with_env(value, full_key)
            else:
                env_value = os.getenv(full_key)
                if env_value is not None:
                    if isinstance(value, bool):
                        config[key] = env_value.lower() == 'true'
                    elif isinstance(value, int):
                        config[key] = int(env_value)
                    elif isinstance(value, float):
                        config[key] = float(env_value)
                    else:
                        config[key] = env_value
    
    def get(self, key: str, default=None):
        keys = key.split('.')
        value = self.config_data
        for k in keys:
            value = value.get(k, {})
        return value if value != {} else default

config = Config()
