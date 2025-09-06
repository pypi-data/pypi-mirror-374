"""Collection of tools used in cosmologix.

- Physical constants:
  Constants
- Cache management:
  get_cache_dir, clear_cache, cached_download, cached (decorator)
- input/output files:
  load_csv_from_url, save, load
- Integration:
  trapezoidal_rule_integration
- stats:
  conflevel_to_delta_chi2, randn, speed_measurement
- wrapper around vmap: safe_vmap
"""

import hashlib
import os
from pathlib import Path
import pickle
import shutil
import time
from typing import Callable, Tuple
import jax.numpy as jnp
import jax
import numpy as np


class Constants:
    """A container for physical constants."""

    # pylint: disable=too-few-public-methods
    G = 6.67384e-11  # m^3/kg/s^2
    c = 299792458.0  # m/s
    pc = 3.08567758e16  # m
    mp = 1.67262158e-27  # kg
    h = 6.62617e-34  # J.s
    k = 1.38066e-23  # J/K
    e = 1.60217663e-19  # C
    year = 31557600.0  # s
    sigma = (
        2 * jnp.pi**5 * k**4 / (15 * h**3 * c**2)
    )  # Stefan-Boltzmann constant J/s / K^4 /m^2
    zeta3 = 1.2020569031595942853997
    zeta5 = 1.0369277551433699263313


def get_cache_dir(jit=False):
    """Determines the appropriate cache directory based on the OS.

    Args:
        jit (bool, optional): If True, returns the path to the JIT cache
            subdirectory. Defaults to False.

    Returns:
        str: The path to the cache directory.
    """

    if os.name == "nt":  # Windows
        cache_dir = Path(os.getenv("LOCALAPPDATA")) / "Cache" / "cosmologix"
    elif os.name == "posix":  # Unix-like systems
        if "XDG_CACHE_HOME" in os.environ:
            cache_dir = Path(os.environ["XDG_CACHE_HOME"]) / "cosmologix"
        else:
            cache_dir = Path.home() / ".cache" / "cosmologix"
    else:
        raise OSError("Unsupported operating system")
    if jit:
        cache_dir = cache_dir / "jit"
    return str(cache_dir)


def persistent_compilation_cache_setup() -> str:
    """Sets up the JAX persistent compilation cache.

    This function checks the size of the cache directory and disables caching
    if it exceeds a certain threshold.

    Returns:
        str: A human-readable size of the cache directory or an error message.
    """
    try:
        # Get the cache directory path
        cache_dir = get_cache_dir(jit=True)

        # Ensure path is a Path object
        cache_path = Path(cache_dir)
        os.makedirs(cache_path, exist_ok=True)
        if not cache_path.is_dir():
            print(f"Path is not a directory: {cache_dir}")
            return

        # Sum the size of all files in the directory and subdirectories
        total_size = sum(
            file.stat().st_size for file in cache_path.rglob("*") if file.is_file()
        )

        if total_size > 2**30:
            # Convert to human-readable format
            for unit in ["B", "KB", "MB", "GB", "TB"]:
                if total_size < 1024:
                    break
                total_size /= 1024
            print(
                f"The compilation cache as grown to {total_size:.2f} {unit}."
                "Caching is disabled for now."
                "Clear the cache using `cosmologix clear-cache -j` to re-enable."
            )
        else:
            jax.config.update("jax_compilation_cache_dir", get_cache_dir(True))
            jax.config.update("jax_persistent_cache_min_entry_size_bytes", -1)
            jax.config.update("jax_persistent_cache_min_compile_time_secs", 0.1)
            # This is not available in all jax version
            try:
                jax.config.update(
                    "jax_persistent_cache_enable_xla_caches",
                    "xla_gpu_per_fusion_autotune_cache_dir",
                )
            except AttributeError:
                pass

    except PermissionError:
        print(f"Permission denied accessing cache directory: {cache_dir}")


persistent_compilation_cache_setup()


def clear_cache(jit=False):
    """Clears the cache directory.

    Args:
        jit (bool, optional): If True, clears only the JIT cache
            subdirectory. Defaults to False.
    """
    cache_dir = get_cache_dir(jit)

    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)  # Remove the entire directory
        jax.experimental.compilation_cache.compilation_cache.reset_cache()
        print(f"Cache directory {cache_dir} has been cleared.")
    else:
        print(f"Cache directory {cache_dir} does not exist.")


def cached_download(url):
    """Downloads a file from the web with caching.

    Args:
        url (str): The URL to download from.

    Returns:
        str: The path to the cached file.
    """
    cache_dir = get_cache_dir()

    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)

    # Use URL hash for filename to avoid conflicts
    filename = hashlib.md5(url.encode("utf-8")).hexdigest()
    cache_path = os.path.join(cache_dir, filename)

    if os.path.exists(cache_path):
        print(f"Using cached file: {cache_path}")
        return cache_path

    # Download the file
    # this module is a bit slow to import (don't unless needed)
    import requests  # pylint: disable=import-outside-toplevel

    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()

    with open(cache_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    print(f"File downloaded and cached at: {cache_path}")
    return cache_path


def cached(constant_function):
    """Decorator to cache the result of a function that always returns the same object.

    This decorator is designed for functions with no arguments that consistently
    return an identical object. It stores the result in a file-based cache
    using pickle serialization.

    Args:
        constant_function (callable): A function with no arguments that returns a
            constant object to be cached.

    Returns:
        callable: A wrapped function that returns the cached object.

    Notes:
        The cache is stored in a file named `func_cache_<function_name>` within
        the directory specified by `get_cache_dir()`. The decorator assumes
        `constant_function` is deterministic and side-effect-free. Uses
        `pickle` for serialization, so the returned object must be picklable.

    Examples:
        >>> @cached
        ... def expensive_likelihood():
        ...     return Chi2FullCov(...)  # Expensive computation
        >>> result = expensive_likelihood()  # Computes and caches
        >>> result2 = expensive_likelihood()  # Loads from cache
    """
    cache_dir = get_cache_dir()

    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)

    cache_path = os.path.join(cache_dir, f"func_cache_{constant_function.__name__}")

    def cached_function():
        if os.path.exists(cache_path):
            print(f"Using cached file: {cache_path}")
            with open(cache_path, "rb") as fid:
                return pickle.load(fid)
        else:
            obj = constant_function()
            with open(cache_path, "wb") as fid:
                pickle.dump(obj, fid)
            return obj

    return cached_function


def safe_vmap(in_axes: Tuple[None | int, ...] = (None, 0)) -> Callable:
    """Vectorizes a function with JAX's vmap, treating all inputs as arrays.

    Converts scalar inputs to 1D arrays before applying vmap, ensuring 1D
    array outputs.

    Args:
        in_axes (Tuple[None | int, ...]): Specifies which dimensions of inputs
            to vectorize.

    Returns:
        Callable: A JIT-compiled, vectorized version of the input function.
    """

    def wrapper(f: Callable) -> Callable:
        @jax.jit
        def vectorized(*args):
            vargs = [
                jnp.atleast_1d(arg) if ax is not None else arg
                for arg, ax in zip(args, in_axes)
            ]
            result = jax.vmap(f, in_axes=in_axes)(*vargs)
            return result

        return vectorized

    return wrapper


def trapezoidal_rule_integration(
    f: Callable, bound_inf: float, bound_sup: float, n_step: int = 1000, **kwargs
) -> float:
    """Computes the integral of a function using the trapezoidal rule.

    Args:
        f (Callable): The function to integrate.
        bound_inf (float): The lower bound of integration.
        bound_sup (float): The upper bound of integration.
        n_step (int, optional): The number of subdivisions. Defaults to 1000.
        **kwargs: Additional arguments passed to `f`.

    Returns:
        float: The computed integral.
    """
    x = jnp.linspace(bound_inf, bound_sup, n_step)
    y = f(x, **kwargs)
    h = (bound_sup - bound_inf) / (n_step - 1)
    return (h / 2) * (y[1:] + y[:-1]).sum()


def load_csv_from_url(url, delimiter=","):
    """Loads a CSV file from a URL into a NumPy array.

    Args:
        url (str): The URL of the CSV file to download.
        delimiter (str, optional): The string used to separate values in the
            CSV file. Defaults to ",".

    Returns:
        numpy.ndarray: The loaded CSV data as a NumPy array.
    """
    # Decode the response content and split into lines
    # lines = response.content.decode("utf-8").splitlines()
    path = cached_download(url)
    with open(path, "r", encoding="utf-8") as fid:
        lines = fid.readlines()

    # Process the CSV data
    def convert(value):
        """Attemps to convert values to numerical types"""
        value = value.strip()
        if not value:
            value = "nan"
        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                pass
        return value

    header = lines[0].split(delimiter)
    data = [[convert(value) for value in line.split(delimiter)] for line in lines[1:]]

    return np.rec.fromrecords(data, names=header)


def conflevel_to_delta_chi2(level, dof=2, max_iter=1000, tol=1e-6):
    """Returns the Δχ² value corresponding to a given confidence level.

    Note:
        For some reason, `ppf` is not available in `jax.scipy` but `cdf` is.
        A quick fix was to solve for the root using Newton's method.

    Args:
        level (float): The confidence level in percent.
        dof (int, optional): The number of degrees of freedom of the chi-squared
            distribution. Defaults to 2.
        max_iter (int, optional): The maximum number of iterations in the
            Newton search. Defaults to 1000.
        tol (float, optional): The tolerance for the numerical accuracy of the
            solution. Defaults to 1e-6.

    Returns:
        float: The Δχ² value.
    """
    x = jnp.array(dof)
    prob = level / 100

    def f(x):
        return jax.scipy.stats.chi2.cdf(x, dof) - prob

    def df(x):
        return jax.scipy.stats.chi2.pdf(x, dof)

    for _ in range(max_iter):
        x_new = x - f(x) / df(x)
        if jnp.abs(x_new - x) < tol:
            return x_new
        x = x_new
    raise ValueError("Newton's method did not converge")


# This global random key at the module level is provided for
# conveniency so that random vector can be obtained with onliners when
# need. This will note ensure actual randomness nor reproducibility.
# To be used cautiously
GLOBAL_KEY = None


# pylint: disable=global-statement
def randn(sigma, n=None, key=None):
    """Generates a Gaussian random vector scaled by sigma.

    Args:
        sigma (float or array_like): Standard deviation to scale the random
            vector.
        n (int or tuple, optional): The shape of the output. If None, the
            shape of `sigma` is used. Defaults to None.
        key (jax.random.PRNGKey, optional): The PRNG key for random number
            generation. If None, uses the global key. Defaults to None.

    Returns:
        jnp.ndarray: An array of Gaussian random numbers scaled by `sigma`.

    Notes:
        Using the global key (`key=None`) can lead to correlated results
        across function calls. For reproducibility, pass an explicit key.

    Examples:
        >>> import jax.numpy as jnp
        >>> randn(1.0, (2, 3))
        >>> randn(jnp.array([1, 2, 3]))
    """
    global GLOBAL_KEY
    if key is None:
        if GLOBAL_KEY is None:
            # This global random key at the module level is provided for
            # conveniency so that random vector can be obtained with onliners when
            # need. This will note ensure actual randomness nor reproducibility.
            # To be used cautiously
            GLOBAL_KEY = jax.random.PRNGKey(42)
        GLOBAL_KEY, subkey = jax.random.split(GLOBAL_KEY)
    else:
        subkey = key
    if n is None:
        n = sigma.shape
    gaussian_vector = jax.random.normal(subkey, n)
    return gaussian_vector * sigma


def speed_measurement(func, *args, n=10):
    """Measures the execution and JIT compilation speed of a function.

    Args:
        func (callable): The function to measure.
        *args: Arguments to pass to the function.
        n (int, optional): The number of executions to average over.
            Defaults to 10.

    Returns:
        tuple: A tuple containing the compilation time, execution time,
            JIT compilation time, JIT execution time, and averaged JIT
            execution time.
    """
    jax.clear_caches()  # make sure that compilation is triggered
    tstart = time.time()
    jax.block_until_ready(func(*args))
    tcomp = time.time()
    for _ in range(n):
        jax.block_until_ready(func(*args))
    tstop1 = time.time()
    jax.clear_caches()  # make sure that compilation is triggered
    tstart2 = time.time()
    jfunc = jax.jit(func)
    tjit = time.time()
    jax.block_until_ready(jfunc(*args))  # pylint: disable=not-callable
    tcomp2 = time.time()
    for _ in range(n):
        jax.block_until_ready(jfunc(*args))  # pylint: disable=not-callable
    tstop2 = time.time()
    # return (len(z), tcomp-tstart, (tstop-tcomp)/n)
    return (
        tcomp - tstart,
        (tstop1 - tcomp) / n,
        tjit - tstart2,
        tcomp2 - tjit,
        (tstop2 - tcomp2) / n,
    )


def save(grid, filename):
    """Saves a data dictionary to a pickle or ASDF file.

    Args:
        grid (dict): The dictionary to save.
        filename (str or Path): The name of the file.
    """
    filename = Path(filename)
    if filename.suffix == ".asdf":
        _save_asdf(grid, filename)
        return
    if filename.suffix == ".zst":
        import zstandard

        with zstandard.open(filename, "wb") as fid:
            pickle.dump(grid, fid)
        return
    with open(filename, "wb") as fid:
        pickle.dump(grid, fid)


def jax_to_numpy(x):
    """Converts a JAX array to a NumPy array.

    Args:
        x: The input array.

    Returns:
        numpy.ndarray: The converted array.
    """
    return np.asarray(x) if isinstance(x, jax.Array) else x


def _save_asdf(grid, filename):
    """Saves a data dictionary to an ASDF file.

    Args:
        grid (dict): The dictionary to save.
        filename (str or Path): The name of the file.
    """
    import asdf

    # Transform the pytree to convert JAX arrays to NumPy arrays
    numpy_pytree = jax.tree_util.tree_map(jax_to_numpy, grid)

    af = asdf.AsdfFile(numpy_pytree)
    af.write_to(filename)


def load(filename):
    """Loads a data dictionary from a pickle or ASDF file.

    Args:
        filename (str or Path): The name of the file.

    Returns:
        dict: The loaded dictionary.
    """
    if isinstance(filename, (str, Path)):
        filename = Path(filename)
        if filename.suffix == ".asdf":
            import asdf

            return asdf.open(filename)
        if filename.suffix == ".zst":
            import zstandard

            with zstandard.open(filename, "rb") as fid:
                return pickle.load(fid)
        with open(filename, "rb") as fid:
            return pickle.load(fid)
    else:
        return filename
