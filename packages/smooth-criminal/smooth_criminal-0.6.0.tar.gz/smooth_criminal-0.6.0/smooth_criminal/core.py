import statistics
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import inspect
import ast
import sys
import os
import random

from numba import jit, vectorize as nb_vectorize, guvectorize as nb_guvectorize
import numpy as np
import asyncio
import logging
import time
from functools import wraps
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    ParamSpec,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    overload,
    Literal,
)

from smooth_criminal import memory
from smooth_criminal.memory import log_execution_stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SmoothCriminal")

# Flag global para activar efectos de MJ
MJ_MODE = False

# Almacena las funciones que ya han "entusiasmado" los benchmarks para evitar
# mensajes repetidos de mejora significativa.
_THRILLER_ANNOUNCED: set[str] = set()


def set_mj_mode(enabled: bool) -> None:
    """Activa o desactiva el modo MJ.

    Parameters
    ----------
    enabled:
        Si ``True`` se habilitan los efectos especiales al detectar mejoras de
        rendimiento.
    """

    global MJ_MODE
    MJ_MODE = enabled


def play_mj_effect(improvement: float, mj_mode: bool | None = None, *, threshold: float = 10.0) -> None:
    """Reproduce un efecto especial al mejorar el rendimiento.

    Intenta reproducir un sonido usando :mod:`playsound`.  Si no está
    disponible o falla, muestra un mensaje/ASCII mediante ``rich``.

    Parameters
    ----------
    improvement:
        Porcentaje de mejora obtenida.
    mj_mode:
        Permite forzar el modo MJ de forma explícita.  Si es ``None`` se usa el
        valor global establecido por :func:`set_mj_mode`.
    threshold:
        Porcentaje mínimo de mejora para activar el efecto.
    """

    active = MJ_MODE if mj_mode is None else mj_mode
    if not active or improvement < threshold:
        return

    try:
        from playsound import playsound  # type: ignore

        audio_path = os.path.join(os.path.dirname(__file__), "mj.mp3")
        playsound(audio_path)
        return
    except Exception as exc:  # pragma: no cover - dependencias opcionales
        logger.warning("No se pudo reproducir audio MJ: %s", exc)

    try:
        from rich.console import Console

        console = Console()
        console.print(
            f"[bold magenta]Hee-hee! Mejora de {improvement:.1f}%[/bold magenta]"
        )
    except Exception as exc:  # pragma: no cover - dependencias opcionales
        logger.warning("No se pudo mostrar efecto MJ: %s", exc)

T = TypeVar("T")
A = TypeVar("A")
P = ParamSpec("P")


def mj_mode(func: Callable[P, T]) -> Callable[P, T]:
    """Aplica al azar un decorador icónico de MJ y muestra un mensaje."""

    options = [
        (smooth, "🕺 Hee-Hee! You're now smooth."),
        (bad(), "😎 Who's bad? You're bad!"),
        (thriller, "🎬 It's Thriller time!"),
        (jam(workers=4), "🥁 Jam session with 4 workers!"),
    ]

    decorator, message = random.choice(options)
    logger.info(message)
    return decorator(func)


def _process_worker(module_name: str, func_name: str, q) -> List[T]:
    from queue import Empty
    import importlib

    module = importlib.import_module(module_name)
    func: Callable[[A], T] = getattr(module, func_name)

    local_results: List[T] = []
    while True:
        try:
            arg = q.get_nowait()
        except Empty:
            break
        try:
            local_results.append(func(arg))
        except Exception as e:
            logger.warning(f"Worker failed on input {arg}: {e}")
    return local_results

def smooth(func: Callable[P, T]) -> Callable[P, T]:
    """Compila ``func`` con Numba para acelerar su ejecución.

    Ejemplo
    -------
    >>> import logging
    >>> logging.getLogger("SmoothCriminal").setLevel(logging.CRITICAL)
    >>> @smooth
    ... def suma(a: int, b: int) -> int:
    ...     return a + b
    >>> suma(2, 3)
    5
    """
    try:
        jit_func = jit(nopython=True, cache=True)(func)

        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            logger.info("You've been hit by... a Smooth Criminal!")
            try:
                return jit_func(*args, **kwargs)
            except Exception:
                logger.warning("Beat it! Numba failed at runtime. Falling back.")
                return func(*args, **kwargs)

        return wrapper
    except Exception:
        def fallback(*args: P.args, **kwargs: P.kwargs) -> T:
            logger.warning("Beat it! Numba failed. Falling back.")
            return func(*args, **kwargs)

        return fallback


def vectorized(ftylist_or_function=(), **kws):
    """Envuelve ``numba.vectorize`` añadiendo registro y *fallback*.

    Parametros
    ----------
    ftylist_or_function : sequence or function, optional
        Igual que en :func:`numba.vectorize`.
    **kws : Any
        Argumentos adicionales para ``numba.vectorize``.
    """

    if callable(ftylist_or_function):
        func = ftylist_or_function
        signatures = ()
    else:
        func = None
        signatures = ftylist_or_function

    def _compile(f: Callable):
        try:
            jit_func = nb_vectorize(signatures, **kws)(f)

            @wraps(f)
            def wrapper(*args, **kwargs):
                logger.info("Vectorization... that's smooth!")
                try:
                    return jit_func(*args, **kwargs)
                except Exception:
                    logger.warning(
                        "Beat it! Numba vectorize failed at runtime. Falling back."
                    )
                    return f(*args, **kwargs)

            return wrapper
        except Exception:
            logger.warning("Beat it! Numba vectorize failed. Falling back.")
            return f

    if func is not None:
        return _compile(func)

    def decorator(f: Callable):
        return _compile(f)

    return decorator


def guvectorized(*args, **kws):
    """Envuelve ``numba.guvectorize`` añadiendo registro y *fallback*."""

    if args and callable(args[0]):
        func = args[0]
        sig_args = ()
    else:
        func = None
        sig_args = args

    def _compile(f: Callable):
        try:
            jit_func = nb_guvectorize(*sig_args, **kws)(f)

            @wraps(f)
            def wrapper(*w_args, **w_kwargs):
                logger.info("GUVectorization in the groove!")
                try:
                    return jit_func(*w_args, **w_kwargs)
                except Exception:
                    logger.warning(
                        "Beat it! Numba guvectorize failed at runtime. Falling back."
                    )
                    return f(*w_args, **w_kwargs)

            return wrapper
        except Exception:
            logger.warning("Beat it! Numba guvectorize failed. Falling back.")
            return f

    if func is not None:
        return _compile(func)

    def decorator(f: Callable):
        return _compile(f)

    return decorator

@overload
def moonwalk(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]: ...


@overload
def moonwalk(func: Callable[P, T]) -> Callable[P, Awaitable[T]]: ...


def moonwalk(func: Callable[P, Any]) -> Callable[P, Awaitable[T]]:
    """Permite ejecutar funciones sincrónicas o asíncronas de forma asíncrona.

    Ejemplos
    --------
    >>> import asyncio, logging
    >>> logging.getLogger("SmoothCriminal").setLevel(logging.CRITICAL)
    >>> @moonwalk
    ... async def saludar(nombre: str) -> str:
    ...     return f"Hola {nombre}"
    >>> asyncio.run(saludar("Ana"))
    'Hola Ana'
    >>> @moonwalk
    ... def doble(x: int) -> int:
    ...     return x * 2
    >>> asyncio.run(doble(3))
    6
    """

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        logger.info("Moonwalk complete — your async function is now gliding!")

        if inspect.iscoroutinefunction(func):
            return await func(*args, **kwargs)

        if hasattr(asyncio, "to_thread"):
            return await asyncio.to_thread(func, *args, **kwargs)

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)

    return wrapper

def thriller(func: Callable[P, T]) -> Callable[P, T]:
    """Cronometra la ejecución de ``func`` y registra el tiempo empleado.

    Ejemplo
    -------
    >>> import logging
    >>> logging.getLogger("SmoothCriminal").setLevel(logging.CRITICAL)
    >>> @thriller
    ... def cuadrado(x: int) -> int:
    ...     return x * x
    >>> cuadrado(4)
    16
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        logger.info("🎬 It’s close to midnight… benchmarking begins (Thriller Mode).")

        history = memory.get_execution_history(func.__name__)
        thriller_durations = [
            h["duration"] for h in history if h.get("decorator") == "@thriller"
        ]
        prev_avg = statistics.mean(thriller_durations) if thriller_durations else None

        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        duration = end - start
        logger.info(
            f"🧟 ‘Thriller’ just revealed a performance monster: {duration:.6f} seconds."
        )

        improvement_ratio = prev_avg / duration if prev_avg and duration > 0 else None
        if (
            improvement_ratio
            and improvement_ratio >= 5
            and func.__name__ not in _THRILLER_ANNOUNCED
        ):
            logger.info(
                "♂ It's close to midnight... and your code just THRILLED the benchmarks."
            )
            _THRILLER_ANNOUNCED.add(func.__name__)

        # Registrar nueva duración para futuras comparaciones
        memory.log_execution_stats(
            func_name=func.__name__,
            input_type=type(args[0]) if args else type(None),
            decorator_used="@thriller",
            duration=duration,
        )

        # Analizar mejora y efectos MJ si está activado
        if MJ_MODE and prev_avg and prev_avg > 0:
            improvement = (prev_avg - duration) / prev_avg * 100
            play_mj_effect(improvement)

        return result

    return wrapper

def jam(
    workers: int = 4,
    *,
    backend: Literal["thread", "process", "async"] = "thread",
) -> Callable[[Callable[[A], T]], Callable[[Sequence[A]], Any]]:
    """Ejecuta ``func`` en paralelo sobre una secuencia de argumentos.

    Parámetros
    ----------
    workers: int
        Número de *workers* concurrentes.
    backend: {"thread", "process", "async"}
        Mecanismo de paralelización a utilizar.

    Ejemplo
    -------
    >>> import logging
    >>> logging.getLogger("SmoothCriminal").setLevel(logging.CRITICAL)
    >>> @jam(workers=2, backend="thread")
    ... def cuadrado(x: int) -> int:
    ...     return x * x
    >>> sorted(cuadrado([1, 2, 3]))
    [1, 4, 9]
    """

    def decorator(func: Callable[[A], T]) -> Callable[[Sequence[A]], Any]:
        if backend == "async":
            if inspect.iscoroutinefunction(func):
                async def async_wrapper(args_list: Sequence[A]) -> List[T]:
                    logger.info(
                        f"🎶 Async jam session with {workers} workers (async func)"
                    )
                    tasks = [func(arg) for arg in args_list]
                    return await asyncio.gather(*tasks)

                return wraps(func)(async_wrapper)

            async def async_wrapper(args_list: Sequence[A]) -> List[T]:
                logger.info(
                    f"🎶 Async jam session with {workers} workers (sync func)"
                )
                loop = asyncio.get_event_loop()
                tasks = [loop.run_in_executor(None, func, arg) for arg in args_list]
                return await asyncio.gather(*tasks)

            return wraps(func)(async_wrapper)

        module_name = func.__module__
        func_name = func.__name__
        if backend == "process":
            module = sys.modules.get(module_name)
            orig_name = f"__jam_orig_{func_name}"
            setattr(module, orig_name, func)
            target_name = orig_name
        else:
            target_name = func_name

        def thread_backend(args_list: Sequence[A]) -> List[T]:
            logger.info(
                f"🎶 Don't stop 'til you get enough... workers! (x{workers}, backend={backend})"
            )
            results: List[T] = []

            if backend == "thread":
                from queue import Queue, Empty
                import threading

                q: Queue = Queue()
                for arg in args_list:
                    q.put(arg)

                lock = threading.Lock()

                def worker() -> None:
                    while True:
                        try:
                            arg = q.get_nowait()
                        except Empty:
                            break
                        try:
                            res = func(arg)
                            with lock:
                                results.append(res)
                        except Exception as e:
                            logger.warning(f"Worker failed on input {arg}: {e}")

                with ThreadPoolExecutor(max_workers=workers) as executor:
                    futures = [executor.submit(worker) for _ in range(workers)]
                    for future in as_completed(futures):
                        future.result()

                return results

            if backend == "process":
                from multiprocessing import Manager

                manager = Manager()
                q = manager.Queue()
                for arg in args_list:
                    q.put(arg)

                with ProcessPoolExecutor(max_workers=workers) as executor:
                    futures = [
                        executor.submit(_process_worker, module_name, target_name, q)
                        for _ in range(workers)
                    ]
                    for future in as_completed(futures):
                        results.extend(future.result())

                return results

            raise ValueError(f"Unknown backend: {backend}")

        return wraps(func)(thread_backend)

    return decorator

Mode = Literal["auto", "light", "precise"]


def black_or_white(mode: Mode = "auto") -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Optimiza los tipos numéricos de ``numpy.ndarray`` antes de ejecutar ``func``.

    Ejemplo
    -------
    >>> import numpy as np, logging
    >>> logging.getLogger("SmoothCriminal").setLevel(logging.CRITICAL)
    >>> @black_or_white("light")
    ... def tipo(arr: np.ndarray) -> str:
    ...     return str(arr.dtype)
    >>> tipo(np.array([1, 2, 3], dtype=np.int64))
    'int32'
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            converted_args: List[Any] = []
            for arg in args:
                if isinstance(arg, np.ndarray):
                    if mode == "light":
                        arg = _convert_to_light(arg)
                        logger.info(
                            "🌓 It's black or white! Using light types (float32/int32)."
                        )
                    elif mode == "precise":
                        arg = _convert_to_precise(arg)
                        logger.info("🌕 Going for precision! Using float64/int64.")
                    elif mode == "auto":
                        if arg.size > 1e6:
                            arg = _convert_to_light(arg)
                            logger.info(
                                "🌓 Auto mode: array is large, switching to float32/int32."
                            )
                        else:
                            arg = _convert_to_precise(arg)
                            logger.info(
                                "🌕 Auto mode: small array, using float64/int64."
                            )
                converted_args.append(arg)
            return func(*converted_args, **kwargs)

        return wrapper

    return decorator

def _convert_to_light(arr):
    if np.issubdtype(arr.dtype, np.integer):
        return arr.astype(np.int32)
    elif np.issubdtype(arr.dtype, np.floating):
        return arr.astype(np.float32)
    return arr

def _convert_to_precise(arr):
    if np.issubdtype(arr.dtype, np.integer):
        return arr.astype(np.int64)
    elif np.issubdtype(arr.dtype, np.floating):
        return arr.astype(np.float64)
    return arr

def beat_it(
    fallback_func: Optional[Callable[P, T]] = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Ejecuta ``func`` y usa ``fallback_func`` si ocurre una excepción.

    Ejemplo
    -------
    >>> import logging
    >>> logging.getLogger("SmoothCriminal").setLevel(logging.CRITICAL)
    >>> def respaldo(x: int) -> int:
    ...     return -1
    >>> @beat_it(respaldo)
    ... def falla(x: int) -> int:
    ...     raise ValueError("error")
    >>> falla(3)
    -1
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(
                    "🧥 Beat it! Something failed... Switching to fallback."
                )
                if fallback_func:
                    return fallback_func(*args, **kwargs)
                logger.error("No fallback provided. Rethrowing exception.")
                raise e

        return wrapper

    return decorator

def bad(parallel: bool = False) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Aplica optimizaciones agresivas de Numba a ``func``.

    Ejemplo
    -------
    >>> import logging
    >>> logging.getLogger("SmoothCriminal").setLevel(logging.CRITICAL)
    >>> @bad(parallel=False)
    ... def suma(a: float, b: float) -> float:
    ...     return a + b
    >>> suma(1.0, 2.0)
    3.0
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        try:
            jit_func = jit(
                nopython=True, fastmath=True, cache=True, parallel=parallel
            )(func)

            @wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                logger.info(
                    "🕶 Who's bad? This function is. Activating aggressive optimizations."
                )
                return jit_func(*args, **kwargs)

            return wrapper
        except Exception as e:
            logger.warning(
                "Bad mode failed. Reverting to original function. Reason: %s", e
            )
            return func

    return decorator
def dangerous(
    func: Callable[P, T], *, parallel: bool = True
) -> Callable[P, T]:
    """Combina :func:`bad` y :func:`thriller` para optimizar ``func``.

    Ejemplo
    -------
    >>> import logging
    >>> logging.getLogger("SmoothCriminal").setLevel(logging.CRITICAL)
    >>> @dangerous
    ... def cubo(x: int) -> int:
    ...     return x ** 3
    >>> cubo(2)
    8
    """
    logger.info("⚠️ Entering Dangerous Mode... Optimizing without mercy.")

    # Aplicar decoradores agresivos
    func = bad(parallel=parallel)(func)
    func = thriller(func)

    return func


def bad_and_dangerous(
    fallback: Optional[Callable[P, T]] = None, *, parallel: bool = True
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Combina :func:`bad`, :func:`thriller` y :func:`profile_it` con *fallback*.

    Aplica optimización agresiva, cronometra la ejecución, perfila la función y
    registra las estadísticas de ejecución. Si ocurre un error, se usa el
    ``fallback`` proporcionado.
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        optimized = bad(parallel=parallel)(func)
        timed = thriller(optimized)

        @wraps(func)
        def inner(*args: P.args, **kwargs: P.kwargs) -> T:
            logger.info("🚨 bad_and_dangerous: inicio")
            result = timed(*args, **kwargs)
            stats = profile_it(optimized, args=args, kwargs=kwargs, parallel=parallel)
            input_type = type(args[0]) if args else None
            log_execution_stats(
                func_name=func.__name__,
                input_type=input_type,
                decorator_used="@bad_and_dangerous",
                duration=round(stats["mean"], 6),
            )
            logger.info("✅ bad_and_dangerous: fin")
            return result

        return beat_it(fallback)(inner)

    return decorator

def _run_once(
    args: Tuple[Callable[..., Any], Tuple[Any, ...], Dict[str, Any]]
) -> float:
    func, func_args, func_kwargs = args
    start = time.perf_counter()
    func(*func_args, **func_kwargs)
    end = time.perf_counter()
    return end - start


def profile_it(
    func: Callable[P, Any],
    args: Tuple[Any, ...] = (),
    kwargs: Optional[Dict[str, Any]] = None,
    repeat: int = 5,
    parallel: bool = False,
) -> Dict[str, Union[float, List[float]]]:
    """Obtiene estadísticas de rendimiento ejecutando ``func`` repetidas veces.

    Ejemplo
    -------
    >>> import logging
    >>> logging.getLogger("SmoothCriminal").setLevel(logging.CRITICAL)
    >>> def suma(a: int, b: int) -> int:
    ...     return a + b
    >>> stats = profile_it(suma, args=(1, 2), repeat=2)
    >>> sorted(stats.keys())
    ['best', 'mean', 'runs', 'std_dev']
    """
    if kwargs is None:
        kwargs = {}

    logger.info("🧪 Profiling in progress... Don't stop 'til you get enough data!")

    exec_args = (func, args, kwargs)
    times: List[float] = []

    if parallel:
        with Pool(min(repeat, cpu_count())) as pool:
            results = pool.map(_run_once, [exec_args] * repeat)
            times.extend(results)
    else:
        for _ in range(repeat):
            duration = _run_once(exec_args)
            times.append(duration)

    mean_time = statistics.mean(times)
    std_dev = statistics.stdev(times) if repeat > 1 else 0.0
    best_time = min(times)

    logger.info(
        f"⏱ Mean: {mean_time:.6f}s | Best: {best_time:.6f}s | Std dev: {std_dev:.6f}s"
    )
    return {
        "mean": mean_time,
        "best": best_time,
        "std_dev": std_dev,
        "runs": times,
    }

def auto_boost(
    workers: int = 4, fallback: Optional[Callable[P, T]] = None
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Aplica automáticamente el mejor decorador según el patrón de uso.

    Ejemplo
    -------
    >>> import logging
    >>> logging.getLogger("SmoothCriminal").setLevel(logging.CRITICAL)
    >>> @auto_boost()
    ... def cuadrado(x: int) -> int:
    ...     return x * x
    >>> sorted(cuadrado([1, 2, 3]))
    [1, 4, 9]
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        use_jam = False
        use_smooth = False

        try:
            source = inspect.getsource(func)
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.For):
                    if isinstance(node.iter, ast.Call) and getattr(node.iter.func, 'id', '') == 'range':
                        use_smooth = True
                elif isinstance(node, ast.Call) and getattr(node.func, 'id', '') in ['sum', 'map', 'filter']:
                    use_smooth = True

        except Exception as e:
            logger.warning(f"auto_boost: AST inspection failed: {e}")

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            nonlocal use_jam
            input_type = type(args[0]) if args else None

            if len(args) == 1 and isinstance(args[0], (list, tuple)):
                use_jam = True

            boosted: Callable[P, T] = func
            decorator_used = "none"

            if fallback:
                boosted = beat_it(fallback)(boosted)
                decorator_used = "@beat_it"

            if use_smooth:
                boosted = smooth(boosted)
                decorator_used = "@smooth"
                logger.info("🧠 auto_boost: Applied @smooth")
            elif use_jam:
                boosted = jam(workers=workers)(boosted)
                decorator_used = "@jam"
                logger.info("🎶 auto_boost: Applied @jam")

            boosted = thriller(boosted)

            # Medición de tiempo para logging de memoria
            start = time.perf_counter()
            result = boosted(*args, **kwargs)
            end = time.perf_counter()

            log_execution_stats(
                func_name=func.__name__,
                input_type=input_type,
                decorator_used=decorator_used,
                duration=round(end - start, 6),
            )

            return result

        return wrapper

    return decorator
