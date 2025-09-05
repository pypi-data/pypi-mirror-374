# langchain-modelscope-integration

This package contains the LangChain integration with ModelScope

## Installation

```bash
pip install -U langchain-modelscope-integration
```

Head to [ModelScope](https://modelscope.cn/) to sign up to ModelScope and generate an [SDK token](https://modelscope.cn/my/myaccesstoken). Once you've done this set the `MODELSCOPE_SDK_TOKEN` environment variable:

```bash
export MODELSCOPE_SDK_TOKEN=<your_sdk_token>
```

## Chat Models

`ModelScopeChatEndpoint` class exposes chat models from ModelScope. See available models [here](https://www.modelscope.cn/docs/model-service/API-Inference/intro).

```python
from langchain_modelscope import ModelScopeChatEndpoint

llm = ModelScopeChatEndpoint(model="Qwen/Qwen2.5-Coder-32B-Instruct")
llm.invoke("Sing a ballad of LangChain.")
```

## Embeddings

`ModelScopeEmbeddings` class exposes embeddings from ModelScope.

```python
from langchain_modelscope import ModelScopeEmbeddings

embeddings = ModelScopeEmbeddings(model_id="damo/nlp_corom_sentence-embedding_english-base")
embeddings.embed_query("What is the meaning of life?")
```