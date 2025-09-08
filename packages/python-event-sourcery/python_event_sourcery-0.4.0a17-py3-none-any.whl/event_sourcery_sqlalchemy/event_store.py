from collections.abc import Sequence
from dataclasses import dataclass, replace
from typing import cast

from more_itertools import first_true
from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from typing_extensions import Self

from event_sourcery.event_store import (
    NO_VERSIONING,
    Dispatcher,
    Position,
    RawEvent,
    RecordedRaw,
    StreamId,
    Versioning,
)
from event_sourcery.event_store.exceptions import (
    AnotherStreamWithThisNameButOtherIdExists,
    ConcurrentStreamWriteError,
)
from event_sourcery.event_store.interfaces import StorageStrategy
from event_sourcery.event_store.tenant_id import DEFAULT_TENANT, TenantId
from event_sourcery_sqlalchemy.models import Event as EventModel
from event_sourcery_sqlalchemy.models import Snapshot as SnapshotModel
from event_sourcery_sqlalchemy.models import Stream as StreamModel
from event_sourcery_sqlalchemy.outbox import SqlAlchemyOutboxStorageStrategy


@dataclass(repr=False)
class SqlAlchemyStorageStrategy(StorageStrategy):
    _session: Session
    _dispatcher: Dispatcher
    _outbox: SqlAlchemyOutboxStorageStrategy | None = None
    _tenant_id: TenantId = DEFAULT_TENANT

    def fetch_events(
        self,
        stream_id: StreamId,
        start: int | None = None,
        stop: int | None = None,
    ) -> list[RawEvent]:
        events_stmt = (
            select(EventModel)
            .filter_by(stream_id=stream_id, tenant_id=self._tenant_id)
            .order_by(EventModel.version)
        )

        if start is not None:
            events_stmt = events_stmt.filter(EventModel.version >= start)

        if stop is not None:
            events_stmt = events_stmt.filter(EventModel.version < stop)

        events: Sequence[EventModel | SnapshotModel]
        try:
            snapshot_stmt = (
                select(SnapshotModel)
                .join(StreamModel)
                .filter(
                    StreamModel.stream_id == stream_id,
                    StreamModel.tenant_id == self._tenant_id,
                )
                .order_by(SnapshotModel.created_at.desc())
                .limit(1)
            )
            if start is not None:
                snapshot_stmt = snapshot_stmt.filter(SnapshotModel.version >= start)

            if stop is not None:
                snapshot_stmt = snapshot_stmt.filter(SnapshotModel.version < stop)

            latest_snapshot = self._session.execute(snapshot_stmt).scalars().one()
        except NoResultFound:
            events = self._session.execute(events_stmt).scalars().all()
        else:
            events_stmt = events_stmt.filter(
                EventModel.version > latest_snapshot.version
            )
            newer_events = list(self._session.execute(events_stmt).scalars().all())
            events = [latest_snapshot, *newer_events]

        if not events:
            return []

        raw_dict_events = [
            RawEvent(
                uuid=event.uuid,
                stream_id=event.stream_id,
                created_at=event.created_at,
                version=event.version,
                name=event.name,
                data=event.data,
                context=event.event_context,
            )
            for event in events
        ]
        return raw_dict_events

    def _ensure_stream(self, stream_id: StreamId, versioning: Versioning) -> None:
        initial_version = versioning.initial_version

        condition = (
            (StreamModel.uuid == stream_id)
            & (StreamModel.category == (stream_id.category or ""))
            & (StreamModel.tenant_id == self._tenant_id)
        )
        if stream_id.name:
            condition = condition | (
                (StreamModel.name == stream_id.name)
                & (StreamModel.category == (stream_id.category or ""))
                & (StreamModel.tenant_id == self._tenant_id)
            )
        matching_streams_stmt = select(StreamModel).where(condition)
        matching_streams = self._session.execute(matching_streams_stmt).scalars().all()
        if not matching_streams:
            ensure_stream_stmt = (
                postgresql_insert(StreamModel)
                .values(
                    uuid=stream_id,
                    name=stream_id.name,
                    category=stream_id.category or "",
                    version=initial_version,
                    tenant_id=self._tenant_id,
                )
                .on_conflict_do_nothing()
            )
            self._session.execute(ensure_stream_stmt)
            matching_streams = (
                self._session.execute(matching_streams_stmt).scalars().all()
            )

        if stream_id.name is not None:
            matching_stream_with_same_name: StreamModel = [
                stream
                for stream in matching_streams
                if stream.name == stream_id.name
                and stream.category == (stream_id.category or "")
            ].pop()
            if matching_stream_with_same_name.stream_id != stream_id:
                raise AnotherStreamWithThisNameButOtherIdExists()

        stream = cast(
            StreamModel,
            first_true(
                matching_streams, pred=lambda stream: stream.stream_id == stream_id
            ),
        )
        self._session.info.setdefault("strong_set", set())
        self._session.info["strong_set"].add(stream)

        versioning.validate_if_compatible(stream.version)

        if versioning.expected_version and versioning is not NO_VERSIONING:
            bump_version_stmt = (
                update(StreamModel)
                .where(
                    StreamModel.stream_id == stream_id,
                    StreamModel.version == versioning.expected_version,
                )
                .values(version=versioning.initial_version)
            )
            result = self._session.execute(bump_version_stmt)

            if result.rowcount != 1:
                # optimistic lock failed
                raise ConcurrentStreamWriteError

    def insert_events(
        self, stream_id: StreamId, versioning: Versioning, events: list[RawEvent]
    ) -> None:
        self._ensure_stream(stream_id=stream_id, versioning=versioning)

        stream = cast(
            StreamModel,
            first_true(
                self._session.info["strong_set"],
                pred=lambda model: isinstance(model, StreamModel)
                and model.stream_id == stream_id
                and model.tenant_id == self._tenant_id,
            ),
        )

        entries = [
            EventModel(
                uuid=event.uuid,
                created_at=event.created_at,
                name=event.name,
                data=event.data,
                event_context=event.context,
                version=event.version,
            )
            for event in events
        ]
        stream.events.extend(entries)
        self._session.flush()
        records = [
            RecordedRaw(entry=raw, position=db.id, tenant_id=db.tenant_id)
            for raw, db in zip(events, entries, strict=False)
        ]
        if self._outbox:
            self._outbox.put_into_outbox(records)
        self._session.flush()
        self._dispatcher.dispatch(*records)

    def save_snapshot(self, snapshot: RawEvent) -> None:
        entry = SnapshotModel(
            uuid=snapshot.uuid,
            created_at=snapshot.created_at,
            version=snapshot.version,
            name=snapshot.name,
            data=snapshot.data,
            event_context=snapshot.context,
        )
        stream = (
            self._session.query(StreamModel)
            .filter_by(stream_id=snapshot.stream_id)
            .one()
        )
        stream.snapshots.append(entry)
        self._session.flush()

    def delete_stream(self, stream_id: StreamId) -> None:
        delete_events_stmt = delete(EventModel).where(
            EventModel.stream_id == stream_id,
        )
        self._session.execute(delete_events_stmt)
        delete_stream_stmt = delete(StreamModel).where(
            StreamModel.stream_id == stream_id,
        )
        self._session.execute(delete_stream_stmt)

    @property
    def current_position(self) -> Position | None:
        stmt = select(func.max(EventModel.id))
        last_event = self._session.scalar(stmt)
        return last_event or Position(0)

    def scoped_for_tenant(self, tenant_id: TenantId) -> Self:
        return replace(self, _tenant_id=tenant_id)
