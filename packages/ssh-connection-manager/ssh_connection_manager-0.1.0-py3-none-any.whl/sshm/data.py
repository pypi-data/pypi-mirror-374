from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import JSON, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import List
from platformdirs import user_data_dir
class Base(DeclarativeBase):
    pass

class Connection(Base):
    __tablename__ = "connections"
    id: Mapped[int] = mapped_column(primary_key=True)
    host: Mapped[str] = mapped_column(unique=True)
    args: Mapped[List[str]] = mapped_column(
        MutableList.as_mutable(JSON),  # works in SQLite (json1)
        default=list,                  # default to []
        nullable=False,
    )

db_path = user_data_dir(appname="sshm", ensure_exists=True) + "/data.sqlite"
engine = create_engine("sqlite:///" + db_path, echo=False)
Base.metadata.create_all(engine)