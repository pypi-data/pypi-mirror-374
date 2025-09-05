import ast
from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

import msgspec
from msgspec import Struct

from msgflux.dsl.typed_parsers.base import BaseTypedParser
from msgflux.utils.chat import response_format_from_json_schema
from msgflux.utils.xml import apply_xml_tags


SIGNATURE_DEFAULT_SYSTEM_MESSAGE = """
Your goal is to provide accurate, helpful, and well-reasoned responses.
Carefully analyze the user's request to fully understand the objective. Address all parts of the query.
Think step-by-step to formulate your answer. Where appropriate, briefly explain your reasoning process.
Structure your response clearly and concisely using dicts, lists, or other formatting.
Strive for factual accuracy.
Be helpful and informative, focusing on directly answering the user's prompt.
""".strip() # noqa: E501


@dataclass
class SignatureExamples:
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]


@dataclass
class FieldDescription:
    name: str
    dtype: str
    desc: Optional[str] = None
    ex: Optional[str] = None


class Field:
    def __init__(self, desc: Optional[str] = None, ex: Optional[str] = None):
        if isinstance(desc, str) or desc is None:
            self.desc = desc
        else:
            raise TypeError("desc must be a string or None")
        if isinstance(ex, str) or ex is None:
            self.ex = ex
        else:
            raise TypeError("ex must be a string or None")


class InputField(Field):
    """Represents an input field in a model signature.

    Args:
        desc:
            A description of the input field. Defaults to an empty string.
        ex:
            Input parameter example.
    """


class OutputField(Field):
    """Represents an output field in a model signature.

    Args:
        desc:
            A description of the output field. Defaults to an empty string.
        ex:
            Output parameter example.
    """


class _SignatureMeta(type):
    """Metaclass to process input and output fields in a model signature.

    This metaclass collects all `InputField` and `OutputField` instances
    defined in a class and stores them in `_inputs` and `_outputs`
    dictionaries, respectively.
    """

    def __new__(cls, name, bases, dct):
        inputs = {}
        outputs = {}

        for key, value in dct.items():
            if isinstance(value, InputField):
                inputs[key] = value
            elif isinstance(value, OutputField):
                outputs[key] = value

        dct["_inputs"] = inputs
        dct["_outputs"] = outputs
        return super().__new__(cls, name, bases, dct)


class Signature(metaclass=_SignatureMeta):
    """Base class for model signatures.

    This class provides functionality to define and inspect input and output fields
    of a model. It uses the `_SignatureMeta` metaclass to automatically collect
    `InputField` and `OutputField` instances.

    !!! example:
        ```python
        class CheckCitationFaithfulness(Signature):
            \"\"\"Verify that the text is based on the provided context.\"\"\"

            context: str = InputField(desc="Facts here are assumed to be true")
            text: str = InputField()
            faithfulness: bool = OutputField(ex="True")
            evidence: dict[str, list[str]] = OutputField(
                desc="Supporting evidence for claims"
            )

        # Get the class docstring
        print(CheckCitationFaithfulness.get_instructions())
        # Output:
        # "Verify that the text is based on the provided context."

        # Get the signature in string format
        print(CheckCitationFaithfulness.get_str_signature())
        # Output:
        # "context: str, text: str -> faithfulness: bool, evidence: dict[str, list[str]]"

        # Get input descriptions
        print(CheckCitationFaithfulness.get_input_descriptions())
        # Output:
        #[
        #   ('context', 'str', 'Facts here are assumed to be true', None),
        #   ('text', 'str', '', None)
        #]

        # Get output descriptions
        print(CheckCitationFaithfulness.get_output_descriptions())
        # Output:
        #[
        #   ('faithfulness', 'bool', '', "True"),
        #   ('evidence', 'dict[str, list[str]]', 'Supporting evidence for claims', None)
        #]
        ```
    """

    @classmethod
    def _dtype_to_str(cls, dtype_obj: Any) -> str:
        """Converts a type object to a readable string representation.

        Args:
            dtype_obj:
                The type object to convert.

        Returns:
            A string representation of the dtype.
        """
        origin = get_origin(dtype_obj)
        if origin is not None:
            args = get_args(dtype_obj)
            if origin is Union:
                # Checks if it is an Optional (Union with None)
                if len(args) == 2 and type(None) in args:
                    # Get the type that is not None
                    non_none_type = next(arg for arg in args if arg is not type(None))
                    return f"Optional[{cls._type_to_str(non_none_type)}]"
                else:
                    return " | ".join(cls._type_to_str(arg) for arg in args)
            else:
                arg_strs = [cls._type_to_str(arg) for arg in args]
                return f"{origin.__name__}[{', '.join(arg_strs)}]"
        elif hasattr(dtype_obj, "__name__"):
            return dtype_obj.__name__
        else:
            return str(dtype_obj)

    @classmethod
    def _get_inputs(cls) -> Dict[str, str]:
        """Retrieves the input fields with their names and types.

        Returns:
            A dictionary mapping input field names to their types.
        """
        type_hints = get_type_hints(cls)
        return {key: cls._dtype_to_str(type_hints[key]) for key in cls._inputs}

    @classmethod
    def _get_outputs(cls) -> Dict[str, str]:
        """Retrieves the output fields with their names and types.

        Returns:
            A dictionary mapping output field names to their types.
        """
        type_hints = get_type_hints(cls)
        return {key: cls._dtype_to_str(type_hints[key]) for key in cls._outputs}

    @classmethod
    def get_str_signature(cls) -> str:
        """Returns the signature of the parameters in string format.

        Returns:
            A string representation of the input and output fields.
        """
        inputs = [f"{key}: {dtype}" for key, dtype in cls._get_inputs().items()]
        outputs = [f"{key}: {dtype}" for key, dtype in cls._get_outputs().items()]
        return ", ".join(inputs) + " -> " + ", ".join(outputs)

    # TODO: tem bugs no parser quando usa optional

    @classmethod
    def get_input_descriptions(cls) -> List[FieldDescription]:
        """Returns a list of objects containing the input field name,
        dtype, and description.
        """
        inputs = cls._get_inputs()
        return [
            FieldDescription(key, dtype, cls._inputs[key].desc, cls._inputs[key].ex)
            for key, dtype in inputs.items()
        ]

    @classmethod
    def get_output_descriptions(cls) -> List[FieldDescription]:
        """Returns a list of objects containing the output field name,
        dtype, and description.
        """
        outputs = cls._get_outputs()
        return [
            FieldDescription(key, dtype, cls._outputs[key].desc, cls._outputs[key].ex)
            for key, dtype in outputs.items()
        ]

    @classmethod
    def get_instructions(cls) -> Optional[str]:
        """Returns the class docstring.

        Returns:
            The docstring of the class, or `None` if no docstring is present.
        """
        return cls.__doc__.strip() if cls.__doc__ else None

    @classmethod
    def get_input_examples(cls) -> Dict[str, Optional[str]]:
        """Returns a mapping of input field names to their examples.

        Returns:
            A dictionary where keys are input field names and values are
            their corresponding examples ('ex'). If an example is not
            provided for a field, its value will be None.
        """
        return {key: field.ex for key, field in cls._inputs.items()}

    @classmethod
    def get_output_examples(cls) -> Dict[str, Optional[str]]:
        """Returns a mapping of output field names to their examples.

        Returns:
            A dictionary where keys are output field names and values are
            their corresponding examples ('ex'). If an example is not
            provided for a field, its value will be None.
        """
        return {key: field.ex for key, field in cls._outputs.items()}


class SignatureFactory:

    @classmethod
    def _parse_example_str(cls, example_str: str, target_type: Type) -> Any: # noqa: C901
        """Attempts to parse an example string into the target Python type.
        Uses ast.literal_eval for safety and to handle Python literals.
        """
        origin_type = get_origin(target_type)

        # Trata 'None' literal -> None Python
        if example_str.strip().lower() == "none":
            # Checks if the target type allows None (Optional)
            is_optional = origin_type is Union and type(None) in get_args(target_type)
            if target_type is type(None) or is_optional:
                return None
            else:
                raise ValueError(
                    f"Received string `None` but target type `{target_type}` "
                    " is not None or Optional."
                )

        # Analyze based on destination type
        if target_type is str:
            return example_str
        elif target_type is bool:
            low_ex = example_str.strip().lower()
            if low_ex in ("true", "yes", "1"):
                return True
            elif low_ex in ("false", "no", "0"):
                return False
            else:
                raise ValueError(f"Could not parse `{example_str}` as boolean.")
        elif target_type is int:
            return int(example_str)
        elif target_type is float:
            return float(example_str)
        elif origin_type in (list, dict, tuple, set, List, Dict, Tuple, Set):
            try:
                parsed_value = ast.literal_eval(example_str)
                expected_type = (
                    list
                    if origin_type in (list, List)
                    else dict
                    if origin_type in (dict, Dict)
                    else tuple
                    if origin_type in (tuple, Tuple)
                    else set
                    if origin_type in (set, Set)
                    else None
                )

                if expected_type and not isinstance(parsed_value, expected_type):
                    raise TypeError(
                        f"Parsed value `{parsed_value}` is not of "
                        "expected type {expected_type} for {target_type}"
                    )

                return parsed_value
            except (ValueError, SyntaxError, TypeError, MemoryError) as e:
                raise ValueError(
                    f"Failed to parse `{example_str}` as {target_type} "
                    f"using ast.literal_eval: {e}"
                ) from e
        else:
            try:
                # It might be useful if the type is, for example, Optional[int]
                # and the example is "123"
                return ast.literal_eval(example_str)
            except (ValueError, SyntaxError, TypeError, MemoryError) as e:
                raise ValueError(
                    f"Unsupported type `{target_type}` for automatic parsing "
                    f"of example string `{example_str}`"
                ) from e

    @classmethod
    def get_examples_from_signature(
        cls, signature_cls: Type[Signature],
    ) -> Optional[SignatureExamples]:
        """Processes examples of a Signature class, returning a dict for inputs
        and a JSON or Typed string for outputs, only if all examples are present.
        """
        input_descs = signature_cls.get_input_descriptions()
        output_descs = signature_cls.get_output_descriptions()

        # Check if ALL fields have an example (not None)
        all_inputs_have_examples = all(desc.ex is not None for desc in input_descs)
        all_outputs_have_examples = all(desc.ex is not None for desc in output_descs)

        if not (all_inputs_have_examples and all_outputs_have_examples):
            return None

        # 1. Create dictionary of input examples (name -> example string)
        input_examples = {desc.name: desc.ex for desc in input_descs}

        # 2. Create the dictionary of output examples (name -> *parsed* example)
        output_examples = {}
        type_hints = get_type_hints(signature_cls)  # Get the actual types

        try:
            for desc in output_descs:
                target_type = type_hints.get(desc.name)
                if target_type is None:
                    raise ValueError(
                        f"Type hint not found for output field `{desc.name}` in "
                        f"{signature_cls.__name__}"
                    )
                # Parse the example string to the correct type
                parsed_value = cls._parse_example_str(desc.ex, target_type)
                output_examples[desc.name] = parsed_value
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Error parsing output examples for {signature_cls.__name__}: {e}"
            ) from e

        return SignatureExamples(inputs=input_examples, outputs=output_examples)

    @classmethod
    def get_expected_output_from_signature(
        cls,
        inputs_desc: List[FieldDescription],
        outputs_desc: List[FieldDescription],
        typed_parser_cls: Optional[Type[BaseTypedParser]] = None,
        fused_output_struct: Optional[Type[Struct]] = None
    ) -> str:
        expected_output = "Your task inputs are:\n\n"
        for i, input_desc in enumerate(inputs_desc, 1):
            part = f"{i}. `{input_desc.name}` ({input_desc.dtype})"
            if input_desc.desc:
                part += f": {input_desc.desc}"
            expected_output += part + "\n"

        expected_output += "\nYour final answer should have:\n\n"
        if typed_parser_cls is not None:
            json_schema = msgspec.json.schema(fused_output_struct)
            schema = typed_parser_cls.schema_from_json_schema(json_schema)
            expected_output += schema + "\n"
        else:
            # Expose ONLY the outputs for JSON-based. If fused with another Struct
            # (e.g ReAct) it will be passed as 'response_format' to the model client.
            # This removes duplication.
            for i, output_desc in enumerate(outputs_desc, 1):
                part = f"{i}. `{output_desc.name}` ({output_desc.dtype})"
                if output_desc.desc:
                    part += f": {output_desc.desc}"
                expected_output += part + "\n"
            expected_output += "\nWrite an encoded JSON."
        expected_output += "\nBe consise in choosing your answers."
        return expected_output

    @classmethod
    def get_task_template_from_signature(
        cls, inputs_desc: List[FieldDescription],
    ) -> str:
        task_template = ""
        for input_desc in inputs_desc:
            part = apply_xml_tags(input_desc.name, f"{{{{ {input_desc.name} }}}}")
            task_template += part + "\n"
        return task_template.strip()
