"""Configuration management for pydantic-rpn."""

from typing import Dict, Any, Optional
from contextlib import contextmanager


class Config:
    """Global configuration for RPN expressions."""
    
    _defaults = {
        'precision': None,
        'angle_unit': 'radians',
        'strict': True,
        'max_stack_size': 1000,
        'constants': {},
    }
    
    _current = _defaults.copy()
    
    @classmethod
    def set_defaults(cls, **kwargs) -> None:
        """Set global default configuration."""
        cls._current.update(kwargs)
    
    @classmethod
    def get(cls, key: str) -> Any:
        """Get a configuration value."""
        return cls._current.get(key)
    
    @classmethod
    def reset(cls) -> None:
        """Reset configuration to defaults."""
        cls._current = cls._defaults.copy()
    
    @classmethod
    @contextmanager
    def temporary(cls, **kwargs):
        """Context manager for temporary configuration changes."""
        old_config = cls._current.copy()
        try:
            cls._current.update(kwargs)
            yield
        finally:
            cls._current = old_config
    
    def __init__(self, **kwargs):
        """Create a temporary configuration context."""
        self.config = kwargs
    
    def __enter__(self):
        self.old_config = Config._current.copy()
        Config._current.update(self.config)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        Config._current = self.old_config