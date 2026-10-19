from langchain_core.tools import tool
from tavily import TavilyClient
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from config import Chroma_Path, Tavily_Api_Key


# Initialize embeddings once instead of on every tool call.
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)


@tool
def web_search(query: str) -> str:
    """
    Search the web for current, recent, external,
    or changing information.
    """

    if not Tavily_Api_Key:
        return "Tavily API key is not configured."

    if not query.strip():
        return "Please provide a search query."

    try:
        client = TavilyClient(
            api_key=Tavily_Api_Key
        )

        response = client.search(
            query=query,
            max_results=5,
        )

        results = response.get("results", [])

        if not results:
            return "No web results found."

        output = []

        for result in results:
            output.append(
                f"Title: {result.get('title', 'No title')}\n"
                f"Content: {result.get('content', '')}\n"
                f"URL: {result.get('url', '')}"
            )

        return "\n\n".join(output)

    except Exception as error:
        return f"Web search failed: {error}"


@tool
def search_documents(query: str) -> str:
    """
    Search user-uploaded documents using ChromaDB.
    Use this tool when answers should come from
    the user's own documents.
    """

    if not query.strip():
        return "Please provide a search query."

    try:
        vector_store = Chroma(
            embedding_function=embeddings,
            persist_directory=Chroma_Path,
            collection_name="private_doc",
        )

        documents = vector_store.similarity_search(
            query,
            k=3,
        )

        if not documents:
            return "No relevant information found."

        results = []

        for document in documents:
            source = document.metadata.get(
                "source",
                "Unknown source",
            )

            results.append(
                f"Source: {source}\n"
                f"Content: {document.page_content}"
            )

        return "\n\n".join(results)

    except Exception as error:
        return f"Document search failed: {error}"