import time
import uuid


def uuid_to_bytes32(uuid_str: str) -> str:
    """Converts UUID string to bytes32 hex format.

    Args:
        uuid_str (str): UUID string to convert.

    Returns:
        str: Bytes32 hex string prefixed with '0x'.
    """
    uuid_obj = uuid.UUID(uuid_str)

    # remove hyphens and convert to hex
    uuid_hex = uuid_obj.hex

    # pad the hex to make it 32 bytes
    padded_hex = uuid_hex.rjust(64, "0")

    return "0x" + padded_hex


def is_uuid(value: str) -> bool:
    """Checks if a string is a valid UUID.

    Args:
        value (str): String to check.

    Returns:
        bool: True if string is a valid UUID, False otherwise.
    """
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def client_order_id_to_bytes32(client_order_id: str) -> str:
    """Converts client_order_id to appropriate bytes32 format.

    Args:
        client_order_id (str): Client order ID to convert.

    Returns:
        str: Converted client order ID in bytes32 hex format.

    Raises:
        ValueError: If string is longer than 32 characters and not a UUID, or if input is None/empty.
    """
    if client_order_id is None:
        raise ValueError("Client order ID cannot be None")
    
    if not client_order_id:
        raise ValueError("Client order ID cannot be empty")

    if is_uuid(client_order_id):
        return uuid_to_bytes32(client_order_id)
    else:
        # For non-UUID strings, check 32 character limit
        if len(client_order_id) > 32:
            raise ValueError(
                f"Client order ID cannot be longer than 32 characters, got {len(client_order_id)}"
            )

        # Convert string to bytes32 hex format
        client_order_bytes = client_order_id.encode("utf-8")
        padded_bytes = client_order_bytes.ljust(32, b"\0")
        return "0x" + padded_bytes.hex()


def generate_nonce() -> str:
    """Generates a timestamp-based nonce.

    Returns:
        str: Current timestamp in nanoseconds as string.
    """
    return str(time.time_ns())
