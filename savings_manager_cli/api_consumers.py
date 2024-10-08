import asyncio
import http
from abc import ABC
from functools import partial
from typing import Any, Callable

import requests
import typer
from requests import Response

from savings_manager_cli.custom_types import Endpoint, MoveDirection
from savings_manager_cli.utils import colorize_number, exit_with_error, tabulate_str

BASE_URL = "http://localhost"
PORT = 8001


class ApiConsumerFactory(ABC):
    """Base class for all API consumers."""

    request_method_callbacks = {
        http.HTTPMethod.GET: requests.get,
        http.HTTPMethod.PATCH: requests.patch,
        http.HTTPMethod.POST: requests.post,
        http.HTTPMethod.DELETE: requests.delete,
    }

    def __init__(
        self,
        domain: str,
        port: int,
        endpoint: Endpoint,
        request_method: http.HTTPMethod,
        request_data: dict[str, Any] | Callable | None = None,
    ):
        self.domain = domain
        self.port = port
        self.endpoint = endpoint
        self.response = None

        if request_data is not None:
            if callable(request_data):
                self.request_data = request_data()
            elif isinstance(request_data, dict):
                self.request_data = request_data
            else:
                raise TypeError(
                    "Error in Request: request_data must be callable or dict."
                )

        request_callback = ApiConsumerFactory.request_method_callbacks[request_method]

        self.consumer_request = (
            partial(request_callback, url=self.url)
            if request_data is None
            else partial(request_callback, url=self.url, json=self.request_data)
        )

    @property
    def url(self):
        raise NotImplementedError()

    def __enter__(self):
        self.run()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    async def __aenter__(self):
        await self.async_run()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def run(self) -> Response:
        self.response = self.consumer_request()
        return self.response

    async def async_run(self) -> Response:
        loop = asyncio.get_event_loop()
        self.response = await loop.run_in_executor(
            None,
            self.consumer_request,
        )
        return self.response

    def __str__(self):
        raise NotImplementedError()


class GetMoneyboxApiConsumer(ApiConsumerFactory):
    """`GET: /api/moneybox/{moneybox_id}` consumer class."""

    def __init__(self, moneybox_id: int | None):
        self.moneybox_id = moneybox_id

        endpoint = (
            Endpoint.LIST_ALL_MONEYBOXES
            if moneybox_id is None
            else Endpoint.LIST_SPECIFIC_MONEYBOX
        )
        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=endpoint,
            request_method=http.HTTPMethod.GET,
        )

    @property
    def url(self) -> str:
        return f"{BASE_URL}:{PORT}{self.endpoint.replace('{moneybox_id}', str(self.moneybox_id))}"

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
            request_method=http.HTTPMethod.GET,
        )

    @property
    def url(self) -> str:
        return f"{BASE_URL}:{PORT}{self.endpoint}"

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
        self.moneybox_id = moneybox_id
        self.amount = amount
        self.description = description

        post_data = {"amount": amount, "description": description}

        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=Endpoint.ADD_AMOUNT_TO_MONEYBOX,
            request_method=http.HTTPMethod.POST,
            request_data=post_data,
        )

    @property
    def url(self) -> str:
        return f"{BASE_URL}:{PORT}{self.endpoint.replace('{moneybox_id}', str(self.moneybox_id))}"

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
        self.moneybox_id = moneybox_id
        self.amount = amount
        self.description = description

        post_data = {"amount": amount, "description": description}

        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=Endpoint.SUB_AMOUNT_TO_MONEYBOX,
            request_method=http.HTTPMethod.POST,
            request_data=post_data,
        )

    @property
    def url(self) -> str:
        return f"{BASE_URL}:{PORT}{self.endpoint.replace('{moneybox_id}', str(self.moneybox_id))}"

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
        self.from_moneybox_id = from_moneybox_id
        self.to_moneybox_id = to_moneybox_id
        self.amount = amount
        self.description = description

        post_data = {
            "amount": amount,
            "toMoneyboxId": to_moneybox_id,
            "description": description,
        }

        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=Endpoint.TRANSFER_AMOUNT,
            request_method=http.HTTPMethod.POST,
            request_data=post_data,
        )

    @property
    def url(self) -> str:
        return f"{BASE_URL}:{PORT}{self.endpoint.replace('{moneybox_id}', str(self.from_moneybox_id))}"

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
        savings_amount: int = 0,
        savings_target: int | None = None,
    ):
        self.name = name
        self.savings_amount = savings_amount
        self.savings_target = savings_target

        post_data = {
            "name": self.name,
            "savingsAmount": self.savings_amount,
            "savingsTarget": self.savings_target,
        }

        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=Endpoint.CREATE_MONEYBOX,
            request_method=http.HTTPMethod.POST,
            request_data=post_data,
        )

    @property
    def url(self) -> str:
        return f"{BASE_URL}:{PORT}{self.endpoint}"

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
        name: str,
        savings_amount: int,
        savings_target: int,
        clear_savings_target: bool,
    ):
        if clear_savings_target and savings_target >= 0:
            raise typer.BadParameter(
                "You can't set savings target and clear it at same time."
            )

        self.moneybox_id = moneybox_id
        self.new_name = name
        self.new_savings_amount = savings_amount
        self.new_savings_target = savings_target
        self.clear_savings_target = clear_savings_target

        patch_data = {}

        if self.new_name:
            patch_data["name"] = self.new_name

        if self.new_savings_amount >= 0:
            patch_data["savingsAmount"] = self.new_savings_amount

        if self.new_savings_target >= 0:
            patch_data["savingsTarget"] = self.new_savings_target

        if clear_savings_target:
            patch_data["savingsTarget"] = None

        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=Endpoint.UPDATE_MONEYBOX,
            request_method=http.HTTPMethod.PATCH,
            request_data=patch_data,
        )

    @property
    def url(self) -> str:
        return f"{BASE_URL}:{PORT}{self.endpoint.replace('{moneybox_id}', str(self.moneybox_id))}"

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
        self.moneybox_id = moneybox_id
        self.n = n

        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=Endpoint.SHOW_MONEYBOX_LOGS,
            request_method=http.HTTPMethod.GET,
        )

    @property
    def url(self) -> str:
        return f"{BASE_URL}:{PORT}{self.endpoint.replace('{moneybox_id}', str(self.moneybox_id))}"

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
        content["transactionLogs"].sort(key=lambda item: item["createdAt"])

        # filter and get last n entries
        if self.n is not None:
            content["transactionLogs"] = content["transactionLogs"][-self.n :]

        content["transactionLogs"] = [
            {key: colorize_number(key, value) for key, value in data.items()}
            for data in content["transactionLogs"]
        ]

        headers = content["transactionLogs"][0].keys()
        rows = [data.values() for data in content["transactionLogs"]]

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
        self.moneybox_id = moneybox_id

        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=Endpoint.DELETE_MONEYBOX,
            request_method=http.HTTPMethod.DELETE,
        )

    @property
    def url(self) -> str:
        return f"{BASE_URL}:{PORT}{self.endpoint.replace('{moneybox_id}', str(self.moneybox_id))}"

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
            request_method=http.HTTPMethod.GET,
        )

    @property
    def url(self) -> str:
        return f"{BASE_URL}:{PORT}{self.endpoint}"

    def __str__(self) -> str:
        """Parse the response of `GET: /api/prioritylist`
        to a console represented string and returns it.

        :return: response json as a console str representation.
        :rtype: str
        """

        if not self.response:
            exit_with_error(content=self.response.json())

        content = self.response.json()["prioritylist"]

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
        self.moneybox_id = moneybox_id
        self.move_direction = move_direction
        self.move_steps = move_steps

        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=Endpoint.UPDATE_PRIORITYLIST,
            request_method=http.HTTPMethod.PATCH,
            request_data=self._build_patch_data,
        )

    @property
    def url(self) -> str:
        return f"{BASE_URL}:{PORT}{self.endpoint.replace('{moneybox_id}', str(self.moneybox_id))}"

    def _build_patch_data(self) -> dict[str, list[dict[str, int | str]]]:
        """Build the new priority list dict data.

        :return: priority list dict data.
        :rtype: :class:`dict[str, list[dict[str, int|str]]]`
        """

        with GetPriorityListApiConsumer() as consumer:
            prioritylist = consumer.response.json()["prioritylist"]

        # move logic
        priority_sorted_list = sorted(
            prioritylist,
            key=lambda item: item["priority"],
        )

        old_index = None
        for i, item in enumerate(priority_sorted_list):
            if item["moneyboxId"] == self.moneybox_id:
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
            "prioritylist": [
                {
                    "moneyboxId": priority["moneyboxId"],
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

        content = self.response.json()["prioritylist"]

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
            request_method=http.HTTPMethod.GET,
        )

    @property
    def url(self) -> str:
        return f"{BASE_URL}:{PORT}{self.endpoint}"

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
        self.send_reports_via_email = send_reports_via_email
        self.user_email_address = user_email_address
        self.is_automated_saving_active = is_automated_saving_active
        self.savings_amount = savings_amount
        self.overflow_moneybox_automated_savings_mode = (
            overflow_moneybox_automated_savings_mode
        )

        patch_data = {}

        if self.send_reports_via_email >= 0:
            patch_data["sendReportsViaEmail"] = bool(self.send_reports_via_email)

        if self.user_email_address:
            patch_data["userEmailAddress"] = self.user_email_address

        if self.is_automated_saving_active >= 0:
            patch_data["isAutomatedSavingActive"] = bool(
                self.is_automated_saving_active
            )

        if self.savings_amount >= 0:
            patch_data["savingsAmount"] = self.savings_amount

        if self.overflow_moneybox_automated_savings_mode:
            patch_data["overflowMoneyboxAutomatedSavingsMode"] = (
                self.overflow_moneybox_automated_savings_mode
            )

        super().__init__(
            domain=BASE_URL,
            port=PORT,
            endpoint=Endpoint.UPDATE_APPSETTINGS,
            request_method=http.HTTPMethod.PATCH,
            request_data=patch_data,
        )

    @property
    def url(self) -> str:
        return f"{BASE_URL}:{PORT}{self.endpoint}"

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
            request_method=http.HTTPMethod.PATCH,
        )

    @property
    def url(self) -> str:
        return f"{BASE_URL}:{PORT}{self.endpoint}"

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
