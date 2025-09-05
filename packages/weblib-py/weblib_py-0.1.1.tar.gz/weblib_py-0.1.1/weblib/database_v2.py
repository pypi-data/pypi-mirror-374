#!/usr/bin/env python3
"""
Sistema Database Integrato per WebLib v2.0
Combina ORM esistente con supporto multi-database
"""

import sqlite3
import json
import os
import threading
from contextlib import contextmanager
from typing import Dict, Any, List, Optional, Union, Type
from datetime import datetime
from dataclasses import dataclass, field

# Import del nuovo sistema multi-database
from .multi_database import DatabaseManager, DatabaseAdapter, get_database_config, build_connection_string


class DatabaseError(Exception):
    """Eccezione per errori database"""
    pass


@dataclass 
class QueryResult:
    """Risultato di una query"""
    rows: List[Dict[str, Any]]
    rowcount: int
    lastrowid: Optional[int] = None


class Field:
    """Campo base del modello"""
    
    def __init__(self, max_length=None, unique=False, null=True, default=None, primary_key=False, auto_increment=False):
        self.max_length = max_length
        self.unique = unique
        self.null = null
        self.default = default
        self.primary_key = primary_key
        self.auto_increment = auto_increment
        self.field_type = self.__class__.__name__
    
    def get_schema_info(self):
        """Ritorna info schema per il database adapter"""
        return {
            'type': self.field_type,
            'max_length': self.max_length,
            'unique': self.unique,
            'nullable': self.null,
            'default': self.default,
            'primary_key': self.primary_key,
            'auto_increment': self.auto_increment
        }


class CharField(Field):
    """Campo stringa"""
    def __init__(self, max_length=255, **kwargs):
        super().__init__(max_length=max_length, **kwargs)


class TextField(Field):
    """Campo testo lungo"""
    pass


class IntegerField(Field):
    """Campo intero"""
    pass


class FloatField(Field):
    """Campo decimale"""
    pass


class BooleanField(Field):
    """Campo booleano"""
    def __init__(self, default=False, **kwargs):
        super().__init__(default=default, **kwargs)


class DateTimeField(Field):
    """Campo data/ora"""
    def __init__(self, auto_now=False, auto_now_add=False, **kwargs):
        super().__init__(**kwargs)
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add


class JSONField(Field):
    """Campo JSON"""
    pass


class QuerySet:
    """Query builder per diversi database"""
    
    def __init__(self, model, database):
        self.model = model
        self.database = database
        self._filters = []
        self._order = []
        self._limit_value = None
        self._offset_value = None
    
    def filter(self, **kwargs):
        """Aggiunge filtri WHERE"""
        new_qs = QuerySet(self.model, self.database)
        new_qs._filters = self._filters + [kwargs]
        new_qs._order = self._order[:]
        new_qs._limit_value = self._limit_value
        new_qs._offset_value = self._offset_value
        return new_qs
    
    def order_by(self, field):
        """Aggiunge ordinamento"""
        new_qs = QuerySet(self.model, self.database)
        new_qs._filters = self._filters[:]
        new_qs._order = self._order + [field]
        new_qs._limit_value = self._limit_value
        new_qs._offset_value = self._offset_value
        return new_qs
    
    def limit(self, limit):
        """Limita numero risultati"""
        new_qs = QuerySet(self.model, self.database)
        new_qs._filters = self._filters[:]
        new_qs._order = self._order[:]
        new_qs._limit_value = limit
        new_qs._offset_value = self._offset_value
        return new_qs
    
    def offset(self, offset):
        """Imposta offset risultati"""
        new_qs = QuerySet(self.model, self.database)
        new_qs._filters = self._filters[:]
        new_qs._order = self._order[:]
        new_qs._limit_value = self._limit_value
        new_qs._offset_value = offset
        return new_qs
    
    def all(self):
        """Esegue query e ritorna tutti i risultati"""
        if hasattr(self.database, 'adapter') and self.database.adapter.db_type == 'mongodb':
            return self._execute_mongo_query()
        else:
            return self._execute_sql_query()
    
    def first(self):
        """Ritorna primo risultato o None"""
        results = self.limit(1).all()
        return results[0] if results else None
    
    def get(self, **kwargs):
        """Ritorna singolo risultato"""
        results = self.filter(**kwargs).limit(2).all()
        if not results:
            raise Exception(f"{self.model.__name__} not found")
        if len(results) > 1:
            raise Exception(f"Multiple {self.model.__name__} found")
        return results[0]
    
    def count(self):
        """Conta risultati"""
        if hasattr(self.database, 'adapter') and self.database.adapter.db_type == 'mongodb':
            return len(self.all())  # Semplificato per demo
        else:
            query, params = self._build_count_query()
            if hasattr(self.database, 'adapter'):
                result = self.database.adapter.execute_query(query, params)
                return result[0]['count'] if result else 0
            else:
                # Fallback per database legacy con connessione thread-safe
                with self.database.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    result = cursor.fetchone()
                    return result[0] if result else 0
    
    def delete(self):
        """Elimina record che matchano i filtri"""
        if hasattr(self.database, 'adapter') and self.database.adapter.db_type == 'mongodb':
            filter_dict = self._build_mongo_filter()
            return self.database.adapter.execute_non_query(
                self.model._table_name, 'delete', filter_dict
            )
        else:
            query, params = self._build_delete_query()
            if hasattr(self.database, 'adapter'):
                return self.database.adapter.execute_non_query(query, params)
            else:
                # Fallback per database legacy con connessione thread-safe
                with self.database.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    conn.commit()
                    return cursor.rowcount
    
    def _execute_sql_query(self):
        """Esegue query SQL"""
        query, params = self._build_select_query()
        
        if hasattr(self.database, 'adapter'):
            # Nuovo sistema multi-database
            results = self.database.adapter.execute_query(query, params)
            return [self.model._from_dict(row) for row in results]
        else:
            # Fallback per database legacy con connessione thread-safe
            with self.database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [self.model._from_dict(dict(row)) for row in rows]
    
    def _execute_mongo_query(self):
        """Esegue query MongoDB"""
        filter_dict = self._build_mongo_filter()
        results = self.database.adapter.execute_query(self.model._table_name, filter_dict)
        return [self.model._from_dict(row) for row in results]
    
    def _build_select_query(self):
        """Costruisce query SELECT SQL"""
        query = f"SELECT * FROM {self.model._table_name}"
        params = []
        
        # WHERE clause
        if self._filters:
            where_clauses = []
            for filter_dict in self._filters:
                for key, value in filter_dict.items():
                    where_clauses.append(f"{key} = ?")
                    params.append(value)
            
            query += f" WHERE {' AND '.join(where_clauses)}"
        
        # ORDER BY clause
        if self._order:
            order_clauses = []
            for field in self._order:
                if field.startswith('-'):
                    order_clauses.append(f"{field[1:]} DESC")
                else:
                    order_clauses.append(f"{field} ASC")
            query += f" ORDER BY {', '.join(order_clauses)}"
        
        # LIMIT clause
        if self._limit_value:
            query += f" LIMIT {self._limit_value}"
            
        if self._offset_value:
            query += f" OFFSET {self._offset_value}"
        
        return query, tuple(params)
    
    def _build_count_query(self):
        """Costruisce query COUNT"""
        query = f"SELECT COUNT(*) as count FROM {self.model._table_name}"
        params = []
        
        if self._filters:
            where_clauses = []
            for filter_dict in self._filters:
                for key, value in filter_dict.items():
                    where_clauses.append(f"{key} = ?")
                    params.append(value)
            
            query += f" WHERE {' AND '.join(where_clauses)}"
        
        return query, tuple(params)
    
    def _build_delete_query(self):
        """Costruisce query DELETE"""
        query = f"DELETE FROM {self.model._table_name}"
        params = []
        
        if self._filters:
            where_clauses = []
            for filter_dict in self._filters:
                for key, value in filter_dict.items():
                    where_clauses.append(f"{key} = ?")
                    params.append(value)
            
            query += f" WHERE {' AND '.join(where_clauses)}"
        
        return query, tuple(params)
    
    def _build_mongo_filter(self):
        """Costruisce filtro MongoDB"""
        filter_dict = {}
        for filter_obj in self._filters:
            filter_dict.update(filter_obj)
        return filter_dict


class Model:
    """Modello base con supporto multi-database"""
    _table_name = None
    _database = None
    
    def __init__(self, **kwargs):
        # Auto-imposta _table_name se non specificato
        if not self._table_name:
            self._table_name = self.__class__.__name__.lower()
        
        # Imposta valori campi
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        # Imposta ID se non presente
        if not hasattr(self, 'id'):
            self.id = None
    
    def save(self, database):
        """Salva il modello nel database"""
        self._database = database
        
        # Ottieni dati del modello
        data = self._to_dict()
        
        if self.id is None:
            # INSERT
            return self._insert(database, data)
        else:
            # UPDATE
            return self._update(database, data)
    
    def delete(self, database):
        """Elimina il modello dal database"""
        if self.id is None:
            raise ValueError("Cannot delete unsaved model")
        
        if hasattr(database, 'adapter') and database.adapter.db_type == 'mongodb':
            return database.adapter.execute_non_query(
                self._table_name, 'delete', {'id': self.id}
            )
        elif hasattr(database, 'adapter'):
            query = f"DELETE FROM {self._table_name} WHERE id = ?"
            return database.adapter.execute_non_query(query, (self.id,))
        else:
            # Fallback per database legacy con connessione thread-safe
            query = f"DELETE FROM {self._table_name} WHERE id = ?"
            with database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (self.id,))
                conn.commit()
                return cursor.rowcount
    
    def _insert(self, database, data):
        """Inserisce nuovo record"""
        if hasattr(database, 'adapter') and database.adapter.db_type == 'mongodb':
            # MongoDB insert
            if 'id' in data:
                del data['id']  # MongoDB genera _id automaticamente
            
            result = database.adapter.execute_non_query(
                self._table_name, 'insert', data
            )
            if result:
                # MongoDB non restituisce ID facilmente, simuliamo
                import time
                self.id = str(int(time.time()))
            return result
        elif hasattr(database, 'adapter'):
            # SQL insert con nuovo adapter
            fields = [k for k in data.keys() if k != 'id']
            values = [data[k] for k in fields]
            placeholders = ', '.join(['?' for _ in fields])
            
            query = f"INSERT INTO {self._table_name} ({', '.join(fields)}) VALUES ({placeholders})"
            result = database.adapter.execute_non_query(query, tuple(values))
            
            if result > 0:
                self.id = database.adapter.get_last_insert_id()
            
            return result
        else:
            # Fallback per database legacy con connessione thread-safe
            fields = [k for k in data.keys() if k != 'id']
            values = [data[k] for k in fields]
            placeholders = ', '.join(['?' for _ in fields])
            
            query = f"INSERT INTO {self._table_name} ({', '.join(fields)}) VALUES ({placeholders})"
            
            with database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, values)
                conn.commit()
                
                self.id = cursor.lastrowid
                return cursor.rowcount
    
    def _update(self, database, data):
        """Aggiorna record esistente"""
        if hasattr(database, 'adapter') and database.adapter.db_type == 'mongodb':
            # MongoDB update
            filter_dict = {'id': self.id}
            update_data = {k: v for k, v in data.items() if k != 'id'}
            
            return database.adapter.execute_non_query(
                self._table_name, 'update', {
                    'filter': filter_dict,
                    'update': update_data
                }
            )
        elif hasattr(database, 'adapter'):
            # SQL update con nuovo adapter
            fields = [k for k in data.keys() if k != 'id']
            set_clause = ', '.join([f"{k} = ?" for k in fields])
            values = [data[k] for k in fields] + [self.id]
            
            query = f"UPDATE {self._table_name} SET {set_clause} WHERE id = ?"
            return database.adapter.execute_non_query(query, tuple(values))
        else:
            # Fallback per database legacy con connessione thread-safe
            fields = [k for k in data.keys() if k != 'id']
            set_clause = ', '.join([f"{k} = ?" for k in fields])
            values = [data[k] for k in fields] + [self.id]
            
            query = f"UPDATE {self._table_name} SET {set_clause} WHERE id = ?"
            
            with database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, values)
                conn.commit()
                
                return cursor.rowcount
    
    def _to_dict(self):
        """Converte modello in dizionario"""
        data = {}
        for attr_name in dir(self):
            if not attr_name.startswith('_') and not callable(getattr(self, attr_name)):
                attr_value = getattr(self, attr_name)
                
                # Gestisci campi speciali
                if isinstance(attr_value, datetime):
                    data[attr_name] = attr_value.isoformat()
                elif isinstance(attr_value, (dict, list)):
                    # Per MongoDB lascia native, per SQL converte in JSON
                    if hasattr(self._database, 'adapter') and self._database.adapter.db_type == 'mongodb':
                        data[attr_name] = attr_value
                    else:
                        data[attr_name] = json.dumps(attr_value)
                else:
                    data[attr_name] = attr_value
        
        return data
    
    @classmethod
    def _from_dict(cls, data):
        """Crea istanza da dizionario"""
        instance = cls()
        for key, value in data.items():
            setattr(instance, key, value)
        return instance
    
    @classmethod
    def objects(cls, database):
        """Ritorna QuerySet per queries"""
        return QuerySet(cls, database)
    
    @classmethod
    def _get_schema(cls):
        """Ottiene schema del modello"""
        schema = {}
        
        # ID field (sempre presente)
        schema['id'] = {
            'type': 'IntegerField',
            'primary_key': True,
            'auto_increment': True,
            'nullable': False
        }
        
        # Altri campi
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, Field):
                schema[attr_name] = attr.get_schema_info()
        
        return schema


class Database:
    """Database manager unificato con supporto multi-database e legacy"""
    
    def __init__(self, connection_string: str = None, db_type: str = None, db_path: str = None):
        """
        Inizializza database con supporto legacy e multi-database
        
        Args:
            connection_string: String di connessione per multi-database
            db_type: Tipo database (auto-detect se non specificato)
            db_path: Path SQLite per backward compatibility
        """
        # Backward compatibility
        if db_path and not connection_string:
            connection_string = f"sqlite:///{db_path}"
        
        if connection_string is None:
            config = get_database_config()
            connection_string = config['DATABASE_URL']
        
        self.db_path = connection_string  # Backward compatibility
        self._registered_models = []
        
        # Thread-local storage per connessioni SQLite
        self._thread_local = threading.local()
        
        # Prova nuovo sistema multi-database
        try:
            if db_type is None:
                db_type, _ = DatabaseManager.parse_connection_string(connection_string)
            
            self.adapter = DatabaseManager.create_adapter(db_type, connection_string)
            self.multi_db = True
            print(f"✅ Database multi-support attivo: {db_type}")
            
        except Exception as e:
            # Fallback a SQLite legacy
            print(f"⚠️  Fallback to SQLite legacy: {e}")
            self.multi_db = False
            self.adapter = None
            
            # Estrai path da connection string se necessario
            if connection_string.startswith('sqlite:///'):
                db_path = connection_string[10:]  # Rimuovi 'sqlite:///'
            else:
                db_path = connection_string
            
            self._sqlite_path = db_path
    
    @contextmanager
    def get_connection(self):
        """Ottiene connessione thread-safe per SQLite legacy"""
        if self.multi_db:
            yield self.adapter
        else:
            # Thread-safe SQLite connection
            if not hasattr(self._thread_local, 'connection'):
                self._thread_local.connection = sqlite3.connect(
                    self._sqlite_path, 
                    check_same_thread=False
                )
                self._thread_local.connection.row_factory = sqlite3.Row
            
            try:
                yield self._thread_local.connection
            except Exception as e:
                # Riconnetti in caso di errore
                try:
                    self._thread_local.connection.close()
                except:
                    pass
                self._thread_local.connection = sqlite3.connect(
                    self._sqlite_path,
                    check_same_thread=False
                )
                self._thread_local.connection.row_factory = sqlite3.Row
                raise e
    
    def _connect_legacy(self, db_path):
        """Connessione legacy SQLite - DEPRECATED, usa get_connection()"""
        print(f"⚠️  _connect_legacy è deprecato, uso thread-safe connections")
        pass
    
    def register_model(self, model_class):
        """Registra un modello e crea tabella"""
        if model_class not in self._registered_models:
            self._registered_models.append(model_class)
            self._create_table_for_model(model_class)
    
    def _create_table_for_model(self, model_class):
        """Crea tabella per modello"""
        table_name = model_class._table_name or model_class.__name__.lower()
        
        if self.multi_db:
            # Nuovo sistema multi-database
            if not self.adapter.table_exists(table_name):
                schema = model_class._get_schema()
                self.adapter.create_table(table_name, schema)
                print(f"✅ Tabella '{table_name}' creata ({self.adapter.db_type})")
        else:
            # Sistema legacy con connessione thread-safe
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=?
                """, (table_name,))
                
                if not cursor.fetchone():
                    # Crea tabella con schema legacy
                    schema = self._get_legacy_schema(model_class)
                    query = f"CREATE TABLE {table_name} ({', '.join(schema)})"
                    
                    cursor.execute(query)
                    conn.commit()
                    print(f"✅ Tabella '{table_name}' creata (SQLite legacy)")
    
    def _get_legacy_schema(self, model_class):
        """Schema legacy per SQLite"""
        schema = []
        
        # ID field
        schema.append("id INTEGER PRIMARY KEY AUTOINCREMENT")
        
        # Altri campi
        for attr_name in dir(model_class):
            attr = getattr(model_class, attr_name)
            if isinstance(attr, Field):
                field_def = f"{attr_name}"
                
                # Tipo campo
                if isinstance(attr, CharField):
                    field_def += f" VARCHAR({attr.max_length or 255})"
                elif isinstance(attr, TextField):
                    field_def += " TEXT"
                elif isinstance(attr, IntegerField):
                    field_def += " INTEGER"
                elif isinstance(attr, BooleanField):
                    field_def += " BOOLEAN"
                elif isinstance(attr, DateTimeField):
                    field_def += " DATETIME"
                elif isinstance(attr, JSONField):
                    field_def += " TEXT"
                else:
                    field_def += " TEXT"
                
                # Vincoli
                if not attr.null:
                    field_def += " NOT NULL"
                if attr.unique:
                    field_def += " UNIQUE"
                if attr.default is not None:
                    if isinstance(attr.default, str):
                        field_def += f" DEFAULT '{attr.default}'"
                    else:
                        field_def += f" DEFAULT {attr.default}"
                
                schema.append(field_def)
        
        return schema
    
    def close(self):
        """Chiude connessione database"""
        if self.multi_db and self.adapter:
            self.adapter.disconnect()
        else:
            # Chiudi connessione thread-local se esiste
            if hasattr(self._thread_local, 'connection'):
                try:
                    self._thread_local.connection.close()
                    delattr(self._thread_local, 'connection')
                except:
                    pass


# Database singleton con supporto parametri multipli
_database_instance = None

def get_db(connection_string: str = None, db_type: str = None, db_path: str = None) -> Database:
    """
    Ottiene istanza database singleton con supporto multi-database e legacy
    
    Args:
        connection_string: Per multi-database (es: 'postgresql://user:pass@host/db')
        db_type: Tipo database esplicito
        db_path: Per backward compatibility SQLite
    """
    global _database_instance
    
    if _database_instance is None or connection_string or db_type or db_path:
        _database_instance = Database(connection_string, db_type, db_path)
    
    return _database_instance
