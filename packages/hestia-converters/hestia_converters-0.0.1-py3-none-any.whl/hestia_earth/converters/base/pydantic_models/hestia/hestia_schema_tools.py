import heapq
import json
from collections import defaultdict
from itertools import groupby
from pathlib import Path
from typing import List, Optional
from hestia_earth.utils.api import node_to_path

from . import Indicator, Input


def squash_by_uuid(entries: list) -> list:
    uuid_strs = {e['flow']['@id'] for e in entries}
    new_list = []
    for uuid_str in uuid_strs:
        entries_with_uuid = [e for e in entries if e['flow']['@id'] == uuid_str]
        if len(entries_with_uuid) > 1:
            pass
        template_dict = entries_with_uuid[0] | {'processed': False}
        new_amount = sum([e_d['amount'] for e_d in entries_with_uuid])
        new_list.append(template_dict | {'amount': new_amount})
    return new_list


dummy_indicator = {
    "term": {
        "@id": "landTransformation20YearAverageDuringCycle",
        "termType": "resourceUse",
        "units": "m2 / year"
    },
    "value": 0,
    "landCover": {
        "@id": "forest",
    },
    "previousLandCover":
        {
            "@id": "forest",
        },
    "methodModelDescription": "ECOALIM"
}


def _indicator_group_key(indicator: Indicator):
    return [indicator.term.id,
            indicator.key.id if indicator.key else None,
            indicator.operation.id if indicator.operation else None,
            indicator.methodModel.id if indicator.methodModel else None,
            indicator.transformation.id if indicator.transformation else None,
            indicator.country.id if indicator.country else None,
            indicator.landCover.id if indicator.landCover else None,
            indicator.previousLandCover.id if indicator.previousLandCover else None,
            tuple({i.id for i in indicator.inputs}) if indicator.inputs else None,
            ]


def _inputs_group_key(input_entry: Input):
    # term.@id, dates, startDate, endDate, isAnimalFeed, producedInCycle, transport.term.@id, operation.@id, country.@id, region.@id, impactAssessment.id, site.id
    return [input_entry.term.id if input_entry.term else None,
            # input_entry.dates,
            # input_entry.startDate,
            # input_entry.endDate,
            # input_entry.isAnimalFeed,
            # input_entry.transport.term.id if input_entry.transport else None,
            # input_entry.operation.id,
            # input_entry.country.id,
            # input_entry.region.id,
            # input_entry.impactAssessment.id,
            # input_entry.site.id,
            # indicator.country.id if indicator.country else None,
            # indicator.landCover.id if indicator.landCover else None,
            # indicator.previousLandCover.id if indicator.previousLandCover else None,
            # tuple({i.id for i in indicator.inputs}) if indicator.inputs else None,
            ]


def group_indicators(resulting_indicators):
    grouped_enviVals = defaultdict(list)
    for k, v in groupby(resulting_indicators, key=_indicator_group_key):
        grouped_enviVals[tuple(k)].extend(list(v))
    return grouped_enviVals


def group_inputs(group_inputs):
    grouped_enviVals = defaultdict(list)
    for k, v in groupby(group_inputs, key=_inputs_group_key):
        grouped_enviVals[tuple(k)].extend(list(v))
    return grouped_enviVals


proxy_terms_with_inputs_field = ['pesticideToAirInputsProduction',
                                 'pesticideToAirIndoorInputsProduction',
                                 'pesticideToAirUrbanCloseToGroundInputsProduction',
                                 'pesticideToAirOtherHigherAltitudesInputsProduction',
                                 'pesticideToWaterInputsProduction',
                                 'pesticideToSaltWaterInputsProduction',
                                 'pesticideToFreshWaterInputsProduction',
                                 'pesticideToSoilInputsProduction',
                                 'pesticideToSoilAgriculturalInputsProduction',
                                 'pesticideToSoilNonAgriculturalInputsProduction',
                                 'pesticideToHarvestedCropInputsProduction',
                                 'resourceUseMineralsAndMetalsInputsProduction',
                                 'resourceUseEnergyDepletionInputsProduction',
                                 'heavyMetalsToWaterInputsProduction',
                                 "ionisingCompoundsToAirInputsProduction",
                                 "ionisingCompoundsToWaterInputsProduction",
                                 "ionisingCompoundsToSaltwaterInputsProduction", ]


def _is_emissions_resource_indicator(best_candidate):
    if best_candidate.FlowContext in ["emission", "resourceUse"]:
        return True
    elif best_candidate.FlowContext in proxy_terms_with_inputs_field:
        if best_candidate.MatchCondition == "~":
            return True
        else:
            return False
    return False


def _is_a_inputs(best_candidate):
    if best_candidate.FlowContext in [
        "biologicalControlAgent", "electricity", "feedFoodAdditive", "fuel", "material", "inorganicFertiliser",
        "organicFertiliser",
        "fertiliserBrandName", "biochar", "pesticideAI", "pesticideBrandName", "processingAid", "seed",
        "otherOrganicChemical",
        "otherInorganicChemical", "soilAmendment", "substrate", "water", "animalProduct", "crop", "forage",
        "liveAnimal",
        "liveAquaticSpecies", "excreta", "processedFood", "veterinaryDrug", "waste"
    ]:
        return True
    return False


def closest(lst, K):
    # using heapq.nsmallest() to find the element in the list with the smallest absolute difference with K
    return heapq.nsmallest(1, lst, key=lambda x: abs(x['amount'] - K))[0]


def merge_duplicate_cycle_inputs(cycle_inputs: List[Input]) -> List[Input]:
    result = []
    grouped_cycle_inputs = group_inputs(cycle_inputs)
    for k, group in grouped_cycle_inputs.items():
        new_value = 0
        for i in group:
            if isinstance(i.value, list):
                new_value += sum(i.value)
            else:
                new_value += i.value

        template_i = group[0]
        template_i.value = [new_value]
        # new_cycle.inputs.append(template_i)
        result.append(template_i)
    return result


def merge_duplicate_indicators(original_indicators: List[Indicator]) -> List[Indicator]:
    grouped_indicators = group_indicators(original_indicators)
    new_emissionsResourceUse = []
    for k, group in grouped_indicators.items():  # dedup indicators
        new_value = sum([i.value for i in group])
        template_i = group[0]
        template_i.value = new_value
        new_emissionsResourceUse.append(template_i)
    return new_emissionsResourceUse


land_cover_map = {
    "forest": "forest",
    'forest, unspecified': "forest",
    "forest, intensive": "plantationForest",
    # 'forest, extensive': "", # Todo no hestia term unique cf
    "forest, used": "plantationForest",
    "grassland/pasture/meadow": "otherNaturalVegetation",  # todo warning! this may change soon
    'grassland, natural (non-use)': 'otherNaturalVegetation',
    # todo danger! nativePasture has been removed! no equivalent! mapping to "grassland/pasture/meadow" as same CF so that's otherNaturalVegetation
    "desert": "desert",
    "permanent crops": "permanentCropland",
    "arable": "annualCropland",
    "arable, irrigated": "annualCropland",
    "arable, non-irrigated": "annualCropland",

    "annual crop": "annualCropland",  # all have same CF of 50.191
    "annual crop, irrigated": "annualCropland",  # all have same CF of 50.191
    "annual crop, non-irrigated": "annualCropland",  # all have same CF of 50.191
    "arable land, unspecified use": "annualCropland",  # all have same CF of 50.191
    "permanent crop": "permanentCropland",  # all have same CF of 50.191
    "permanent crop, irrigated": "permanentCropland",  # all have same CF of 50.191
    "permanent crop, irrigated, intensive": "permanentCropland",  # all have same CF of 50.191
    "permanent crop, non-irrigated": "permanentCropland",  # all have same CF of 50.191
    "permanent crop, non-irrigated, intensive": "permanentCropland",  # all have same CF of 50.191

    # 'annual crop, irrigated, extensive'': "",
    # arable, irrigated, extensive
    # arable, non-irrigated, extensive
    # permanent crops, irrigated, extensive
    # permanent crops, non-irrigated, extensive
    # todo no hestia term unique cf "arable, non-irrigated, extensive"  and "arable, irrigated, extensive" same cf 462.11
    # 'annual crop, non-irrigated, extensive': "",# todo no hestia term unique cf "arable, non-irrigated, extensive" "permanent crops, irrigated, extensive" "permanent crops, non-irrigated, extensive" and "arable, irrigated, extensive" same cf 46.211
    # 'annual crop, irrigated, intensive': "" , # CF 50.946 todo no hestia term "arable, irrigated, intensive" in region-pefTermGrouping-landOccupation-lookup.csv same cf as "arable, non-irrigated, intensive"
    'annual crop, greenhouse': "glassOrHighAccessibleCover",
    "arable, greenhouse": "glassOrHighAccessibleCover",
    "grassland, for livestock grazing": "permanentPasture",
    'grassland, natural, for livestock grazing': "permanentPasture",
    "pasture/meadow": "permanentPasture",  # same cf as "grassland, for livestock grazing"
    "grassland, not used": "otherNaturalVegetation",
    # todo danger! nativePasture has been removed! no equivalent! mapping to "grassland/pasture/meadow" as same CF so that's otherNaturalVegetation
    "grassland": "otherNaturalVegetation",
    # # todo danger! nativePasture has been removed! no equivalent! mapping to "grassland/pasture/meadow" as same CF so that's otherNaturalVegetation same cf 35.641 as 'grassland, not used'
    # "grassland/pasture/meadow": "improvedPastureNOPE",
    "inland waters": "pond",
    'industrial area': "industrialBuilding",
    "urban": "urbanArea",

    "permanent crops, irrigated": "permanentCropland",
    "permanent crops, irrigated, intensive": "permanentCropland",

    "mineral extraction site": "mineralExtractionSite",

    # todo hestia has no equivalent for these terms
    # found in hestia_earth/models/hestia/landCover.py:89
    'annual crop, non-irrigated, intensive': "annualCropland",  # todo we have no term for this CF 50.946 USING FALLBACK
    'annual crop, irrigated, intensive': "annualCropland",  # todo we have no term for this CF 50.946 USING FALLBACK
    'urban, green areas': "urbanAreaGreenAreas",  # todo we have no term for this no eq CFs
    # 'urban, discontinuously built': "", # todo we have no term for this no eq CFs
    # 'urban, continuously built': "", # todo we have no term for this no eq CFs
    # 'urban/industrial fallow (non-use)': "", # todo we have no term for this no eq CFs "urban/industrial fallow" in region-pefTermGrouping-landOccupation-lookup.csv
    'dump site': "dumpSite",
    "dump site, inert material landfill": "dumpSite",
    "dump site, residual material landfill": "dumpSite",
    "dump site, sanitary landfill": "dumpSite",
    "dump site, slag compartment": "dumpSite",

    # "permanent crops"
    # "permanent crops, non-irrigated, intensive"
    # "permanent crops, non-irrigated
    # "permanent crops, irrigated, intensive" and
    # "permanent crops, irrigated"
    # have same CF

    # 'unspecified, natural (non-use)': "", # todo no term with eq CF "unspecified, natural" in region-pefTermGrouping-landOccupation-lookup.csv

    'seabed, drilling and mining': "seaOrOcean",  # not in pef
    'seabed, unspecified': "seaOrOcean",  # not in pef
    'seabed, infrastructure': "seaOrOcean",  # not in pef
    'inland waterbody, unspecified': "lake",  # not in pef
    'wetland, inland (non-use)': "lake",  # not in pef #extra in ecoinvent
    'river, artificial': "riverOrStream",  # not in pef
    'river, natural (non-use)': "riverOrStream",  # not in pef
    'traffic area, rail/road embankment': "trafficAreaRailAndRoadEmbankment",  # todo not in hestia, unique CF
    'traffic area, road network': "trafficAreaRoadNetwork",  # todo not in hestia, unique CF
    'traffic area, rail network': "trafficAreaRailNetwork",  # todo not in hestia, unique CF
    'lake, artificial': "lake",  # not in pef
    # 'pasture, man made, intensive': "", # todo no term with eq CF "pasture/meadow, extensive" in region-pefTermGrouping-landOccupation-lookup.csv cf 38.973
    'construction site': "constructionSite",  # todo not in glossary yet
    # 'unspecified': "",                  # no equivalent in hestia, has a default CF of `69.262` use everywhere? 'unspecified'in region-pefTermGrouping-landOccupation-lookup.csv
    'pasture, man made': "permanentPasture",
    # todo!! nominallyManagedPasture removed so "pasture/meadow" is now permanentPasture
    # unique cf hestia "pasture/meadow" in region-pefTermGrouping-landOccupation-lookup.csv #cf is 54.923
    # 'pasture, man made, extensive': "", # todo unique cf and not in hestia "pasture/meadow, extensive" in region-pefTermGrouping-landOccupation-lookup.csv
    'shrub land': "shrubLand",
    'shrub land, sclerophyllous': "shrubLand",  # workaround for ecoinvent name

    # transformations only?
    'cropland fallow (non-use)': "shortFallow",
    # "arable, fallow" in region-pefTermGrouping-landTransformation-to-lookup.csv cf 516.99
    # same as 'to annual crop, fallow'?
    'annual crop, fallow': "shortFallow",
    # or "shortBareFallow"? agribalyse "to annual crop, fallow" matches  cf 516.99 of ef "to arable, fallow"
    'annual crop, non-irrigated, fallow': "shortFallow",
    # same as above agribalyse:'from annual crop, non-irrigated, fallow' cf of -516.99 ef "from arable, fallow"

    'forest, primary (non-use)': "primaryForest",
    # updated! have "primaryForest" and  'forest, primary' and 'forest, natural' have same cf 114.59 todo need to fix corune mapping

    'forest, secondary': "secondaryForest",
    # updated now have 'forest, secondary'  todo need to fix corine mapping aka "forest, secondary" in ef
    'forest, secondary (non-use)': "secondaryForest",
    'heterogeneous, agricultural': None,
    # Todo no hestia term. "agriculture, mosaic" and "agriculture" in region-pefTermGrouping-landTransformation-to-lookup.csv same cf 482.18

    # new:
    'agriculture': None,  # todo same as above
    'arable, non-irrigated, diverse-intensive': "annualCropland",
    # cf of 46.211 of ef "arable, non-irrigated, extensive" todo add term USING FALLBACK
    'arable, non-irrigated, monotone-intensive': "annualCropland",
    # cf of 50.946 of ef "arable, non-irrigated, intensive" todo add term USING FALLBACK
    'forest, intensive, normal': "plantationForest",
    'forest, intensive, short-cycle': "plantationForest",

    'industrial area, vegetation': "industrialBuilding",
    'industrial area, built up': "industrialBuilding",
    'pasture and meadow, extensive': "permanentPasture",  # todo fix mapping not correct
    'pasture and meadow, intensive': "permanentPasture",  # todo fix mapping not correct
    'traffic area': "trafficArea",
    # 'traffic area, rail network': "urbanArea",
    'traffic area, road embankment': "trafficAreaRailAndRoadEmbankment",

    'tropical rain forest': "primaryForest",

    'urban, continuously built': "urbanAreaContinuouslyBuilt",  # todo no term unique cf
    'urban, discontinuously built': "urbanAreaDiscontinuouslyBuilt",  # todo no term unique cf
    'urban/industrial fallow (non-use)': "urbanAndIndustrialAreaFallow",  # todo no term unique cf
    'urban/industrial fallow': "urbanAndIndustrialAreaFallow",  # todo no term unique cf
    # todo definetly need to add these:
    'unspecified': None,
    'unspecified, used': None,
    'unknown': None,  # aka "unspecified" in ef
    'unspecified, natural (non-use)': None,  # aka "unspecified, natural" in ef todo need to find!
    "unknown (used)": None,  # aka "unspecified, used" in ef todo need to add! USING FALLBACK
    'pasture and meadow': "permanentPasture",
    'permanent crop, vine': "permanentCropland",  # uses CF 50.191 same as
    'permanent crop, vine, intensive': "permanentCropland",  # uses CF 50.191 same as
    'permanent crop, fruit': "permanentCropland",  # uses CF 50.191 same as
    'permanent crop, fruit, intensive': "permanentCropland",  # uses CF 50.191 same as

    'sea and ocean': "seaOrOcean",

    # agribalyse workaround
    'industrial area, benthos': "industrialBuilding",
    'dump site, benthos': "dumpSite",

    'water bodies, artificial': "pond",  # co cf for water bodies

}

# def trim_excess_country_field(new_impact, resulting_indicators) -> List[Indicator]:
#     resulting_indicators_less_country = []  # strips out redudant country entries if same as IA to save space
#     for indicator in resulting_indicators:
#         if new_impact.country and indicator.country and indicator.country.id == new_impact.country.id:
#             new_indicator = indicator.model_copy(deep=True)
#             new_indicator.country = None
#             resulting_indicators_less_country.append(new_indicator)
#         else:
#             resulting_indicators_less_country.append(indicator)
#     return resulting_indicators_less_country


indicators_allowed_negative_values = ['freshwaterWithdrawalsDuringCycle',
                                      'freshwaterWithdrawalsInputsProduction',
                                      'greenWaterUseDuringCycle',
                                      'greenWaterUseInputsProduction',
                                      'greyWaterUseDuringCycle',
                                      'greyWaterUseInputsProduction',
                                      'resourceUseEnergyDepletionDuringCycle',
                                      'resourceUseEnergyDepletionInputsProduction',
                                      ]


def filter_term_d(downloaded_term_d: dict) -> dict:
    return {key: downloaded_term_d[key] for key in ['@type', "@id", "name", "units", "termType"]}


def expand_reference_from_id(node: dict, target_folder_path: Path) -> Optional[dict]:
    s_path = node_to_path(node_type=node['@type'], node_id=node['@id'])
    target_file = target_folder_path / Path(s_path)
    if not target_file.exists():
        return None
    with open(target_file) as f:
        new_node_from_file = json.load(f)
    return new_node_from_file


def recursively_expand_all_refs(data: dict, target_folder_path: Path) -> dict:
    new_data = {}
    for field_name, ref_node in data.items():
        if type(ref_node) is dict and (set(ref_node.keys()) == {"@id", "@type"} or
                                       set(ref_node.keys()) == {"@id", "@type", "name"}
        ):
            updated_node = expand_reference_from_id(ref_node, target_folder_path)
            if updated_node:
                new_data[field_name] = recursively_expand_all_refs(updated_node, target_folder_path)
            else:
                new_data[field_name] = ref_node
        elif type(ref_node) is list and all([isinstance(e, dict) for e in ref_node]):
            new_l = []
            for ref_node_e in ref_node:
                new_l.append(recursively_expand_all_refs(ref_node_e, target_folder_path))
            new_data[field_name] = new_l
        else:
            new_data[field_name] = ref_node
    return new_data
