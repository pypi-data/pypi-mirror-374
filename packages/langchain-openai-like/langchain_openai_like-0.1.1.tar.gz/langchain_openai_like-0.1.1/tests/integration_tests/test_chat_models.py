import json
from typing import Annotated, Optional, TypedDict, cast
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessageChunk,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import tool
from langchain_tests.integration_tests.chat_models import (
    magic_function,
    magic_function_no_args,
    _validate_tool_call_message,
    _validate_tool_call_message_no_args,
)
from pydantic import BaseModel, Field
from langchain_openai_like import init_openai_like_chat_model
from dotenv import load_dotenv

load_dotenv()

model = init_openai_like_chat_model(model="qwen3-30b-a3b-instruct-2507")
# model = init_openai_like_chat_model("dashscope/qwen3-32b")
# model = init_openai_like_chat_model("qwen-flash", provider="dashscope")
# model = init_openai_like_chat_model("deepseek-chat")
# model = init_openai_like_chat_model("deepseek/deepseek-chat")
# model = init_openai_like_chat_model("moonshot/kimi-k2-0711-preview")
# model = init_openai_like_chat_model("glm-4.5")
# model = init_openai_like_chat_model("Qwen/Qwen3-4B", provider="vllm")
# model = init_openai_like_chat_model("ollama/qwen2.5:7b")
# model = init_openai_like_chat_model("qwen/qwen3-235b-a22b:free", provider="openrouter")
# model = init_openai_like_chat_model(
#     "Qwen/Qwen3-235B-A22B-Instruct-2507", provider="siliconflow"
# )


def test_invoke() -> None:
    result = model.invoke("Hello")
    assert result is not None
    assert isinstance(result, AIMessage)
    assert isinstance(result.text(), str)
    assert len(result.content) > 0


async def test_ainvoke() -> None:
    result = await model.ainvoke("Hello")
    assert result is not None
    assert isinstance(result, AIMessage)
    assert isinstance(result.text(), str)
    assert len(result.content) > 0


def test_stream() -> None:
    num_tokens = 0
    for token in model.stream("Hello"):
        assert token is not None
        assert isinstance(token, AIMessageChunk)
        num_tokens += len(token.content)
    assert num_tokens > 0


async def test_astream() -> None:
    num_tokens = 0
    async for token in model.astream("Hello"):
        assert token is not None
        assert isinstance(token, AIMessageChunk)
        num_tokens += len(token.content)
    assert num_tokens > 0


def test_batch() -> None:
    batch_results = model.batch(["Hello", "Hey"])
    assert batch_results is not None
    assert isinstance(batch_results, list)
    assert len(batch_results) == 2
    for result in batch_results:
        assert result is not None
        assert isinstance(result, AIMessage)
        assert isinstance(result.text(), str)
        assert len(result.content) > 0


async def test_abatch() -> None:
    batch_results = await model.abatch(["Hello", "Hey"])
    assert batch_results is not None
    assert isinstance(batch_results, list)
    assert len(batch_results) == 2
    for result in batch_results:
        assert result is not None
        assert isinstance(result, AIMessage)
        assert isinstance(result.text(), str)
        assert len(result.content) > 0


def test_conversation() -> None:
    messages = [
        HumanMessage("hello"),
        AIMessage("hello"),
        HumanMessage("how are you"),
    ]
    result = model.invoke(messages)
    assert result is not None
    assert isinstance(result, AIMessage)
    assert isinstance(result.text(), str)
    assert len(result.content) > 0


def test_double_messages_conversation() -> None:
    messages = [
        SystemMessage("hello"),
        SystemMessage("hello"),
        HumanMessage("hello"),
        HumanMessage("hello"),
        AIMessage("hello"),
        AIMessage("hello"),
        HumanMessage("how are you"),
    ]
    result = model.invoke(messages)
    assert result is not None
    assert isinstance(result, AIMessage)
    assert isinstance(result.text(), str)
    assert len(result.content) > 0


def test_usage_metadata() -> None:
    result = model.invoke("Hello")
    assert result is not None
    assert isinstance(result, AIMessage)
    assert result.usage_metadata is not None
    assert isinstance(result.usage_metadata["input_tokens"], int)
    assert isinstance(result.usage_metadata["output_tokens"], int)
    assert isinstance(result.usage_metadata["total_tokens"], int)

    # Check model_name is in response_metadata
    # Needed for langchain_core.callbacks.usage
    model_name = result.response_metadata.get("model_name")
    assert isinstance(model_name, str)
    assert model_name


def test_usage_metadata_streaming() -> None:
    full: Optional[AIMessageChunk] = None
    for chunk in model.stream("Write me 2 haikus. Only include the haikus."):
        assert isinstance(chunk, AIMessageChunk)
        if full and full.usage_metadata and full.usage_metadata["input_tokens"]:
            assert (
                not chunk.usage_metadata or not chunk.usage_metadata["input_tokens"]
            ), "Only one chunk should set input_tokens, the rest should be 0 or None"
        full = chunk if full is None else cast(AIMessageChunk, full + chunk)

    assert isinstance(full, AIMessageChunk)
    assert full.usage_metadata is not None
    assert isinstance(full.usage_metadata["input_tokens"], int)
    assert isinstance(full.usage_metadata["output_tokens"], int)
    assert isinstance(full.usage_metadata["total_tokens"], int)

    # Check model_name is in response_metadata
    # Needed for langchain_core.callbacks.usage
    model_name = full.response_metadata.get("model_name")
    assert isinstance(model_name, str)
    assert model_name


def test_stop_sequence() -> None:
    result = model.invoke("hi", stop=["you"])
    assert isinstance(result, AIMessage)


def test_tool_calling() -> None:
    model_with_tools = model.bind_tools([magic_function])

    # Test invoke
    query = "What is the value of magic_function(3)? Use the tool."
    result = model_with_tools.invoke(query)
    _validate_tool_call_message(result)

    # Test stream
    full: Optional[BaseMessageChunk] = None
    for chunk in model_with_tools.stream(query):
        full = chunk if full is None else full + chunk  # type: ignore
    assert isinstance(full, AIMessage)
    _validate_tool_call_message(full)


async def test_tool_calling_async() -> None:
    model_with_tools = model.bind_tools([magic_function])

    # Test ainvoke
    query = "What is the value of magic_function(3)? Use the tool."
    result = await model_with_tools.ainvoke(query)
    _validate_tool_call_message(result)

    # Test astream
    full: Optional[BaseMessageChunk] = None
    async for chunk in model_with_tools.astream(query):
        full = chunk if full is None else full + chunk  # type: ignore
    assert isinstance(full, AIMessage)
    _validate_tool_call_message(full)


def test_tool_calling_with_no_arguments() -> None:
    model_with_tools = model.bind_tools([magic_function_no_args])
    query = "What is the value of magic_function_no_args()? Use the tool."
    result = model_with_tools.invoke(query)
    _validate_tool_call_message_no_args(result)

    full: Optional[BaseMessageChunk] = None
    for chunk in model_with_tools.stream(query):
        full = chunk if full is None else full + chunk  # type: ignore
    assert isinstance(full, AIMessage)
    _validate_tool_call_message_no_args(full)


def test_structured_output_optional_param() -> None:
    # Pydantic
    class Joke(BaseModel):
        """Joke to tell user."""

        setup: str = Field(description="question to set up a joke")
        punchline: Optional[str] = Field(
            default=None, description="answer to resolve the joke"
        )

    chat = model.with_structured_output(Joke)
    setup_result = chat.invoke("Give me the setup to a joke about cats, no punchline.")
    assert isinstance(setup_result, Joke)

    joke_result = chat.invoke("Give me a joke about cats, include the punchline.")
    assert isinstance(joke_result, Joke)

    # TypedDict
    class JokeDict(TypedDict):
        """Joke to tell user."""

        setup: Annotated[str, ..., "question to set up a joke"]
        punchline: Annotated[Optional[str], None, "answer to resolve the joke"]

    chat = model.with_structured_output(JokeDict)
    result = chat.invoke("Tell me a joke about cats.")
    assert isinstance(result, dict)


def test_tool_message_histories_string_content() -> None:
    @tool
    def my_adder_tool(a: int, b: int) -> int:
        """Add two numbers together."""
        return a + b

    model_with_tools = model.bind_tools([my_adder_tool])
    function_name = "my_adder_tool"
    function_args = {"a": "1", "b": "2"}

    messages_string_content = [
        HumanMessage("What is 1 + 2"),
        # string content (e.g. OpenAI)
        AIMessage(
            "",
            tool_calls=[
                {
                    "name": function_name,
                    "args": function_args,
                    "id": "abc123",
                    "type": "tool_call",
                },
            ],
        ),
        ToolMessage(
            json.dumps({"result": 3}),
            name=function_name,
            tool_call_id="abc123",
        ),
    ]
    result_string_content = model_with_tools.invoke(messages_string_content)
    assert isinstance(result_string_content, AIMessage)


def test_tool_message_histories_list_content() -> None:
    @tool
    def my_adder_tool(a: int, b: int) -> int:
        """add two numbers together"""
        return a + b

    model_with_tools = model.bind_tools([my_adder_tool])
    function_name = "my_adder_tool"
    function_args = {"a": 1, "b": 2}

    messages_list_content = [
        HumanMessage("What is 1 + 2"),
        # List content (e.g., Anthropic)
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": function_name,
                    "args": function_args,
                    "id": "abc123",
                    "type": "tool_call",
                },
            ],
        ),
        ToolMessage(
            json.dumps({"result": 3}),
            name=function_name,
            tool_call_id="abc123",
        ),
    ]
    result_list_content = model_with_tools.invoke(messages_list_content)
    assert isinstance(result_list_content, AIMessage)


def test_tool_message_error_status() -> None:
    @tool
    def my_adder_tool(a: int, b: int) -> int:
        """Add two numbers together."""
        return a + b

    model_with_tools = model.bind_tools([my_adder_tool])
    messages = [
        HumanMessage("What is 1 + 2"),
        AIMessage(
            "",
            tool_calls=[
                {
                    "name": "my_adder_tool",
                    "args": {"a": 1},
                    "id": "abc123",
                    "type": "tool_call",
                },
            ],
        ),
        ToolMessage(
            "Error: Missing required argument 'b'.",
            name="my_adder_tool",
            tool_call_id="abc123",
            status="error",
        ),
    ]
    result = model_with_tools.invoke(messages)
    assert isinstance(result, AIMessage)


def test_message_with_name() -> None:
    result = model.invoke([HumanMessage("hello", name="example_user")])
    assert result is not None
    assert isinstance(result, AIMessage)
    assert isinstance(result.text(), str)
    assert len(result.content) > 0


def test_agent_loop() -> None:
    @tool
    def get_weather(location: str) -> str:
        """Call to surf the web."""
        return "It's sunny."

    llm_with_tools = model.bind_tools([get_weather])
    input_message = HumanMessage("What is the weather in San Francisco, CA?")
    tool_call_message = llm_with_tools.invoke([input_message])
    assert isinstance(tool_call_message, AIMessage)
    tool_calls = tool_call_message.tool_calls
    assert len(tool_calls) == 1
    tool_call = tool_calls[0]
    tool_message = get_weather.invoke(tool_call)
    assert isinstance(tool_message, ToolMessage)
    response = llm_with_tools.invoke(
        [
            input_message,
            tool_call_message,
            tool_message,
        ]
    )
    assert isinstance(response, AIMessage)
