from hestia_earth.converters.base.pydantic_models.hestia import Term

from ..pydantic_models.schema_enums import (
    emissions_to, ElementaryFlowType,
    SubCompartment, parent_compartment
)

hestia_transformation_indicator_ids = ['landTransformation20YearAverageInputsProduction',
                                       'landTransformation20YearAverageDuringCycle']
hestia_occupation_indicator_ids = ['landOccupationInputsProduction', 'landOccupationDuringCycle']


def prefer_relevant_simapro_candidate(term: Term) -> list:
    """
    :param term:
    :return:
    """
    if "ToAir" in term.id:
        prefer = emissions_to(ElementaryFlowType.EMISSIONS_TO_AIR)

    elif "ToAirIndoor" in term.id:
        prefer = [
            SubCompartment.AIR_INDOOR.compartment_path_str(),
        ]


    elif "ToAirOtherHigherAltitudes" in term.id:
        prefer = [
            SubCompartment.AIR_LOW_POP.compartment_path_str(),
            SubCompartment.AIR_LOW_POP_LONG_TERM.compartment_path_str(),
            SubCompartment.AIR_STRATOSPHERE.compartment_path_str(),
            SubCompartment.AIR_STRATOSPHERE_TROPOSPHERE.compartment_path_str(),
        ]


    elif "ToAirUrbanCloseToGround" in term.id:
        prefer = [
            SubCompartment.AIR_HIGH_POP.compartment_path_str(),
        ]


    elif "ToWater" in term.id:
        prefer = emissions_to(ElementaryFlowType.EMISSIONS_TO_WATER)

    elif "ToSaltwater" in term.id:
        prefer = [SubCompartment.WATER_OCEAN.compartment_path_str()]

    elif "ToSurfaceWater" in term.id or "ToFreshWater" in term.id:
        prefer = [
            SubCompartment.WATER_LAKE.compartment_path_str(),
            SubCompartment.WATER_RIVER.compartment_path_str(),
            SubCompartment.WATER_RIVER_LONG_TERM.compartment_path_str(),
        ]

    elif "ToGroundwater" in term.id:
        prefer = [
            SubCompartment.WATER_GROUND.compartment_path_str(),
            SubCompartment.WATER_GROUND_LONG_TERM.compartment_path_str(),
        ]


    elif "ToSoil" in term.id:
        prefer = emissions_to(ElementaryFlowType.EMISSIONS_TO_SOIL)

    elif "ToSoilAgricultural" in term.id:
        prefer = [SubCompartment.SOIL_AGRICULTURAL.compartment_path_str()]

    elif "ToSoilNonAgricultural" in term.id:
        prefer = [
            SubCompartment.SOIL_FORESTRY.compartment_path_str(),
            SubCompartment.SOIL_INDUSTRIAL.compartment_path_str(),
            SubCompartment.SOIL_URBAN.compartment_path_str(),
        ]

    elif term.id in hestia_occupation_indicator_ids + hestia_transformation_indicator_ids:
        prefer = [SubCompartment.RESOURCES_LAND.compartment_path_str()]

    elif term.id in ['freshwaterWithdrawalsDuringCycle', 'freshwaterWithdrawalsInputsProduction']:
        prefer = [
            SubCompartment.RESOURCES_IN_GROUND.compartment_path_str(),
            SubCompartment.RESOURCES_IN_WATER.compartment_path_str(),
            SubCompartment.RESOURCES_IN_AIR.compartment_path_str(),
        ]

    elif term.termType == "resourceUse":
        prefer = emissions_to(ElementaryFlowType.RESOURCES)

    else:
        prefer = []

    return prefer


def prefer_relevant_simapro_candidate_block_alias(term: Term) -> list:
    """
    :param term:
    :return:
    """

    if term.id in hestia_occupation_indicator_ids + hestia_transformation_indicator_ids:
        prefer = [SubCompartment.RESOURCES_LAND.compartment_path_block_alias_str()]

    elif term.id in ['freshwaterWithdrawalsDuringCycle', 'freshwaterWithdrawalsInputsProduction']:
        prefer = [
            SubCompartment.RESOURCES_IN_GROUND.compartment_path_block_alias_str(),
            SubCompartment.RESOURCES_IN_WATER.compartment_path_block_alias_str(),
            SubCompartment.RESOURCES_IN_AIR.compartment_path_block_alias_str(),
        ]

    elif term.termType in ["resourceUse",
                           "biologicalControlAgent", "electricity", "feedFoodAdditive", "fuel", "material",
                           "inorganicFertiliser", "organicFertiliser", "fertiliserBrandName", "biochar", "pesticideAI",
                           "pesticideBrandName", "processingAid", "seed", "otherOrganicChemical",
                           "otherInorganicChemical", "soilAmendment", "substrate", "water", "animalProduct", "crop",
                           "forage", "liveAnimal", "liveAquaticSpecies", "excreta", "processedFood", "veterinaryDrug",
                           "waste"]:
        prefer = [parent_compartment(ElementaryFlowType.RESOURCES).block_header(),
                  parent_compartment(ElementaryFlowType.RESOURCES).compartment_str()
                  ] + emissions_to(ElementaryFlowType.RESOURCES)

    else:
        prefer = []

    return prefer
