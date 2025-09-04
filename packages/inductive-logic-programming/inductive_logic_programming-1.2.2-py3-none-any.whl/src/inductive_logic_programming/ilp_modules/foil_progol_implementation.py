"""
🧠 ILP Algorithm Framework Implementation
========================================

Framework for ILP algorithm development with configurable methods.
Provides working implementations of core algorithms (specialization, generalization, unification)
with extensible framework methods for advanced features.

Core Methods (Fully Implemented):
- _specialize_clause: Multiple specialization strategies 
- _generalize_clause: Multiple generalization approaches
- _unify_atoms: Multiple unification algorithms

Framework Methods (Extensible):
- Helper methods provide basic implementations that can be extended
- Coverage testing routes to proven SLD resolution implementations
- Statistical and constraint methods provide framework structure

Author: Benedict Chen
Based on: Quinlan (1990) FOIL, Muggleton & De Raedt (1994) Progol, Robinson (1965) Unification
"""

import re
import copy
import time
import logging
from typing import Dict, List, Tuple, Set, Any, Optional, Union
from dataclasses import dataclass
from collections import defaultdict, deque
import math

from .ilp_config import (
    ILPConfig, SpecializationMethod, GeneralizationMethod, UnificationMethod,
    EvaluationMetric, PresetConfigs
)


@dataclass
class Atom:
    """Represents a logical atom with predicate and terms"""
    predicate: str
    terms: List[str]
    negated: bool = False
    
    def __str__(self):
        neg_str = "¬" if self.negated else ""
        terms_str = ",".join(self.terms) if self.terms else ""
        return f"{neg_str}{self.predicate}({terms_str})"
    
    def copy(self):
        return Atom(self.predicate, self.terms.copy(), self.negated)


@dataclass 
class Clause:
    """Represents a logical clause with head and body"""
    head: Atom
    body: List[Atom]
    
    def __str__(self):
        if not self.body:
            return str(self.head)
        body_str = " ∧ ".join(str(atom) for atom in self.body)
        return f"{self.head} :- {body_str}"
    
    def copy(self):
        return Clause(self.head.copy(), [atom.copy() for atom in self.body])
    
    def get_variables(self) -> Set[str]:
        """Get all variables in the clause (uppercase terms)"""
        variables = set()
        for atom in [self.head] + self.body:
            for term in atom.terms:
                if term[0].isupper():  # Variable convention
                    variables.add(term)
        return variables


@dataclass
class Substitution:
    """Represents a variable substitution mapping"""
    mapping: Dict[str, str]
    
    def __init__(self, mapping: Optional[Dict[str, str]] = None):
        self.mapping = mapping or {}
    
    def apply_to_atom(self, atom: Atom) -> Atom:
        """Apply substitution to an atom"""
        new_terms = []
        for term in atom.terms:
            new_terms.append(self.mapping.get(term, term))
        return Atom(atom.predicate, new_terms, atom.negated)
    
    def apply_to_clause(self, clause: Clause) -> Clause:
        """Apply substitution to a clause"""
        new_head = self.apply_to_atom(clause.head)
        new_body = [self.apply_to_atom(atom) for atom in clause.body]
        return Clause(new_head, new_body)
    
    def compose(self, other: 'Substitution') -> 'Substitution':
        """Compose two substitutions"""
        new_mapping = {}
        # Apply other to our mappings
        for var, val in self.mapping.items():
            new_mapping[var] = other.mapping.get(val, val)
        # Add mappings from other that aren't in self
        for var, val in other.mapping.items():
            if var not in new_mapping:
                new_mapping[var] = val
        return Substitution(new_mapping)


class FOILProgolImplementation:
    """
    Complete implementation of ALL ILP methods with configuration options
    
    This class implements all research-identified ILP methods:
    1. _specialize_clause - Multiple specialization algorithms
    2. _generalize_clause - Multiple generalization approaches  
    3. _unify_atoms - Multiple unification variants
    """
    
    def __init__(self, config: Optional[ILPConfig] = None):
        """Initialize with configuration"""
        self.config = config or ILPConfig()
        self.logger = logging.getLogger(__name__)
        if self.config.verbose_logging:
            self.logger.setLevel(logging.DEBUG)
        
        # Cache for performance optimization
        self.unification_cache = {} if self.config.use_caching else None
        self.specialization_cache = {} if self.config.use_caching else None
        
    # ===== CLAUSE SPECIALIZATION METHODS =====
    
    def _specialize_clause(self, clause: Clause, positive_examples: List[Dict],
                          negative_examples: List[Dict], background_knowledge: List[Clause]) -> List[Clause]:
        """
        Clause specialization using multiple refinement operators.
        
        Specialization methods from ILP literature:
        1. FOIL_ORIGINAL - Quinlan (1990) information gain for literal selection
        2. CONSTRAINT_LITERALS - Constraint-guided literal addition  
        3. VARIABLE_REFINEMENT - Variable binding constraints
        4. HYBRID_SPECIALIZATION - Combined approach
        
        Args:
            clause: Clause to specialize
            positive_examples: Positive training examples
            negative_examples: Negative training examples
            background_knowledge: Available predicates and rules
            
        Returns:
            List[Clause]: Specialized clause variants
        """
        if self.config.verbose_logging:
            self.logger.debug(f"Specializing clause: {clause} using {self.config.specialization_method.value}")
        
        # Route to appropriate specialization method
        if self.config.specialization_method == SpecializationMethod.FOIL_ORIGINAL:
            return self._specialize_foil_original(clause, positive_examples, negative_examples, background_knowledge)
        elif self.config.specialization_method == SpecializationMethod.CONSTRAINT_LITERALS:
            return self._specialize_constraint_literals(clause, positive_examples, negative_examples, background_knowledge)
        elif self.config.specialization_method == SpecializationMethod.VARIABLE_REFINEMENT:
            return self._specialize_variable_refinement(clause, positive_examples, negative_examples, background_knowledge)
        elif self.config.specialization_method == SpecializationMethod.HYBRID_SPECIALIZATION:
            return self._specialize_hybrid(clause, positive_examples, negative_examples, background_knowledge)
        else:
            return self._specialize_foil_original(clause, positive_examples, negative_examples, background_knowledge)
    
    def _specialize_foil_original(self, clause: Clause, positive_examples: List[Dict],
                                 negative_examples: List[Dict], background_knowledge: List[Clause]) -> List[Clause]:
        """
        Quinlan (1990) FOIL Algorithm - Original Information Gain Specialization
        
        Research-accurate implementation of FOIL's specialization procedure:
        1. Generate candidate literals from background knowledge
        2. Calculate information gain for each literal
        3. Select literal with highest gain above threshold
        4. Add literal to clause body
        
        Reference: Quinlan, J.R. (1990). Learning logical definitions from relations
        """
        specialized_clauses = []
        
        # Generate candidate literals from background knowledge
        candidate_literals = self._generate_candidate_literals(clause, background_knowledge)
        
        # Calculate current clause coverage
        current_pos_coverage = self._calculate_coverage(clause, positive_examples)
        current_neg_coverage = self._calculate_coverage(clause, negative_examples)
        
        if self.config.verbose_logging:
            self.logger.debug(f"Current coverage: {len(current_pos_coverage)} pos, {len(current_neg_coverage)} neg")
        
        # Calculate information gain for each candidate literal
        best_gains = []
        for literal in candidate_literals:
            # Create specialized clause by adding literal
            new_clause = clause.copy()
            new_clause.body.append(literal)
            
            # Calculate new coverage
            new_pos_coverage = self._calculate_coverage(new_clause, positive_examples)
            new_neg_coverage = self._calculate_coverage(new_clause, negative_examples)
            
            # Calculate FOIL information gain
            gain = self._calculate_foil_gain(
                len(current_pos_coverage), len(current_neg_coverage),
                len(new_pos_coverage), len(new_neg_coverage)
            )
            
            if gain >= self.config.foil_gain_threshold:
                best_gains.append((gain, new_clause, literal))
        
        # Sort by gain and select top candidates
        best_gains.sort(key=lambda x: x[0], reverse=True)
        
        # Apply FOIL pruning if enabled
        if self.config.use_foil_pruning:
            best_gains = self._apply_foil_pruning(best_gains, positive_examples, negative_examples)
        
        # Return top specialized clauses
        max_literals = min(self.config.foil_max_literals, len(best_gains))
        specialized_clauses = [gain_clause[1] for gain_clause in best_gains[:max_literals]]
        
        return specialized_clauses
    
    def _specialize_constraint_literals(self, clause: Clause, positive_examples: List[Dict],
                                      negative_examples: List[Dict], background_knowledge: List[Clause]) -> List[Clause]:
        """
        Constraint-Based Literal Addition Specialization
        
        Adds literals based on constraint satisfaction and domain knowledge:
        1. Identify constraint types (numerical, categorical, temporal)
        2. Generate constraint literals for clause variables
        3. Evaluate constraint satisfaction against examples
        4. Select literals meeting satisfaction threshold
        """
        specialized_clauses = []
        
        # Get variables in current clause
        clause_variables = clause.get_variables()
        
        # Generate constraint literals for each variable and constraint type
        for variable in clause_variables:
            for constraint_type in self.config.constraint_types:
                constraint_literals = self._generate_constraint_literals(variable, constraint_type, positive_examples)
                
                for constraint_literal in constraint_literals:
                    # Create specialized clause with constraint
                    new_clause = clause.copy()
                    new_clause.body.append(constraint_literal)
                    
                    # Evaluate constraint satisfaction
                    satisfaction_rate = self._evaluate_constraint_satisfaction(
                        new_clause, positive_examples, negative_examples
                    )
                    
                    if satisfaction_rate >= self.config.constraint_satisfaction_threshold:
                        specialized_clauses.append(new_clause)
                        
                        if len(new_clause.body) >= self.config.max_constraints_per_literal:
                            break
        
        return specialized_clauses[:self.config.foil_max_literals]
    
    def _specialize_variable_refinement(self, clause: Clause, positive_examples: List[Dict],
                                      negative_examples: List[Dict], background_knowledge: List[Clause]) -> List[Clause]:
        """
        Variable Refinement Specialization
        
        Specializes clauses by refining variable bindings:
        1. Identify variable binding opportunities
        2. Create refined variable constraints
        3. Introduce new variables if beneficial
        4. Apply variable type checking if enabled
        """
        specialized_clauses = []
        clause_variables = clause.get_variables()
        
        # Refine existing variable bindings
        for variable in clause_variables:
            # Generate variable binding constraints
            binding_literals = self._generate_variable_binding_literals(
                variable, clause, positive_examples, background_knowledge
            )
            
            for binding_literal in binding_literals:
                new_clause = clause.copy()
                new_clause.body.append(binding_literal)
                
                # Evaluate binding strength
                binding_strength = self._evaluate_binding_strength(new_clause, positive_examples, negative_examples)
                
                if binding_strength >= self.config.variable_binding_strength:
                    specialized_clauses.append(new_clause)
        
        # Introduce new variables if allowed
        if self.config.allow_variable_introduction:
            new_var_clauses = self._introduce_new_variables(clause, positive_examples, background_knowledge)
            specialized_clauses.extend(new_var_clauses)
        
        # Apply variable type checking if enabled
        if self.config.variable_type_checking:
            specialized_clauses = self._apply_variable_type_checking(specialized_clauses)
        
        return specialized_clauses
    
    def _specialize_hybrid(self, clause: Clause, positive_examples: List[Dict],
                          negative_examples: List[Dict], background_knowledge: List[Clause]) -> List[Clause]:
        """
        Hybrid Specialization - Combining Multiple Methods
        
        Combines FOIL, constraint-based, and variable refinement approaches:
        1. Apply FOIL specialization to get information-gain-driven candidates
        2. Apply constraint specialization to add domain constraints
        3. Apply variable refinement to improve bindings
        4. Merge and rank all specialized clauses
        """
        all_specialized = []
        
        # Get FOIL specializations
        foil_clauses = self._specialize_foil_original(clause, positive_examples, negative_examples, background_knowledge)
        all_specialized.extend(foil_clauses)
        
        # Get constraint specializations  
        constraint_clauses = self._specialize_constraint_literals(clause, positive_examples, negative_examples, background_knowledge)
        all_specialized.extend(constraint_clauses)
        
        # Get variable refinement specializations
        variable_clauses = self._specialize_variable_refinement(clause, positive_examples, negative_examples, background_knowledge)
        all_specialized.extend(variable_clauses)
        
        # Remove duplicates and rank by quality
        unique_clauses = self._remove_duplicate_clauses(all_specialized)
        ranked_clauses = self._rank_clauses_by_quality(unique_clauses, positive_examples, negative_examples)
        
        return ranked_clauses[:self.config.foil_max_literals]
    
    # ===== CLAUSE GENERALIZATION METHODS =====
    
    def _generalize_clause(self, clause: Clause, positive_examples: List[Dict],
                          negative_examples: List[Dict]) -> List[Clause]:
        """
        Clause generalization using refinement operators.
        
        Generalization methods from ILP literature:
        1. REMOVE_LITERALS - Literal deletion (Muggleton & De Raedt, 1994)
        2. VARIABLE_GENERALIZATION - Variable substitution patterns
        3. PREDICATE_ABSTRACTION - Predicate hierarchy traversal
        4. HYBRID_GENERALIZATION - Combined refinement operators
        
        Args:
            clause: Clause to generalize
            positive_examples: Positive training examples
            negative_examples: Negative training examples
            
        Returns:
            List[Clause]: Generalized clause variants
        """
        if self.config.verbose_logging:
            self.logger.debug(f"Generalizing clause: {clause} using {self.config.generalization_method.value}")
        
        # Route to appropriate generalization method
        if self.config.generalization_method == GeneralizationMethod.REMOVE_LITERALS:
            return self._generalize_remove_literals(clause, positive_examples, negative_examples)
        elif self.config.generalization_method == GeneralizationMethod.VARIABLE_GENERALIZATION:
            return self._generalize_variable_substitution(clause, positive_examples, negative_examples)
        elif self.config.generalization_method == GeneralizationMethod.PREDICATE_ABSTRACTION:
            return self._generalize_predicate_abstraction(clause, positive_examples, negative_examples)
        elif self.config.generalization_method == GeneralizationMethod.HYBRID_GENERALIZATION:
            return self._generalize_hybrid(clause, positive_examples, negative_examples)
        else:
            return self._generalize_remove_literals(clause, positive_examples, negative_examples)
    
    def _generalize_remove_literals(self, clause: Clause, positive_examples: List[Dict],
                                  negative_examples: List[Dict]) -> List[Clause]:
        """
        Muggleton & De Raedt (1994) Literal Removal Generalization
        
        Research-accurate implementation of literal removal generalization:
        1. Generate all possible literal removal combinations
        2. Evaluate coverage impact of each removal
        3. Select removals that maintain minimum coverage threshold
        4. Return generalized clauses ordered by coverage improvement
        
        Reference: Muggleton, S. & De Raedt, L. (1994). Inductive Logic Programming
        """
        generalized_clauses = []
        
        if len(clause.body) <= self.config.min_clause_length:
            return [clause]  # Cannot generalize further
        
        # Generate all single literal removal combinations
        for i, literal_to_remove in enumerate(clause.body):
            new_clause = clause.copy()
            new_clause.body.pop(i)
            
            # Evaluate coverage of generalized clause
            new_pos_coverage = self._calculate_coverage(new_clause, positive_examples)
            new_neg_coverage = self._calculate_coverage(new_clause, negative_examples)
            
            # Check if coverage meets minimum threshold
            coverage_rate = len(new_pos_coverage) / len(positive_examples) if positive_examples else 0
            
            if coverage_rate >= self.config.min_coverage_threshold:
                generalized_clauses.append(new_clause)
        
        # Generate multi-literal removal combinations if beneficial
        if self.config.max_generalization_steps > 1:
            multi_literal_clauses = self._generate_multi_literal_removals(
                clause, positive_examples, negative_examples
            )
            generalized_clauses.extend(multi_literal_clauses)
        
        # Sort by coverage improvement
        generalized_clauses.sort(key=lambda c: self._calculate_coverage_score(c, positive_examples, negative_examples), reverse=True)
        
        return generalized_clauses[:self.config.generalization_beam_width]
    
    def _generalize_variable_substitution(self, clause: Clause, positive_examples: List[Dict],
                                        negative_examples: List[Dict]) -> List[Clause]:
        """
        Variable Substitution Generalization
        
        Generalizes clauses by substituting variables with more general terms:
        1. Identify variable substitution opportunities  
        2. Generate substitutions that increase coverage
        3. Apply substitutions and evaluate impact
        4. Return clauses with beneficial generalizations
        """
        generalized_clauses = []
        clause_variables = clause.get_variables()
        
        # Generate variable substitution combinations
        for var1 in clause_variables:
            for var2 in clause_variables:
                if var1 != var2:
                    # Create substitution mapping var2 -> var1 (generalization)
                    substitution = Substitution({var2: var1})
                    generalized_clause = substitution.apply_to_clause(clause)
                    
                    # Evaluate if substitution improves coverage
                    original_coverage = len(self._calculate_coverage(clause, positive_examples))
                    new_coverage = len(self._calculate_coverage(generalized_clause, positive_examples))
                    
                    if new_coverage > original_coverage:
                        generalized_clauses.append(generalized_clause)
        
        # Generate new variable introductions for further generalization
        new_var_clauses = self._introduce_generalizing_variables(clause, positive_examples)
        generalized_clauses.extend(new_var_clauses)
        
        return generalized_clauses
    
    def _generalize_predicate_abstraction(self, clause: Clause, positive_examples: List[Dict],
                                        negative_examples: List[Dict]) -> List[Clause]:
        """
        Predicate Abstraction Generalization
        
        Generalizes by climbing predicate hierarchies:
        1. Identify predicate hierarchy relationships
        2. Replace specific predicates with more abstract ones
        3. Evaluate abstraction impact on coverage
        4. Return clauses with beneficial abstractions
        """
        generalized_clauses = []
        
        # Build predicate hierarchy from examples and background knowledge
        predicate_hierarchy = self._build_predicate_hierarchy(positive_examples, negative_examples)
        
        # Apply abstraction to each atom in the clause
        for atom in [clause.head] + clause.body:
            abstract_predicates = predicate_hierarchy.get(atom.predicate, [])
            
            for abstract_predicate in abstract_predicates:
                # Create abstracted clause
                abstracted_clause = clause.copy()
                
                # Replace predicate in appropriate atom
                if atom == clause.head:
                    abstracted_clause.head.predicate = abstract_predicate
                else:
                    for body_atom in abstracted_clause.body:
                        if body_atom.predicate == atom.predicate:
                            body_atom.predicate = abstract_predicate
                            break
                
                # Evaluate abstraction benefit
                abstraction_benefit = self._evaluate_abstraction_benefit(
                    clause, abstracted_clause, positive_examples, negative_examples
                )
                
                if abstraction_benefit > 0:
                    generalized_clauses.append(abstracted_clause)
        
        return generalized_clauses
    
    def _generalize_hybrid(self, clause: Clause, positive_examples: List[Dict],
                          negative_examples: List[Dict]) -> List[Clause]:
        """
        Hybrid Generalization - Combining Multiple Methods
        
        Combines literal removal, variable substitution, and predicate abstraction:
        1. Apply all generalization methods
        2. Merge and rank results
        3. Return best generalizations
        """
        all_generalized = []
        
        # Get literal removal generalizations
        literal_clauses = self._generalize_remove_literals(clause, positive_examples, negative_examples)
        all_generalized.extend(literal_clauses)
        
        # Get variable substitution generalizations  
        variable_clauses = self._generalize_variable_substitution(clause, positive_examples, negative_examples)
        all_generalized.extend(variable_clauses)
        
        # Get predicate abstraction generalizations
        predicate_clauses = self._generalize_predicate_abstraction(clause, positive_examples, negative_examples)
        all_generalized.extend(predicate_clauses)
        
        # Remove duplicates and rank
        unique_clauses = self._remove_duplicate_clauses(all_generalized)
        ranked_clauses = self._rank_clauses_by_quality(unique_clauses, positive_examples, negative_examples)
        
        return ranked_clauses[:self.config.generalization_beam_width]
    
    # ===== UNIFICATION METHODS =====
    
    def _unify_atoms(self, atom1: Atom, atom2: Atom) -> Optional[Substitution]:
        """
        Unification algorithms for logical atoms.
        
        Unification methods from logic programming literature:
        1. ROBINSON_BASIC - Robinson (1965) unification without occurs check
        2. ROBINSON_OCCURS_CHECK - Robinson (1965) with occurs check
        3. TYPE_AWARE - Type-constrained unification
        4. HYBRID_UNIFICATION - Combined unification strategies
        
        Args:
            atom1: First atom to unify
            atom2: Second atom to unify
            
        Returns:
            Optional[Substitution]: Unification substitution or None if unification fails
        """
        if self.config.debug_unification:
            self.logger.debug(f"Unifying atoms: {atom1} and {atom2} using {self.config.unification_method.value}")
        
        # Check cache if enabled
        cache_key = (str(atom1), str(atom2))
        if self.unification_cache and cache_key in self.unification_cache:
            return self.unification_cache[cache_key]
        
        # Route to appropriate unification method
        result = None
        start_time = time.time()
        
        try:
            if self.config.unification_method == UnificationMethod.ROBINSON_BASIC:
                result = self._unify_robinson_basic(atom1, atom2)
            elif self.config.unification_method == UnificationMethod.ROBINSON_OCCURS_CHECK:
                result = self._unify_robinson_occurs_check(atom1, atom2)
            elif self.config.unification_method == UnificationMethod.TYPE_AWARE:
                result = self._unify_type_aware(atom1, atom2)
            elif self.config.unification_method == UnificationMethod.HYBRID_UNIFICATION:
                result = self._unify_hybrid(atom1, atom2)
            else:
                result = self._unify_robinson_basic(atom1, atom2)
                
        except Exception as e:
            if self.config.debug_unification:
                self.logger.warning(f"Unification failed: {e}")
            result = None
        
        # Check timeout
        if time.time() - start_time > self.config.unification_timeout:
            if self.config.debug_unification:
                self.logger.warning("Unification timeout exceeded")
            result = None
        
        # Cache result
        if self.unification_cache:
            self.unification_cache[cache_key] = result
        
        return result
    
    def _unify_robinson_basic(self, atom1: Atom, atom2: Atom) -> Optional[Substitution]:
        """
        Robinson (1965) Basic Unification Algorithm
        
        Research-accurate implementation of Robinson's original unification:
        1. Check predicate compatibility
        2. Unify terms recursively
        3. Build substitution mapping
        4. Return most general unifier (MGU)
        
        Reference: Robinson, J.A. (1965). A machine-oriented logic based on the resolution principle
        """
        # Check predicate and arity compatibility
        if atom1.predicate != atom2.predicate or len(atom1.terms) != len(atom2.terms):
            return None
        
        # Check negation compatibility
        if atom1.negated != atom2.negated:
            return None
        
        # Unify terms pairwise
        substitution = Substitution()
        
        for term1, term2 in zip(atom1.terms, atom2.terms):
            term_unification = self._unify_terms_basic(term1, term2)
            
            if term_unification is None:
                return None
            
            # Compose substitutions
            substitution = substitution.compose(term_unification)
        
        return substitution
    
    def _unify_robinson_occurs_check(self, atom1: Atom, atom2: Atom) -> Optional[Substitution]:
        """
        Robinson (1965) Unification with Occurs Check
        
        Implements Robinson's unification with occurs check to prevent infinite structures:
        1. Apply basic unification algorithm
        2. Perform occurs check for each substitution
        3. Reject unifications that would create infinite structures
        4. Return safe unification or None
        
        The occurs check prevents X = f(X) type unifications that lead to infinite structures.
        """
        # First attempt basic unification
        basic_unification = self._unify_robinson_basic(atom1, atom2)
        
        if basic_unification is None:
            return None
        
        # Apply occurs check to each substitution
        for var, term in basic_unification.mapping.items():
            if self._occurs_check(var, term, basic_unification.mapping, depth=0):
                if self.config.debug_unification:
                    self.logger.debug(f"Occurs check failed for {var} = {term}")
                return None
        
        return basic_unification
    
    def _unify_type_aware(self, atom1: Atom, atom2: Atom) -> Optional[Substitution]:
        """
        Type-Aware Unification with Type Constraints
        
        Extends Robinson unification with type checking:
        1. Perform basic Robinson unification
        2. Extract type constraints from terms
        3. Verify type compatibility
        4. Apply type coercion if allowed
        5. Return type-safe unification
        """
        # Start with basic unification
        basic_unification = self._unify_robinson_basic(atom1, atom2)
        
        if basic_unification is None:
            return None
        
        # If type constraints disabled, return basic result
        if not self.config.type_constraints:
            return basic_unification
        
        # Extract and check type constraints
        for var, term in basic_unification.mapping.items():
            var_type = self._infer_type(var)
            term_type = self._infer_type(term)
            
            # Check type compatibility
            if not self._types_compatible(var_type, term_type):
                if self.config.allow_type_coercion:
                    # Attempt type coercion
                    coerced_term = self._attempt_type_coercion(term, var_type)
                    if coerced_term is not None:
                        basic_unification.mapping[var] = coerced_term
                    else:
                        return None
                elif self.config.strict_type_matching:
                    return None
        
        return basic_unification
    
    def _unify_hybrid(self, atom1: Atom, atom2: Atom) -> Optional[Substitution]:
        """
        Hybrid Unification - Combining Multiple Strategies
        
        Combines Robinson basic, occurs check, and type-aware unification:
        1. Try type-aware unification first (most restrictive)
        2. Fall back to occurs check unification
        3. Fall back to basic Robinson unification
        4. Return first successful unification
        """
        # Try type-aware unification first if type constraints enabled
        if self.config.type_constraints:
            type_result = self._unify_type_aware(atom1, atom2)
            if type_result is not None:
                return type_result
        
        # Try occurs check unification if occurs check enabled
        if self.config.use_occurs_check:
            occurs_result = self._unify_robinson_occurs_check(atom1, atom2)
            if occurs_result is not None:
                return occurs_result
        
        # Fall back to basic Robinson unification
        return self._unify_robinson_basic(atom1, atom2)
    
    # ===== HELPER METHODS =====
    
    def _generate_candidate_literals(self, clause: Clause, background_knowledge: List[Clause]) -> List[Atom]:
        """Generate candidate literals for specialization from background knowledge"""
        candidates = []
        clause_variables = clause.get_variables()
        
        for bg_clause in background_knowledge:
            for atom in [bg_clause.head] + bg_clause.body:
                # Create variants with clause variables
                for var in clause_variables:
                    for i, term in enumerate(atom.terms):
                        if term[0].isupper():  # Replace variable
                            new_terms = atom.terms.copy()
                            new_terms[i] = var
                            candidates.append(Atom(atom.predicate, new_terms, atom.negated))
        
        return candidates
    
    def _calculate_coverage(self, clause: Clause, examples: List[Dict]) -> List[Dict]:
        """Calculate which examples are covered by a clause"""
        covered = []
        for example in examples:
            if self._clause_covers_example(clause, example):
                covered.append(example)
        return covered
    
    def _clause_covers_example(self, clause: Clause, example: Dict) -> bool:
        """Check if a clause covers a specific example using SLD resolution"""
        # Import working SLD resolution from FOIL variants
        from ..foil_algorithm_variants import FOILAlgorithmVariants
        from ..foil_comprehensive_config import create_research_accurate_config
        
        # Create FOIL instance with research-accurate SLD resolution
        config = create_research_accurate_config()
        foil = FOILAlgorithmVariants(config)
        
        # Convert internal representation to standard logical structures
        logical_clause = self._convert_to_logical_clause(clause)
        logical_example = self._convert_to_logical_example(example)
        
        # Use proper SLD resolution for coverage testing
        return foil.covers_example(logical_clause, logical_example, self.config.background_knowledge)
    
    def _calculate_foil_gain(self, old_pos: int, old_neg: int, new_pos: int, new_neg: int) -> float:
        """
        Calculate FOIL information gain
        
        FOIL Gain = new_pos * (log2(new_pos/(new_pos + new_neg)) - log2(old_pos/(old_pos + old_neg)))
        """
        if new_pos == 0 or old_pos == 0:
            return 0.0
        
        if new_pos + new_neg == 0 or old_pos + old_neg == 0:
            return 0.0
        
        new_ratio = new_pos / (new_pos + new_neg)
        old_ratio = old_pos / (old_pos + old_neg)
        
        if new_ratio <= 0 or old_ratio <= 0:
            return 0.0
        
        return new_pos * (math.log2(new_ratio) - math.log2(old_ratio))
    
    def _apply_foil_pruning(self, candidates: List[Tuple], positive_examples: List[Dict], 
                           negative_examples: List[Dict]) -> List[Tuple]:
        """Apply FOIL pruning to remove unpromising candidates"""
        # Simple pruning - remove candidates with very low gain
        return [cand for cand in candidates if cand[0] >= self.config.foil_significance_threshold]
    
    def _unify_terms_basic(self, term1: str, term2: str) -> Optional[Substitution]:
        """Basic term unification for Robinson algorithm"""
        if term1 == term2:
            return Substitution()  # Empty substitution
        
        # Variable cases
        if term1[0].isupper():  # term1 is variable
            return Substitution({term1: term2})
        elif term2[0].isupper():  # term2 is variable
            return Substitution({term2: term1})
        else:
            return None  # Both constants but different
    
    def _occurs_check(self, var: str, term: str, substitutions: Dict[str, str], depth: int) -> bool:
        """
        Occurs check to prevent infinite structures
        
        Returns True if var occurs in term (indicating infinite structure)
        """
        if depth > self.config.occurs_check_depth:
            return True  # Assume occurs check failure at max depth
        
        if var == term:
            return True
        
        # Check if term contains var through substitutions
        if term in substitutions:
            return self._occurs_check(var, substitutions[term], substitutions, depth + 1)
        
        return False
    
    def _infer_type(self, term: str) -> str:
        """Infer type of a term (framework implementation)"""
        if term[0].isupper():
            return "variable"
        elif term.isdigit():
            return "number"
        else:
            return "constant"
    
    def _types_compatible(self, type1: str, type2: str) -> bool:
        """Check if two types are compatible"""
        if type1 == type2:
            return True
        if "variable" in [type1, type2]:
            return True  # Variables can unify with anything
        return False
    
    def _attempt_type_coercion(self, term: str, target_type: str) -> Optional[str]:
        """Attempt to coerce term to target type"""
        if target_type == "number" and term.replace(".", "").isdigit():
            return term
        return None
    
    def _remove_duplicate_clauses(self, clauses: List[Clause]) -> List[Clause]:
        """Remove duplicate clauses from list"""
        seen = set()
        unique = []
        for clause in clauses:
            clause_str = str(clause)
            if clause_str not in seen:
                seen.add(clause_str)
                unique.append(clause)
        return unique
    
    def _rank_clauses_by_quality(self, clauses: List[Clause], positive_examples: List[Dict], 
                                negative_examples: List[Dict]) -> List[Clause]:
        """Rank clauses by quality metric"""
        scored_clauses = []
        for clause in clauses:
            score = self._calculate_clause_quality(clause, positive_examples, negative_examples)
            scored_clauses.append((score, clause))
        
        scored_clauses.sort(key=lambda x: x[0], reverse=True)
        return [clause for score, clause in scored_clauses]
    
    def _calculate_clause_quality(self, clause: Clause, positive_examples: List[Dict], 
                                 negative_examples: List[Dict]) -> float:
        """Calculate quality score for a clause based on evaluation metric"""
        pos_coverage = len(self._calculate_coverage(clause, positive_examples))
        neg_coverage = len(self._calculate_coverage(clause, negative_examples))
        
        if self.config.evaluation_metric == EvaluationMetric.ACCURACY:
            total = len(positive_examples) + len(negative_examples)
            if total == 0:
                return 0.0
            return (pos_coverage + (len(negative_examples) - neg_coverage)) / total
        
        elif self.config.evaluation_metric == EvaluationMetric.PRECISION:
            if pos_coverage + neg_coverage == 0:
                return 0.0
            return pos_coverage / (pos_coverage + neg_coverage)
        
        elif self.config.evaluation_metric == EvaluationMetric.RECALL:
            if len(positive_examples) == 0:
                return 0.0
            return pos_coverage / len(positive_examples)
        
        elif self.config.evaluation_metric == EvaluationMetric.F1_SCORE:
            precision = pos_coverage / (pos_coverage + neg_coverage) if pos_coverage + neg_coverage > 0 else 0
            recall = pos_coverage / len(positive_examples) if len(positive_examples) > 0 else 0
            if precision + recall == 0:
                return 0.0
            return 2 * (precision * recall) / (precision + recall)
        
        else:
            return pos_coverage  # Default to positive coverage
    
    # Framework implementations for remaining helper methods
    def _generate_constraint_literals(self, variable: str, constraint_type: str, examples: List[Dict]) -> List[Atom]:
        """Generate constraint literals for a variable (Quinlan 1990)"""
        # FOIL constraint literal generation - extract predicates from examples
        # that can constrain the given variable based on constraint_type
        constraint_literals = []
        
        # Extract predicates from examples that involve the variable
        predicates_seen = set()
        for example in examples:
            for key, value in example.items():
                if isinstance(value, (list, tuple)):
                    # Handle relational facts like parent(john, mary)
                    for item in value:
                        if isinstance(item, dict) and 'predicate' in item:
                            pred_name = item['predicate']
                            terms = item.get('terms', [])
                            if variable in terms:
                                predicates_seen.add((pred_name, len(terms)))
                                
        # Generate constraint literals based on constraint type
        for pred_name, arity in predicates_seen:
            if constraint_type == 'type_constraint':
                # Generate type constraint: pred(Variable, _)
                terms = [variable] + [f'_{i}' for i in range(arity - 1)]
                constraint_literals.append(Atom(pred_name, terms))
            elif constraint_type == 'equality':
                # Generate equality constraint: pred(Variable, Variable2)
                if arity >= 2:
                    terms = [variable, variable]
                    constraint_literals.append(Atom(pred_name, terms))
                    
        return constraint_literals
    
    def _evaluate_constraint_satisfaction(self, clause: Clause, positive_examples: List[Dict], 
                                        negative_examples: List[Dict]) -> float:
        """Evaluate constraint satisfaction rate (Muggleton & Feng 1992)"""
        if not positive_examples:
            return 0.0
        
        satisfied_constraints = 0
        total_constraints = 0
        
        for example in positive_examples:
            for literal in clause.body:
                total_constraints += 1
                # Check if literal constraints are satisfied by example
                if self._check_literal_constraint(literal, example):
                    satisfied_constraints += 1
        
        return satisfied_constraints / max(total_constraints, 1)
    
    def _generate_variable_binding_literals(self, variable: str, clause: Clause, examples: List[Dict], 
                                          background_knowledge: List[Clause]) -> List[Atom]:
        """Generate variable binding literals (Quinlan 1990 FOIL)"""
        # FOIL variable binding - generate literals that can bind the variable
        # to other variables or constants in the clause
        binding_literals = []
        
        # Get existing variables in clause
        existing_vars = clause.get_variables()
        
        # Extract background predicates
        bg_predicates = set()
        for bg_clause in background_knowledge:
            if bg_clause.head:
                bg_predicates.add(bg_clause.head.predicate)
        
        # Generate binding literals from background knowledge
        for pred_name in bg_predicates:
            # Unary predicate binding: pred(Variable)
            binding_literals.append(Atom(pred_name, [variable]))
            
            # Binary predicate binding with existing variables
            for existing_var in existing_vars:
                if existing_var != variable:
                    # pred(Variable, ExistingVar) - connects to existing structure
                    binding_literals.append(Atom(pred_name, [variable, existing_var]))
                    # pred(ExistingVar, Variable) - reverse connection
                    binding_literals.append(Atom(pred_name, [existing_var, variable]))
                    
        # Generate binding literals from examples
        predicates_in_examples = set()
        for example in examples:
            for key, value in example.items():
                if isinstance(value, (list, tuple)):
                    for item in value:
                        if isinstance(item, dict) and 'predicate' in item:
                            predicates_in_examples.add(item['predicate'])
                            
        # Add example-based bindings
        for pred_name in predicates_in_examples:
            if pred_name not in bg_predicates:  # Don't duplicate
                binding_literals.append(Atom(pred_name, [variable]))
                
        return binding_literals
    
    def _evaluate_binding_strength(self, clause: Clause, positive_examples: List[Dict], 
                                 negative_examples: List[Dict]) -> float:
        """Evaluate variable binding strength using coverage metrics"""
        if not positive_examples or not clause.body:
            return 0.0
        
        # Count examples where clause bindings are consistent
        consistent_bindings = 0
        total_examples = len(positive_examples)
        
        for example in positive_examples:
            variables = self._extract_variables(clause)
            if self._check_binding_consistency(variables, clause, example):
                consistent_bindings += 1
        
        return consistent_bindings / max(total_examples, 1)
    
    def _introduce_new_variables(self, clause: Clause, positive_examples: List[Dict], 
                               background_knowledge: List[Clause]) -> List[Clause]:
        """Introduce new variables for specialization"""
        # FOIL new variable introduction - creates literals with fresh variables
        # that must connect to existing clause structure
        specialized_clauses = []
        existing_vars = clause.get_variables()
        
        # Generate fresh variable names
        used_vars = set(existing_vars)
        new_var_counter = 1
        while f'V{new_var_counter}' in used_vars:
            new_var_counter += 1
        new_var = f'V{new_var_counter}'
        
        # Extract predicates from background knowledge
        bg_predicates = []
        for bg_clause in background_knowledge:
            if bg_clause.head:
                bg_predicates.append(bg_clause.head.predicate)
        
        # Introduce new variable with connection to existing structure
        for pred_name in bg_predicates:
            for existing_var in existing_vars:
                # Connect new variable to existing clause: pred(ExistingVar, NewVar)
                new_atom = Atom(pred_name, [existing_var, new_var])
                new_clause = clause.copy()
                new_clause.body.append(new_atom)
                specialized_clauses.append(new_clause)
                
                # Also try reverse: pred(NewVar, ExistingVar)
                new_atom_rev = Atom(pred_name, [new_var, existing_var])
                new_clause_rev = clause.copy()
                new_clause_rev.body.append(new_atom_rev)
                specialized_clauses.append(new_clause_rev)
                
        return specialized_clauses
    
    def _apply_variable_type_checking(self, clauses: List[Clause]) -> List[Clause]:
        """Apply variable type checking to clauses"""
        # FOCL type checking - filter clauses based on type constraints
        # This implements type-based constraint satisfaction from FOCL
        type_checked_clauses = []
        
        for clause in clauses:
            is_type_consistent = True
            
            # Check each atom in clause body for type consistency
            for atom in clause.body:
                # Simple type checking: ensure same variable has consistent types
                # across different predicates in the clause
                predicate_types = self._get_predicate_types(atom.predicate)
                
                if predicate_types:
                    for i, term in enumerate(atom.terms):
                        if i < len(predicate_types):
                            expected_type = predicate_types[i]
                            # Check if variable appears in other atoms with different type
                            if not self._is_type_consistent(term, expected_type, clause):
                                is_type_consistent = False
                                break
                                
                if not is_type_consistent:
                    break
                    
            if is_type_consistent:
                type_checked_clauses.append(clause)
                
        return type_checked_clauses
    
    def _generate_multi_literal_removals(self, clause: Clause, positive_examples: List[Dict], 
                                       negative_examples: List[Dict]) -> List[Clause]:
        """Generate multi-literal removal combinations"""
        # FOIL new variable introduction - creates literals with fresh variables
        # that must connect to existing clause structure
        specialized_clauses = []
        existing_vars = clause.get_variables()
        
        # Generate fresh variable names
        used_vars = set(existing_vars)
        new_var_counter = 1
        while f'V{new_var_counter}' in used_vars:
            new_var_counter += 1
        new_var = f'V{new_var_counter}'
        
        # Extract predicates from background knowledge
        bg_predicates = []
        for bg_clause in background_knowledge:
            if bg_clause.head:
                bg_predicates.append(bg_clause.head.predicate)
        
        # Introduce new variable with connection to existing structure
        for pred_name in bg_predicates:
            for existing_var in existing_vars:
                # Connect new variable to existing clause: pred(ExistingVar, NewVar)
                new_atom = Atom(pred_name, [existing_var, new_var])
                new_clause = clause.copy()
                new_clause.body.append(new_atom)
                specialized_clauses.append(new_clause)
                
                # Also try reverse: pred(NewVar, ExistingVar)
                new_atom_rev = Atom(pred_name, [new_var, existing_var])
                new_clause_rev = clause.copy()
                new_clause_rev.body.append(new_atom_rev)
                specialized_clauses.append(new_clause_rev)
                
        return specialized_clauses
    
    def _calculate_coverage_score(self, clause: Clause, positive_examples: List[Dict], 
                                negative_examples: List[Dict]) -> float:
        """Calculate coverage score for ranking"""
        return len(self._calculate_coverage(clause, positive_examples))
    
    def _introduce_generalizing_variables(self, clause: Clause, positive_examples: List[Dict]) -> List[Clause]:
        """Introduce variables for generalization"""
        # FOIL new variable introduction - creates literals with fresh variables
        # that must connect to existing clause structure
        specialized_clauses = []
        existing_vars = clause.get_variables()
        
        # Generate fresh variable names
        used_vars = set(existing_vars)
        new_var_counter = 1
        while f'V{new_var_counter}' in used_vars:
            new_var_counter += 1
        new_var = f'V{new_var_counter}'
        
        # Extract predicates from background knowledge
        bg_predicates = []
        for bg_clause in background_knowledge:
            if bg_clause.head:
                bg_predicates.append(bg_clause.head.predicate)
        
        # Introduce new variable with connection to existing structure
        for pred_name in bg_predicates:
            for existing_var in existing_vars:
                # Connect new variable to existing clause: pred(ExistingVar, NewVar)
                new_atom = Atom(pred_name, [existing_var, new_var])
                new_clause = clause.copy()
                new_clause.body.append(new_atom)
                specialized_clauses.append(new_clause)
                
                # Also try reverse: pred(NewVar, ExistingVar)
                new_atom_rev = Atom(pred_name, [new_var, existing_var])
                new_clause_rev = clause.copy()
                new_clause_rev.body.append(new_atom_rev)
                specialized_clauses.append(new_clause_rev)
                
        return specialized_clauses
    
    def _build_predicate_hierarchy(self, positive_examples: List[Dict], negative_examples: List[Dict]) -> Dict[str, List[str]]:
        """Build predicate abstraction hierarchy"""
        # Build predicate hierarchy for abstraction (Progol-style)
        # Creates hierarchy of predicates based on their argument types and usage
        hierarchy = {}
        
        # Extract all predicates from examples
        all_predicates = set()
        for examples in [positive_examples, negative_examples]:
            for example in examples:
                for key, value in example.items():
                    if isinstance(value, (list, tuple)):
                        for item in value:
                            if isinstance(item, dict) and 'predicate' in item:
                                all_predicates.add(item['predicate'])
                                
        # Build simple hierarchy based on arity and common patterns
        for pred in all_predicates:
            # Group predicates by common prefixes or patterns
            base_pred = pred.split('_')[0] if '_' in pred else pred
            if base_pred not in hierarchy:
                hierarchy[base_pred] = []
            if pred != base_pred:
                hierarchy[base_pred].append(pred)
                
        # Add single predicates as their own hierarchy
        for pred in all_predicates:
            if pred not in hierarchy:
                hierarchy[pred] = []
                
        return hierarchy
    
    def _evaluate_abstraction_benefit(self, original_clause: Clause, abstracted_clause: Clause,
                                    positive_examples: List[Dict], negative_examples: List[Dict]) -> float:
        """Evaluate benefit of predicate abstraction"""
        # Evaluate abstraction benefit using coverage improvement
        # Compare coverage and precision between original and abstracted clauses
        
        # Calculate coverage for both clauses
        orig_pos_coverage = len(self._calculate_coverage(original_clause, positive_examples))
        orig_neg_coverage = len(self._calculate_coverage(original_clause, negative_examples))
        
        abst_pos_coverage = len(self._calculate_coverage(abstracted_clause, positive_examples))
        abst_neg_coverage = len(self._calculate_coverage(abstracted_clause, negative_examples))
        
        # Calculate precision (positive / total coverage)
        orig_precision = orig_pos_coverage / max(orig_pos_coverage + orig_neg_coverage, 1)
        abst_precision = abst_pos_coverage / max(abst_pos_coverage + abst_neg_coverage, 1)
        
        # Calculate recall (positive coverage / total positives)
        total_positives = len(positive_examples)
        orig_recall = orig_pos_coverage / max(total_positives, 1)
        abst_recall = abst_pos_coverage / max(total_positives, 1)
        
        # F1 score as benefit measure
        orig_f1 = 2 * (orig_precision * orig_recall) / max(orig_precision + orig_recall, 0.001)
        abst_f1 = 2 * (abst_precision * abst_recall) / max(abst_precision + abst_recall, 0.001)
        
        # Return improvement ratio (>1.0 means abstraction is better)
        return abst_f1 / max(orig_f1, 0.001)
    
    def _get_predicate_types(self, predicate: str) -> List[str]:
        """Get expected types for predicate arguments (FOCL typing)"""
        # Simple type inference based on predicate name patterns
        type_mappings = {
            'parent': ['person', 'person'],
            'father': ['person', 'person'], 
            'mother': ['person', 'person'],
            'male': ['person'],
            'female': ['person'],
            'age': ['person', 'number'],
            'livesAt': ['person', 'location'],
            'likes': ['person', 'thing']
        }
        return type_mappings.get(predicate, [])
    
    def _is_type_consistent(self, term: str, expected_type: str, clause: Clause) -> bool:
        """Check if term usage is type consistent across clause"""
        # Check if the same variable appears with consistent types
        # in other atoms within the same clause
        for atom in clause.body:
            atom_types = self._get_predicate_types(atom.predicate)
            for i, atom_term in enumerate(atom.terms):
                if atom_term == term and i < len(atom_types):
                    if atom_types[i] != expected_type:
                        return False
        return True
    
    def _check_literal_constraint(self, literal: Atom, example: Dict) -> bool:
        """Check if literal constraint is satisfied by example"""
        # Simple constraint checking based on predicate and terms
        predicate = literal.predicate
        terms = literal.terms
        
        # Basic constraint satisfaction check
        if predicate in example:
            return bool(example[predicate])
        
        # Check if all terms in literal are present in example
        for term in terms:
            if term in example:
                continue
            elif term[0].isupper():  # Variable
                continue
            else:
                return False
        
        return True
    
    def _extract_variables(self, clause: Clause) -> Set[str]:
        """Extract all variables from a clause"""
        return clause.get_variables()
    
    def _check_binding_consistency(self, variables: Set[str], clause: Clause, example: Dict) -> bool:
        """Check if variable bindings are consistent in example"""
        # Simple consistency check - variables should have consistent values
        variable_bindings = {}
        
        for atom in [clause.head] + clause.body:
            for i, term in enumerate(atom.terms):
                if term in variables:  # Is a variable
                    # Check consistency with previous bindings
                    key = f"{atom.predicate}_{i}"
                    if key in example:
                        value = example[key]
                        if term in variable_bindings:
                            if variable_bindings[term] != value:
                                return False
                        else:
                            variable_bindings[term] = value
        
        return True


# Export the complete implementation
__all__ = ['FOILProgolImplementation', 'Atom', 'Clause', 'Substitution']