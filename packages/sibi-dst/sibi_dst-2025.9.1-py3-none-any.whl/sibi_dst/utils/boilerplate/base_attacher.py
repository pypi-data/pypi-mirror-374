from typing import Any, Awaitable, Callable, Sequence, Type

def make_attacher(
    cube_cls: Type,
    fieldnames: Sequence[str],
    column_names: Sequence[str],
) -> Callable[..., Awaitable[Any]]:
    """
    Factory for async attachers.
    Skips work if any param value is falsy ([], None, {}, etc.).
    """

    async def attach(*, logger=None, debug: bool = False, **params: Any):
        if any(not v for v in params.values()):
            return None
        call_params = {
            "fieldnames": tuple(fieldnames),
            "column_names": list(column_names),
            **params,
        }
        return await cube_cls(logger=logger, debug=debug).aload(**call_params)

    return attach

__all__ = ['make_attacher']