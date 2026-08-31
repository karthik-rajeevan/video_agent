from core.summarizer import get_llm, split_transcript
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def _extract_mapped(transcript: str, system_prompt: str) -> str:
    """Run map-reduce over the transcript with a single extraction prompt."""
    llm = get_llm()

    map_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "{instruction} Extract from ONE portion of the meeting transcript only."),
            ("human", "{text}"),
        ]
    )
    map_chain = map_prompt | llm | StrOutputParser()

    chunks = split_transcript(transcript)

    partials = [map_chain.invoke({"instruction": system_prompt, "text": chunk}) for chunk in chunks]

    combined = "\n\n".join(partials)

    reduce_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert meeting analyst. Below are extractions from different portions "
                "of the same meeting transcript. Deduplicate and merge them into one clean, complete {label}.",
            ),
            ("human", "{text}"),
        ]
    )
    reduce_chain = reduce_prompt | llm | StrOutputParser()

    return reduce_chain.invoke({"label": system_prompt, "text": combined}).strip()


def extract_action_items(transcript: str) -> str:
    system_prompt = (
        "Extract all action items from the meeting. For each item list who is the owner "
        "and the deadline (if mentioned). Use bullet points."
    )
    return _extract_mapped(transcript, system_prompt)


def extract_key_decisions(transcript: str) -> str:
    system_prompt = (
        "Extract all key decisions made during the meeting in bullet points."
    )
    return _extract_mapped(transcript, system_prompt)


def extract_questions(transcript: str) -> str:
    system_prompt = (
        "Extract all open questions and follow-ups raised during the meeting in bullet points."
    )
    return _extract_mapped(transcript, system_prompt)