
import uuid
from typing import Optional

def company_seed_uuid() -> str:
    """
    Returns Future Edge Group's Seed UUID which was generated using:
    uuid.uuid5(uuid.NAMESPACE_DNS, "ftredge.com")
    """
    return "d0a97da8-66c8-5946-ab48-340ef927b0ff"


def generate_reproducible_uuid_for_namespace(namespace: uuid.UUID | str, seed_description: str, prefix:Optional[str]=None) -> str:
    """
    Generates a reproducible UUID based on the input namespace (UUID object or string) and seed_description.
    For reproducibility, ensure the same namespace and seed_description are used.
    """
    if isinstance(namespace, str):
        namespace = uuid.UUID(namespace)  # Convert string to uuid.UUID object
    if prefix:
        return f"{prefix}_{str(uuid.uuid5(namespace, seed_description))}"
    return str(uuid.uuid5(namespace, seed_description))
