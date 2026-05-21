from langchain_google_community.drive import GoogleDriveAPIWrapper
from langchain_google_community import GoogleDriveSearchTool


def get_drive_tools() -> list:
    """
    Returns LangChain Google Drive tools for the Stock & Catalog agent.
    Credentials are loaded from the path set in GOOGLE_CREDENTIALS_PATH env var.
    """
    api_wrapper = GoogleDriveAPIWrapper()
    drive_tool = GoogleDriveSearchTool(api_wrapper=api_wrapper)
    return [drive_tool]
