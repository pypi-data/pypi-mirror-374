from collections import defaultdict
from decimal import Decimal
from itertools import groupby
from pathlib import Path
from typing import List, Union, Literal, Set
from hestia_earth.models.utils.term import get_lookup_value as get_term_lookup_value

from hestia_earth.converters.base.pydantic_models.hestia.api_utils import download_hestia, update_hestia_node
from hestia_earth.converters.base.pydantic_models.hestia import (
    ImpactAssessment, Indicator, Product, Emission, Input, Term,
    HestiaCycleContent, Source, Cycle,
    LandOccupationIndicator, Country,
    LandTransformationIndicator
)
from hestia_earth.converters.base.pydantic_models.hestia.hestia_schema_tools import proxy_terms_with_inputs_field
from hestia_earth.converters.base.converter import Converter
from hestia_earth.converters.base.converter.helpers import is_url, is_uuid
from hestia_earth.converters.base.converter.utils import safe_string
from hestia_earth.converters.base.RosettaFlow import (
    FlowMap, MapperError, pick_best_match, MappingChoices, CandidateFlow
)

from ..log import logger
from ..rosetta_flow.helpers import (
    prefer_relevant_simapro_candidate,
    prefer_relevant_simapro_candidate_block_alias
)
from ..pydantic_models import (
    SimaProFile, ElementaryExchangeRow, ProductOutputRow, SimaProHeader, UnitBlock,
    GenericBiosphere, ElementaryFlowRow,
    QuantityBlock,
    SimaProProcessBlock, UncertaintyRecordUndefined, UnitRow, QuantityRow,
    TechExchangeRow, SystemDescriptionBlock,
    SystemDescriptionRow, ExternalDocumentsRow, LiteratureRow,
    LiteratureReferenceBlock, EcoinventTechExchangeRow
)
from ..pydantic_models.schema_enums import unit_categories
from ..pydantic_models.util import minify_semapro_compartment
from ..ecoinvent_api import get_external_ecoinvent_process_data


TARGET_SEMA_PRO_NOMENCLATURES = [
    "SimaPro/Professional 10.2",
    "Professional 10.2",
    "SimaPro EF 3.1.2",
    "SimaPro/SimaPro EF 3.1.1",
    "SimaPro ecoinvent 3.11 EN15804",
    "SimaPro ecoinvent 3.10 EN15804",
    "SimaPro EF 3.1",
    "Professional 9.6",
    "Professional 9.5",
    "Professional 9.4",
    "SimaPro9.4",
    "Professional 10.2+Hestia",
]

SIMAPRO_LIBRARY_ECOINVENT = {
    'Ecoinvent 3 - allocation at point of substitution - system',
    'Ecoinvent 3 - allocation at point of substitution - unit',
    # 'Ecoinvent 3 - consequential - system',
    # 'Ecoinvent 3 - consequential - unit',
}

converter_obj = Converter()

hestia_transformation_indicator_ids = ['landTransformation20YearAverageInputsProduction',
                                       'landTransformation20YearAverageDuringCycle']
hestia_occupation_indicator_ids = ['landOccupationInputsProduction', 'landOccupationDuringCycle']
hestia_land_use_indicator_ids = hestia_occupation_indicator_ids + hestia_transformation_indicator_ids

attribute_maps = {
    "emission": {
        "ToAir": "emissionsToAir",  # ElementaryExchangeRow
        # 'pErosionSoilFlux': "emissionsToAir",  # ElementaryExchangeRow
        # 'nErosionSoilFlux': "emissionsToAir",  # ElementaryExchangeRow
        "ToWater": "emissionsToWater",  # ElementaryExchangeRow
        "ToGroundwater": "emissionsToWater",  # ElementaryExchangeRow
        "ToDrainageWater": "emissionsToWater",  # ElementaryExchangeRow
        "ToSoil": "emissionsToSoil",  # ElementaryExchangeRow
    },
    "resourceUse": {
        "landTransformation": "resources",  # ElementaryExchangeRow
        "landOccupation": "resources",  # ElementaryExchangeRow
        "freshwaterWithdrawals": "resources",  # ElementaryExchangeRow
        "resourceUseMineralsAndMetals": "resources",  # ElementaryExchangeRow
    },
    "electricity": {
        "electricity": "electricityAndHeat"  # TechExchangeRow
    }
}
attribute_maps_blocks = {  # ElementaryFlowTypeAlias
    "emission": {
        "ToAir": "Airborne emissions",
        # 'pErosionSoilFlux': "Airborne emissions",
        # 'nErosionSoilFlux': "Airborne emissions",
        "ToWater": "Waterborne emissions",
        "ToGroundwater": "Waterborne emissions",
        "ToDrainageWater": "Waterborne emissions",
        "ToSoil": "Emissions to soil",
    },
    "resourceUse": "Raw materials",
    "electricity": {"electricity": "electricityAndHeat"}
}

product_category_map = {  # todo
    "material": "Others",
    "crop": "Agricultural\\Plant production",
    "seed": "Agricultural\\Plant production",
    "animalProduct": "Agricultural\\Animal production",
    "liveAnimal": "Agricultural\\Animal production",
    "liveAquaticSpecies": "Agricultural\\Animal production",
    "processedFood": "Agricultural\\Food",
    "fuel": "Fuels",
    # "":"Agricultural\\Plant production\\Cereals",
    # "":"Agricultural\\Plant production\\Sugar crops",
    # "":"Agricultural\\Plant production\\Vegetables",
}  # , , cropResidue, electricity, feedFoodAdditive, forage, fuel, , , excreta, organicFertiliser, inorganicFertiliser, biochar, otherOrganicChemical, otherInorganicChemical, processingAid, , , soilAmendment, substrate,, waste


class ExtractingProcessError(Exception):
    """Cannot turn a Hestia cycle input and related emission into a separate Simapro process"""


def _map_to_category(hestia_product: Product) -> str:
    if hestia_product.term.termType in product_category_map:
        return 'Material\\' + product_category_map[hestia_product.term.termType]
    return 'Material\\' + str(hestia_product.term.termType).capitalize(),


def _country_to_iso_code(country: Country) -> Union[str, None]:
    if not country.iso31662Code:
        country = update_hestia_node(country)
    return country.iso31662Code


def _handle_hestia_indicator_to_simapro_exchange_row(source_model: Indicator, context=None,
                                                     **kwargs) -> ElementaryExchangeRow | List[ElementaryExchangeRow]:
    if context is None:
        context = {}

    hestia_indicator = source_model

    if ((
            hestia_indicator.landCover and hestia_indicator.previousLandCover and hestia_indicator.term.id in hestia_transformation_indicator_ids) or
            isinstance(hestia_indicator, LandTransformationIndicator)):

        from_exchange_row = convert_hestia_indicator_to_simapro_exchange_row(
            context | {
                "target_context": [
                    "Resources/land",
                ],
                "requirement": {"FlowName": "Transformation, from "}},
            hestia_indicator,
            hestia_indicator.previousLandCover)

        to_exchange_row = convert_hestia_indicator_to_simapro_exchange_row(
            context | {
                "target_context": [
                    "Resources/land",
                ],
                "requirement": {"FlowName": "Transformation, to "}},
            hestia_indicator,
            hestia_indicator.landCover)

        if from_exchange_row.amount != to_exchange_row.amount:
            raise Exception("Bad land transformation flowmap")
        return [from_exchange_row, to_exchange_row]

    elif ((hestia_indicator.landCover and hestia_indicator.term.id in hestia_occupation_indicator_ids) or
          isinstance(hestia_indicator, LandOccupationIndicator)):

        exchange_row = convert_hestia_indicator_to_simapro_exchange_row(
            context | {
                "target_context": [
                    "Resources/land",
                ],
                "requirement": {"FlowName": "Occupation, "}},
            hestia_indicator,
            hestia_indicator.landCover)
        return exchange_row

    elif hestia_indicator.key:
        exchange_row = convert_hestia_indicator_to_simapro_exchange_row(context, hestia_indicator, hestia_indicator.key)
        return exchange_row

    elif hestia_indicator.inputs and hestia_indicator.term.id in proxy_terms_with_inputs_field:
        exchange_row = convert_hestia_indicator_to_simapro_exchange_row(context, hestia_indicator,
                                                                        hestia_indicator.inputs[0])
        return exchange_row

    else:
        exchange_row = convert_hestia_indicator_to_simapro_exchange_row(context, hestia_indicator,
                                                                        hestia_indicator.term)
        return exchange_row


def _handle_hestia_emission_to_simapro_exchange_row(source_model: Emission, context=None,
                                                    **kwargs) -> ElementaryExchangeRow | List[ElementaryExchangeRow]:
    if context is None:
        context = {}

    hestia_emission = source_model

    exchange_row = convert_hestia_indicator_to_simapro_exchange_row(context, hestia_emission, hestia_emission.term)
    return exchange_row


def _handle_hestia_product_to_simapro_exchange_row(source_model: Product, context=None,
                                                   **kwargs) -> ElementaryExchangeRow:
    if context is None:
        context = {}

    hestia_product = source_model

    exchange_row = convert_hestia_indicator_to_simapro_exchange_row(context, hestia_product, hestia_product.term)
    return exchange_row


def _hestia_input_to_simapro_external_process_WIP(source_model: Input, context=None,
                                                  **kwargs) -> EcoinventTechExchangeRow:
    if context is None:
        context = {}

    input_entry = source_model

    # for input_term in cycle_emission.inputs:
    term_dict = input_entry.term.model_dump(by_alias=True, exclude_none=True)
    ecoinventMapping_process_name = get_term_lookup_value(term_dict, 'ecoinventMapping', skip_debug=True)

    if not ecoinventMapping_process_name:
        raise Exception(f"No ecoinventMapping for {input_entry.term.id}")

    standardised_process_name = ecoinventMapping_process_name.split(": ")[0]

    candidate_ecoinvent_products = term_map_obj.map_flow(term_dict, check_reverse=True,
                                                         search_indirect_mappings=False,
                                                         source_nomenclatures=["HestiaList"],
                                                         target_nomenclature="ecoinvent",
                                                         )

    ecoinvent_product_candidate = pick_best_match(candidate_ecoinvent_products)

    term_ecoinvent_id = parse_ecoinvent_ref_id(input_entry)

    if ecoinvent_product_candidate:
        ref_platform_id = ecoinvent_product_candidate.FlowUUID.upper()
        if term_ecoinvent_id.upper() != ref_platform_id:
            raise ExtractingProcessError(f"Found ecoinvent model process uuid does not match term {term_ecoinvent_id}")

        comment = generate_tech_exchange_comment(ecoinvent_product_candidate, input_entry)
        conversion_factor = ecoinvent_product_candidate.ConversionFactor
        new_unit = ecoinvent_product_candidate.Unit

    else:
        logger.error("No known flowmaps from term: '{}' to ecoinvent product. "
                     "Attempting to use ecoinvent api as fallback".format(term_dict.get("@id")))

        ecoinvent_api_json = get_external_ecoinvent_process_data(input_entry.term.ecoinventReferenceProductId.id)

        new_unit = ecoinvent_api_json['unit']['name']
        if new_unit in input_entry.term.units:
            conversion_factor = 1
        else:
            raise ExtractingProcessError(f"Cannot guess conversion factor for process {standardised_process_name}")
        ref_platform_id = term_ecoinvent_id.upper()
        comment = generate_tech_exchange_comment(None, input_entry)

    comment += " Ecoinvent process"
    # reference the process with a tech exchange row
    tech_exchange_row = EcoinventTechExchangeRow(platformId=ref_platform_id,
                                                 name=standardised_process_name,
                                                 comment=comment,
                                                 unit=new_unit,
                                                 amount=conversion_factor * unpack_list_values(input_entry.value),
                                                 uncertainty=UncertaintyRecordUndefined(),
                                                 flow_metadata={}
                                                 )
    tech_exchange_row.flow_metadata = {"conversion_factor": conversion_factor,
                                       "original_term": term_dict,
                                       "source_unit": input_entry.term.units,
                                       "target_unit": new_unit,
                                       "ecoinventMapping_process_name": ecoinventMapping_process_name,
                                       }

    if source_model.country:
        if not source_model.country.name:
            source_model.country = update_hestia_node(source_model.country)
        tech_exchange_row.flow_metadata.update(
            {
                "original_term_country": source_model.country.model_dump(by_alias=True, exclude_unset=True),
                "original_term_country_iso31662Code": _country_to_iso_code(source_model.country),
            }
        )

    return tech_exchange_row


def _hestia_emission_to_simapro_dummy_process(source_model: Emission, context=None,
                                              **kwargs) -> List[SimaProProcessBlock]:
    if context is None:
        context = {}

    cycle_emission = source_model

    dummy_processes = []
    for input_term in cycle_emission.inputs:

        common_name = f"{cycle_emission.methodModel.name} | {input_term.termType}/{input_term.id}"
        product_name = common_name
        dummy_process_name = f"Dummy: {common_name}"

        if cycle_emission.country:
            iso_str = _country_to_iso_code(cycle_emission.country)
            product_name += " {" + iso_str + "}"

        dummy_process = SimaProProcessBlock(
            category="material",
            processType="Unit process",
            name=dummy_process_name,
            status="",
            infrastructure=False,
            date=context.get("sima_pro_process_date"),
            comment=cycle_emission.methodModelDescription or "No",
            systemDescription=SystemDescriptionRow(name="", ),
            products=[
                ProductOutputRow(
                    name=product_name,
                    unit=input_term.units,
                    amount=1,
                    allocation=100,
                    wasteType="Undefined",  # todo
                    category='Others\\Dummies',
                    comment='',
                    # comment=_build_hestia_product_description(hestia_product) + allocation_notes,
                    # platformId=input_term.id,
                    row_metadata={"orignal_term": input_term.model_dump(by_alias=True, exclude_unset=True)}
                )
            ],
        )
        inventory_blocks = defaultdict(list)  # todo
        used_units = set()  # todo
        added = False
        # if cycle_emission.term.termType in attribute_maps:
        # for compartment_string, attribute_name in attribute_maps[str(cycle_emission.term.termType)].items():
        #     if compartment_string in cycle_emission.term.id:
        # block_name = attribute_maps2[str(cycle_emission.term.termType)][compartment_string]

        attribute_name = _bucket_term_to_process_field(cycle_emission.term)
        block_name = _bucket_term_to_inventory_block(cycle_emission.term)

        dummy_process, used_units, inventory_blocks = hestia_entry_to_exchange_fields(
            context, cycle_emission,
            inventory_blocks,
            dummy_process,
            used_units,
            process_attribute=attribute_name,
            inventory_blocks_name=block_name)

        dummy_processes.append(dummy_process)

    return dummy_processes


def _handle_hestia_input_to_simapro_elementary_exchange_row(source_model: Input, context=None,
                                                            **kwargs) -> ElementaryExchangeRow | List[
    ElementaryExchangeRow]:
    if context is None:
        context = {}

    hestia_input = source_model
    context = context | {"target_context": ["Raw materials",
                                            "Resources/land",
                                            "Resources/biotic",
                                            "Resources/in ground",
                                            "Resources/in air",
                                            "Resources/in water",
                                            "Resources/fossil well",
                                            "Substance",
                                            ]}
    exchange_row = convert_hestia_indicator_to_simapro_exchange_row(context, hestia_input, hestia_input.term)
    return exchange_row


def _handle_hestia_input_to_simapro_tech_exchange_row(source_model: Input, context=None,
                                                      **kwargs) -> TechExchangeRow:
    if context is None:
        context = {}

    hestia_input = source_model

    term_dict = hestia_input.term.model_dump(by_alias=True, exclude_unset=True)

    candidate_mapped_flows = term_map_obj.map_flow(term_dict, check_reverse=True,
                                                   search_indirect_mappings=False,
                                                   source_nomenclatures=["HestiaList"],
                                                   target_nomenclature=TARGET_SEMA_PRO_NOMENCLATURES,
                                                   target_context=["Raw materials", "Raw materials/"])
    if not candidate_mapped_flows:
        raise MapperError("Could not map hestia term: '{}'".format(term_dict.get("@id")))

    prefer = prefer_relevant_simapro_candidate_block_alias(hestia_input.term)  # inputs?

    iso_str = None
    if hasattr(hestia_input, "country") and hestia_input.country:
        iso_str = _country_to_iso_code(hestia_input.country)
        requirement = context.get("requirement", {}) | {"Geography": iso_str}
    else:
        requirement = context.get("requirement", {}) | {"Geography": None}

    best_candidate = pick_best_match(candidate_mapped_flows, context={"prefer": prefer}, requirement=requirement,
                                     preferred_list_names=TARGET_SEMA_PRO_NOMENCLATURES)

    comment = generate_tech_exchange_comment(best_candidate, hestia_input)
    new_amount = best_candidate.ConversionFactor * unpack_list_values(hestia_input.value)

    tech_row = TechExchangeRow(platformId=best_candidate.FlowUUID.upper(),
                               name=best_candidate.FlowName,
                               comment=comment,
                               line_no=None,
                               unit=best_candidate.Unit,
                               amount=new_amount,
                               uncertainty=UncertaintyRecordUndefined(),
                               flow_metadata={}
                               )
    tech_row.flow_metadata = {"conversion_factor": best_candidate.ConversionFactor,
                              "original_term": term_dict,
                              "source_unit": hestia_input.term.units,
                              "target_unit": best_candidate.Unit,
                              }

    if source_model.country:
        if not source_model.country.name:
            source_model.country = update_hestia_node(source_model.country)
        tech_row.flow_metadata.update(
            {
                "original_term_country": source_model.country.model_dump(by_alias=True, exclude_unset=True),
                "original_term_country_iso31662Code": _country_to_iso_code(source_model.country),
            }
        )

    return tech_row


def convert_hestia_indicator_to_simapro_exchange_row(context: dict, hestia_indicator: HestiaCycleContent,
                                                     term: Term) -> ElementaryExchangeRow:
    term_dict = term.model_dump(by_alias=True, exclude_unset=True)

    candidate_mapped_flows = term_map_obj.map_flow(term_dict,
                                                   check_reverse=True,
                                                   search_indirect_mappings=False,
                                                   source_nomenclatures=["HestiaList"],
                                                   target_nomenclature=TARGET_SEMA_PRO_NOMENCLATURES,
                                                   target_context=context.get("target_context"))
    if not candidate_mapped_flows:
        raise MapperError("Could not map hestia term: '{}'".format(term.id))

    if isinstance(hestia_indicator, Emission):
        prefer = prefer_relevant_simapro_candidate(term)
    elif isinstance(hestia_indicator, Input):
        prefer = prefer_relevant_simapro_candidate_block_alias(term)
    else:
        prefer = []

    if hasattr(hestia_indicator, "country") and hestia_indicator.country:
        iso_str = _country_to_iso_code(hestia_indicator.country)
        requirement = context.get("requirement", {}) | {"Geography": iso_str}
    else:
        requirement = context.get("requirement", {}) | {"Geography": None}

    best_candidate = pick_best_match(candidate_mapped_flows, context={"prefer": prefer}, requirement=requirement,
                                     preferred_list_names=TARGET_SEMA_PRO_NOMENCLATURES)
    if not best_candidate:
        raise MapperError("Could not map hestia term: '{}'".format(term_dict.get("@id")))

    new_amount = best_candidate.ConversionFactor * unpack_list_values(hestia_indicator.value)

    comment = generate_elementary_exchange_comment(best_candidate, hestia_indicator, term_dict)

    exchange_row = ElementaryExchangeRow(
        platformId=best_candidate.FlowUUID.upper() if best_candidate.FlowUUID else None,
        subCompartment=minify_semapro_compartment(best_candidate.FlowContext),
        name=best_candidate.FlowName,
        comment=comment,
        unit=best_candidate.Unit,
        amount=new_amount,
        uncertainty=UncertaintyRecordUndefined(),
        flow_metadata={}
    )

    exchange_row.flow_metadata = {"conversion_factor": best_candidate.ConversionFactor,
                                  "original_term": term_dict,
                                  "source_unit": hestia_indicator.term.units,
                                  "target_unit": best_candidate.Unit,
                                  }

    if hasattr(hestia_indicator, "country") and hestia_indicator.country:
        if not hestia_indicator.country.name:
            hestia_indicator.country = update_hestia_node(hestia_indicator.country)
        exchange_row.flow_metadata.update(
            {
                "original_term_country": hestia_indicator.country.model_dump(by_alias=True, exclude_unset=True),
                "original_term_country_iso31662Code": _country_to_iso_code(hestia_indicator.country),
            }
        )

    return exchange_row


def generate_elementary_exchange_comment(best_candidate, hestia_indicator, term_dict):
    via_str = add_indirect_mapping_comment(best_candidate)

    if best_candidate.MatchCondition == MappingChoices.A_PROXY_FOR.value:
        match_str = "Proxy mapped"
    elif best_candidate.MatchCondition == MappingChoices.A_SUBSET_OF.value:
        match_str = "Subset mapped"
    elif best_candidate.MatchCondition == MappingChoices.A_SUPERSET_OF.value:
        match_str = "Superset mapped"
    else:
        match_str = "Mapped"

    comment = f"{match_str} from HESTIA term '{term_dict.get('termType')}/{term_dict.get("@id")}'{via_str}"
    comment += f" conversion factor: {best_candidate.ConversionFactor}" if best_candidate.ConversionFactor != 1 else ""
    if (isinstance(hestia_indicator, Emission) or isinstance(hestia_indicator, Indicator)) and hestia_indicator.inputs:
        comment += f" Emission from: "
        for input_t in hestia_indicator.inputs:
            comment += f"'{input_t.termType}/{input_t.id}' "
        comment += f"Modeled by '{hestia_indicator.methodModel.name}'"
        if hestia_indicator.methodModelDescription:
            comment += f"Model description:'{hestia_indicator.methodModelDescription}'"

    if hasattr(hestia_indicator, "description") and hestia_indicator.description:
        comment += f"{str(type(hestia_indicator))} description '{hestia_indicator.description}'"

    return comment


def generate_tech_exchange_comment(best_candidate: CandidateFlow, hestia_input: Input) -> str:
    if best_candidate:
        via_str = add_indirect_mapping_comment(best_candidate)
    else:
        via_str = ""
    model_str = hestia_input.model.name if hestia_input.model else ""
    comment = f"Mapped from HESTIA term '{hestia_input.term.id}'{via_str} {model_str}"
    return comment


def add_indirect_mapping_comment(best_candidate: CandidateFlow) -> str:
    if best_candidate.meta_data and best_candidate.meta_data.stepping_stones:
        via_str = " indirectly via " + " > ".join(
            [f"'{x.list_name}'" for x in best_candidate.meta_data.stepping_stones])
    else:
        via_str = ""
    return via_str


def _update_amounts_depending_on_unit(model_data: dict,
                                      source_model: ImpactAssessment = None,
                                      destination_model_type=None,
                                      **kwargs) -> dict:
    model_data = model_data.copy()
    coef = model_data['flow'].flow_metadata.get('conversion_factor')
    if coef:
        new_value = model_data['values'] * coef
        model_data['values'] = new_value
    return model_data

    hestia_product = source_model.product

    product_exchange = converter_obj.transmute(source_model_obj=hestia_product,
                                               destination_model=Exchange,
                                               context={})
    product_exchange.is_quantitative_reference = True

    model_data['exchanges'].append(product_exchange)

    return model_data


def _map_is_input(source_model: Indicator, **kwargs) -> bool:
    return source_model.term.termType != 'emission'


def _value_unpacker(source_model: Indicator | Product, **kwargs) -> float | int:
    """
    for products:
    "The quantity of the Product. If an average, it should always be the mean. Can be a single number (array of length one) or an array of numbers with associated dates (e.g., for multiple harvests in one Cycle. For crops, value should always be per harvest or per year, following FAOSTAT conventions. "

    Todo policy
    :param source_model:
    :param kwargs:
    :return:
    """
    hestia_value = source_model.value

    return unpack_list_values(hestia_value)


def unpack_list_values(schema_value: Union[List, int, float, Decimal]):
    if isinstance(schema_value, list):
        return sum(schema_value)
    else:
        return schema_value


def _source_to_literature_ref_block(source_model: Source, **kwargs) -> LiteratureReferenceBlock:
    description = f"Uploader notes: {source_model.uploadNotes}\n" if source_model.uploadNotes else ""

    if source_model.model_fields_set == {'id', 'type'}:
        source_model = update_hestia_node(source_model)

    if source_model.bibliography:
        for k, v in source_model.bibliography.model_dump(exclude_none=True, by_alias=True, mode='python',
                                                         exclude=['name', 'type', 'authors']).items():
            description += f"{k.capitalize()}: {v}\n"  # todo use  = convert_schema_dict_to_text(k, comment, v)
        if source_model.bibliography.authors:
            authors_str = f"Authors:"
            has_authors = False
            for author in source_model.bibliography.authors:
                if author.model_fields_set == {'id', 'type'}:
                    author = update_hestia_node(author)
                if author.dataPrivate is not True and author.name:
                    authors_str += f" {author.name},"
                    has_authors = True
            if has_authors:
                description += authors_str.rstrip(",") + "\n"

    if source_model.originalLicense:
        description += f"Original license: {source_model.originalLicense}\n"

    return LiteratureReferenceBlock(name=source_model.name,
                                    documentation_link=f"https://www.hestia.earth/source/{source_model.id}",
                                    category="Hestia sources",
                                    description=description.strip("\n"),
                                    )


# def _build_header_from_ia(source_model, model_data, **kwargs) -> SimaProHeader:
#     header = SimaProHeader()
#     return header
#
#
# def _create_process_block(source_model, model_data, **kwargs) -> SimaProProcessBlock:
#     pass
#
#
# converter_obj.register_model_map(source_model_type=ImpactAssessment,
#                                  destination_model_type=SimaProFile,
#                                  map_field_dict={"header": _build_header_from_ia,
#                                                  "blocks": _create_process_block,
#                                                  # # todo all by alias or by real field name? or both?
#                                                  # # "location": "country",
#                                                  # "header.project": "name",
#                                                  # "header.version": "version",
#                                                  # "header.date": "updatedAt",
#                                                  # "header.time": "updatedAt",
#                                                  # "_get_process_block.resources": _distribute_emissionsResourceUse,
#                                                  # "_get_process_block.emissionsToAir": _distribute_emissionsResourceUse,
#                                                  # "_get_process_block.emissionsToWater": _distribute_emissionsResourceUse,
#                                                  # "_get_process_block.emissionsToSoil": _distribute_emissionsResourceUse,
#                                                  # "_get_process_block.finalWasteFlows": _distribute_emissionsResourceUse,
#                                                  # "_get_process_block.nonMaterialEmissions": _distribute_emissionsResourceUse,
#                                                  # "_get_process_block.socialIssues": _distribute_emissionsResourceUse,
#                                                  # "_get_process_block.economicIssues": _distribute_emissionsResourceUse,
#                                                  # # "_always_run_": _convert_product_and_move_to_exchanges
#                                                  })

# converter_obj.register_model_map(source_model_type=Indicator,
#                                  destination_model_type=Exchange,
#                                  map_field_dict={"flow": "term",
#                                                  "amount": _value_unpacker,
#                                                  "location": "country",
#                                                  "unit": _indicator_unit_convertion,
#                                                  "flow_property": _set_flow_property,
#                                                  "is_input": _map_is_input,
#                                                  "_always_run_": _update_amounts_depending_on_unit,
#                                                  })

# converter_obj.register_model_map(source_model_type=Product,
#                                  destination_model_type=ProductOutputRow,
#                                  map_field_dict={
#                                      # "allocation": ,
#                                      # "wasteType": _set_flow_property,
#                                      # "category": "term.termtype", #todo "material"
#                                      # "name": "term.id",
#                                      "name": "term.name",
#                                      "unit": "term.units",
#                                      "amount": _value_unpacker,
#                                      # "allocation":1,  # todo
#                                      "comment": "description",
#                                      "platformId": "term.id"
#                                  },
#                                  )

converter_obj.register_model_map(source_model_type=Product,
                                 destination_model_type=ElementaryExchangeRow,
                                 map_function=_handle_hestia_product_to_simapro_exchange_row)

converter_obj.register_model_map(source_model_type=Indicator,
                                 destination_model_type=ElementaryExchangeRow,
                                 map_function=_handle_hestia_indicator_to_simapro_exchange_row)

converter_obj.register_model_map(source_model_type=LandOccupationIndicator,
                                 destination_model_type=ElementaryExchangeRow,
                                 map_function=_handle_hestia_indicator_to_simapro_exchange_row)

converter_obj.register_model_map(source_model_type=LandTransformationIndicator,
                                 destination_model_type=ElementaryExchangeRow,
                                 map_function=_handle_hestia_indicator_to_simapro_exchange_row)

converter_obj.register_model_map(source_model_type=Emission,
                                 destination_model_type=ElementaryExchangeRow,
                                 map_function=_handle_hestia_emission_to_simapro_exchange_row)

converter_obj.register_model_map(source_model_type=Emission,
                                 destination_model_type=SimaProProcessBlock,
                                 map_function=_hestia_emission_to_simapro_dummy_process)

converter_obj.register_model_map(source_model_type=Input,
                                 destination_model_type=EcoinventTechExchangeRow,
                                 map_function=_hestia_input_to_simapro_external_process_WIP)

converter_obj.register_model_map(source_model_type=Input,
                                 destination_model_type=TechExchangeRow,
                                 map_function=_handle_hestia_input_to_simapro_tech_exchange_row)

converter_obj.register_model_map(source_model_type=Input,
                                 destination_model_type=ElementaryExchangeRow,
                                 map_function=_handle_hestia_input_to_simapro_elementary_exchange_row)

converter_obj.register_model_map(source_model_type=Source,
                                 destination_model_type=LiteratureReferenceBlock,
                                 map_function=_source_to_literature_ref_block)

converter_obj.register_model_map(source_model_type=Source,
                                 destination_model_type=LiteratureRow,
                                 map_field_dict={
                                     "Name": "name",
                                     "comment": lambda source_model, field_name, default,
                                                       model_data: f"https://www.hestia.earth/source/{source_model.id}",
                                 })


def _product_is_waste(product: Product) -> bool:
    if product.term.termType in ['cropResidue', 'waste', 'excreta', 'substrate']:
        # todo confirm with domain expert  # discardedCropTotal , aboveGroundCropResidueTotal
        return True
    else:
        return False


def _bucket_term_to_process_field(
        term: Term) -> str:  # todo replace with get_term_standard_compartment > compartment to field_name
    if term.termType in attribute_maps:
        for compartment_string, attribute_name in attribute_maps[str(term.termType)].items():
            if compartment_string in term.id:
                return attribute_name
    raise MapperError(f"Do not know what emission compartment the term {term.id} is emitted to.")


def _bucket_term_to_inventory_block(term: Term) -> str:
    if term.termType in attribute_maps:
        for compartment_string, block_name in attribute_maps_blocks[str(term.termType)].items():
            if compartment_string in term.id:
                return block_name
    raise MapperError(f"Do not know what emission compartment the term {term.id} is emitted to.")


def _group__by_inputs_key(emission: Emission) -> tuple:
    if not emission.inputs:
        return None, emission.methodModel.id
    input_ids = set([x.id for x in emission.inputs])
    return tuple(input_ids), emission.methodModel.id


def hestia_to_simapro_converter_from_recalculated_impact_assessment(impact_assessment: ImpactAssessment,
                                                                    mapping_files_directory: Path = None,
                                                                    process_type: Literal[
                                                                        'System',
                                                                        'Unit process'] = "System"
                                                                    ) -> SimaProFile:
    """

    Given a cycle containing one or more cycle.products, the inputs/emissions/products/transformations are expressed per "1ha"

    We create a SimaPro process block that contains the same products as in the form of "ProductOutputRow" and contains the same list of cycle.emissions and cycle.inputs converted and stored in
     `ProcessBlock.emissionsToAir`
     `ProcessBlock.emissionsToWater`
     `ProcessBlock.electricityAndHeat`
     `ProcessBlock.resources`
     etc, with the same amounts.

     Each ProductOutputRow has a ProductOutputRow.allocation as a %. Summing all ProductOutputRow.allocation sums to 100. The SemaPro software will display scaled values of all emissions / resources depending on the product selected.

     We turn the cycle into a system process block.


    """
    global term_map_obj

    term_map_obj = FlowMap(mapping_files_directory)
    context = {"term_map_obj": term_map_obj}

    if not impact_assessment.cycle:
        raise Exception(f"No cycle found in {impact_assessment.id}")

    target_cycle = impact_assessment.cycle
    if target_cycle.transformations:
        logger.warning("Not implemented: cycle.transformations")

    if target_cycle.functionalUnit != "1 ha":
        raise Exception("Only relative functional unit supported")

    if target_cycle.functionalUnitDetails:
        logger.warning("Not implemented: cycle.functionalUnitDetails")

    if target_cycle.siteArea and target_cycle.siteArea != 1:
        logger.warning("Not implemented: cycle.siteArea !- 1")

    if target_cycle.covarianceMatrixIds or target_cycle.covarianceMatrix:
        logger.warning("Not implemented: covarianceMatrix")

    logger.info(msg=f"Loaded data as hestia schema {type(impact_assessment)}")

    date_created = (target_cycle.updatedAt or
                    target_cycle.createdAt or
                    impact_assessment.updatedAt or
                    impact_assessment.createdAt)

    sima_pro_header = SimaProHeader(date=date_created, project=generate_project_name(impact_assessment, target_cycle))

    sema_pro_file_obj = SimaProFile(header=sima_pro_header, blocks=[])

    if impact_assessment.allocationMethod != "economic":
        raise Exception("Only economic allocation supported")

    hestia_products = [product for product in target_cycle.products if not _product_is_waste(product)]
    hestia_waste_products = [product for product in target_cycle.products if _product_is_waste(product)]

    total_allocation = sum([x.economicValueShare or 0 for x in hestia_products])
    recalculate_allocation = total_allocation != 100
    recalculate_allocation and logger.warning("Product allocations do not sum to 100%. Estimating new product allocations.")

    product_rows = convert_products(hestia_products, target_cycle, recalculate_allocation=recalculate_allocation)
    finalWasteFlows, waste_to_treatment = convert_waste_products(context, hestia_waste_products, target_cycle)

    process_name = f"{target_cycle.name or impact_assessment.name}, at farm gate"
    if process_type == "System":
        process_name += ", S"
    elif process_type == "Unit process":
        process_name += ", U"

    literatures, new_literature_blocks = convert_cycle_sources(context, impact_assessment, target_cycle)

    verification_comment = "Validator: HESTIA Team\\nE-mail: community@hestia.earth"
    if target_cycle.aggregated and target_cycle.aggregatedDataValidated is not None:
        verification_comment += f"\\nAggregation validated by hestia: {target_cycle.aggregatedDataValidated}"

    sima_pro_process = SimaProProcessBlock(
        category="material",
        processType=process_type,
        name=process_name,
        status="Draft",
        time_period=f"{target_cycle.startDate.year}-{target_cycle.endDate.year}" if target_cycle.startDate and target_cycle.endDate else None,
        geography=safe_string(target_cycle.site.country.name) if target_cycle.site.country else None,
        infrastructure=False,
        date=target_cycle.updatedAt or target_cycle.createdAt,
        record="Data entry by: HESTIA Team\\nE-mail: community@hestia.earth",
        generator="HESTIA team",
        collectionMethod="Data collected by the HESTIA team from industry reports, databases, and published Life Cycle Assessments.",
        verification=verification_comment,
        comment=generate_process_comment(target_cycle),
        allocationRules="economic",
        allocation_method=None,
        dataTreatment=None,
        systemDescription=SystemDescriptionRow(name="HESTIA", comment=""),
        external_documents=ExternalDocumentsRow(url=f"https://www.hestia.earth/cycle/{target_cycle.id}"),
        wasteTreatment=None,
        # wasteScenario=None,
        literatures=literatures,
        products=product_rows,
        avoidedProducts=[],
        materialsAndFuels=[],  # TechExchangeRow ref upstream processes and their products
        electricityAndHeat=[],
        wasteToTreatment=waste_to_treatment,  # TechExchangeRow
        # separatedWaste=[],
        # remainingWaste=[],
        resources=[],
        emissionsToAir=[],
        emissionsToWater=[],
        emissionsToSoil=[],
        finalWasteFlows=finalWasteFlows,
        nonMaterialEmissions=[],
        socialIssues=[],
        economicIssues=[],
        inputParameters=[],
        calculatedParameters=[],
    )

    inventory_blocks = defaultdict(list)
    inventory_blocks.update({
        "Raw materials": [],
        "Airborne emissions": [],
        "Waterborne emissions": [],
        "Emissions to soil": [],
        "Final waste flows": finalWasteFlows,
        "Non material emissions": [],
    })
    used_units = set()
    dummy_processes = []
    new_processes = []

    if target_cycle.transformations:
        raise Exception("Cycle transformations not implemented")

    if sima_pro_process.processType == "Unit process":
        recreate_processes_from_background_emissions = True
    else:
        recreate_processes_from_background_emissions = False

    cycle_background_emissions = [em for em in target_cycle.emissions if
                                  em.methodTier == "background" and unpack_list_values(em.value) != 0]
    cycle_other_emissions = [em for em in target_cycle.emissions if
                             em.methodTier != "background" and unpack_list_values(em.value) != 0]

    resources_inputs = [input_entry for input_entry in target_cycle.inputs if not
    input_entry.term.termType in ['electricity']]  # ElementaryExchangeRow

    if recreate_processes_from_background_emissions:
        # WIP todo cannot recreate unit processes when an emission comes from multiple .inputs
        updated_cycle_emissions, updated_cycle_inputs, sima_pro_process, new_processes, used_libraries = convert_to_multiple_processes(
            context,
            cycle_background_emissions,
            sima_pro_process,
            target_cycle)
        emissions_to_add_to_main_process = updated_cycle_emissions
        resources_inputs_to_add_to_main_process = [input_entry for input_entry in updated_cycle_inputs
                                                   if not input_entry.term.termType in ['electricity']]
        sema_pro_file_obj.header.libraries.extend(sorted(list(used_libraries)))

    else:
        emissions_to_add_to_main_process = cycle_other_emissions + cycle_background_emissions
        resources_inputs_to_add_to_main_process = resources_inputs

    for cycle_emission in emissions_to_add_to_main_process:

        if cycle_emission.sd or cycle_emission.min or cycle_emission.max or cycle_emission.statsDefinition != "cycles":
            logger.warning("Not implemented: Emission SD/Min/Max")

        try:
            if cycle_emission.term.termType in attribute_maps:

                attribute_name = _bucket_term_to_process_field(cycle_emission.term)
                block_name = _bucket_term_to_inventory_block(cycle_emission.term)

                sima_pro_process, used_units, inventory_blocks = hestia_entry_to_exchange_fields(
                    context, cycle_emission,
                    inventory_blocks,
                    sima_pro_process,
                    used_units,
                    process_attribute=attribute_name,
                    inventory_blocks_name=block_name)

                # getattr(sima_pro_process, attribute_name).append(elementary_exchange_row)
                # added = True
                # inventory_blocks[
                #     attribute_maps2[str(cycle_emission.term.termType)][compartment_string]].append(
                #     elementary_exchange_row)
                # break
                # if not added:
                #     pass

            else:
                raise Exception("not implemented")

        except MapperError as e:
            logger.error(e)
        except Exception as e:
            logger.error(e)
            raise e

    # cycle.inputs to ElementaryExchangeRow
    for input_entry in resources_inputs_to_add_to_main_process:
        if input_entry.sd or input_entry.min or input_entry.max:
            logger.warning("Not implemented: Input SD/Min/Max")

        if input_entry.impactAssessment or input_entry.impactAssessmentIsProxy:
            logger.warning("Background emissions via impactAssessment not implemented")

        if input_entry.operation:
            logger.warning("Not implemented: Input operation")

        try:
            sima_pro_process, used_units, inventory_blocks = hestia_entry_to_exchange_fields(
                context, input_entry,
                inventory_blocks,
                sima_pro_process,
                used_units,
                process_attribute="resources",
                inventory_blocks_name="Raw materials")

        except MapperError as e:
            logger.error(e)
        except Exception as e:
            logger.error(e)
            raise e

    # impact_assessment.emissionsResourceUse to ElementaryExchangeRow (rescaled)
    for product in target_cycle.products:
        if _product_is_waste(product):
            continue
        for target_impact_assessment in [impact_assessment]:
            if product.term.id in target_impact_assessment.product.term.id:
                for indicator_entry in target_impact_assessment.emissionsResourceUse:
                    if indicator_entry.term.id in hestia_land_use_indicator_ids:
                        if indicator_entry.value != 0:
                            # rescale as impact assessments have functional unit 1.
                            indicator_entry.value = [indicator_entry.value * unpack_list_values(product.value)]

                            try:
                                sima_pro_process, used_units, inventory_blocks = hestia_entry_to_exchange_fields(
                                    context, indicator_entry,
                                    inventory_blocks,
                                    sima_pro_process,
                                    used_units,
                                    process_attribute="resources",
                                    inventory_blocks_name="Raw materials")

                            except MapperError as e:
                                logger.error(e)
                            except Exception as e:
                                logger.error(e)
                                raise e

    electricityAndHeat_inputs = [input_entry for input_entry in target_cycle.inputs if
                                 input_entry.term.termType in ['electricity']]  # TechExchangeRow todo

    for input_entry in electricityAndHeat_inputs:  # TechExchangeRow
        if input_entry.sd or input_entry.min or input_entry.max:
            raise Exception("Not implemented")
        try:  # todo if linking to an external process must add as dummy or include real process
            tech_exchange_row = converter_obj.transmute(source_model_obj=input_entry,
                                                        destination_model=TechExchangeRow,
                                                        context=context)
            if isinstance(tech_exchange_row, list):
                tech_exchange_rows = tech_exchange_row
            else:
                tech_exchange_rows = [tech_exchange_row]

            for tech_exchange_row in tech_exchange_rows:
                if tech_exchange_row.flow_metadata and "target_unit" in tech_exchange_row.flow_metadata:
                    used_units.add(add_default_unit(tech_exchange_row))

                # if input_entry.term.termType in attribute_maps:
                #     for tag in attribute_maps[str(cycle_emission.term.termType)]:
                #         if tag in cycle_emission.term.id:
                #             getattr(sima_pro_process, attribute_maps[str(cycle_emission.term.termType)][tag]).append(
                #                 pydantic_process_out)
                #             inventory_blocks[attribute_maps2[str(cycle_emission.term.termType)][tag]].append(
                #                 pydantic_process_out)
                #             break
                #
                # elif input_entry.term.termType in ['resourceUse']:
                #     sima_pro_process.resources.append(pydantic_process_out)
                #     inventory_blocks['Raw materials'].append(pydantic_process_out)
                #
                # else:
                # todo
                sima_pro_process.materialsAndFuels.append(tech_exchange_row)

        except MapperError as e:
            logger.error(e)
        except Exception as e:
            logger.error(e)
            raise e

    sema_pro_file_obj.blocks.append(sima_pro_process)
    sema_pro_file_obj.blocks.extend(new_processes)
    sema_pro_file_obj.blocks.extend(dummy_processes)

    units_block = UnitBlock(rows=[])
    for used_unit in sorted(list(used_units)):
        units_block.rows.append(UnitRow(name=used_unit[0],
                                        conversion_factor=used_unit[1],
                                        dimension=unit_categories.get(used_unit[2], "Unknown"),
                                        reference_unit=used_unit[2],
                                        )
                                )

    quantities_block = QuantityBlock(rows=[])

    quantities_cats = set()
    for used_unit in units_block.rows:
        quantities_cats.add(used_unit.dimension)

    for used_category in sorted(list(quantities_cats)):
        quantities_block.rows.append(QuantityRow(name=used_category, comment=True))
    sema_pro_file_obj.blocks.append(quantities_block)
    sema_pro_file_obj.blocks.append(units_block)

    for block_label, inventory_rows in inventory_blocks.items():
        new_block = GenericBiosphere(block_header=block_label, rows=[])

        seen = set()
        for row in inventory_rows:
            cas_field, comment_field = _build_elementary_flow_description(row)

            if (row.name, row.unit, cas_field) in seen:
                continue

            new_block.rows.append(ElementaryFlowRow(name=row.name,
                                                    unit=row.unit,
                                                    cas=cas_field,
                                                    comment=comment_field,
                                                    platformId=row.platformId)
                                  )
            seen.add((row.name, row.unit, cas_field))
        sema_pro_file_obj.blocks.append(new_block)

    sema_pro_file_obj.blocks.append(SystemDescriptionBlock(name="HESTIA",
                                                           category="Others",
                                                           description="Hestia Platform",
                                                           allocation_rules="economic",
                                                           ))
    sema_pro_file_obj.blocks.extend(new_literature_blocks)

    return sema_pro_file_obj


whitelisted_ecoinvent_background_inputs = {  # todo
    'diesel': 'B80EB2D5-1256-41BB-A61D-83252D0DFD4D',
    'machineryInfrastructureDepreciatedAmountPerCycle': '663A4580-9FA2-4EC3-8174-5A18ED250015',
}
whitelisted_openlca_background_inputs = []


def emission_is_from_ecoinvent(emission: Emission) -> bool:
    if emission.methodModel and emission.methodModel.id in ['ecoinventV3']:
        return True
    return False


def term_should_be_split_out(full_input: Input) -> bool:
    if ref_ecoinvent_platform_id := parse_ecoinvent_ref_id(full_input):
        if ref_ecoinvent_platform_id.upper() in whitelisted_ecoinvent_background_inputs.values():  # todo
            return True
        else:
            return False
    elif full_input.term.openLCAId and full_input.term.openLCAId in whitelisted_openlca_background_inputs:
        return True

    elif full_input.impactAssessment:
        return True

    return False


def convert_to_multiple_processes(context: dict,
                                  cycle_background_emissions: list,
                                  sima_pro_process: SimaProProcessBlock,
                                  target_cycle: Cycle) -> tuple[list, list, SimaProProcessBlock, List[
    SimaProProcessBlock], Set[str]]:
    new_processes_blocks = []
    used_libraries = set()
    if not cycle_background_emissions:
        return cycle_background_emissions, target_cycle.inputs, sima_pro_process, new_processes_blocks, used_libraries

    updated_cycle_background_emissions = cycle_background_emissions.copy()
    updated_cycle_inputs = target_cycle.inputs.copy()

    background_emissions_group_by_inputs = defaultdict(list)
    for k, v in groupby(cycle_background_emissions, key=_group__by_inputs_key):
        background_emissions_group_by_inputs[k].extend(list(v))

    for input_key, grouped_cycle_emission in background_emissions_group_by_inputs.items():
        # Each background emission should have one or more .inputs that match cycle.inputs.
        tech_exchange_row = None
        is_ecoinvent_process = False
        create_new_process = False
        added_tech_exchange = False
        try:
            if len(input_key[0]) != 1:
                raise ExtractingProcessError(
                    f"Cannot separate emissions with more than one contributing input: {input_key}")

            if any([len(emission.inputs) != 1 for emission in grouped_cycle_emission]):
                raise ExtractingProcessError("Cannot separate emissions with more than one contributing input")

            input_term_id = input_key[0][0]

            full_input = next((input_e for input_e in target_cycle.inputs if input_e.term.id == input_term_id), None)

            if not full_input:
                raise ExtractingProcessError(f"Cannot find referenced input for emission group {input_key}")

            full_input.term = update_hestia_node(full_input.term)

            if not term_should_be_split_out(full_input):
                raise ExtractingProcessError(f"Skipping: {full_input}")

            if full_input.term.openLCAId:
                raise ExtractingProcessError("Not implemented openLCAId")

            if parse_ecoinvent_ref_id(full_input):
                create_new_process = False
                is_ecoinvent_process = True

            elif full_input.impactAssessment:
                # Then we can add an entire new process to the file and link processes together
                raise ExtractingProcessError("Not implemented")
                create_new_process = True
            else:
                create_new_process = False

            try:
                tech_exchange_row = converter_obj.transmute(  # todo return what
                    source_model_obj=full_input,
                    destination_model=EcoinventTechExchangeRow,
                )

                sima_pro_process.materialsAndFuels.append(tech_exchange_row)
                added_tech_exchange = True
            except Exception as e:
                raise ExtractingProcessError(e)

            if create_new_process:  # todo add as a dummy or add as a converted impact assessment?
                raise Exception("not implemented")
                # We create a new process linking to this emission:
                new_background_process: SimaProProcessBlock = converter_obj.transmute(
                    source_model_obj=full_input.impactAssessment,
                    destination_model=SimaProProcessBlock,
                    context=context | {"sima_pro_process_date": sima_pro_process.date})

                new_processes_blocks.append(new_background_process)


        except MapperError as e:
            logger.error(e)
        except ExtractingProcessError as e:
            logger.error(e)
            added_tech_exchange = False
        except Exception as e:
            logger.error(e)
            raise e

        if added_tech_exchange:
            # then we remove the emissions and inputs from the original cycle:
            updated_cycle_inputs.remove(full_input)
            for emission in grouped_cycle_emission:
                updated_cycle_background_emissions.remove(emission)

            if is_ecoinvent_process:
                used_libraries.update(SIMAPRO_LIBRARY_ECOINVENT)
        else:
            # Then emissions and input stay within the same process.
            pass

    if new_processes_blocks:
        # each of these processes should be referenced in the main process "Materials/fuels":
        for simapro_process in new_processes_blocks:
            # get the equivalent input term / tech exchange row from cycle.inputs
            new_process_product_row = simapro_process.products[0]

            # for candidate_input in target_cycle.inputs:  # todo check for edge case where a emission has 2 cycle_inputs or 2 emissions point to the same cycle_input and the cycle_input amount should not be duplicated or split in half?
            #     if candidate_input.term.model_dump(by_alias=True,
            #                                        exclude_unset=True) == new_process_product_row.row_metadata.get(
            #         "orignal_term"):
            tech_exchange_row = converter_obj.transmute(source_model_obj=simapro_process,
                                                        destination_model=TechExchangeRow,
                                                        context=context)
            sima_pro_process.materialsAndFuels.append(tech_exchange_row)
            # must be same product name as in dummy process

    return updated_cycle_background_emissions, updated_cycle_inputs, sima_pro_process, new_processes_blocks, used_libraries


def convert_cycle_sources(context: dict, impact_assessment: ImpactAssessment, target_cycle: Cycle):
    new_literature_blocks = []
    literatures = []
    target_sources = []
    if target_cycle.defaultSource:
        target_sources.append(target_cycle.defaultSource)
        if target_cycle.defaultSource.metaAnalyses:
            target_sources.extend(target_cycle.defaultSource.metaAnalyses)
    if target_cycle.aggregatedSources:
        target_sources.extend(target_cycle.aggregatedSources)
    if impact_assessment.source:
        target_sources.append(impact_assessment.source)
        if impact_assessment.source.metaAnalyses:
            target_sources.extend(impact_assessment.source.metaAnalyses)
    for source in target_sources:
        if not any([source.name == x.name for x in new_literature_blocks]):
            literature_row = converter_obj.transmute(source_model_obj=source,
                                                     destination_model=LiteratureRow,
                                                     context=context)
            literatures.append(literature_row)

            literature_ref_block = converter_obj.transmute(source_model_obj=source,
                                                           destination_model=LiteratureReferenceBlock,
                                                           context=context)

            new_literature_blocks.append(literature_ref_block)
    return literatures, new_literature_blocks


def generate_project_name(impact_assessment, target_cycle):
    if target_cycle and target_cycle.name:
        project_name = target_cycle.name
        if target_cycle.aggregated:
            project_name += " (aggregated)"

    else:
        project_name = impact_assessment.name
        if impact_assessment.aggregated:
            project_name += " (aggregated)"
    return project_name


def convert_products(hestia_products: List[Product], target_cycle: Cycle, recalculate_allocation=False):
    product_rows = []

    if recalculate_allocation:
        if len(hestia_products) == 1 and hestia_products[0].primary:
            hestia_product = hestia_products[0]
            product_platform_id = parse_ecoinvent_ref_id(hestia_product)

            new_allocation = 100
            logger.warning(f"Updating primary product '{hestia_product.term.id}' allocation to {new_allocation}")
            allocation_notes = f"\n Original economicValueShare: {hestia_product.economicValueShare}"

            product_rows.append(ProductOutputRow(
                name=hestia_product.term.name + " | " + target_cycle.name + ", at farm gate",
                unit=hestia_product.term.units,
                amount=unpack_list_values(hestia_product.value),
                allocation=new_allocation,
                wasteType="Undefined",  # todo
                category=_map_to_category(hestia_product),
                comment=_build_hestia_product_description(hestia_product) + allocation_notes,
                platformId=product_platform_id)
            )
            return product_rows

        else:
            raise Exception(
                "Cannot recalculate missing economicValueShare for {} products".format(len(hestia_products)))

    total_evs = 0
    for hestia_product in hestia_products:
        if hestia_product.value and unpack_list_values(hestia_product.value) != 0:
            product_platform_id = parse_ecoinvent_ref_id(hestia_product)

            if not product_platform_id:
                logger.warning(f"Could not find ecoinvent id for: {hestia_product.term.id}")

            allocation_notes = ''

            if hestia_product.economicValueShare is None:
                logger.error(f"Skipping product '{hestia_product.term.id}' because 'economicValueShare' is None")
                continue
            total_evs += hestia_product.economicValueShare
            product_rows.append(ProductOutputRow(
                name=hestia_product.term.name + " | " + target_cycle.name + ", at farm gate",
                unit=hestia_product.term.units,
                amount=hestia_product.value[0],
                allocation=hestia_product.economicValueShare,
                wasteType="Undefined",  # todo
                category='material\\' + str(hestia_product.term.termType),
                comment=_build_hestia_product_description(hestia_product) + allocation_notes,
                platformId=product_platform_id.upper() if product_platform_id else None)
            )

    if not product_rows:
        raise Exception("No products can be added")

    if not (99.5 <= total_evs <= 100.5):
        raise Exception("Total sum of economicValueShare must be 100%")

    return product_rows


def parse_ecoinvent_ref_id(hestia_product: Product | Input):
    platform_id = None
    if hestia_product.term.ecoinventReferenceProductId:
        if is_url(hestia_product.term.ecoinventReferenceProductId.id):
            new_id = hestia_product.term.ecoinventReferenceProductId.id.removesuffix("/").removeprefix(
                "https://glossary.ecoinvent.org/ids/")
            if is_uuid(new_id):
                platform_id = new_id.upper()
        elif is_uuid(hestia_product.term.ecoinventReferenceProductId.id):
            platform_id = hestia_product.term.ecoinventReferenceProductId.id
    return platform_id


def convert_waste_products(context: dict,
                           hestia_waste_products: List[Product],
                           target_cycle: Cycle,
                           split_out_waste=True,
                           waste_fallback_to_tech_exchange=False):
    # strip out "duplicate" waste entries when the cycle contains overlapping indicators:
    for waste_product in hestia_waste_products:
        waste_term_u = update_hestia_node(waste_product.term)
        waste_product.term = waste_term_u

    new_hestia_waste_products = hestia_waste_products.copy()
    for waste_product in hestia_waste_products:
        if waste_product.term.subClassOf:
            for parent_term in waste_product.term.subClassOf:
                for i, prod in enumerate(new_hestia_waste_products):
                    if parent_term.id == prod.term.id:
                        del new_hestia_waste_products[i]
                        break
    hestia_waste_products = new_hestia_waste_products

    finalWasteFlows = []
    waste_to_treatment = []

    if split_out_waste:
        for hestia_product in hestia_waste_products:
            if hestia_product.value and unpack_list_values(hestia_product.value) != 0:

                try:
                    elementary_exchange_row_waste = converter_obj.transmute(source_model_obj=hestia_product,
                                                                            destination_model=ElementaryExchangeRow,
                                                                            context=context)
                    finalWasteFlows.append(elementary_exchange_row_waste)
                except Exception as e:
                    logger.error(e)

                    if waste_fallback_to_tech_exchange:
                        waste_to_treatment.append(
                            TechExchangeRow(
                                name=hestia_product.term.name + " | " + target_cycle.name,
                                unit=hestia_product.term.units,
                                amount=unpack_list_values(hestia_product.value),
                                uncertainty=UncertaintyRecordUndefined(),
                                # wasteType="Undefined",  # todo
                                # category=f"material\\{hestia_product.term.termType}",
                                # todo add hestia_product.term.id in freetext?
                                comment=_build_hestia_product_description(hestia_product),
                                platformId=None)  # todo check platformid
                        )
                    else:
                        if not "kg" in hestia_product.term.units:
                            raise Exception("Cannot fallback to mapping waste product to 'Waste, unspecified' "
                                            "due to unit missmatch")
                        finalWasteFlows.append(ElementaryExchangeRow(
                            name="Waste, unspecified",
                            subCompartment="Final waste flows",
                            unit="kg",
                            amount=unpack_list_values(hestia_product.value),
                            # uncertainty=UncertaintyRecordUndefined,
                            comment=_build_hestia_product_description(
                                hestia_product) + f" Hestia term id: {hestia_product.term.id}",
                            platformId="a9e58a44-064a-4870-ab7c-07312074c42c".upper(),
                            # Professional 9.6	"Waste, unspecified"
                            flow_metadata={
                                "orignal_term": hestia_product.term.model_dump(by_alias=True, exclude_unset=True)}
                        ))
    return finalWasteFlows, waste_to_treatment


def generate_process_comment(cycle: Cycle):
    """
    # DescriptionStatus: DraftRecord: Data entry by: HESTIA TeamGenerator: HESTIA team# Timetime description 2027 to 2028# Geographygeo afghanistan desciption# Technologytech description# ProjectSystem: HESTIA# CopyrightNo
    """

    hestia_products = [product for product in cycle.products if not _product_is_waste(product)]

    main_hestia_product = next((product_entry for product_entry in hestia_products if product_entry.primary), None)

    comment = ""
    if main_hestia_product:
        comment += f"\nMain product:\n"
        for k, v in main_hestia_product.term.model_dump(exclude_none=True, by_alias=True, mode='json',
                                                        include={'name', 'iso31662Code', 'gadmFullName'
                                                                 }).items():
            comment = convert_schema_dict_to_text(k, comment, v)

        for k, v in main_hestia_product.model_dump(
                exclude_none=True, by_alias=True, mode='json',
                include={'description', 'variety', 'primary'}).items():
            comment = convert_schema_dict_to_text(k, comment, v)
        comment += "\n"

    if cycle and cycle.site and cycle.site.country:
        # comment += f"\\n# Geography\\n{cycle.site.country.name}\\n"  # todo openlca workaround
        comment += f"\nGeography\n{cycle.site.country.name}\n"

    if cycle.aggregated:
        comment += f"\nAggregated from multiple cycles: Yes"
        comment += f"\nAggregated from {len(cycle.aggregatedCycles)} cycles"

    if cycle.aggregatedQualityScore:
        comment += f"\nAggregated Quality Score: {cycle.aggregatedQualityScore}"

    if cycle.aggregatedQualityScoreMax:
        comment += f"\nMaximum Aggregated Quality Score: {cycle.aggregatedQualityScoreMax}"

    if cycle.startDate and cycle.endDate:
        comment += f"\nTime Period: {cycle.startDate.year}-{cycle.endDate.year}"

    comment += f"\n"
    for k, v in cycle.model_dump(
            exclude_none=True, by_alias=True, mode='json',
            include={'startDateDefinition',
                     'originalId',
                     'numberOfCycles',
                     'numberOfReplications',
                     'description',
                     'updatedAt',
                     'treatment',
                     }).items():
        comment = convert_schema_dict_to_text(k, comment, v)
    return comment.replace("\n", "\\n")


def hestia_entry_to_exchange_fields(context: dict,
                                    input_entry, inventory_blocks: dict, sima_pro_process, used_units: set,
                                    process_attribute: Literal[
                                        'resources',
                                        'emissionsToAir',
                                        'emissionsToSoil',
                                        'emissionsToWater',
                                        'nonMaterialEmissions',
                                        'economicIssues',
                                        'socialIssues',
                                        'finalWasteFlows',
                                    ],
                                    inventory_blocks_name: Literal[
                                        "Raw materials",
                                        "Airborne emissions",
                                        "Waterborne emissions",
                                        "Emissions to soil",
                                        "Final waste flows",
                                        "Non material emissions",
                                    ]):
    elementary_exchange_row = converter_obj.transmute(source_model_obj=input_entry,
                                                      destination_model=ElementaryExchangeRow,
                                                      context=context)
    if isinstance(elementary_exchange_row, list):
        elementary_exchange_rows = elementary_exchange_row
    else:
        elementary_exchange_rows = [elementary_exchange_row]

    for elementary_exchange_row in elementary_exchange_rows:
        getattr(sima_pro_process, process_attribute).append(elementary_exchange_row)

        if elementary_exchange_row.flow_metadata and "target_unit" in elementary_exchange_row.flow_metadata:
            used_units.add(add_default_unit(elementary_exchange_row))

        inventory_blocks[inventory_blocks_name].append(elementary_exchange_row)

    return sima_pro_process, used_units, inventory_blocks


def _build_elementary_flow_description(row: ElementaryExchangeRow):
    include_cas = True
    cas_field = None

    comment_field = ""
    if row.flow_metadata.get('original_term_country') and row.flow_metadata.get('original_term_country_iso31662Code'):
        country_str = row.flow_metadata.get('original_term_country').get("name") or row.flow_metadata.get(
            'original_term_country').get("@id")
        comment_field += f"{row.flow_metadata.get('original_term_country_iso31662Code')} = {country_str}"
    if row.comment:
        if "Emission from: " in row.comment:
            stripped_comment = row.comment.split("Emission from: ")[0]
            comment_field += stripped_comment.rstrip(" ") + " "
        else:
            comment_field += row.comment + " "
    if include_cas:
        result = download_hestia(row.flow_metadata.get('original_term', {}).get("@id"))
        cas_entry = result.get('casNumber')
        if cas_entry:
            padded_cas_entry = cas_entry.rjust(11, '0')

            if len(cas_entry) == 12:
                cas_field = None
                comment_field = comment_field + "Cas: " + padded_cas_entry + " "
            else:
                cas_field = padded_cas_entry

        if result.get("canonicalSmiles"):
            comment_field += f"Formula: {result.get('canonicalSmiles')} "
        elif row.flow_metadata.get('original_term', {}).get("units", "").startswith("kg "):
            unit = row.flow_metadata.get('original_term', {}).get("units")
            if (unit.startswith("kg ") and
                    not any([non_formula in unit for non_formula in ["dry matter", "active ingredient"]])):
                formula = unit.removeprefix("kg ")
                comment_field += f"Formula: {formula} "
    return cas_field, comment_field.rstrip()


def add_default_unit(e_row):
    return (e_row.flow_metadata['target_unit'], 1, e_row.flow_metadata['target_unit'],)


def _build_hestia_product_description(hestia_product: Product) -> str:
    product_comment = ""
    hestia_product.term = update_hestia_node(hestia_product.term)
    for k, v in hestia_product.term.model_dump(exclude_none=True, by_alias=True, mode='json',
                                               include={'name', 'id',
                                                        'synonyms',
                                                        'definition', 'description', 'scientificName', 'agrovoc',
                                                        'wikipedia', 'pubchem',
                                                        'subClassOf', 'casNumber', 'gadmFullName', 'iso31662Code',
                                                        }).items():
        product_comment = convert_schema_dict_to_text(k, product_comment, v)

    for k, v in hestia_product.model_dump(
            exclude_none=True, by_alias=True, mode='json',
            include={'description', 'variety', 'startDate', 'endDate', 'dates', 'fate', 'observations',
                     'priceStatsDefinition', 'price', 'priceMax', 'priceMin',
                     'priceSd', 'properties', 'revenueStatsDefinition', 'revenue', 'revenueMax', 'revenueMin',
                     'revenueSd', 'transport'
                     }).items():
        product_comment = convert_schema_dict_to_text(k, product_comment, v)
    return product_comment.strip("\n")


def convert_schema_dict_to_text(k: str, comment_str: str, v: Union[str, dict, list]) -> str:
    comment_str += f"{k.capitalize()}: "
    if isinstance(v, str):
        comment_str += f"'{v}'\n"
    elif isinstance(v, dict) and "@id" in v:
        comment_str += f"'{v.get("@id")}'\n"
    elif isinstance(v, list):
        items = []
        for entry in v[:min(4, len(v))]:
            if isinstance(entry, str) or isinstance(entry, float):
                items.append(repr(entry))
            elif isinstance(entry, dict):
                if entry.get('@type') == "Term":
                    items.append(f"'{entry.get("@id")}'")
                elif entry.get('@type') == "Property":
                    items.append(f"Property: '{entry.get("term", {}).get("@id")}'")
                    if entry.get("value"):
                        items.append(f"with value: '{entry.get("value")}'")
                    if entry.get("share"):
                        items.append(f"with share: '{entry.get("share")}'")
                else:
                    items.append(repr(entry))
            else:
                pass
        comment_str += ", ".join(items) + "\n"
    else:
        comment_str += f"{repr(v)}\n"
    return comment_str
