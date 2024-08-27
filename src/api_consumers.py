from abc import ABC

import requests
import typer
from rich import status

from src.config import BASE_URL, PORT
from src.custom_types import Endpoint, MoveDirection
from src.utils import colorize_number, exit_with_error, tabulate_str


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
        name: str,
        priority: int,
        savings_amount: int = 0,
        savings_target: int | None = None,
    ):
        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=Endpoint.CREATE_MONEYBOX,
        )
        self.name = name
        self.priority = priority
        self.savings_amount = savings_amount
        self.savings_target = savings_target

        self.url = f"{BASE_URL}:{PORT}{self.endpoint}"
        self.post_data = {
            "name": self.name,
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

        # if self.new_priority >= 0:
        self.patch_data["priority"] = self.new_priority

        if self.new_name:
            self.patch_data["name"] = self.new_name

        if self.new_savings_amount >= 0:
            self.patch_data["savings_amount"] = self.new_savings_amount

        if self.new_savings_target is None or self.new_savings_target >= 0:
            self.patch_data["savings_target"] = self.new_savings_target

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
            content["transaction_logs"] = content["transaction_logs"][-self.n :]

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


class GetPriorityListApiConsumer(ApiConsumerFactory):
    """`GET: /api/prioritylist` consumer class."""

    def __init__(self):
        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=Endpoint.GET_PRIORITYLIST,
        )

        self.url = f"{BASE_URL}:{PORT}{self.endpoint}"
        self.response = requests.get(self.url)

    def __str__(self) -> str:
        """Parse the response of `GET: /api/prioritylist`
        to a console represented string and returns it.

        :return: response json as a console str representation.
        :rtype: str
        """

        if not self.response:
            exit_with_error(content=self.response.json())

        content = self.response.json()["priority_list"]

        headers = content[0].keys()
        rows = [list(priority.values()) for priority in content]

        return tabulate_str(headers=headers, rows=rows)


class UpdatePriorityListApiConsumer(ApiConsumerFactory):
    """`PATCH: /api/prioritylist` consumer class."""

    def __init__(
        self,
        moneybox_id: int,
        move_direction: MoveDirection,
        move_steps: int,
    ):
        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=Endpoint.UPDATE_PRIORITYLIST,
        )

        self.moneybox_id = moneybox_id
        self.move_direction = move_direction
        self.move_steps = move_steps

        self.url = f"{BASE_URL}:{PORT}{self.endpoint}"
        self.response = None
        patch_data = self._build_patch_data()
        self.response = requests.patch(self.url, json=patch_data)

    def _build_patch_data(self) -> dict[str, list[dict[str, int | str]]]:
        """Build the new priority list dict data.

        :return: priority list dict data.
        :rtype: :class:`dict[str, list[dict[str, int|str]]]`
        """

        consumer = GetPriorityListApiConsumer()
        priority_list = consumer.response.json()["priority_list"]

        # move logic
        priority_sorted_list = sorted(
            priority_list,
            key=lambda item: item["priority"],
        )

        old_index = None
        for i, item in enumerate(priority_sorted_list):
            if item["moneybox_id"] == self.moneybox_id:
                old_index = i
                break
        else:
            raise typer.BadParameter(
                f"Moneybox {self.moneybox_id} does not exist or can't be moved "
                "(e.g. the Overflow Moneybox with priority 0)."
            )

        if self.move_direction == MoveDirection.UP:
            new_index = max(0, old_index - self.move_steps)
        else:
            new_index = min(len(priority_sorted_list) - 1, old_index + self.move_steps)

        priority_sorted_list.insert(new_index, priority_sorted_list.pop(old_index))

        for i, priority in enumerate(priority_sorted_list):
            priority["priority"] = i + 1

        return {
            "priority_list": [
                {
                    "moneybox_id": priority["moneybox_id"],
                    "priority": priority["priority"],
                }
                for priority in priority_sorted_list
            ]
        }

    def __str__(self) -> str:
        """Parse the response of `PATCH: /api/prioritylist`
        to a console represented string and returns it.

        :return: response json as a console str representation.
        :rtype: str
        """

        if not self.response:
            exit_with_error(content=self.response.json())

        content = self.response.json()["priority_list"]

        headers = content[0].keys()
        rows = [list(priority.values()) for priority in content]

        return tabulate_str(headers=headers, rows=rows)


class GetAppSettingsApiConsumer(ApiConsumerFactory):
    """`GET: /api/settings` consumer class."""

    def __init__(self):
        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=Endpoint.GET_APPSETTINGS,
        )

        self.url = f"{BASE_URL}:{PORT}{self.endpoint}"
        self.response = requests.get(self.url)

    def __str__(self) -> str:
        """Parse the response of `GET: /api/settings`
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


class PatchAppSettingsApiConsumer(ApiConsumerFactory):
    """`PATCH:  /api/settings` consumer class."""

    def __init__(
        self,
        send_reports_via_email: int,
        user_email_address: str,
        is_automated_saving_active: int,
        savings_amount: int,
        overflow_moneybox_automated_savings_mode: str,
    ):
        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=Endpoint.UPDATE_APPSETTINGS,
        )
        self.send_reports_via_email = send_reports_via_email
        self.user_email_address = user_email_address
        self.is_automated_saving_active = is_automated_saving_active
        self.savings_amount = savings_amount
        self.overflow_moneybox_automated_savings_mode = (
            overflow_moneybox_automated_savings_mode
        )

        self.url = f"{BASE_URL}:{PORT}{self.endpoint}"

        self.patch_data = {}

        if self.send_reports_via_email >= 0:
            self.patch_data["savings_amount"] = self.savings_amount

        if self.user_email_address:
            self.patch_data["user_email_address"] = self.user_email_address

        if self.is_automated_saving_active >= 0:
            self.patch_data["is_automated_saving_active"] = (
                self.is_automated_saving_active
            )

        if self.savings_amount >= 0:
            self.patch_data["savings_amount"] = self.savings_amount

        if self.overflow_moneybox_automated_savings_mode:
            self.patch_data["overflow_moneybox_automated_savings_mode"] = (
                self.overflow_moneybox_automated_savings_mode
            )

        self.response = requests.patch(self.url, json=self.patch_data)

    def __str__(self) -> str:
        """Parse the response of `PATCH:  /api/settings`
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


class PatchSendTestEmailApiConsumer(ApiConsumerFactory):
    """`PATCH:  /api/email/send-testemail` consumer class."""

    def __init__(
        self,
    ):
        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=Endpoint.SEND_TESTEMAIL,
        )

        self.url = f"{BASE_URL}:{PORT}{self.endpoint}"
        self.response = requests.patch(self.url)

    def __str__(self) -> str:
        """Parse the response of `PATCH:  /api/email/send-testemail`
        to a console represented string and returns it.

        :return: response json as a console str representation.
        :rtype: str
        """

        content = (
            "Ok. Test email sent"
            if self.response.status_code == 204
            else "Failed sending test email."
        )
        return content
