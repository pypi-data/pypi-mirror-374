standard_comp_fields = [
    "Elementary flows/Emission to air/high population density",
    "Elementary flows/Emission to air/low population density",
    "Elementary flows/Emission to air/low population density, long-term",
    "Elementary flows/Emission to air/lower stratosphere + upper troposphere",
    "Elementary flows/Emission to air/unspecified",
    "Elementary flows/Emission to soil/agricultural",
    "Elementary flows/Emission to soil/forestry",
    "Elementary flows/Emission to soil/industrial",
    "Elementary flows/Emission to soil/unspecified",
    "Elementary flows/Emission to water/ground water",
    "Elementary flows/Emission to water/ground water, long-term",
    "Elementary flows/Emission to water/lake",
    "Elementary flows/Emission to water/ocean",
    "Elementary flows/Emission to water/river",
    "Elementary flows/Emission to water/surface water",
    "Elementary flows/Emission to water/unspecified",
    'Elementary flows/Resource/in ground',
    'Elementary flows/Resource/unspecified',
    'Elementary flows/Resource/biotic',
    'Elementary flows/Resource/in air',
    'Elementary flows/Waste/unspecified',

]
comp_map = {
    "Emissions to air": "Elementary flows/Emission to air/unspecified",
    "Emissions to air/high. pop.": "Elementary flows/Emission to air/high population density",
    "Emissions to air/low. pop.": "Elementary flows/Emission to air/low population density",
    "Emissions to air/low. pop., long-term": "Elementary flows/Emission to air/low population density, long-term",
    "Emissions to soil": "Elementary flows/Emission to soil/unspecified",
    "Emissions to soil/forestry": "Elementary flows/Emission to soil/forestry",
    "Emissions to water": "Elementary flows/Emission to water/unspecified",
    "Emissions to water/groundwater": "Elementary flows/Emission to water/ground water",
    "Emissions to water/groundwater, long-term": "Elementary flows/Emission to water/ground water, long-term",
    "Emissions to water/lake": "Elementary flows/Emission to water/lake",
    "Emissions to water/ocean": "Elementary flows/Emission to water/ocean",
    "Emissions to water/river": "Elementary flows/Emission to water/river",
    "water, ground-, long-term": "Elementary flows/Emission to water/ground water, long-term",
    'Emissions to soil/agricultural': "Elementary flows/Emission to soil/agricultural",
    'Emissions to air/stratosphere + troposphere': "Elementary flows/Emission to air/lower stratosphere + upper troposphere",
    'Emissions to soil/industrial': "Elementary flows/Emission to soil/industrial",

}


def convert_to_common_compartment(comp_name) -> str:
    if comp_name in standard_comp_fields:
        return comp_name
    if comp_name in comp_map:
        return comp_map[comp_name]
    raise Exception("unknown compartment {}".format(comp_name))


def comp_is_same_compartment_class(com_1, comp2):
    if com_1 not in standard_comp_fields:
        raise Exception("unknown compartment {}".format(com_1))
    if comp2 not in standard_comp_fields:
        raise Exception("unknown compartment {}".format(comp2))

    split1 = com_1.split("/")
    split2 = comp2.split("/")

    if split1[0:2] == split2[0:2]:
        return True
    return False


def compartment_is_a_subset_of(compartment_1, compartment_2):
    split1 = compartment_1.split("/")
    split2 = compartment_2.split("/")

    if split1[0:2] == split2[0:2]:
        if split2[2].lower() in ["", "unspecified"]:
            return True
        else:
            return False
    return False
