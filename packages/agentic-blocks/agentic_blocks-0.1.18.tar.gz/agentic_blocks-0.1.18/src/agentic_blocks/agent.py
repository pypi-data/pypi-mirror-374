from pocketflow import Node, Flow
from agentic_blocks.utils.tools_utils import (
    create_tool_registry,
    execute_pending_tool_calls,
)
from agentic_blocks import call_llm, Messages


class Agent:
    def __init__(self, system_prompt: str, tools: list):
        self.system_prompt = system_prompt
        self.tools = tools
        self.tool_registry = create_tool_registry(tools)

        # Create nodes
        self.llm_node = self._create_llm_node()
        self.tool_node = self._create_tool_node()
        self.answer_node = self._create_answer_node()

        # Set up flow
        self.llm_node - "tool_node" >> self.tool_node
        self.tool_node - "llm_node" >> self.llm_node
        self.llm_node - "answer_node" >> self.answer_node

        self.flow = Flow(self.llm_node)

    def _create_llm_node(self):
        class LLMNode(Node):
            def __init__(self, system_prompt, tools):
                super().__init__()
                self.system_prompt = system_prompt
                self.tools = tools

            def prep(self, shared):
                return shared["messages"]

            def exec(self, messages) -> Messages:
                response = call_llm(messages=messages, tools=self.tools)
                messages.add_response_message(response)
                return messages

            def post(self, shared, prep_res, messages):
                if messages.has_pending_tool_calls():
                    return "tool_node"
                else:
                    return "answer_node"

        return LLMNode(self.system_prompt, self.tools)

    def _create_tool_node(self):
        class ToolNode(Node):
            def __init__(self, tool_registry):
                super().__init__()
                self.tool_registry = tool_registry

            def prep(self, shared):
                return shared["messages"]

            def exec(self, messages) -> Messages:
                tool_responses = execute_pending_tool_calls(
                    messages, self.tool_registry
                )
                messages.add_tool_responses(tool_responses)
                return messages

            def post(self, shared, prep_res, messages):
                return "llm_node"

        return ToolNode(self.tool_registry)

    def _create_answer_node(self):
        class AnswerNode(Node):
            def prep(self, shared):
                messages = shared["messages"]
                shared["answer"] = messages.get_messages()[-1]["content"]
                return messages

        return AnswerNode()

    def invoke(self, user_prompt: str) -> str:
        messages = Messages(user_prompt=user_prompt)
        if self.system_prompt:
            messages.add_system_message(self.system_prompt)

        shared = {"messages": messages}
        self.flow.run(shared)

        return shared["answer"]
