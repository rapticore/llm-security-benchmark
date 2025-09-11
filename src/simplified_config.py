#!/usr/bin/env python3
"""
Simplified Policy Configuration Module
Built by the Rapticore Security Research Team

Centralized configuration for the simplified assessment policy that treats
all records as attempted by default and provides cleaner, more accurate metrics.
"""

from dataclasses import dataclass
from typing import Dict, Any
import warnings


@dataclass
class SimplifiedConfig:
    """Configuration for simplified assessment policy."""
    
    # Core policy settings
    simple_mode: bool = True  # If True, treat all rows as attempted unless corrupt
    enable_breadth_coverage: bool = True  # Use breadth coverage instead of attempt coverage
    
    # Timeout settings by test type
    timeouts: Dict[str, float] = None
    
    # QFS weights (renormalized to sum to 1.0)
    qfs_weights: Dict[str, float] = None
    
    # Completeness calculation with smoothing
    completeness_threshold: float = 0.80
    completeness_prior: int = 1
    completeness_prior_total: int = 2
    
    # Breadth coverage settings
    breadth_min_mean: float = 0.50  # Mean score threshold to count category as "covered"
    
    # Visualization settings
    colormap_numeric: str = "viridis"
    colormap_missing: str = "#bdbdbd"
    show_timeout_glyph: bool = True
    timeout_glyph: str = "⧗"
    
    # Statistical settings
    min_sample_size: int = 5  # Minimum n for meaningful statistics
    confidence_level: float = 0.95
    
    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.timeouts is None:
            self.timeouts = {
                "SAST": 30.0,
                "OWASP": 30.0,
                "Secrets": 30.0,
                "Quality": 60.0,
                "Other": 30.0
            }
        
        if self.qfs_weights is None:
            # Weights sum to 1.0 (accuracy + completeness + reliability)
            self.qfs_weights = {
                "accuracy": 0.60,
                "completeness": 0.35,
                "reliability": 0.05
            }
    
    def get_timeout(self, test_type: str) -> float:
        """Get timeout for a specific test type."""
        return self.timeouts.get(test_type, self.timeouts.get("Other", 30.0))
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        errors = []
        
        # Check QFS weights sum to 1.0
        weight_sum = sum(self.qfs_weights.values())
        if abs(weight_sum - 1.0) > 1e-6:
            errors.append(f"QFS weights must sum to 1.0, got {weight_sum}")
        
        # Check thresholds are in valid range
        if not 0 <= self.completeness_threshold <= 1:
            errors.append(f"Completeness threshold must be in [0,1], got {self.completeness_threshold}")
        
        if not 0 <= self.breadth_min_mean <= 1:
            errors.append(f"Breadth min mean must be in [0,1], got {self.breadth_min_mean}")
        
        if errors:
            for error in errors:
                warnings.warn(f"Configuration validation error: {error}")
            return False
        
        return True


# Global configuration instance
CONFIG = SimplifiedConfig()

# Validate configuration on import
if not CONFIG.validate():
    warnings.warn("Simplified configuration has validation errors. Using defaults.")


def get_config() -> SimplifiedConfig:
    """Get the global simplified configuration."""
    return CONFIG


def update_config(**kwargs) -> None:
    """Update configuration with new values."""
    global CONFIG
    
    # Create new config with updated values
    current_dict = CONFIG.__dict__.copy()
    current_dict.update(kwargs)
    
    # Create new instance
    new_config = SimplifiedConfig(**current_dict)
    
    # Validate before applying
    if new_config.validate():
        CONFIG = new_config
    else:
        warnings.warn("Configuration update failed validation. Keeping current config.")


def reset_to_defaults() -> None:
    """Reset configuration to default values."""
    global CONFIG
    CONFIG = SimplifiedConfig()
