import datetime
import itertools
import typing

import sqlalchemy.event as event
import sqlalchemy.orm as orm

from temporal_sqlalchemy.bases import ClockedOption, Clocked


def _temporal_models(session: orm.Session) -> typing.Iterable[Clocked]:
    for obj in session:
        if isinstance(getattr(obj, 'temporal_options', None), ClockedOption):
            yield obj


def persist_history(session: orm.Session, flush_context, instances):
    if any(_temporal_models(session.deleted)):
        raise ValueError("Cannot delete temporal objects!!!! YOU WILL REGRET THIS!!!!")

    correlate_timestamp = datetime.datetime.now(tz=datetime.timezone.utc)
    for obj in _temporal_models(itertools.chain(session.dirty, session.new)):
        obj.temporal_options.record_history(obj, session, correlate_timestamp)


def temporal_session(session: orm.Session) -> orm.Session:
    event.listen(session, 'before_flush', persist_history)
    return session