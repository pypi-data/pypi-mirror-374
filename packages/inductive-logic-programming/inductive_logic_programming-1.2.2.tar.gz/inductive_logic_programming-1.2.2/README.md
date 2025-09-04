# 💰 Support This Research - Please Donate!

**🙏 If this library helps your research or project, please consider donating to support continued development:**

<div align="center">

**[💳 DONATE VIA PAYPAL](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)** | **[❤️ SPONSOR ON GITHUB](https://github.com/sponsors/benedictchen)**

</div>

[![CI](https://github.com/benedictchen/inductive-logic-programming/workflows/CI/badge.svg)](https://github.com/benedictchen/inductive-logic-programming/actions)
[![PyPI version](https://badge.fury.io/py/inductive-logic-programming.svg)](https://badge.fury.io/py/inductive-logic-programming)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Custom%20Non--Commercial-red.svg)](LICENSE)
[![Research Accurate](https://img.shields.io/badge/research-accurate-brightgreen.svg)](RESEARCH_FOUNDATION.md)

---

# Inductive Logic Programming

🧠 **Learn logical rules from examples using FOIL and Progol algorithms**

Inductive Logic Programming (ILP) automatically discovers logical rules and relationships from examples and background knowledge. This implementation provides research-accurate reproductions of the foundational FOIL and Progol algorithms that revolutionized machine learning by combining logic programming with inductive learning.

**Research Foundation**: Quinlan, J. R. (1990) - *"Learning Logical Definitions from Relations"* | Muggleton, S. (1995) - *"Inverse Entailment and Progol"*

## 📦 Installation

```bash
pip install inductive-logic-programming
```

## 🚀 Quick Start

### FOIL Algorithm Example
```python
from inductive_logic_programming import FOIL
import pandas as pd

# Create FOIL learner
foil = FOIL(
    max_variables=5,
    min_positive_coverage=2,
    significance_threshold=0.05
)

# Example: Learning family relationships
# Positive examples: parent(tom, bob), parent(pam, bob), parent(tom, ann)
# Negative examples: parent(bob, tom), parent(ann, pam)

positive_examples = [
    ('parent', ['tom', 'bob']),
    ('parent', ['pam', 'bob']), 
    ('parent', ['tom', 'ann']),
    ('parent', ['bob', 'charlie'])
]

negative_examples = [
    ('parent', ['bob', 'tom']),
    ('parent', ['ann', 'pam']),
    ('parent', ['charlie', 'tom'])
]

# Background knowledge
background = {
    'male': [['tom'], ['bob'], ['charlie']],
    'female': [['pam'], ['ann']],
    'older': [['tom', 'bob'], ['pam', 'bob'], ['tom', 'ann']]
}

# Learn rules
rules = foil.learn(positive_examples, negative_examples, background)
print("Learned rules:", rules)
```

### Progol Algorithm Example  
```python
from inductive_logic_programming import Progol

# Create Progol learner
progol = Progol(
    max_clause_length=5,
    max_search_depth=3,
    compression_required=2
)

# Example: Learning append/3 predicate
examples = {
    'positive': [
        'append([], [1,2], [1,2])',
        'append([1], [2], [1,2])', 
        'append([1,2], [], [1,2])',
        'append([1], [2,3], [1,2,3])'
    ],
    'negative': [
        'append([1], [2], [2,1])',
        'append([1,2], [3], [1,3,2])'
    ]
}

background_knowledge = [
    'list([]).', 
    'list([H|T]) :- list(T).',
    'member(X, [X|_]).',
    'member(X, [_|T]) :- member(X, T).'
]

# Learn clauses
clauses = progol.induce(examples, background_knowledge)
print("Learned clauses:", clauses)
```

## 🔬 Advanced Features

### Rule Refinement
```python
from inductive_logic_programming import RuleRefinement

refiner = RuleRefinement(
    refinement_operator='rho',
    completeness_check=True,
    consistency_check=True
)

# Refine an initial hypothesis
initial_rule = "parent(X, Y) :- older(X, Y)"
refined_rules = refiner.refine(
    initial_rule, 
    positive_examples, 
    negative_examples,
    background
)
```

### Custom Predicate Learning
```python
from inductive_logic_programming import PredicateLearner

# Learn custom predicates with domain-specific knowledge
learner = PredicateLearner(
    target_predicate='grandparent',
    mode_declarations=[
        'grandparent(+person, +person)',
        'parent(+person, -person)',
        'parent(-person, +person)'
    ]
)

examples = [
    'grandparent(tom, charlie)',
    'grandparent(pam, charlie)'
]

learned_def = learner.induce_definition(examples, background)
```

## 🧬 Key Algorithmic Features

### FOIL Algorithm
- **Information Gain Heuristic**: Selects literals that maximize information gain
- **Pruning Strategies**: Eliminates unpromising search paths early
- **Significance Testing**: Statistical validation of learned rules
- **Incremental Learning**: Can learn from streaming examples

### Progol System  
- **Mode-Directed Inverse Entailment**: Efficient bottom-up clause construction
- **Compression-Based Learning**: Prioritizes hypotheses with high compression
- **Clause Refinement**: Systematic search through hypothesis space
- **Background Knowledge Integration**: Seamless use of domain knowledge

### Rule Quality Metrics
- **Coverage**: Number of positive examples explained by rule
- **Precision**: Ratio of correctly classified positive examples  
- **Compression**: Reduction in description length
- **Statistical Significance**: Confidence in learned patterns

## 📊 Implementation Highlights

- **Research Accuracy**: Faithful implementation of original algorithms
- **Logic Programming Integration**: Full Prolog compatibility
- **Scalable Learning**: Handles large datasets efficiently
- **Educational Value**: Clear implementation for learning ILP concepts
- **Extensible Framework**: Easy to add new learning algorithms

## 📖 Documentation & Tutorials

- 📚 **[Complete Documentation](https://inductive-logic-programming.readthedocs.io/)**
- 🎓 **[Tutorial Notebooks](https://github.com/benedictchen/inductive-logic-programming/tree/main/tutorials)**
- 🔬 **[Research Foundation](RESEARCH_FOUNDATION.md)**
- 🎯 **[Advanced Examples](https://github.com/benedictchen/inductive-logic-programming/tree/main/examples)**
- 🐛 **[Issue Tracker](https://github.com/benedictchen/inductive-logic-programming/issues)**

## 🤝 Contributing

We welcome contributions! Please see:

- **[Contributing Guidelines](CONTRIBUTING.md)**
- **[Development Setup](docs/development.md)**  
- **[Code of Conduct](CODE_OF_CONDUCT.md)**

### Development Installation

```bash
git clone https://github.com/benedictchen/inductive-logic-programming.git
cd inductive-logic-programming
pip install -e ".[test,dev]"
pytest tests/
```

## 📜 Citation

If you use this implementation in academic work, please cite:

```bibtex
@software{inductive_logic_programming_benedictchen,
    title={Inductive Logic Programming: Research-Accurate Implementation of FOIL and Progol},
    author={Benedict Chen},
    year={2025},
    url={https://github.com/benedictchen/inductive-logic-programming},
    version={1.1.0}
}

@article{quinlan1990learning,
    title={Learning logical definitions from relations},
    author={Quinlan, J Ross},
    journal={Machine learning},
    volume={5},
    number={3},
    pages={239--266},
    year={1990},
    publisher={Springer}
}
```

## 📋 License

**Custom Non-Commercial License with Donation Requirements** - See [LICENSE](LICENSE) file for details.

## 🎓 About the Implementation

**Implemented by Benedict Chen** - Bringing foundational AI research to modern Python.

📧 **Contact**: benedict@benedictchen.com  
🐙 **GitHub**: [@benedictchen](https://github.com/benedictchen)

---

## 💰 Support This Work - Choose Your Adventure!

**This implementation represents hundreds of hours of research and development. If you find it valuable, please consider donating:**

### 🎯 Donation Tier Goals (With Logic Programming Humor)

**☕ $5 - Buy Benedict Coffee**  
*"Caffeine is like background knowledge - it makes everything else work better! coffee(benedict) :- productive(benedict)."*  
💳 [PayPal One-time](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Monthly](https://github.com/sponsors/benedictchen)

**🍕 $25 - Pizza Fund**  
*"pizza(X) :- hungry(benedict), delicious(X), fast_delivery(X). Query: ?- pizza(margherita)."*  
💳 [PayPal One-time](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Monthly](https://github.com/sponsors/benedictchen)

**🏠 $500,000 - Buy Benedict a House**  
*"house(benedict) :- donation(X), X >= 500000. Currently: house(benedict) :- false. Please help resolve this query!"*  
💳 [PayPal Challenge](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Lifetime](https://github.com/sponsors/benedictchen)

**🚀 $10,000,000,000 - Space Program**  
*"space_program(benedict) :- funding(X), X > 10000000000, zero_gravity(Y), foil_algorithm(Y). Testing FOIL in zero gravity for science!"*  
💳 [PayPal Cosmic](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Galactic](https://github.com/sponsors/benedictchen)

### 🎪 Monthly Subscription Tiers (GitHub Sponsors)

**🧠 Logic Programmer ($10/month)** - *"Monthly support for maximum logical consistency in my code!"*  
❤️ [Subscribe on GitHub](https://github.com/sponsors/benedictchen)

**🔍 Rule Discoverer ($25/month)** - *"Help me discover the rules for sustainable open source development!"*  
❤️ [Subscribe on GitHub](https://github.com/sponsors/benedictchen)

**👑 Prolog Royalty ($100/month)** - *"Become part of my background knowledge for life success!"*  
❤️ [Subscribe on GitHub](https://github.com/sponsors/benedictchen)

<div align="center">

**One-time donation?**  
**[💳 DONATE VIA PAYPAL](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)**

**Ongoing support?**  
**[❤️ SPONSOR ON GITHUB](https://github.com/sponsors/benedictchen)**

**Can't decide?**  
**Why not both?** 🤷‍♂️

</div>

**Every contribution helps me learn the rule: successful_research(benedict) :- funding(adequate), coffee(unlimited), community(supportive). 🚀**

*P.S. - If you help me learn that house rule, I'll name a FOIL refinement operator after you! foil_refinement_operator_[your_name](Rule, ImprovedRule) :- ...*

---

<div align="center">

## 🌟 What the Community is Saying

</div>

---

> **@LogicLordTech** (623K followers) • *6 hours ago* • *(parody)*
> 
> *"YO this ILP library just made me understand how AI learns rules from examples and I'm actually having an existential crisis! 🤯 It's like when you finally figure out the pattern in your Wordle guesses but make it SCIENTIFIC! FOIL and Progol are literally the algorithms that taught computers logical thinking - they're giving 'I can deduce the rules of reality' energy fr. Been using this to understand why my mom always knows when I'm lying and turns out there's actual mathematical principles behind pattern recognition in human behavior no cap! 🧠✨"*
> 
> **94.7K ❤️ • 18.2K 🔄 • 5.1K 🤔**