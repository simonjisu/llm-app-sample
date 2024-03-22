import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from tools import get_ticker_info, get_income_statement, get_balance_sheet, get_news

from operator import itemgetter
from typing import Union
from langchain.output_parsers import JsonOutputToolsParser
from langchain_core.runnables import (
    Runnable,
    RunnableLambda,
    RunnableMap,
    RunnablePassthrough,
)
load_dotenv()


def create_chain():

    llm = ChatOpenAI(
        api_key = os.getenv("OPENAI_API_KEY"),
        model = "gpt-3.5-turbo-0125",
    )
    all_tools = [get_ticker_info, get_income_statement, get_balance_sheet, get_news]
    tool_map = {tool.name: tool for tool in all_tools}

    def call_tool(tool_invocation: dict) -> Union[str, Runnable]:
        """Function for dynamically constructing the end of the chain based on the model-selected tool."""
        tool = tool_map[tool_invocation["type"]]
        return RunnablePassthrough.assign(output=itemgetter("args") | tool)
    call_tool_list = RunnableLambda(call_tool).map()

    llm_with_tools = llm.bind_tools(all_tools)
    chain = llm_with_tools | JsonOutputToolsParser() | call_tool_list
    return chain

def chat_response(prompt: str):
    llm = create_chain()
    response = llm.invoke(prompt)
    return response