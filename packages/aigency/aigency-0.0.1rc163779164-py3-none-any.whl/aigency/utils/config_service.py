"""Configuration service for loading and parsing agent configurations."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from aigency.schemas.aigency_config import AigencyConfig
from aigency.utils.logger import get_logger


logger = get_logger()


class ConfigService:
    """Service for loading and managing agent configurations."""

    def __init__(self, config_file: str, environment: Optional[str] = None):
        self.config_file = config_file
        self.environment = environment or os.getenv("ENVIRONMENT", None)
        self.config = self._load_and_parse()

    def _load_and_parse(self) -> AigencyConfig:
        """Carga los YAMLs, los mergea y parsea según AigencyConfig."""

        logger.info(f"Loading configuration from {self.config_file}")
        config = self._load_yaml(self.config_file)

        if self.environment is not None:
            logger.info(
                f"Environment '{self.environment}' detected, loading environment-specific configuration"
            )
            env_config = self._load_env_config()
            if env_config:
                logger.info(
                    f"Successfully loaded environment configuration with {len(env_config)} keys: {list(env_config.keys())}"
                )
                config = self._merge_configs(config, env_config)
                logger.debug(
                    f"Configuration merged successfully for environment '{self.environment}'"
                )
            else:
                logger.warning(
                    f"No environment-specific configuration found for '{self.environment}', using base configuration only"
                )

        return AigencyConfig(**config)

    def _load_yaml(self, file_path: str) -> Dict[str, Any]:
        """Carga un archivo YAML."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Archivo de configuración no encontrado: {file_path}"
            )
        except yaml.YAMLError as e:
            raise ValueError(f"Error al parsear YAML {file_path}: {e}")

    def _load_env_config(self) -> Optional[Dict[str, Any]]:
        """Carga configuración específica del entorno."""
        config_path = Path(self.config_file)
        env_file = (
            config_path.parent
            / f"{config_path.stem}.{self.environment}{config_path.suffix}"
        )

        return self._load_yaml(str(env_file)) if env_file.exists() else None

    def _merge_configs(
        self, base: Dict[str, Any], env: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Mergea configuración base con configuración de entorno."""
        if not env:
            return base

        result = base.copy()
        for key, value in env.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
