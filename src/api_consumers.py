from abc import ABC
from enum import StrEnum

import requests

from src.config import BASE_URL, PORT
from src.utils import exit_with_error, tabulate_str, colorize_number


class Endpoint(StrEnum):
    """The endpoint types."""

    LIST_ALL_MONEYBOXES = "/api/moneyboxes"
    """GET Endpoint for list all moneyboxes."""

    LIST_SPECIFIC_MONEYBOX = "/api/moneybox"
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


class ApiConsumerFactory(ABC):
    """Base class for all API consumers."""

    def __init__(
        self,
        domain: str,
        port: int,
        endpoint: Endpoint,
    ):
        self.domain = domain
        self.port = port
        self.endpoint = endpoint

    def __str__(self):
        raise NotImplementedError


class GetMoneyboxApiConsumer(ApiConsumerFactory):
    """`GET: /api/moneybox/{moneybox_id}` consumer class."""

    def __init__(self, moneybox_id: int):
        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=Endpoint.LIST_SPECIFIC_MONEYBOX,
        )
        self.moneybox_id = moneybox_id

        self.url = f"{BASE_URL}:{PORT}{self.endpoint}/{self.moneybox_id}"
        self.response = requests.get(self.url)

    def __str__(self) -> str:
        """Parse the response of `GET: /api/moneybox/{moneybox_id}`
        to a console represented string and returns it.

        :return: response json as a console str representation.
        :rtype: str
        """

        if not self.response:
            exit_with_error(content=self.response.json())

        content = self.response.json()

        headers = content.keys()
        rows = [content.values()]

        return tabulate_str(headers=headers, rows=rows)


class GetMoneyboxesApiConsumer(ApiConsumerFactory):
    """`GET: /api/moneyboxes` consumer class."""

    def __init__(self):
        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=Endpoint.LIST_ALL_MONEYBOXES,
        )

        self.url = f"{BASE_URL}:{PORT}{self.endpoint}"
        self.response = requests.get(self.url)

    def __str__(self) -> str:
        """Parse the response of `GET: /api/moneyboxes`
        to a console represented string and returns it.

        :return: response json as a console str representation.
        :rtype: str
        """

        if not self.response:
            exit_with_error(content=self.response.json())

        if self.response.status_code == 204:
            return "No data"

        content = self.response.json()

        total_balance = sum(moneybox["balance"] for moneybox in content["moneyboxes"])
        total_balance_str = f"{total_balance / 100:,.2f} €"

        headers = content["moneyboxes"][0].keys()
        rows = [data.values() for data in content["moneyboxes"]]

        return_contents = [
            tabulate_str(headers=headers, rows=rows, showindex=True),
            f"\nTotal Balance: {total_balance_str:<15}",
        ]

        return "".join(return_contents)


class PostMoneyboxBalanceAddApiConsumer(ApiConsumerFactory):
    """`POST:  /api/moneybox/{moneybox_id}/balance/add` consumer class."""

    def __init__(
        self,
        moneybox_id: int,
        amount: int,
        description: str,
    ):
        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=Endpoint.ADD_AMOUNT_TO_MONEYBOX,
        )
        self.moneybox_id = moneybox_id
        self.amount = amount
        self.description = description

        self.url = f"{BASE_URL}:{PORT}{self.endpoint.value.replace('{moneybox_id}', str(self.moneybox_id))}"
        self.post_data = {"amount": amount, "description": description}

        self.response = requests.post(self.url, json=self.post_data)

    def __str__(self) -> str:
        """Parse the response of `POST:  /api/moneybox/{moneybox_id}/balance/add`
        to a console represented string and returns it.

        :return: response json as a console str representation.
        :rtype: str
        """

        if not self.response:
            exit_with_error(content=self.response.json())

        content = self.response.json()

        headers = content.keys()
        rows = [content.values()]

        return tabulate_str(headers=headers, rows=rows)


class PostMoneyboxBalanceSubApiConsumer(ApiConsumerFactory):
    """`POST:  /api/moneybox/{moneybox_id}/balance/sub` consumer class."""

    def __init__(
        self,
        moneybox_id: int,
        amount: int,
        description: str,
    ):
        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=Endpoint.SUB_AMOUNT_TO_MONEYBOX,
        )
        self.moneybox_id = moneybox_id
        self.amount = amount
        self.description = description

        self.url = f"{BASE_URL}:{PORT}{self.endpoint.value.replace('{moneybox_id}', str(self.moneybox_id))}"
        self.post_data = {"amount": amount, "description": description}

        self.response = requests.post(self.url, json=self.post_data)

    def __str__(self) -> str:
        """Parse the response of `POST:  /api/moneybox/{moneybox_id}/balance/sub`
        to a console represented string and returns it.

        :return: response json as a console str representation.
        :rtype: str
        """

        if not self.response:
            exit_with_error(content=self.response.json())

        content = self.response.json()

        headers = content.keys()
        rows = [content.values()]

        return tabulate_str(headers=headers, rows=rows)


class PostMoneyboxBalanceTransferApiConsumer(ApiConsumerFactory):
    """`POST:  /api/moneybox/{moneybox_id}/balance/transfer` consumer class."""

    def __init__(
        self,
        from_moneybox_id: int,
        to_moneybox_id: int,
        amount: int,
        description: str,
    ):
        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=Endpoint.TRANSFER_AMOUNT,
        )
        self.from_moneybox_id = from_moneybox_id
        self.to_moneybox_id = to_moneybox_id
        self.amount = amount
        self.description = description

        self.url = f"{BASE_URL}:{PORT}{self.endpoint.value.replace('{moneybox_id}', str(self.from_moneybox_id))}"
        self.post_data = {
            "amount": amount,
            "to_moneybox_id": to_moneybox_id,
            "description": description,
        }

        self.response = requests.post(self.url, json=self.post_data)

    def __str__(self) -> str:
        """Parse the response of `POST:  /api/moneybox/{moneybox_id}/balance/sub`
        to a console represented string and returns it.

        :return: response json as a console str representation.
        :rtype: str
        """

        if not self.response:
            exit_with_error(content=self.response.json())

        return f"Transferred '{self.amount/100:.2f} €' from moneybox ({self.from_moneybox_id}) to moneybox ({self.to_moneybox_id})"


class PostMoneyboxApiConsumer(ApiConsumerFactory):
    """`POST:  /api/moneybox` consumer class."""

    def __init__(
        self,
        moneybox_name: str,
        priority: int,
        savings_amount: int = 0,
        savings_target: int | None = None,
    ):
        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=Endpoint.CREATE_MONEYBOX,
        )
        self.moneybox_name = moneybox_name
        self.priority = priority
        self.savings_amount = savings_amount
        self.savings_target = savings_target

        self.url = f"{BASE_URL}:{PORT}{self.endpoint}"
        self.post_data = {
            "name": self.moneybox_name,
            "priority": self.priority,
            "savings_amount": self.savings_amount,
            "savings_target": self.savings_target,
        }

        self.response = requests.post(self.url, json=self.post_data)

    def __str__(self) -> str:
        """Parse the response of `POST:  /api/moneybox`
        to a console represented string and returns it.

        :return: response json as a console str representation.
        :rtype: str
        """

        if not self.response:
            exit_with_error(content=self.response.json())

        content = self.response.json()

        headers = content.keys()
        rows = [content.values()]

        return tabulate_str(headers=headers, rows=rows)

class PatchMoneyboxApiConsumer(ApiConsumerFactory):
    """`PATCH:  /api/moneybox/{moneybox_id}` consumer class."""

    def __init__(
        self,
        moneybox_id: int,
        priority: int,
        name: str,
        savings_amount: int,
        savings_target: int | None,
    ):
        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=Endpoint.UPDATE_MONEYBOX,
        )
        self.moneybox_id = moneybox_id
        self.new_priority = priority
        self.new_name = name
        self.new_savings_amount = savings_amount
        self.new_savings_target = savings_target

        self.url = f"{BASE_URL}:{PORT}{self.endpoint.value.replace('{moneybox_id}', str(self.moneybox_id))}"

        self.patch_data = {}

        #if self.new_priority >= 0:
        self.patch_data["priority"] = self.new_priority

        if len(self.new_name) > 0:
            self.patch_data["name"] = self.new_name

        if self.new_savings_amount >= 0:
            self.patch_data["savings_amount"] = self.new_savings_amount

        if self.new_savings_target is None or self.new_savings_target >= 0:
            self.patch_data["savings_target"] = self.new_savings_target

        from pprint import pprint
        pprint(self.patch_data)
        self.response = requests.patch(self.url, json=self.patch_data)

    def __str__(self) -> str:
        """Parse the response of `PATCH:  /api/moneybox/{moneybox_id}`
        to a console represented string and returns it.

        :return: response json as a console str representation.
        :rtype: str
        """

        if not self.response:
            exit_with_error(content=self.response.json())

        content = self.response.json()

        headers = content.keys()
        rows = [content.values()]

        return tabulate_str(headers=headers, rows=rows)


class GetMoneyboxTransactionsApiConsumer(ApiConsumerFactory):
    """`GET: 	/api/moneybox/{moneybox_id}/transactions` consumer class."""

    def __init__(
        self,
        moneybox_id: int,
        n: int | None,
    ):
        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=Endpoint.SHOW_MONEYBOX_LOGS,
        )
        self.moneybox_id = moneybox_id
        self.n = n

        self.url = f"{BASE_URL}:{PORT}{self.endpoint.value.replace('{moneybox_id}', str(self.moneybox_id))}"

        self.response = requests.get(self.url)

    def __str__(self) -> str:
        """Parse the response of `GET: 	/api/moneybox/{moneybox_id}/transactions`
        to a console represented string and returns it.

        :return: response json as a console str representation.
        :rtype: str
        """

        if not self.response:
            exit_with_error(content=self.response.json())

        if self.response.status_code == 204:
            return "No data"

        content = self.response.json()

        # sort by created_at
        content["transaction_logs"].sort(key=lambda item: item["created_at"])

        # filter and get last n entries
        if self.n is not None:
            content["transaction_logs"] = content["transaction_logs"][-self.n:]

        content["transaction_logs"] = [
            {key: colorize_number(key, value) for key, value in data.items()}
            for data in content["transaction_logs"]
        ]

        headers = content["transaction_logs"][0].keys()
        rows = [data.values() for data in content["transaction_logs"]]

        return_contents = [
            tabulate_str(headers=headers, rows=rows, showindex=True),
        ]

        return "".join(return_contents)


class DeleteMoneyboxApiConsumer(ApiConsumerFactory):
    """`DELETE:  /api/moneybox/{moneybox_id}` consumer class."""

    def __init__(
        self,
        moneybox_id: int,
    ):
        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=Endpoint.DELETE_MONEYBOX,
        )
        self.moneybox_id = moneybox_id

        self.url = f"{BASE_URL}:{PORT}{self.endpoint.value.replace('{moneybox_id}', str(self.moneybox_id))}"
        self.response = requests.delete(self.url)

    def __str__(self) -> str:
        """Parse the response of `DELETE:  /api/moneybox/{moneybox_id}`
        to a console represented string and returns it.

        :return: response json as a console str representation.
        :rtype: str
        """

        if not self.response:
            exit_with_error(content=self.response.json())

        return f"Deleted moneybox ({self.moneybox_id})."
