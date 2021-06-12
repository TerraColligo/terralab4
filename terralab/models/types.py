# -*- coding: utf-8 -*-
# Python typings for TerraLab models
from typing import Any, Dict, List, Union
try:
    from typing import TypedDict # type: ignore
except:
    from typing_extensions import TypedDict

# Odoo Actions returned by model action methods
OdooActionResponse = Any

# Odoo model base
OdooModel = Any
