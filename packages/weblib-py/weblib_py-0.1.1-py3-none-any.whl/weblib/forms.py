"""
Sistema di Form Validation per WebLib
Validazione avanzata dei form con feedback utente
"""

import re
from typing import Dict, Any, List, Optional, Callable, Union
from .html import HtmlElement, Form, Div, Label, Input, Select, Option, Textarea, Button, Span, P
from .config import CSSClasses


class ValidationError(Exception):
    """Eccezione per errori di validazione"""
    pass


class Field:
    """Campo base per form"""
    
    def __init__(self, required=False, validators=None, error_message=None, **kwargs):
        self.required = required
        self.validators = validators or []
        self.error_message = error_message
        self.kwargs = kwargs
        self.value = None
        self.errors = []
    
    def validate(self, value):
        """Valida il valore del campo"""
        self.value = value
        self.errors = []
        
        # Controllo required
        if self.required and not value:
            self.errors.append(self.error_message or "This field is required")
            return False
        
        # Esegui validatori personalizzati
        for validator in self.validators:
            try:
                if callable(validator):
                    validator(value)
                else:
                    # Validatore con parametri
                    validator_func, args = validator
                    validator_func(value, *args)
            except ValidationError as e:
                self.errors.append(str(e))
        
        return len(self.errors) == 0
    
    def render(self, name: str) -> HtmlElement:
        """Renderizza il campo HTML"""
        raise NotImplementedError("Field must implement render() method")


class StringField(Field):
    """Campo testo semplice"""
    
    def __init__(self, min_length=None, max_length=None, pattern=None, **kwargs):
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = pattern
        
        validators = kwargs.get('validators', [])
        
        if min_length:
            validators.append(lambda x: self._validate_min_length(x, min_length))
        if max_length:
            validators.append(lambda x: self._validate_max_length(x, max_length))
        if pattern:
            validators.append(lambda x: self._validate_pattern(x, pattern))
        
        kwargs['validators'] = validators
        super().__init__(**kwargs)
    
    def _validate_min_length(self, value, min_len):
        if value and len(value) < min_len:
            raise ValidationError(f"Minimum length is {min_len} characters")
    
    def _validate_max_length(self, value, max_len):
        if value and len(value) > max_len:
            raise ValidationError(f"Maximum length is {max_len} characters")
    
    def _validate_pattern(self, value, pattern):
        if value and not re.match(pattern, value):
            raise ValidationError("Invalid format")
    
    def render(self, name: str) -> HtmlElement:
        input_classes = [CSSClasses.FORM_CONTROL]
        if self.errors:
            input_classes.append("is-invalid")
        
        attrs = {
            'name': name,
            'id': name,
            'classes': input_classes,
            'value': self.value or ''
        }
        
        if self.min_length:
            attrs['minlength'] = self.min_length
        if self.max_length:
            attrs['maxlength'] = self.max_length
        
        attrs.update(self.kwargs)
        
        return Input(input_type="text", **attrs)


class EmailField(StringField):
    """Campo email con validazione"""
    
    def __init__(self, **kwargs):
        email_validator = lambda x: self._validate_email(x)
        validators = kwargs.get('validators', [])
        validators.append(email_validator)
        kwargs['validators'] = validators
        super().__init__(**kwargs)
    
    def _validate_email(self, value):
        if value:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, value):
                raise ValidationError("Invalid email format")
    
    def render(self, name: str) -> HtmlElement:
        input_classes = [CSSClasses.FORM_CONTROL]
        if self.errors:
            input_classes.append("is-invalid")
        
        attrs = {
            'name': name,
            'id': name,
            'classes': input_classes,
            'value': self.value or ''
        }
        attrs.update(self.kwargs)
        
        return Input(input_type="email", **attrs)


class NumberField(Field):
    """Campo numerico"""
    
    def __init__(self, min_value=None, max_value=None, **kwargs):
        self.min_value = min_value
        self.max_value = max_value
        
        validators = kwargs.get('validators', [])
        validators.append(lambda x: self._validate_number(x))
        
        if min_value is not None:
            validators.append(lambda x: self._validate_min_value(x, min_value))
        if max_value is not None:
            validators.append(lambda x: self._validate_max_value(x, max_value))
        
        kwargs['validators'] = validators
        super().__init__(**kwargs)
    
    def _validate_number(self, value):
        if value:
            try:
                float(value)
            except ValueError:
                raise ValidationError("Must be a valid number")
    
    def _validate_min_value(self, value, min_val):
        if value and float(value) < min_val:
            raise ValidationError(f"Minimum value is {min_val}")
    
    def _validate_max_value(self, value, max_val):
        if value and float(value) > max_val:
            raise ValidationError(f"Maximum value is {max_val}")
    
    def render(self, name: str) -> HtmlElement:
        input_classes = [CSSClasses.FORM_CONTROL]
        if self.errors:
            input_classes.append("is-invalid")
        
        attrs = {
            'name': name,
            'id': name,
            'classes': input_classes,
            'value': self.value or ''
        }
        
        if self.min_value is not None:
            attrs['min'] = self.min_value
        if self.max_value is not None:
            attrs['max'] = self.max_value
        
        attrs.update(self.kwargs)
        
        return Input(input_type="number", **attrs)


class SelectField(Field):
    """Campo select con opzioni"""
    
    def __init__(self, choices=None, **kwargs):
        self.choices = choices or []
        super().__init__(**kwargs)
    
    def render(self, name: str) -> HtmlElement:
        select_classes = [CSSClasses.FORM_SELECT]
        if self.errors:
            select_classes.append("is-invalid")
        
        options = []
        for choice in self.choices:
            if isinstance(choice, tuple):
                value, text = choice
                selected = str(value) == str(self.value) if self.value else False
                options.append(Option(text, value=value, selected=selected))
            else:
                selected = str(choice) == str(self.value) if self.value else False
                options.append(Option(choice, value=choice, selected=selected))
        
        attrs = {
            'name': name,
            'id': name,
            'classes': select_classes
        }
        attrs.update(self.kwargs)
        
        return Select(options, **attrs)


class TextAreaField(Field):
    """Campo textarea"""
    
    def __init__(self, rows=3, **kwargs):
        self.rows = rows
        super().__init__(**kwargs)
    
    def render(self, name: str) -> HtmlElement:
        textarea_classes = [CSSClasses.FORM_CONTROL]
        if self.errors:
            textarea_classes.append("is-invalid")
        
        attrs = {
            'name': name,
            'id': name,
            'classes': textarea_classes,
            'rows': self.rows
        }
        attrs.update(self.kwargs)
        
        return Textarea(self.value or '', **attrs)


class FormValidator:
    """Classe base per validatori di form"""
    
    def __init__(self):
        self.fields = {}
        self.data = {}
        self.errors = {}
        self._initialize_fields()
    
    def _initialize_fields(self):
        """Inizializza i campi dal metaclass o attributi"""
        for name in dir(self):
            attr = getattr(self, name)
            if isinstance(attr, Field):
                self.fields[name] = attr
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Valida i dati del form"""
        self.data = data
        self.errors = {}
        is_valid = True
        
        # Valida ogni campo
        for name, field in self.fields.items():
            value = data.get(name, '')
            if not field.validate(value):
                self.errors[name] = field.errors
                is_valid = False
        
        # Validazioni personalizzate
        try:
            self.clean()
        except ValidationError as e:
            self.errors['__all__'] = [str(e)]
            is_valid = False
        
        return is_valid
    
    def clean(self):
        """Metodo per validazioni personalizzate cross-field"""
        pass
    
    def get_field_errors(self, field_name: str) -> List[str]:
        """Ottiene gli errori di un campo specifico"""
        return self.errors.get(field_name, [])
    
    def get_form_errors(self) -> List[str]:
        """Ottiene gli errori globali del form"""
        return self.errors.get('__all__', [])
    
    def render_field(self, field_name: str, label: str = None) -> HtmlElement:
        """Renderizza un campo con label ed errori"""
        if field_name not in self.fields:
            raise ValueError(f"Field '{field_name}' not found")
        
        field = self.fields[field_name]
        field_html = field.render(field_name)
        
        content = []
        
        # Label
        if label:
            label_element = Label(label, **{'for': field_name}, classes=[CSSClasses.FORM_LABEL])
            content.append(label_element)
        
        # Campo
        content.append(field_html)
        
        # Errori
        field_errors = self.get_field_errors(field_name)
        if field_errors:
            for error in field_errors:
                error_div = Div(error, classes=["invalid-feedback"])
                content.append(error_div)
        
        return Div(content, classes=[CSSClasses.MB_3])
    
    def render_form(self, action="/", method="POST", submit_text="Submit") -> HtmlElement:
        """Renderizza l'intero form"""
        form_content = []
        
        # Errori globali
        global_errors = self.get_form_errors()
        if global_errors:
            for error in global_errors:
                alert = Div([
                    error
                ], classes=[CSSClasses.ALERT, CSSClasses.ALERT_DANGER])
                form_content.append(alert)
        
        # Campi
        for field_name in self.fields.keys():
            # Crea label dal nome del campo (capitalizza e sostituisce underscore)
            label = field_name.replace('_', ' ').title()
            field_html = self.render_field(field_name, label)
            form_content.append(field_html)
        
        # Bottone submit
        submit_btn = Button(submit_text, 
                           button_type="submit", 
                           classes=[CSSClasses.BTN, CSSClasses.BTN_PRIMARY])
        form_content.append(submit_btn)
        
        return Form(form_content, action=action, method=method)


# Validatori comuni
def min_length(min_len: int):
    """Validatore lunghezza minima"""
    def validator(value):
        if value and len(value) < min_len:
            raise ValidationError(f"Minimum length is {min_len} characters")
    return validator


def max_length(max_len: int):
    """Validatore lunghezza massima"""
    def validator(value):
        if value and len(value) > max_len:
            raise ValidationError(f"Maximum length is {max_len} characters")
    return validator


def email_validator(value):
    """Validatore email"""
    if value:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise ValidationError("Invalid email format")


def phone_validator(value):
    """Validatore telefono (formato semplice)"""
    if value:
        phone_pattern = r'^\+?[\d\s\-\(\)]{8,15}$'
        if not re.match(phone_pattern, value.replace(' ', '')):
            raise ValidationError("Invalid phone number format")


def url_validator(value):
    """Validatore URL"""
    if value:
        url_pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w._~!$&\'()*+,;=:@]|%[\dA-F]{2})*)*(?:\?(?:[\w._~!$&\'()*+,;=:@/?]|%[\dA-F]{2})*)?(?:#(?:[\w._~!$&\'()*+,;=:@/?]|%[\dA-F]{2})*)?$'
        if not re.match(url_pattern, value, re.IGNORECASE):
            raise ValidationError("Invalid URL format")


def custom_validator(func: Callable):
    """Wrapper per validatori personalizzati"""
    def validator(value):
        try:
            func(value)
        except Exception as e:
            raise ValidationError(str(e))
    return validator
