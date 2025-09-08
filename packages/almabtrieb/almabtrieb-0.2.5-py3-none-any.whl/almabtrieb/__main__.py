import click
import os
import json
import asyncio

from . import Almabtrieb


@click.group
@click.option(
    "--connection_string",
    help="Connection String to use, if None the CONNECTION_STRING environment variable is used",
)
@click.pass_context
def main(ctx, connection_string: str | None):
    """Helper to inspect traffic from the cattle drive protocol"""
    ctx.ensure_object(dict)

    if connection_string is None:
        connection_string = os.environ.get("CONNECTION_STRING")

    if connection_string is None:
        print("ERROR: Need to specify connection string")
        exit(1)

    ctx.obj["connection"] = Almabtrieb.from_connection_string(connection_string)


async def list_incoming(connection: Almabtrieb):
    async with connection:
        async for msg in connection.incoming():
            print(json.dumps(msg, indent=2))


async def list_outgoing(connection: Almabtrieb):
    async with connection:
        async for msg in connection.outgoing():
            print(json.dumps(msg, indent=2))


async def print_info(connection: Almabtrieb):
    async with connection:
        info = await connection.info()
        print("Actors:")
        for actor in info.actors:
            print(f"{actor.name:>30}: {actor.id}")

        print()
        print("Base URLs: " + ", ".join(info.base_urls))
        print()

        print("Method information")
        for mi in info.method_information:
            print(f"{mi.get('routing_key'):>30}: {mi.get('module')}")
            print(mi["description"])
            print()


@main.command("in")
@click.pass_context
def incoming(ctx):
    """Displays incoming messages"""
    asyncio.run(list_incoming(ctx.obj["connection"]))


@main.command("out")
@click.pass_context
def outgoing(ctx):
    """Displays outgoing messages"""
    asyncio.run(list_outgoing(ctx.obj["connection"]))


@main.command
@click.pass_context
def info(ctx):
    """Prints the information about the connection."""
    asyncio.run(print_info(ctx.obj["connection"]))


if __name__ == "__main__":
    main()
