from typing import Annotated, Optional

import typer

from src.api_consumers import (DeleteMoneyboxApiConsumer,
                               GetAppSettingsApiConsumer,
                               GetMoneyboxApiConsumer,
                               GetMoneyboxesApiConsumer,
                               GetMoneyboxTransactionsApiConsumer,
                               GetPriorityListApiConsumer,
                               PatchAppSettingsApiConsumer,
                               PatchMoneyboxApiConsumer,
                               PatchSendTestEmailApiConsumer,
                               PostMoneyboxApiConsumer,
                               PostMoneyboxBalanceAddApiConsumer,
                               PostMoneyboxBalanceSubApiConsumer,
                               PostMoneyboxBalanceTransferApiConsumer,
                               UpdatePriorityListApiConsumer)
from src.custom_types import MoveDirection
from src.utils import int_or_none

app = typer.Typer()


@app.command("list")
def list_specific_or_all_moneyboxes(
    moneybox_id: Annotated[Optional[int], typer.Argument()] = None,
):
    if moneybox_id is None:
        consumer = GetMoneyboxesApiConsumer()
    else:
        consumer = GetMoneyboxApiConsumer(moneybox_id=moneybox_id)

    with consumer:
        print(consumer)


@app.command("add")
def add_amount_to_specific_moneybox(
    moneybox_id: Annotated[int, typer.Argument()],
    amount: Annotated[int, typer.Argument(min=1)],
    description: Annotated[str, typer.Argument()] = "",
):
    with PostMoneyboxBalanceAddApiConsumer(
        moneybox_id=moneybox_id,
        amount=amount,
        description=description,
    ) as consumer:
        print(consumer)


@app.command("sub")
def sub_amount_to_specific_moneybox(
    moneybox_id: Annotated[int, typer.Argument()],
    amount: Annotated[int, typer.Argument(min=1)],
    description: Annotated[str, typer.Argument()] = "",
):
    with PostMoneyboxBalanceSubApiConsumer(
        moneybox_id=moneybox_id,
        amount=amount,
        description=description,
    ) as consumer:
        print(consumer)


@app.command("transfer")
def transfer_amount(
    from_moneybox_id: Annotated[int, typer.Argument()],
    to_moneybox_id: Annotated[int, typer.Argument()],
    amount: Annotated[int, typer.Argument(min=1)],
    description: Annotated[str, typer.Argument()] = "",
):
    with PostMoneyboxBalanceTransferApiConsumer(
        from_moneybox_id=from_moneybox_id,
        to_moneybox_id=to_moneybox_id,
        amount=amount,
        description=description,
    ) as consumer:
        print(consumer)


@app.command("create")
def create_moneybox(
    name: Annotated[str, typer.Option()],
    savings_amount: Annotated[int, typer.Option()] = 0,
    savings_target: Annotated[Optional[int], typer.Option()] = None,
):
    with PostMoneyboxApiConsumer(
        name=name,
        savings_amount=savings_amount,
        savings_target=savings_target,
    ) as consumer:
        print(consumer)


@app.command("update")
def update_moneybox(
    moneybox_id: Annotated[int, typer.Argument()],
    name: Annotated[str, typer.Option()] = "",
    savings_amount: Annotated[int, typer.Option()] = -1,
    savings_target: Annotated[Optional[int], typer.Option()] = -1,
    clear_savings_target: Annotated[Optional[bool], typer.Option()] = False,
):
    with PatchMoneyboxApiConsumer(
        moneybox_id=moneybox_id,
        name=name,
        savings_amount=savings_amount,
        savings_target=savings_target,
        clear_savings_target=clear_savings_target,
    ) as consumer:
        print(consumer)


@app.command("delete")
def delete_moneybox(
    moneybox_id: Annotated[int, typer.Argument()],
):
    with DeleteMoneyboxApiConsumer(moneybox_id=moneybox_id) as consumer:
        print(consumer)


@app.command("logs")
def show_logs(
    moneybox_id: Annotated[int, typer.Argument()],
    n: Annotated[Optional[int], typer.Option()] = None,
):
    with GetMoneyboxTransactionsApiConsumer(
        moneybox_id=moneybox_id,
        n=n,
    ) as consumer:
        print(consumer)


@app.command("get-prioritylist")
def get_pioritylist():
    with GetPriorityListApiConsumer() as consumer:
        print(consumer)


@app.command("update-prioritylist")
def update_pioritylist(
    moneybox_id: Annotated[int, typer.Argument(help="The ID of the moneybox.")],
    direction: Annotated[
        str, typer.Argument(help="To move direction (supported: up|down).")
    ],
    n: Annotated[
        int, typer.Argument(help="The move steps [optional], defaults to 1.")
    ] = 1,
):
    try:
        move_direction = MoveDirection(direction)
    except:
        raise typer.BadParameter(f"{direction} unknown move direction.")

    with UpdatePriorityListApiConsumer(
        moneybox_id=moneybox_id,
        move_direction=move_direction,
        move_steps=n,
    ) as consumer:
        print(consumer)


@app.command("get-appsettings")
def get_appsettings():
    with GetAppSettingsApiConsumer() as consumer:
        print(consumer)


@app.command("update-appsettings")
def update_appsettings(
    is_automated_saving_active: Annotated[
        Optional[int], typer.Option(help="Activate automated savings.")
    ] = -1,
    overflow_moneybox_automated_savings_mode: Annotated[
        Optional[str],
        typer.Option(
            help="The mode for the overflow moneybox, modes: 'collect', 'add', 'fill'"
        ),
    ] = "",
    savings_amount: Annotated[
        Optional[int], typer.Option(help="The amount for automated distribution.")
    ] = -1,
    send_reports_via_email: Annotated[
        Optional[int],
        typer.Option(help="Enabled receiving emails after automated savings."),
    ] = -1,
    user_email_address: Annotated[
        Optional[str], typer.Option(help="The receivers email for automated savings.")
    ] = "",
):
    if overflow_moneybox_automated_savings_mode == "add":
        overflow_moneybox_automated_savings_mode = "add_to_automated_savings_amount"
    elif overflow_moneybox_automated_savings_mode == "fill":
        overflow_moneybox_automated_savings_mode = "fill_up_limited_moneyboxes"

    with PatchAppSettingsApiConsumer(
        send_reports_via_email=send_reports_via_email,
        user_email_address=user_email_address,
        is_automated_saving_active=is_automated_saving_active,
        savings_amount=savings_amount,
        overflow_moneybox_automated_savings_mode=overflow_moneybox_automated_savings_mode,
    ) as consumer:
        print(consumer)


@app.command("send-testemail")
def send_testemail():
    with PatchSendTestEmailApiConsumer() as consumer:
        print(consumer)


if __name__ == "__main__":
    app()
