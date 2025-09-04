from contextlib import AsyncExitStack
from functools import partial
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Container,
    Dict,
    Iterable,
    Optional,
    Type,
    Union,
)

from typemapping import VarTypeInfo, get_func_args, get_return_type

if TYPE_CHECKING:
    from ctxinject.overrides import Provider

from ctxinject.model import CallableInjectable, CastType, Injectable, ModelFieldInject
from ctxinject.resolvers import (
    BaseResolver,
    DefaultResolver,
    DependsResolver,
    ModelFieldResolver,
    NameResolver,
    TypeResolver,
    ValidateResolver,
)
from ctxinject.runner import run_async_tasks
from ctxinject.validation import get_validator


class UnresolvedInjectableError(Exception):
    """
    Raised when a dependency cannot be resolved in the injection context.

    This exception is thrown when:
    - A required argument has no corresponding value in the context
    - A type cannot be found in the context
    - A model field injection fails to resolve
    - allow_incomplete=False and some dependencies are missing
    """

    ...


def inject_validate(
    value: BaseResolver,
    instance: Optional[Injectable],
    from_type: Optional[Type[Any]],
    bt: Optional[Type[Any]],
) -> BaseResolver:
    if instance is not None:
        if not instance.has_validate:
            instance._validator = get_validator(from_type, bt)  # type: ignore
        if instance.has_validate:
            value = ValidateResolver(
                func=value,
                instance=instance,
                bt=bt,  # type: ignore
            )
    return value


def map_ctx(
    args: Iterable[VarTypeInfo],
    context: Container[Union[str, Type[Any]]],
    allow_incomplete: bool,
    validate: bool = True,
    overrides: Optional[Dict[Callable[..., Any], Callable[..., Any]]] = None,
    enable_async_model_field: bool = False,
    ordered: bool = False,
) -> Dict[str, Any]:
    ctx: Dict[str, Any] = {}
    overrides = overrides or {}

    for arg in args:
        instance = arg.getinstance(Injectable)
        default_ = instance.default if instance else None
        bt = arg.basetype
        from_type = arg.basetype
        value: Optional[BaseResolver] = None

        # resolve dependencies
        if isinstance(instance, CallableInjectable):

            dep_func = overrides.get(instance.default, instance.default)
            dep_ctx_map = get_mapped_ctx(
                func=dep_func,
                context=context,
                allow_incomplete=allow_incomplete,
                validate=validate,
                overrides=overrides,
                ordered=ordered,
            )
            value = DependsResolver(
                dep_func,
                dep_ctx_map,
                resolve_mapped_ctx,
                instance.order,
            )
            from_type = get_return_type(dep_func)
        # by name
        elif arg.name in context:
            value = NameResolver(
                arg_name=arg.name,
            )
            if isinstance(instance, CastType):
                from_type = instance.from_type
        # by model field/method
        elif isinstance(instance, ModelFieldInject):
            tgtmodel = instance.model
            tgt_field = instance.field or arg.name
            modeltype = instance.get_nested_field_type(tgt_field)
            if tgtmodel in context and (modeltype or enable_async_model_field):
                from_type = modeltype
                value = ModelFieldResolver(
                    model_type=tgtmodel,
                    field_name=tgt_field,
                    async_model_field=enable_async_model_field,
                )
        # by type
        elif value is None and bt is not None and bt in context:
            from_type = bt
            value = TypeResolver(target_type=bt)
        # by default
        elif value is None and default_ is not None and default_ is not Ellipsis:
            from_type = type(default_)
            value = DefaultResolver(
                default_value=default_,
            )

        if value is None and not allow_incomplete:
            raise UnresolvedInjectableError(
                f"Argument '{arg.name}' is incomplete or missing a valid injectable context."
            )
        if value is not None:
            if validate:
                value = inject_validate(value, instance, from_type, bt)

            ctx[arg.name] = value

    return ctx


def get_mapped_ctx(
    func: Callable[..., Any],
    context: Container[Union[str, Type[Any]]],
    allow_incomplete: bool = True,
    validate: bool = True,
    overrides: Optional[Dict[Callable[..., Any], Callable[..., Any]]] = None,
    enable_async_model_field: bool = False,
    ordered: bool = False,
) -> Iterable[Dict[str, Any]]:
    """
    Get mapped context with resolver wrappers for a function (standard version).

    This function analyzes a function's signature and creates a mapping of
    parameter names to their corresponding resolvers based on the injection context.
    For optimized pre-computed ordering, use order=True.

    Args:
        func: The function to analyze and create resolvers for
        context: Injection context containing values, types, and model instances
        allow_incomplete: Whether to allow missing dependencies (default: True)
        validate: Whether to apply validation if defined (default: True)
        overrides: Optional mapping to override dependency functions
        enable_async_model_field: Whether to enable async model field injection

    Returns:
        Dictionary mapping parameter names to their resolvers

    Raises:
        UnresolvedInjectableError: When allow_incomplete=False and dependencies are missing

    Example:
        ```python
        def my_func(name: str, count: int = ArgsInjectable(42)):
            return f"{name}: {count}"

        context = {"name": "test", int: 100}
        mapped = get_mapped_ctx(my_func, context)

        # mapped contains resolvers for 'name' and 'count' parameters
        # You can then use resolve_mapped_ctx() to get actual values
        ```

    Note:
        This is typically used internally by inject_args(), but can be useful
        for advanced scenarios where you need to inspect or modify the resolution
        process before executing it. For maximum performance with pre-computed
        ordering, consider using the ordered variants.
    """
    funcargs = get_func_args(func)
    mapped_ctx = map_ctx(
        args=funcargs,
        context=context,
        allow_incomplete=allow_incomplete,
        validate=validate,
        overrides=overrides,
        enable_async_model_field=enable_async_model_field,
        ordered=ordered,
    )
    return sort_mapped_ctx(mapped_ctx) if ordered else [mapped_ctx]


def sort_mapped_ctx(
    mapped_ctx: Dict[str, "BaseResolver"],
) -> Iterable[Dict[str, "BaseResolver"]]:
    batches: Dict[int, Dict[str, "BaseResolver"]] = {}
    for key, resolver in mapped_ctx.items():
        batches.setdefault(resolver.order, {})[key] = resolver
    return [batch for _, batch in sorted(batches.items())]


async def inject_args(
    func: Callable[..., Any],
    context: Union[Dict[Union[str, Type[Any]], Any], Any],
    allow_incomplete: bool = True,
    validate: bool = True,
    overrides: Optional[
        Union[Dict[Callable[..., Any], Callable[..., Any]], "Provider"]
    ] = None,
    use_global_provider: bool = False,
    stack: Optional[AsyncExitStack] = None,
    enable_async_model_field: bool = False,
    ordered: bool = True,
) -> Callable[..., Any]:
    """
    Inject arguments into function with dependency injection and optional ordering optimization.

    This is the main entry point for dependency injection. It analyzes a function's
    signature, resolves dependencies from the provided context, and returns a
    partially applied function with those dependencies injected.

    Args:
        func: The target function to inject dependencies into
        context: Dictionary containing injectable values:
            - By name: {"param_name": value}
            - By type: {SomeClass: instance}
            - Model instances for ModelFieldInject
        allow_incomplete: If True, allows missing dependencies (they remain as parameters).
                         If False, raises UnresolvedInjectableError for missing deps.
        validate: Whether to apply validation functions defined in injectable annotations
        overrides: Dependency overrides - can be:
                  - Dict mapping original functions to replacements (legacy)
                  - Provider instance for advanced override management
        use_global_provider: Whether to use the global provider for overrides
        stack: Optional AsyncExitStack for context managers
        enable_async_model_field: Whether to enable async model field injection
        ordered: If True, uses optimized execution with pre-computed sync/async separation
                and order-based batching for maximum performance (default: False)

    Returns:
        A functools.partial object with resolved dependencies pre-filled.
        The returned function has a reduced signature containing only unresolved parameters.

    Raises:
        UnresolvedInjectableError: When allow_incomplete=False and required dependencies
                                 cannot be resolved from context
        ValidationError: When validate=True and a validator rejects a value

    Examples:
        Basic injection by name and type:
        ```python
        from typing_extensions import Annotated
        from ctxinject.inject import inject_args
        from ctxinject.model import ArgsInjectable

        def greet(name: str, count: int = ArgsInjectable(1)):
            return f"Hello {name}! (x{count})"

        context = {"name": "Alice", int: 5}
        injected = await inject_args(greet, context)
        result = injected()  # "Hello Alice! (x5)"
        ```

        Optimized injection with ordering:
        ```python
        # Use ordered=True for maximum performance
        injected = await inject_args(greet, context, ordered=True)
        result = injected()  # Same result, optimized execution
        ```

        Async dependency functions with ordering:
        ```python
        async def get_user_service() -> UserService:
            return await UserService.create()

        def handle_request(
            service: UserService = DependsInject(get_user_service, order=1)
        ):
            return service.get_current_user()

        context = {}  # Dependencies resolved automatically
        injected = await inject_args(handle_request, context, ordered=True)
        result = injected()
        ```

    Performance Notes:
        - Standard mode: Uses isinstance() checks to separate sync and async resolvers
        - Ordered mode (ordered=True): Pre-computes sync/async separation and ordering
          for maximum runtime performance, eliminates isinstance checks
        - Async dependencies are resolved concurrently for maximum performance
        - Supports chaining multiple injections on the same function
        - Name-based injection takes precedence over type-based injection
        - Recursive dependencies automatically use the same execution strategy
    """
    # Resolve final overrides from provider or legacy parameter
    from ctxinject.overrides import Provider, resolve_overrides

    if overrides is None or isinstance(overrides, Provider):
        # No overrides provided, just use global if enabled
        resolved_overrides = resolve_overrides(
            local_provider=None, use_global=use_global_provider
        )
    elif isinstance(overrides, dict):
        # Legacy dict format - convert to resolved format
        global_overrides = (
            resolve_overrides(local_provider=None, use_global=use_global_provider)
            if use_global_provider
            else {}
        )
        resolved_overrides = {**global_overrides, **overrides}
    else:
        raise TypeError(f"overrides must be Dict or Provider, got {type(overrides)}")

    if not isinstance(context, dict):
        context = {type(context): context}
    context_list = list(context.keys())

    mapped_ctx = get_mapped_ctx(
        func=func,
        context=context_list,
        allow_incomplete=allow_incomplete,
        validate=validate,
        overrides=resolved_overrides,
        enable_async_model_field=enable_async_model_field,
        ordered=ordered,
    )
    resolved = await resolve_mapped_ctx(context, mapped_ctx, stack)
    return partial(func, **resolved)


async def resolve_mapped_ctx(
    input_ctx: Dict[Union[str, Type[Any]], Any],
    mapped_ctx: Iterable[Dict[str, BaseResolver]],
    stack: Optional[AsyncExitStack] = None,
) -> Dict[Any, Any]:

    if not mapped_ctx:
        return {}

    results = {}

    for resolvers in mapped_ctx:
        async_keys = []
        async_tasks = []
        for key, resolver in resolvers.items():

            try:
                result = resolver(input_ctx, stack)
                results[key] = result
                if resolver.isasync:
                    async_keys.append(key)
                    async_tasks.append(result)
            except Exception:
                raise
        if async_tasks:
            if len(async_tasks) == 1:
                key, task = async_keys[0], async_tasks[0]
                results[key] = await task
            else:
                await run_async_tasks(
                    async_tasks=async_tasks, async_keys=async_keys, results=results
                )
    return results
