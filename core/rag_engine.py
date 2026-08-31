from core.vector_store import build_vector_store, get_retriever
from core.summarizer import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda


def _format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)


def build_rag_chain(transcript: str):
    print("Building RAG chain...")

    vector_store = build_vector_store(transcript)
    retriever = get_retriever(vector_store, k=4)

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an assistant that answers questions strictly using the meeting transcript. "
                "If the answer is not in the provided context, say you don't know. "
                "Keep answers concise and cite the relevant part of the transcript where possible.\n\n"
                "Context:\n{context}",
            ),
            ("human", "{question}"),
        ]
    )

    chain = (
        RunnablePassthrough.assign(context=RunnableLambda(lambda x: _format_docs(retriever.invoke(x["question"]))))
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain


def ask_question(rag_chain, question: str) -> str:
    return rag_chain.invoke({"question": question}).strip()