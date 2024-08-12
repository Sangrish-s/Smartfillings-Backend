from openai import OpenAI
from dotenv import load_dotenv
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain_text_splitters import TokenTextSplitter
from langchain.schema.document import Document
from bs4 import BeautifulSoup  # type: ignore
from .select_prompt import select_prompt
import os


load_dotenv(".env")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

model = "gpt-3.5-turbo"


def ai_analysis_from_filing(html, prompt_type, form_type, option, min_sentences=3, max_sentences=20):
    prompt = select_prompt(prompt_type, form_type, option, min_sentences, max_sentences)
    return get_response_on_html(html, prompt)


def get_text_chunks_langchain(text):
    text_splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=0)
    return [Document(page_content=x) for x in text_splitter.split_text(text)]


# not using now
def get_response_from_gpt(message):
    completion = client.chat.completions.create(
        model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message},
        ],
    )
    return completion.choices[0].message.content


def get_response_on_html(html, prompt):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    docs = get_text_chunks_langchain(text)

    llm = ChatOpenAI(temperature=0, model_name=model, api_key=OPENAI_API_KEY)

    map_template = """
        The following is a set of documents
        {docs}
        Based on this list of docs, please summarize these docs and avoid the boiler plate info.
        Helpful Answer:
    """

    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = LLMChain(llm=llm, prompt=map_prompt)
    reduce_prompt = PromptTemplate.from_template(prompt)

    # Run chain
    reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)

    # Takes a list of documents, combines them into a single string, and passes this to an LLMChain
    combine_documents_chain = StuffDocumentsChain(
        llm_chain=reduce_chain, document_variable_name="docs"
    )

    # Combines and iteratively reduces the mapped documents
    reduce_documents_chain = ReduceDocumentsChain(
        combine_documents_chain=combine_documents_chain,
        collapse_documents_chain=combine_documents_chain,
        token_max=4000,
    )

    # Combining documents by mapping a chain over them, then combining results
    map_reduce_chain = MapReduceDocumentsChain(
        llm_chain=map_chain,
        reduce_documents_chain=reduce_documents_chain,
        document_variable_name="docs",
        return_intermediate_steps=False,
    )

    result = map_reduce_chain.invoke(docs)
    return result["output_text"]
