
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules['pysqlite3']

import os
import gradio as gr
from dotenv import load_dotenv, find_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import JsonOutputParser
from langchain.pydantic_v1 import BaseModel, Field
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from langchain_core.documents import Document
from pprint import pprint

class Answer(BaseModel):
    context_id: int = Field(..., title='The retrieved context number(integer)')
    quote: str = Field(..., title='The relevant text(part of the context)')
    answer: str = Field(..., title='The answer to the question')

def numbering_context(context: list) -> str:
    s = ''
    for i, c in enumerate(context):
        s += f'[source {i+1}] {c}\n'
    return s

def remove_duplicates_by_id(documents: list) -> list:
    seen = set()
    return [d for d in documents if not (d.metadata['id'] in seen or seen.add(d.metadata['id']))]

def create_chain():
    _ = load_dotenv(find_dotenv())

    with open('./travel_guides_db.txt', 'r') as f:
        tg_data = f.read().split('\n\n')

    docs = []
    for i, data in enumerate(tg_data):
        name_and_type = data.split('###')[0].lstrip('## ').rstrip()
        typ, name = name_and_type.split(': ')
        doc = Document(
            page_content = data,
            metadata = {'id': i, 'type': typ, 'name': name}
        )
        docs.append(doc)

    llm = ChatOpenAI(
        model='gpt-4o-mini',
        temperature=0.5,
    )
    openai_embeddings = OpenAIEmbeddings(api_key = os.getenv('OPENAI_API_KEY'))
    vectorstore = Chroma.from_documents(docs, embedding=openai_embeddings)

    metadata_fields = [
        AttributeInfo(name='id', type='int', description='The unique identifier of the document'),
        AttributeInfo(name='type', type='str', description='The type of the document: one of ["Hotel", "Restaurant", "Attraction"]'),
    ]
    contents_description = ''''The documents about three cities in New York, Paris and Seoul. 
    We have three types of documents: Hotel, Restaurant, and Attraction.'''
    retriever = SelfQueryRetriever.from_llm(
        llm=llm,
        vectorstore=vectorstore,
        document_contents=contents_description,
        metadata_field_info=metadata_fields,
        search_type='similarity_score_threshold',
        search_kwargs={'k': 5, 'score_threshold': 0.65}
    )

    template = '''You are an assistant for question-answering tasks. 
    Use the following pieces of retrieved context to answer the question. 
    When you answer the question you must quote the context number and the relevant text.
    The output format should be a JSON object with the following structure:
    ```json
    {{
        "context_id": "The retrieved context number(integer)",
        "quote": "The relevant text(part of the context)",
        "answer": "The answer to the question"
    }}
    ```

    [Question]:
    {question}

    [Context]:
    {context}

    [Answer]:
    '''

    prompt = PromptTemplate(
        template=template, 
        input_variables=['question', 'context']
    )

    model_openai = ChatOpenAI(
        model='gpt-4o-mini',
        temperature=0.5,
        model_kwargs = {'response_format': {'type': 'json_object'}}
    )

    chain = (
        {'question': RunnablePassthrough(), 
        'context': retriever | RunnableLambda(remove_duplicates_by_id) | RunnableLambda(numbering_context)}
        | prompt
        | model_openai
        | JsonOutputParser(pydantic_object=Answer)
    )

    return chain, docs

def response(chain, question, docs):
    answer = chain.invoke(question)
    ans = Answer(**answer)
    doc = [d for d in docs if d.metadata['id'] == ans.context_id]
    return answer.answer

if __name__ == '__main__':
    
    chain, docs = create_chain()
    list_of_availables = [d.metadata['name'] for d in docs]

    gr.ChatInterface(
        fn=response,
        textbox=gr.Textbox(placeholder="Ask", container=False, scale=7),
        # 채팅창의 크기를 조절한다.
        chatbot=gr.Chatbot(height=1000),
        title="Travel Search Guide",
        description="Travel Search Guide",
        theme="soft",
        examples=[],
        retry_btn="다시보내기 ↩",
        undo_btn="이전챗 삭제 ❌",
        clear_btn="전챗 삭제 💫",
        additional_inputs=[
            gr.Textbox("", label="System Prompt를 입력해주세요", placeholder="I'm lovely chatbot.")
        ]
).launch()





















def user_greeting(name):
    return "안녕하세요! " + name + "님, 첫 번째 Gradio 애플리케이션에 오신 것을 환영합니다!😎"

app = gr.Interface(fn=user_greeting, inputs="text", outputs="text")
app.launch()