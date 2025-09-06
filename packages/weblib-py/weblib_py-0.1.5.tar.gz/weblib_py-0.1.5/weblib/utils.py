"""
Utility functions for WebLib framework
"""

from typing import Any, Union, Dict, List, Optional, TypeVar, Callable, cast

T = TypeVar('T')

def safe_int(x, default=0):
    try:
        if isinstance(x, str):
            s = x.strip()
            if not s:
                return default
            try:
                return int(s)
            except ValueError:
                return int(float(s))   # "3.0" -> 3
        return int(x)
    except Exception:
        return default

def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert a value to a float.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        float: Converted value or default
    """
    if value is None:
        return default
    
    if isinstance(value, float):
        return value
    
    if isinstance(value, int):
        return float(value)
    
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_str(value: Any, default: str = "") -> str:
    """
    Safely convert a value to a string.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        str: Converted value or default
    """
    if value is None:
        return default
    
    try:
        return str(value)
    except (ValueError, TypeError):
        return default


def safe_cast(value: Any, target_type: Callable[[Any], T], default: T) -> T:
    """
    Safely cast a value to a target type.
    
    Args:
        value: Value to cast
        target_type: Type casting function (e.g., int, float, str)
        default: Default value if casting fails
        
    Returns:
        T: Casted value or default
    """
    if value is None:
        return default
    
    try:
        return cast(T, target_type(value))
    except (ValueError, TypeError):
        return default


def safe_add(a: Any, b: Any, default: Any = 0) -> Any:
    """
    Safely add two values with type checking.
    
    Args:
        a: First value
        b: Second value
        default: Default value if addition fails
        
    Returns:
        Any: Result of addition or default
    """
    try:
        # Handle numeric types
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a + b
            
        # Convert string numbers to actual numbers
        if isinstance(a, str):
            if a.isdigit():
                a = int(a)
            else:
                try:
                    a = float(a)
                except (ValueError, TypeError):
                    # Keep as string if it's not a number
                    pass
                    
        if isinstance(b, str):
            if b.isdigit():
                b = int(b)
            else:
                try:
                    b = float(b)
                except (ValueError, TypeError):
                    # Keep as string if it's not a number
                    pass
        
        # Now check types again after conversion
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a + b
        
        # String concatenation
        if isinstance(a, str) and isinstance(b, str):
            return a + b
            
        # Convert to string for concatenation as a fallback
        if isinstance(a, str):
            return a + str(b)
            
        if isinstance(b, str):
            return str(a) + b
            
        # If we reach here, something is wrong with the types
        print(f"WARNING: safe_add called with incompatible types: {type(a)} and {type(b)}")
        return default
    except Exception as e:
        print(f"ERROR in safe_add: {str(e)} with values a={a} ({type(a)}) and b={b} ({type(b)})")
        return default


def safe_sub(a: Any, b: Any, default: Any = 0) -> Any:
    """
    Safely subtract two values with type checking.
    
    Args:
        a: First value
        b: Second value
        default: Default value if subtraction fails
        
    Returns:
        Any: Result of subtraction or default
    """
    # For subtraction, we need numeric types
    try:
        # Convert both to integers if possible
        if isinstance(a, str):
            if a.isdigit():
                a = int(a)
            else:
                try:
                    a = float(a)
                except (ValueError, TypeError):
                    return default
                    
        if isinstance(b, str):
            if b.isdigit():
                b = int(b)
            else:
                try:
                    b = float(b)
                except (ValueError, TypeError):
                    return default
        
        # Now we should have numeric types
        if isinstance(a, int) and isinstance(b, int):
            return a - b
        
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return float(a) - float(b)
            
        # If we've reached here, something is wrong with the types
        print(f"WARNING: safe_sub called with incompatible types: {type(a)} and {type(b)}")
        return default
    except Exception as e:
        print(f"ERROR in safe_sub: {str(e)} with values a={a} ({type(a)}) and b={b} ({type(b)})")
        return default


def clean_form_data(data: Dict[str, Any]) -> Dict[str, Any]:
    cleaned = {}
    for k, v in data.items():
        if isinstance(v, str):
            s = v.strip()
            if not s:
                cleaned[k] = v
                continue
            try:
                cleaned[k] = int(s)
                continue
            except Exception:
                try:
                    cleaned[k] = float(s)
                    continue
                except Exception:
                    cleaned[k] = v
        else:
            cleaned[k] = v
    return cleaned



def extract_query_param(query_string: str, param_name: str, default: Any = None, 
                     as_int: bool = False, as_float: bool = False) -> Any:
    """
    Extract a query parameter from a query string with robust type conversion.
    
    Args:
        query_string: Query string to parse
        param_name: Parameter name to extract
        default: Default value if parameter is not found
        as_int: Whether to convert the value to an integer
        as_float: Whether to convert the value to a float
        
    Returns:
        Any: Parameter value or default
    """
    if not query_string:
        return default
    
    param_prefix = f"{param_name}="
    
    if param_prefix not in query_string:
        return default
    
    try:
        # Find the parameter in the query string
        param_start = query_string.index(param_prefix) + len(param_prefix)
        param_end = query_string.find("&", param_start)
        
        if param_end == -1:
            param_value = query_string[param_start:]
        else:
            param_value = query_string[param_start:param_end]
        
        # Try to convert to appropriate type
        if as_int:
            try:
                return int(param_value)
            except (ValueError, TypeError):
                return default
        
        elif as_float:
            try:
                return float(param_value)
            except (ValueError, TypeError):
                return default
        
        return param_value
    except (ValueError, IndexError, TypeError):
        return default
