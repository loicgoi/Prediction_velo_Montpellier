from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager


class DatabaseManager:
    """
    class to manage database connection and sessions using SQLAlchemy.
    """

    def __init__(self, connection_string: str):
        """
        Initialize DatabaseManager with a connection string.
        Creates the SQLAlchemy engine and session factory.
        """
        self.connection_string = connection_string
        # Create SQLAlchemy engine
        self.engine = create_engine(connection_string, echo=True, future=True)
        # Create session factory
        self.session_local = sessionmaker(bind=self.engine, autoflush=False)

    @contextmanager
    def get_session(self):
        """
        Context manager to provide a transactional session.
        Usage:
            with db.get_session() as session:
                session.add(obj)
                session.commit()
        """
        session = self.session_local()
        try:
            yield session
            session.commit()  # Commit after successful operations
        except Exception as e:
            session.rollback()  # Rollback if there is an error
            raise e
        finally:
            session.close()  # Always close the session
