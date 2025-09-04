"""Transform followthemoney.EntityProxy into index actions"""

import functools
import itertools
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from multiprocessing import cpu_count
from typing import Generator, Iterable

from anystore.logging import get_logger
from anystore.util import Took
from banal import ensure_list, first
from followthemoney import EntityProxy, model, registry

from openaleph_search.index.indexer import Action, Actions
from openaleph_search.index.indexes import entities_write_index, schema_bucket
from openaleph_search.index.mapping import NUMERIC_TYPES, Field
from openaleph_search.settings import Settings, __version__
from openaleph_search.transform.tagging import (
    get_name_symbols,
    get_symbols,
    select_symbols,
)
from openaleph_search.transform.util import (
    get_geopoints,
    index_name_keys,
    index_name_parts,
    phonetic_names,
)
from openaleph_search.util import valid_dataset

log = get_logger(__name__)
settings = Settings()


def _numeric_values(type_, values) -> list[float]:
    values = [type_.to_number(v) for v in ensure_list(values)]
    return [v for v in values if v is not None]


def _caption_names(entity: EntityProxy) -> set[str]:
    names: set[str] = set()
    for prop_ in entity.schema.caption:
        # prop = entity.schema.properties[prop_]
        # if prop.type == registry.name:
        names.update(entity.get(prop_))
    return names


def _get_symbols(entity: EntityProxy) -> set[str]:
    symbols = select_symbols(entity)  # pre-computed in earlier stage
    if symbols:
        return symbols
    if entity.schema.is_a("LegalEntity"):
        return {str(s) for s in get_symbols(entity)}
    symbols: set[str] = set()
    symbols.update(map(str, get_name_symbols(model["Person"], *entity.names)))
    symbols.update(map(str, get_name_symbols(model["Organization"], *entity.names)))
    return symbols


def format_entity(dataset: str, entity: EntityProxy, **kwargs) -> Action | None:
    """Apply final denormalisations to the index."""
    # Abstract entities can appear when profile fragments for a missing entity
    # are present.
    if entity.schema.abstract:
        log.warning("Tried to index an abstract-typed entity: %r", entity)
        return None

    dataset = valid_dataset(dataset)

    data = entity.to_dict()
    # deprecated
    collection_id = kwargs.get("collection_id")
    if collection_id is not None:
        data[Field.COLLECTION_ID] = collection_id

    data[Field.DATASET] = dataset
    data[Field.SCHEMATA] = list(entity.schema.names)
    data[Field.CAPTION] = entity.caption

    # actual displayable entity names
    data[Field.NAME] = list(_caption_names(entity))
    # all names, including mentioned ones, for lookups
    names = list(entity.names)
    data[Field.NAME_SYMBOLS] = list(_get_symbols(entity))
    data[Field.NAME_KEYS] = list(index_name_keys(entity.schema, names))
    data[Field.NAME_PARTS] = list(index_name_parts(entity.schema, names))
    data[Field.NAME_PHONETIC] = list(phonetic_names(entity.schema, names))

    # Slight hack: a magic property in followthemoney that gets taken out
    # of the properties and added straight to the index text.
    properties = data.get("properties", {})
    data[Field.CONTENT] = properties.pop("indexText", [])

    # length normalization
    data[Field.NUM_VALUES] = sum([len(v) for v in properties.values()])

    # integer casting
    numeric = {}
    for prop in entity.iterprops():
        if prop.type in NUMERIC_TYPES:
            values = entity.get(prop)
            numeric[prop.name] = _numeric_values(prop.type, values)
    # also cast group field for dates
    numeric["dates"] = _numeric_values(
        registry.date, entity.get_type_values(registry.date)
    )
    data[Field.NUMERIC] = numeric

    # geo data if entity is an Address
    if "latitude" in entity.schema.properties:
        data[Field.GEO_POINT] = get_geopoints(entity)

    # Context data - from aleph system, not followthemoney. Probably deprecated soon
    data[Field.ROLE] = first(data.get("role_id", []))
    data[Field.PROFILE] = first(data.get("profile_id", []))
    data["mutable"] = kwargs.get("mutable", False)  # deprecated
    data[Field.ORIGIN] = ensure_list(data.get("origin"))
    # Logical simplifications of dates:
    created_at = ensure_list(data.get("created_at"))
    if len(created_at) > 0:
        data[Field.CREATED_AT] = min(created_at)
    updated_at = ensure_list(data.get("updated_at")) or created_at
    if len(updated_at) > 0:
        data[Field.UPDATED_AT] = max(updated_at)

    data[Field.INDEX_BUCKET] = schema_bucket(data["schema"])
    data[Field.INDEX_VERSION] = __version__
    data[Field.INDEX_TS] = datetime.now().isoformat()

    # log.info("%s", pformat(data))
    entity_id = data.pop("id")
    return {
        "_id": entity_id,
        "_index": entities_write_index(entity.schema),
        "_source": data,
    }


def format_entities(dataset: str, entities: Iterable[EntityProxy], **kwargs) -> Actions:
    for entity in entities:
        formatted = format_entity(dataset, entity, **kwargs)
        if formatted is not None:
            yield formatted


def format_batch(
    dataset: str, entities: Iterable[EntityProxy], **kwargs
) -> list[Action]:
    actions = []
    for entity in entities:
        formatted = format_entity(dataset, entity, **kwargs)
        if formatted is not None:
            actions.append(formatted)
    return actions


def format_parallel(
    dataset: str,
    entities: Generator[EntityProxy, None, None],
    concurrency: int | None = settings.indexer_concurrency,
    chunk_size: int | None = settings.indexer_chunk_size,
    **kwargs,
) -> Actions:
    """
    Transform entities into index actions in parallel
    """
    batches = itertools.batched(entities, n=chunk_size or settings.indexer_chunk_size)
    max_workers = min((cpu_count(), concurrency or settings.indexer_concurrency))
    max_queued = max_workers * 2
    func = functools.partial(format_batch, dataset=dataset, **kwargs)

    # shortcut for 1 worker
    if max_workers == 1:
        yield from func(entities=entities)
        return

    with ProcessPoolExecutor(max_workers=max_workers) as executor, Took() as t:
        transformed = 0
        active_futures = {}
        # Submit initial batches
        for _ in range(max_queued):
            try:
                batch = next(batches)
                future = executor.submit(func, entities=batch)
                active_futures[hash(future)] = future
            except StopIteration:
                break

        # Process results as they complete
        while active_futures:
            # Wait for at least one to complete
            completed = [f for f in active_futures.values() if f.done()]
            for future in completed:
                for action in future.result():
                    transformed += 1
                    yield action
                del active_futures[hash(future)]

                # Submit next batch
                try:
                    batch = next(batches)
                    new_future = executor.submit(func, entities=batch)
                    active_futures[hash(new_future)] = new_future
                except StopIteration:
                    pass

            if not completed:
                # If none completed, wait a bit
                time.sleep(0.1)

    log.info(f"Transformed {transformed} actions.", took=t.took)
