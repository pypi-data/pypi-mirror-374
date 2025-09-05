from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from jinja2 import Template
from msgspec import Struct
from typing_extensions import Generic, TypeVar

from msgflux.generation.control_flow import ToolFlowControl

T = TypeVar("T", default=str)


REACT_SYSTEM_MESSAGE = """
You are an Agent. In each episode, you will be given the task as input. And you can see your past trajectory so far.

Your goal is to use one or more of the supplied tools to collect any necessary information for producing the final_response.

To do this, you will generate a `Thought` containing your reasoning and plan.
Identify and define necessary `actions` by creating a list of `ToolCall` objects.
You MUST use the available tools when needed to achieve the objective.
Include the function `name`, `arguments`, and `justification` for each call.
Await the results for the tool calls.
Analyze the results and repeat the thought-action cycle if necessary.
Once the objective is met using the tools, provide the `final_answer`.

Do NOT provide the `final_answer` before completing the required tool calls.
Optional fields may be omitted.
"""

REACT_TOOLS_TEMPLATE = """
You are a function calling AI model. You may call one or more functions
to assist with the user query. Don't make assumptions about what values
to plug into functions. Here are the available tools:


{%- for tool in tools %}
    {{- '<tool>' + tool['function']['name'] + '\n' }}
    {%- for argument in tool['function']['parameters']['properties'] %}
        {{- argument + ': ' + tool['function']['parameters']
                    ['properties'][argument]['description'] + '\n' }}
    {%- endfor %}
    {{- '\n</tool>' }}
{%- endif %}

For each function call return a encoded json object with function name
and arguments within <tool_call></tool_call> XML tags as follows:
"""


class ToolCall(Struct, kw_only=True):
    #id: Optional[UUID] = uuid4()
    justification: Optional[str] = None    
    name: str
    arguments: Optional[Dict[str, Any]] = {}
    result: Optional[str] = None


class Thought(Struct, kw_only=True):
    plan: Optional[str] = None
    reasoning: str


class ReActStep(Struct):
    thought: Thought
    actions: List[ToolCall] = []


class ReAct(Struct, ToolFlowControl, Generic[T]):
    current_step: Optional[ReActStep] = None
    final_answer: Optional[T] = None


def get_react_tools_prompt_format(tool_schemas):
    template = Template(REACT_TOOLS_TEMPLATE)
    react_tools = template.render(tools=tool_schemas)
    return react_tools


ReAct.system_message = REACT_SYSTEM_MESSAGE
ReAct.tools_template = REACT_TOOLS_TEMPLATE
