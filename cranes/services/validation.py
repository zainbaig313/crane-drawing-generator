"""
Centralized validation configuration and logic for crane design parameters.
Distinguishes software validation boundaries from certified engineering design.
"""
from decimal import Decimal, InvalidOperation
from typing import Dict, Any, Tuple

# Centralized software validation ranges
# These are prototype software bounds for parametric generation, NOT industry-certified limits.
CRANE_VALIDATION_CONFIG: Dict[str, Dict[str, Any]] = {
    'capacity': {
        'min': Decimal('0.01'),
        'max': Decimal('20.0'),
        'unit': 'Tonnes',
        'label': 'Crane capacity',
        'help': 'Safe Working Load (SWL) in metric tonnes (0 < capacity <= 20 t).'
    },
    'span': {
        'min': 5000,
        'max': 25000,
        'unit': 'mm',
        'label': 'Crane span',
        'help': 'Center-to-center distance between runway rails (5,000 to 25,000 mm).'
    },
    'lifting_height': {
        'min': 100,
        'max': 15000,
        'unit': 'mm',
        'label': 'Lifting height',
        'help': 'Maximum vertical hook travel distance (100 to 15,000 mm).'
    },
    'girder_depth': {
        'min': 100,
        'max': 2500,
        'unit': 'mm',
        'label': 'Main girder depth',
        'help': 'Overall vertical depth of the main girder beam (100 to 2,500 mm).'
    },
    'end_carriage_height': {
        'min': 100,
        'max': 1500,
        'unit': 'mm',
        'label': 'End carriage height',
        'help': 'Vertical height of the end trucks/carriages (100 to 1,500 mm).'
    },
    'trolley_width': {
        'min': 100,
        'max': 3000,
        'unit': 'mm',
        'label': 'Hoist/trolley width',
        'help': 'Overall horizontal width of the hoist/trolley assembly (100 to 3,000 mm).'
    },
    'hook_block_height': {
        'min': 100,
        'max': 2000,
        'unit': 'mm',
        'label': 'Hook block height',
        'help': 'Vertical height of hook block from saddle to top sheave (100 to 2,000 mm).'
    },
    'runway_rail_height': {
        'min': 10,
        'max': 300,
        'unit': 'mm',
        'label': 'Runway rail height',
        'help': 'Vertical height of the runway crane rails (10 to 300 mm).'
    },
}

REQUIRED_PARAMETERS = [
    'capacity',
    'span',
    'lifting_height',
    'girder_depth',
    'end_carriage_height',
    'trolley_width',
    'hook_block_height',
    'runway_rail_height',
]


def clean_and_validate_parameter(field_name: str, raw_value: Any) -> Tuple[Any, str | None]:
    """
    Validates a single parameter against its configured range and numeric type.
    Returns (cleaned_value, error_message).
    """
    if raw_value is None or (isinstance(raw_value, str) and raw_value.strip() == ''):
        return None, f"{CRANE_VALIDATION_CONFIG[field_name]['label']} is required."

    cfg = CRANE_VALIDATION_CONFIG[field_name]
    label = cfg['label']
    unit = cfg['unit']

    if field_name == 'capacity':
        try:
            val = Decimal(str(raw_value).strip())
        except (InvalidOperation, ValueError, TypeError):
            return None, f"{label} must be a valid number."
        
        if val <= Decimal('0'):
            return None, f"{label} must be greater than 0 {unit}."
        if val > cfg['max']:
            return None, f"{label} cannot exceed {cfg['max']} {unit}."
        if val < cfg['min']:
            return None, f"{label} must be at least {cfg['min']} {unit}."
        return val, None

    # mm dimension parameters
    try:
        # Accept float or string representation of integer/float
        val_float = float(raw_value)
        if not val_float.is_integer() and isinstance(raw_value, str) and '.' in raw_value:
            # Check if fractional mm is provided
            val_int = int(round(val_float))
        else:
            val_int = int(val_float)
    except (ValueError, TypeError):
        return None, f"{label} must be a valid integer in {unit}."

    if val_int <= 0:
        return None, f"{label} must be a positive dimension greater than 0 {unit}."

    if val_int < cfg['min']:
        return None, f"{label} cannot be less than {cfg['min']:,} {unit}."
    if val_int > cfg['max']:
        return None, f"{label} cannot exceed {cfg['max']:,} {unit}."

    return val_int, None


def validate_crane_parameters(data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, list[str]]]:
    """
    Validates all 8 primary crane parameters, including cross-field layout constraints.
    Returns:
        (cleaned_data, errors_dict)
    """
    cleaned: Dict[str, Any] = {}
    errors: Dict[str, list[str]] = {}

    # 1. Field-level validation
    for field in REQUIRED_PARAMETERS:
        raw = data.get(field)
        val, err = clean_and_validate_parameter(field, raw)
        if err:
            errors.setdefault(field, []).append(err)
        else:
            cleaned[field] = val

    # If any single field failed, return early to avoid invalid cross-field arithmetic
    if errors:
        return cleaned, errors

    # 2. Cross-field consistency and layout compatibility checks
    span = cleaned['span']
    trolley_width = cleaned['trolley_width']
    lifting_height = cleaned['lifting_height']
    hook_block_height = cleaned['hook_block_height']
    girder_depth = cleaned['girder_depth']
    end_carriage_height = cleaned['end_carriage_height']

    # Cross-check 1: Trolley width vs. Crane span
    # The trolley must physically fit on the girder between the end carriages.
    # Estimated minimum end carriage clearance is 600 mm on each side.
    if trolley_width >= span:
        errors.setdefault('trolley_width', []).append(
            f"Trolley width ({trolley_width:,} mm) cannot be equal to or greater than crane span ({span:,} mm)."
        )
    elif trolley_width > (span - 1000):
        errors.setdefault('trolley_width', []).append(
            f"Trolley width ({trolley_width:,} mm) exceeds allowable travel clearance for span ({span:,} mm). Minimum 1,000 mm clearance required."
        )

    # Cross-check 2: Hook block height vs. Lifting height
    # The hook block assembly itself cannot exceed the total vertical lifting height.
    if hook_block_height >= lifting_height:
        errors.setdefault('hook_block_height', []).append(
            f"Hook block height ({hook_block_height:,} mm) must be less than total lifting height ({lifting_height:,} mm)."
        )

    # Cross-check 3: End carriage height vs. Girder depth
    # Extremely mismatched girder depth and end carriage produce impossible physical joints.
    if end_carriage_height > (girder_depth * 3):
        errors.setdefault('end_carriage_height', []).append(
            f"End carriage height ({end_carriage_height:,} mm) is disproportionately large compared to main girder depth ({girder_depth:,} mm)."
        )

    return cleaned, errors
