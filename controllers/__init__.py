"""
Módulo de controllers
"""

from controllers.chat_controller import chat_with_agent, chat_stream_generator, get_agent
from controllers.knowledge_controller import (
    add_url_to_knowledge,
    add_json_to_knowledge,
    add_pdf_to_knowledge,
    get_knowledge_status,
    clear_knowledge_base
)

__all__ = [
    "chat_with_agent",
    "chat_stream_generator",
    "get_agent",
    "add_url_to_knowledge",
    "add_json_to_knowledge",
    "add_pdf_to_knowledge",
    "get_knowledge_status",
    "clear_knowledge_base",
]
