import inspect
import logging
from functools import reduce
from typing import (
    Type,
    Optional,
    Any,
    Dict,
    Callable,
    Tuple,
    Union,
    get_type_hints,
    List,
    _UnionGenericAlias, _GenericAlias,
    TypeVar,
)
from pydantic import ValidationError as ModelValidationError, BaseModel, TypeAdapter
from pydantic import validate_call

from .utils import extract_nested_annotated_field_types

DestinationFieldName = str
SourceFieldName = str
FieldMap = Dict[DestinationFieldName, Union[Callable, SourceFieldName]]
ModelSchemaMapType = Dict[Tuple[str, str], Union[FieldMap, Callable]]
pydanticBaseModel = TypeVar('pydanticBaseModel', bound=BaseModel)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ConverterValidationError(Exception):
    """Base exception for Model Validation Errors"""


class CustomFunctionException(Exception):
    """Exception generated when running a custom function"""


class Converter:
    """
    Pydantic model schema converter.

    Based on pymapme https://github.com/funnydman/pymapme by author funnydman

    """

    @validate_call
    def __init__(self, map_field_dict: ModelSchemaMapType = None, validate_custom_function_args=False):
        self.validate_custom_function_args = validate_custom_function_args
        self.source_sep = "."
        self.model_schema_maps: ModelSchemaMapType = map_field_dict if map_field_dict else {}

    # @validate_call
    def register_model_map(
            self,
            source_model_type: Type[BaseModel],
            destination_model_type: Type[BaseModel],
            map_field_dict: Optional[FieldMap] = None,
            map_function: Optional[Callable] = None,
            reverse_function: Optional[Callable] = None,
            register_reverse_map: bool = True,
    ):
        """
        Declares how to transmute a pydantic model `source_model_type` to a `destination_model_type` pydantic model.

        Accepts a `map_field_dict` dictionary mapping fields to `destination_model_type` field names
        from `source_model_type` field names. Assumes the field map is symmetrical and saves the same map in reverse
        if `register_reverse_map` is True and the mappings are strings.

        Or a callable `map_function` that, given a instance of `source_model_type` must return a
        instance of `destination_model_type`. Can also specify a callable `reverse_function` that reverses
        the transformation.

        :param source_model_type:
        :param destination_model_type:
        :param map_field_dict:
        :param map_function:
        :param reverse_function:
        :param register_reverse_map:
        :return:
        """
        old_model_shema_maps = self.get_model_map(source_model_type=source_model_type,
                                                  destination_model_type=destination_model_type)
        if map_field_dict and not map_function:
            if old_model_shema_maps:
                logger.warning("Replacing existing model map with new field dict model map")

            self.model_schema_maps[
                (repr(source_model_type), repr(destination_model_type))
            ]: ModelSchemaMapType = map_field_dict

            # reverse
            if register_reverse_map:
                reversed_field_map: FieldMap = {v: k for k, v in map_field_dict.items() if
                                     isinstance(v, str) and self.source_sep not in v}
                if reversed_field_map:
                    self.register_model_map(source_model_type=destination_model_type,
                                            destination_model_type=source_model_type,
                                            map_field_dict=reversed_field_map,
                                            register_reverse_map=False)

        elif map_function and not map_field_dict:
            if old_model_shema_maps:
                logger.warning("Replacing existing model map with new map function")

            self.model_schema_maps[(repr(source_model_type), repr(destination_model_type))]: Callable = map_function

            self.check_function_types(map_function, source_model_type, destination_model_type)

            if reverse_function:
                self.register_model_map(source_model_type=destination_model_type,
                                        destination_model_type=source_model_type,
                                        map_function=reverse_function,
                                        register_reverse_map=False)
        else:
            raise Exception("Not a valid model schema map")

    def get_callable_model_map(
            self,
            source_model_type: Type[BaseModel],
            destination_model_type: Type[BaseModel],
    ):
        map_f: Callable = self.get_model_map(source_model_type=source_model_type,
                                             destination_model_type=destination_model_type)
        if map_f and isinstance(map_f, Callable):
            return map_f
        else:
            return None

    def get_schema_field_map(
            self,
            source_model_type: Type[BaseModel],
            destination_model_type: Type[BaseModel],
            field_name: str,
            manual_field_map: FieldMap = None) -> Optional[str]:
        map_d: FieldMap = manual_field_map or self.get_model_map(source_model_type=source_model_type,
                                                                 destination_model_type=destination_model_type)

        if (
                map_d
                and isinstance(map_d, dict)
                and field_name in map_d
                and not isinstance(map_d[field_name], Callable)
        ):
            return map_d[field_name]
        else:
            return None

    def get_callable_schema_field_map(
            self,
            source_model_type: Type[BaseModel],
            destination_model_type: Type[BaseModel],
            field_name: str,
            manual_function_map: FieldMap = None) -> Optional[Callable]:
        map_d: FieldMap = manual_function_map or self.get_model_map(source_model_type=source_model_type,
                                                                    destination_model_type=destination_model_type)

        if (
                map_d
                and isinstance(map_d, dict)
                and field_name in map_d
                and isinstance(map_d[field_name], Callable)
        ):
            return map_d[field_name]
        else:
            return None

    def get_model_map(
            self, source_model_type, destination_model_type
    ) -> Union[FieldMap, Callable]:
        return self.model_schema_maps.get(
            (repr(source_model_type), repr(destination_model_type))
        )

    # @validate_call
    def map_fields_from_model(
            self,
            source_model: BaseModel,
            destination_model_type: Type["BaseModel"],
            context: dict,
            manual_field_map: FieldMap = None,
            manual_function_map: FieldMap = None,
            **kwargs,
    ) -> dict:
        _default = object()
        model_data = {}
        if not context:
            context = {}
        if not manual_field_map:
            manual_field_map: FieldMap = {}
        if not manual_function_map:
            manual_function_map: FieldMap = {}
        try:
            dest_model_fields = destination_model_type.model_fields
        except AttributeError as e:
            logger.warning("Using old version of pydantic.", e)
            dest_model_fields = destination_model_type.__fields__

        for field_name, field in dest_model_fields.items():
            custom_model_function, value, adapter = None, None, None

            if source_path := self.get_schema_field_map(source_model_type=type(source_model),
                                                        destination_model_type=destination_model_type,
                                                        field_name=field_name,
                                                        manual_field_map=manual_field_map):
                value = self.map_from_model_field(
                    source_model=source_model,
                    source_path=source_path,
                    sep=self.source_sep,
                    default=_default,
                )

            elif source_func := self.get_callable_schema_field_map(
                    source_model_type=type(source_model),
                    destination_model_type=destination_model_type,
                    field_name=field_name,
                    manual_function_map=manual_function_map
            ):
                source_func_context = self.build_func_context(source_func, context)

                if self.validate_custom_function_args:
                    source_func = validate_call(source_func)

                value = source_func(
                    source_model,
                    field_name=field_name,
                    default=field.default or _default,
                    model_data=model_data,
                    **source_func_context,
                )
                # asas = self.extract_annotated_field_types(field, field_name)
                # self.check_custom_function_result(custom_function_result=value,
                #   todo                                custom_model_function=source_func,
                #                                   destination_model_type=asas,
                #                                   source_model=source_model)


            else:
                value = getattr(source_model, field_name, _default)

            if value is not _default:
                transmuted_value = self.transmute_field_data(value, source_model, destination_model_type, field_name,
                                                             # todo add amount conversion here?
                                                             context=context | {'model_data': model_data})

                if transmuted_value:
                    model_data[field_name] = transmuted_value
                else:
                    model_data[field_name] = value

                context['model_data'] = model_data

        if always_run_function := self.get_callable_schema_field_map(
                source_model_type=type(source_model),
                destination_model_type=destination_model_type,
                field_name="_always_run_",
        ):
            source_func_context = self.build_func_context(always_run_function, context)
            if self.validate_custom_function_args:
                always_run_function = validate_call(always_run_function)
            model_data = always_run_function(model_data=model_data,
                                             source_model=source_model,
                                             destination_model_type=destination_model_type,
                                             **source_func_context
                                             )

        return model_data

    def transmute_field_data(self, value,
                             source_model: BaseModel,
                             destination_model_type: Type["BaseModel"],
                             field_name: str,
                             context: dict) -> Union[List[pydanticBaseModel], pydanticBaseModel, None]:
        transmuted_value = None
        annotated_field_types = self.extract_annotated_field_types(destination_model_type, field_name)

        for acceptable_type in annotated_field_types:
            if isinstance(value, acceptable_type):
                # Then there is no need to transmute this field since it is already in an acceptable format
                return None

        for annotated_field_type in annotated_field_types:
            # if (get_type_hints(destination_model_type)[field_name].__name__ == "List" and annotated_field_type)
            if ("typing.List[" in str(get_type_hints(destination_model_type)[field_name]) and
                    annotated_field_type and
                    isinstance(annotated_field_type, type) and
                    issubclass(annotated_field_type, BaseModel)):
                # Handles list of a sub schema we know how to handle
                if isinstance(value, list):  # todo check me Add better list type detection
                    source_field_type = type(value[0])
                else:
                    source_field_type = type(value)

                skip_on_error = self.get_schema_field_map(source_model_type=source_field_type,
                                                          destination_model_type=annotated_field_type,
                                                          field_name="_skip_on_error") or False
                transmuted_value: List = self.handle_list_of_items_using_transmute(
                    value,
                    destination_model=annotated_field_type,
                    context=context,
                    skip_on_error=skip_on_error
                )

            else:
                model_map = self.get_model_map(source_model_type=type(value), destination_model_type=annotated_field_type)

                if isinstance(value, BaseModel) or issubclass(type(value), BaseModel) or model_map:
                    try:
                        transmuted_value: pydanticBaseModel = self.transmute(source_model_obj=value,
                                                                             destination_model=annotated_field_type,
                                                                             context=context)
                    except CustomFunctionException as e:
                        logger.error(e)
                        logger.error(f"Failed to transmute for field {field_name}")

            return transmuted_value
        return None

    def handle_list_of_items_using_transmute(self, source_models: list, destination_model: Type, context: dict = None,
                                             skip_on_error: bool = False) -> List[pydanticBaseModel]:
        results = []
        for model_obj in source_models:
            result = None
            try:
                result: pydanticBaseModel = self.transmute(source_model_obj=model_obj,
                                                           destination_model=destination_model,
                                                           context=context)
            except Exception as e:
                if not skip_on_error:
                    raise e
            if result:
                results.append(result)
        return results

    @staticmethod
    def extract_annotated_field_types(destination_model_type: Type, field_name: str) -> List[type]:
        direct_type_hint = get_type_hints(destination_model_type)[field_name]

        nested_field_types = extract_nested_annotated_field_types(direct_type_hint)
        if nested_field_types and (
                isinstance(direct_type_hint, _UnionGenericAlias) or isinstance(direct_type_hint, _GenericAlias)):
            return nested_field_types
        else:
            return [direct_type_hint]

    @staticmethod
    def check_custom_function_result(custom_function_result: BaseModel,
                                     custom_model_function: Callable,
                                     destination_model_type: Type,
                                     source_model: BaseModel):

        if not isinstance(custom_function_result, destination_model_type):
            if isinstance(custom_function_result, list):
                list_of_destination_model_adapter = TypeAdapter(list[destination_model_type])
                try:
                    list_of_destination_model_adapter.validate_python(custom_function_result)
                except Exception as e:
                    raise CustomFunctionException(
                        f"Custom function '{custom_model_function.__name__}' for map "
                        f"'{type(source_model).__name__}' to '{repr(destination_model_type)}' returned a list that"
                        f"was not a valid list of '{destination_model_type}'", *e.args
                    )
            else:
                raise CustomFunctionException(
                    f"Custom function '{custom_model_function.__name__}' for map "
                    f"'{type(source_model).__name__}' to '{repr(destination_model_type)}' did not return a"
                    f" model of the desired schema {destination_model_type}"
                )

    @staticmethod
    def build_func_context(always_run_function, context):
        source_func_context: dict = {}
        if context:

            if "model_data" in context:
                context['parent_model_data'] = context['model_data']
                del context['model_data']

            source_func_params = inspect.signature(always_run_function).parameters
            source_func_context = {
                key: value
                for key, value in context.items()
                if key in source_func_params
            }
        return source_func_context

    @staticmethod
    def map_from_model_field(
            source_model: object,
            source_path: str,
            sep: Optional[str] = ".",
            default: Optional[Any] = None,
    ) -> Any:
        value = reduce(
            lambda val, key: (
                getattr(val, key, default) if isinstance(val, object) else default
            ),
            source_path.split(sep),
            source_model,
        )
        return value

    def map_from_model(
            self,
            source_model: BaseModel,
            destination_model_type: Type["BaseModel"],
            context: Optional[dict] = None,
            manual_field_map: Optional[dict] = None,
    ) -> "BaseModel":

        if custom_model_function := self.get_callable_model_map(
                source_model_type=type(source_model),
                destination_model_type=destination_model_type,
        ):
            custom_function_result: BaseModel = custom_model_function(
                source_model=source_model,
                destination_model=destination_model_type,
                context=context,
            )
            self.check_custom_function_result(custom_function_result, custom_model_function, destination_model_type,
                                              source_model)
            return custom_function_result

        else:
            try:
                model_data = self.map_fields_from_model(
                    source_model=source_model,
                    destination_model_type=destination_model_type,
                    context=context,
                    manual_field_map=manual_field_map,
                )

                return destination_model_type(**model_data)
            except Exception as e:
                if self.get_schema_field_map(source_model_type=type(source_model),
                                             destination_model_type=destination_model_type,
                                             field_name="_skip_on_error"):
                    return None
                else:
                    raise e

    # @validate_call
    def transmute(
            self,
            source_model_obj: BaseModel,
            destination_model: Type[BaseModel],
            context: Optional[dict] = None,
            manual_field_map: Optional[dict] = None,
    ) -> pydanticBaseModel:
        try:
            return self.map_from_model(
                source_model=source_model_obj,
                destination_model_type=destination_model,
                context=context,
                manual_field_map=manual_field_map,
            )
        except (AttributeError, TypeError) as exc:
            logging.error(
                "Failed to map model due to error. Reason: %s",
                exc,
            )
            raise ConverterValidationError(exc) from exc
        except ModelValidationError as exc:
            logging.error(
                "Failed to map model due to model validation error. Reason: %s", exc
            )
            raise ConverterValidationError(exc) from exc

    @staticmethod
    def check_function_types(
            map_function, source_model_type, destination_model_type
    ):

        type_hints = get_type_hints(map_function)
        if not type_hints.get("return"):
            logging.warning(
                f"Warning: register_model_map(): "
                f"Mapping '{source_model_type.__name__}' to '{destination_model_type.__name__}': "
                f"The custom function '{map_function.__name__}()' does not have a return type set. "
                f"Please add ' -> {destination_model_type.__name__}:' to your function's signature."
            )

        elif get_type_hints(map_function)["return"] != destination_model_type:
            logging.warning(
                f"Warning: register_model_map(): "
                f"Mapping '{source_model_type.__name__}' to '{destination_model_type.__name__}': "
                f"The custom function '{map_function.__name__}'() may return data of "
                f"type {get_type_hints(map_function)['return']} instead of the "
                f"expected {destination_model_type} "
            )
