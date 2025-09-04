from typing import Annotated, Optional

import typer
from anystore.cli import ErrorHandler
from anystore.io import (
    logged_items,
    smart_read,
    smart_stream_json,
    smart_write,
    smart_write_json,
)
from anystore.logging import configure_logging, get_logger
from anystore.util import Took, dump_json
from ftmq.io import smart_read_proxies
from rich import print

from openaleph_search.index import admin, entities
from openaleph_search.index.indexer import bulk_actions
from openaleph_search.search.logic import search_body, search_query_string
from openaleph_search.settings import Settings, __version__
from openaleph_search.transform.entity import format_parallel

settings = Settings()

cli = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=settings.debug)
cli_search = typer.Typer(name="search", no_args_is_help=True)
cli.add_typer(cli_search, short_help="Execute search queries")
log = get_logger(__name__)

OPT_INPUT_URI = typer.Option("-", "-i", help="Input uri, default stdin")
OPT_OUTPUT_URI = typer.Option("-", "-o", help="Output uri, default stdout")
OPT_DATASET = typer.Option(..., "-d", help="Dataset")


@cli.callback(invoke_without_command=True)
def cli_openaleph_search(
    version: Annotated[Optional[bool], typer.Option(..., help="Show version")] = False,
    settings: Annotated[
        Optional[bool], typer.Option(..., help="Show current settings")
    ] = False,
):
    if version:
        print(__version__)
        raise typer.Exit()
    if settings:
        settings_ = Settings()
        print(settings_)
        raise typer.Exit()
    configure_logging()


@cli.command("upgrade")
def cli_upgrade():
    """Upgrade the index mappings or create if they don't exist"""
    with ErrorHandler(log):
        admin.upgrade_search()


@cli.command("reset")
def cli_reset():
    """Drop all data and indexes and re-upgrade"""
    with ErrorHandler(log):
        admin.delete_index()
        admin.upgrade_search()


@cli.command("format-entities")
def cli_format_entities(
    input_uri: str = OPT_INPUT_URI,
    output_uri: str = OPT_OUTPUT_URI,
    dataset: str = OPT_DATASET,
):
    """Transform entities into index actions"""
    with ErrorHandler(log):
        entities = smart_read_proxies(input_uri)
        formatted = logged_items(
            format_parallel(dataset, entities), "Format", 10_000, "Entity", log
        )
        smart_write_json(output_uri, formatted)


@cli.command("index-entities")
def cli_index_entities(
    input_uri: str = OPT_INPUT_URI,
    dataset: str = OPT_DATASET,
):
    """Index entities into given dataset"""
    with ErrorHandler(log):
        entities.index_bulk(dataset, smart_read_proxies(input_uri))


@cli.command("index-actions")
def cli_index_actions(input_uri: str = OPT_INPUT_URI):
    """Index a stream of actions"""
    with ErrorHandler(log), Took() as t:
        actions = smart_stream_json(input_uri)
        bulk_actions(actions)
        log.info("Index actions complete.", input_uri=input_uri, took=t.took)


OPT_SEARCH_ARGS = Annotated[
    Optional[str],
    typer.Option(
        help="Query parser args and filters (e.g. `filter:dataset=my_dataset`)"
    ),
]
OPT_SEARCH_FORMAT = Annotated[
    Optional[str], typer.Option(help="Output format (raw, parsed)")
]


@cli_search.command("query-string")
def cli_search_query(
    q: str,
    args: OPT_SEARCH_ARGS = None,
    output_uri: str = OPT_OUTPUT_URI,
    output_format: OPT_SEARCH_FORMAT = "raw",
):
    """Search using elastic 'query_string' using the `EntitiesQuery` class"""
    res = search_query_string(q, args)
    data = dump_json(dict(res), clean=True, newline=True)
    smart_write(output_uri, data)


@cli_search.command("body")
def cli_search_body(
    input_uri: str = OPT_INPUT_URI,
    output_uri: str = OPT_OUTPUT_URI,
    output_format: OPT_SEARCH_FORMAT = "raw",
    index: str | None = None,
    routing: str | None = None,
):
    """Search with raw json body for query"""
    body = smart_read(input_uri, serialization_mode="json")
    res = search_body(body, index, routing)
    data = dump_json(dict(res), clean=True, newline=True)
    smart_write(output_uri, data)


@cli_search.command("match")
def cli_match(
    q: str,
    args: OPT_SEARCH_ARGS = None,
    output_uri: str = OPT_OUTPUT_URI,
    output_format: OPT_SEARCH_FORMAT = "raw",
):
    """Search using elastic 'match_query' using the `MatchQuery` class"""
    res = search_query_string(q, args)
    data = dump_json(dict(res), clean=True, newline=True)
    smart_write(output_uri, data)
