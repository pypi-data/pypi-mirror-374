"""
Sistema di Database ORM Semplice per WebLib
Integrazione con SQLite e operazioni CRUD base
"""

import sqlite3
import json
import os
from typing import Dict, Any, List, Optional, Union, Type
from datetime import datetime
from dataclasses import dataclass, field


class DatabaseError(Exception):
    """Eccezione per errori database"""
    pass


@dataclass
class QueryResult:
    """Risultato di una query"""
    rows: List[Dict[str, Any]]
    rowcount: int
    lastrowid: Optional[int] = None


class Database:
    """Gestore database SQLite"""
    
    def __init__(self, db_path: str = 'weblib.db', auto_create_tables: bool = True):
        self.db_path = db_path
        self.auto_create_tables = auto_create_tables
        self._connection = None
        self._registered_models = {}
        
        # Inizializza il database sempre
        self._initialize_db()
    
    def _initialize_db(self):
        """Inizializza il database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Crea tabella di sistema per tracciare modelli
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS _weblib_models (
                model_name TEXT PRIMARY KEY,
                table_name TEXT NOT NULL,
                schema_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
    
    def get_connection(self) -> sqlite3.Connection:
        """Ottiene connessione al database"""
        if not self._connection:
            self._connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row  # Per accesso tramite nome colonna
        return self._connection
    
    def close(self):
        """Chiude la connessione"""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def execute(self, query: str, params: tuple = ()) -> QueryResult:
        """Esegue una query"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            
            # Ottieni risultati
            if query.strip().upper().startswith('SELECT'):
                rows = [dict(row) for row in cursor.fetchall()]
            else:
                rows = []
                conn.commit()
            
            return QueryResult(
                rows=rows,
                rowcount=cursor.rowcount,
                lastrowid=cursor.lastrowid
            )
            
        except sqlite3.Error as e:
            conn.rollback()
            raise DatabaseError(f"Database error: {e}")
    
    def register_model(self, model_class: Type['Model']):
        """Registra un modello"""
        self._registered_models[model_class.__name__] = model_class
        
        if self.auto_create_tables:
            model_class._create_table(self)


class Field:
    """Campo del database"""
    
    def __init__(self, field_type: str, primary_key: bool = False, 
                 nullable: bool = True, default=None, unique: bool = False,
                 max_length: int = None):
        self.field_type = field_type
        self.primary_key = primary_key
        self.nullable = nullable
        self.default = default
        self.unique = unique
        self.max_length = max_length
        self.name = None  # Verrà impostato dal metaclass
    
    def to_sql(self) -> str:
        """Converte in definizione SQL"""
        sql_parts = [self.field_type]
        
        if self.primary_key:
            sql_parts.append("PRIMARY KEY")
        
        if not self.nullable and not self.primary_key:
            sql_parts.append("NOT NULL")
        
        if self.unique and not self.primary_key:
            sql_parts.append("UNIQUE")
        
        if self.default is not None:
            if isinstance(self.default, str):
                sql_parts.append(f"DEFAULT '{self.default}'")
            else:
                sql_parts.append(f"DEFAULT {self.default}")
        
        return " ".join(sql_parts)


# Tipi di campo comuni
class CharField(Field):
    def __init__(self, max_length: int = 255, **kwargs):
        super().__init__(f"VARCHAR({max_length})", max_length=max_length, **kwargs)


class TextField(Field):
    def __init__(self, **kwargs):
        super().__init__("TEXT", **kwargs)


class IntegerField(Field):
    def __init__(self, **kwargs):
        super().__init__("INTEGER", **kwargs)


class FloatField(Field):
    def __init__(self, **kwargs):
        super().__init__("REAL", **kwargs)


class BooleanField(Field):
    def __init__(self, **kwargs):
        super().__init__("INTEGER", **kwargs)
    
    def to_python(self, value):
        return bool(value) if value is not None else None
    
    def to_db(self, value):
        return int(value) if value is not None else None


class DateTimeField(Field):
    def __init__(self, auto_now: bool = False, auto_now_add: bool = False, **kwargs):
        super().__init__("TIMESTAMP", **kwargs)
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add
        
        if auto_now_add:
            self.default = "CURRENT_TIMESTAMP"
    
    def to_python(self, value):
        if value is None:
            return None
        if isinstance(value, str):
            # Gestisci formato ISO e timestamp SQLite
            if value == 'CURRENT_TIMESTAMP':
                return datetime.now()
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                # Prova formato SQLite standard: YYYY-MM-DD HH:MM:SS
                try:
                    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    return datetime.now()
        return value
    
    def to_db(self, value):
        if isinstance(value, datetime):
            return value.isoformat()
        return value


class JSONField(Field):
    def __init__(self, **kwargs):
        super().__init__("TEXT", **kwargs)
    
    def to_python(self, value):
        if isinstance(value, str):
            return json.loads(value)
        return value
    
    def to_db(self, value):
        return json.dumps(value) if value is not None else None


class ModelMeta(type):
    """Metaclass per i modelli"""
    
    def __new__(cls, name, bases, attrs):
        # Non processare la classe Model base
        if name == 'Model':
            return super().__new__(cls, name, bases, attrs)
        
        # Raccogli i campi
        fields = {}
        for key, value in attrs.items():
            if isinstance(value, Field):
                value.name = key
                fields[key] = value
        
        # Aggiungi ID automatico se non presente
        if 'id' not in fields:
            id_field = IntegerField(primary_key=True)
            id_field.name = 'id'
            fields['id'] = id_field
            attrs['id'] = id_field
        
        attrs['_fields'] = fields
        attrs['_table_name'] = attrs.get('_table_name', name.lower())
        
        return super().__new__(cls, name, bases, attrs)


class QuerySet:
    """Set di query per i modelli"""
    
    def __init__(self, model_class: Type['Model'], db: Database):
        self.model_class = model_class
        self.db = db
        self._filters = []
        self._order_by = []
        self._limit = None
        self._offset = None
    
    def filter(self, **kwargs):
        """Filtra i risultati"""
        new_qs = self._clone()
        for key, value in kwargs.items():
            if '__' in key:
                field, operator = key.split('__', 1)
            else:
                field, operator = key, 'exact'
            
            new_qs._filters.append((field, operator, value))
        return new_qs
    
    def order_by(self, *fields):
        """Ordina i risultati"""
        new_qs = self._clone()
        new_qs._order_by = list(fields)
        return new_qs
    
    def limit(self, count: int):
        """Limita il numero di risultati"""
        new_qs = self._clone()
        new_qs._limit = count
        return new_qs
    
    def offset(self, count: int):
        """Offset dei risultati"""
        new_qs = self._clone()
        new_qs._offset = count
        return new_qs
    
    def all(self) -> List['Model']:
        """Ottiene tutti i risultati"""
        query, params = self._build_query()
        result = self.db.execute(query, params)
        return [self.model_class._from_db_row(row) for row in result.rows]
    
    def first(self) -> Optional['Model']:
        """Ottiene il primo risultato"""
        results = self.limit(1).all()
        return results[0] if results else None
    
    def get(self, **kwargs) -> 'Model':
        """Ottiene un singolo oggetto"""
        results = self.filter(**kwargs).limit(2).all()
        if not results:
            raise DatabaseError(f"{self.model_class.__name__} not found")
        if len(results) > 1:
            raise DatabaseError(f"Multiple {self.model_class.__name__} found")
        return results[0]
    
    def count(self) -> int:
        """Conta i risultati"""
        query, params = self._build_count_query()
        result = self.db.execute(query, params)
        return result.rows[0]['count'] if result.rows else 0
    
    def delete(self) -> int:
        """Elimina i risultati"""
        query, params = self._build_delete_query()
        result = self.db.execute(query, params)
        return result.rowcount
    
    def _clone(self) -> 'QuerySet':
        """Clona il QuerySet"""
        new_qs = QuerySet(self.model_class, self.db)
        new_qs._filters = self._filters.copy()
        new_qs._order_by = self._order_by.copy()
        new_qs._limit = self._limit
        new_qs._offset = self._offset
        return new_qs
    
    def _build_query(self) -> tuple:
        """Costruisce la query SELECT"""
        query = f"SELECT * FROM {self.model_class._table_name}"
        params = []
        
        # WHERE
        if self._filters:
            where_clauses = []
            for field, operator, value in self._filters:
                if operator == 'exact':
                    where_clauses.append(f"{field} = ?")
                elif operator == 'icontains':
                    where_clauses.append(f"{field} LIKE ?")
                    value = f"%{value}%"
                elif operator == 'gt':
                    where_clauses.append(f"{field} > ?")
                elif operator == 'lt':
                    where_clauses.append(f"{field} < ?")
                elif operator == 'gte':
                    where_clauses.append(f"{field} >= ?")
                elif operator == 'lte':
                    where_clauses.append(f"{field} <= ?")
                params.append(value)
            
            query += " WHERE " + " AND ".join(where_clauses)
        
        # ORDER BY
        if self._order_by:
            order_clauses = []
            for field in self._order_by:
                if field.startswith('-'):
                    order_clauses.append(f"{field[1:]} DESC")
                else:
                    order_clauses.append(f"{field} ASC")
            query += " ORDER BY " + ", ".join(order_clauses)
        
        # LIMIT e OFFSET
        if self._limit:
            query += f" LIMIT {self._limit}"
        if self._offset:
            query += f" OFFSET {self._offset}"
        
        return query, tuple(params)
    
    def _build_count_query(self) -> tuple:
        """Costruisce query COUNT"""
        query = f"SELECT COUNT(*) as count FROM {self.model_class._table_name}"
        params = []
        
        if self._filters:
            where_clauses = []
            for field, operator, value in self._filters:
                if operator == 'exact':
                    where_clauses.append(f"{field} = ?")
                elif operator == 'icontains':
                    where_clauses.append(f"{field} LIKE ?")
                    value = f"%{value}%"
                params.append(value)
            
            query += " WHERE " + " AND ".join(where_clauses)
        
        return query, tuple(params)
    
    def _build_delete_query(self) -> tuple:
        """Costruisce query DELETE"""
        query = f"DELETE FROM {self.model_class._table_name}"
        params = []
        
        if self._filters:
            where_clauses = []
            for field, operator, value in self._filters:
                if operator == 'exact':
                    where_clauses.append(f"{field} = ?")
                params.append(value)
            
            query += " WHERE " + " AND ".join(where_clauses)
        
        return query, tuple(params)


class Model(metaclass=ModelMeta):
    """Classe base per i modelli"""
    
    def __init__(self, **kwargs):
        for field_name, field in self._fields.items():
            value = kwargs.get(field_name, field.default)
            setattr(self, field_name, value)
        
        self._is_saved = False
    
    @classmethod
    def _create_table(cls, db: Database):
        """Crea la tabella nel database"""
        columns = []
        for field_name, field in cls._fields.items():
            columns.append(f"{field_name} {field.to_sql()}")
        
        query = f"""
            CREATE TABLE IF NOT EXISTS {cls._table_name} (
                {', '.join(columns)}
            )
        """
        
        db.execute(query)
        
        # Registra il modello
        schema = {name: field.field_type for name, field in cls._fields.items()}
        db.execute(
            "INSERT OR REPLACE INTO _weblib_models (model_name, table_name, schema_json) VALUES (?, ?, ?)",
            (cls.__name__, cls._table_name, json.dumps(schema))
        )
    
    @classmethod
    def _from_db_row(cls, row: Dict[str, Any]) -> 'Model':
        """Crea istanza da riga database"""
        instance = cls()
        for field_name, field in cls._fields.items():
            value = row.get(field_name)
            
            # Converti valore se il campo ha to_python
            if hasattr(field, 'to_python'):
                value = field.to_python(value)
            
            setattr(instance, field_name, value)
        
        instance._is_saved = True
        return instance
    
    def save(self, db: Database) -> 'Model':
        """Salva il modello"""
        data = {}
        for field_name, field in self._fields.items():
            value = getattr(self, field_name, None)
            
            # Converti valore se il campo ha to_db
            if hasattr(field, 'to_db'):
                value = field.to_db(value)
            
            # Auto-now per DateTimeField
            if isinstance(field, DateTimeField) and field.auto_now:
                value = datetime.now().isoformat()
            
            data[field_name] = value
        
        if self._is_saved and hasattr(self, 'id') and self.id:
            # UPDATE
            set_clauses = []
            params = []
            for field_name, value in data.items():
                if field_name != 'id':
                    set_clauses.append(f"{field_name} = ?")
                    params.append(value)
            
            params.append(self.id)
            query = f"UPDATE {self._table_name} SET {', '.join(set_clauses)} WHERE id = ?"
            result = db.execute(query, tuple(params))
        else:
            # INSERT
            if 'id' in data and data['id'] is None:
                del data['id']
            
            columns = list(data.keys())
            placeholders = ['?' for _ in columns]
            query = f"INSERT INTO {self._table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
            result = db.execute(query, tuple(data.values()))
            
            if result.lastrowid:
                self.id = result.lastrowid
        
        self._is_saved = True
        return self
    
    def delete(self, db: Database):
        """Elimina il modello"""
        if hasattr(self, 'id') and self.id:
            query = f"DELETE FROM {self._table_name} WHERE id = ?"
            db.execute(query, (self.id,))
    
    @classmethod
    def objects(cls, db: Database) -> QuerySet:
        """Ottiene il QuerySet per il modello"""
        return QuerySet(cls, db)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte in dizionario"""
        result = {}
        for field_name in self._fields.keys():
            value = getattr(self, field_name, None)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[field_name] = value
        return result


# Database globale di default
default_db = Database()


def get_db() -> Database:
    """Ottiene il database di default"""
    return default_db


def set_db(db: Database):
    """Imposta il database di default"""
    global default_db
    default_db = db
