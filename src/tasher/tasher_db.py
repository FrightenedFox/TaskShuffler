from sqlalchemy import create_engine, Table, Column, ForeignKey, String, Integer
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def create_db(echo=False):
    engine = create_engine("sqlite+pysqlite:///../../tasher.db", echo=echo, future=True)
    Base.metadata.create_all(engine)
    return engine


def delete_db(engine):
    Base.metadata.drop_all(engine)


class Topics(Base):
    __tablename__ = "topics"

    topic_name = Column(String, primary_key=True)


class Tags(Base):
    __tablename__ = "tags"

    tag_name = Column(String, primary_key=True)


class Tasks(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True)
    task_tex = Column(String, nullable=False)
    difficulty = Column(Integer, nullable=False)
    answer = Column(String)

    solutions = relationship("Solutions")


class Solutions(Base):
    __tablename__ = "solutions"

    solution_id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.task_id"))
    path = Column(String, nullable=False)


topics_tags = Table(
    "topics_tags",
    Base.metadata,
    Column("topic_name", ForeignKey("topics.topic_name"), primary_key=True),
    Column("tag_name", ForeignKey("tags.tag_name"), primary_key=True),
)

tags_tasks = Table(
    "tags_tasks",
    Base.metadata,
    Column("tag_name", ForeignKey("tags.tag_name"), primary_key=True),
    Column("task_id", ForeignKey("tasks.task_id"), primary_key=True),
)


if __name__ == '__main__':
    create_db(echo=False)
