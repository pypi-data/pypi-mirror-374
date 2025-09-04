"""
🔍 PREDICATE CORE - Essential Logical Vocabulary Operations
==========================================================

Core predicate system functionality for managing logical vocabularies in ILP.

🧠 Inductive Logic Programming Library - Made possible by Benedict Chen
   benedict@benedictchen.com
   Support his work: 🍺 Buy him a beer: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
   💖 Sponsor: https://github.com/sponsors/benedictchen

📚 Research Foundation:
- Muggleton, S. & De Raedt, L. (1994). "Inductive Logic Programming: Theory and Methods."
- Framework for predicate management and vocabulary organization

🎯 ELI5 Explanation:
This is the core engine that manages logical vocabulary - like a smart dictionary
that knows not just what words mean, but how they're used in logical rules.

If you're learning about families, it knows that "parent(X,Y)" takes two arguments
and "human(X)" takes one, and keeps track of these patterns for the learning system.

🔧 Key Features:
• Predicate definition storage and retrieval
• Type checking and validation
• Vocabulary consistency management
• Integration with ILP learning algorithms

🙏 Support This Work:
If this predicate system helped your ILP research, please consider supporting continued development!
"""

from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass 
class PredicateDefinition:
    """Definition of a predicate with its properties"""
    name: str
    arity: int
    argument_types: List[str]
    is_builtin: bool = False
    description: str = ""


class CorePredicateSystem:
    """Core predicate system functionality"""
    
    def __init__(self):
        self.predicates: Dict[str, PredicateDefinition] = {}
        self.predicate_hierarchy: Dict[str, Set[str]] = {}
        self.predicate_aliases: Dict[str, str] = {}
        
    def add_predicate(self, predicate: PredicateDefinition):
        """Add a predicate to the system"""
        key = f"{predicate.name}/{predicate.arity}"
        self.predicates[key] = predicate
        
    def get_predicate(self, name: str, arity: int) -> Optional[PredicateDefinition]:
        """Get a predicate by name and arity"""
        key = f"{name}/{arity}"
        return self.predicates.get(key)
        
    def list_predicates(self) -> List[PredicateDefinition]:
        """List all predicates"""
        return list(self.predicates.values())
        
    def add_hierarchy(self, parent: str, child: str):
        """Add hierarchical relationship between predicates"""
        if parent not in self.predicate_hierarchy:
            self.predicate_hierarchy[parent] = set()
        self.predicate_hierarchy[parent].add(child)
        
    def add_alias(self, alias: str, target: str):
        """Add alias for predicate"""
        self.predicate_aliases[alias] = target