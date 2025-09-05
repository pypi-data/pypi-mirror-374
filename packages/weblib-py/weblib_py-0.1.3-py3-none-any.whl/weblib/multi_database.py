#!/usr/bin/env python3
"""
Sistema Multi-Database per WebLib v2.0
Supporta SQLite, PostgreSQL, MySQL, MongoDB
"""

import os
import json
import sqlite3
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from datetime import datetime


class DatabaseAdapter(ABC):
    """Classe base per adapter database"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None
        self.db_type = self.__class__.__name__.replace("Adapter", "").lower()
    
    @abstractmethod
    def connect(self):
        """Connessione al database"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Disconnessione dal database"""
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Esegue una query e ritorna risultati"""
        pass
    
    @abstractmethod
    def execute_non_query(self, query: str, params: tuple = None) -> int:
        """Esegue una query che non ritorna risultati (INSERT, UPDATE, DELETE)"""
        pass
    
    @abstractmethod
    def create_table(self, table_name: str, schema: Dict):
        """Crea una tabella con lo schema specificato"""
        pass
    
    @abstractmethod
    def table_exists(self, table_name: str) -> bool:
        """Controlla se una tabella esiste"""
        pass
    
    @abstractmethod
    def get_last_insert_id(self) -> int:
        """Ottiene l'ultimo ID inserito"""
        pass


class SQLiteAdapter(DatabaseAdapter):
    """Adapter per SQLite"""
    
    def connect(self):
        """Connessione a SQLite"""
        try:
            # Estrai il path del database dalla connection string
            if self.connection_string.startswith('sqlite:///'):
                db_path = self.connection_string[10:]  # Rimuovi 'sqlite:///'
            else:
                db_path = self.connection_string
            
            self.connection = sqlite3.connect(db_path)
            self.connection.row_factory = sqlite3.Row  # Per risultati come dict
            return True
        except Exception as e:
            print(f"❌ Errore connessione SQLite: {e}")
            return False
    
    def disconnect(self):
        if self.connection:
            self.connection.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Esegue SELECT e ritorna risultati"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"❌ Errore query SQLite: {e}")
            return []
    
    def execute_non_query(self, query: str, params: tuple = None) -> int:
        """Esegue INSERT, UPDATE, DELETE"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Errore non-query SQLite: {e}")
            return 0
    
    def create_table(self, table_name: str, schema: Dict):
        """Crea tabella SQLite"""
        columns = []
        for field_name, field_info in schema.items():
            field_type = self._map_field_type(field_info['type'])
            column_def = f"{field_name} {field_type}"
            
            if field_info.get('primary_key'):
                column_def += " PRIMARY KEY"
                if field_info.get('auto_increment'):
                    column_def += " AUTOINCREMENT"
            
            if field_info.get('unique'):
                column_def += " UNIQUE"
            
            if not field_info.get('nullable', True):
                column_def += " NOT NULL"
            
            if 'default' in field_info:
                column_def += f" DEFAULT {field_info['default']}"
            
            columns.append(column_def)
        
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
        self.execute_non_query(query)
    
    def table_exists(self, table_name: str) -> bool:
        """Controlla se tabella esiste in SQLite"""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = self.execute_query(query, (table_name,))
        return len(result) > 0
    
    def get_last_insert_id(self) -> int:
        """Ultimo ID inserito in SQLite"""
        return self.connection.lastrowid
    
    def _map_field_type(self, weblib_type: str) -> str:
        """Mappa tipi WebLib a tipi SQLite"""
        mapping = {
            'CharField': 'TEXT',
            'TextField': 'TEXT',
            'IntegerField': 'INTEGER',
            'FloatField': 'REAL',
            'BooleanField': 'INTEGER',
            'DateTimeField': 'TEXT',
            'JSONField': 'TEXT'
        }
        return mapping.get(weblib_type, 'TEXT')


class PostgreSQLAdapter(DatabaseAdapter):
    """Adapter per PostgreSQL"""
    
    def connect(self):
        """Connessione a PostgreSQL"""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            self.connection = psycopg2.connect(
                self.connection_string,
                cursor_factory=RealDictCursor
            )
            return True
        except ImportError:
            print("❌ PostgreSQL: pip install psycopg2-binary")
            return False
        except Exception as e:
            print(f"❌ Errore connessione PostgreSQL: {e}")
            return False
    
    def disconnect(self):
        if self.connection:
            self.connection.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Esegue SELECT PostgreSQL"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"❌ Errore query PostgreSQL: {e}")
            return []
    
    def execute_non_query(self, query: str, params: tuple = None) -> int:
        """Esegue INSERT, UPDATE, DELETE PostgreSQL"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Errore non-query PostgreSQL: {e}")
            self.connection.rollback()
            return 0
    
    def create_table(self, table_name: str, schema: Dict):
        """Crea tabella PostgreSQL"""
        columns = []
        for field_name, field_info in schema.items():
            field_type = self._map_field_type(field_info['type'])
            column_def = f"{field_name} {field_type}"
            
            if field_info.get('primary_key') and field_info.get('auto_increment'):
                column_def = f"{field_name} SERIAL PRIMARY KEY"
            elif field_info.get('primary_key'):
                column_def += " PRIMARY KEY"
            
            if field_info.get('unique') and not field_info.get('primary_key'):
                column_def += " UNIQUE"
            
            if not field_info.get('nullable', True):
                column_def += " NOT NULL"
            
            if 'default' in field_info:
                column_def += f" DEFAULT {field_info['default']}"
            
            columns.append(column_def)
        
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
        self.execute_non_query(query)
    
    def table_exists(self, table_name: str) -> bool:
        """Controlla se tabella esiste in PostgreSQL"""
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = %s
        );
        """
        result = self.execute_query(query, (table_name,))
        return result[0]['exists'] if result else False
    
    def get_last_insert_id(self) -> int:
        """Ultimo ID inserito PostgreSQL"""
        result = self.execute_query("SELECT LASTVAL()")
        return result[0]['lastval'] if result else 0
    
    def _map_field_type(self, weblib_type: str) -> str:
        """Mappa tipi WebLib a tipi PostgreSQL"""
        mapping = {
            'CharField': 'VARCHAR(255)',
            'TextField': 'TEXT',
            'IntegerField': 'INTEGER',
            'FloatField': 'REAL',
            'BooleanField': 'BOOLEAN',
            'DateTimeField': 'TIMESTAMP',
            'JSONField': 'JSONB'
        }
        return mapping.get(weblib_type, 'TEXT')


class MySQLAdapter(DatabaseAdapter):
    """Adapter per MySQL"""
    
    def connect(self):
        """Connessione a MySQL"""
        try:
            import pymysql
            
            # Parse connection string
            # Format: mysql://user:password@host:port/database
            parts = self.connection_string.replace('mysql://', '').split('/')
            auth_host = parts[0]
            database = parts[1] if len(parts) > 1 else 'weblib'
            
            if '@' in auth_host:
                auth, host = auth_host.split('@')
                user, password = auth.split(':')
            else:
                host = auth_host
                user = 'root'
                password = ''
            
            host_port = host.split(':')
            host = host_port[0]
            port = int(host_port[1]) if len(host_port) > 1 else 3306
            
            self.connection = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                cursorclass=pymysql.cursors.DictCursor
            )
            return True
        except ImportError:
            print("❌ MySQL: pip install PyMySQL")
            return False
        except Exception as e:
            print(f"❌ Errore connessione MySQL: {e}")
            return False
    
    def disconnect(self):
        if self.connection:
            self.connection.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Esegue SELECT MySQL"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Errore query MySQL: {e}")
            return []
    
    def execute_non_query(self, query: str, params: tuple = None) -> int:
        """Esegue INSERT, UPDATE, DELETE MySQL"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Errore non-query MySQL: {e}")
            self.connection.rollback()
            return 0
    
    def create_table(self, table_name: str, schema: Dict):
        """Crea tabella MySQL"""
        columns = []
        for field_name, field_info in schema.items():
            field_type = self._map_field_type(field_info['type'])
            column_def = f"{field_name} {field_type}"
            
            if field_info.get('primary_key'):
                column_def += " PRIMARY KEY"
                if field_info.get('auto_increment'):
                    column_def += " AUTO_INCREMENT"
            
            if field_info.get('unique') and not field_info.get('primary_key'):
                column_def += " UNIQUE"
            
            if not field_info.get('nullable', True):
                column_def += " NOT NULL"
            
            if 'default' in field_info:
                column_def += f" DEFAULT {field_info['default']}"
            
            columns.append(column_def)
        
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)}) ENGINE=InnoDB"
        self.execute_non_query(query)
    
    def table_exists(self, table_name: str) -> bool:
        """Controlla se tabella esiste in MySQL"""
        query = "SHOW TABLES LIKE %s"
        result = self.execute_query(query, (table_name,))
        return len(result) > 0
    
    def get_last_insert_id(self) -> int:
        """Ultimo ID inserito MySQL"""
        return self.connection.insert_id()
    
    def _map_field_type(self, weblib_type: str) -> str:
        """Mappa tipi WebLib a tipi MySQL"""
        mapping = {
            'CharField': 'VARCHAR(255)',
            'TextField': 'TEXT',
            'IntegerField': 'INT',
            'FloatField': 'FLOAT',
            'BooleanField': 'BOOLEAN',
            'DateTimeField': 'DATETIME',
            'JSONField': 'JSON'
        }
        return mapping.get(weblib_type, 'TEXT')


class MongoAdapter(DatabaseAdapter):
    """Adapter per MongoDB"""
    
    def connect(self):
        """Connessione a MongoDB"""
        try:
            from pymongo import MongoClient
            
            self.client = MongoClient(self.connection_string)
            # Estrai nome database dalla connection string
            db_name = self.connection_string.split('/')[-1] or 'weblib'
            self.connection = self.client[db_name]
            return True
        except ImportError:
            print("❌ MongoDB: pip install pymongo")
            return False
        except Exception as e:
            print(f"❌ Errore connessione MongoDB: {e}")
            return False
    
    def disconnect(self):
        if hasattr(self, 'client'):
            self.client.close()
    
    def execute_query(self, collection: str, filter_dict: Dict = None) -> List[Dict]:
        """Query MongoDB (equivalente SELECT)"""
        try:
            collection_obj = self.connection[collection]
            filter_dict = filter_dict or {}
            
            results = list(collection_obj.find(filter_dict))
            
            # Converti ObjectId in string
            for result in results:
                if '_id' in result:
                    result['id'] = str(result['_id'])
                    del result['_id']
            
            return results
        except Exception as e:
            print(f"❌ Errore query MongoDB: {e}")
            return []
    
    def execute_non_query(self, collection: str, operation: str, data: Dict) -> int:
        """Operazioni MongoDB (INSERT, UPDATE, DELETE)"""
        try:
            collection_obj = self.connection[collection]
            
            if operation == 'insert':
                result = collection_obj.insert_one(data)
                return 1 if result.inserted_id else 0
            elif operation == 'update':
                filter_dict = data.get('filter', {})
                update_dict = data.get('update', {})
                result = collection_obj.update_many(filter_dict, {'$set': update_dict})
                return result.modified_count
            elif operation == 'delete':
                result = collection_obj.delete_many(data)
                return result.deleted_count
                
            return 0
        except Exception as e:
            print(f"❌ Errore non-query MongoDB: {e}")
            return 0
    
    def create_table(self, collection_name: str, schema: Dict):
        """Crea collection MongoDB (non serve schema)"""
        # MongoDB è schemaless, creiamo solo la collection
        try:
            if collection_name not in self.connection.list_collection_names():
                self.connection.create_collection(collection_name)
        except Exception as e:
            print(f"❌ Errore creazione collection MongoDB: {e}")
    
    def table_exists(self, collection_name: str) -> bool:
        """Controlla se collection esiste in MongoDB"""
        return collection_name in self.connection.list_collection_names()
    
    def get_last_insert_id(self) -> str:
        """MongoDB usa ObjectId invece di integer"""
        return str(self.last_insert_id) if hasattr(self, 'last_insert_id') else ""


class DatabaseManager:
    """Manager per database multipli"""
    
    _adapters = {
        'sqlite': SQLiteAdapter,
        'postgresql': PostgreSQLAdapter,
        'postgres': PostgreSQLAdapter,  # Alias
        'mysql': MySQLAdapter,
        'mongodb': MongoAdapter,
        'mongo': MongoAdapter  # Alias
    }
    
    @classmethod
    def create_adapter(cls, db_type: str, connection_string: str) -> DatabaseAdapter:
        """Crea adapter per tipo database"""
        if db_type.lower() not in cls._adapters:
            raise ValueError(f"Database '{db_type}' non supportato. Disponibili: {list(cls._adapters.keys())}")
        
        adapter_class = cls._adapters[db_type.lower()]
        adapter = adapter_class(connection_string)
        
        if adapter.connect():
            return adapter
        else:
            raise ConnectionError(f"Impossibile connettersi a {db_type}")
    
    @classmethod
    def register_adapter(cls, db_type: str, adapter_class: type):
        """Registra un nuovo adapter database"""
        if not issubclass(adapter_class, DatabaseAdapter):
            raise ValueError("L'adapter deve ereditare da DatabaseAdapter")
        
        cls._adapters[db_type.lower()] = adapter_class
    
    @classmethod
    def list_supported_databases(cls) -> List[str]:
        """Lista database supportati"""
        return list(cls._adapters.keys())
    
    @classmethod
    def parse_connection_string(cls, connection_string: str) -> tuple:
        """Parse connection string per estrarre tipo DB"""
        if '://' not in connection_string:
            # Default SQLite
            return 'sqlite', connection_string
        
        db_type = connection_string.split('://')[0]
        return db_type, connection_string


# Supporto per environment variables
def get_database_config() -> Dict:
    """Ottiene configurazione database da environment variables"""
    return {
        'DATABASE_URL': os.getenv('DATABASE_URL', 'sqlite:///weblib.db'),
        'DATABASE_TYPE': os.getenv('DATABASE_TYPE', 'sqlite'),
        'DATABASE_HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'DATABASE_PORT': os.getenv('DATABASE_PORT', '5432'),
        'DATABASE_NAME': os.getenv('DATABASE_NAME', 'weblib'),
        'DATABASE_USER': os.getenv('DATABASE_USER', 'weblib'),
        'DATABASE_PASSWORD': os.getenv('DATABASE_PASSWORD', '')
    }


def build_connection_string(db_type: str, **kwargs) -> str:
    """Costruisce connection string per database"""
    templates = {
        'sqlite': 'sqlite:///{database}',
        'postgresql': 'postgresql://{user}:{password}@{host}:{port}/{database}',
        'mysql': 'mysql://{user}:{password}@{host}:{port}/{database}',
        'mongodb': 'mongodb://{host}:{port}/{database}'
    }
    
    template = templates.get(db_type.lower())
    if not template:
        raise ValueError(f"Tipo database '{db_type}' non supportato")
    
    return template.format(**kwargs)


if __name__ == "__main__":
    print("🧪 Test Database Multi-Support")
    
    # Test SQLite
    print("\n📦 Test SQLite:")
    try:
        adapter = DatabaseManager.create_adapter('sqlite', 'test.db')
        print("✅ SQLite connesso")
        adapter.disconnect()
    except Exception as e:
        print(f"❌ SQLite: {e}")
    
    # Lista database supportati
    print(f"\n📋 Database supportati: {DatabaseManager.list_supported_databases()}")
    
    # Test connection string parsing
    examples = [
        'sqlite:///weblib.db',
        'postgresql://user:pass@localhost:5432/weblib',
        'mysql://user:pass@localhost:3306/weblib',
        'mongodb://localhost:27017/weblib'
    ]
    
    print("\n🔗 Parse Connection Strings:")
    for conn_str in examples:
        db_type, parsed = DatabaseManager.parse_connection_string(conn_str)
        print(f"  {conn_str} -> {db_type}")
