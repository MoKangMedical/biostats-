"""配置管理 — Biostats应用配置"""

import os
import json
from typing import Any, Dict, Optional


class Config:
    """Biostats配置管理器"""

    DEFAULT_CONFIG = {
        "app_name": "Biostats",
        "version": "1.0.0",
        "debug": False,
        "host": "0.0.0.0",
        "port": 8001,
        "database": {"type": "sqlite", "path": "data/biostats.db"},
        "api": {"rate_limit": 100, "timeout": 60, "cors_origins": ["*"]},
        "analysis": {
            "default_alpha": 0.05,
            "bootstrap_iterations": 1000,
            "max_sample_size": 1000000,
            "convergence_tolerance": 1e-6,
        },
        "visualization": {"default_format": "png", "dpi": 150, "figure_size": [10, 6]},
        "export": {"formats": ["csv", "json", "html"], "max_rows": 10000},
        "notification": {"enabled": False, "channels": ["email"]},
        "language": "zh-CN",
        "timezone": "Asia/Shanghai",
    }

    def __init__(self, config_path: str = None):
        self._config = dict(self.DEFAULT_CONFIG)
        self._config_path = config_path
        if config_path and os.path.exists(config_path):
            self.load(config_path)

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        val = self._config
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            else:
                return default
            if val is None:
                return default
        return val

    def set(self, key: str, value: Any):
        keys = key.split(".")
        d = self._config
        for k in keys[:-1]:
            if k not in d:
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value

    def load(self, path: str):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._config.update(data)
        except Exception:
            pass

    def save(self, path: str = None):
        path = path or self._config_path
        if not path:
            return False
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def get_all(self) -> dict:
        return dict(self._config)

    def reset(self):
        self._config = dict(self.DEFAULT_CONFIG)

    def is_debug(self) -> bool:
        return self.get("debug", False)

    def get_analysis_config(self) -> dict:
        return self.get("analysis", {})

    def get_db_config(self) -> dict:
        return self.get("database", {})

    def from_env(self, prefix: str = "BIOSTATS_"):
        for key, val in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower().replace("__", ".")
                self.set(config_key, val)

    def validate(self) -> bool:
        required = ["app_name", "version", "host", "port"]
        return all(self.get(k) is not None for k in required)

    def __repr__(self):
        return f"BiostatsConfig({json.dumps(self._config, ensure_ascii=False)[:100]}...)"
