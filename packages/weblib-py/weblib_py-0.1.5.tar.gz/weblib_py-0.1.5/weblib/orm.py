"""
A Unified Object-Relational Mapper (ORM) for WebLib, powered by SQLAlchemy.
This module provides a simple, consistent, and powerful API for database
interactions across multiple SQL database backends.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Table, MetaData
from sqlalchemy.orm import sessionmaker, Session as SQLAlchemySession, relationship, declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy.ext.declarative import declared_attr
from contextlib import contextmanager
import datetime
import types
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('weblib.orm')

# --- Database Connection Management ---

class Database:
    """Manages database connections and sessions."""

    def __init__(self, db_url: str, echo=False, pool_size=5, max_overflow=10, pool_timeout=30, pool_recycle=1800):
        """
        Initialize a database connection.
        
        Args:
            db_url: Database connection URL
            echo: Whether to log SQL statements
            pool_size: Size of the connection pool
            max_overflow: Maximum overflow connections
            pool_timeout: Timeout for getting a connection from the pool
            pool_recycle: Recycle connections after this many seconds
        """
        if not db_url:
            raise ValueError("Database URL cannot be empty.")
            
        logger.info(f"Initializing database connection to {db_url.split('@')[0].split(':')[0]}://****")
        
        # Configure engine with connection pooling for production use
        self.engine = create_engine(
            db_url, 
            echo=echo,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle
        )
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = self.SessionLocal()
        self._check_connection()

    def _check_connection(self):
        """Check if the database connection is working."""
        try:
            with self.engine.connect():
                logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to the database: {e}")
            raise ConnectionError(f"Failed to connect to the database: {e}")

    def create_all(self):
        """Creates all database tables defined by models that inherit from the base."""
        logger.info("Creating all database tables")
        # Use the MetaData from the model to create tables
        BaseModel.metadata.create_all(bind=self.engine)
        
    def create_tables(self, tables=None):
        """Creates database tables for the given models or all models."""
        if tables:
            logger.info(f"Creating specific database tables: {tables}")
        else:
            logger.info("Creating all database tables")
        BaseModel.metadata.create_all(bind=self.engine, tables=tables)

    @property
    def get_session(self):
        """Get the current database session."""
        return self.session

    @contextmanager
    def session_scope(self):
        """Provides a transactional scope around a series of operations."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            logger.error(f"Error in session scope: {e}")
            session.rollback()
            raise
        finally:
            session.close()

# --- Create a custom Base Model with the proper configuration ---
class _CustomBase:
    """Custom base for all models."""
    
    @declared_attr
    def __tablename__(cls):
        """Default tablename is the class name in lowercase."""
        return cls.__name__.lower()
    
    @declared_attr
    def __table_args__(cls):
        """Default table arguments with extend_existing=True."""
        return {'extend_existing': True}
        
    id = Column(Integer, primary_key=True)

    def __repr__(self):
        """Default string representation."""
        attrs = ', '.join(f"{k}={repr(v)}" for k, v in self.__dict__.items() 
                         if not k.startswith('_'))
        return f"<{self.__class__.__name__}({attrs})>"

# Create the base model class with our custom base
BaseModel = declarative_base(cls=_CustomBase)

# --- QuerySet and Manager for Active Record-style queries ---

class QuerySet:
    """Represents a collection of objects from a database query, allowing chaining."""

    def __init__(self, model_class, session: SQLAlchemySession):
        self.model_class = model_class
        self.session = session
        self.query = session.query(model_class)

    def filter(self, *criterion, **kwargs):
        """Filters the query based on criteria or keyword arguments."""
        if criterion:
            self.query = self.query.filter(*criterion)
        if kwargs:
            self.query = self.query.filter_by(**kwargs)
        return self

    def all(self):
        """Executes the query and returns all results."""
        return self.query.all()

    def first(self):
        """Executes the query and returns the first result."""
        return self.query.first()

    def get(self, **kwargs):
        """Retrieves a single object matching the criteria."""
        return self.filter(**kwargs).first()

    def create(self, **kwargs):
        """Creates and saves a new model instance."""
        instance = self.model_class(**kwargs)
        self.session.add(instance)
        self.session.commit()
        return instance

    def update(self, **kwargs):
        """Updates all objects in the current query."""
        count = self.query.update(kwargs, synchronize_session=False)
        self.session.commit()
        return count

    def delete(self):
        """Deletes all objects in the current query."""
        count = self.query.delete(synchronize_session=False)
        self.session.commit()
        return count
        
    def order_by(self, *args):
        """Orders the query results by the given fields."""
        self.query = self.query.order_by(*args)
        return self
        
    def count(self):
        """Returns the count of objects matching the query."""
        return self.query.count()

class Manager:
    """Provides the entry point for database queries on a model."""

    def __init__(self, model_class):
        self.model_class = model_class
        self.session = None

    def __call__(self, db: Database) -> QuerySet:
        self.session = db.session
        return QuerySet(self.model_class, db.session)

# --- Field Definitions for simplified model creation ---

class Field:
    """
    A Field represents a database column with a specific type.
    This is a simplified API that creates the appropriate SQLAlchemy Column.
    """
    
    def __init__(self, field_type, **kwargs):
        self.field_type = field_type
        self.kwargs = kwargs
        
        # Process max_length for strings
        if field_type == str and 'max_length' in kwargs:
            self.max_length = kwargs.pop('max_length')
        
    def _get_column_type(self):
        """Maps Python types to SQLAlchemy column types."""
        type_map = {
            int: Integer,
            str: String(self.kwargs.pop('max_length', 255)),
            float: Float,
            bool: Boolean,
            datetime.datetime: DateTime
        }
        
        return type_map.get(self.field_type, String(255))

# --- Base Model ---

# Add common functionality to all models
class Model(BaseModel):
    """Base model class with ORM functionality."""
    
    __abstract__ = True  # Don't create a table for this model
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def save(self):
        """Saves the model instance to the database."""
        session = object_session(self)
        if session:
            session.add(self)
            session.commit()
        return self
        
    def delete(self):
        """Deletes the model instance from the database."""
        session = object_session(self)
        if session:
            session.delete(self)
            session.commit()
    
    @classmethod
    def create_user(cls, db, username=None, email=None, password=None, **kwargs):
        """Convenience method to create a user with a hashed password."""
        with db.session_scope() as session:
            user = cls(
                username=username,
                email=email,
                password=password,
                **kwargs
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
    
    @classmethod
    def __init_subclass__(cls, **kwargs):
        # Add Field attributes as SQLAlchemy columns
        for name, attr in list(cls.__dict__.items()):
            if isinstance(attr, Field):
                # Convert Field to Column
                column_type = attr._get_column_type()
                column_kwargs = attr.kwargs.copy()
                
                # Handle foreign key
                if 'foreign_key' in column_kwargs:
                    foreign_key = column_kwargs.pop('foreign_key')
                    if isinstance(attr.field_type, type) and hasattr(attr.field_type, '__tablename__'):
                        column_kwargs['foreign_key'] = f"{attr.field_type.__tablename__}.id"
                
                # Create Column
                setattr(cls, name, Column(column_type, **column_kwargs))
        
        # Create manager
        cls.objects = Manager(cls)
        
        super().__init_subclass__(**kwargs)

# Import needed for save/delete methods
from sqlalchemy.orm import object_session

# --- Pre-defined Column Types for convenience ---

class IntegerColumn(Column):
    def __init__(self, *args, **kwargs):
        super().__init__(Integer, *args, **kwargs)

class StringColumn(Column):
    def __init__(self, length=255, *args, **kwargs):
        super().__init__(String(length), *args, **kwargs)

class FloatColumn(Column):
    def __init__(self, *args, **kwargs):
        super().__init__(Float, *args, **kwargs)

class BooleanColumn(Column):
    def __init__(self, *args, **kwargs):
        super().__init__(Boolean, *args, **kwargs)

class DateTimeColumn(Column):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', datetime.datetime.utcnow)
        super().__init__(DateTime, *args, **kwargs)

# --- Example Usage ---
if __name__ == "__main__":
    
    # 1. Configure the database
    db = Database('sqlite:///./test.db')

    # 2. Define a model with Field class
    class User(Model):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        name = Column(String(255), nullable=False)
        email = Column(String(255), unique=True, nullable=False)
        is_active = Column(Boolean, default=True)

    # 3. Create the table
    print("Creating database table...")
    db.create_tables()
    print("Table 'users' created.")

    # 4. Use the new ORM API
    print("Creating a new user...")
    User.objects(db).create(name="Jane Doe", email="jane.doe@example.com")

    print("Querying for user...")
    user = User.objects(db).filter(email="jane.doe@example.com").first()
    if user:
        print(f"Found user: {user.name} ({user.email})")

    print("Updating user...")
    User.objects(db).filter(email="jane.doe@example.com").update(is_active=False)
    
    updated_user = User.objects(db).get(email="jane.doe@example.com")
    if updated_user:
        print(f"User is now inactive: {not updated_user.is_active}")

    print("Deleting user...")
    User.objects(db).filter(email="jane.doe@example.com").delete()

    print("Example finished.")
    # Clean up the test database
    import os
    if os.path.exists("test.db"):
        os.remove("test.db")