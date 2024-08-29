from enum import StrEnum


class MoveDirection(StrEnum):
    UP = "up"
    DOWN = "down"


class Endpoint(StrEnum):
    """The endpoint types."""

    LIST_ALL_MONEYBOXES = "/api/moneyboxes"
    """GET Endpoint for list all moneyboxes."""

    LIST_SPECIFIC_MONEYBOX = "/api/moneybox/{moneybox_id}"
    """GET Endpoint for list specific moneybox."""

    ADD_AMOUNT_TO_MONEYBOX = "/api/moneybox/{moneybox_id}/balance/add"
    """POST Endpoint to add amount to specific moneybox."""

    SUB_AMOUNT_TO_MONEYBOX = "/api/moneybox/{moneybox_id}/balance/sub"
    """POST Endpoint to sub amount from specific moneybox."""

    TRANSFER_AMOUNT = "/api/moneybox/{moneybox_id}/balance/transfer"
    """POST Endpoint to transfer amount between specific moneyboxes."""

    CREATE_MONEYBOX = "/api/moneybox"
    """POST Endpoint to create moneybox."""

    UPDATE_MONEYBOX = "/api/moneybox/{moneybox_id}"
    """PATCH Endpoint to update specific moneybox."""

    SHOW_MONEYBOX_LOGS = "/api/moneybox/{moneybox_id}/transactions"
    """GET Endpoint for show moneybox logs."""

    DELETE_MONEYBOX = "/api/moneybox/{moneybox_id}"
    """DELETE Endpoint to delete a specific moneybox."""

    GET_PRIORITYLIST = "/api/prioritylist"
    """GET Endpoint for get prioritylist."""

    UPDATE_PRIORITYLIST = "/api/prioritylist"
    """UPDATE Endpoint for update prioritylist."""

    GET_APPSETTINGS = "/api/settings"
    """GET Endpoint for get app settings."""

    UPDATE_APPSETTINGS = "/api/settings"
    """UPDATE Endpoint for get app settings."""

    SEND_TESTEMAIL = "/api/email/send-testemail"
    """Send Testemail Endpoint."""
