from typing import Annotated, Optional, Union

import typer
from pydantic import BaseModel

from src.api_consumers import (
    DeleteMoneyboxApiConsumer,
    GetMoneyboxApiConsumer,
    GetMoneyboxesApiConsumer,
    PatchMoneyboxApiConsumer,
    PostMoneyboxApiConsumer,
    PostMoneyboxBalanceAddApiConsumer,
    PostMoneyboxBalanceSubApiConsumer,
    PostMoneyboxBalanceTransferApiConsumer,
    GetMoneyboxTransactionsApiConsumer, GetPriorityList, UpdatePriorityList,
)
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

    print(consumer)


@app.command("add")
def add_amount_to_specific_moneybox(
    moneybox_id: Annotated[int, typer.Argument()],
    amount: Annotated[int, typer.Argument(min=1)],
    description: Annotated[str, typer.Argument()] = "",
):
    consumer = PostMoneyboxBalanceAddApiConsumer(
        moneybox_id=moneybox_id,
        amount=amount,
        description=description,
    )

    print(consumer)


@app.command("sub")
def sub_amount_to_specific_moneybox(
    moneybox_id: Annotated[int, typer.Argument()],
    amount: Annotated[int, typer.Argument(min=1)],
    description: Annotated[str, typer.Argument()] = "",
):
    consumer = PostMoneyboxBalanceSubApiConsumer(
        moneybox_id=moneybox_id,
        amount=amount,
        description=description,
    )

    print(consumer)


@app.command("transfer")
def transfer_amount(
    from_moneybox_id: Annotated[int, typer.Argument()],
    to_moneybox_id: Annotated[int, typer.Argument()],
    amount: Annotated[int, typer.Argument(min=1)],
    description: Annotated[str, typer.Argument()] = "",
):
    consumer = PostMoneyboxBalanceTransferApiConsumer(
        from_moneybox_id=from_moneybox_id,
        to_moneybox_id=to_moneybox_id,
        amount=amount,
        description=description,
    )

    print(consumer)


@app.command("create")
def create_moneybox(
    name: Annotated[str, typer.Argument()],
):
    consumer = PostMoneyboxApiConsumer(
        new_moneybox_name=name,
    )

    print(consumer)


@app.command("update")
def update_moneybox(
    moneybox_id: Annotated[int, typer.Argument()],
    priority: Annotated[int, typer.Option()] = -1,
    name: Annotated[Optional[str], typer.Option()] = "",
    savings_amount: Annotated[Optional[int], typer.Option()] = -1,
    savings_target: Annotated[Optional[int], typer.Option(parser=int_or_none)] = -1,
):
    consumer = PatchMoneyboxApiConsumer(
        moneybox_id=moneybox_id,
        priority=priority,
        name=name,
        savings_amount=savings_amount,
        savings_target=savings_target,
    )

    print(consumer)


@app.command("delete")
def delete_moneybox(
    moneybox_id: Annotated[int, typer.Argument()],
):
    consumer = DeleteMoneyboxApiConsumer(moneybox_id=moneybox_id)

    print(consumer)


@app.command("logs")
def show_logs(
    moneybox_id: Annotated[int, typer.Argument()],
    n: Annotated[Optional[int], typer.Option()] = None,
):
    consumer = GetMoneyboxTransactionsApiConsumer(
        moneybox_id=moneybox_id,
        n=n,
    )

    print(consumer)


@app.command("get-prioritylist")
def get_pioritylist():
    consumer = GetPriorityList()
    print(consumer)


@app.command("update-prioritylist")
def update_pioritylist(
        moneybox_id: Annotated[int, typer.Argument(help="The ID of the moneybox.")],
        direction: Annotated[str, typer.Argument(help="To move direction (supported: up|down).")],
        n: Annotated[int, typer.Argument(help="The move steps [optional], defaults to 1.")] = 1,
):
    try:
        move_direction = MoveDirection(direction)
    except:
        raise typer.BadParameter(f"{direction} unknown move direction.")

    consumer = UpdatePriorityList(
        moneybox_id=moneybox_id,
        move_direction=move_direction,
        move_steps=n,
    )
    print(consumer)

if __name__ == "__main__":
    app()
