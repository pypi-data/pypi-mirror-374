"""Async helper functions."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Any, Callable

executor = ThreadPoolExecutor()


async def to_async(func: Callable[..., Any], *args: Any, **kwargs: dict[str, Any]) -> Any:  # noqa: ANN401
    """Run a blocking function in an async context using ThreadPoolExecutor.

    Args:
        func: The blocking function to run.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    """
    loop = asyncio.get_event_loop()
    func_with_args = partial(func, *args, **kwargs)
    return await loop.run_in_executor(executor, func_with_args)
