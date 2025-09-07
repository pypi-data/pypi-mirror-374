"""Chat flow construction - conversation between two intelligent entities."""

from clearflow import Node, flow
from examples.chat.nodes import ChatState, HumanNode, LlmNode


def create_chat_flow() -> Node[ChatState]:
    """Create a conversation flow between two intelligent entities.

    This flow models conversation as interaction between two complete
    intelligent entities, each with their own I/O capabilities:

    - HumanNode: Human intelligent entity with console I/O
    - LlmNode: AI intelligent entity with OpenAI API I/O

    The flow alternates between the two entities until the human
    chooses to quit, creating a natural conversational pattern.

    Returns:
        Flow configured for intelligent entity conversation.
    """
    human = HumanNode(name="human")
    llm = LlmNode(name="llm")

    # Conversation between two intelligent entities
    return (
        flow("IntelligentConversation", human)
        .route(human, "responded", llm)
        .route(llm, "responded", human)
        .end(human, "quit")  # Single termination when human decides to quit
    )
