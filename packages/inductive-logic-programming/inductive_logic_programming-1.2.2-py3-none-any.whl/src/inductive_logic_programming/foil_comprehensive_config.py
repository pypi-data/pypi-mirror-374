"""
🎯 FOIL Comprehensive Configuration
===================================================================

This module implements configuration options for FOIL algorithm variants
with complete user configuration control. Users can pick and choose between
multiple research-accurate approaches.

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Analysis of FOIL algorithm variants from research literature
Research Foundation: Quinlan (1990) "Learning logical definitions from relations"
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional, Union, Callable
import numpy as np
import logging


class InformationGainMethod(Enum):
    """All approaches for FOIL information gain computation"""
    QUINLAN_ORIGINAL = "quinlan_original"                    # Quinlan (1990) exact formula with bindings
    LAPLACE_CORRECTED = "laplace_corrected"                 # Laplace correction for numerical stability
    MODERN_INFO_THEORY = "modern_info_theory"               # Modern information-theoretic approach
    EXAMPLE_BASED_APPROXIMATION = "example_approximation"    # Simplified implementation (for comparison)


class CoverageTestingMethod(Enum):
    """All approaches for coverage testing"""
    SLD_RESOLUTION = "sld_resolution"                       # Standard SLD resolution for definite clauses
    CONSTRAINT_LOGIC_PROGRAMMING = "clp"                   # CLP for typed variables and constraints
    TABLED_RESOLUTION = "tabled_resolution"                # Tabled resolution with memoization for cycles
    SIMPLIFIED_UNIFICATION = "simplified_unification"      # Simplified method (for comparison)


class VariableBindingStrategy(Enum):
    """Variable binding generation strategies"""
    EXHAUSTIVE_ENUMERATION = "exhaustive"                  # Generate all possible substitutions
    CONSTRAINT_GUIDED = "constraint_guided"                # Use constraints to prune search space
    HEURISTIC_PRUNING = "heuristic_pruning"               # Use heuristics to focus on promising bindings


@dataclass 
class FOILComprehensiveConfig:
    """Comprehensive configuration for FOIL algorithm variants"""
    
    # Information gain method selection
    information_gain_method: InformationGainMethod = InformationGainMethod.QUINLAN_ORIGINAL
    use_exact_binding_counts: bool = True
    logarithmic_base: float = 2.0
    laplace_alpha: float = 1.0
    laplace_beta: float = 2.0
    
    # Coverage testing method selection  
    coverage_method: CoverageTestingMethod = CoverageTestingMethod.SLD_RESOLUTION
    sld_max_resolution_steps: int = 100
    sld_timeout_seconds: float = 1.0
    
    # Variable binding strategy
    binding_strategy: VariableBindingStrategy = VariableBindingStrategy.CONSTRAINT_GUIDED
    max_binding_combinations: int = 10000
    type_constraint_checking: bool = True
    
    # Performance and debugging
    enable_detailed_logging: bool = False
    log_level: str = "WARNING"
    validate_theoretical_properties: bool = True
    
    def validate_config(self) -> Tuple[bool, List[str]]:
        """Validate configuration parameters"""
        errors = []
        
        if self.logarithmic_base <= 0:
            errors.append("logarithmic_base must be > 0")
        if self.sld_max_resolution_steps < 1:
            errors.append("sld_max_resolution_steps must be >= 1")
        if self.max_binding_combinations < 1:
            errors.append("max_binding_combinations must be >= 1")
            
        return len(errors) == 0, errors


def create_research_accurate_config() -> FOILComprehensiveConfig:
    """Maximum research accuracy - implements all Quinlan (1990) requirements"""
    return FOILComprehensiveConfig(
        information_gain_method=InformationGainMethod.QUINLAN_ORIGINAL,
        coverage_method=CoverageTestingMethod.SLD_RESOLUTION,
        binding_strategy=VariableBindingStrategy.EXHAUSTIVE_ENUMERATION,
        use_exact_binding_counts=True,
        sld_max_resolution_steps=200,
        max_binding_combinations=50000,
        enable_detailed_logging=True,
        log_level="DEBUG"
    )


def create_fast_approximation_config() -> FOILComprehensiveConfig:
    """Fast approximation - good balance of accuracy and speed"""
    return FOILComprehensiveConfig(
        information_gain_method=InformationGainMethod.LAPLACE_CORRECTED,
        coverage_method=CoverageTestingMethod.SIMPLIFIED_UNIFICATION,
        binding_strategy=VariableBindingStrategy.HEURISTIC_PRUNING,
        max_binding_combinations=1000,
        sld_max_resolution_steps=20
    )


if __name__ == "__main__":
    print("🎯 FOIL comprehensive configuration system ready!")