import typing

import gremlin_python.process.graph_traversal
import pydantic

from ...utils import T, use_default_when_none
from ...utils.run_utils import run_function_in_threadpool
from ..generic.column import UNSET, GenericColumn, _Unset
from .exceptions import GremlinMissingSessionException

if typing.TYPE_CHECKING:
    from .model import GremlinModel

__all__ = ["GremlinColumn", "GremlinRelationship"]


class OnBeforeCreateParams(typing.TypedDict):
    session: gremlin_python.process.graph_traversal.GraphTraversalSource
    source: str
    target: str
    edge_name: str
    properties: dict[str, typing.Any] | None


class GremlinColumn(GenericColumn[T]):
    label_key = False
    lazy = True

    def __init__(
        self,
        col_type: typing.Type[T],
        *,
        primary_key: bool = False,
        auto_increment: bool = False,
        unique: bool = False,
        nullable: bool = True,
        label_key: bool = False,
        lazy: bool = True,
        default: T
        | typing.Callable[[], T]
        | typing.Callable[["GremlinModel"], T]
        | _Unset = UNSET,
    ):
        """
        Initializes a GenericColumn instance.

        Args:
            col_type (typing.Type[T]): The type of the column.
            primary_key (bool, optional): Whether the column is a primary key. Defaults to False.
            auto_increment (bool, optional): Whether the column is auto incremented. Only works if the column is a primary key. Defaults to False.
            unique (bool, optional): Whether the column is unique. Defaults to False.
            nullable (bool, optional): Whether the column is nullable. Defaults to True.
            label_key (bool, optional): Whether the column is a label key. If True, the column will be used as the label key in the Gremlin graph. Defaults to False.
            lazy (bool, optional): Whether the column should be lazy loaded when accessed. Defaults to True.
            default (T | typing.Callable[[], T] | typing.Callable[["GenericModel"], T] | _NoDefaultValue, optional): The default value of the column. Will be used if the column is not set by the user. Defaults to UNSET (no default value).

        Raises:
            GenericColumnException: If auto increment is set on a non-primary key column or if the column type is not int when auto increment is set.
            GenericColumnException: If auto increment is set on a non-integer column type.
        """
        self.label_key = label_key
        self.lazy = lazy
        super().__init__(
            col_type,
            primary_key=primary_key,
            auto_increment=auto_increment,
            unique=unique,
            nullable=nullable,
            default=default,
        )

    def __get__(
        self,
        instance: typing.Optional["GremlinModel"],
        owner: typing.Type["GremlinModel"],
    ):
        if (
            instance
            and instance.__table__
            and self.lazy
            and not self.is_column_set(instance)
            and not self.is_lazy_loaded(instance)
        ):
            self.set_lazy_loaded(instance, True)
            self.lazy_load(instance)
        return super().__get__(instance, owner)

    def is_lazy_loaded(self, instance: "GremlinModel"):
        """
        Checks if the column has been lazy loaded.

        Args:
            instance (GremlinModel): The instance of the model.

        Returns:
            bool: True if the column has been lazy loaded, False otherwise.
        """
        return f"_lazy_{self._col_name}" in instance.__dict__

    def set_lazy_loaded(self, instance: "GremlinModel", value: bool):
        """
        Sets the lazy loaded state of the column.

        Args:
            instance (GremlinModel): The instance of the model.
            value (bool): The lazy loaded state to set.
        """
        if value:
            instance.__dict__[f"_lazy_{self._col_name}"] = value
        else:
            instance.__dict__.pop(f"_lazy_{self._col_name}", None)

    def lazy_load(self, instance: "GremlinModel"):
        """
        Lazy loads the column value from the database and sets it on the instance.

        Args:
            instance (GremlinModel): The instance of the model.
        """
        if not instance.__session__:
            raise GremlinMissingSessionException(
                instance.__class__.__name__,
                f"Cannot lazy load column '{self._col_name}' without an active session.",
            )
        statement = instance.__session__.V(instance.get_pk()).values(self._col_name)
        self.logger.debug(
            f"{instance.__class__.__name__}: Lazy loading column '{self._col_name}', statement: {statement}"
        )
        exists = run_function_in_threadpool(statement.hasNext)
        if exists:
            value = run_function_in_threadpool(statement.next)
            setattr(instance, self._col_name, value)


class GremlinRelationship(GremlinColumn[T]):
    """
    A column that represents a relation in Gremlin.
    """

    name: str | None = None
    properties: dict[str, typing.Any] | None = None
    direction: typing.Literal["in", "out", "both"] = "out"
    uselist = False
    with_edge = False
    obj: typing.Type["GremlinModel"] | str | None = None
    obj_properties: dict[str, typing.Any] | None = None
    on_before_create: (
        typing.Callable[
            ["GremlinModel", "GremlinModel", OnBeforeCreateParams],
            None | dict[str, typing.Any],
        ]
        | None
    ) = None

    def __init__(
        self,
        col_type: typing.Type[T],
        *,
        name: str | None = None,
        properties: dict[str, typing.Any] | None = None,
        direction: typing.Literal["in", "out", "both"] = "out",
        uselist=False,
        with_edge=False,
        obj: typing.Type["GremlinModel"] | str | None = None,
        obj_properties: dict[str, typing.Any] | None = None,
        nullable: bool = True,
        lazy: bool = True,
        default: T
        | typing.Callable[[], T]
        | typing.Callable[["GremlinModel"], T]
        | _Unset = UNSET,
        on_before_create: typing.Callable[
            ["GremlinModel", "GremlinModel", OnBeforeCreateParams],
            None
            | dict[str, typing.Any]
            | typing.Coroutine[None, None, dict[str, typing.Any] | None],
        ]
        | None = None,
    ):
        """
        Initializes a GenericColumn instance.

        Args:
            col_type (typing.Type[T]): The type of the column.
            name (str | None, optional): The edge name of the relation. Defaults to None.
            properties (dict[str, typing.Any] | None, optional): Additional properties to filter the edge of the relation. Defaults to None.
            direction (typing.Literal["in", "out", "both"], optional): The direction of the relation. Use "in" for incoming relations and "out" for outgoing relations or "both" for both directions. Defaults to "out".
            uselist (bool, optional): Whether the relation is a list. Defaults to False.
            with_edge (bool, optional): Whether to return the edge properties along with the related vertex. If True, the column will return a dictionary with two keys: "edge" and the property name. When `obj` is set, the related object needs to have an `edge` property to hold the edge properties. Defaults to False.
            obj (typing.Type["GremlinModel"] | str | None, optional): The model class that this relation points to. To handle relation to itself, use `typing.Self`. To use a simple dictionary, gives nothing. Defaults to None.
            obj_properties (dict[str, typing.Any] | None, optional): Additional properties to filter the related vertex of the relation. Defaults to None.
            nullable (bool, optional): Whether the column is nullable. Defaults to True.
            lazy (bool, optional): Whether the column should be lazy loaded when accessed. Defaults to True.
            default (T | typing.Callable[[], T] | typing.Callable[["GenericModel"], T] | _NoDefaultValue, optional): The default value of the column. Will be used if the column is not set by the user. Defaults to UNSET (no default value).
            on_before_create (typing.Callable[["GremlinModel", "GremlinModel", OnBeforeCreateParams], None | dict[str, typing.Any]] | typing.Coroutine[None, None, dict[str, typing.Any] | None], optional): A callback function to be called before creating the relation. It receives the source model, target model, and a dictionary with parameters for creating the edge. The function can return a dictionary with additional properties to set on the edge or None. Defaults to None.

        Raises:
            GenericColumnException: If auto increment is set on a non-primary key column or if the column type is not int when auto increment is set.
            GenericColumnException: If auto increment is set on a non-integer column type.
        """
        self.name = name
        self.properties = properties
        self.direction = direction
        self.uselist = uselist
        self.with_edge = with_edge
        self.obj = obj
        self.obj_properties = obj_properties
        self.lazy = lazy
        self.on_before_create = on_before_create
        if uselist:
            if col_type is not list:
                raise TypeError(
                    "The col_type of a GremlinRelationship with uselist=True must be `list`."
                )
        else:
            if col_type is not typing.Any:
                raise TypeError(
                    "The col_type of a GremlinRelationship with uselist=False must be `typing.Any`."
                )
        super().__init__(
            col_type,
            primary_key=False,
            auto_increment=False,
            unique=False,
            nullable=nullable,
            label_key=False,
            default=default,
        )

    def __set_name__(self, owner, name):
        from .model import GremlinModel

        if self.obj is typing.Self:
            self.obj = owner
            if self.uselist:
                if issubclass(self.obj, GremlinModel):
                    self.col_type = (
                        self.col_type
                        | typing.Annotated[
                            list[self.obj],
                            pydantic.AfterValidator(
                                lambda values: [v.to_json() for v in values]
                                if values
                                else values
                            ),
                        ]
                    )
                else:
                    self.col_type = self.col_type | list[self.obj]
            else:
                if issubclass(self.obj, GremlinModel):
                    self.col_type = (
                        self.col_type
                        | typing.Annotated[
                            self.obj,
                            pydantic.AfterValidator(lambda v: v.to_json()),
                        ]
                    )
                else:
                    self.col_type = self.col_type | self.obj
        elif isinstance(self.obj, type) and issubclass(self.obj, GremlinModel):
            self.obj_properties = use_default_when_none(
                self.obj_properties, self.obj.__properties__
            )
        elif isinstance(self.obj, str):
            GremlinModel._register_model_callback(
                self.obj,
                lambda model: setattr(self, "obj", model),
            )
            GremlinModel._register_model_callback(
                self.obj,
                lambda model: setattr(
                    self,
                    "obj_properties",
                    use_default_when_none(self.obj_properties, model.__properties__),
                ),
            )

        return super().__set_name__(owner, name)

    def build_statement(
        self,
        statement: gremlin_python.process.graph_traversal.GraphTraversal,
        columns: list[str] | None = None,
    ):
        """
        Builds the Gremlin statement to fetch the related vertices.

        Args:
            statement (gremlin_python.process.graph_traversal.GraphTraversal): The initial Gremlin statement.
            columns (list[str] | None, optional): The columns to fetch from the related vertices. If None, all columns will be fetched. Defaults to None.

        Returns:
            gremlin_python.process.graph_traversal.GraphTraversal: The modified Gremlin statement.
        """
        current_statement = statement
        match self.direction:
            case "in":
                current_statement = current_statement.inE
            case "out":
                current_statement = current_statement.outE
            case "both":
                current_statement = current_statement.bothE
        if self.name:
            current_statement = current_statement(self.name)
        else:
            current_statement = current_statement()
        if self.properties:
            for key, value in self.properties.items():
                current_statement = current_statement.has(key, value)
        sub_other_v_statement = (
            current_statement.otherV()
            if not self.with_edge
            else gremlin_python.process.graph_traversal.__.otherV()
        )
        if self.obj_properties:
            for key, value in self.obj_properties.items():
                sub_other_v_statement = sub_other_v_statement.has(key, value)
        sub_other_v_statement = sub_other_v_statement.valueMap(True, *(columns or []))
        if self.with_edge:
            current_statement = (
                current_statement.project("edge", self._col_name)
                .by(gremlin_python.process.graph_traversal.__.valueMap(True))
                .by(sub_other_v_statement)
            )
        else:
            current_statement = sub_other_v_statement
        return current_statement

    def lazy_load(self, instance):
        if not instance.__session__:
            raise GremlinMissingSessionException(
                instance.__class__.__name__,
                f"Cannot lazy load relationship '{self._col_name}' without an active session.",
            )
        statement = instance.__session__.V(instance.get_pk())
        statement = self.build_statement(statement)
        self.logger.debug(
            f"{instance.__class__.__name__}: Lazy loading relationship '{self._col_name}', statement: {statement}"
        )
        result = run_function_in_threadpool(statement.toList)
        result = self.from_gremlinpython(instance, result)
        setattr(instance, self._col_name, result)

    def from_gremlinpython(
        self,
        model: typing.Type["GremlinModel"] | "GremlinModel",
        value: typing.Any,
        *,
        as_json=False,
    ) -> T:
        """
        Converts the value returned from Gremlin Python to the appropriate type.

        Args:
            model (typing.Type[&quot;GremlinModel&quot;] | &quot;GremlinModel&quot;): The model class or instance to use for conversion.
            value (typing.Any): The value to convert.
            as_json (bool, optional): Whether to return the value as a JSON-serializable dictionary. Defaults to False.

        Returns:
            T: The converted value.
        """
        if self.uselist:
            value = value if isinstance(value, list) else [value]
        else:
            value = value[0] if isinstance(value, list) and value else None
        if value is None:
            return value
        if self.obj and not as_json:
            value = (
                [
                    self._handle_data_conversion(val, session=model.__session__)
                    for val in value
                ]
                if self.uselist
                else self._handle_data_conversion(value, session=model.__session__)
            )
        else:
            value = (
                [model.parse_from_gremlinpython(val) for val in value]
                if self.uselist
                else model.parse_from_gremlinpython(value)
            )
        return value

    def _handle_data_conversion(
        self,
        data: dict[str, typing.Any],
        *,
        session: gremlin_python.process.graph_traversal.GraphTraversalSource
        | None = None,
    ):
        """
        Handles the conversion of data from Gremlin Python to the appropriate model instance.

        Args:
            data (dict[str, typing.Any]): The data to convert.
            session (gremlin_python.process.graph_traversal.GraphTraversalSource | None, optional): The active Gremlin session. Required if the related model has lazy-loaded columns. Defaults to None.

        Returns:
            GremlinModel: The converted model instance.
        """
        if self.with_edge:
            data = {**data[self._col_name], "edge": data["edge"]}
        for col in [
            x
            for x in self.obj.__mapper__.columns
            if x != self.obj.__mapper__.pk and x != self.obj.__mapper__.lk
        ]:
            # TODO: Handle lazy loading for relationship attributes, since if the attribute is not in the database, it will try to lazy load it again, even after fetched, right now we ensure everything is loaded, but next time, if partial selected in list_columns, use that instead
            if col not in data:
                data[col] = None
        return self.obj.from_gremlinpython(
            data,
            preserve_as_list=[self._col_name] if self.uselist else None,
            session=session,
        )
