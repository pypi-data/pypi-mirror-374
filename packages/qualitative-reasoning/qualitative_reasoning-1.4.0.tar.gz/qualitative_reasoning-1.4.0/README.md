# Qualitative Reasoning

A comprehensive Python library for qualitative reasoning systems based on Forbus's Process Theory and de Kleer's Qualitative Physics framework.

This package enables AI systems to reason about physical systems using qualitative relationships rather than precise numerical values, similar to how humans understand physics intuitively.

## Features

- **Modular Architecture**: Clean separation of concerns with specialized components
- **Security-First Design**: Constraint evaluation without eval() vulnerabilities
- **Rich Visualization**: Comprehensive analysis and visualization capabilities
- **Factory Functions**: Pre-configured reasoners for common use cases
- **Backward Compatibility**: Full compatibility with original implementation

## Core Components

- **QualitativeReasoner**: Main reasoning engine
- **QualitativeValue/Direction/Quantity**: Core qualitative types
- **QualitativeState/Process**: System state and process modeling
- **Constraint Evaluation**: Security-focused constraint system
- **Visualization**: Rich reporting and analysis tools

## Installation

```bash
pip install qualitative-reasoning
```

## Basic Usage

```python
from qualitative_reasoning import QualitativeReasoner

# Create a reasoner
reasoner = QualitativeReasoner()

# Add quantities and processes
reasoner.add_quantity("temperature", "increasing")
reasoner.add_process("heating", {"temperature": "increasing"})

# Run simulation
reasoner.simulate_step()
```

## Research Foundation

Based on foundational work in qualitative physics:
- Forbus's Process Theory
- de Kleer's Qualitative Physics framework

## Author

**Benedict Chen** (benedict@benedictchen.com)

- Support: [PayPal](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)
- Sponsor: [GitHub Sponsors](https://github.com/sponsors/benedictchen)

## License

Custom Non-Commercial License with Donation Requirements