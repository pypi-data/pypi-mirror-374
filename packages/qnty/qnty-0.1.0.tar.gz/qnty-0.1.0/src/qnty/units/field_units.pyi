"""Type stubs for field units."""

from .registry import UnitConstant


class AbsorbedDoseUnits:
    """Unit constants for Absorbed Radiation Dose."""
    __slots__: tuple[()]

    erg_per_gram: UnitConstant
    erg_g: UnitConstant
    erg_per_g: UnitConstant
    gram_rad: UnitConstant
    g_rad: UnitConstant
    gray: UnitConstant
    Gy: UnitConstant
    rad: UnitConstant
    milligray: UnitConstant
    mGy: UnitConstant
    microgray: UnitConstant

class AccelerationUnits:
    """Unit constants for Acceleration."""
    __slots__: tuple[()]

    meter_per_second_squared: UnitConstant
    mathrm_m_mathrm_s_2: UnitConstant
    m_per_s2: UnitConstant
    foot_per_second_squared: UnitConstant
    mathrm_ft_mathrm_s_2_or_mathrm_ft_mathrm_sec_2: UnitConstant
    ft_per_s2: UnitConstant
    fps2: UnitConstant

class ActivationEnergyUnits:
    """Unit constants for Activation Energy."""
    __slots__: tuple[()]

    btu_per_pound_mole: UnitConstant
    Btu_lb_mol: UnitConstant
    btu_per_lbmol: UnitConstant
    calorie_mean_per_gram_mole: UnitConstant
    cal_mol: UnitConstant
    cal_mean_per_gmol: UnitConstant
    joule_per_gram_mole: UnitConstant
    J_mol: UnitConstant
    joule_per_kilogram_mole: UnitConstant
    J_kmol: UnitConstant
    kilocalorie_per_kilogram_mole: UnitConstant
    kcal_kmol: UnitConstant

class AmountOfSubstanceUnits:
    """Unit constants for Amount of Substance."""
    __slots__: tuple[()]

    kilogram_mol: UnitConstant
    kmol: UnitConstant
    mole: UnitConstant
    mol: UnitConstant
    pound_mole: UnitConstant
    lb_mol_or_mole: UnitConstant
    lb_mol: UnitConstant
    mole: UnitConstant
    millimole: UnitConstant
    mmol: UnitConstant
    micromole: UnitConstant

class AnglePlaneUnits:
    """Unit constants for Angle, Plane."""
    __slots__: tuple[()]

    degree: UnitConstant
    circ: UnitConstant
    gon: UnitConstant
    grade: UnitConstant
    minute_new: UnitConstant
    c: UnitConstant
    minute_of_angle: UnitConstant
    unnamed: UnitConstant
    percent: UnitConstant
    plane_angle: UnitConstant
    quadrant: UnitConstant
    quadr: UnitConstant
    radian: UnitConstant
    rad: UnitConstant
    right_angle: UnitConstant
    perp: UnitConstant
    round: UnitConstant
    tr_or_r: UnitConstant
    tr: UnitConstant
    r: UnitConstant
    second_new: UnitConstant
    cc: UnitConstant
    second_of_angle: UnitConstant
    thousandth_us: UnitConstant
    US: UnitConstant
    turn: UnitConstant
    turn_or_rev: UnitConstant
    rev: UnitConstant

class AngleSolidUnits:
    """Unit constants for Angle, Solid."""
    __slots__: tuple[()]

    spat: UnitConstant
    square_degree: UnitConstant
    left_circ_right_2: UnitConstant
    square_gon: UnitConstant
    g_2: UnitConstant
    steradian: UnitConstant
    sr: UnitConstant

class AngularAccelerationUnits:
    """Unit constants for Angular Acceleration."""
    __slots__: tuple[()]

    radian_per_second_squared: UnitConstant
    mathrm_rad_mathrm_s_2: UnitConstant
    revolution_per_second_squared: UnitConstant
    mathrm_rev_mathrm_sec_2: UnitConstant
    rpm_or_revolution_per_minute: UnitConstant
    mathrm_rev_mathrm_min_2_or_rpm_min: UnitConstant
    rev_min_2: UnitConstant
    rpm_min: UnitConstant

class AngularMomentumUnits:
    """Unit constants for Angular Momentum."""
    __slots__: tuple[()]

    gram_centimeter_squared_per_second: UnitConstant
    mathrm_g_mathrm_cm_2_mathrm_s: UnitConstant
    kilogram_meter_squared_per_second: UnitConstant
    mathrm_kg_mathrm_m_2_mathrm_s: UnitConstant
    pound_force_square_foot_per_second: UnitConstant
    lb_ft_2_mathrm_sec: UnitConstant

class AreaUnits:
    """Unit constants for Area."""
    __slots__: tuple[()]

    acre_general: UnitConstant
    ac: UnitConstant
    are: UnitConstant
    a: UnitConstant
    arpent_quebec: UnitConstant
    arp: UnitConstant
    barn: UnitConstant
    b: UnitConstant
    circular_inch: UnitConstant
    cin: UnitConstant
    circular_mil: UnitConstant
    cmil: UnitConstant
    hectare: UnitConstant
    ha: UnitConstant
    shed: UnitConstant
    square_centimeter: UnitConstant
    mathrm_cm_2: UnitConstant
    square_chain_ramsden: UnitConstant
    sq_ch_Rams: UnitConstant
    square_chain_survey_gunters: UnitConstant
    sq_ch_surv: UnitConstant
    square_decimeter: UnitConstant
    mathrm_dm_2: UnitConstant
    square_fermi: UnitConstant
    mathrm_F_2: UnitConstant
    square_foot: UnitConstant
    sq_ft_or_ft_2: UnitConstant
    sq_ft: UnitConstant
    ft_2: UnitConstant
    square_hectometer: UnitConstant
    mathrm_hm_2: UnitConstant
    square_inch: UnitConstant
    sq_in_or_in_2: UnitConstant
    sq_in: UnitConstant
    in_2: UnitConstant
    square_kilometer: UnitConstant
    mathrm_km_2: UnitConstant
    square_league_statute: UnitConstant
    sq_lg_stat: UnitConstant
    square_meter: UnitConstant
    mathrm_m_2: UnitConstant
    square_micron: UnitConstant
    mu_mathrm_m_2_or_mu_2: UnitConstant
    mu_m_2: UnitConstant
    mu_2: UnitConstant
    square_mile_statute: UnitConstant
    sq_mi_stat: UnitConstant
    square_mile_us_survey: UnitConstant
    sq_mi_US_Surv: UnitConstant
    square_millimeter: UnitConstant
    mathrm_mm_2: UnitConstant
    square_nanometer: UnitConstant
    mathrm_nm_2: UnitConstant
    square_yard: UnitConstant
    sq_yd: UnitConstant
    township_us: UnitConstant
    twshp: UnitConstant

class AreaPerUnitVolumeUnits:
    """Unit constants for Area per Unit Volume."""
    __slots__: tuple[()]

    square_centimeter_per_cubic_centimeter: UnitConstant
    mathrm_cm_2_mathrm_cc: UnitConstant
    square_foot_per_cubic_foot: UnitConstant
    mathrm_ft_2_mathrm_ft_3_or_sqft_cft: UnitConstant
    ft_2_ft_3: UnitConstant
    sqft_cft: UnitConstant
    square_inch_per_cubic_inch: UnitConstant
    mathrm_in_2_mathrm_in_3_or_sq_in_cu_in: UnitConstant
    in_2_in_3: UnitConstant
    sq_in_cu_in: UnitConstant
    square_meter_per_cubic_meter: UnitConstant
    mathrm_m_2_mathrm_m_3_or_1_mathrm_m_3: UnitConstant
    m_2_m_3: UnitConstant
    unit_1_m_3: UnitConstant

class AtomicWeightUnits:
    """Unit constants for Atomic Weight."""
    __slots__: tuple[()]

    atomic_mass_unit_12c: UnitConstant
    amu: UnitConstant
    grams_per_mole: UnitConstant
    g_mol: UnitConstant
    kilograms_per_kilomole: UnitConstant
    kg_kmol: UnitConstant
    pounds_per_pound_mole: UnitConstant
    mathrm_lb_mathrm_lb_mol_or_mathrm_lb_mole: UnitConstant
    lb_lb_mol: UnitConstant
    lb_mole: UnitConstant

class ConcentrationUnits:
    """Unit constants for Concentration."""
    __slots__: tuple[()]

    grains_of_i_per_cubic_foot: UnitConstant
    mathrm_gr_mathrm_ft_3_or_gr_cft: UnitConstant
    gr_ft_3: UnitConstant
    gr_cft: UnitConstant
    grains_of_i_per_gallon_us: UnitConstant
    gr_gal: UnitConstant

class DimensionlessUnits:
    """Unit constants for Dimensionless."""
    __slots__: tuple[()]

    dimensionless: UnitConstant
    ratio: UnitConstant
    parts_per_million: UnitConstant
    ppm: UnitConstant
    parts_per_billion: UnitConstant
    ppb: UnitConstant

class DynamicFluidityUnits:
    """Unit constants for Dynamic Fluidity."""
    __slots__: tuple[()]

    meter_seconds_per_kilogram: UnitConstant
    m_s_kg: UnitConstant
    rhe: UnitConstant
    square_foot_per_pound_second: UnitConstant
    mathrm_ft_2_lb_sec: UnitConstant
    square_meters_per_newton_per_second: UnitConstant
    mathrm_m_2_mathrm_N_mathrm_s: UnitConstant

class ElectricCapacitanceUnits:
    """Unit constants for Electric Capacitance."""
    __slots__: tuple[()]

    cm: UnitConstant
    abfarad: UnitConstant
    emu_cgs: UnitConstant
    farad: UnitConstant
    F: UnitConstant
    farad_intl: UnitConstant
    F_int: UnitConstant
    jar: UnitConstant
    puff: UnitConstant
    statfarad: UnitConstant
    esu_cgs: UnitConstant
    millifarad: UnitConstant
    mF: UnitConstant
    microfarad: UnitConstant
    nanofarad: UnitConstant
    nF: UnitConstant
    picofarad: UnitConstant
    pF: UnitConstant

class ElectricChargeUnits:
    """Unit constants for Electric Charge."""
    __slots__: tuple[()]

    abcoulomb: UnitConstant
    ampere_hour: UnitConstant
    Ah: UnitConstant
    coulomb: UnitConstant
    C: UnitConstant
    faraday_c12: UnitConstant
    franklin: UnitConstant
    Fr: UnitConstant
    statcoulomb: UnitConstant
    u_a_charge: UnitConstant
    u_a: UnitConstant
    kilocoulomb: UnitConstant
    kC: UnitConstant
    millicoulomb: UnitConstant
    mC: UnitConstant
    microcoulomb: UnitConstant
    nanocoulomb: UnitConstant
    nC: UnitConstant
    picocoulomb: UnitConstant
    pC: UnitConstant

class ElectricCurrentIntensityUnits:
    """Unit constants for Electric Current Intensity."""
    __slots__: tuple[()]

    abampere: UnitConstant
    ampere_intl_mean: UnitConstant
    A_int_mean: UnitConstant
    ampere_intl_us: UnitConstant
    A_int_US: UnitConstant
    ampere_or_amp: UnitConstant
    A: UnitConstant
    biot: UnitConstant
    statampere: UnitConstant
    u_a_or_current: UnitConstant

class ElectricDipoleMomentUnits:
    """Unit constants for Electric Dipole Moment."""
    __slots__: tuple[()]

    ampere_meter_second: UnitConstant
    A_m_s: UnitConstant
    coulomb_meter: UnitConstant
    C_m: UnitConstant
    debye: UnitConstant
    D: UnitConstant
    electron_meter: UnitConstant
    e_m: UnitConstant

class ElectricFieldStrengthUnits:
    """Unit constants for Electric Field Strength."""
    __slots__: tuple[()]

    volt_per_centimeter: UnitConstant
    V_cm: UnitConstant
    volt_per_meter: UnitConstant
    V_m: UnitConstant

class ElectricInductanceUnits:
    """Unit constants for Electric Inductance."""
    __slots__: tuple[()]

    abhenry: UnitConstant
    cm: UnitConstant
    henry: UnitConstant
    H: UnitConstant
    henry_intl_mean: UnitConstant
    H_int_mean: UnitConstant
    henry_intl_us: UnitConstant
    H_int_US: UnitConstant
    mic: UnitConstant
    stathenry: UnitConstant
    millihenry: UnitConstant
    mH: UnitConstant
    microhenry: UnitConstant
    nanohenry: UnitConstant
    nH: UnitConstant

class ElectricPotentialUnits:
    """Unit constants for Electric Potential."""
    __slots__: tuple[()]

    abvolt: UnitConstant
    statvolt: UnitConstant
    u_a_potential: UnitConstant
    volt: UnitConstant
    V: UnitConstant
    volt_intl_mean: UnitConstant
    V_int_mean: UnitConstant
    volt_us: UnitConstant
    V_int_US: UnitConstant
    kilovolt: UnitConstant
    kV: UnitConstant
    millivolt: UnitConstant
    mV: UnitConstant
    microvolt: UnitConstant
    nanovolt: UnitConstant
    nV: UnitConstant
    picovolt: UnitConstant
    pV: UnitConstant

class ElectricResistanceUnits:
    """Unit constants for Electric Resistance."""
    __slots__: tuple[()]

    abohm: UnitConstant
    jacobi: UnitConstant
    lenz: UnitConstant
    Metric: UnitConstant
    ohm: UnitConstant
    Omega: UnitConstant
    ohm_intl_mean: UnitConstant
    Omega_int_mean: UnitConstant
    ohm_intl_us: UnitConstant
    Omega_int_US: UnitConstant
    ohm_legal: UnitConstant
    Omega_legal: UnitConstant
    preece: UnitConstant
    statohm: UnitConstant
    csu_cgs: UnitConstant
    wheatstone: UnitConstant
    kiloohm: UnitConstant
    k_Omega: UnitConstant
    megaohm: UnitConstant
    M_Omega: UnitConstant
    milliohm: UnitConstant
    m_Omega: UnitConstant

class ElectricalConductanceUnits:
    """Unit constants for Electrical Conductance."""
    __slots__: tuple[()]

    emu_cgs: UnitConstant
    abmho: UnitConstant
    esu_cgs: UnitConstant
    statmho: UnitConstant
    mho: UnitConstant
    microsiemens: UnitConstant
    mu_mathrm_S: UnitConstant
    siemens: UnitConstant
    S: UnitConstant
    millisiemens: UnitConstant
    mS: UnitConstant

class ElectricalPermittivityUnits:
    """Unit constants for Electrical Permittivity."""
    __slots__: tuple[()]

    farad_per_meter: UnitConstant
    F_m: UnitConstant

class ElectricalResistivityUnits:
    """Unit constants for Electrical Resistivity."""
    __slots__: tuple[()]

    circular_mil_ohm_per_foot: UnitConstant
    circmil_Omega_mathrm_ft: UnitConstant
    emu_cgs: UnitConstant
    abohm_cm: UnitConstant
    microhm_inch: UnitConstant
    mu_Omega_in: UnitConstant
    ohm_centimeter: UnitConstant
    boldsymbol_Omega_mathbf_c_m: UnitConstant
    ohm_meter: UnitConstant
    Omega_mathrm_m: UnitConstant

class EnergyFluxUnits:
    """Unit constants for Energy Flux."""
    __slots__: tuple[()]

    btu_per_square_foot_per_hour: UnitConstant
    mathrm_Btu_mathrm_ft_2_mathrm_hr: UnitConstant
    calorie_per_square_centimeter_per_second: UnitConstant
    mathrm_cal_mathrm_cm_2_mathrm_s_or_mathrm_cal_mathrm_cm_2_mathrm_s: UnitConstant
    cal_cm_2_s: UnitConstant
    celsius_heat_units_chu: UnitConstant
    mathrm_Chu_mathrm_ft_2_mathrm_hr: UnitConstant
    kilocalorie_per_square_foot_per_hour: UnitConstant
    mathrm_kcal_left_mathrm_ft_2_mathrm_hr_right: UnitConstant
    kilocalorie_per_square_meter_per_hour: UnitConstant
    mathrm_kcal_left_mathrm_m_2_mathrm_hr_right: UnitConstant
    watt_per_square_meter: UnitConstant
    mathrm_W_mathrm_m_2: UnitConstant

class EnergyHeatWorkUnits:
    """Unit constants for Energy, Heat, Work."""
    __slots__: tuple[()]

    barrel_oil_equivalent_or_equivalent_barrel: UnitConstant
    bboe_or_boe: UnitConstant
    bboe: UnitConstant
    boe: UnitConstant
    billion_electronvolt: UnitConstant
    BeV: UnitConstant
    british_thermal_unit_4circ_mathrmc: UnitConstant
    Btu_39_2_circ_mathrm_F: UnitConstant
    british_thermal_unit_60circ_mathrmf: UnitConstant
    Btu_60_circ_mathrm_F: UnitConstant
    british_thermal_unit_international_steam_tables: UnitConstant
    Btu_IT: UnitConstant
    british_thermal_unit_isotc_12: UnitConstant
    Btu_ISO: UnitConstant
    british_thermal_unit_mean: UnitConstant
    Btu_mean_or_Btu: UnitConstant
    Btu_mean: UnitConstant
    Btu: UnitConstant
    british_thermal_unit_thermochemical: UnitConstant
    Btu_therm: UnitConstant
    calorie_20circ_mathrmc: UnitConstant
    cal_20_circ_mathrm_C: UnitConstant
    calorie_4circ_mathrmc: UnitConstant
    cal_4_circ_mathrm_C: UnitConstant
    calorie_international_steam_tables: UnitConstant
    cal_IT: UnitConstant
    calorie_mean: UnitConstant
    cal_mean: UnitConstant
    calorie_nutritional: UnitConstant
    Cal_nutr: UnitConstant
    calorie_thermochemical: UnitConstant
    cal_therm: UnitConstant
    celsius_heat_unit: UnitConstant
    Chu: UnitConstant
    celsius_heat_unit_15_circ_mathrmc: UnitConstant
    Chu_15_circ_mathrm_C: UnitConstant
    electron_volt: UnitConstant
    eV: UnitConstant
    erg: UnitConstant
    foot_pound_force_duty: UnitConstant
    ft_mathrm_lb_mathrm_f: UnitConstant
    foot_poundal: UnitConstant
    ft_pdl: UnitConstant
    frigorie: UnitConstant
    fg: UnitConstant
    hartree_atomic_unit_of_energy: UnitConstant
    mathrm_E_mathrm_H_a_u: UnitConstant
    joule: UnitConstant
    J: UnitConstant
    joule_international: UnitConstant
    J_intl: UnitConstant
    kilocalorie_thermal: UnitConstant
    kcal_therm: UnitConstant
    kilogram_force_meter: UnitConstant
    mathrm_kg_mathrm_f_m: UnitConstant
    kiloton_tnt: UnitConstant
    kt_TNT: UnitConstant
    kilowatt_hour: UnitConstant
    kWh: UnitConstant
    liter_atmosphere: UnitConstant
    L_atm: UnitConstant
    megaton_tnt: UnitConstant
    Mt_TNT: UnitConstant
    pound_centigrade_unit_15circ_mathrmc: UnitConstant
    pcu_15_circ_mathrm_C: UnitConstant
    prout: UnitConstant
    q_unit: UnitConstant
    Q: UnitConstant
    quad_quadrillion_btu: UnitConstant
    quad: UnitConstant
    rydberg: UnitConstant
    Ry: UnitConstant
    therm_eeg: UnitConstant
    therm_EEG: UnitConstant
    therm_refineries: UnitConstant
    therm_refy_or_therm: UnitConstant
    therm_refy: UnitConstant
    therm: UnitConstant
    therm_us: UnitConstant
    therm_US_or_therm: UnitConstant
    ton_coal_equivalent: UnitConstant
    tce_tec: UnitConstant
    ton_oil_equivalent: UnitConstant
    toe_tep: UnitConstant
    kilojoule: UnitConstant
    kJ: UnitConstant
    megajoule: UnitConstant
    MJ: UnitConstant
    gigajoule: UnitConstant
    GJ: UnitConstant

class EnergyPerUnitAreaUnits:
    """Unit constants for Energy per Unit Area."""
    __slots__: tuple[()]

    british_thermal_unit_per_square_foot: UnitConstant
    mathrm_Btu_mathrm_ft_2_or_Btu_sq_ft: UnitConstant
    Btu_ft_2: UnitConstant
    Btu_sq_ft: UnitConstant
    joule_per_square_meter: UnitConstant
    mathrm_J_mathrm_m_2: UnitConstant
    langley: UnitConstant
    Ly: UnitConstant

class ForceUnits:
    """Unit constants for Force."""
    __slots__: tuple[()]

    crinal: UnitConstant
    dyne: UnitConstant
    dyn: UnitConstant
    funal: UnitConstant
    kilogram_force: UnitConstant
    mathrm_kg_mathrm_f: UnitConstant
    kip_force: UnitConstant
    operatorname_kip_mathrm_f: UnitConstant
    newton: UnitConstant
    N: UnitConstant
    ounce_force: UnitConstant
    mathrm_oz_mathrm_f_or_oz: UnitConstant
    oz_f: UnitConstant
    oz: UnitConstant
    pond: UnitConstant
    p: UnitConstant
    pound_force: UnitConstant
    mathrm_lb_mathrm_f_or_lb: UnitConstant
    lb_f: UnitConstant
    lb: UnitConstant
    poundal: UnitConstant
    pdl: UnitConstant
    slug_force: UnitConstant
    operatorname_slug_f: UnitConstant
    sth_ne: UnitConstant
    sn: UnitConstant
    ton_force_long: UnitConstant
    LT: UnitConstant
    ton_force_metric: UnitConstant
    MT: UnitConstant
    ton_force_short: UnitConstant
    T: UnitConstant
    kilonewton: UnitConstant
    kN: UnitConstant
    millinewton: UnitConstant
    mN: UnitConstant

class ForceBodyUnits:
    """Unit constants for Force (Body)."""
    __slots__: tuple[()]

    dyne_per_cubic_centimeter: UnitConstant
    dyn_cc_or_dyn_mathrm_cm_3: UnitConstant
    dyn_cc: UnitConstant
    dyn_cm_3: UnitConstant
    kilogram_force_per_cubic_centimeter: UnitConstant
    mathrm_kg_mathrm_f_mathrm_cm_3: UnitConstant
    kilogram_force_per_cubic_meter: UnitConstant
    mathrm_kg_mathrm_f_mathrm_m_3: UnitConstant
    newton_per_cubic_meter: UnitConstant
    mathrm_N_mathrm_m_3: UnitConstant
    pound_force_per_cubic_foot: UnitConstant
    mathrm_lb_mathrm_f_mathrm_cft: UnitConstant
    pound_force_per_cubic_inch: UnitConstant
    mathrm_lb_mathrm_f_mathrm_cu_mathrm_in: UnitConstant
    ton_force_per_cubic_foot: UnitConstant
    ton_mathrm_f_mathrm_cft: UnitConstant

class ForcePerUnitMassUnits:
    """Unit constants for Force per Unit Mass."""
    __slots__: tuple[()]

    dyne_per_gram: UnitConstant
    dyn_g: UnitConstant
    kilogram_force_per_kilogram: UnitConstant
    mathrm_kg_mathrm_f_mathrm_kg: UnitConstant
    newton_per_kilogram: UnitConstant
    N_kg: UnitConstant
    pound_force_per_pound_mass: UnitConstant
    mathrm_lb_mathrm_f_mathrm_lb_or_mathrm_lb_mathrm_f_mathrm_lb_mathrm_m: UnitConstant
    lb_f_lb: UnitConstant
    lb_f_lb_m: UnitConstant
    pound_force_per_slug: UnitConstant
    mathrm_lb_mathrm_f_slug: UnitConstant

class FrequencyVoltageRatioUnits:
    """Unit constants for Frequency Voltage Ratio."""
    __slots__: tuple[()]

    cycles_per_second_per_volt: UnitConstant
    cycle_sec_V: UnitConstant
    hertz_per_volt: UnitConstant
    Hz_V: UnitConstant
    terahertz_per_volt: UnitConstant
    THz_V: UnitConstant

class FuelConsumptionUnits:
    """Unit constants for Fuel Consumption."""
    __slots__: tuple[()]

    unit_100_km_per_liter: UnitConstant
    gallons_uk: UnitConstant
    gal_UK_100_mi: UnitConstant
    gallons_us: UnitConstant
    gal_US_100_mi: UnitConstant
    kilometers_per_gallon_uk: UnitConstant
    km_gal_UK: UnitConstant
    kilometers_per_gallon_us: UnitConstant
    km_gal_US: UnitConstant
    kilometers_per_liter: UnitConstant
    km_l: UnitConstant
    liters_per_100_km: UnitConstant
    liters_per_kilometer: UnitConstant
    unit_1_km: UnitConstant
    meters_per_gallon_uk: UnitConstant
    m_gal_UK: UnitConstant
    meters_per_gallon_us: UnitConstant
    unit_1_gal_US: UnitConstant
    miles_per_gallon_uk: UnitConstant
    mi_gal_UK_or_mpg_UK: UnitConstant
    mi_gal_UK: UnitConstant
    mpg_UK: UnitConstant
    miles_per_gallon_us: UnitConstant
    mi_gal_US_or_mpg_US: UnitConstant
    mi_gal_US: UnitConstant
    mpg_US: UnitConstant
    miles_per_liter: UnitConstant
    mi_l: UnitConstant

class HeatOfCombustionUnits:
    """Unit constants for Heat of Combustion."""
    __slots__: tuple[()]

    british_thermal_unit_per_pound: UnitConstant
    Btu_lb: UnitConstant
    calorie_per_gram: UnitConstant
    mathrm_cal_mathrm_g: UnitConstant
    chu_per_pound: UnitConstant
    Chu_lb: UnitConstant
    joule_per_kilogram: UnitConstant
    J_kg: UnitConstant

class HeatOfFusionUnits:
    """Unit constants for Heat of Fusion."""
    __slots__: tuple[()]

    british_thermal_unit_mean: UnitConstant
    Btu_mean_lb: UnitConstant
    british_thermal_unit_per_pound: UnitConstant
    calorie_per_gram: UnitConstant
    chu_per_pound: UnitConstant
    joule_per_kilogram: UnitConstant

class HeatOfVaporizationUnits:
    """Unit constants for Heat of Vaporization."""
    __slots__: tuple[()]

    british_thermal_unit_per_pound: UnitConstant
    calorie_per_gram: UnitConstant
    chu_per_pound: UnitConstant
    joule_per_kilogram: UnitConstant

class HeatTransferCoefficientUnits:
    """Unit constants for Heat Transfer Coefficient."""
    __slots__: tuple[()]

    btu_per_square_foot_per_hour_per_degree_fahrenheit_or_rankine: UnitConstant
    mathrm_Btu_left_mathrm_ft_2_mathrm_h_circ_mathrm_F_right: UnitConstant
    watt_per_square_meter_per_degree_celsius_or_kelvin: UnitConstant
    mathrm_W_left_mathrm_m_2_circ_mathrm_C_right: UnitConstant

class IlluminanceUnits:
    """Unit constants for Illuminance."""
    __slots__: tuple[()]

    foot_candle: UnitConstant
    mathrm_ft_mathrm_C_or_mathrm_ft_mathrm_Cd: UnitConstant
    ft_C: UnitConstant
    ft_Cd: UnitConstant
    lux: UnitConstant
    lx: UnitConstant
    nox: UnitConstant
    phot: UnitConstant
    ph: UnitConstant
    skot: UnitConstant

class KineticEnergyOfTurbulenceUnits:
    """Unit constants for Kinetic Energy of Turbulence."""
    __slots__: tuple[()]

    square_foot_per_second_squared: UnitConstant
    mathrm_ft_2_mathrm_s_2_or_sqft_sec_2: UnitConstant
    ft_2_s_2: UnitConstant
    sqft_sec_2: UnitConstant
    square_meters_per_second_squared: UnitConstant
    mathrm_m_2_mathrm_s_2: UnitConstant

class LengthUnits:
    """Unit constants for Length."""
    __slots__: tuple[()]

    ngstr_m: UnitConstant
    AA: UnitConstant
    arpent_quebec: UnitConstant
    astronomic_unit: UnitConstant
    AU: UnitConstant
    attometer: UnitConstant
    am: UnitConstant
    calibre_centinch: UnitConstant
    centimeter: UnitConstant
    cm: UnitConstant
    chain_engrs_or_ramsden: UnitConstant
    ch_eng_or_Rams: UnitConstant
    ch_eng: UnitConstant
    Rams: UnitConstant
    chain_gunters: UnitConstant
    ch_Gunt: UnitConstant
    chain_surveyors: UnitConstant
    ch_surv: UnitConstant
    cubit_uk: UnitConstant
    cu_UK: UnitConstant
    ell: UnitConstant
    fathom: UnitConstant
    fath: UnitConstant
    femtometre: UnitConstant
    fm: UnitConstant
    fermi: UnitConstant
    foot: UnitConstant
    ft: UnitConstant
    furlong_uk_and_us: UnitConstant
    fur: UnitConstant
    inch: UnitConstant
    in_unit: UnitConstant
    kilometer: UnitConstant
    km: UnitConstant
    league_us_statute: UnitConstant
    lg_US_stat: UnitConstant
    lieue_metric: UnitConstant
    ligne_metric: UnitConstant
    line_us: UnitConstant
    li_US: UnitConstant
    link_surveyors: UnitConstant
    li_surv: UnitConstant
    meter: UnitConstant
    m: UnitConstant
    micrometer: UnitConstant
    mu_mathrm_m: UnitConstant
    micron: UnitConstant
    mu: UnitConstant
    mil: UnitConstant
    mile_geographical: UnitConstant
    mi: UnitConstant
    mile_us_nautical: UnitConstant
    mi_US_naut: UnitConstant
    mile_us_statute: UnitConstant
    mile_us_survey: UnitConstant
    mi_US_surv: UnitConstant
    millimeter: UnitConstant
    mm: UnitConstant
    millimicron: UnitConstant
    mathrm_m_mu: UnitConstant
    nanometer_or_nanon: UnitConstant
    nm: UnitConstant
    parsec: UnitConstant
    pc: UnitConstant
    perche: UnitConstant
    rod: UnitConstant
    pica: UnitConstant
    picometer: UnitConstant
    pm: UnitConstant
    point_didot: UnitConstant
    pt_Didot: UnitConstant
    point_us: UnitConstant
    pt_US: UnitConstant
    rod_or_pole: UnitConstant
    span: UnitConstant
    thou_millinch: UnitConstant
    thou: UnitConstant
    toise_metric: UnitConstant
    yard: UnitConstant
    yd: UnitConstant
    nanometer: UnitConstant

class LinearMassDensityUnits:
    """Unit constants for Linear Mass Density."""
    __slots__: tuple[()]

    denier: UnitConstant
    kilogram_per_centimeter: UnitConstant
    kg_cm: UnitConstant
    kilogram_per_meter: UnitConstant
    kg_m: UnitConstant
    pound_per_foot: UnitConstant
    lb_ft: UnitConstant
    pound_per_inch: UnitConstant
    lb_in: UnitConstant
    pound_per_yard: UnitConstant
    lb_yd: UnitConstant
    ton_metric: UnitConstant
    t_km_or_MT_km: UnitConstant
    t_km: UnitConstant
    MT_km: UnitConstant
    ton_metric: UnitConstant
    t_m_or_MT_m: UnitConstant
    t_m: UnitConstant
    MT_m: UnitConstant

class LinearMomentumUnits:
    """Unit constants for Linear Momentum."""
    __slots__: tuple[()]

    foot_pounds_force_per_hour: UnitConstant
    mathrm_ft_mathrm_lb_mathrm_f_mathrm_h_or_mathrm_ft_mathrm_lb_mathrm_hr: UnitConstant
    ft_lb_f_h: UnitConstant
    ft_lb_hr: UnitConstant
    foot_pounds_force_per_minute: UnitConstant
    mathrm_ft_mathrm_lb_mathrm_f_min_or_mathrm_ft_mathrm_lb_min: UnitConstant
    ft_lb_f_min: UnitConstant
    ft_lb_min: UnitConstant
    foot_pounds_force_per_second: UnitConstant
    mathrm_ft_mathrm_lb_mathrm_f_mathrm_s_or_ft_lb_sec: UnitConstant
    ft_lb_f_s: UnitConstant
    ft_lb_sec: UnitConstant
    gram_centimeters_per_second: UnitConstant
    mathrm_g_mathrm_cm_mathrm_s: UnitConstant
    kilogram_meters_per_second: UnitConstant
    mathrm_kg_mathrm_m_mathrm_s: UnitConstant

class LuminanceSelfUnits:
    """Unit constants for Luminance (self)."""
    __slots__: tuple[()]

    apostilb: UnitConstant
    asb: UnitConstant
    blondel: UnitConstant
    B1: UnitConstant
    candela_per_square_meter: UnitConstant
    mathrm_cd_mathrm_m_2: UnitConstant
    foot_lambert: UnitConstant
    ft_L: UnitConstant
    lambert: UnitConstant
    L: UnitConstant
    luxon: UnitConstant
    nit: UnitConstant
    stilb: UnitConstant
    sb: UnitConstant
    troland: UnitConstant
    luxon: UnitConstant

class LuminousFluxUnits:
    """Unit constants for Luminous Flux."""
    __slots__: tuple[()]

    candela_steradian: UnitConstant
    cd_sr: UnitConstant
    lumen: UnitConstant

class LuminousIntensityUnits:
    """Unit constants for Luminous Intensity."""
    __slots__: tuple[()]

    candela: UnitConstant
    cd: UnitConstant
    candle_international: UnitConstant
    Cd_int: UnitConstant
    carcel: UnitConstant
    hefner_unit: UnitConstant
    HK: UnitConstant

class MagneticFieldUnits:
    """Unit constants for Magnetic Field."""
    __slots__: tuple[()]

    ampere_per_meter: UnitConstant
    A_m: UnitConstant
    lenz: UnitConstant
    oersted: UnitConstant
    Oe: UnitConstant
    praoersted: UnitConstant

class MagneticFluxUnits:
    """Unit constants for Magnetic Flux."""
    __slots__: tuple[()]

    kapp_line: UnitConstant
    line: UnitConstant
    maxwell: UnitConstant
    Mx: UnitConstant
    unit_pole: UnitConstant
    weber: UnitConstant
    Wb: UnitConstant
    milliweber: UnitConstant
    mWb: UnitConstant
    microweber: UnitConstant

class MagneticInductionFieldStrengthUnits:
    """Unit constants for Magnetic Induction Field Strength."""
    __slots__: tuple[()]

    gamma: UnitConstant
    gauss: UnitConstant
    G: UnitConstant
    line_per_square_centimeter: UnitConstant
    line_mathrm_cm_2: UnitConstant
    maxwell_per_square_centimeter: UnitConstant
    mathrm_Mx_mathrm_cm_2: UnitConstant
    tesla: UnitConstant
    u_a: UnitConstant
    weber_per_square_meter: UnitConstant
    mathrm_Wb_mathrm_m_2: UnitConstant
    millitesla: UnitConstant
    mT: UnitConstant
    microtesla: UnitConstant
    nanotesla: UnitConstant
    nT: UnitConstant

class MagneticMomentUnits:
    """Unit constants for Magnetic Moment."""
    __slots__: tuple[()]

    bohr_magneton: UnitConstant
    Bohr_magneton: UnitConstant
    joule_per_tesla: UnitConstant
    J_T: UnitConstant
    nuclear_magneton: UnitConstant
    nucl_Magneton: UnitConstant

class MagneticPermeabilityUnits:
    """Unit constants for Magnetic Permeability."""
    __slots__: tuple[()]

    henrys_per_meter: UnitConstant
    H_m: UnitConstant
    newton_per_square_ampere: UnitConstant
    N_A_2: UnitConstant

class MagnetomotiveForceUnits:
    """Unit constants for Magnetomotive Force."""
    __slots__: tuple[()]

    abampere_turn: UnitConstant
    ampere: UnitConstant
    ampere_turn: UnitConstant
    A_turn: UnitConstant
    gilbert: UnitConstant
    Gb: UnitConstant
    kiloampere: UnitConstant
    kA: UnitConstant
    milliampere: UnitConstant
    mA: UnitConstant
    microampere: UnitConstant
    nanoampere: UnitConstant
    nA: UnitConstant
    picoampere: UnitConstant
    pA: UnitConstant

class MassUnits:
    """Unit constants for Mass."""
    __slots__: tuple[()]

    slug: UnitConstant
    sl: UnitConstant
    atomic_mass_unit_12_mathrmc: UnitConstant
    mathrm_u_left_12_mathrm_C_right_or_amu: UnitConstant
    uleft_12_Cright: UnitConstant
    carat_metric: UnitConstant
    ct: UnitConstant
    cental: UnitConstant
    sh_cwt_cH: UnitConstant
    centigram: UnitConstant
    cg: UnitConstant
    clove_uk: UnitConstant
    cl: UnitConstant
    drachm_apothecary: UnitConstant
    dr_ap: UnitConstant
    dram_avoirdupois: UnitConstant
    dr_av: UnitConstant
    dram_troy: UnitConstant
    dr_troy: UnitConstant
    grain: UnitConstant
    gr: UnitConstant
    gram: UnitConstant
    g: UnitConstant
    hundredweight_long_or_gross: UnitConstant
    cwt_lg_cwt: UnitConstant
    hundredweight_short_or_net: UnitConstant
    sh_cwt: UnitConstant
    kilogram: UnitConstant
    kg: UnitConstant
    kip: UnitConstant
    microgram: UnitConstant
    mu_mathrm_g: UnitConstant
    milligram: UnitConstant
    mg: UnitConstant
    ounce_apothecary: UnitConstant
    oz_ap: UnitConstant
    ounce_avoirdupois: UnitConstant
    ounce_troy: UnitConstant
    oz_troy: UnitConstant
    pennyweight_troy: UnitConstant
    dwt_troy: UnitConstant
    pood_russia: UnitConstant
    pood: UnitConstant
    pound_apothecary: UnitConstant
    lb_ap: UnitConstant
    pound_avoirdupois: UnitConstant
    lb_av: UnitConstant
    pound_troy: UnitConstant
    lb_troy: UnitConstant
    pound_mass: UnitConstant
    mathrm_lb_mathrm_m: UnitConstant
    quarter_uk: UnitConstant
    qt: UnitConstant
    quintal_metric: UnitConstant
    q_dt: UnitConstant
    quital_us: UnitConstant
    quint_US: UnitConstant
    scruple_avoirdupois: UnitConstant
    scf: UnitConstant
    stone_uk: UnitConstant
    st: UnitConstant
    ton_metric: UnitConstant
    t: UnitConstant
    ton_us_long: UnitConstant
    lg_ton: UnitConstant
    ton_us_short: UnitConstant
    sh_ton: UnitConstant

class MassDensityUnits:
    """Unit constants for Mass Density."""
    __slots__: tuple[()]

    gram_per_cubic_centimeter: UnitConstant
    g_cc_or_g_ml: UnitConstant
    g_cc: UnitConstant
    g_ml: UnitConstant
    gram_per_cubic_decimeter: UnitConstant
    mathrm_g_mathrm_dm_3: UnitConstant
    gram_per_cubic_meter: UnitConstant
    mathrm_g_mathrm_m_3: UnitConstant
    gram_per_liter: UnitConstant
    mathrm_g_mathrm_l_or_g_L: UnitConstant
    g_l: UnitConstant
    g_L: UnitConstant
    kilogram_per_cubic_meter: UnitConstant
    mathrm_kg_mathrm_m_3: UnitConstant
    ounce_avdp: UnitConstant
    oz_gal: UnitConstant
    pound_avdp: UnitConstant
    mathrm_lb_mathrm_cu_mathrm_ft_or_lb_ft_3: UnitConstant
    lb_cu_ft: UnitConstant
    lb_ft_3: UnitConstant
    pound_avdp: UnitConstant
    lb_gal: UnitConstant
    pound_mass: UnitConstant
    mathrm_lb_mathrm_cu_in_or_mathrm_lb_mathrm_in_3: UnitConstant
    lb_cu_in: UnitConstant
    lb_in_3: UnitConstant
    ton_metric: UnitConstant
    mathrm_t_mathrm_m_3_or_MT_mathrm_m_3: UnitConstant
    t_m_3: UnitConstant
    MT_m_3: UnitConstant

class MassFlowRateUnits:
    """Unit constants for Mass Flow Rate."""
    __slots__: tuple[()]

    kilograms_per_day: UnitConstant
    kg_d: UnitConstant
    kilograms_per_hour: UnitConstant
    kg_h: UnitConstant
    kilograms_per_minute: UnitConstant
    kg_min: UnitConstant
    kilograms_per_second: UnitConstant
    kg_s: UnitConstant
    metric_tons_per_day: UnitConstant
    MT_d_or_MTD: UnitConstant
    MT_d: UnitConstant
    MTD: UnitConstant
    metric_tons_per_hour: UnitConstant
    MT_h_or_MTD: UnitConstant
    MT_h: UnitConstant
    metric_tons_per_minute: UnitConstant
    metric_tons_per_second: UnitConstant
    MT_s: UnitConstant
    metric_tons_per_year_365_d: UnitConstant
    MT_yr_or_MTY: UnitConstant
    MT_yr: UnitConstant
    MTY: UnitConstant
    pounds_per_day: UnitConstant
    mathrm_lb_mathrm_d_or_mathrm_lb_mathrm_da_or_PPD: UnitConstant
    lb_d: UnitConstant
    lb_da: UnitConstant
    PPD: UnitConstant
    pounds_per_hour: UnitConstant
    mathrm_lb_mathrm_h_or_lb_hr_or_PPH: UnitConstant
    lb_h: UnitConstant
    lb_hr: UnitConstant
    PPH: UnitConstant
    pounds_per_minute: UnitConstant
    mathrm_lb_mathrm_min_or_PPM: UnitConstant
    lb_min: UnitConstant
    PPM: UnitConstant
    pounds_per_second: UnitConstant
    mathrm_lb_mathrm_s_or_lb_sec_or_PPS: UnitConstant
    lb_s: UnitConstant
    lb_sec: UnitConstant
    PPS: UnitConstant

class MassFluxUnits:
    """Unit constants for Mass Flux."""
    __slots__: tuple[()]

    kilogram_per_square_meter_per_day: UnitConstant
    mathrm_kg_left_mathrm_m_2_mathrm_d_right: UnitConstant
    kilogram_per_square_meter_per_hour: UnitConstant
    mathrm_kg_left_mathrm_m_2_mathrm_h_right: UnitConstant
    kilogram_per_square_meter_per_minute: UnitConstant
    mathrm_kg_left_mathrm_m_2_mathrm_min_right: UnitConstant
    kilogram_per_square_meter_per_second: UnitConstant
    mathrm_kg_left_mathrm_m_2_mathrm_s_right: UnitConstant
    pound_per_square_foot_per_day: UnitConstant
    mathrm_lb_left_mathrm_ft_2_mathrm_d_right_or_lb_sqft_da: UnitConstant
    lb_left_ft_2_dright: UnitConstant
    lb_sqft_da: UnitConstant
    pound_per_square_foot_per_hour: UnitConstant
    mathrm_lb_left_mathrm_ft_2_mathrm_h_right_or_lb_sqft_hr: UnitConstant
    lb_left_ft_2_hright: UnitConstant
    lb_sqft_hr: UnitConstant
    pound_per_square_foot_per_minute: UnitConstant
    mathrm_lb_left_mathrm_ft_2_min_right_or_lb_sqft_min: UnitConstant
    lb_left_ft_2_min_right: UnitConstant
    lb_sqft_min: UnitConstant
    pound_per_square_foot_per_second: UnitConstant
    mathrm_lb_left_mathrm_ft_2_mathrm_s_right_or_lb_sqft_sec: UnitConstant
    lb_left_ft_2_sright: UnitConstant
    lb_sqft_sec: UnitConstant

class MassFractionOfIUnits:
    """Unit constants for Mass Fraction of "i"."""
    __slots__: tuple[()]

    grains_of_i_per_pound_total: UnitConstant
    mathrm_gr_mathrm_i_mathrm_lb: UnitConstant
    gram_of_i_per_kilogram_total: UnitConstant
    mathrm_g_mathrm_i_mathrm_kg: UnitConstant
    kilogram_of_i_per_kilogram_total: UnitConstant
    mathrm_kg_mathrm_i_mathrm_kg: UnitConstant
    pound_of_i_per_pound_total: UnitConstant
    mathrm_lb_mathrm_i_mathrm_lb: UnitConstant

class MassTransferCoefficientUnits:
    """Unit constants for Mass Transfer Coefficient."""
    __slots__: tuple[()]

    gram_per_square_centimeter_per_second: UnitConstant
    kilogram_per_square_meter_per_second: UnitConstant
    pounds_force_per_cubic_foot_per_hour: UnitConstant
    mathrm_lb_mathrm_f_mathrm_ft_3_mathrm_h_or_mathrm_lb_mathrm_f_mathrm_cft_mathrm_hr: UnitConstant
    lb_f_ft_3_h: UnitConstant
    lb_f_cft_hr: UnitConstant
    pounds_mass_per_square_foot_per_hour: UnitConstant
    lb_ft_2_mathrm_hr_or_lb_sqft_hr: UnitConstant
    lb_ft_2_hr: UnitConstant
    pounds_mass_per_square_foot_per_second: UnitConstant

class MolalityOfSoluteIUnits:
    """Unit constants for Molality of Solute "i"."""
    __slots__: tuple[()]

    gram_moles_of_i_per_kilogram: UnitConstant
    mathrm_mol_mathrm_i_mathrm_kg: UnitConstant
    kilogram_mols_of_i_per_kilogram: UnitConstant
    mathrm_kmol_mathrm_i_mathrm_kg: UnitConstant
    kmols_of_i_per_kilogram: UnitConstant
    mols_of_i_per_gram: UnitConstant
    mathrm_mol_mathrm_i_mathrm_g: UnitConstant
    pound_moles_of_i_per_pound_mass: UnitConstant
    mole_mathrm_i_mathrm_lb_mass: UnitConstant

class MolarConcentrationByMassUnits:
    """Unit constants for Molar Concentration by Mass."""
    __slots__: tuple[()]

    gram_mole_or_mole_per_gram: UnitConstant
    mol_g: UnitConstant
    gram_mole_or_mole_per_kilogram: UnitConstant
    mol_kg: UnitConstant
    kilogram_mole_or_kmol_per_kilogram: UnitConstant
    kmol_kg: UnitConstant
    micromole_per_gram: UnitConstant
    mu_mathrm_mol_mathrm_g: UnitConstant
    millimole_per_gram: UnitConstant
    mmol_g: UnitConstant
    picomole_per_gram: UnitConstant
    pmol_g: UnitConstant
    pound_mole_per_pound: UnitConstant
    mathrm_lb_mathrm_mol_mathrm_lb_or_mole_lb: UnitConstant
    lb_mol_lb: UnitConstant
    mole_lb: UnitConstant

class MolarFlowRateUnits:
    """Unit constants for Molar Flow Rate."""
    __slots__: tuple[()]

    gram_mole_per_day: UnitConstant
    mol_d: UnitConstant
    gram_mole_per_hour: UnitConstant
    mol_h: UnitConstant
    gram_mole_per_minute: UnitConstant
    mol_min: UnitConstant
    gram_mole_per_second: UnitConstant
    mol_s: UnitConstant
    kilogram_mole_or_kmol_per_day: UnitConstant
    kmol_d: UnitConstant
    kilogram_mole_or_kmol_per_hour: UnitConstant
    kmol_h: UnitConstant
    kilogram_mole_or_kmol_per_minute: UnitConstant
    kmol_min: UnitConstant
    kilogram_mole_or_kmol_per_second: UnitConstant
    kmol_s: UnitConstant
    pound_mole_or_lb_mol_per_day: UnitConstant
    lb_mol_d_or_mole_da: UnitConstant
    lb_mol_d: UnitConstant
    mole_da: UnitConstant
    pound_mole_or_lb_mol_per_hour: UnitConstant
    lb_mol_h_or_mole_hr: UnitConstant
    lb_mol_h: UnitConstant
    mole_hr: UnitConstant
    pound_mole_or_lb_mol_per_minute: UnitConstant
    lb_mol_min_or_mole_min: UnitConstant
    lb_mol_min: UnitConstant
    mole_min: UnitConstant
    pound_mole_or_lb_mol_per_second: UnitConstant
    mathrm_lb_mathrm_mol_mathrm_s_or_mole_sec: UnitConstant
    lb_mol_s: UnitConstant
    mole_sec: UnitConstant

class MolarFluxUnits:
    """Unit constants for Molar Flux."""
    __slots__: tuple[()]

    kmol_per_square_meter_per_day: UnitConstant
    mathrm_kmol_left_mathrm_m_2_mathrm_d_right: UnitConstant
    kmol_per_square_meter_per_hour: UnitConstant
    mathrm_kmol_left_mathrm_m_2_mathrm_h_right: UnitConstant
    kmol_per_square_meter_per_minute: UnitConstant
    mathrm_kmol_left_mathrm_m_2_right_amin: UnitConstant
    kmol_per_square_meter_per_second: UnitConstant
    mathrm_kmol_left_mathrm_m_2_mathrm_s_right: UnitConstant
    pound_mole_per_square_foot_per_day: UnitConstant
    mathrm_lb_mathrm_mol_left_mathrm_ft_2_mathrm_d_right_or_mole_sqft_da: UnitConstant
    lb_mol_left_ft_2_dright: UnitConstant
    mole_sqft_da: UnitConstant
    pound_mole_per_square_foot_per_hour: UnitConstant
    mathrm_lb_mathrm_mol_left_mathrm_ft_2_mathrm_h_right_or_mole_sqft_hr: UnitConstant
    lb_mol_left_ft_2_hright: UnitConstant
    mole_sqft_hr: UnitConstant
    pound_mole_per_square_foot_per_minute: UnitConstant
    mathrm_lb_mathrm_mol_left_mathrm_ft_2_mathrm_min_right_or_mole_sqft_min: UnitConstant
    lb_mol_left_ft_2_minright: UnitConstant
    mole_sqft_min: UnitConstant
    pound_mole_per_square_foot_per_second: UnitConstant
    mathrm_lb_mathrm_mol_left_mathrm_ft_2_mathrm_s_right_or_mole_sqft_sec: UnitConstant
    lb_mol_left_ft_2_sright: UnitConstant
    mole_sqft_sec: UnitConstant

class MolarHeatCapacityUnits:
    """Unit constants for Molar Heat Capacity."""
    __slots__: tuple[()]

    btu_per_pound_mole_per_degree_fahrenheit_or_degree_rankine: UnitConstant
    Btu_lb_mol_circ_mathrm_F: UnitConstant
    calories_per_gram_mole_per_kelvin_or_degree_celsius: UnitConstant
    cal_mol_K: UnitConstant
    joule_per_gram_mole_per_kelvin_or_degree_celsius: UnitConstant
    J_mol_K: UnitConstant

class MolarityOfIUnits:
    """Unit constants for Molarity of "i"."""
    __slots__: tuple[()]

    gram_moles_of_i_per_cubic_meter: UnitConstant
    mathrm_mol_mathrm_i_mathrm_m_3_or_mathrm_c_mathrm_i: UnitConstant
    mol_i_m_3: UnitConstant
    c_i: UnitConstant
    gram_moles_of_i_per_liter: UnitConstant
    mathrm_mol_mathrm_i_mathrm_l: UnitConstant
    kilogram_moles_of_i_per_cubic_meter: UnitConstant
    mathrm_kmol_mathrm_i_mathrm_m_3: UnitConstant
    kilogram_moles_of_i_per_liter: UnitConstant
    mathrm_kmol_mathrm_i_mathrm_l: UnitConstant
    pound_moles_of_i_per_cubic_foot: UnitConstant
    lb_mathrm_mol_mathrm_i_mathrm_ft_3_or_mathrm_mole_mathrm_i_cft: UnitConstant
    lb_mol_i_ft_3: UnitConstant
    mole_i_cft: UnitConstant
    pound_moles_of_i_per_gallon_us: UnitConstant
    lb_mathrm_mol_mathrm_i_mathrm_gal_or_mathrm_mole_mathrm_i_gal: UnitConstant
    lb_mol_i_gal: UnitConstant
    mole_i_gal: UnitConstant

class MoleFractionOfIUnits:
    """Unit constants for Mole Fraction of "i"."""
    __slots__: tuple[()]

    gram_mole_of_i_per_gram_mole_total: UnitConstant
    mathrm_mol_mathrm_i_mathrm_mol: UnitConstant
    kilogram_mole_of_i_per_kilogram_mole_total: UnitConstant
    mathrm_kmol_mathrm_i_mathrm_kmol: UnitConstant
    kilomole_of_i_per_kilomole_total: UnitConstant
    pound_mole_of_i_per_pound_mole_total: UnitConstant
    lb_mathrm_mol_mathrm_i_mathrm_lb_mathrm_mol: UnitConstant

class MomentOfInertiaUnits:
    """Unit constants for Moment of Inertia."""
    __slots__: tuple[()]

    gram_force_centimeter_square_second: UnitConstant
    mathrm_g_mathrm_f_mathrm_cm_mathrm_s_2: UnitConstant
    gram_square_centimeter: UnitConstant
    mathrm_g_mathrm_cm_2: UnitConstant
    kilogram_force_centimeter_square_second: UnitConstant
    mathrm_kg_mathrm_f_mathrm_cm_mathrm_s_2: UnitConstant
    kilogram_force_meter_square_second: UnitConstant
    mathrm_kg_mathrm_f_mathrm_m_mathrm_s_2: UnitConstant
    kilogram_square_centimeter: UnitConstant
    mathrm_kg_mathrm_cm_2: UnitConstant
    kilogram_square_meter: UnitConstant
    mathrm_kg_mathrm_m_2: UnitConstant
    ounce_force_inch_square_second: UnitConstant
    mathrm_oz_mathrm_f_in_mathrm_s_2: UnitConstant
    ounce_mass_square_inch: UnitConstant
    oz_in_2: UnitConstant
    pound_mass_square_foot: UnitConstant
    lb_ft_2_or_lb_sq_ft: UnitConstant
    lb_ft_2: UnitConstant
    lb_sq_ft: UnitConstant
    pound_mass_square_inch: UnitConstant
    mathrm_lb_mathrm_in_2: UnitConstant

class MomentumFlowRateUnits:
    """Unit constants for Momentum Flow Rate."""
    __slots__: tuple[()]

    foot_pounds_per_square_hour: UnitConstant
    mathrm_ft_mathrm_lb_mathrm_h_2_or_mathrm_ft_mathrm_lb_mathrm_hr_2: UnitConstant
    ft_lb_h_2: UnitConstant
    ft_lb_hr_2: UnitConstant
    foot_pounds_per_square_minute: UnitConstant
    mathrm_ft_mathrm_lb_mathrm_min_2: UnitConstant
    foot_pounds_per_square_second: UnitConstant
    mathrm_ft_mathrm_lb_mathrm_s_2_or_ft_lb_sec_2: UnitConstant
    ft_lb_s_2: UnitConstant
    ft_lb_sec_2: UnitConstant
    gram_centimeters_per_square_second: UnitConstant
    mathrm_g_mathrm_cm_mathrm_s_2: UnitConstant
    kilogram_meters_per_square_second: UnitConstant
    mathrm_kg_mathrm_m_mathrm_s_2: UnitConstant

class MomentumFluxUnits:
    """Unit constants for Momentum Flux."""
    __slots__: tuple[()]

    dyne_per_square_centimeter: UnitConstant
    dyn_mathrm_cm_2: UnitConstant
    gram_per_centimeter_per_square_second: UnitConstant
    newton_per_square_meter: UnitConstant
    mathrm_N_mathrm_m_2: UnitConstant
    pound_force_per_square_foot: UnitConstant
    mathrm_lb_mathrm_f_mathrm_sq_mathrm_ft: UnitConstant
    pound_mass_per_foot_per_square_second: UnitConstant
    mathrm_lb_mathrm_m_mathrm_ft_mathrm_s_2_or_mathrm_lb_mathrm_ft_mathrm_sec_2: UnitConstant
    lb_m_ft_s_2: UnitConstant
    lb_ft_sec_2: UnitConstant

class NormalityOfSolutionUnits:
    """Unit constants for Normality of Solution."""
    __slots__: tuple[()]

    gram_equivalents_per_cubic_meter: UnitConstant
    mathrm_eq_mathrm_m_3: UnitConstant
    gram_equivalents_per_liter: UnitConstant
    eq_l: UnitConstant
    pound_equivalents_per_cubic_foot: UnitConstant
    mathrm_lb_mathrm_eq_mathrm_ft_3_or_lb_eq_cft: UnitConstant
    lb_eq_ft_3: UnitConstant
    lb_eq_cft: UnitConstant
    pound_equivalents_per_gallon: UnitConstant
    lb_eq_gal_US: UnitConstant

class ParticleDensityUnits:
    """Unit constants for Particle Density."""
    __slots__: tuple[()]

    particles_per_cubic_centimeter: UnitConstant
    part_cm_3_or_part_cc: UnitConstant
    part_cm_3: UnitConstant
    part_cc: UnitConstant
    particles_per_cubic_foot: UnitConstant
    part_mathrm_ft_3_or_part_cft: UnitConstant
    part_ft_3: UnitConstant
    part_cft: UnitConstant
    particles_per_cubic_meter: UnitConstant
    part_mathrm_m_3: UnitConstant
    particles_per_gallon_us: UnitConstant
    part_gal: UnitConstant
    particles_per_liter: UnitConstant
    part_l: UnitConstant
    particles_per_milliliter: UnitConstant
    part_ml: UnitConstant

class PercentUnits:
    """Unit constants for Percent."""
    __slots__: tuple[()]

    percent: UnitConstant
    per_mille: UnitConstant
    basis_point: UnitConstant
    bp: UnitConstant
    bps: UnitConstant

class PermeabilityUnits:
    """Unit constants for Permeability."""
    __slots__: tuple[()]

    darcy: UnitConstant
    square_feet: UnitConstant
    mathrm_ft_2_or_sq_ft: UnitConstant
    square_meters: UnitConstant

class PhotonEmissionRateUnits:
    """Unit constants for Photon Emission Rate."""
    __slots__: tuple[()]

    rayleigh: UnitConstant
    R: UnitConstant
    reciprocal_square_meter_second: UnitConstant

class PowerPerUnitMassUnits:
    """Unit constants for Power per Unit Mass or Specific Power."""
    __slots__: tuple[()]

    british_thermal_unit_per_hour_per_pound_mass: UnitConstant
    Btu_h_lb_or_Btu_lb_hr: UnitConstant
    Btu_h_lb: UnitConstant
    Btu_lb_hr: UnitConstant
    calorie_per_second_per_gram: UnitConstant
    cal_s_g_or_cal_g_sec: UnitConstant
    cal_s_g: UnitConstant
    cal_g_sec: UnitConstant
    kilocalorie_per_hour_per_kilogram: UnitConstant
    kcal_h_kg_or_kcal_kg_hr: UnitConstant
    kcal_h_kg: UnitConstant
    kcal_kg_hr: UnitConstant
    watt_per_kilogram: UnitConstant
    W_kg: UnitConstant

class PowerPerUnitVolumeUnits:
    """Unit constants for Power per Unit Volume or Power Density."""
    __slots__: tuple[()]

    british_thermal_unit_per_hour_per_cubic_foot: UnitConstant
    mathrm_Btu_mathrm_h_mathrm_ft_3_or_mathrm_Btu_mathrm_hr_cft: UnitConstant
    Btu_h_ft_3: UnitConstant
    Btu_hr_cft: UnitConstant
    calorie_per_second_per_cubic_centimeter: UnitConstant
    mathrm_cal_mathrm_s_mathrm_cm_3_or_mathrm_cal_mathrm_s_mathrm_cc: UnitConstant
    cal_s_cm_3: UnitConstant
    cal_s_cc: UnitConstant
    chu_per_hour_per_cubic_foot: UnitConstant
    Chu_h_ft3_or_Chu_hr_cft: UnitConstant
    Chu_h_ft3: UnitConstant
    Chu_hr_cft: UnitConstant
    kilocalorie_per_hour_per_cubic_centimeter: UnitConstant
    mathrm_kcal_mathrm_h_mathrm_cm_3_or_mathrm_kcal_hr_cc: UnitConstant
    kcal_h_cm_3: UnitConstant
    kcal_hr_cc: UnitConstant
    kilocalorie_per_hour_per_cubic_foot: UnitConstant
    mathrm_kcal_mathrm_h_mathrm_ft_3_or_mathrm_kcal_mathrm_hr_cft: UnitConstant
    kcal_h_ft_3: UnitConstant
    kcal_hr_cft: UnitConstant
    kilocalorie_per_second_per_cubic_centimeter: UnitConstant
    kcal_s_cm_3_or_kcal_s_cc: UnitConstant
    kcal_s_cm_3: UnitConstant
    kcal_s_cc: UnitConstant
    watt_per_cubic_meter: UnitConstant
    mathrm_W_mathrm_m_3: UnitConstant

class PowerThermalDutyUnits:
    """Unit constants for Power, Thermal Duty."""
    __slots__: tuple[()]

    abwatt_emu_of_power: UnitConstant
    emu: UnitConstant
    boiler_horsepower: UnitConstant
    HP_boiler: UnitConstant
    british_thermal_unit_mean: UnitConstant
    Btu_mean_hr_or_Btu_hr: UnitConstant
    Btu_mean_hr: UnitConstant
    Btu_hr: UnitConstant
    british_thermal_unit_mean: UnitConstant
    Btu_min_or_Btu_mean_min: UnitConstant
    Btu_min: UnitConstant
    Btu_mean_min: UnitConstant
    british_thermal_unit_thermochemical: UnitConstant
    Btu_therm_hr_or_Btu_hr: UnitConstant
    Btu_therm_hr: UnitConstant
    british_thermal_unit_thermochemical: UnitConstant
    mathrm_Btu_mathrm_min_or_Btu_therm_min: UnitConstant
    Btu_therm_min: UnitConstant
    calorie_mean: UnitConstant
    cal_mean_hr: UnitConstant
    calorie_thermochemical: UnitConstant
    cal_therm_hr: UnitConstant
    donkey: UnitConstant
    erg_per_second: UnitConstant
    erg_s: UnitConstant
    foot_pondal_per_second: UnitConstant
    ft_pdl_s: UnitConstant
    foot_pound_force_per_hour: UnitConstant
    mathrm_ft_mathrm_lb_mathrm_f_mathrm_hr: UnitConstant
    foot_pound_force_per_minute: UnitConstant
    mathrm_ft_mathrm_lb_mathrm_f_min: UnitConstant
    foot_pound_force_per_second: UnitConstant
    mathrm_ft_mathrm_lb_mathrm_f_mathrm_s: UnitConstant
    horsepower_550_mathrmft_mathrmlb_mathrmf_mathrms: UnitConstant
    HP: UnitConstant
    horsepower_electric: UnitConstant
    HP_elect: UnitConstant
    horsepower_uk: UnitConstant
    HP_UK: UnitConstant
    kcal_per_hour: UnitConstant
    kcal_hr: UnitConstant
    kilogram_force_meter_per_second: UnitConstant
    mathrm_kg_mathrm_f_mathrm_m_mathrm_s: UnitConstant
    kilowatt: UnitConstant
    kW: UnitConstant
    megawatt: UnitConstant
    MW: UnitConstant
    metric_horsepower: UnitConstant
    HP_metric: UnitConstant
    million_british_thermal_units_per_hour_petroleum: UnitConstant
    MMBtu_hr: UnitConstant
    million_kilocalorie_per_hour: UnitConstant
    MM_kcal_hr: UnitConstant
    prony: UnitConstant
    ton_of_refrigeration_us: UnitConstant
    CTR_US: UnitConstant
    ton_or_refrigeration_uk: UnitConstant
    CTR_UK: UnitConstant
    volt_ampere: UnitConstant
    VA: UnitConstant
    water_horsepower: UnitConstant
    HP_water: UnitConstant
    watt: UnitConstant
    W: UnitConstant
    watt_international_mean: UnitConstant
    W_int_mean: UnitConstant
    watt_international_us: UnitConstant
    watt_int_US: UnitConstant
    gigawatt: UnitConstant
    GW: UnitConstant
    milliwatt: UnitConstant
    mW: UnitConstant
    microwatt: UnitConstant

class PressureUnits:
    """Unit constants for Pressure."""
    __slots__: tuple[()]

    atmosphere_standard: UnitConstant
    atm: UnitConstant
    bar: UnitConstant
    barye: UnitConstant
    dyne_per_square_centimeter: UnitConstant
    foot_of_mercury_60_circ_mathrmf: UnitConstant
    ft_Hg_60_circ_mathrm_F: UnitConstant
    foot_of_water_60_circ_mathrmf: UnitConstant
    ft_mathrm_H_2_mathrm_O_left_60_circ_mathrm_F_right: UnitConstant
    gigapascal: UnitConstant
    GPa: UnitConstant
    hectopascal: UnitConstant
    hPa: UnitConstant
    inch_of_mercury_60_circ_mathrmf: UnitConstant
    in_mathrm_Hg_left_60_circ_mathrm_F_right: UnitConstant
    inch_of_water_60_circ_mathrmf: UnitConstant
    in_mathrm_H_2_mathrm_O_left_60_circ_mathrm_F_right: UnitConstant
    kilogram_force_per_square_centimeter: UnitConstant
    at_or_mathrm_kg_mathrm_f_mathrm_cm_2: UnitConstant
    at: UnitConstant
    kg_f_cm_2: UnitConstant
    kilogram_force_per_square_meter: UnitConstant
    mathrm_kg_mathrm_f_mathrm_m_2: UnitConstant
    kip_force_per_square_inch: UnitConstant
    KSI_or_ksi_or_kip_f_mathrm_in_2: UnitConstant
    KSI: UnitConstant
    ksi: UnitConstant
    kip_f_in_2: UnitConstant
    megapascal: UnitConstant
    MPa: UnitConstant
    meter_of_water_4circ_mathrmc: UnitConstant
    mathrm_m_mathrm_H_2_mathrm_O_left_4_circ_mathrm_C_right: UnitConstant
    microbar: UnitConstant
    mu_mathrm_bar: UnitConstant
    millibar: UnitConstant
    mbar: UnitConstant
    millimeter_of_mercury_4circ_mathrmc: UnitConstant
    mathrm_mm_mathrm_Hg_left_4_circ_mathrm_C_right: UnitConstant
    millimeter_of_water_4circ_mathrmc: UnitConstant
    mathrm_mm_mathrm_H_2_mathrm_O_left_4_circ_mathrm_C_right: UnitConstant
    newton_per_square_meter: UnitConstant
    ounce_force_per_square_inch: UnitConstant
    OSI_or_osi_or_mathrm_oz_mathrm_f_mathrm_in_2: UnitConstant
    OSI: UnitConstant
    osi: UnitConstant
    pascal: UnitConstant
    Pa: UnitConstant
    pi_ze: UnitConstant
    pz: UnitConstant
    pound_force_per_square_foot: UnitConstant
    PSF_or_psf_or_mathrm_lb_mathrm_f_mathrm_ft_2: UnitConstant
    psf: UnitConstant
    pound_force_per_square_inch: UnitConstant
    psi: UnitConstant
    torr: UnitConstant
    torr_or_mm_Hg_0_circ_C: UnitConstant
    mm_Hg_0_circ_C: UnitConstant
    kilopascal: UnitConstant
    kPa: UnitConstant

class RadiationDoseEquivalentUnits:
    """Unit constants for Radiation Dose Equivalent."""
    __slots__: tuple[()]

    rem: UnitConstant
    sievert: UnitConstant
    Sv: UnitConstant
    millisievert: UnitConstant
    mSv: UnitConstant
    microsievert: UnitConstant

class RadiationExposureUnits:
    """Unit constants for Radiation Exposure."""
    __slots__: tuple[()]

    coulomb_per_kilogram: UnitConstant
    C_kg: UnitConstant
    d_unit: UnitConstant
    D_unit: UnitConstant
    pastille_dose_b_unit: UnitConstant
    B_unit: UnitConstant
    r_entgen: UnitConstant

class RadioactivityUnits:
    """Unit constants for Radioactivity."""
    __slots__: tuple[()]

    becquerel: UnitConstant
    Bq: UnitConstant
    curie: UnitConstant
    Ci: UnitConstant
    mache_unit: UnitConstant
    Mache: UnitConstant
    rutherford: UnitConstant
    Rd: UnitConstant
    stat: UnitConstant
    kilobecquerel: UnitConstant
    kBq: UnitConstant
    megabecquerel: UnitConstant
    MBq: UnitConstant
    gigabecquerel: UnitConstant
    GBq: UnitConstant

class SecondMomentOfAreaUnits:
    """Unit constants for Second Moment of Area."""
    __slots__: tuple[()]

    inch_quadrupled: UnitConstant
    in_4: UnitConstant
    centimeter_quadrupled: UnitConstant
    mathrm_cm_4: UnitConstant
    foot_quadrupled: UnitConstant
    mathrm_ft_4: UnitConstant
    meter_quadrupled: UnitConstant
    mathrm_m_4: UnitConstant

class SecondRadiationConstantPlanckUnits:
    """Unit constants for Second Radiation Constant (Planck)."""
    __slots__: tuple[()]

    meter_kelvin: UnitConstant
    m_K: UnitConstant

class SpecificEnthalpyUnits:
    """Unit constants for Specific Enthalpy."""
    __slots__: tuple[()]

    british_thermal_unit_mean: UnitConstant
    british_thermal_unit_per_pound: UnitConstant
    calorie_per_gram: UnitConstant
    chu_per_pound: UnitConstant
    joule_per_kilogram: UnitConstant
    kilojoule_per_kilogram: UnitConstant
    kJ_kg: UnitConstant

class SpecificGravityUnits:
    """Unit constants for Specific Gravity."""
    __slots__: tuple[()]

    dimensionless: UnitConstant
    Dmls: UnitConstant

class SpecificHeatCapacityConstantPressureUnits:
    """Unit constants for Specific Heat Capacity (Constant Pressure)."""
    __slots__: tuple[()]

    btu_per_pound_per_degree_fahrenheit_or_degree_rankine: UnitConstant
    Btu_lb_circ_mathrm_F: UnitConstant
    calories_per_gram_per_kelvin_or_degree_celsius: UnitConstant
    cal_g_K: UnitConstant
    joules_per_kilogram_per_kelvin_or_degree_celsius: UnitConstant
    J_kg_K: UnitConstant

class SpecificLengthUnits:
    """Unit constants for Specific Length."""
    __slots__: tuple[()]

    centimeter_per_gram: UnitConstant
    cm_g: UnitConstant
    cotton_count: UnitConstant
    ft_per_pound: UnitConstant
    ft_lb: UnitConstant
    meters_per_kilogram: UnitConstant
    m_kg: UnitConstant
    newton_meter: UnitConstant
    Nm: UnitConstant
    worsted: UnitConstant

class SpecificSurfaceUnits:
    """Unit constants for Specific Surface."""
    __slots__: tuple[()]

    square_centimeter_per_gram: UnitConstant
    mathrm_cm_2_mathrm_g: UnitConstant
    square_foot_per_kilogram: UnitConstant
    mathrm_ft_2_mathrm_kg_or_sq_ft_kg: UnitConstant
    ft_2_kg: UnitConstant
    sq_ft_kg: UnitConstant
    square_foot_per_pound: UnitConstant
    mathrm_ft_2_mathrm_lb_or_sq_ft_lb: UnitConstant
    ft_2_lb: UnitConstant
    sq_ft_lb: UnitConstant
    square_meter_per_gram: UnitConstant
    mathrm_m_2_mathrm_g: UnitConstant
    square_meter_per_kilogram: UnitConstant
    mathrm_m_2_mathrm_kg: UnitConstant

class SpecificVolumeUnits:
    """Unit constants for Specific Volume."""
    __slots__: tuple[()]

    cubic_centimeter_per_gram: UnitConstant
    mathrm_cm_3_mathrm_g_or_mathrm_cc_mathrm_g: UnitConstant
    cm_3_g: UnitConstant
    cc_g: UnitConstant
    cubic_foot_per_kilogram: UnitConstant
    mathrm_ft_3_mathrm_kg_or_mathrm_cft_mathrm_kg: UnitConstant
    ft_3_kg: UnitConstant
    cft_kg: UnitConstant
    cubic_foot_per_pound: UnitConstant
    mathrm_ft_3_mathrm_lb_or_mathrm_cft_mathrm_lb: UnitConstant
    ft_3_lb: UnitConstant
    cft_lb: UnitConstant
    cubic_meter_per_kilogram: UnitConstant
    mathrm_m_3_mathrm_kg: UnitConstant

class StressUnits:
    """Unit constants for Stress."""
    __slots__: tuple[()]

    dyne_per_square_centimeter: UnitConstant
    gigapascal: UnitConstant
    hectopascal: UnitConstant
    kilogram_force_per_square_centimeter: UnitConstant
    kilogram_force_per_square_meter: UnitConstant
    kip_force_per_square_inch: UnitConstant
    megapascal: UnitConstant
    newton_per_square_meter: UnitConstant
    ounce_force_per_square_inch: UnitConstant
    oz_f_in_2: UnitConstant
    pascal: UnitConstant
    pound_force_per_square_foot: UnitConstant
    PSF: UnitConstant
    lb_f_ft_2: UnitConstant
    pound_force_per_square_inch: UnitConstant

class SurfaceMassDensityUnits:
    """Unit constants for Surface Mass Density."""
    __slots__: tuple[()]

    gram_per_square_centimeter: UnitConstant
    gram_per_square_meter: UnitConstant
    mathrm_g_mathrm_m_2: UnitConstant
    kilogram_per_square_meter: UnitConstant
    pound_mass: UnitConstant
    mathrm_lb_mathrm_ft_2: UnitConstant
    pound_mass: UnitConstant

class SurfaceTensionUnits:
    """Unit constants for Surface Tension."""
    __slots__: tuple[()]

    dyne_per_centimeter: UnitConstant
    dyn_cm: UnitConstant
    gram_force_per_centimeter: UnitConstant
    mathrm_g_mathrm_f_mathrm_cm: UnitConstant
    newton_per_meter: UnitConstant
    N_m: UnitConstant
    pound_force_per_foot: UnitConstant
    mathrm_lb_mathrm_f_mathrm_ft: UnitConstant
    pound_force_per_inch: UnitConstant
    mathrm_lb_mathrm_f_mathrm_in: UnitConstant

class TemperatureUnits:
    """Unit constants for Temperature."""
    __slots__: tuple[()]

    degree_celsius_unit_size: UnitConstant
    mathrm_C_circ: UnitConstant
    degree_fahrenheit_unit_size: UnitConstant
    mathrm_F_circ: UnitConstant
    degree_r_aumur_unit_size: UnitConstant
    R_circ: UnitConstant
    kelvin_absolute_scale: UnitConstant
    K: UnitConstant
    rankine_absolute_scale: UnitConstant
    circ_mathrm_R: UnitConstant

class ThermalConductivityUnits:
    """Unit constants for Thermal Conductivity."""
    __slots__: tuple[()]

    btu_it: UnitConstant
    Btu_IT_in_hr_circ_mathrm_F: UnitConstant
    btu_therm: UnitConstant
    mathrm_Btu_left_mathrm_ft_mathrm_hr_circ_mathrm_F_right: UnitConstant
    btu_therm: UnitConstant
    Btu_in_hr_circ_mathrm_F: UnitConstant
    calorie_therm: UnitConstant
    operatorname_cal_mathrm_IT_left_mathrm_cm_mathrm_s_circ_mathrm_C_right: UnitConstant
    joule_per_second_per_centimeter_per_kelvin: UnitConstant
    J_cm_s_K: UnitConstant
    watt_per_centimeter_per_kelvin: UnitConstant
    W_cm_K: UnitConstant
    watt_per_meter_per_kelvin: UnitConstant
    W_m_K: UnitConstant

class TimeUnits:
    """Unit constants for Time."""
    __slots__: tuple[()]

    blink: UnitConstant
    century: UnitConstant
    chronon_or_tempon: UnitConstant
    gigan_or_eon: UnitConstant
    Ga_or_eon: UnitConstant
    Ga: UnitConstant
    eon: UnitConstant
    hour: UnitConstant
    h_or_hr: UnitConstant
    h: UnitConstant
    hr: UnitConstant
    julian_year: UnitConstant
    a_jul_or_yr: UnitConstant
    a_jul: UnitConstant
    yr: UnitConstant
    mean_solar_day: UnitConstant
    da_or_d: UnitConstant
    da: UnitConstant
    d: UnitConstant
    millenium: UnitConstant
    minute: UnitConstant
    min: UnitConstant
    second: UnitConstant
    s: UnitConstant
    shake: UnitConstant
    sidereal_year_1900_ad: UnitConstant
    a_sider_or_yr: UnitConstant
    a_sider: UnitConstant
    tropical_year: UnitConstant
    a_trop: UnitConstant
    wink: UnitConstant
    year: UnitConstant
    a_or_y_or_yr: UnitConstant
    y: UnitConstant
    millisecond: UnitConstant
    ms: UnitConstant
    microsecond: UnitConstant
    nanosecond: UnitConstant
    ns: UnitConstant
    picosecond: UnitConstant
    ps: UnitConstant

class TorqueUnits:
    """Unit constants for Torque."""
    __slots__: tuple[()]

    centimeter_kilogram_force: UnitConstant
    cm_kg_mathrm_f: UnitConstant
    dyne_centimeter: UnitConstant
    foot_kilogram_force: UnitConstant
    mathrm_ft_mathrm_kg_mathrm_f: UnitConstant
    foot_pound_force: UnitConstant
    mathrm_ft_mathrm_lb_mathrm_f: UnitConstant
    foot_poundal: UnitConstant
    in_pound_force: UnitConstant
    in_mathrm_lb_mathrm_f: UnitConstant
    inch_ounce_force: UnitConstant
    in_mathrm_OZ_mathrm_f: UnitConstant
    meter_kilogram_force: UnitConstant
    mathrm_m_mathrm_kg_mathrm_f: UnitConstant
    newton_centimeter: UnitConstant
    N_cm: UnitConstant
    newton_meter: UnitConstant

class TurbulenceEnergyDissipationRateUnits:
    """Unit constants for Turbulence Energy Dissipation Rate."""
    __slots__: tuple[()]

    square_foot_per_cubic_second: UnitConstant
    mathrm_ft_2_mathrm_s_3_or_sq_ft_sec_3: UnitConstant
    ft_2_s_3: UnitConstant
    sq_ft_sec_3: UnitConstant
    square_meter_per_cubic_second: UnitConstant
    mathrm_m_2_mathrm_s_3: UnitConstant

class VelocityAngularUnits:
    """Unit constants for Velocity, Angular."""
    __slots__: tuple[()]

    degree_per_minute: UnitConstant
    deg_min_or_circ_mathrm_min: UnitConstant
    deg_min: UnitConstant
    circ_min: UnitConstant
    degree_per_second: UnitConstant
    deg_s_or_circ_s: UnitConstant
    deg_s: UnitConstant
    circ_s: UnitConstant
    grade_per_minute: UnitConstant
    gon_min_or_grad_min: UnitConstant
    gon_min: UnitConstant
    grad_min: UnitConstant
    radian_per_minute: UnitConstant
    mathrm_rad_mathrm_min: UnitConstant
    radian_per_second: UnitConstant
    mathrm_rad_mathrm_s: UnitConstant
    revolution_per_minute: UnitConstant
    rev_m_or_rpm: UnitConstant
    rev_m: UnitConstant
    rpm: UnitConstant
    revolution_per_second: UnitConstant
    rev_s_or_rps: UnitConstant
    rev_s: UnitConstant
    rps: UnitConstant
    turn_per_minute: UnitConstant
    tr_min: UnitConstant

class VelocityLinearUnits:
    """Unit constants for Velocity, Linear."""
    __slots__: tuple[()]

    foot_per_hour: UnitConstant
    ft_h_or_ft_hr_or_fph: UnitConstant
    ft_h: UnitConstant
    ft_hr: UnitConstant
    fph: UnitConstant
    foot_per_minute: UnitConstant
    ft_min_or_fpm: UnitConstant
    ft_min: UnitConstant
    fpm: UnitConstant
    foot_per_second: UnitConstant
    ft_s_or_fps: UnitConstant
    ft_s: UnitConstant
    fps: UnitConstant
    inch_per_second: UnitConstant
    in_s_or_ips: UnitConstant
    in_s: UnitConstant
    ips: UnitConstant
    international_knot: UnitConstant
    knot: UnitConstant
    kilometer_per_hour: UnitConstant
    km_h_ot_kph: UnitConstant
    kilometer_per_second: UnitConstant
    km_s: UnitConstant
    meter_per_second: UnitConstant
    mathrm_m_mathrm_s: UnitConstant
    mile_per_hour: UnitConstant
    mathrm_mi_mathrm_h_or_mathrm_mi_mathrm_hr_or_mph: UnitConstant
    mi_h: UnitConstant
    mi_hr: UnitConstant
    mph: UnitConstant

class ViscosityDynamicUnits:
    """Unit constants for Viscosity, Dynamic."""
    __slots__: tuple[()]

    centipoise: UnitConstant
    cP_or_cPo: UnitConstant
    cP: UnitConstant
    cPo: UnitConstant
    dyne_second_per_square_centimeter: UnitConstant
    dyn_s_mathrm_cm_2: UnitConstant
    kilopound_second_per_square_meter: UnitConstant
    kip_mathrm_s_mathrm_m_2: UnitConstant
    millipoise: UnitConstant
    mP_or_mPo: UnitConstant
    mP: UnitConstant
    mPo: UnitConstant
    newton_second_per_square_meter: UnitConstant
    mathrm_N_mathrm_s_mathrm_m_2: UnitConstant
    pascal_second: UnitConstant
    Pa_s_or_PI: UnitConstant
    Pa_s: UnitConstant
    PI: UnitConstant
    poise: UnitConstant
    P_or_Po: UnitConstant
    P: UnitConstant
    Po: UnitConstant
    pound_force_hour_per_square_foot: UnitConstant
    mathrm_lb_mathrm_f_mathrm_h_mathrm_ft_2_or_mathrm_lb_mathrm_hr_mathrm_sq_ft: UnitConstant
    lb_f_h_ft_2: UnitConstant
    lb_hr_sq_ft: UnitConstant
    pound_force_second_per_square_foot: UnitConstant
    mathrm_lb_mathrm_f_mathrm_s_mathrm_ft_2_or_mathrm_lb_mathrm_sec_mathrm_sq_ft: UnitConstant
    lb_f_s_ft_2: UnitConstant
    lb_sec_sq_ft: UnitConstant

class ViscosityKinematicUnits:
    """Unit constants for Viscosity, Kinematic."""
    __slots__: tuple[()]

    centistokes: UnitConstant
    cSt: UnitConstant
    millistokes: UnitConstant
    mSt: UnitConstant
    square_centimeter_per_second: UnitConstant
    mathrm_cm_2_mathrm_s: UnitConstant
    square_foot_per_hour: UnitConstant
    mathrm_ft_2_mathrm_h_or_mathrm_ft_2_mathrm_hr: UnitConstant
    ft_2_h: UnitConstant
    ft_2_hr: UnitConstant
    square_foot_per_second: UnitConstant
    mathrm_ft_2_mathrm_s: UnitConstant
    square_meters_per_second: UnitConstant
    mathrm_m_2_mathrm_s: UnitConstant
    stokes: UnitConstant
    St: UnitConstant

class VolumeUnits:
    """Unit constants for Volume."""
    __slots__: tuple[()]

    acre_foot: UnitConstant
    ac_ft: UnitConstant
    acre_inch: UnitConstant
    ac_in: UnitConstant
    barrel_us_liquid: UnitConstant
    bbl_US_liq: UnitConstant
    barrel_us_petro: UnitConstant
    bbl: UnitConstant
    board_foot_measure: UnitConstant
    BM_or_fbm: UnitConstant
    BM: UnitConstant
    fbm: UnitConstant
    bushel_us_dry: UnitConstant
    bu_US_dry: UnitConstant
    centiliter: UnitConstant
    cl_or_cL: UnitConstant
    cL: UnitConstant
    cord: UnitConstant
    cord_or_cd: UnitConstant
    cord_foot: UnitConstant
    cord_ft: UnitConstant
    cubic_centimeter: UnitConstant
    mathrm_cm_3_or_cc: UnitConstant
    cm_3: UnitConstant
    cubic_decameter: UnitConstant
    dam_3: UnitConstant
    cubic_decimeter: UnitConstant
    mathrm_dm_3: UnitConstant
    cubic_foot: UnitConstant
    cu_ft_or_ft_3: UnitConstant
    cu_ft: UnitConstant
    ft_3: UnitConstant
    cubic_inch: UnitConstant
    cu_in_or_mathrm_in_3: UnitConstant
    cu_in: UnitConstant
    in_3: UnitConstant
    cubic_kilometer: UnitConstant
    mathrm_km_3: UnitConstant
    cubic_meter: UnitConstant
    mathrm_m_3: UnitConstant
    cubic_micrometer: UnitConstant
    mu_mathrm_m_3: UnitConstant
    cubic_mile_us_intl: UnitConstant
    cu_mi: UnitConstant
    cubic_millimeter: UnitConstant
    mathrm_mm_3: UnitConstant
    cubic_yard: UnitConstant
    cu_yd_or_mathrm_yd_3: UnitConstant
    cu_yd: UnitConstant
    yd_3: UnitConstant
    decast_re: UnitConstant
    dast: UnitConstant
    deciliter: UnitConstant
    dl_or_dL: UnitConstant
    dl: UnitConstant
    dL: UnitConstant
    fluid_drachm_uk: UnitConstant
    fl_dr_UK: UnitConstant
    fluid_dram_us: UnitConstant
    fl_dr_US_liq: UnitConstant
    fluid_ounce_us: UnitConstant
    fl_oz: UnitConstant
    gallon_imperial_uk: UnitConstant
    gal_UK_or_Imp_gal: UnitConstant
    gal_UK: UnitConstant
    Imp_gal: UnitConstant
    gallon_us_dry: UnitConstant
    gal_US_dry: UnitConstant
    gallon_us_liquid: UnitConstant
    gal: UnitConstant
    last: UnitConstant
    liter: UnitConstant
    unit_1_or_L: UnitConstant
    unit_1: UnitConstant
    microliter: UnitConstant
    mu_mathrm_l_or_mu_mathrm_L: UnitConstant
    mu_l: UnitConstant
    mu_L: UnitConstant
    milliliter: UnitConstant
    ml: UnitConstant
    mohr_centicube: UnitConstant
    pint_uk: UnitConstant
    pt_UK: UnitConstant
    pint_us_dry: UnitConstant
    pt_US_dry: UnitConstant
    pint_us_liquid: UnitConstant
    pt: UnitConstant
    quart_us_dry: UnitConstant
    qt_US_dry: UnitConstant
    st_re: UnitConstant
    tablespoon_metric: UnitConstant
    tbsp_Metric: UnitConstant
    tablespoon_us: UnitConstant
    tbsp: UnitConstant
    teaspoon_us: UnitConstant
    tsp: UnitConstant

class VolumeFractionOfIUnits:
    """Unit constants for Volume Fraction of "i"."""
    __slots__: tuple[()]

    cubic_centimeters_of_i_per_cubic_meter_total: UnitConstant
    mathrm_cm_mathrm_i_3_mathrm_m_3_or_mathrm_cc_mathrm_i_mathrm_m_3: UnitConstant
    cm_i_3_m_3: UnitConstant
    cc_i_m_3: UnitConstant
    cubic_foot_of_i_per_cubic_foot_total: UnitConstant
    mathrm_ft_mathrm_i_3_mathrm_ft_3_or_mathrm_cft_mathrm_i_mathrm_cft: UnitConstant
    ft_i_3_ft_3: UnitConstant
    cft_i_cft: UnitConstant
    cubic_meters_of_i_per_cubic_meter_total: UnitConstant
    mathrm_m_mathrm_i_3_mathrm_m_3: UnitConstant
    gallons_of_i_per_gallon_total: UnitConstant
    mathrm_gal_mathrm_i_mathrm_gal: UnitConstant

class VolumetricCalorificHeatingValueUnits:
    """Unit constants for Volumetric Calorific (Heating) Value."""
    __slots__: tuple[()]

    british_thermal_unit_per_cubic_foot: UnitConstant
    mathrm_Btu_mathrm_ft_3_or_Btu_cft: UnitConstant
    Btu_ft_3: UnitConstant
    Btu_cft: UnitConstant
    british_thermal_unit_per_gallon_uk: UnitConstant
    Btu_gal_UK: UnitConstant
    british_thermal_unit_per_gallon_us: UnitConstant
    Btu_gal_US: UnitConstant
    calorie_per_cubic_centimeter: UnitConstant
    mathrm_cal_mathrm_cm_3_or_mathrm_cal_mathrm_cc: UnitConstant
    cal_cm_3: UnitConstant
    cal_cc: UnitConstant
    chu_per_cubic_foot: UnitConstant
    mathrm_Chu_mathrm_ft_3_or_mathrm_Chu_mathrm_cft: UnitConstant
    Chu_ft_3: UnitConstant
    Chu_cft: UnitConstant
    joule_per_cubic_meter: UnitConstant
    mathrm_J_mathrm_m_3: UnitConstant
    kilocalorie_per_cubic_foot: UnitConstant
    mathrm_kcal_mathrm_ft_3_or_mathrm_kcal_mathrm_cft: UnitConstant
    kcal_ft_3: UnitConstant
    kcal_cft: UnitConstant
    kilocalorie_per_cubic_meter: UnitConstant
    mathrm_kcal_mathrm_m_3: UnitConstant
    therm_100_k_btu: UnitConstant
    thm_cft: UnitConstant

class VolumetricCoefficientOfExpansionUnits:
    """Unit constants for Volumetric Coefficient of Expansion."""
    __slots__: tuple[()]

    gram_per_cubic_centimeter_per_kelvin_or_degree_celsius: UnitConstant
    mathrm_g_mathrm_cm_3_mathrm_K_or_g_cc_circ_mathrm_C: UnitConstant
    g_cm_3_K: UnitConstant
    g_cc_circ_C: UnitConstant
    kilogram_per_cubic_meter_per_kelvin_or_degree_celsius: UnitConstant
    mathrm_kg_mathrm_m_3_mathrm_K_or_mathrm_kg_mathrm_m_3_circ_C: UnitConstant
    kg_m_3_K: UnitConstant
    kg_m_3_circ_C: UnitConstant
    pound_per_cubic_foot_per_degree_fahrenheit_or_degree_rankine: UnitConstant
    mathrm_lb_mathrm_ft_3_circ_mathrm_R_or_mathrm_lb_mathrm_cft_circ_mathrm_F: UnitConstant
    lb_ft_3_circ_R: UnitConstant
    lb_cft_circ_F: UnitConstant
    pound_per_cubic_foot_per_kelvin_or_degree_celsius: UnitConstant
    mathrm_lb_mathrm_ft_3_mathrm_K_or_mathrm_lb_mathrm_cft_circ_mathrm_C: UnitConstant
    lb_ft_3_K: UnitConstant
    lb_cft_circ_C: UnitConstant

class VolumetricFlowRateUnits:
    """Unit constants for Volumetric Flow Rate."""
    __slots__: tuple[()]

    cubic_feet_per_day: UnitConstant
    mathrm_ft_3_mathrm_d_or_mathrm_cft_mathrm_da_or_cfd: UnitConstant
    ft_3_d: UnitConstant
    cft_da: UnitConstant
    cfd: UnitConstant
    cubic_feet_per_hour: UnitConstant
    mathrm_ft_3_mathrm_h_or_mathrm_cft_mathrm_hr_or_cfh: UnitConstant
    ft_3_h: UnitConstant
    cft_hr: UnitConstant
    cfh: UnitConstant
    cubic_feet_per_minute: UnitConstant
    mathrm_ft_3_mathrm_min_or_mathrm_cft_mathrm_min_or_cfm: UnitConstant
    ft_3_min: UnitConstant
    cft_min: UnitConstant
    cfm: UnitConstant
    cubic_feet_per_second: UnitConstant
    mathrm_ft_3_mathrm_s_or_cft_sec_or_cfs: UnitConstant
    ft_3_s: UnitConstant
    cft_sec: UnitConstant
    cfs: UnitConstant
    cubic_meters_per_day: UnitConstant
    mathrm_m_3_mathrm_d: UnitConstant
    cubic_meters_per_hour: UnitConstant
    mathrm_m_3_mathrm_h: UnitConstant
    cubic_meters_per_minute: UnitConstant
    mathrm_m_3_min: UnitConstant
    cubic_meters_per_second: UnitConstant
    mathrm_m_3_mathrm_s: UnitConstant
    gallons_per_day: UnitConstant
    gal_d_or_gpd_or_gal_da: UnitConstant
    gal_d: UnitConstant
    gpd: UnitConstant
    gal_da: UnitConstant
    gallons_per_hour: UnitConstant
    gal_h_or_gph_or_gal_hr: UnitConstant
    gal_h: UnitConstant
    gph: UnitConstant
    gal_hr: UnitConstant
    gallons_per_minute: UnitConstant
    gal_min_or_gpm: UnitConstant
    gal_min: UnitConstant
    gpm: UnitConstant
    gallons_per_second: UnitConstant
    gal_s_or_gps_or_gal_sec: UnitConstant
    gal_s: UnitConstant
    gps: UnitConstant
    gal_sec: UnitConstant
    liters_per_day: UnitConstant
    unit_1_d: UnitConstant
    liters_per_hour: UnitConstant
    unit_1_h: UnitConstant
    liters_per_minute: UnitConstant
    liters_per_second: UnitConstant
    unit_1_s: UnitConstant

class VolumetricFluxUnits:
    """Unit constants for Volumetric Flux."""
    __slots__: tuple[()]

    cubic_feet_per_square_foot_per_day: UnitConstant
    mathrm_ft_3_left_mathrm_ft_2_mathrm_d_right_or_mathrm_cft_mathrm_sqft_da: UnitConstant
    ft_3_left_ft_2_dright: UnitConstant
    cft_sqft_da: UnitConstant
    cubic_feet_per_square_foot_per_hour: UnitConstant
    mathrm_ft_3_left_mathrm_ft_2_mathrm_h_right_or_mathrm_cft_mathrm_sqft_hr: UnitConstant
    ft_3_left_ft_2_hright: UnitConstant
    cft_sqft_hr: UnitConstant
    cubic_feet_per_square_foot_per_minute: UnitConstant
    mathrm_ft_3_left_mathrm_ft_2_min_right_or_mathrm_cft_sqft_min: UnitConstant
    ft_3_left_ft_2_min_right: UnitConstant
    cft_sqft_min: UnitConstant
    cubic_feet_per_square_foot_per_second: UnitConstant
    mathrm_ft_3_left_mathrm_ft_2_mathrm_s_right_or_cft_sqft_sec: UnitConstant
    ft_3_left_ft_2_sright: UnitConstant
    cft_sqft_sec: UnitConstant
    cubic_meters_per_square_meter_per_day: UnitConstant
    mathrm_m_3_left_mathrm_m_2_mathrm_d_right: UnitConstant
    cubic_meters_per_square_meter_per_hour: UnitConstant
    mathrm_m_3_left_mathrm_m_2_mathrm_h_right: UnitConstant
    cubic_meters_per_square_meter_per_minute: UnitConstant
    mathrm_m_3_left_mathrm_m_2_mathrm_min_right: UnitConstant
    cubic_meters_per_square_meter_per_second: UnitConstant
    mathrm_m_3_left_mathrm_m_2_mathrm_s_right: UnitConstant
    gallons_per_square_foot_per_day: UnitConstant
    mathrm_gal_left_mathrm_ft_2_mathrm_d_right_or_gal_sqft_da: UnitConstant
    gal_left_ft_2_dright: UnitConstant
    gal_sqft_da: UnitConstant
    gallons_per_square_foot_per_hour: UnitConstant
    mathrm_gal_left_mathrm_ft_2_mathrm_h_right_or_gal_sqft_hr: UnitConstant
    gal_left_ft_2_hright: UnitConstant
    gal_sqft_hr: UnitConstant
    gallons_per_square_foot_per_minute: UnitConstant
    mathrm_gal_left_mathrm_ft_2_mathrm_min_right_or_gal_sqft_min_or_gpm_sqft: UnitConstant
    gal_left_ft_2_minright: UnitConstant
    gal_sqft_min: UnitConstant
    gpm_sqft: UnitConstant
    gallons_per_square_foot_per_second: UnitConstant
    mathrm_gal_left_mathrm_ft_2_mathrm_s_right_or_gal_mathrm_sqft_mathrm_sec: UnitConstant
    gal_left_ft_2_sright: UnitConstant
    gal_sqft_sec: UnitConstant
    liters_per_square_meter_per_day: UnitConstant
    liters_per_square_meter_per_hour: UnitConstant
    liters_per_square_meter_per_minute: UnitConstant
    liters_per_square_meter_per_second: UnitConstant

class VolumetricMassFlowRateUnits:
    """Unit constants for Volumetric Mass Flow Rate."""
    __slots__: tuple[()]

    gram_per_second_per_cubic_centimeter: UnitConstant
    mathrm_g_left_mathrm_s_mathrm_cm_3_right_or_g_s_cc_or_mathrm_g_mathrm_cc_mathrm_sec: UnitConstant
    g_left_s_cm_3right: UnitConstant
    g_s_cc: UnitConstant
    g_cc_sec: UnitConstant
    kilogram_per_hour_per_cubic_foot: UnitConstant
    kg_h_ft_3_or_kg_hr_cft: UnitConstant
    kg_h_ft_3: UnitConstant
    kg_hr_cft: UnitConstant
    kilogram_per_hour_per_cubic_meter: UnitConstant
    kg_h_m3_or_kg_hr_cu_m: UnitConstant
    kg_h_m3: UnitConstant
    kg_hr_cu_m: UnitConstant
    kilogram_per_second_per_cubic_meter: UnitConstant
    mathrm_kg_left_mathrm_s_mathrm_m_3_right_or_kg_sec_cu_m: UnitConstant
    kg_left_s_m_3right: UnitConstant
    kg_sec_cu_m: UnitConstant
    pound_per_hour_per_cubic_foot: UnitConstant
    mathrm_lb_left_mathrm_h_mathrm_ft_3_right_or_mathrm_lb_mathrm_hr_mathrm_cft_or_PPH_cft: UnitConstant
    lb_left_h_ft_3right: UnitConstant
    lb_hr_cft: UnitConstant
    PPH_cft: UnitConstant
    pound_per_minute_per_cubic_foot: UnitConstant
    lb_min_mathrm_ft_3_or_lb_mathrm_min_mathrm_cft: UnitConstant
    lb_min_ft_3: UnitConstant
    lb_min_cft: UnitConstant
    pound_per_second_per_cubic_foot: UnitConstant
    b_s_ft_3_or_lb_sec_cft: UnitConstant
    b_s_ft_3: UnitConstant
    lb_sec_cft: UnitConstant

class WavenumberUnits:
    """Unit constants for Wavenumber."""
    __slots__: tuple[()]

    diopter: UnitConstant
    kayser: UnitConstant
    reciprocal_meter: UnitConstant
    unit_1_m: UnitConstant

def register_all_units() -> None: ...

