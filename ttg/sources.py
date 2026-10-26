"""Source registry and footnote numbering."""

from dataclasses import dataclass, field

from markupsafe import Markup, escape


@dataclass(frozen=True)
class Source:
    label: str
    url: str


SOURCES: dict[str, Source] = {
    "meijer": Source("Meijer et al. 2021, More than 1000 rivers account for 80% of global riverine plastic emissions into the ocean, Science Advances", "https://doi.org/10.1126/sciadv.aaz5803"),
    "meijer_data": Source("Meijer et al. 2021, supplementary data (river outfalls)", "https://doi.org/10.6084/m9.figshare.14515590"),
    "owid_meijer": Source("Our World in Data, Plastic waste emitted to the ocean, by country (Meijer et al. 2021)", "https://ourworldindata.org/grapher/plastic-waste-emitted-to-the-ocean"),
    "owid_mismanaged": Source("Our World in Data, Mismanaged plastic waste per capita (Meijer et al. 2021)", "https://ourworldindata.org/grapher/mismanaged-plastic-waste-per-capita"),
    "rr2025": Source("Resource Recycling, Plastic exports decline again in 2024 (2025)", "http://resource-recycling.com/plastics/2025/02/12/plastic-exports-decline-again-in-2024/"),
    "owid_trade": Source("Our World in Data, Plastic waste trade", "https://ourworldindata.org/plastic-waste-trade"),
    "owid_ocean": Source("Our World in Data, Where does the plastic in our oceans come from?", "https://ourworldindata.org/ocean-plastics"),
    "lebreton": Source("Lebreton et al. 2018, Evidence that the Great Pacific Garbage Patch is rapidly accumulating plastic, Scientific Reports", "https://doi.org/10.1038/s41598-018-22939-w"),
    "wip": Source("Works in Progress, Just bury your trash", "https://worksinprogress.co/issue/just-bury-your-trash/"),
    "epa2018": Source("EPA, Advancing Sustainable Materials Management: 2018 Fact Sheet", "https://www.epa.gov/sites/default/files/2021-01/documents/2018_ff_fact_sheet_dec_2020_fnl_508.pdf"),
    "japan_moe": Source("Japan Ministry of the Environment, Municipal solid waste emissions and disposal in FY2024 (2026)", "https://www.env.go.jp/en/press/press_01569.html"),
    "ggp": Source("San Francisco Recreation and Parks, Getting to Golden Gate Park", "https://sfrecpark.org/1159/Getting-to-Golden-Gate-Park"),
    "waste360_2011": Source("Waste360, Profiles in Garbage: latest EPA data (2013)", "https://www.waste360.com/industry-insights/profiles-in-garbage-latest-epa-data"),
    "pa_landfill": Source("Pennsylvania DEP, CES landfill permit renewal application: remaining life", "https://files.dep.state.pa.us/RegionalResources/NERO/NEROPortalFiles/CommunityInformation/ces-landfill/renewal-application/Permit%20Renewal%20remaining%20life.pdf"),
    "epa_lmop": Source("EPA, Basic information about landfill gas", "https://www.epa.gov/lmop/basic-information-about-landfill-gas"),
    "lmop_data": Source("EPA Landfill Methane Outreach Program, landfill-level data (2024)", "https://www.epa.gov/system/files/documents/2024-09/landfilllmopdata.xlsx"),
    "cdc_life": Source("CDC NCHS, Mortality in the United States, 2024 (Data Brief 548)", "https://www.cdc.gov/nchs/products/databriefs/db548.htm"),
    "nrc2007": Source("National Research Council 2007, Assessment of the Performance of Engineered Waste Containment Barriers, p. 65", "https://www.nationalacademies.org/read/11930/chapter/7"),
    "cusworth": Source("Cusworth et al. 2024, Quantifying methane emissions from United States landfills, Science", "https://doi.org/10.1126/science.adi7735"),
    "arc2024": Source("ARC (Amager Resource Center), Annual report 2024, p. 13", "https://a-r-c.dk/app/uploads/2025/07/ARCs-aarsrapport-2024.pdf"),
    "epa_food_methane": Source("EPA, Quantifying methane emissions from landfilled food waste", "https://epa.gov/land-research/quantifying-methane-emissions-landfilled-food-waste"),
    "waste360_capacity": Source("Waste360, Regional landfill capacity problems do not equate to national shortage (2015)", "https://www.waste360.com/operations/regional-landfill-capacity-problems-do-not-equate-national-shortage"),
    "epa_combustion": Source("EPA, Air emissions from MSW combustion facilities", "https://archive.epa.gov/epawaste/nonhaz/municipal/web/html/airem.html"),
    "warm_plastics": Source("EPA, WARM v16: Containers, Packaging, and Non-Durable Good Materials chapters (2023)", "https://www.epa.gov/system/files/documents/2023-12/warm_containers_packaging_and_non-durable_goods_materials_v16_dec.pdf"),
    "zheng_suh": Source("Zheng and Suh 2019, Strategies to reduce the global carbon footprint of plastics, Nature Climate Change", "https://doi.org/10.1038/s41558-019-0459-z"),
    "egrid": Source("EPA, Greenhouse gas equivalencies calculator: calculations and references (eGRID2022)", "https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references"),
    "minderoo": Source("Minderoo Foundation, The Plastic Waste Makers Index (2021), p. 63", "https://cdn.minderoo.org/assets/uploads/resources/plastic-waste-makers-index-2021/20211105-plastic-waste-makers-index.pdf"),
    "epa_ghg": Source("EPA, Inventory of U.S. Greenhouse Gas Emissions and Sinks: 1990-2022, Table ES-2 (2024)", "https://www.epa.gov/system/files/documents/2024-04/us-ghg-inventory-2024-main-text_04-18-2024.pdf"),
    "desnz": Source("UK Department for Energy Security and Net Zero, Greenhouse gas reporting: conversion factors 2025", "https://assets.publishing.service.gov.uk/media/6846b6ea57f3515d9611f0dd/ghg-conversion-factors-2025-flat-format.xlsx"),
    "shaka": Source("Shaka Guide, San Francisco to Lake Tahoe", "https://www.shakaguide.com/article/lake-tahoe/san-francisco-to-lake-tahoe"),
    "epa_vehicle": Source("EPA, Greenhouse gas emissions from a typical passenger vehicle", "https://www.epa.gov/greenvehicles/greenhouse-gas-emissions-typical-passenger-vehicle"),
    "edinburgh": Source("University of Edinburgh, The truth about cats and dogs and climate", "https://impact.ed.ac.uk/research/climate-environmental-crisis/truth-about-cats-and-dogs-and-climate/"),
    "ers_cheese": Source("USDA Economic Research Service, Per capita consumption of selected cheese varieties", "https://www.ers.usda.gov/media/5522/per-capita-consumption-of-selected-cheese-varieties-annual.csv"),
    "berners_lee": Source("Mike Berners-Lee, How Bad Are Bananas? (2020 edition), p. 131", "https://profilebooks.com/wp-content/uploads/wpallimport/files/PDFs/9781788163811_preview.pdf"),
    "poore": Source("Poore and Nemecek 2018, Reducing food's environmental impacts through producers and consumers, Science", "https://doi.org/10.1126/science.aaq0216"),
    "ipcc2006": Source("IPCC 2006 Guidelines for National Greenhouse Gas Inventories, Vol. 2, Ch. 1", "https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/V2_1_Ch1_Introduction.pdf"),
    "danish_epa": Source("Danish Environmental Protection Agency 2018, Life Cycle Assessment of grocery carrier bags", "https://www2.mst.dk/Udgiv/publications/2018/02/978-87-93614-73-4.pdf"),
    "epa_plastics": Source("EPA, Plastics: Material-Specific Data", "https://www.epa.gov/facts-and-figures-about-materials-waste-and-recycling/plastics-material-specific-data"),
    "lbc2022": Source("The Last Beach Cleanup and Beyond Plastics, The Real Truth About the U.S. Plastic Recycling Rate (2022), Table 2", "https://www.lastbeachcleanup.org/_files/ugd/dba7d7_5ae55cdb66d241239e8ae123c96ec9b8.pdf"),
    "greenpeace2022": Source("Greenpeace USA, Circular Claims Fall Flat Again: 2022 Update, Table A-3", "https://storage.googleapis.com/planet4-usa-stateless/2024/11/7287b658-gpus_finalreport_2022.pdf"),
    "trp2020": Source("The Recycling Partnership, 2019 West Coast Contamination Initiative Research Report (2020), p. 10", "https://recyclingpartnership.org/wp-content/uploads/2020/04/The-Recycling-Partnership_WCCI-Report_April-2020_Final.pdf"),
    "wri_dac": Source("World Resources Institute, Direct Air Capture: resource considerations and costs for carbon removal", "https://www.wri.org/insights/direct-air-capture-resource-considerations-and-costs-carbon-removal"),
    "alu_lca": Source("The Aluminum Association, Life Cycle Assessment of North American Aluminum Cans (2021), Sec. 2.1", "https://www.aluminum.org/sites/default/files/2021-10/2021AluminumCanLCAReportFullVersion.pdf"),
    "epa_doubt": Source("EPA, What you can do to improve the recycling rate", "https://www.epa.gov/circulareconomy/what-you-can-do-improve-recycling-rate"),
    "uk_ea_bags": Source("UK Environment Agency 2011, Life cycle assessment of supermarket carrier bags, Table 3.1", "https://assets.publishing.service.gov.uk/media/5a7bff74ed915d01ba1ca7c7/scho0711buan-e-e.pdf"),
}

METHODS = {
    "ocean": "How we calculated: Ocean",
    "landfills": "How we calculated: Landfills",
    "climate": "How we calculated: Climate",
    "bin": "How we calculated: In the bin",
}


@dataclass
class Notes:
    """Numbers sources by first use; each section lists the ones it cited."""

    order: list[str] = field(default_factory=list)
    by_section: dict[str, list[str]] = field(default_factory=dict)
    section: str = ""

    def start(self, section: str) -> str:
        self.section = section
        self.by_section.setdefault(section, [])
        return ""

    def _use(self, key: str) -> int:
        if key not in SOURCES and not key.startswith("calc"):
            raise KeyError(f"unknown source {key}")
        if key not in self.order:
            self.order.append(key)
        cited = self.by_section[self.section]
        if key not in cited:
            cited.append(key)
        return self.order.index(key) + 1

    def fn(self, *keys: str) -> Markup:
        """Footnote markers for one number; calc:<section> points at that section's methods."""
        nums = sorted({self._use(key) for key in keys})
        marks = [f'<a href="#{self.section}-n{n}" aria-label="Source {n}">{n}</a>' for n in nums]
        return Markup(f'<sup class="fn">{",".join(marks)}</sup>')

    def cite(self, key: str, label: str | None = None) -> Markup:
        """Inline link to a source by name, for source columns."""
        self._use(key)
        s = SOURCES[key]
        return Markup(f'<a href="{escape(s.url)}">{escape(label or s.label)}</a>')

    def _item(self, key: str, anchor: str) -> str:
        n = self.order.index(key) + 1
        if key.startswith("calc"):
            sec = key.split(":", 1)[1]
            body = f'<a href="#{sec}-methods" class="open-methods">{escape(METHODS[sec])}</a>'
        else:
            s = SOURCES[key]
            body = f'<a href="{escape(s.url)}">{escape(s.label)}</a>'
        return f'<li id="{anchor}"><span class="k">{n}</span><span>{body}</span></li>'

    def section_list(self) -> Markup:
        keys = sorted(self.by_section[self.section], key=self.order.index)
        items = "".join(self._item(k, f"{self.section}-n{self.order.index(k) + 1}") for k in keys)
        return Markup(f'<div class="sources"><h3>Sources</h3><ol>{items}</ol></div>')

    def all(self) -> Markup:
        items = "".join(self._item(k, f"src-{i + 1}") for i, k in enumerate(self.order))
        return Markup(f"<ol>{items}</ol>")
