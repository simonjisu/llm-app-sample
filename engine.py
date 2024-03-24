import os
import sys
import time
from dotenv import load_dotenv
from operator import itemgetter

from langchain import hub
from langchain.agents import AgentExecutor, create_json_chat_agent
from langchain_openai import ChatOpenAI
from tools import (
    get_ticker_info, 
    get_income_statement, 
    get_balance_sheet, 
    get_news,
    get_recent_price,
    create_web_retriever,
    formatting_output,
    get_google_search_results
)

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain.globals import set_verbose
from langchain_core.runnables import (
    RunnablePassthrough, RunnableParallel, RunnableLambda
)
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

set_verbose(True)
load_dotenv()


# ---------------------------------------- Financial QA ----------------------------------------
def create_agent():
    llm = ChatOpenAI(
        api_key = os.getenv("OPENAI_API_KEY"),
        model = "gpt-3.5-turbo-0125",
    )
    tools = [get_ticker_info, get_income_statement, get_balance_sheet, get_news, get_recent_price]
    prompt = hub.pull("hwchase17/react-chat-json")
    agent = create_json_chat_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    return agent_executor

def agent_response(prompt: str):
    agent_executor = create_agent()
    response = agent_executor.invoke({"input": prompt})
    return response

# ---------------------------------------- Travel Planner ----------------------------------------
class Templates:
    query_template = """You are a travel agent helping a customer's travel plan.
question: {question}

{context}

Using the search results and extract 3 distinct {query_type}. 
Output must be the list of each items.

{format_instructions}
"""

class ListOfItems(BaseModel):
    items: list[str] = Field(description="List of items")
    city: str = Field(description="City of the items")

def create_query_type_sub_chain(query_type: str, db_path: str, k:int=5):
    response_llm = ChatOpenAI(
        model = "gpt-3.5-turbo",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0
    )
    output_parser = JsonOutputParser(pydantic_object=ListOfItems)
    web_retriever = create_web_retriever(query_type, db_path=db_path)
    prompt = ChatPromptTemplate.from_template(Templates.query_template).partial(
        query_type=query_type,
        format_instructions=output_parser.get_format_instructions()
    )
    chain = (
        RunnableLambda(lambda x: f"Could you find five {query_type} in {x['city']} for travelers?")
        | {"context": web_retriever, "question": RunnablePassthrough()} 
        | prompt
        | response_llm
        | output_parser
        | RunnableLambda(formatting_output)  # list
    )
    return chain

def travel_response(prompt: str) -> dict[str, list[dict[str, str]]]:
    hotel_chain = create_query_type_sub_chain("hotels", "./chroma_hotel")
    restaurant_chain = create_query_type_sub_chain("restaurants", "./chroma_restaurant")

    map_chain = (
        {"city": RunnablePassthrough()}
        | RunnableParallel(
            hotel=hotel_chain,  # -> hotel
            resturant=restaurant_chain,
        )
    )
    response = map_chain.invoke(prompt)
    results = get_google_search_results(response)
    return results