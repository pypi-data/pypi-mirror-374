"""
🧠 INDUCTIVE LOGIC PROGRAMMING - Research-Accurate ILP Implementation
===================================================================

Complete implementation of Inductive Logic Programming algorithms with full research accuracy.
Includes FOIL (Quinlan 1990) and Progol (Muggleton 1995) with comprehensive configuration.

🧠 Inductive Logic Programming Library - Made possible by Benedict Chen
   benedict@benedictchen.com
   Support his work: 🍺 Buy him a beer: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
   💖 Sponsor: https://github.com/sponsors/benedictchen

📚 Research Foundation:
- Muggleton, S. & De Raedt, L. (1994). "Inductive Logic Programming: Theory and Methods."
- Quinlan, J.R. (1990). "Learning logical definitions from relations."
- Muggleton, S. (1995). "Inverse entailment and Progol."
- First-principles implementations with complete theoretical accuracy

🎯 ELI5 Explanation:
Inductive Logic Programming is like teaching a computer to discover logical rules from examples.

Imagine showing a computer family tree examples:
• father(john, mary) ✓ (john is mary's father)
• father(bob, alice) ✓ (bob is alice's father) 
• mother(jane, mary) ✗ (not a father relationship)

The ILP system learns: "X is father of Y if X is male and parent(X,Y)"

This package provides two learning algorithms from the ILP literature:
1. **FOIL**: Uses information gain to build rules step-by-step
2. **Progol**: Uses inverse entailment for hypothesis construction

🏗️ ILP System Architecture:
┌─────────────────────────────────────────────────────────────────────┐
│                  INDUCTIVE LOGIC PROGRAMMING                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │ FOIL LEARNER    │  │ PROGOL SYSTEM   │  │ PREDICATE       │     │
│  │                 │  │                 │  │ SYSTEM          │     │
│  │ • Info gain     │  │ • Inverse       │  │                 │     │
│  │ • Coverage test │  │   entailment    │  │ • Vocabulary    │     │
│  │ • Rule building │  │ • Bottom clause │  │ • Types         │     │
│  │ • Quinlan 1990  │  │ • Muggleton 95  │  │ • Hierarchies   │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
│           │                       │                       │         │
│           ▼                       ▼                       ▼         │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │              LOGICAL FOUNDATIONS                            │     │
│  │  • LogicalTerm: Variables, constants, functions           │     │
│  │  • LogicalAtom: Predicate applications                    │     │
│  │  • LogicalClause: Rules and facts                         │     │
│  │  • Example: Training examples with labels                 │     │
│  │  • Unification: Term matching and substitution            │     │
│  └─────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘

⚙️ Key Components:

🔧 **Core ILP System**:
• InductiveLogicProgrammer: Main unified ILP system
• Factory functions for different use cases (educational, research, production)
• Modular architecture with mix-and-match components

🧮 **Learning Algorithms**:
• FOILLearner: Quinlan's information-gain based rule learning
• ProgolSystem: Muggleton's inverse entailment approach
• Both algorithms with full configuration and research accuracy

🔍 **Logical Infrastructure**:
• LogicalTerm: Variables (X,Y), constants (john, mary), functions (f(X))
• LogicalAtom: Predicates like father(john, mary)
• LogicalClause: Rules like "father(X,Y) :- male(X), parent(X,Y)"
• Example: Training data with positive/negative labels

🎪 Quick Start Examples:
```python
# Simple educational use
from inductive_logic_programming import create_educational_ilp, create_atom, create_constant

ilp = create_educational_ilp()
father_example = create_atom("father", [create_constant("john"), create_constant("mary")])
ilp.add_example(father_example, True)
rules = ilp.learn_rules("father")

# Research-grade FOIL with full configuration
from inductive_logic_programming.foil import FOILLearner
from inductive_logic_programming.foil_comprehensive_config import create_research_accurate_config

config = create_research_accurate_config()
foil = FOILLearner(config)
rules = foil.learn_predicate(examples, background_knowledge)

# Research-grade Progol with inverse entailment
from inductive_logic_programming.progol import ProgolSystem  
from inductive_logic_programming.progol_comprehensive_config import create_muggleton_accurate_config

config = create_muggleton_accurate_config()
progol = ProgolSystem(config)
hypothesis = progol.induce_hypothesis(examples, background_knowledge, mode_declarations)
```

🔧 Factory Functions for Every Use Case:
• create_educational_ilp(): Simplified for teaching and demos
• create_research_ilp_system(): Advanced system for academic research
• create_production_ilp(): Optimized for real-world applications  
• create_custom_ilp(): Fully configurable with all options

📈 Research vs Production Trade-offs:
• Educational: Simple, clear, good for learning ILP concepts
• Research: Maximum accuracy, all theoretical features, slower
• Production: Balanced speed/accuracy, robust error handling
• Custom: Full control over every algorithmic choice

🙏 Support This Work:
If this ILP library helped your machine learning research:
🍺 Buy Benedict a beer: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
💖 GitHub Sponsor: https://github.com/sponsors/benedictchen

Your support enables continued development of theoretically-grounded AI systems!
"""

# Import main ILP system and factory functions
from .ilp_core import (
    InductiveLogicProgrammer,
    create_educational_ilp,
    create_research_ilp_system,
    create_production_ilp,
    create_custom_ilp
)

# Import logical structures
from .ilp_core import (
    LogicalTerm,
    LogicalAtom,
    LogicalClause,
    Example
)

# Import convenience functions
from .ilp_core import (
    create_variable,
    create_constant,
    create_function,
    create_atom,
    create_fact,
    create_rule,
    parse_term
)

# Import individual mixins for custom systems
from .ilp_core import (
    HypothesisGenerationMixin,
    UnificationEngineMixin,
    SemanticEvaluationMixin,
    RuleRefinementMixin,
    CoverageAnalysisMixin,
    PredicateSystemMixin
)

# Import all modules for backward compatibility
from .ilp_modules import *

# Import recovered core algorithms
# Import module groups
from . import foil
from . import progol
from . import rule_refinement

# Import the main classes directly
from .foil import FOILLearner
from .progol import ProgolSystem
print("✅ Connected to REAL FOIL and Progol implementations!")

__version__ = "2.0.0"
__author__ = "Benedict Chen"

# Define what gets imported with "from inductive_logic_programming import *"
__all__ = [
    # Main ILP system
    'InductiveLogicProgrammer',
    
    # Factory functions  
    'create_educational_ilp',
    'create_research_ilp_system',
    'create_production_ilp',
    'create_custom_ilp',
    
    # Logical structures
    'LogicalTerm',
    'LogicalAtom',
    'LogicalClause', 
    'Example',
    
    # Convenience functions
    'create_variable',
    'create_constant',
    'create_function',
    'create_atom',
    'create_fact',
    'create_rule',
    'parse_term',
    
    # Individual mixins
    'HypothesisGenerationMixin',
    'UnificationEngineMixin',
    'SemanticEvaluationMixin',
    'RuleRefinementMixin', 
    'CoverageAnalysisMixin',
    'PredicateSystemMixin',
    
    # Core algorithms (if available)
    'foil',
    'progol', 
    'rule_refinement',
    
    # Real ILP algorithm classes
    'FOILLearner',
    'ProgolSystem'
]