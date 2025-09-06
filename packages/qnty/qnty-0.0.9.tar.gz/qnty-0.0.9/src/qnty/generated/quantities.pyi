"""
Type stubs for quantities module - Complete Edition.

Provides complete type hints for IDE autocomplete and type checking
for quantity classes and their setter relationships.
Contains 107 quantity types with 871 total units.

Auto-generated from unit_data.json.
"""

from typing import Any

from ..quantities.typed_quantity import TypedQuantity
from . import dimensions as dim
from . import setters as ts

# ===== QUANTITY CLASSES =====
# Type stubs for quantity classes with setter relationships

class AbsorbedDose(TypedQuantity):
    """
    Type-safe absorbed radiation dose quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - AbsorbedDose("variable_name") -> Create unknown absorbed radiation dose
    - AbsorbedDose(value, "unit", "variable_name") -> Create known absorbed radiation dose
    
    Examples:
    ---------
    >>> unknown = AbsorbedDose("pressure")  # Unknown absorbed radiation dose
    >>> known = AbsorbedDose(100, "erg_per_gram", "inlet_pressure")  # Known absorbed radiation dose
    
    Available units: "erg_per_gram", "gram_rad", "gray"
    """
    __slots__ = ()
    _setter_class = ts.AbsorbedDoseSetter
    _expected_dimension = dim.ABSORBED_DOSE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.AbsorbedDoseSetter:
        """
        Create a setter for this absorbed radiation dose quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            AbsorbedDoseSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class Acceleration(TypedQuantity):
    """
    Type-safe acceleration quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Acceleration("variable_name") -> Create unknown acceleration
    - Acceleration(value, "unit", "variable_name") -> Create known acceleration
    
    Examples:
    ---------
    >>> unknown = Acceleration("pressure")  # Unknown acceleration
    >>> known = Acceleration(100, "meter_per_second_squared", "inlet_pressure")  # Known acceleration
    
    Available units: "meter_per_second_squared", "foot_per_second_squared"
    """
    __slots__ = ()
    _setter_class = ts.AccelerationSetter
    _expected_dimension = dim.ACCELERATION
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.AccelerationSetter:
        """
        Create a setter for this acceleration quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            AccelerationSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class ActivationEnergy(TypedQuantity):
    """
    Type-safe activation energy quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ActivationEnergy("variable_name") -> Create unknown activation energy
    - ActivationEnergy(value, "unit", "variable_name") -> Create known activation energy
    
    Examples:
    ---------
    >>> unknown = ActivationEnergy("pressure")  # Unknown activation energy
    >>> known = ActivationEnergy(100, "btu_per_pound_mole", "inlet_pressure")  # Known activation energy
    
    Available units: "btu_per_pound_mole", "calorie_mean_per_gram_mole", "joule_per_gram_mole"
    """
    __slots__ = ()
    _setter_class = ts.ActivationEnergySetter
    _expected_dimension = dim.ACTIVATION_ENERGY
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.ActivationEnergySetter:
        """
        Create a setter for this activation energy quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            ActivationEnergySetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class AmountOfSubstance(TypedQuantity):
    """
    Type-safe amount of substance quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - AmountOfSubstance("variable_name") -> Create unknown amount of substance
    - AmountOfSubstance(value, "unit", "variable_name") -> Create known amount of substance
    
    Examples:
    ---------
    >>> unknown = AmountOfSubstance("pressure")  # Unknown amount of substance
    >>> known = AmountOfSubstance(100, "kilogram_mol", "inlet_pressure")  # Known amount of substance
    
    Available units: "kilogram_mol", "mole", "pound_mole"
    """
    __slots__ = ()
    _setter_class = ts.AmountOfSubstanceSetter
    _expected_dimension = dim.AMOUNT_OF_SUBSTANCE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.AmountOfSubstanceSetter:
        """
        Create a setter for this amount of substance quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            AmountOfSubstanceSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class AnglePlane(TypedQuantity):
    """
    Type-safe angle, plane quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - AnglePlane("variable_name") -> Create unknown angle, plane
    - AnglePlane(value, "unit", "variable_name") -> Create known angle, plane
    
    Examples:
    ---------
    >>> unknown = AnglePlane("pressure")  # Unknown angle, plane
    >>> known = AnglePlane(100, "degree", "inlet_pressure")  # Known angle, plane
    
    Available units: "degree", "gon", "grade"
    """
    __slots__ = ()
    _setter_class = ts.AnglePlaneSetter
    _expected_dimension = dim.ANGLE_PLANE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.AnglePlaneSetter:
        """
        Create a setter for this angle, plane quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            AnglePlaneSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class AngleSolid(TypedQuantity):
    """
    Type-safe angle, solid quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - AngleSolid("variable_name") -> Create unknown angle, solid
    - AngleSolid(value, "unit", "variable_name") -> Create known angle, solid
    
    Examples:
    ---------
    >>> unknown = AngleSolid("pressure")  # Unknown angle, solid
    >>> known = AngleSolid(100, "spat", "inlet_pressure")  # Known angle, solid
    
    Available units: "spat", "square_degree", "square_gon"
    """
    __slots__ = ()
    _setter_class = ts.AngleSolidSetter
    _expected_dimension = dim.ANGLE_SOLID
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.AngleSolidSetter:
        """
        Create a setter for this angle, solid quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            AngleSolidSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class AngularAcceleration(TypedQuantity):
    """
    Type-safe angular acceleration quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - AngularAcceleration("variable_name") -> Create unknown angular acceleration
    - AngularAcceleration(value, "unit", "variable_name") -> Create known angular acceleration
    
    Examples:
    ---------
    >>> unknown = AngularAcceleration("pressure")  # Unknown angular acceleration
    >>> known = AngularAcceleration(100, "radian_per_second_squared", "inlet_pressure")  # Known angular acceleration
    
    Available units: "radian_per_second_squared", "revolution_per_second_squared", "rpm_or_revolution_per_minute"
    """
    __slots__ = ()
    _setter_class = ts.AngularAccelerationSetter
    _expected_dimension = dim.ANGULAR_ACCELERATION
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.AngularAccelerationSetter:
        """
        Create a setter for this angular acceleration quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            AngularAccelerationSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class AngularMomentum(TypedQuantity):
    """
    Type-safe angular momentum quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - AngularMomentum("variable_name") -> Create unknown angular momentum
    - AngularMomentum(value, "unit", "variable_name") -> Create known angular momentum
    
    Examples:
    ---------
    >>> unknown = AngularMomentum("pressure")  # Unknown angular momentum
    >>> known = AngularMomentum(100, "gram_centimeter_squared_per_second", "inlet_pressure")  # Known angular momentum
    
    Available units: "gram_centimeter_squared_per_second", "kilogram_meter_squared_per_second", "pound_force_square_foot_per_second"
    """
    __slots__ = ()
    _setter_class = ts.AngularMomentumSetter
    _expected_dimension = dim.ANGULAR_MOMENTUM
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.AngularMomentumSetter:
        """
        Create a setter for this angular momentum quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            AngularMomentumSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class Area(TypedQuantity):
    """
    Type-safe area quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Area("variable_name") -> Create unknown area
    - Area(value, "unit", "variable_name") -> Create known area
    
    Examples:
    ---------
    >>> unknown = Area("pressure")  # Unknown area
    >>> known = Area(100, "acre_general", "inlet_pressure")  # Known area
    
    Available units: "acre_general", "are", "arpent_quebec"
    """
    __slots__ = ()
    _setter_class = ts.AreaSetter
    _expected_dimension = dim.AREA
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.AreaSetter:
        """
        Create a setter for this area quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            AreaSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class AreaPerUnitVolume(TypedQuantity):
    """
    Type-safe area per unit volume quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - AreaPerUnitVolume("variable_name") -> Create unknown area per unit volume
    - AreaPerUnitVolume(value, "unit", "variable_name") -> Create known area per unit volume
    
    Examples:
    ---------
    >>> unknown = AreaPerUnitVolume("pressure")  # Unknown area per unit volume
    >>> known = AreaPerUnitVolume(100, "square_centimeter_per_cubic_centimeter", "inlet_pressure")  # Known area per unit volume
    
    Available units: "square_centimeter_per_cubic_centimeter", "square_foot_per_cubic_foot", "square_inch_per_cubic_inch"
    """
    __slots__ = ()
    _setter_class = ts.AreaPerUnitVolumeSetter
    _expected_dimension = dim.AREA_PER_UNIT_VOLUME
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.AreaPerUnitVolumeSetter:
        """
        Create a setter for this area per unit volume quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            AreaPerUnitVolumeSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class AtomicWeight(TypedQuantity):
    """
    Type-safe atomic weight quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - AtomicWeight("variable_name") -> Create unknown atomic weight
    - AtomicWeight(value, "unit", "variable_name") -> Create known atomic weight
    
    Examples:
    ---------
    >>> unknown = AtomicWeight("pressure")  # Unknown atomic weight
    >>> known = AtomicWeight(100, "atomic_mass_unit_12c", "inlet_pressure")  # Known atomic weight
    
    Available units: "atomic_mass_unit_12c", "grams_per_mole", "kilograms_per_kilomole"
    """
    __slots__ = ()
    _setter_class = ts.AtomicWeightSetter
    _expected_dimension = dim.ATOMIC_WEIGHT
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.AtomicWeightSetter:
        """
        Create a setter for this atomic weight quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            AtomicWeightSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class Concentration(TypedQuantity):
    """
    Type-safe concentration quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Concentration("variable_name") -> Create unknown concentration
    - Concentration(value, "unit", "variable_name") -> Create known concentration
    
    Examples:
    ---------
    >>> unknown = Concentration("pressure")  # Unknown concentration
    >>> known = Concentration(100, "grains_of_i_per_cubic_foot", "inlet_pressure")  # Known concentration
    
    Available units: "grains_of_i_per_cubic_foot", "grains_of_i_per_gallon_us"
    """
    __slots__ = ()
    _setter_class = ts.ConcentrationSetter
    _expected_dimension = dim.CONCENTRATION
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.ConcentrationSetter:
        """
        Create a setter for this concentration quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            ConcentrationSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class Dimensionless(TypedQuantity):
    """
    Type-safe dimensionless quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Dimensionless("variable_name") -> Create unknown dimensionless
    - Dimensionless(value, "variable_name") -> Create known dimensionless
    
    Examples:
    ---------
    >>> unknown = Dimensionless("efficiency")  # Unknown dimensionless
    >>> known = Dimensionless(0.85, "thermal_efficiency")  # Known dimensionless
    """
    __slots__ = ()
    _setter_class = ts.DimensionlessSetter
    _expected_dimension = dim.DIMENSIONLESS
    
    def __init__(self, name_or_value: str | int | float, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.DimensionlessSetter:
        """
        Create a setter for this dimensionless quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            DimensionlessSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class DynamicFluidity(TypedQuantity):
    """
    Type-safe dynamic fluidity quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - DynamicFluidity("variable_name") -> Create unknown dynamic fluidity
    - DynamicFluidity(value, "unit", "variable_name") -> Create known dynamic fluidity
    
    Examples:
    ---------
    >>> unknown = DynamicFluidity("pressure")  # Unknown dynamic fluidity
    >>> known = DynamicFluidity(100, "meter_seconds_per_kilogram", "inlet_pressure")  # Known dynamic fluidity
    
    Available units: "meter_seconds_per_kilogram", "rhe", "square_foot_per_pound_second"
    """
    __slots__ = ()
    _setter_class = ts.DynamicFluiditySetter
    _expected_dimension = dim.DYNAMIC_FLUIDITY
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.DynamicFluiditySetter:
        """
        Create a setter for this dynamic fluidity quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            DynamicFluiditySetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class ElectricCapacitance(TypedQuantity):
    """
    Type-safe electric capacitance quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ElectricCapacitance("variable_name") -> Create unknown electric capacitance
    - ElectricCapacitance(value, "unit", "variable_name") -> Create known electric capacitance
    
    Examples:
    ---------
    >>> unknown = ElectricCapacitance("pressure")  # Unknown electric capacitance
    >>> known = ElectricCapacitance(100, "cm", "inlet_pressure")  # Known electric capacitance
    
    Available units: "cm", "abfarad", "farad"
    """
    __slots__ = ()
    _setter_class = ts.ElectricCapacitanceSetter
    _expected_dimension = dim.ELECTRIC_CAPACITANCE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.ElectricCapacitanceSetter:
        """
        Create a setter for this electric capacitance quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            ElectricCapacitanceSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class ElectricCharge(TypedQuantity):
    """
    Type-safe electric charge quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ElectricCharge("variable_name") -> Create unknown electric charge
    - ElectricCharge(value, "unit", "variable_name") -> Create known electric charge
    
    Examples:
    ---------
    >>> unknown = ElectricCharge("pressure")  # Unknown electric charge
    >>> known = ElectricCharge(100, "abcoulomb", "inlet_pressure")  # Known electric charge
    
    Available units: "abcoulomb", "ampere_hour", "coulomb"
    """
    __slots__ = ()
    _setter_class = ts.ElectricChargeSetter
    _expected_dimension = dim.ELECTRIC_CHARGE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.ElectricChargeSetter:
        """
        Create a setter for this electric charge quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            ElectricChargeSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class ElectricCurrentIntensity(TypedQuantity):
    """
    Type-safe electric current intensity quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ElectricCurrentIntensity("variable_name") -> Create unknown electric current intensity
    - ElectricCurrentIntensity(value, "unit", "variable_name") -> Create known electric current intensity
    
    Examples:
    ---------
    >>> unknown = ElectricCurrentIntensity("pressure")  # Unknown electric current intensity
    >>> known = ElectricCurrentIntensity(100, "abampere", "inlet_pressure")  # Known electric current intensity
    
    Available units: "abampere", "ampere_intl_mean", "ampere_intl_us"
    """
    __slots__ = ()
    _setter_class = ts.ElectricCurrentIntensitySetter
    _expected_dimension = dim.ELECTRIC_CURRENT_INTENSITY
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.ElectricCurrentIntensitySetter:
        """
        Create a setter for this electric current intensity quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            ElectricCurrentIntensitySetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class ElectricDipoleMoment(TypedQuantity):
    """
    Type-safe electric dipole moment quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ElectricDipoleMoment("variable_name") -> Create unknown electric dipole moment
    - ElectricDipoleMoment(value, "unit", "variable_name") -> Create known electric dipole moment
    
    Examples:
    ---------
    >>> unknown = ElectricDipoleMoment("pressure")  # Unknown electric dipole moment
    >>> known = ElectricDipoleMoment(100, "ampere_meter_second", "inlet_pressure")  # Known electric dipole moment
    
    Available units: "ampere_meter_second", "coulomb_meter", "debye"
    """
    __slots__ = ()
    _setter_class = ts.ElectricDipoleMomentSetter
    _expected_dimension = dim.ELECTRIC_DIPOLE_MOMENT
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.ElectricDipoleMomentSetter:
        """
        Create a setter for this electric dipole moment quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            ElectricDipoleMomentSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class ElectricFieldStrength(TypedQuantity):
    """
    Type-safe electric field strength quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ElectricFieldStrength("variable_name") -> Create unknown electric field strength
    - ElectricFieldStrength(value, "unit", "variable_name") -> Create known electric field strength
    
    Examples:
    ---------
    >>> unknown = ElectricFieldStrength("pressure")  # Unknown electric field strength
    >>> known = ElectricFieldStrength(100, "volt_per_centimeter", "inlet_pressure")  # Known electric field strength
    
    Available units: "volt_per_centimeter", "volt_per_meter"
    """
    __slots__ = ()
    _setter_class = ts.ElectricFieldStrengthSetter
    _expected_dimension = dim.ELECTRIC_FIELD_STRENGTH
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.ElectricFieldStrengthSetter:
        """
        Create a setter for this electric field strength quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            ElectricFieldStrengthSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class ElectricInductance(TypedQuantity):
    """
    Type-safe electric inductance quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ElectricInductance("variable_name") -> Create unknown electric inductance
    - ElectricInductance(value, "unit", "variable_name") -> Create known electric inductance
    
    Examples:
    ---------
    >>> unknown = ElectricInductance("pressure")  # Unknown electric inductance
    >>> known = ElectricInductance(100, "abhenry", "inlet_pressure")  # Known electric inductance
    
    Available units: "abhenry", "cm", "henry"
    """
    __slots__ = ()
    _setter_class = ts.ElectricInductanceSetter
    _expected_dimension = dim.ELECTRIC_INDUCTANCE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.ElectricInductanceSetter:
        """
        Create a setter for this electric inductance quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            ElectricInductanceSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class ElectricPotential(TypedQuantity):
    """
    Type-safe electric potential quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ElectricPotential("variable_name") -> Create unknown electric potential
    - ElectricPotential(value, "unit", "variable_name") -> Create known electric potential
    
    Examples:
    ---------
    >>> unknown = ElectricPotential("pressure")  # Unknown electric potential
    >>> known = ElectricPotential(100, "abvolt", "inlet_pressure")  # Known electric potential
    
    Available units: "abvolt", "statvolt", "u_a_potential"
    """
    __slots__ = ()
    _setter_class = ts.ElectricPotentialSetter
    _expected_dimension = dim.ELECTRIC_POTENTIAL
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.ElectricPotentialSetter:
        """
        Create a setter for this electric potential quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            ElectricPotentialSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class ElectricResistance(TypedQuantity):
    """
    Type-safe electric resistance quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ElectricResistance("variable_name") -> Create unknown electric resistance
    - ElectricResistance(value, "unit", "variable_name") -> Create known electric resistance
    
    Examples:
    ---------
    >>> unknown = ElectricResistance("pressure")  # Unknown electric resistance
    >>> known = ElectricResistance(100, "abohm", "inlet_pressure")  # Known electric resistance
    
    Available units: "abohm", "jacobi", "lenz"
    """
    __slots__ = ()
    _setter_class = ts.ElectricResistanceSetter
    _expected_dimension = dim.ELECTRIC_RESISTANCE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.ElectricResistanceSetter:
        """
        Create a setter for this electric resistance quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            ElectricResistanceSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class ElectricalConductance(TypedQuantity):
    """
    Type-safe electrical conductance quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ElectricalConductance("variable_name") -> Create unknown electrical conductance
    - ElectricalConductance(value, "unit", "variable_name") -> Create known electrical conductance
    
    Examples:
    ---------
    >>> unknown = ElectricalConductance("pressure")  # Unknown electrical conductance
    >>> known = ElectricalConductance(100, "emu_cgs", "inlet_pressure")  # Known electrical conductance
    
    Available units: "emu_cgs", "esu_cgs", "mho"
    """
    __slots__ = ()
    _setter_class = ts.ElectricalConductanceSetter
    _expected_dimension = dim.ELECTRICAL_CONDUCTANCE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.ElectricalConductanceSetter:
        """
        Create a setter for this electrical conductance quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            ElectricalConductanceSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class ElectricalPermittivity(TypedQuantity):
    """
    Type-safe electrical permittivity quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ElectricalPermittivity("variable_name") -> Create unknown electrical permittivity
    - ElectricalPermittivity(value, "unit", "variable_name") -> Create known electrical permittivity
    
    Examples:
    ---------
    >>> unknown = ElectricalPermittivity("pressure")  # Unknown electrical permittivity
    >>> known = ElectricalPermittivity(100, "farad_per_meter", "inlet_pressure")  # Known electrical permittivity
    
    Available units: "farad_per_meter"
    """
    __slots__ = ()
    _setter_class = ts.ElectricalPermittivitySetter
    _expected_dimension = dim.ELECTRICAL_PERMITTIVITY
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.ElectricalPermittivitySetter:
        """
        Create a setter for this electrical permittivity quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            ElectricalPermittivitySetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class ElectricalResistivity(TypedQuantity):
    """
    Type-safe electrical resistivity quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ElectricalResistivity("variable_name") -> Create unknown electrical resistivity
    - ElectricalResistivity(value, "unit", "variable_name") -> Create known electrical resistivity
    
    Examples:
    ---------
    >>> unknown = ElectricalResistivity("pressure")  # Unknown electrical resistivity
    >>> known = ElectricalResistivity(100, "circular_mil_ohm_per_foot", "inlet_pressure")  # Known electrical resistivity
    
    Available units: "circular_mil_ohm_per_foot", "emu_cgs", "microhm_inch"
    """
    __slots__ = ()
    _setter_class = ts.ElectricalResistivitySetter
    _expected_dimension = dim.ELECTRICAL_RESISTIVITY
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.ElectricalResistivitySetter:
        """
        Create a setter for this electrical resistivity quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            ElectricalResistivitySetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class EnergyFlux(TypedQuantity):
    """
    Type-safe energy flux quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - EnergyFlux("variable_name") -> Create unknown energy flux
    - EnergyFlux(value, "unit", "variable_name") -> Create known energy flux
    
    Examples:
    ---------
    >>> unknown = EnergyFlux("pressure")  # Unknown energy flux
    >>> known = EnergyFlux(100, "btu_per_square_foot_per_hour", "inlet_pressure")  # Known energy flux
    
    Available units: "btu_per_square_foot_per_hour", "calorie_per_square_centimeter_per_second", "celsius_heat_units_chu"
    """
    __slots__ = ()
    _setter_class = ts.EnergyFluxSetter
    _expected_dimension = dim.ENERGY_FLUX
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.EnergyFluxSetter:
        """
        Create a setter for this energy flux quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            EnergyFluxSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class EnergyHeatWork(TypedQuantity):
    """
    Type-safe energy, heat, work quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - EnergyHeatWork("variable_name") -> Create unknown energy, heat, work
    - EnergyHeatWork(value, "unit", "variable_name") -> Create known energy, heat, work
    
    Examples:
    ---------
    >>> unknown = EnergyHeatWork("pressure")  # Unknown energy, heat, work
    >>> known = EnergyHeatWork(100, "barrel_oil_equivalent_or_equivalent_barrel", "inlet_pressure")  # Known energy, heat, work
    
    Available units: "barrel_oil_equivalent_or_equivalent_barrel", "billion_electronvolt", "british_thermal_unit_4circ_mathrmc"
    """
    __slots__ = ()
    _setter_class = ts.EnergyHeatWorkSetter
    _expected_dimension = dim.ENERGY_HEAT_WORK
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.EnergyHeatWorkSetter:
        """
        Create a setter for this energy, heat, work quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            EnergyHeatWorkSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class EnergyPerUnitArea(TypedQuantity):
    """
    Type-safe energy per unit area quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - EnergyPerUnitArea("variable_name") -> Create unknown energy per unit area
    - EnergyPerUnitArea(value, "unit", "variable_name") -> Create known energy per unit area
    
    Examples:
    ---------
    >>> unknown = EnergyPerUnitArea("pressure")  # Unknown energy per unit area
    >>> known = EnergyPerUnitArea(100, "british_thermal_unit_per_square_foot", "inlet_pressure")  # Known energy per unit area
    
    Available units: "british_thermal_unit_per_square_foot", "joule_per_square_meter", "langley"
    """
    __slots__ = ()
    _setter_class = ts.EnergyPerUnitAreaSetter
    _expected_dimension = dim.ENERGY_PER_UNIT_AREA
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.EnergyPerUnitAreaSetter:
        """
        Create a setter for this energy per unit area quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            EnergyPerUnitAreaSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class Force(TypedQuantity):
    """
    Type-safe force quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Force("variable_name") -> Create unknown force
    - Force(value, "unit", "variable_name") -> Create known force
    
    Examples:
    ---------
    >>> unknown = Force("pressure")  # Unknown force
    >>> known = Force(100, "crinal", "inlet_pressure")  # Known force
    
    Available units: "crinal", "dyne", "funal"
    """
    __slots__ = ()
    _setter_class = ts.ForceSetter
    _expected_dimension = dim.FORCE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.ForceSetter:
        """
        Create a setter for this force quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            ForceSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class ForceBody(TypedQuantity):
    """
    Type-safe force (body) quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ForceBody("variable_name") -> Create unknown force (body)
    - ForceBody(value, "unit", "variable_name") -> Create known force (body)
    
    Examples:
    ---------
    >>> unknown = ForceBody("pressure")  # Unknown force (body)
    >>> known = ForceBody(100, "dyne_per_cubic_centimeter", "inlet_pressure")  # Known force (body)
    
    Available units: "dyne_per_cubic_centimeter", "kilogram_force_per_cubic_centimeter", "kilogram_force_per_cubic_meter"
    """
    __slots__ = ()
    _setter_class = ts.ForceBodySetter
    _expected_dimension = dim.FORCE_BODY
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.ForceBodySetter:
        """
        Create a setter for this force (body) quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            ForceBodySetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class ForcePerUnitMass(TypedQuantity):
    """
    Type-safe force per unit mass quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ForcePerUnitMass("variable_name") -> Create unknown force per unit mass
    - ForcePerUnitMass(value, "unit", "variable_name") -> Create known force per unit mass
    
    Examples:
    ---------
    >>> unknown = ForcePerUnitMass("pressure")  # Unknown force per unit mass
    >>> known = ForcePerUnitMass(100, "dyne_per_gram", "inlet_pressure")  # Known force per unit mass
    
    Available units: "dyne_per_gram", "kilogram_force_per_kilogram", "newton_per_kilogram"
    """
    __slots__ = ()
    _setter_class = ts.ForcePerUnitMassSetter
    _expected_dimension = dim.FORCE_PER_UNIT_MASS
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.ForcePerUnitMassSetter:
        """
        Create a setter for this force per unit mass quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            ForcePerUnitMassSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class FrequencyVoltageRatio(TypedQuantity):
    """
    Type-safe frequency voltage ratio quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - FrequencyVoltageRatio("variable_name") -> Create unknown frequency voltage ratio
    - FrequencyVoltageRatio(value, "unit", "variable_name") -> Create known frequency voltage ratio
    
    Examples:
    ---------
    >>> unknown = FrequencyVoltageRatio("pressure")  # Unknown frequency voltage ratio
    >>> known = FrequencyVoltageRatio(100, "cycles_per_second_per_volt", "inlet_pressure")  # Known frequency voltage ratio
    
    Available units: "cycles_per_second_per_volt", "hertz_per_volt", "terahertz_per_volt"
    """
    __slots__ = ()
    _setter_class = ts.FrequencyVoltageRatioSetter
    _expected_dimension = dim.FREQUENCY_VOLTAGE_RATIO
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.FrequencyVoltageRatioSetter:
        """
        Create a setter for this frequency voltage ratio quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            FrequencyVoltageRatioSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class FuelConsumption(TypedQuantity):
    """
    Type-safe fuel consumption quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - FuelConsumption("variable_name") -> Create unknown fuel consumption
    - FuelConsumption(value, "unit", "variable_name") -> Create known fuel consumption
    
    Examples:
    ---------
    >>> unknown = FuelConsumption("pressure")  # Unknown fuel consumption
    >>> known = FuelConsumption(100, "unit_100_km_per_liter", "inlet_pressure")  # Known fuel consumption
    
    Available units: "unit_100_km_per_liter", "gallons_uk", "gallons_us"
    """
    __slots__ = ()
    _setter_class = ts.FuelConsumptionSetter
    _expected_dimension = dim.FUEL_CONSUMPTION
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.FuelConsumptionSetter:
        """
        Create a setter for this fuel consumption quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            FuelConsumptionSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class HeatOfCombustion(TypedQuantity):
    """
    Type-safe heat of combustion quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - HeatOfCombustion("variable_name") -> Create unknown heat of combustion
    - HeatOfCombustion(value, "unit", "variable_name") -> Create known heat of combustion
    
    Examples:
    ---------
    >>> unknown = HeatOfCombustion("pressure")  # Unknown heat of combustion
    >>> known = HeatOfCombustion(100, "british_thermal_unit_per_pound", "inlet_pressure")  # Known heat of combustion
    
    Available units: "british_thermal_unit_per_pound", "calorie_per_gram", "chu_per_pound"
    """
    __slots__ = ()
    _setter_class = ts.HeatOfCombustionSetter
    _expected_dimension = dim.HEAT_OF_COMBUSTION
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.HeatOfCombustionSetter:
        """
        Create a setter for this heat of combustion quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            HeatOfCombustionSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class HeatOfFusion(TypedQuantity):
    """
    Type-safe heat of fusion quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - HeatOfFusion("variable_name") -> Create unknown heat of fusion
    - HeatOfFusion(value, "unit", "variable_name") -> Create known heat of fusion
    
    Examples:
    ---------
    >>> unknown = HeatOfFusion("pressure")  # Unknown heat of fusion
    >>> known = HeatOfFusion(100, "british_thermal_unit_mean", "inlet_pressure")  # Known heat of fusion
    
    Available units: "british_thermal_unit_mean", "british_thermal_unit_per_pound", "calorie_per_gram"
    """
    __slots__ = ()
    _setter_class = ts.HeatOfFusionSetter
    _expected_dimension = dim.HEAT_OF_FUSION
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.HeatOfFusionSetter:
        """
        Create a setter for this heat of fusion quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            HeatOfFusionSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class HeatOfVaporization(TypedQuantity):
    """
    Type-safe heat of vaporization quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - HeatOfVaporization("variable_name") -> Create unknown heat of vaporization
    - HeatOfVaporization(value, "unit", "variable_name") -> Create known heat of vaporization
    
    Examples:
    ---------
    >>> unknown = HeatOfVaporization("pressure")  # Unknown heat of vaporization
    >>> known = HeatOfVaporization(100, "british_thermal_unit_per_pound", "inlet_pressure")  # Known heat of vaporization
    
    Available units: "british_thermal_unit_per_pound", "calorie_per_gram", "chu_per_pound"
    """
    __slots__ = ()
    _setter_class = ts.HeatOfVaporizationSetter
    _expected_dimension = dim.HEAT_OF_VAPORIZATION
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.HeatOfVaporizationSetter:
        """
        Create a setter for this heat of vaporization quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            HeatOfVaporizationSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class HeatTransferCoefficient(TypedQuantity):
    """
    Type-safe heat transfer coefficient quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - HeatTransferCoefficient("variable_name") -> Create unknown heat transfer coefficient
    - HeatTransferCoefficient(value, "unit", "variable_name") -> Create known heat transfer coefficient
    
    Examples:
    ---------
    >>> unknown = HeatTransferCoefficient("pressure")  # Unknown heat transfer coefficient
    >>> known = HeatTransferCoefficient(100, "btu_per_square_foot_per_hour_per_degree_fahrenheit_or_rankine", "inlet_pressure")  # Known heat transfer coefficient
    
    Available units: "btu_per_square_foot_per_hour_per_degree_fahrenheit_or_rankine", "watt_per_square_meter_per_degree_celsius_or_kelvin"
    """
    __slots__ = ()
    _setter_class = ts.HeatTransferCoefficientSetter
    _expected_dimension = dim.HEAT_TRANSFER_COEFFICIENT
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.HeatTransferCoefficientSetter:
        """
        Create a setter for this heat transfer coefficient quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            HeatTransferCoefficientSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class Illuminance(TypedQuantity):
    """
    Type-safe illuminance quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Illuminance("variable_name") -> Create unknown illuminance
    - Illuminance(value, "unit", "variable_name") -> Create known illuminance
    
    Examples:
    ---------
    >>> unknown = Illuminance("pressure")  # Unknown illuminance
    >>> known = Illuminance(100, "foot_candle", "inlet_pressure")  # Known illuminance
    
    Available units: "foot_candle", "lux", "nox"
    """
    __slots__ = ()
    _setter_class = ts.IlluminanceSetter
    _expected_dimension = dim.ILLUMINANCE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.IlluminanceSetter:
        """
        Create a setter for this illuminance quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            IlluminanceSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class KineticEnergyOfTurbulence(TypedQuantity):
    """
    Type-safe kinetic energy of turbulence quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - KineticEnergyOfTurbulence("variable_name") -> Create unknown kinetic energy of turbulence
    - KineticEnergyOfTurbulence(value, "unit", "variable_name") -> Create known kinetic energy of turbulence
    
    Examples:
    ---------
    >>> unknown = KineticEnergyOfTurbulence("pressure")  # Unknown kinetic energy of turbulence
    >>> known = KineticEnergyOfTurbulence(100, "square_foot_per_second_squared", "inlet_pressure")  # Known kinetic energy of turbulence
    
    Available units: "square_foot_per_second_squared", "square_meters_per_second_squared"
    """
    __slots__ = ()
    _setter_class = ts.KineticEnergyOfTurbulenceSetter
    _expected_dimension = dim.KINETIC_ENERGY_OF_TURBULENCE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.KineticEnergyOfTurbulenceSetter:
        """
        Create a setter for this kinetic energy of turbulence quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            KineticEnergyOfTurbulenceSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class Length(TypedQuantity):
    """
    Type-safe length quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Length("variable_name") -> Create unknown length
    - Length(value, "unit", "variable_name") -> Create known length
    
    Examples:
    ---------
    >>> unknown = Length("pressure")  # Unknown length
    >>> known = Length(100, "ngstr_m", "inlet_pressure")  # Known length
    
    Available units: "ngstr_m", "arpent_quebec", "astronomic_unit"
    """
    __slots__ = ()
    _setter_class = ts.LengthSetter
    _expected_dimension = dim.LENGTH
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.LengthSetter:
        """
        Create a setter for this length quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            LengthSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class LinearMassDensity(TypedQuantity):
    """
    Type-safe linear mass density quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - LinearMassDensity("variable_name") -> Create unknown linear mass density
    - LinearMassDensity(value, "unit", "variable_name") -> Create known linear mass density
    
    Examples:
    ---------
    >>> unknown = LinearMassDensity("pressure")  # Unknown linear mass density
    >>> known = LinearMassDensity(100, "denier", "inlet_pressure")  # Known linear mass density
    
    Available units: "denier", "kilogram_per_centimeter", "kilogram_per_meter"
    """
    __slots__ = ()
    _setter_class = ts.LinearMassDensitySetter
    _expected_dimension = dim.LINEAR_MASS_DENSITY
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.LinearMassDensitySetter:
        """
        Create a setter for this linear mass density quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            LinearMassDensitySetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class LinearMomentum(TypedQuantity):
    """
    Type-safe linear momentum quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - LinearMomentum("variable_name") -> Create unknown linear momentum
    - LinearMomentum(value, "unit", "variable_name") -> Create known linear momentum
    
    Examples:
    ---------
    >>> unknown = LinearMomentum("pressure")  # Unknown linear momentum
    >>> known = LinearMomentum(100, "foot_pounds_force_per_hour", "inlet_pressure")  # Known linear momentum
    
    Available units: "foot_pounds_force_per_hour", "foot_pounds_force_per_minute", "foot_pounds_force_per_second"
    """
    __slots__ = ()
    _setter_class = ts.LinearMomentumSetter
    _expected_dimension = dim.LINEAR_MOMENTUM
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.LinearMomentumSetter:
        """
        Create a setter for this linear momentum quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            LinearMomentumSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class LuminanceSelf(TypedQuantity):
    """
    Type-safe luminance (self) quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - LuminanceSelf("variable_name") -> Create unknown luminance (self)
    - LuminanceSelf(value, "unit", "variable_name") -> Create known luminance (self)
    
    Examples:
    ---------
    >>> unknown = LuminanceSelf("pressure")  # Unknown luminance (self)
    >>> known = LuminanceSelf(100, "apostilb", "inlet_pressure")  # Known luminance (self)
    
    Available units: "apostilb", "blondel", "candela_per_square_meter"
    """
    __slots__ = ()
    _setter_class = ts.LuminanceSelfSetter
    _expected_dimension = dim.LUMINANCE_SELF
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.LuminanceSelfSetter:
        """
        Create a setter for this luminance (self) quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            LuminanceSelfSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class LuminousFlux(TypedQuantity):
    """
    Type-safe luminous flux quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - LuminousFlux("variable_name") -> Create unknown luminous flux
    - LuminousFlux(value, "unit", "variable_name") -> Create known luminous flux
    
    Examples:
    ---------
    >>> unknown = LuminousFlux("pressure")  # Unknown luminous flux
    >>> known = LuminousFlux(100, "candela_steradian", "inlet_pressure")  # Known luminous flux
    
    Available units: "candela_steradian", "lumen"
    """
    __slots__ = ()
    _setter_class = ts.LuminousFluxSetter
    _expected_dimension = dim.LUMINOUS_FLUX
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.LuminousFluxSetter:
        """
        Create a setter for this luminous flux quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            LuminousFluxSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class LuminousIntensity(TypedQuantity):
    """
    Type-safe luminous intensity quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - LuminousIntensity("variable_name") -> Create unknown luminous intensity
    - LuminousIntensity(value, "unit", "variable_name") -> Create known luminous intensity
    
    Examples:
    ---------
    >>> unknown = LuminousIntensity("pressure")  # Unknown luminous intensity
    >>> known = LuminousIntensity(100, "candela", "inlet_pressure")  # Known luminous intensity
    
    Available units: "candela", "candle_international", "carcel"
    """
    __slots__ = ()
    _setter_class = ts.LuminousIntensitySetter
    _expected_dimension = dim.LUMINOUS_INTENSITY
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.LuminousIntensitySetter:
        """
        Create a setter for this luminous intensity quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            LuminousIntensitySetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class MagneticField(TypedQuantity):
    """
    Type-safe magnetic field quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MagneticField("variable_name") -> Create unknown magnetic field
    - MagneticField(value, "unit", "variable_name") -> Create known magnetic field
    
    Examples:
    ---------
    >>> unknown = MagneticField("pressure")  # Unknown magnetic field
    >>> known = MagneticField(100, "ampere_per_meter", "inlet_pressure")  # Known magnetic field
    
    Available units: "ampere_per_meter", "lenz", "oersted"
    """
    __slots__ = ()
    _setter_class = ts.MagneticFieldSetter
    _expected_dimension = dim.MAGNETIC_FIELD
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.MagneticFieldSetter:
        """
        Create a setter for this magnetic field quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            MagneticFieldSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class MagneticFlux(TypedQuantity):
    """
    Type-safe magnetic flux quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MagneticFlux("variable_name") -> Create unknown magnetic flux
    - MagneticFlux(value, "unit", "variable_name") -> Create known magnetic flux
    
    Examples:
    ---------
    >>> unknown = MagneticFlux("pressure")  # Unknown magnetic flux
    >>> known = MagneticFlux(100, "kapp_line", "inlet_pressure")  # Known magnetic flux
    
    Available units: "kapp_line", "line", "maxwell"
    """
    __slots__ = ()
    _setter_class = ts.MagneticFluxSetter
    _expected_dimension = dim.MAGNETIC_FLUX
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.MagneticFluxSetter:
        """
        Create a setter for this magnetic flux quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            MagneticFluxSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class MagneticInductionFieldStrength(TypedQuantity):
    """
    Type-safe magnetic induction field strength quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MagneticInductionFieldStrength("variable_name") -> Create unknown magnetic induction field strength
    - MagneticInductionFieldStrength(value, "unit", "variable_name") -> Create known magnetic induction field strength
    
    Examples:
    ---------
    >>> unknown = MagneticInductionFieldStrength("pressure")  # Unknown magnetic induction field strength
    >>> known = MagneticInductionFieldStrength(100, "gamma", "inlet_pressure")  # Known magnetic induction field strength
    
    Available units: "gamma", "gauss", "line_per_square_centimeter"
    """
    __slots__ = ()
    _setter_class = ts.MagneticInductionFieldStrengthSetter
    _expected_dimension = dim.MAGNETIC_INDUCTION_FIELD_STRENGTH
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.MagneticInductionFieldStrengthSetter:
        """
        Create a setter for this magnetic induction field strength quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            MagneticInductionFieldStrengthSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class MagneticMoment(TypedQuantity):
    """
    Type-safe magnetic moment quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MagneticMoment("variable_name") -> Create unknown magnetic moment
    - MagneticMoment(value, "unit", "variable_name") -> Create known magnetic moment
    
    Examples:
    ---------
    >>> unknown = MagneticMoment("pressure")  # Unknown magnetic moment
    >>> known = MagneticMoment(100, "bohr_magneton", "inlet_pressure")  # Known magnetic moment
    
    Available units: "bohr_magneton", "joule_per_tesla", "nuclear_magneton"
    """
    __slots__ = ()
    _setter_class = ts.MagneticMomentSetter
    _expected_dimension = dim.MAGNETIC_MOMENT
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.MagneticMomentSetter:
        """
        Create a setter for this magnetic moment quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            MagneticMomentSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class MagneticPermeability(TypedQuantity):
    """
    Type-safe magnetic permeability quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MagneticPermeability("variable_name") -> Create unknown magnetic permeability
    - MagneticPermeability(value, "unit", "variable_name") -> Create known magnetic permeability
    
    Examples:
    ---------
    >>> unknown = MagneticPermeability("pressure")  # Unknown magnetic permeability
    >>> known = MagneticPermeability(100, "henrys_per_meter", "inlet_pressure")  # Known magnetic permeability
    
    Available units: "henrys_per_meter", "newton_per_square_ampere"
    """
    __slots__ = ()
    _setter_class = ts.MagneticPermeabilitySetter
    _expected_dimension = dim.MAGNETIC_PERMEABILITY
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.MagneticPermeabilitySetter:
        """
        Create a setter for this magnetic permeability quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            MagneticPermeabilitySetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class MagnetomotiveForce(TypedQuantity):
    """
    Type-safe magnetomotive force quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MagnetomotiveForce("variable_name") -> Create unknown magnetomotive force
    - MagnetomotiveForce(value, "unit", "variable_name") -> Create known magnetomotive force
    
    Examples:
    ---------
    >>> unknown = MagnetomotiveForce("pressure")  # Unknown magnetomotive force
    >>> known = MagnetomotiveForce(100, "abampere_turn", "inlet_pressure")  # Known magnetomotive force
    
    Available units: "abampere_turn", "ampere", "ampere_turn"
    """
    __slots__ = ()
    _setter_class = ts.MagnetomotiveForceSetter
    _expected_dimension = dim.MAGNETOMOTIVE_FORCE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.MagnetomotiveForceSetter:
        """
        Create a setter for this magnetomotive force quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            MagnetomotiveForceSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class Mass(TypedQuantity):
    """
    Type-safe mass quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Mass("variable_name") -> Create unknown mass
    - Mass(value, "unit", "variable_name") -> Create known mass
    
    Examples:
    ---------
    >>> unknown = Mass("pressure")  # Unknown mass
    >>> known = Mass(100, "slug", "inlet_pressure")  # Known mass
    
    Available units: "slug", "atomic_mass_unit_12_mathrmc", "carat_metric"
    """
    __slots__ = ()
    _setter_class = ts.MassSetter
    _expected_dimension = dim.MASS
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.MassSetter:
        """
        Create a setter for this mass quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            MassSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class MassDensity(TypedQuantity):
    """
    Type-safe mass density quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MassDensity("variable_name") -> Create unknown mass density
    - MassDensity(value, "unit", "variable_name") -> Create known mass density
    
    Examples:
    ---------
    >>> unknown = MassDensity("pressure")  # Unknown mass density
    >>> known = MassDensity(100, "gram_per_cubic_centimeter", "inlet_pressure")  # Known mass density
    
    Available units: "gram_per_cubic_centimeter", "gram_per_cubic_decimeter", "gram_per_cubic_meter"
    """
    __slots__ = ()
    _setter_class = ts.MassDensitySetter
    _expected_dimension = dim.MASS_DENSITY
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.MassDensitySetter:
        """
        Create a setter for this mass density quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            MassDensitySetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class MassFlowRate(TypedQuantity):
    """
    Type-safe mass flow rate quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MassFlowRate("variable_name") -> Create unknown mass flow rate
    - MassFlowRate(value, "unit", "variable_name") -> Create known mass flow rate
    
    Examples:
    ---------
    >>> unknown = MassFlowRate("pressure")  # Unknown mass flow rate
    >>> known = MassFlowRate(100, "kilograms_per_day", "inlet_pressure")  # Known mass flow rate
    
    Available units: "kilograms_per_day", "kilograms_per_hour", "kilograms_per_minute"
    """
    __slots__ = ()
    _setter_class = ts.MassFlowRateSetter
    _expected_dimension = dim.MASS_FLOW_RATE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.MassFlowRateSetter:
        """
        Create a setter for this mass flow rate quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            MassFlowRateSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class MassFlux(TypedQuantity):
    """
    Type-safe mass flux quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MassFlux("variable_name") -> Create unknown mass flux
    - MassFlux(value, "unit", "variable_name") -> Create known mass flux
    
    Examples:
    ---------
    >>> unknown = MassFlux("pressure")  # Unknown mass flux
    >>> known = MassFlux(100, "kilogram_per_square_meter_per_day", "inlet_pressure")  # Known mass flux
    
    Available units: "kilogram_per_square_meter_per_day", "kilogram_per_square_meter_per_hour", "kilogram_per_square_meter_per_minute"
    """
    __slots__ = ()
    _setter_class = ts.MassFluxSetter
    _expected_dimension = dim.MASS_FLUX
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.MassFluxSetter:
        """
        Create a setter for this mass flux quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            MassFluxSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class MassFractionOfI(TypedQuantity):
    """
    Type-safe mass fraction of "i" quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MassFractionOfI("variable_name") -> Create unknown mass fraction of "i"
    - MassFractionOfI(value, "unit", "variable_name") -> Create known mass fraction of "i"
    
    Examples:
    ---------
    >>> unknown = MassFractionOfI("pressure")  # Unknown mass fraction of "i"
    >>> known = MassFractionOfI(100, "grains_of_i_per_pound_total", "inlet_pressure")  # Known mass fraction of "i"
    
    Available units: "grains_of_i_per_pound_total", "gram_of_i_per_kilogram_total", "kilogram_of_i_per_kilogram_total"
    """
    __slots__ = ()
    _setter_class = ts.MassFractionOfISetter
    _expected_dimension = dim.MASS_FRACTION_OF_I
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.MassFractionOfISetter:
        """
        Create a setter for this mass fraction of "i" quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            MassFractionOfISetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class MassTransferCoefficient(TypedQuantity):
    """
    Type-safe mass transfer coefficient quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MassTransferCoefficient("variable_name") -> Create unknown mass transfer coefficient
    - MassTransferCoefficient(value, "unit", "variable_name") -> Create known mass transfer coefficient
    
    Examples:
    ---------
    >>> unknown = MassTransferCoefficient("pressure")  # Unknown mass transfer coefficient
    >>> known = MassTransferCoefficient(100, "gram_per_square_centimeter_per_second", "inlet_pressure")  # Known mass transfer coefficient
    
    Available units: "gram_per_square_centimeter_per_second", "kilogram_per_square_meter_per_second", "pounds_force_per_cubic_foot_per_hour"
    """
    __slots__ = ()
    _setter_class = ts.MassTransferCoefficientSetter
    _expected_dimension = dim.MASS_TRANSFER_COEFFICIENT
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.MassTransferCoefficientSetter:
        """
        Create a setter for this mass transfer coefficient quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            MassTransferCoefficientSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class MolalityOfSoluteI(TypedQuantity):
    """
    Type-safe molality of solute "i" quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MolalityOfSoluteI("variable_name") -> Create unknown molality of solute "i"
    - MolalityOfSoluteI(value, "unit", "variable_name") -> Create known molality of solute "i"
    
    Examples:
    ---------
    >>> unknown = MolalityOfSoluteI("pressure")  # Unknown molality of solute "i"
    >>> known = MolalityOfSoluteI(100, "gram_moles_of_i_per_kilogram", "inlet_pressure")  # Known molality of solute "i"
    
    Available units: "gram_moles_of_i_per_kilogram", "kilogram_mols_of_i_per_kilogram", "kmols_of_i_per_kilogram"
    """
    __slots__ = ()
    _setter_class = ts.MolalityOfSoluteISetter
    _expected_dimension = dim.MOLALITY_OF_SOLUTE_I
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.MolalityOfSoluteISetter:
        """
        Create a setter for this molality of solute "i" quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            MolalityOfSoluteISetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class MolarConcentrationByMass(TypedQuantity):
    """
    Type-safe molar concentration by mass quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MolarConcentrationByMass("variable_name") -> Create unknown molar concentration by mass
    - MolarConcentrationByMass(value, "unit", "variable_name") -> Create known molar concentration by mass
    
    Examples:
    ---------
    >>> unknown = MolarConcentrationByMass("pressure")  # Unknown molar concentration by mass
    >>> known = MolarConcentrationByMass(100, "gram_mole_or_mole_per_gram", "inlet_pressure")  # Known molar concentration by mass
    
    Available units: "gram_mole_or_mole_per_gram", "gram_mole_or_mole_per_kilogram", "kilogram_mole_or_kmol_per_kilogram"
    """
    __slots__ = ()
    _setter_class = ts.MolarConcentrationByMassSetter
    _expected_dimension = dim.MOLAR_CONCENTRATION_BY_MASS
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.MolarConcentrationByMassSetter:
        """
        Create a setter for this molar concentration by mass quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            MolarConcentrationByMassSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class MolarFlowRate(TypedQuantity):
    """
    Type-safe molar flow rate quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MolarFlowRate("variable_name") -> Create unknown molar flow rate
    - MolarFlowRate(value, "unit", "variable_name") -> Create known molar flow rate
    
    Examples:
    ---------
    >>> unknown = MolarFlowRate("pressure")  # Unknown molar flow rate
    >>> known = MolarFlowRate(100, "gram_mole_per_day", "inlet_pressure")  # Known molar flow rate
    
    Available units: "gram_mole_per_day", "gram_mole_per_hour", "gram_mole_per_minute"
    """
    __slots__ = ()
    _setter_class = ts.MolarFlowRateSetter
    _expected_dimension = dim.MOLAR_FLOW_RATE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.MolarFlowRateSetter:
        """
        Create a setter for this molar flow rate quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            MolarFlowRateSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class MolarFlux(TypedQuantity):
    """
    Type-safe molar flux quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MolarFlux("variable_name") -> Create unknown molar flux
    - MolarFlux(value, "unit", "variable_name") -> Create known molar flux
    
    Examples:
    ---------
    >>> unknown = MolarFlux("pressure")  # Unknown molar flux
    >>> known = MolarFlux(100, "kmol_per_square_meter_per_day", "inlet_pressure")  # Known molar flux
    
    Available units: "kmol_per_square_meter_per_day", "kmol_per_square_meter_per_hour", "kmol_per_square_meter_per_minute"
    """
    __slots__ = ()
    _setter_class = ts.MolarFluxSetter
    _expected_dimension = dim.MOLAR_FLUX
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.MolarFluxSetter:
        """
        Create a setter for this molar flux quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            MolarFluxSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class MolarHeatCapacity(TypedQuantity):
    """
    Type-safe molar heat capacity quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MolarHeatCapacity("variable_name") -> Create unknown molar heat capacity
    - MolarHeatCapacity(value, "unit", "variable_name") -> Create known molar heat capacity
    
    Examples:
    ---------
    >>> unknown = MolarHeatCapacity("pressure")  # Unknown molar heat capacity
    >>> known = MolarHeatCapacity(100, "btu_per_pound_mole_per_degree_fahrenheit_or_degree_rankine", "inlet_pressure")  # Known molar heat capacity
    
    Available units: "btu_per_pound_mole_per_degree_fahrenheit_or_degree_rankine", "calories_per_gram_mole_per_kelvin_or_degree_celsius", "joule_per_gram_mole_per_kelvin_or_degree_celsius"
    """
    __slots__ = ()
    _setter_class = ts.MolarHeatCapacitySetter
    _expected_dimension = dim.MOLAR_HEAT_CAPACITY
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.MolarHeatCapacitySetter:
        """
        Create a setter for this molar heat capacity quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            MolarHeatCapacitySetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class MolarityOfI(TypedQuantity):
    """
    Type-safe molarity of "i" quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MolarityOfI("variable_name") -> Create unknown molarity of "i"
    - MolarityOfI(value, "unit", "variable_name") -> Create known molarity of "i"
    
    Examples:
    ---------
    >>> unknown = MolarityOfI("pressure")  # Unknown molarity of "i"
    >>> known = MolarityOfI(100, "gram_moles_of_i_per_cubic_meter", "inlet_pressure")  # Known molarity of "i"
    
    Available units: "gram_moles_of_i_per_cubic_meter", "gram_moles_of_i_per_liter", "kilogram_moles_of_i_per_cubic_meter"
    """
    __slots__ = ()
    _setter_class = ts.MolarityOfISetter
    _expected_dimension = dim.MOLARITY_OF_I
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.MolarityOfISetter:
        """
        Create a setter for this molarity of "i" quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            MolarityOfISetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class MoleFractionOfI(TypedQuantity):
    """
    Type-safe mole fraction of "i" quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MoleFractionOfI("variable_name") -> Create unknown mole fraction of "i"
    - MoleFractionOfI(value, "unit", "variable_name") -> Create known mole fraction of "i"
    
    Examples:
    ---------
    >>> unknown = MoleFractionOfI("pressure")  # Unknown mole fraction of "i"
    >>> known = MoleFractionOfI(100, "gram_mole_of_i_per_gram_mole_total", "inlet_pressure")  # Known mole fraction of "i"
    
    Available units: "gram_mole_of_i_per_gram_mole_total", "kilogram_mole_of_i_per_kilogram_mole_total", "kilomole_of_i_per_kilomole_total"
    """
    __slots__ = ()
    _setter_class = ts.MoleFractionOfISetter
    _expected_dimension = dim.MOLE_FRACTION_OF_I
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.MoleFractionOfISetter:
        """
        Create a setter for this mole fraction of "i" quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            MoleFractionOfISetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class MomentOfInertia(TypedQuantity):
    """
    Type-safe moment of inertia quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MomentOfInertia("variable_name") -> Create unknown moment of inertia
    - MomentOfInertia(value, "unit", "variable_name") -> Create known moment of inertia
    
    Examples:
    ---------
    >>> unknown = MomentOfInertia("pressure")  # Unknown moment of inertia
    >>> known = MomentOfInertia(100, "gram_force_centimeter_square_second", "inlet_pressure")  # Known moment of inertia
    
    Available units: "gram_force_centimeter_square_second", "gram_square_centimeter", "kilogram_force_centimeter_square_second"
    """
    __slots__ = ()
    _setter_class = ts.MomentOfInertiaSetter
    _expected_dimension = dim.MOMENT_OF_INERTIA
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.MomentOfInertiaSetter:
        """
        Create a setter for this moment of inertia quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            MomentOfInertiaSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class MomentumFlowRate(TypedQuantity):
    """
    Type-safe momentum flow rate quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MomentumFlowRate("variable_name") -> Create unknown momentum flow rate
    - MomentumFlowRate(value, "unit", "variable_name") -> Create known momentum flow rate
    
    Examples:
    ---------
    >>> unknown = MomentumFlowRate("pressure")  # Unknown momentum flow rate
    >>> known = MomentumFlowRate(100, "foot_pounds_per_square_hour", "inlet_pressure")  # Known momentum flow rate
    
    Available units: "foot_pounds_per_square_hour", "foot_pounds_per_square_minute", "foot_pounds_per_square_second"
    """
    __slots__ = ()
    _setter_class = ts.MomentumFlowRateSetter
    _expected_dimension = dim.MOMENTUM_FLOW_RATE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.MomentumFlowRateSetter:
        """
        Create a setter for this momentum flow rate quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            MomentumFlowRateSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class MomentumFlux(TypedQuantity):
    """
    Type-safe momentum flux quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - MomentumFlux("variable_name") -> Create unknown momentum flux
    - MomentumFlux(value, "unit", "variable_name") -> Create known momentum flux
    
    Examples:
    ---------
    >>> unknown = MomentumFlux("pressure")  # Unknown momentum flux
    >>> known = MomentumFlux(100, "dyne_per_square_centimeter", "inlet_pressure")  # Known momentum flux
    
    Available units: "dyne_per_square_centimeter", "gram_per_centimeter_per_square_second", "newton_per_square_meter"
    """
    __slots__ = ()
    _setter_class = ts.MomentumFluxSetter
    _expected_dimension = dim.MOMENTUM_FLUX
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.MomentumFluxSetter:
        """
        Create a setter for this momentum flux quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            MomentumFluxSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class NormalityOfSolution(TypedQuantity):
    """
    Type-safe normality of solution quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - NormalityOfSolution("variable_name") -> Create unknown normality of solution
    - NormalityOfSolution(value, "unit", "variable_name") -> Create known normality of solution
    
    Examples:
    ---------
    >>> unknown = NormalityOfSolution("pressure")  # Unknown normality of solution
    >>> known = NormalityOfSolution(100, "gram_equivalents_per_cubic_meter", "inlet_pressure")  # Known normality of solution
    
    Available units: "gram_equivalents_per_cubic_meter", "gram_equivalents_per_liter", "pound_equivalents_per_cubic_foot"
    """
    __slots__ = ()
    _setter_class = ts.NormalityOfSolutionSetter
    _expected_dimension = dim.NORMALITY_OF_SOLUTION
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.NormalityOfSolutionSetter:
        """
        Create a setter for this normality of solution quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            NormalityOfSolutionSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class ParticleDensity(TypedQuantity):
    """
    Type-safe particle density quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ParticleDensity("variable_name") -> Create unknown particle density
    - ParticleDensity(value, "unit", "variable_name") -> Create known particle density
    
    Examples:
    ---------
    >>> unknown = ParticleDensity("pressure")  # Unknown particle density
    >>> known = ParticleDensity(100, "particles_per_cubic_centimeter", "inlet_pressure")  # Known particle density
    
    Available units: "particles_per_cubic_centimeter", "particles_per_cubic_foot", "particles_per_cubic_meter"
    """
    __slots__ = ()
    _setter_class = ts.ParticleDensitySetter
    _expected_dimension = dim.PARTICLE_DENSITY
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.ParticleDensitySetter:
        """
        Create a setter for this particle density quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            ParticleDensitySetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class Percent(TypedQuantity):
    """
    Type-safe percent quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Percent("variable_name") -> Create unknown percent
    - Percent(value, "unit", "variable_name") -> Create known percent
    
    Examples:
    ---------
    >>> unknown = Percent("pressure")  # Unknown percent
    >>> known = Percent(100, "percent", "inlet_pressure")  # Known percent
    
    Available units: "percent", "per_mille", "basis_point"
    """
    __slots__ = ()
    _setter_class = ts.PercentSetter
    _expected_dimension = dim.PERCENT
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.PercentSetter:
        """
        Create a setter for this percent quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            PercentSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class Permeability(TypedQuantity):
    """
    Type-safe permeability quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Permeability("variable_name") -> Create unknown permeability
    - Permeability(value, "unit", "variable_name") -> Create known permeability
    
    Examples:
    ---------
    >>> unknown = Permeability("pressure")  # Unknown permeability
    >>> known = Permeability(100, "darcy", "inlet_pressure")  # Known permeability
    
    Available units: "darcy", "square_feet", "square_meters"
    """
    __slots__ = ()
    _setter_class = ts.PermeabilitySetter
    _expected_dimension = dim.PERMEABILITY
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.PermeabilitySetter:
        """
        Create a setter for this permeability quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            PermeabilitySetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class PhotonEmissionRate(TypedQuantity):
    """
    Type-safe photon emission rate quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - PhotonEmissionRate("variable_name") -> Create unknown photon emission rate
    - PhotonEmissionRate(value, "unit", "variable_name") -> Create known photon emission rate
    
    Examples:
    ---------
    >>> unknown = PhotonEmissionRate("pressure")  # Unknown photon emission rate
    >>> known = PhotonEmissionRate(100, "rayleigh", "inlet_pressure")  # Known photon emission rate
    
    Available units: "rayleigh", "reciprocal_square_meter_second"
    """
    __slots__ = ()
    _setter_class = ts.PhotonEmissionRateSetter
    _expected_dimension = dim.PHOTON_EMISSION_RATE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.PhotonEmissionRateSetter:
        """
        Create a setter for this photon emission rate quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            PhotonEmissionRateSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class PowerPerUnitMass(TypedQuantity):
    """
    Type-safe power per unit mass or specific power quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - PowerPerUnitMass("variable_name") -> Create unknown power per unit mass or specific power
    - PowerPerUnitMass(value, "unit", "variable_name") -> Create known power per unit mass or specific power
    
    Examples:
    ---------
    >>> unknown = PowerPerUnitMass("pressure")  # Unknown power per unit mass or specific power
    >>> known = PowerPerUnitMass(100, "british_thermal_unit_per_hour_per_pound_mass", "inlet_pressure")  # Known power per unit mass or specific power
    
    Available units: "british_thermal_unit_per_hour_per_pound_mass", "calorie_per_second_per_gram", "kilocalorie_per_hour_per_kilogram"
    """
    __slots__ = ()
    _setter_class = ts.PowerPerUnitMassSetter
    _expected_dimension = dim.POWER_PER_UNIT_MASS
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.PowerPerUnitMassSetter:
        """
        Create a setter for this power per unit mass or specific power quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            PowerPerUnitMassSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class PowerPerUnitVolume(TypedQuantity):
    """
    Type-safe power per unit volume or power density quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - PowerPerUnitVolume("variable_name") -> Create unknown power per unit volume or power density
    - PowerPerUnitVolume(value, "unit", "variable_name") -> Create known power per unit volume or power density
    
    Examples:
    ---------
    >>> unknown = PowerPerUnitVolume("pressure")  # Unknown power per unit volume or power density
    >>> known = PowerPerUnitVolume(100, "british_thermal_unit_per_hour_per_cubic_foot", "inlet_pressure")  # Known power per unit volume or power density
    
    Available units: "british_thermal_unit_per_hour_per_cubic_foot", "calorie_per_second_per_cubic_centimeter", "chu_per_hour_per_cubic_foot"
    """
    __slots__ = ()
    _setter_class = ts.PowerPerUnitVolumeSetter
    _expected_dimension = dim.POWER_PER_UNIT_VOLUME
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.PowerPerUnitVolumeSetter:
        """
        Create a setter for this power per unit volume or power density quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            PowerPerUnitVolumeSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class PowerThermalDuty(TypedQuantity):
    """
    Type-safe power, thermal duty quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - PowerThermalDuty("variable_name") -> Create unknown power, thermal duty
    - PowerThermalDuty(value, "unit", "variable_name") -> Create known power, thermal duty
    
    Examples:
    ---------
    >>> unknown = PowerThermalDuty("pressure")  # Unknown power, thermal duty
    >>> known = PowerThermalDuty(100, "abwatt_emu_of_power", "inlet_pressure")  # Known power, thermal duty
    
    Available units: "abwatt_emu_of_power", "boiler_horsepower", "british_thermal_unit_mean"
    """
    __slots__ = ()
    _setter_class = ts.PowerThermalDutySetter
    _expected_dimension = dim.POWER_THERMAL_DUTY
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.PowerThermalDutySetter:
        """
        Create a setter for this power, thermal duty quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            PowerThermalDutySetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class Pressure(TypedQuantity):
    """
    Type-safe pressure quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Pressure("variable_name") -> Create unknown pressure
    - Pressure(value, "unit", "variable_name") -> Create known pressure
    
    Examples:
    ---------
    >>> unknown = Pressure("pressure")  # Unknown pressure
    >>> known = Pressure(100, "atmosphere_standard", "inlet_pressure")  # Known pressure
    
    Available units: "atmosphere_standard", "bar", "barye"
    """
    __slots__ = ()
    _setter_class = ts.PressureSetter
    _expected_dimension = dim.PRESSURE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.PressureSetter:
        """
        Create a setter for this pressure quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            PressureSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class RadiationDoseEquivalent(TypedQuantity):
    """
    Type-safe radiation dose equivalent quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - RadiationDoseEquivalent("variable_name") -> Create unknown radiation dose equivalent
    - RadiationDoseEquivalent(value, "unit", "variable_name") -> Create known radiation dose equivalent
    
    Examples:
    ---------
    >>> unknown = RadiationDoseEquivalent("pressure")  # Unknown radiation dose equivalent
    >>> known = RadiationDoseEquivalent(100, "rem", "inlet_pressure")  # Known radiation dose equivalent
    
    Available units: "rem", "sievert", "millisievert"
    """
    __slots__ = ()
    _setter_class = ts.RadiationDoseEquivalentSetter
    _expected_dimension = dim.RADIATION_DOSE_EQUIVALENT
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.RadiationDoseEquivalentSetter:
        """
        Create a setter for this radiation dose equivalent quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            RadiationDoseEquivalentSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class RadiationExposure(TypedQuantity):
    """
    Type-safe radiation exposure quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - RadiationExposure("variable_name") -> Create unknown radiation exposure
    - RadiationExposure(value, "unit", "variable_name") -> Create known radiation exposure
    
    Examples:
    ---------
    >>> unknown = RadiationExposure("pressure")  # Unknown radiation exposure
    >>> known = RadiationExposure(100, "coulomb_per_kilogram", "inlet_pressure")  # Known radiation exposure
    
    Available units: "coulomb_per_kilogram", "d_unit", "pastille_dose_b_unit"
    """
    __slots__ = ()
    _setter_class = ts.RadiationExposureSetter
    _expected_dimension = dim.RADIATION_EXPOSURE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.RadiationExposureSetter:
        """
        Create a setter for this radiation exposure quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            RadiationExposureSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class Radioactivity(TypedQuantity):
    """
    Type-safe radioactivity quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Radioactivity("variable_name") -> Create unknown radioactivity
    - Radioactivity(value, "unit", "variable_name") -> Create known radioactivity
    
    Examples:
    ---------
    >>> unknown = Radioactivity("pressure")  # Unknown radioactivity
    >>> known = Radioactivity(100, "becquerel", "inlet_pressure")  # Known radioactivity
    
    Available units: "becquerel", "curie", "mache_unit"
    """
    __slots__ = ()
    _setter_class = ts.RadioactivitySetter
    _expected_dimension = dim.RADIOACTIVITY
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.RadioactivitySetter:
        """
        Create a setter for this radioactivity quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            RadioactivitySetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class SecondMomentOfArea(TypedQuantity):
    """
    Type-safe second moment of area quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - SecondMomentOfArea("variable_name") -> Create unknown second moment of area
    - SecondMomentOfArea(value, "unit", "variable_name") -> Create known second moment of area
    
    Examples:
    ---------
    >>> unknown = SecondMomentOfArea("pressure")  # Unknown second moment of area
    >>> known = SecondMomentOfArea(100, "inch_quadrupled", "inlet_pressure")  # Known second moment of area
    
    Available units: "inch_quadrupled", "centimeter_quadrupled", "foot_quadrupled"
    """
    __slots__ = ()
    _setter_class = ts.SecondMomentOfAreaSetter
    _expected_dimension = dim.SECOND_MOMENT_OF_AREA
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.SecondMomentOfAreaSetter:
        """
        Create a setter for this second moment of area quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            SecondMomentOfAreaSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class SecondRadiationConstantPlanck(TypedQuantity):
    """
    Type-safe second radiation constant (planck) quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - SecondRadiationConstantPlanck("variable_name") -> Create unknown second radiation constant (planck)
    - SecondRadiationConstantPlanck(value, "unit", "variable_name") -> Create known second radiation constant (planck)
    
    Examples:
    ---------
    >>> unknown = SecondRadiationConstantPlanck("pressure")  # Unknown second radiation constant (planck)
    >>> known = SecondRadiationConstantPlanck(100, "meter_kelvin", "inlet_pressure")  # Known second radiation constant (planck)
    
    Available units: "meter_kelvin"
    """
    __slots__ = ()
    _setter_class = ts.SecondRadiationConstantPlanckSetter
    _expected_dimension = dim.SECOND_RADIATION_CONSTANT_PLANCK
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.SecondRadiationConstantPlanckSetter:
        """
        Create a setter for this second radiation constant (planck) quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            SecondRadiationConstantPlanckSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class SpecificEnthalpy(TypedQuantity):
    """
    Type-safe specific enthalpy quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - SpecificEnthalpy("variable_name") -> Create unknown specific enthalpy
    - SpecificEnthalpy(value, "unit", "variable_name") -> Create known specific enthalpy
    
    Examples:
    ---------
    >>> unknown = SpecificEnthalpy("pressure")  # Unknown specific enthalpy
    >>> known = SpecificEnthalpy(100, "british_thermal_unit_mean", "inlet_pressure")  # Known specific enthalpy
    
    Available units: "british_thermal_unit_mean", "british_thermal_unit_per_pound", "calorie_per_gram"
    """
    __slots__ = ()
    _setter_class = ts.SpecificEnthalpySetter
    _expected_dimension = dim.SPECIFIC_ENTHALPY
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.SpecificEnthalpySetter:
        """
        Create a setter for this specific enthalpy quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            SpecificEnthalpySetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class SpecificGravity(TypedQuantity):
    """
    Type-safe specific gravity quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - SpecificGravity("variable_name") -> Create unknown specific gravity
    - SpecificGravity(value, "unit", "variable_name") -> Create known specific gravity
    
    Examples:
    ---------
    >>> unknown = SpecificGravity("pressure")  # Unknown specific gravity
    >>> known = SpecificGravity(100, "dimensionless", "inlet_pressure")  # Known specific gravity
    
    Available units: "dimensionless"
    """
    __slots__ = ()
    _setter_class = ts.SpecificGravitySetter
    _expected_dimension = dim.SPECIFIC_GRAVITY
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.SpecificGravitySetter:
        """
        Create a setter for this specific gravity quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            SpecificGravitySetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class SpecificHeatCapacityConstantPressure(TypedQuantity):
    """
    Type-safe specific heat capacity (constant pressure) quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - SpecificHeatCapacityConstantPressure("variable_name") -> Create unknown specific heat capacity (constant pressure)
    - SpecificHeatCapacityConstantPressure(value, "unit", "variable_name") -> Create known specific heat capacity (constant pressure)
    
    Examples:
    ---------
    >>> unknown = SpecificHeatCapacityConstantPressure("pressure")  # Unknown specific heat capacity (constant pressure)
    >>> known = SpecificHeatCapacityConstantPressure(100, "btu_per_pound_per_degree_fahrenheit_or_degree_rankine", "inlet_pressure")  # Known specific heat capacity (constant pressure)
    
    Available units: "btu_per_pound_per_degree_fahrenheit_or_degree_rankine", "calories_per_gram_per_kelvin_or_degree_celsius", "joules_per_kilogram_per_kelvin_or_degree_celsius"
    """
    __slots__ = ()
    _setter_class = ts.SpecificHeatCapacityConstantPressureSetter
    _expected_dimension = dim.SPECIFIC_HEAT_CAPACITY_CONSTANT_PRESSURE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.SpecificHeatCapacityConstantPressureSetter:
        """
        Create a setter for this specific heat capacity (constant pressure) quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            SpecificHeatCapacityConstantPressureSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class SpecificLength(TypedQuantity):
    """
    Type-safe specific length quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - SpecificLength("variable_name") -> Create unknown specific length
    - SpecificLength(value, "unit", "variable_name") -> Create known specific length
    
    Examples:
    ---------
    >>> unknown = SpecificLength("pressure")  # Unknown specific length
    >>> known = SpecificLength(100, "centimeter_per_gram", "inlet_pressure")  # Known specific length
    
    Available units: "centimeter_per_gram", "cotton_count", "ft_per_pound"
    """
    __slots__ = ()
    _setter_class = ts.SpecificLengthSetter
    _expected_dimension = dim.SPECIFIC_LENGTH
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.SpecificLengthSetter:
        """
        Create a setter for this specific length quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            SpecificLengthSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class SpecificSurface(TypedQuantity):
    """
    Type-safe specific surface quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - SpecificSurface("variable_name") -> Create unknown specific surface
    - SpecificSurface(value, "unit", "variable_name") -> Create known specific surface
    
    Examples:
    ---------
    >>> unknown = SpecificSurface("pressure")  # Unknown specific surface
    >>> known = SpecificSurface(100, "square_centimeter_per_gram", "inlet_pressure")  # Known specific surface
    
    Available units: "square_centimeter_per_gram", "square_foot_per_kilogram", "square_foot_per_pound"
    """
    __slots__ = ()
    _setter_class = ts.SpecificSurfaceSetter
    _expected_dimension = dim.SPECIFIC_SURFACE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.SpecificSurfaceSetter:
        """
        Create a setter for this specific surface quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            SpecificSurfaceSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class SpecificVolume(TypedQuantity):
    """
    Type-safe specific volume quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - SpecificVolume("variable_name") -> Create unknown specific volume
    - SpecificVolume(value, "unit", "variable_name") -> Create known specific volume
    
    Examples:
    ---------
    >>> unknown = SpecificVolume("pressure")  # Unknown specific volume
    >>> known = SpecificVolume(100, "cubic_centimeter_per_gram", "inlet_pressure")  # Known specific volume
    
    Available units: "cubic_centimeter_per_gram", "cubic_foot_per_kilogram", "cubic_foot_per_pound"
    """
    __slots__ = ()
    _setter_class = ts.SpecificVolumeSetter
    _expected_dimension = dim.SPECIFIC_VOLUME
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.SpecificVolumeSetter:
        """
        Create a setter for this specific volume quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            SpecificVolumeSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class Stress(TypedQuantity):
    """
    Type-safe stress quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Stress("variable_name") -> Create unknown stress
    - Stress(value, "unit", "variable_name") -> Create known stress
    
    Examples:
    ---------
    >>> unknown = Stress("pressure")  # Unknown stress
    >>> known = Stress(100, "dyne_per_square_centimeter", "inlet_pressure")  # Known stress
    
    Available units: "dyne_per_square_centimeter", "gigapascal", "hectopascal"
    """
    __slots__ = ()
    _setter_class = ts.StressSetter
    _expected_dimension = dim.STRESS
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.StressSetter:
        """
        Create a setter for this stress quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            StressSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class SurfaceMassDensity(TypedQuantity):
    """
    Type-safe surface mass density quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - SurfaceMassDensity("variable_name") -> Create unknown surface mass density
    - SurfaceMassDensity(value, "unit", "variable_name") -> Create known surface mass density
    
    Examples:
    ---------
    >>> unknown = SurfaceMassDensity("pressure")  # Unknown surface mass density
    >>> known = SurfaceMassDensity(100, "gram_per_square_centimeter", "inlet_pressure")  # Known surface mass density
    
    Available units: "gram_per_square_centimeter", "gram_per_square_meter", "kilogram_per_square_meter"
    """
    __slots__ = ()
    _setter_class = ts.SurfaceMassDensitySetter
    _expected_dimension = dim.SURFACE_MASS_DENSITY
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.SurfaceMassDensitySetter:
        """
        Create a setter for this surface mass density quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            SurfaceMassDensitySetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class SurfaceTension(TypedQuantity):
    """
    Type-safe surface tension quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - SurfaceTension("variable_name") -> Create unknown surface tension
    - SurfaceTension(value, "unit", "variable_name") -> Create known surface tension
    
    Examples:
    ---------
    >>> unknown = SurfaceTension("pressure")  # Unknown surface tension
    >>> known = SurfaceTension(100, "dyne_per_centimeter", "inlet_pressure")  # Known surface tension
    
    Available units: "dyne_per_centimeter", "gram_force_per_centimeter", "newton_per_meter"
    """
    __slots__ = ()
    _setter_class = ts.SurfaceTensionSetter
    _expected_dimension = dim.SURFACE_TENSION
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.SurfaceTensionSetter:
        """
        Create a setter for this surface tension quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            SurfaceTensionSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class Temperature(TypedQuantity):
    """
    Type-safe temperature quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Temperature("variable_name") -> Create unknown temperature
    - Temperature(value, "unit", "variable_name") -> Create known temperature
    
    Examples:
    ---------
    >>> unknown = Temperature("pressure")  # Unknown temperature
    >>> known = Temperature(100, "degree_celsius_unit_size", "inlet_pressure")  # Known temperature
    
    Available units: "degree_celsius_unit_size", "degree_fahrenheit_unit_size", "degree_r_aumur_unit_size"
    """
    __slots__ = ()
    _setter_class = ts.TemperatureSetter
    _expected_dimension = dim.TEMPERATURE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.TemperatureSetter:
        """
        Create a setter for this temperature quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            TemperatureSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class ThermalConductivity(TypedQuantity):
    """
    Type-safe thermal conductivity quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ThermalConductivity("variable_name") -> Create unknown thermal conductivity
    - ThermalConductivity(value, "unit", "variable_name") -> Create known thermal conductivity
    
    Examples:
    ---------
    >>> unknown = ThermalConductivity("pressure")  # Unknown thermal conductivity
    >>> known = ThermalConductivity(100, "btu_it", "inlet_pressure")  # Known thermal conductivity
    
    Available units: "btu_it", "btu_therm", "btu_therm"
    """
    __slots__ = ()
    _setter_class = ts.ThermalConductivitySetter
    _expected_dimension = dim.THERMAL_CONDUCTIVITY
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.ThermalConductivitySetter:
        """
        Create a setter for this thermal conductivity quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            ThermalConductivitySetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class Time(TypedQuantity):
    """
    Type-safe time quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Time("variable_name") -> Create unknown time
    - Time(value, "unit", "variable_name") -> Create known time
    
    Examples:
    ---------
    >>> unknown = Time("pressure")  # Unknown time
    >>> known = Time(100, "blink", "inlet_pressure")  # Known time
    
    Available units: "blink", "century", "chronon_or_tempon"
    """
    __slots__ = ()
    _setter_class = ts.TimeSetter
    _expected_dimension = dim.TIME
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.TimeSetter:
        """
        Create a setter for this time quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            TimeSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class Torque(TypedQuantity):
    """
    Type-safe torque quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Torque("variable_name") -> Create unknown torque
    - Torque(value, "unit", "variable_name") -> Create known torque
    
    Examples:
    ---------
    >>> unknown = Torque("pressure")  # Unknown torque
    >>> known = Torque(100, "centimeter_kilogram_force", "inlet_pressure")  # Known torque
    
    Available units: "centimeter_kilogram_force", "dyne_centimeter", "foot_kilogram_force"
    """
    __slots__ = ()
    _setter_class = ts.TorqueSetter
    _expected_dimension = dim.TORQUE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.TorqueSetter:
        """
        Create a setter for this torque quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            TorqueSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class TurbulenceEnergyDissipationRate(TypedQuantity):
    """
    Type-safe turbulence energy dissipation rate quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - TurbulenceEnergyDissipationRate("variable_name") -> Create unknown turbulence energy dissipation rate
    - TurbulenceEnergyDissipationRate(value, "unit", "variable_name") -> Create known turbulence energy dissipation rate
    
    Examples:
    ---------
    >>> unknown = TurbulenceEnergyDissipationRate("pressure")  # Unknown turbulence energy dissipation rate
    >>> known = TurbulenceEnergyDissipationRate(100, "square_foot_per_cubic_second", "inlet_pressure")  # Known turbulence energy dissipation rate
    
    Available units: "square_foot_per_cubic_second", "square_meter_per_cubic_second"
    """
    __slots__ = ()
    _setter_class = ts.TurbulenceEnergyDissipationRateSetter
    _expected_dimension = dim.TURBULENCE_ENERGY_DISSIPATION_RATE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.TurbulenceEnergyDissipationRateSetter:
        """
        Create a setter for this turbulence energy dissipation rate quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            TurbulenceEnergyDissipationRateSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class VelocityAngular(TypedQuantity):
    """
    Type-safe velocity, angular quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - VelocityAngular("variable_name") -> Create unknown velocity, angular
    - VelocityAngular(value, "unit", "variable_name") -> Create known velocity, angular
    
    Examples:
    ---------
    >>> unknown = VelocityAngular("pressure")  # Unknown velocity, angular
    >>> known = VelocityAngular(100, "degree_per_minute", "inlet_pressure")  # Known velocity, angular
    
    Available units: "degree_per_minute", "degree_per_second", "grade_per_minute"
    """
    __slots__ = ()
    _setter_class = ts.VelocityAngularSetter
    _expected_dimension = dim.VELOCITY_ANGULAR
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.VelocityAngularSetter:
        """
        Create a setter for this velocity, angular quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            VelocityAngularSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class VelocityLinear(TypedQuantity):
    """
    Type-safe velocity, linear quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - VelocityLinear("variable_name") -> Create unknown velocity, linear
    - VelocityLinear(value, "unit", "variable_name") -> Create known velocity, linear
    
    Examples:
    ---------
    >>> unknown = VelocityLinear("pressure")  # Unknown velocity, linear
    >>> known = VelocityLinear(100, "foot_per_hour", "inlet_pressure")  # Known velocity, linear
    
    Available units: "foot_per_hour", "foot_per_minute", "foot_per_second"
    """
    __slots__ = ()
    _setter_class = ts.VelocityLinearSetter
    _expected_dimension = dim.VELOCITY_LINEAR
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.VelocityLinearSetter:
        """
        Create a setter for this velocity, linear quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            VelocityLinearSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class ViscosityDynamic(TypedQuantity):
    """
    Type-safe viscosity, dynamic quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ViscosityDynamic("variable_name") -> Create unknown viscosity, dynamic
    - ViscosityDynamic(value, "unit", "variable_name") -> Create known viscosity, dynamic
    
    Examples:
    ---------
    >>> unknown = ViscosityDynamic("pressure")  # Unknown viscosity, dynamic
    >>> known = ViscosityDynamic(100, "centipoise", "inlet_pressure")  # Known viscosity, dynamic
    
    Available units: "centipoise", "dyne_second_per_square_centimeter", "kilopound_second_per_square_meter"
    """
    __slots__ = ()
    _setter_class = ts.ViscosityDynamicSetter
    _expected_dimension = dim.VISCOSITY_DYNAMIC
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.ViscosityDynamicSetter:
        """
        Create a setter for this viscosity, dynamic quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            ViscosityDynamicSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class ViscosityKinematic(TypedQuantity):
    """
    Type-safe viscosity, kinematic quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - ViscosityKinematic("variable_name") -> Create unknown viscosity, kinematic
    - ViscosityKinematic(value, "unit", "variable_name") -> Create known viscosity, kinematic
    
    Examples:
    ---------
    >>> unknown = ViscosityKinematic("pressure")  # Unknown viscosity, kinematic
    >>> known = ViscosityKinematic(100, "centistokes", "inlet_pressure")  # Known viscosity, kinematic
    
    Available units: "centistokes", "millistokes", "square_centimeter_per_second"
    """
    __slots__ = ()
    _setter_class = ts.ViscosityKinematicSetter
    _expected_dimension = dim.VISCOSITY_KINEMATIC
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.ViscosityKinematicSetter:
        """
        Create a setter for this viscosity, kinematic quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            ViscosityKinematicSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class Volume(TypedQuantity):
    """
    Type-safe volume quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Volume("variable_name") -> Create unknown volume
    - Volume(value, "unit", "variable_name") -> Create known volume
    
    Examples:
    ---------
    >>> unknown = Volume("pressure")  # Unknown volume
    >>> known = Volume(100, "acre_foot", "inlet_pressure")  # Known volume
    
    Available units: "acre_foot", "acre_inch", "barrel_us_liquid"
    """
    __slots__ = ()
    _setter_class = ts.VolumeSetter
    _expected_dimension = dim.VOLUME
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.VolumeSetter:
        """
        Create a setter for this volume quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            VolumeSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class VolumeFractionOfI(TypedQuantity):
    """
    Type-safe volume fraction of "i" quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - VolumeFractionOfI("variable_name") -> Create unknown volume fraction of "i"
    - VolumeFractionOfI(value, "unit", "variable_name") -> Create known volume fraction of "i"
    
    Examples:
    ---------
    >>> unknown = VolumeFractionOfI("pressure")  # Unknown volume fraction of "i"
    >>> known = VolumeFractionOfI(100, "cubic_centimeters_of_i_per_cubic_meter_total", "inlet_pressure")  # Known volume fraction of "i"
    
    Available units: "cubic_centimeters_of_i_per_cubic_meter_total", "cubic_foot_of_i_per_cubic_foot_total", "cubic_meters_of_i_per_cubic_meter_total"
    """
    __slots__ = ()
    _setter_class = ts.VolumeFractionOfISetter
    _expected_dimension = dim.VOLUME_FRACTION_OF_I
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.VolumeFractionOfISetter:
        """
        Create a setter for this volume fraction of "i" quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            VolumeFractionOfISetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class VolumetricCalorificHeatingValue(TypedQuantity):
    """
    Type-safe volumetric calorific (heating) value quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - VolumetricCalorificHeatingValue("variable_name") -> Create unknown volumetric calorific (heating) value
    - VolumetricCalorificHeatingValue(value, "unit", "variable_name") -> Create known volumetric calorific (heating) value
    
    Examples:
    ---------
    >>> unknown = VolumetricCalorificHeatingValue("pressure")  # Unknown volumetric calorific (heating) value
    >>> known = VolumetricCalorificHeatingValue(100, "british_thermal_unit_per_cubic_foot", "inlet_pressure")  # Known volumetric calorific (heating) value
    
    Available units: "british_thermal_unit_per_cubic_foot", "british_thermal_unit_per_gallon_uk", "british_thermal_unit_per_gallon_us"
    """
    __slots__ = ()
    _setter_class = ts.VolumetricCalorificHeatingValueSetter
    _expected_dimension = dim.VOLUMETRIC_CALORIFIC_HEATING_VALUE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.VolumetricCalorificHeatingValueSetter:
        """
        Create a setter for this volumetric calorific (heating) value quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            VolumetricCalorificHeatingValueSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class VolumetricCoefficientOfExpansion(TypedQuantity):
    """
    Type-safe volumetric coefficient of expansion quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - VolumetricCoefficientOfExpansion("variable_name") -> Create unknown volumetric coefficient of expansion
    - VolumetricCoefficientOfExpansion(value, "unit", "variable_name") -> Create known volumetric coefficient of expansion
    
    Examples:
    ---------
    >>> unknown = VolumetricCoefficientOfExpansion("pressure")  # Unknown volumetric coefficient of expansion
    >>> known = VolumetricCoefficientOfExpansion(100, "gram_per_cubic_centimeter_per_kelvin_or_degree_celsius", "inlet_pressure")  # Known volumetric coefficient of expansion
    
    Available units: "gram_per_cubic_centimeter_per_kelvin_or_degree_celsius", "kilogram_per_cubic_meter_per_kelvin_or_degree_celsius", "pound_per_cubic_foot_per_degree_fahrenheit_or_degree_rankine"
    """
    __slots__ = ()
    _setter_class = ts.VolumetricCoefficientOfExpansionSetter
    _expected_dimension = dim.VOLUMETRIC_COEFFICIENT_OF_EXPANSION
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.VolumetricCoefficientOfExpansionSetter:
        """
        Create a setter for this volumetric coefficient of expansion quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            VolumetricCoefficientOfExpansionSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class VolumetricFlowRate(TypedQuantity):
    """
    Type-safe volumetric flow rate quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - VolumetricFlowRate("variable_name") -> Create unknown volumetric flow rate
    - VolumetricFlowRate(value, "unit", "variable_name") -> Create known volumetric flow rate
    
    Examples:
    ---------
    >>> unknown = VolumetricFlowRate("pressure")  # Unknown volumetric flow rate
    >>> known = VolumetricFlowRate(100, "cubic_feet_per_day", "inlet_pressure")  # Known volumetric flow rate
    
    Available units: "cubic_feet_per_day", "cubic_feet_per_hour", "cubic_feet_per_minute"
    """
    __slots__ = ()
    _setter_class = ts.VolumetricFlowRateSetter
    _expected_dimension = dim.VOLUMETRIC_FLOW_RATE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.VolumetricFlowRateSetter:
        """
        Create a setter for this volumetric flow rate quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            VolumetricFlowRateSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class VolumetricFlux(TypedQuantity):
    """
    Type-safe volumetric flux quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - VolumetricFlux("variable_name") -> Create unknown volumetric flux
    - VolumetricFlux(value, "unit", "variable_name") -> Create known volumetric flux
    
    Examples:
    ---------
    >>> unknown = VolumetricFlux("pressure")  # Unknown volumetric flux
    >>> known = VolumetricFlux(100, "cubic_feet_per_square_foot_per_day", "inlet_pressure")  # Known volumetric flux
    
    Available units: "cubic_feet_per_square_foot_per_day", "cubic_feet_per_square_foot_per_hour", "cubic_feet_per_square_foot_per_minute"
    """
    __slots__ = ()
    _setter_class = ts.VolumetricFluxSetter
    _expected_dimension = dim.VOLUMETRIC_FLUX
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.VolumetricFluxSetter:
        """
        Create a setter for this volumetric flux quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            VolumetricFluxSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class VolumetricMassFlowRate(TypedQuantity):
    """
    Type-safe volumetric mass flow rate quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - VolumetricMassFlowRate("variable_name") -> Create unknown volumetric mass flow rate
    - VolumetricMassFlowRate(value, "unit", "variable_name") -> Create known volumetric mass flow rate
    
    Examples:
    ---------
    >>> unknown = VolumetricMassFlowRate("pressure")  # Unknown volumetric mass flow rate
    >>> known = VolumetricMassFlowRate(100, "gram_per_second_per_cubic_centimeter", "inlet_pressure")  # Known volumetric mass flow rate
    
    Available units: "gram_per_second_per_cubic_centimeter", "kilogram_per_hour_per_cubic_foot", "kilogram_per_hour_per_cubic_meter"
    """
    __slots__ = ()
    _setter_class = ts.VolumetricMassFlowRateSetter
    _expected_dimension = dim.VOLUMETRIC_MASS_FLOW_RATE
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.VolumetricMassFlowRateSetter:
        """
        Create a setter for this volumetric mass flow rate quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            VolumetricMassFlowRateSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

class Wavenumber(TypedQuantity):
    """
    Type-safe wavenumber quantity with expression capabilities.
    
    Constructor Options:
    -------------------
    - Wavenumber("variable_name") -> Create unknown wavenumber
    - Wavenumber(value, "unit", "variable_name") -> Create known wavenumber
    
    Examples:
    ---------
    >>> unknown = Wavenumber("pressure")  # Unknown wavenumber
    >>> known = Wavenumber(100, "diopter", "inlet_pressure")  # Known wavenumber
    
    Available units: "diopter", "kayser", "reciprocal_meter"
    """
    __slots__ = ()
    _setter_class = ts.WavenumberSetter
    _expected_dimension = dim.WAVENUMBER
    
    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True): ...
    
    def set(self, value: int | float) -> ts.WavenumberSetter:
        """
        Create a setter for this wavenumber quantity.
        
        Args:
            value: The numeric value to set
        
        Returns:
            WavenumberSetter: A setter with unit properties like .meters, .inches, etc.
        
        Example:
            >>> length = Length("beam_length")
            >>> length.set(100).millimeters  # Sets to 100 mm
        """
        ...
    

# All quantity classes are defined above
# Setter classes are defined in setters.pyi
