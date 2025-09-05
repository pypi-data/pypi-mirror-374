import copy
import re
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Union,
    get_origin,
)

from msgflux.logger import logger
from msgflux.utils.inspect import get_mime_type


class ChatBlockMeta(type):
    def __call__(
        cls,
        role: str,
        content: str,
        media: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        role = role.lower()
        role_map = {
            "user": cls.user,
            "assist": cls.assist,
            "system": cls.system
        }
        if role not in role_map:
            raise ValueError(
                f"Invalid role `{role}`. Use {', '.join(role_map)}")
        if role == "user":
            return role_map[role](content, media)
        return role_map[role](content)


class ChatBlock(metaclass=ChatBlockMeta):    
    @classmethod
    def user(
        cls, 
        content: Union[str, List[Dict[str, Any]]],
        media: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        if media is None:
            return {"role": "user", "content": content}
        content_list = []
        if content:
            content_list.append({"type": "text", "text": content})
        if isinstance(media, list):
            content_list.extend(media)
        else:
            content_list.append(media)
        return {"role": "user", "content": content_list}
    
    @classmethod
    def assist(cls, content: str) -> Dict[str, str]:
        return {"role": "assistant", "content": content}
    
    @classmethod
    def system(cls, content: str) -> Dict[str, str]:
        return {"role": "system", "content": content}
    
    @staticmethod
    def tool_call(id: str, name: str, arguments: str) -> Dict[str, str]:
        return {
            "id": id,            
            "type": "function",
            "function": {"name": name, "arguments": arguments}
        }
    
    @classmethod
    def assist_tool_calls(cls, tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {"role": "assistant", "tool_calls": tool_calls}

    @classmethod
    def tool(cls, tool_call_id: str, content: str) -> Dict[str, Any]:
        return {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": content
        }

    @staticmethod
    def text(text: str) ->  Dict[str, str]:
        return {"type": "text", "text": text}

    @staticmethod
    def image(
        url: Union[str, List[str]]
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        if isinstance(url, list):
            return [{
                "type": "image_url",
                "image_url": {"url": u}
            } for u in url]
        return {
            "type": "image_url",
            "image_url": {"url": url}
        }

    @staticmethod
    def video(
        url: Union[str, List[str]]
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        if isinstance(url, list):
            return [{
                "type": "video_url",
                "video_url": {"url": u}
            } for u in url]
        return {
            "type": "video_url",
            "video_url": {"url": url}
        }

    @staticmethod
    def audio(data: str, format: str) -> Dict[str, str]:
        return {
            "type": "input_audio",
            "input_audio": {"data": data, "format": format}
        }
    
    @staticmethod
    def file(filename: str, file_data: str) -> Dict[str, str]:
        return {
            "type": "file",
            "file": {"filename": filename, "file_data": file_data}
        }


class ChatML:
    """Manage messages in ChatML format."""

    def __init__(self, messages: Optional[List[Dict[str, Any]]] = None):
        self.history = messages if messages is not None else []

    def add_user_message(
        self, 
        content: Union[str, Dict[str, Any]],
        media: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None
    ):
        """Adds a message with role `user`."""
        if isinstance(content, dict):
            self._add_message(content)
        self._add_message(ChatBlock.user(content, media))

    def add_assist_message(self, content: Union[str, Dict[str, Any]]):
        """Adds a message with role `assistant`."""
        if isinstance(content, dict):
            self._add_message(content)
        self._add_message(ChatBlock.assist(content))

    #def add_tool_message(self, content: Union[str, Dict[str, Any]]):
    #    """Adds a message with role `tool`."""
    #    self._add_message("tool", content) TODO

    def _add_message(self, message: Dict[str, Any]):
        """Internal method to add message to history."""
        self.history.append(message)

    def extend_history(self, messages):
        """Add a list of messages to the history."""
        return self.history.extend(messages)

    def get_messages(self):
        return self.history

    def clear(self):
        self.history = []


def response_format_from_json_schema(
    original_schema: Dict[str, Any],
) -> Dict[str, Any]:
    """Convert a Msgspec.Struct in Json Schema ChatCompletion-like."""

    def resolve_ref(ref: str, defs: Dict) -> Dict:
        """Resolves a reference `$ref` using the dictionary `$defs`."""
        ref_key = ref.split("/")[-1]
        return defs.get(ref_key, {})

    root_ref = original_schema.get("$ref", "")
    defs = original_schema.get("$defs", {})

    root_schema = resolve_ref(root_ref, defs)

    def deep_resolve_and_enforce_properties(schema: Dict) -> Dict:
        if "$ref" in schema:
            schema = resolve_ref(schema["$ref"], defs)

        # Enforce additionalProperties: false for all object types
        if schema.get("type") == "object":
            schema["additionalProperties"] = False

        if "properties" in schema:
            schema["properties"] = {
                k: deep_resolve_and_enforce_properties(v)
                for k, v in schema["properties"].items()
            }

        if "items" in schema:
            schema["items"] = deep_resolve_and_enforce_properties(schema["items"])

        return schema

    resolved_schema = deep_resolve_and_enforce_properties(root_schema)

    adapted_schema = {
        "type": "json_schema",
        "json_schema": {
            "name": root_schema.get("title", "response").lower(),
            "schema": {
                "type": resolved_schema.get("type", "object"),
                "properties": resolved_schema["properties"],
                "required": resolved_schema.get("required", []),
                "additionalProperties": False,
            },
            "strict": False,
        },
    }

    return adapted_schema


# TODO tirar e deixar como um tutorial
def chatml_to_steps_format(
    model_state: List[Dict[str, Any]], response: Union[str, Dict[str, Any]]
) -> Dict[str, Any]:
    steps = []
    pending_tool_calls = {}

    for message in model_state:
        if message["role"] == "user" and "content" in message:
            steps.append({"task": message["content"]})

        elif message["role"] == "assistant" and "content" in message:
            steps.append({"assistant": message["content"]})

        elif message.get("tool_calls"):
            # Iterates over all function calls in the `tool_calls` list
            for tool_call in message["tool_calls"]:
                fn_call_entry = {
                    "id": tool_call["id"],
                    "name": tool_call["function"]["name"],
                    "arguments": tool_call["function"]["arguments"],
                    "results": None,  # To be updated when the answer is found
                }
                # Add each function call separately
                steps.append({"tool_call": fn_call_entry})
                pending_tool_calls[tool_call["id"]] = fn_call_entry

        elif message["role"] == "tool" and message.get("tool_call_id"):
            # Check if there is a corresponding function call pending
            tool_call_id = message["tool_call_id"]
            if tool_call_id in pending_tool_calls:
                # Update the result of the corresponding function call
                pending_tool_calls[tool_call_id]["result"] = message.get("content", "")

    if response:
        steps.append({"assistant": response})

    return steps


def clean_docstring(docstring: str) -> str:
    """Cleans the docstring by removing the Args section.

    Args:
        docstring: Complete docstring to clean

    Returns:
        Clean docstring without Args section
    """
    if not docstring:
        return ""

    # Remove the Args section and any text after it
    cleaned = re.sub(r"\s*Args:.*", "", docstring, flags=re.DOTALL).strip()

    return cleaned


def parse_docstring_args(docstring: str) -> Dict[str, str]:
    """Extracts parameter descriptions from the Args section of the docstring.

    Args:
        docstring: Complete docstring of the function/class

    Returns:
        Dictionary with parameter descriptions
    """
    if not docstring:
        return {}

    # Find the Args section
    args_match = re.search(
        r"Args:\s*(.*?)(?:\n\n|\n[A-Za-z]+:|\Z)", docstring, re.DOTALL
    )
    if not args_match:
        return {}

    # Extract parameter descriptions
    args_text = args_match.group(1).strip()
    param_descriptions = {}

    # Process line by line to avoid capturing descriptions of other parameters
    lines = args_text.split("\n")
    current_param = None
    current_desc = []

    for raw_line in lines:
        line = raw_line.strip()
        # Find a new parameter
        param_match = re.match(r"(\w+)\s*\((.*?)\):\s*(.+)", line)

        if param_match:
            # Save description of previous parameter if exists
            if current_param:
                param_descriptions[current_param] = " ".join(current_desc).strip()

            # Start new parameter
            current_param = param_match.group(1)
            current_desc = [param_match.group(3)]
        elif current_param and line:
            # Continue description of current parameter
            current_desc.append(line)

    # Save last description
    if current_param:
        param_descriptions[current_param] = " ".join(current_desc).strip()

    return param_descriptions


def generate_json_schema(cls: type) -> Dict[str, Any]:
    """Generates a JSON schema for a class based on its characteristics.

    Args:
        cls: The class to generate the schema for

    Returns:
        JSON schema for the class
    """
    name = cls.get_module_name()
    description = cls.get_module_description()
    clean_description = clean_docstring(description)
    param_descriptions = parse_docstring_args(description)
    annotations = cls.get_module_annotations()

    properties = {}
    required = []

    for param, type_hint in annotations.items():
        if param == "return":
            continue

        prop_schema = {"type": "string"}  # Default as string

        # Check if enum is defined
        if hasattr(type_hint, "__args__") and type_hint.__origin__ is Literal:
            prop_schema["enum"] = list(type_hint.__args__)

        # Add parameter description if available
        if param in param_descriptions:
            prop_schema["description"] = param_descriptions[param]

        # Mark as required
        if get_origin(type_hint) is not Union:
            required.append(param)

        properties[param] = prop_schema

    json_schema = {
        "name": name,
        "description": clean_description or f"Function for {name}",
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        },
        "strict": True,
    }

    return json_schema


def generate_tool_json_schema(cls: type) -> Dict[str, Any]:
    tool = generate_json_schema(cls)
    tool_json_schema = {"type": "function", "function": tool}
    return tool_json_schema


def adapt_messages_for_vllm_audio(
    messages: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Adapts a list of messages from ChatML format, converting audio parts of type
    'input_audio' (OpenAI style) to type 'audio_url' with Data URI (vLLM style).

    Args:
        messages: The original list of messages.

    Returns:
        A new list of messages with the adapted audio parts.
        The original list is not modified.
    """
    adapted_messages = copy.deepcopy(messages)

    for message in adapted_messages:
        content = message.get("content")

        # Checks if the content is a list (indicating multimodality)
        if isinstance(content, list):
            processed_content = []
            for i, part in enumerate(content):
                # Check if the part is of type 'input_audio'
                if isinstance(part, dict) and part.get("type") == "input_audio":
                    input_audio_data = part.get("input_audio")

                    # Check if internal data exists
                    if isinstance(input_audio_data, dict):
                        base64_data = input_audio_data.get("data")
                        audio_format = input_audio_data.get("format")

                        # If you have the base64 data and format, convert
                        if (
                            base64_data
                            and isinstance(base64_data, str)
                            and audio_format
                        ):
                            mime_type = get_mime_type(audio_format)
                            data_uri = f"data:{mime_type};base64,{base64_data}"

                            # Create the new structure of the audio part
                            vllm_audio_part = {
                                "type": "audio_url",
                                "audio_url": {"url": data_uri},
                            }
                            processed_content.append(vllm_audio_part)
                        else:
                            logger.warning(
                                "Skipping malformed `input_audio` part "
                                f"at index {i}: {part}"
                            )
                            processed_content.append(part)
                    else:
                        # Keep the original part if `input_audio` is not a dict
                        logger.warnning(
                            "Skipping malformed `input_audio` part "
                            f"(not a dict) at index {i}: {part}"
                        )
                        processed_content.append(part)

                else:
                    # Keep other parts (text, image, etc.) as is
                    processed_content.append(part)

            # Update the message content with the processed list
            message["content"] = processed_content
        # If the content is not a list (e.g. plain text), do nothing
    return adapted_messages
