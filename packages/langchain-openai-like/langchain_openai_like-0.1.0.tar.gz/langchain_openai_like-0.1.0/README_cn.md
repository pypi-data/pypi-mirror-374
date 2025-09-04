# 🦜️🔗 LangChain-OpenAI-Like

<p align="center">
    <em>一个库接入所有兼容OpenAI风格的模型</em>
</p>

## 动机

随着 OpenAI 风格 API 成为行业标准，越来越多的大模型厂商提供了兼容的接口。然而，当前的接入方式存在分散且低效的问题。例如接入 DeepSeek 需要安装 `langchain-deepseek`，而接入 Qwen3 则需要依赖 `langchain-qwq`，这种为每个模型单独引入依赖包的方式不仅增加了开发复杂度，也降低了灵活性。更极端的例子是 Kimi-K2 等模型，甚至没有对应的封装包，只能通过 `langchain-openai` 接入。

为了解决上述问题，我们开发了本工具库（命名参考了 `llama-index-llms-openai-like`），提供统一的接口函数 `init_openai_like_chat_model`，只需一个依赖包即可接入所有兼容 OpenAI 风格的模型 API。通过本工具，你可以轻松接入各类模型，例如：

```python
from langchain_openai_like import init_openai_like_chat_model

deepseek_model = init_openai_like_chat_model(model="deepseek-chat")
deepseek_model.invoke("你好")
```

> ⚠️ 注意：使用前请确保已正确设置 API Key，如 `DEEPSEEK_API_KEY`。

> ⚠️ 注意：如果接入 OpenAI 的 GPT 模型，推荐直接使用 `langchain-openai`

## 安装

### Pip 安装

```bash
pip install langchain-openai-like
```

### UV 安装

```bash
uv add langchain-openai-like
```

## 使用方法

`init_openai_like_chat_model` 函数中，model 参数为必填项，provider 参数可选。

### 支持的模型提供商

目前支持以下模型提供商：

- DeepSeek (深度求索)
- DashScope (阿里云百炼)
- Groq (Groq)
- HuggingFace (HuggingFace)
- MoonShot-AI (月之暗面)
- Ollama (Ollama)
- OpenRouter (OpenRouter)
- SiliconFlow (硅基流动)
- VLLM (VLLM)
- ZAI (智谱 AI)
- Custom (自定义)

如果你未指定 provider，工具将根据传入的 model 自动判断提供商：

| 模型关键字    | 提供商    | 需要设置的 API_KEY |
| ------------- | --------- | ------------------ |
| deepseek      | DeepSeek  | DEEPSEEK_API_KEY   |
| qwen          | DashScope | DASHSCOPE_API_KEY  |
| moonshot/kimi | MoonShot  | MOONSHOT_API_KEY   |
| glm           | Zhipu-AI  | ZHIPU_API_KEY      |

**注意：**

> (1) 对于 VLLM 和 Ollama，请必须传入 provider="vllm" 或 "ollama"
> 例如

```python
from langchain_openai_like import init_openai_like_chat_model

model = init_openai_like_chat_model(
    model="qwen3:8b",
    provider="ollama"
)
print(model.invoke("你好"))
```

> (2) 对于其他模型参数（如 `temperature`、`top_k` 等），可通过 model_kwargs 传入。
> 例如

```python
from langchain_openai_like import init_openai_like_chat_model

model = init_openai_like_chat_model(
    model="qwen3-32b",
    model_kwargs={
      "thinking_budget": 10
    }
)
print(model.invoke("你好"))
```

### 视觉模型

同时也支持接入 OpenAI 兼容的视觉多模态模型，例如

```python
from langchain_core.messages import HumanMessage
from langchain_openai_like import init_openai_like_chat_model

model = init_openai_like_chat_model(
    model="qwen2.5-vl-32b-instruct"
)
print(model.invoke(
    input=[
        HumanMessage(
            content=[
                {
                    "type": "image_url",
                    "image_url": "https://example.com/image.png"
                },
                {
                    "type": "text",
                    "text": "图中有什么？"
                }
            ]
        )
    ]
))
```

### 嵌入模型

本库也提供了兼容 OpenAI 风格的向量化模型接入，目前支持的提供商有 `custom`、`dashscope`、`ollama`、`vllm`、`siliconflow`、`zai`。

示例代码如下：

```python
from langchain_openai_like import init_openai_like_embeddings

emb = init_openai_like_embeddings("bge-m3:latest", provider="ollama")
print(emb.embed_query("hello world"))
```

### 自定义提供商

对于尚未支持的模型提供商，你可以使用 `provider="custom"` 参数，并手动设置 `base_url` 和 `api_key`。

例如，使用硅基流动平台的 Kimi-K2 模型：

```python
import os

os.environ["OPENAI_LIKE_API_KEY"] = "your_api_key"
os.environ["OPENAI_LIKE_API_BASE"] = "https://api.siliconflow.cn/v1"

from langchain_openai_like import init_openai_like_chat_model

model = init_openai_like_chat_model(
    model="moonshotai/Kimi-K2-Instruct",
    provider="custom",
)
print(model.invoke("你好"))
```

### 使用 ChatModel 类

你也可以使用 ChatModel 类像使用 ChatQwen、ChatDeepSeek 这样。只需要导入对应的类就行了。例如接入 Qwen 则需要

```python
from langchain_openai_like.chat_model.providers.dashscope import ChatDashScopeModel

model = ChatDashScopeModel(model="qwen3-30b-a3b-instruct")
print(model.invoke("你好"))
```

## 使用总结

### 何时使用本库 vs LangChain 官方函数

#### 使用 LangChain 官方的 `init_chat_model` 和 `init_embeddings` 当：

- 你主要使用 OpenAI、Anthropic、Google 等主流模型
- 你希望使用 LangChain 官方维护的稳定实现
- 你的模型已经在官方支持列表中

#### 使用本库的 `init_openai_like_chat_model` 和 `init_openai_like_embeddings` 当：

- 你需要在多个不同提供商的模型之间灵活切换
- 你使用的模型（例如 qwen、glm）不在 LangChain 官方支持列表中，但提供 OpenAI 兼容接口

### 本库的优势

本库的两个核心工具函数命名参考了 LangChain 中的 `init_chat_model` 和 `init_embeddings`，提供了类似的使用体验，但扩展了对更多模型的支持：

- **更广泛的模型支持**：支持 qwen、glm、moonshot 等官方库不支持的模型
- **统一的接口**：一个库即可接入多个提供商的模型
- **灵活切换**：可以轻松在不同模型之间进行切换测试

### 贡献指南

由于作者个人水平有限，还有很多兼容的模型未接入，或者支持的模型接入可能存在问题。如果你的模型提供商也提供了兼容 OpenAI API 风格的接口，欢迎通过 Pull Request (PR) 的方式贡献你的集成实现，帮助更多开发者轻松接入。
