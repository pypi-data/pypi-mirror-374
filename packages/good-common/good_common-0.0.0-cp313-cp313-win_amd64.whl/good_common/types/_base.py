from importlib import import_module
from typing import Any, Callable, Annotated, TYPE_CHECKING

from pydantic import GetCoreSchemaHandler, BeforeValidator
from pydantic_core import CoreSchema, core_schema

type StringDict = dict[str, str]

# Lazy import to avoid circular dependency at module level
def _get_identifier_base():
    """Get the Identifier base class (URL) lazily."""
    from .web import URL
    return URL


if TYPE_CHECKING:
    from .web import URL
    
    class Identifier(URL):
        """Type checking version of Identifier."""
        pass
else:
    # Runtime version with lazy import
    class Identifier:
        """
        Identifier type that lazily inherits from URL.
        """
        _url_class = None
        
        def __new__(cls, url: Any, strict: bool = False):
            # Lazy import URL
            if cls._url_class is None:
                from .web import URL
                cls._url_class = URL
            
            URL = cls._url_class
            
            if isinstance(url, URL):
                _url = url
            else:
                _url = URL(url)

            # Create URL instance with id scheme
            instance = URL.build(
                scheme="id",
                username=_url.username,
                password=_url.password,
                host=_url.host_root.lower(),
                path=_url.path.rstrip("/"),
                query=_url.query_params("flat"),
            )
            
            # Add custom methods
            original_root = instance.root if hasattr(instance, 'root') else None
            
            # Override root property
            def get_root():
                return URL(instance).update(
                    query={
                        k: v
                        for k, v in instance.query_params("flat").items()
                        if not k.startswith("zz_")
                    }
                )
            
            instance.root = property(lambda self: get_root())
            instance.domain = instance.host
            
            return instance


class PythonImportableObjectType(str):
    """
    function or class
    """
    
    _path: str
    _func: str

    def __new__(cls, obj: Any):
        # if
        if not isinstance(obj, str):
            if hasattr(obj, "__module__") and hasattr(obj, "__name__"):
                obj = f"{obj.__module__}:{obj.__name__}"
            else:
                raise ValueError(f"Cannot convert {obj} to PythonImportableObject")
        instance = super().__new__(cls, obj)
        if ":" in obj:
            instance._path, instance._func = obj.rsplit(":", 1)
        else:
            instance._path, instance._func = obj.rsplit(".", 1)
        return instance

    def resolve(self) -> Callable:
        module = import_module(self._path)
        return getattr(module, self._func)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))


PythonImportableObject = Annotated[
    PythonImportableObjectType,
    BeforeValidator(
        lambda x: PythonImportableObjectType(x), json_schema_input_type=str
    ),
]