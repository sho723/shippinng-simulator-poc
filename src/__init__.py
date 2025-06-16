## src/__init__.py
```python
"""
Shipping Simulator Package
"""
from .ship_management import ShipManager
from .port_management import PortManager
from .simulator_engine import ShippingSimulator, Ship, Port, Berth
from .utils import generate_sample_data, validate_data

__all__ = [
    'ShipManager',
    'PortManager', 
    'ShippingSimulator',
    'Ship',
    'Port',
    'Berth',
    'generate_sample_data',
    'validate_data'
]
