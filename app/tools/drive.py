from langchain_core.tools import tool


@tool
def search_drive(query: str) -> str:
    """Search for stock and price information in Google Drive."""
    # TODO: implement real Google Drive integration
    return f"[Drive stub] No results for: {query}"


def get_drive_tools() -> list:
    return [search_drive]
