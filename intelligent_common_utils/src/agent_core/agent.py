"""Agent: config loading, LLM, tools, memory, judge, and interaction loop."""

import logging
from typing import Any, List, Optional, Union

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from agent_core.judge import judge_output
from agent_core.llm import get_llm
from agent_core.memory import load_memory, save_memory
from agent_core.utils.config import AppConfig, load_config

logger = logging.getLogger(__name__)


class Agent:
    """
    Agent brain: loads config, initializes LLM and memory, runs query loop.
    Uses judge for self-critique and optional retry.
    """

    def __init__(
        self,
        config: Optional[AppConfig] = None,
        config_path: Optional[str] = None,
        memory_path: str = "memory.json",
    ) -> None:
        if config is None:
            config = load_config(config_path)
        self.config = config
        self.memory_path = memory_path
        self.llm: BaseChatModel = get_llm(
            model_id=config.model_id,
            temperature=0.0,
        )

    def _messages_from_memory(self) -> List[Union[HumanMessage, AIMessage]]:
        """Load prior conversation as LangChain messages."""
        raw = load_memory(self.memory_path)
        out: list[HumanMessage | AIMessage] = []
        for m in raw:
            role = m.get("role", "")
            content = m.get("content", "")
            if role == "human" or role == "user":
                out.append(HumanMessage(content=content))
            elif role == "ai" or role == "assistant":
                out.append(AIMessage(content=content))
        return out

    async def ainvoke(self, query: str, use_judge: bool = False) -> str:
        """
        Run one user query and return the model response. Optionally judge and retry.
        """
        system = (
            "You are a helpful assistant. Answer concisely and accurately. "
            "When generating test cases, follow the given schema."
        )
        history = self._messages_from_memory()
        messages = [SystemMessage(content=system)] + history + [HumanMessage(content=query)]
        try:
            response = await self.llm.ainvoke(messages)
            content = response.content if hasattr(response, "content") else str(response)
            if use_judge:
                result = judge_output(self.llm, query, content)
                if not result.accept:
                    logger.info("Judge rejected; reason: %s", result.reason)
                    # One retry with judge feedback
                    messages2 = messages + [
                        AIMessage(content=content),
                        HumanMessage(content=f"Improve: {result.reason}"),
                    ]
                    response2 = await self.llm.ainvoke(messages2)
                    content = (
                        response2.content
                        if hasattr(response2, "content")
                        else str(response2)
                    )
            # Append to memory
            new_raw = load_memory(self.memory_path)
            new_raw.append({"role": "human", "content": query})
            new_raw.append({"role": "ai", "content": content})
            save_memory(self.memory_path, new_raw)
            return content
        except Exception as e:
            logger.exception("Agent ainvoke failed: %s", e)
            raise
