"""Every figure the page draws, with derived values computed from sourced inputs."""

from dataclasses import dataclass, field

KG_PER_LB = 0.45359237
LB_PER_SHORT_TON = 2000
KG_PER_SHORT_TON = LB_PER_SHORT_TON * KG_PER_LB
CU_FT_PER_CU_YD = 27


@dataclass(frozen=True)
class Range:
    low: float
    high: float

    def scale(self, k: float) -> "Range":
        return Range(self.low * k, self.high * k)

    @property
    def mid(self) -> float:
        return (self.low + self.high) / 2


@dataclass(frozen=True)
class Country:
    name: str
    tonnes: float
    share_pct: float


@dataclass(frozen=True)
class Ocean:
    # Meijer et al. 2021, model year 2015: country sum and the Pasig outfall (Figshare dataset)
    world_tonnes: float = 979_458
    us_tonnes: float = 2_431
    pasig_tonnes: float = 62_592
    philippines_tonnes: float = 356_371
    # 2019 populations for both per-person figures: Census (US), World Bank (Philippines)
    us_population: float = 328.24e6
    philippines_population: float = 110.8e6
    # UK Environment Agency 2011, conventional HDPE carrier bag
    bag_g: float = 8.12
    exports_mismanaged_tonnes: float = 202_000
    exports_to_sea: Range = Range(0.01, 0.07)
    countries: tuple[Country, ...] = field(default_factory=tuple)

    @property
    def us_share_pct(self) -> float:
        return self.us_tonnes / self.world_tonnes * 100

    @property
    def per_american_g(self) -> float:
        return self.us_tonnes * 1e6 / self.us_population

    @property
    def pasig_vs_us(self) -> float:
        return self.pasig_tonnes / self.us_tonnes

    @property
    def export_tonnes(self) -> Range:
        return self.exports_to_sea.scale(self.exports_mismanaged_tonnes)

    @property
    def us_with_exports(self) -> Range:
        e = self.export_tonnes
        return Range(self.us_tonnes + e.low, self.us_tonnes + e.high)

    @property
    def philippines_kg_per_person(self) -> float:
        return self.philippines_tonnes * 1000 / self.philippines_population

    @property
    def philippines_bags(self) -> float:
        return self.philippines_kg_per_person * 1000 / self.bag_g


@dataclass(frozen=True)
class Landfill:
    landfilled_short_tons: float = 146.1e6
    population: float = 327.2e6
    # compacted density in a modern landfill (PA filing 0.6188; EPA LMOP median about 0.64)
    density_short_tons_per_cu_yd: Range = Range(0.62, 0.62)
    old_average_density: float = 0.3695  # 739 lb per cu yd, 1997 national average
    lifetime_years: float = 79
    depth_ft: float = 100
    bed_in: tuple[float, float] = (38, 75)
    doormat_ft: tuple[float, float] = (2, 3)
    us_landfill_share: float = 0.50
    japan_final_disposal_share: float = 0.0803  # FY2024
    golden_gate_park_acres: float = 1017

    @property
    def lb_per_person_year(self) -> float:
        return self.landfilled_short_tons * LB_PER_SHORT_TON / self.population

    @property
    def cu_ft_per_person_year(self) -> Range:
        # denser trash takes less room, so high density gives the low volume
        d = self.density_short_tons_per_cu_yd
        tons = self.lb_per_person_year / LB_PER_SHORT_TON
        return Range(tons / d.high * CU_FT_PER_CU_YD, tons / d.low * CU_FT_PER_CU_YD)

    @property
    def cu_ft_lifetime(self) -> Range:
        return self.cu_ft_per_person_year.scale(self.lifetime_years)

    @property
    def footprint_sq_ft(self) -> Range:
        return self.cu_ft_lifetime.scale(1 / self.depth_ft)

    @property
    def bed_sq_ft(self) -> float:
        return self.bed_in[0] * self.bed_in[1] / 144

    @property
    def japan_factor(self) -> float:
        return self.us_landfill_share / self.japan_final_disposal_share

    @property
    def japan_footprint_sq_ft(self) -> Range:
        return self.footprint_sq_ft.scale(1 / self.japan_factor)

    @property
    def doormat_sq_ft(self) -> float:
        return self.doormat_ft[0] * self.doormat_ft[1]

    @property
    def old_density_footprint_sq_ft(self) -> float:
        tons = self.lb_per_person_year / LB_PER_SHORT_TON
        return tons / self.old_average_density * CU_FT_PER_CU_YD * self.lifetime_years / self.depth_ft

    @property
    def golden_gate_pile_ft(self) -> Range:
        d = self.density_short_tons_per_cu_yd
        area = self.golden_gate_park_acres * 43_560
        low = self.landfilled_short_tons / d.high * CU_FT_PER_CU_YD / area
        high = self.landfilled_short_tons / d.low * CU_FT_PER_CU_YD / area
        return Range(low, high)


@dataclass(frozen=True)
class Climate:
    resin_kg_per_kg: float = 1.68
    forming_markup: float = 0.49
    burn_kg_per_kg: float = 3.08
    kwh_per_kg: float = 2.3
    grid_kg_per_kwh: float = 0.373
    bury_kg_per_kg: float = 0.02
    plastic_kg_per_person: float = 53
    # EPA GHG Inventory 1990-2022: 6,343.2 MMT CO2e gross in 2022 over 334.0M people
    us_footprint_kg: float = 18_990
    gasoline_kg_per_gal: float = 8.887
    # K4 comparisons
    flight_km_each_way: float = 8_630
    flight_kg_per_pkm: float = 0.06926
    tahoe_miles_each_way: Range = Range(190, 220)
    car_kg_per_mile: float = 0.4
    tahoe_trips: int = 5
    dog_kg: Range = Range(530, 770)
    cheese_lb_per_person: float = 40.15  # USDA ERS, 2023 (revised)
    cheese_kg_co2e_per_kg: float = 23.88

    @property
    def make(self) -> float:
        return self.resin_kg_per_kg * (1 + self.forming_markup)

    @property
    def energy_back(self) -> float:
        return self.kwh_per_kg * self.grid_kg_per_kwh

    @property
    def net_burned(self) -> float:
        return self.make + self.burn_kg_per_kg - self.energy_back

    @property
    def net_buried(self) -> float:
        return self.make + self.bury_kg_per_kg

    @property
    def plastic_year(self) -> Range:
        return Range(self.net_buried * self.plastic_kg_per_person, self.net_burned * self.plastic_kg_per_person)

    @property
    def footprint_pct(self) -> Range:
        return self.plastic_year.scale(100 / self.us_footprint_kg)

    @property
    def flight_round_trip(self) -> float:
        return 2 * self.flight_km_each_way * self.flight_kg_per_pkm

    @property
    def tahoe(self) -> Range:
        return self.tahoe_miles_each_way.scale(2 * self.car_kg_per_mile * self.tahoe_trips)

    @property
    def cheese_year(self) -> float:
        return self.cheese_lb_per_person * KG_PER_LB * self.cheese_kg_co2e_per_kg

    @property
    def dog_to_plastic(self) -> float:
        return self.dog_kg.high / self.plastic_year.high

    @property
    def gallons(self) -> Range:
        return self.plastic_year.scale(1 / self.gasoline_kg_per_gal)


@dataclass(frozen=True)
class Bin:
    plastic_generated_m: float = 35.7
    recycled_m: float = 3.09
    energy_m: float = 5.6
    landfilled_m: float = 27.0
    can_g: float = 12.99
    can_saving_t_per_short_ton: float = 9.15
    # EPA 2018 recycling rates by resin (Greenpeace 2022, Table A-3)
    recycled_pct_by_resin: tuple[tuple[str, float], ...] = (
        ("PET (#1)", 18.5),
        ("HDPE (#2)", 8.9),
        ("LDPE (#4)", 4.3),
        ("PS (#6)", 0.9),
        ("PP (#5)", 0.6),
        ("PVC (#3)", 0.0),
    )

    @property
    def per_can_kg(self) -> float:
        return self.can_saving_t_per_short_ton * 1000 / KG_PER_SHORT_TON * self.can_g / 1000

    @property
    def landfill_share(self) -> float:
        return self.landfilled_m / self.plastic_generated_m


OCEAN = Ocean()
LANDFILL = Landfill()
CLIMATE = Climate()
BIN = Bin()


def check_copy() -> list[str]:
    """Compare derived values against the numbers written in the copy; return mismatches."""
    o, l, c, b = OCEAN, LANDFILL, CLIMATE, BIN
    checks: list[tuple[str, float, float, float]] = [
        ("C1 26x", o.pasig_vs_us, 26, 0.5),
        ("O1 0.25%", o.us_share_pct, 0.25, 0.01),
        ("O1 7 g per American", o.per_american_g, 7, 0.5),
        ("O1b-4 exports low", o.export_tonnes.low, 2_000, 60),
        ("O1b-4 exports high", o.export_tonnes.high, 14_100, 100),
        ("O1b-4 US total low", o.us_with_exports.low, 4_400, 60),
        ("O1b-4 US total high", o.us_with_exports.high, 16_600, 60),
        ("O1b-5 Pasig vs US worst case", o.pasig_tonnes / o.us_with_exports.high, 3.8, 0.05),
        ("O1b-5 Pasig vs US best case", o.pasig_tonnes / o.us_with_exports.low, 14, 0.5),
        ("O2c Philippines kg", o.philippines_kg_per_person, 3.2, 0.05),
        ("O4 bags", o.philippines_bags, 400, 10),
        ("L2b lb", l.lb_per_person_year, 890, 10),
        ("L2b cu ft", l.cu_ft_per_person_year.low, 19, 0.5),
        ("L2c cu ft", l.cu_ft_lifetime.low, 1_540, 10),
        ("L2d sq ft", l.footprint_sq_ft.low, 15, 0.5),
        ("L2d bed", l.bed_sq_ft, 20, 0.5),
        ("L5 old density footprint", l.old_density_footprint_sq_ft, 26, 0.5),
        ("L2e Japan factor", l.japan_factor, 6.2, 0.05),
        ("L2e sq ft", l.japan_footprint_sq_ft.low, 2.5, 0.05),
        ("L2f ft", l.golden_gate_pile_ft.low, 144, 1),
        ("K2 make", c.make, 2.5, 0.05),
        ("K2 energy back", c.energy_back, 0.86, 0.01),
        ("K2 net burned", c.net_burned, 4.7, 0.05),
        ("K1 low", c.plastic_year.low, 130, 6),
        ("K1 high", c.plastic_year.high, 250, 5),
        ("K1 pct low", c.footprint_pct.low, 0.7, 0.05),
        ("K1 pct high", c.footprint_pct.high, 1.3, 0.05),
        ("C3 3x", c.dog_to_plastic, 3, 0.2),
        ("K4 cheese", c.cheese_year, 435, 3),
        ("K4 flight", c.flight_round_trip, 1_195, 5),
        ("K7b gal low", c.gallons.low, 15, 0.6),
        ("K7b gal high", c.gallons.high, 28, 0.6),
        ("R2f per can", b.per_can_kg, 0.13, 0.005),
        ("R6 lb per can", b.per_can_kg / KG_PER_LB, 0.3, 0.02),
        ("R5 cans", c.plastic_year.high / b.per_can_kg, 1_900, 60),
        ("R3 three quarters", b.landfill_share, 0.75, 0.02),
        ("R punch 76%", b.landfill_share * 100, 76, 0.5),
    ]
    return [
        f"{name}: computed {got:.4g}, copy says {want:g}"
        for name, got, want, tol in checks
        if abs(got - want) > tol
    ]
