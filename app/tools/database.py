from langchain_core.tools import tool
from app.services.database import get_db


@tool
def register_order(
    customer_phone: str,
    product: str,
    quantity: int,
    size: str = None,
    total: float = None,
) -> str:
    """Registers a confirmed customer order in the database."""
    # TODO: implement with actual DB session
    return f"Order registered: {quantity}x {product} (size: {size}) for {customer_phone}"


@tool
def register_unmet_demand(
    customer_phone: str,
    product: str,
    quantity: int = 1,
    size: str = None,
) -> str:
    """Registers a product that was requested but is out of stock."""
    # TODO: implement with actual DB session
    return f"Unmet demand registered: {product} (size: {size}) for {customer_phone}"


def get_database_tools() -> list:
    return [register_order, register_unmet_demand]
