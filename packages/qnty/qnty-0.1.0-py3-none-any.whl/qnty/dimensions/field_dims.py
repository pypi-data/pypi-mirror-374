"""
Dimension System
================

Compile-time dimensional analysis using type system for ultra-fast operations.

This file contains dimension constants for all engineering fields.
"""

from .signature import DimensionSignature

# Dimension signature constants - computed from prime factorization
_SIGNATURES: dict[str, int | float] = {
    "ABSORBED_DOSE": 0.16,  # L^2 T^-2
    "ACCELERATION": 0.08,  # L T^-2
    "ACTIVATION_ENERGY": 0.01230769231,  # N^-1 L^2 T^-2
    "AMOUNT_OF_SUBSTANCE": 13,  # N
    "ANGLE_PLANE": 1,  # Dimensionless
    "ANGLE_SOLID": 1,  # Dimensionless
    "ANGULAR_ACCELERATION": 0.04,  # T^-2
    "ANGULAR_MOMENTUM": 2.4,  # L^2 M T^-1
    "AREA": 4,  # L^2
    "AREA_PER_UNIT_VOLUME": 0.5,  # L^-1
    "ATOMIC_WEIGHT": 0.2307692308,  # N^-1 M
    "CONCENTRATION": 0.375,  # L^-3 M
    "DIMENSIONLESS": 1,  # Dimensionless
    "DYNAMIC_FLUIDITY": 3.333333333,  # L M^-1 T
    "ELECTRIC_CAPACITANCE": 2552.083333,  # A^2 L^-2 M^-1 T^4
    "ELECTRIC_CHARGE": 2.692307692,  # N^-1 A T
    "ELECTRIC_CURRENT_INTENSITY": 7,  # A
    "ELECTRIC_DIPOLE_MOMENT": 70,  # A L T
    "ELECTRIC_FIELD_STRENGTH": 0.006857142857,  # A^-1 L M T^-3
    "ELECTRIC_INDUCTANCE": 0.009795918367,  # A^-2 L^2 M T^-2
    "ELECTRIC_POTENTIAL": 0.01371428571,  # A^-1 L^2 M T^-3
    "ELECTRIC_RESISTANCE": 0.001959183673,  # A^-2 L^2 M T^-3
    "ELECTRICAL_CONDUCTANCE": 510.4166667,  # A^2 L^-2 M^-1 T^3
    "ELECTRICAL_PERMITTIVITY": 1276.041667,  # A^2 L^-3 M^-1 T^4
    "ELECTRICAL_RESISTIVITY": 0.003918367347,  # A^-2 L^3 M T^-3
    "ENERGY_FLUX": 0.024,  # M T^-3
    "ENERGY_HEAT_WORK": 0.48,  # L^2 M T^-2
    "ENERGY_PER_UNIT_AREA": 0.12,  # M T^-2
    "FORCE": 0.24,  # L M T^-2
    "FORCE_BODY": 0.03,  # L^-2 M T^-2
    "FORCE_PER_UNIT_MASS": 0.08,  # L T^-2
    "FREQUENCY_VOLTAGE_RATIO": 72.91666667,  # A L^-2 M^-1 T^3
    "FUEL_CONSUMPTION": 0.25,  # L^-2
    "HEAT_OF_COMBUSTION": 0.16,  # L^2 T^-2
    "HEAT_OF_FUSION": 0.16,  # L^2 T^-2
    "HEAT_OF_VAPORIZATION": 0.16,  # L^2 T^-2
    "HEAT_TRANSFER_COEFFICIENT": 0.002181818182,  # M Θ^-1 T^-3
    "ILLUMINANCE": 0.25,  # L^-2 L
    "KINETIC_ENERGY_OF_TURBULENCE": 0.16,  # L^2 T^-2
    "LENGTH": 2,  # L
    "LINEAR_MASS_DENSITY": 1.5,  # L^-1 M
    "LINEAR_MOMENTUM": 1.2,  # L M T^-1
    "LUMINANCE_SELF": 0.25,  # L^-2 L
    "LUMINOUS_FLUX": 1,  # L
    "LUMINOUS_INTENSITY": 1,  # L
    "MAGNETIC_FIELD": 3.5,  # A L^-1
    "MAGNETIC_FLUX": 0.06857142857,  # A^-1 L^2 M T^-2
    "MAGNETIC_INDUCTION_FIELD_STRENGTH": 0.01714285714,  # A^-1 M T^-2
    "MAGNETIC_MOMENT": 28,  # A L^2
    "MAGNETIC_PERMEABILITY": 0.009795918367,  # A^-2 L^2 M T^-2
    "MAGNETOMOTIVE_FORCE": 7,  # A
    "MASS": 3,  # M
    "MASS_DENSITY": 0.375,  # L^-3 M
    "MASS_FLOW_RATE": 0.6,  # M T^-1
    "MASS_FLUX": 0.15,  # L^-2 M T^-1
    "MASS_FRACTION_OF_I": 1,  # Dimensionless
    "MASS_TRANSFER_COEFFICIENT": 0.15,  # L^-2 M T^-1
    "MOLALITY_OF_SOLUTE_I": 4.333333333,  # N M^-1
    "MOLAR_CONCENTRATION_BY_MASS": 13,  # N
    "MOLAR_FLOW_RATE": 2.6,  # N T^-1
    "MOLAR_FLUX": 0.65,  # N L^-2 T^-1
    "MOLAR_HEAT_CAPACITY": 0.001118881119,  # N^-1 L^2 Θ^-1 T^-2
    "MOLARITY_OF_I": 1.625,  # N L^-3
    "MOLE_FRACTION_OF_I": 1,  # Dimensionless
    "MOMENT_OF_INERTIA": 12,  # L^2 M
    "MOMENTUM_FLOW_RATE": 0.24,  # L M T^-2
    "MOMENTUM_FLUX": 0.06,  # L^-1 M T^-2
    "NORMALITY_OF_SOLUTION": 1.625,  # N L^-3
    "PARTICLE_DENSITY": 0.125,  # L^-3
    "PERCENT": 1,  # Dimensionless
    "PERMEABILITY": 4,  # L^2
    "PHOTON_EMISSION_RATE": 0.05,  # L^-2 T^-1
    "POWER_PER_UNIT_MASS": 0.032,  # L^2 T^-3
    "POWER_PER_UNIT_VOLUME": 0.012,  # L^-1 M T^-3
    "POWER_THERMAL_DUTY": 0.096,  # L^2 M T^-3
    "PRESSURE": 0.06,  # L^-1 M T^-2
    "RADIATION_DOSE_EQUIVALENT": 0.16,  # L^2 T^-2
    "RADIATION_EXPOSURE": 11.66666667,  # A M^-1 T
    "RADIOACTIVITY": 0.2,  # T^-1
    "SECOND_MOMENT_OF_AREA": 16,  # L^4
    "SECOND_RADIATION_CONSTANT_PLANCK": 22,  # L Θ
    "SPECIFIC_ENTHALPY": 0.16,  # L^2 T^-2
    "SPECIFIC_GRAVITY": 1,  # Dimensionless
    "SPECIFIC_HEAT_CAPACITY_CONSTANT_PRESSURE": 0.04363636364,  # L^2 M Θ^-1 T^-2
    "SPECIFIC_LENGTH": 0.6666666667,  # L M^-1
    "SPECIFIC_SURFACE": 1.333333333,  # L^2 M^-1
    "SPECIFIC_VOLUME": 2.666666667,  # L^3 M^-1
    "STRESS": 0.06,  # L^-1 M T^-2
    "SURFACE_MASS_DENSITY": 0.75,  # L^-2 M
    "SURFACE_TENSION": 0.12,  # M T^-2
    "TEMPERATURE": 11,  # Θ
    "THERMAL_CONDUCTIVITY": 0.528,  # L M Θ T^-3
    "TIME": 5,  # T
    "TORQUE": 0.48,  # L^2 M T^-2
    "TURBULENCE_ENERGY_DISSIPATION_RATE": 0.032,  # L^2 T^-3
    "VELOCITY_ANGULAR": 0.2,  # T^-1
    "VELOCITY_LINEAR": 0.4,  # L T^-1
    "VISCOSITY_DYNAMIC": 0.3,  # L^-1 M T^-1
    "VISCOSITY_KINEMATIC": 0.8,  # L^2 T^-1
    "VOLUME": 8,  # L^3
    "VOLUME_FRACTION_OF_I": 1,  # Dimensionless
    "VOLUMETRIC_CALORIFIC_HEATING_VALUE": 0.06,  # L^-1 M T^-2
    "VOLUMETRIC_COEFFICIENT_OF_EXPANSION": 0.03409090909,  # L^-3 M Θ^-1
    "VOLUMETRIC_FLOW_RATE": 1.6,  # L^3 T^-1
    "VOLUMETRIC_FLUX": 0.4,  # L T^-1
    "VOLUMETRIC_MASS_FLOW_RATE": 0.075,  # L^-3 M T^-1
    "WAVENUMBER": 0.5,  # L^-1
}

# Generate all dimension constants programmatically to avoid duplication
for _name, _signature in _SIGNATURES.items():
    globals()[_name] = DimensionSignature(_signature)

