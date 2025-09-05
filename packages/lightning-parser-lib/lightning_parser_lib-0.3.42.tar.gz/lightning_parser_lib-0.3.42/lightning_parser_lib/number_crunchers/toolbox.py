import os
import pickle
import hashlib
from typing import List, Mapping, Any
import datetime
import string
import zipfile
import re

def tprint(*args: Any, **kwargs: Any) -> None:
    """
    Prints the provided arguments to standard output with a prefixed timestamp.

    This function wraps the built-in print function to prepend each output with a
    timestamp formatted as "[MM-DD-YYYY HH:MM:SS]". It accepts all positional and
    keyword arguments supported by print.

    Parameters:
        *args: Variable length argument list to be printed.
        **kwargs: Arbitrary keyword arguments for the built-in print function.
                  Common keywords include 'sep', 'end', 'file', and 'flush'.

    Returns:
        None

    Example:
        >>> tprint("System initialized.")
        [03-31-2025 12:34:56] System initialized.
    """
    timestamp = datetime.datetime.now(tz=datetime.timezone.utc).strftime("[%m-%d-%Y %H:%M:%S UTC]")
    print(timestamp, *args, **kwargs)

def zig_zag_range(max_value: int, start: int):
    """
    Generates an iterator over indices in a zig-zag order within the range [0, max_value).

    The iterator starts at the specified `start` index and then alternates between
    increasing and decreasing indices. The pattern is:
    
        start, start + d, start - d, start + 2*d, start - 2*d, ...

    The initial direction is chosen based on the available space toward the range
    boundaries. If the distance to the upper boundary (max_value - 1) is smaller than
    the distance to the lower boundary (0), the iterator will first move upward; otherwise,
    it will move downward.

    Parameters:
      max_value (int): The exclusive upper bound for indices (valid indices are 0 to max_value - 1).
      start (int): The starting index within the range.

    Returns:
      Iterator[int]: An iterator yielding indices in zig-zag order.

    Example:
      >>> list(zig_zag_range(10, 5))
      [5, 6, 4, 7, 3, 8, 2, 9, 1, 0]

      >>> list(zig_zag_range(10, 2))
      [2, 1, 3, 0, 4, 5, 6, 7, 8, 9]

      >>> list(zig_zag_range(0, 0))
      []
    """
    if max_value == 0:
        return

    if start < 0 or start >= max_value:
        raise ValueError("start must be within the range [0, max_value)")

    yield start
    up_max = max_value - start - 1  # maximum upward steps possible
    down_max = start              # maximum downward steps possible
    max_d = max(up_max, down_max)

    # Determine the first direction: if the space upward is smaller, go up first; otherwise, go down.
    first = 'pos' if up_max < down_max else 'neg'

    for d in range(1, max_d + 1):
        if first == 'pos':
            if start + d < max_value:
                yield start + d
            if start - d >= 0:
                yield start - d
        else:
            if start - d >= 0:
                yield start - d
            if start + d < max_value:
                yield start + d


def chunk_items(counter: Mapping[Any, int], max_chunk_size: int):
    """
    Splits items from a counter into chunks based on a maximum allowed sum of counts.

    The function iterates over the items of the provided counter (a dictionary-like object)
    and groups the keys into chunks such that the cumulative sum of their counts does not exceed
    the specified `max_chunk_size`. When adding an item's count would surpass the limit and the current
    chunk is non-empty, the current chunk is yielded and a new chunk is started.

    Parameters:
      counter (Mapping[Any, int]): A dictionary-like object mapping items to their counts.
      max_chunk_size (int): The maximum allowed sum of counts for each chunk.

    Yields:
      List[Any]: A list of keys from the counter forming a chunk.

    Example:
      >>> from collections import Counter
      >>> counts = Counter({'a': 3, 'b': 2, 'c': 5, 'd': 1})
      >>> list(chunk_items(counts, 5))
      [['a'], ['b', 'd'], ['c']]
    """
    current_bin = []
    current_size = 0
    for number, count in counter.items():
        # If adding this count exceeds the limit and there's already data in current_bin, yield it.
        if current_bin and current_size + count > max_chunk_size:
            yield current_bin
            current_bin = []
            current_size = 0
        current_bin.append(number)
        current_size += count
    if current_bin:
        yield current_bin


def hash_string_list(string_list: List[str]):
    """
    Generates a unique hash for a list of strings.

    The function concatenates the list of strings using a null character as a delimiter to
    ensure that the boundaries between strings are preserved, then computes the SHA-256 hash
    of the resulting single string.

    Parameters:
      string_list (List[str]): A list of strings to be hashed.

    Returns:
      str: A hexadecimal string representing the SHA-256 hash of the concatenated input strings.

    Example:
      >>> hash_string_list(["hello", "world"])
      '64ec88ca00b268e5ba1a35678a1b5316d212f4f366b247724e3f0b5a5edb69c6'
    """
    joined = '\0'.join(string_list)  # Use a delimiter unlikely to appear in strings
    return hashlib.sha256(joined.encode('utf-8')).hexdigest()


def compute_directory_hash(directory: str) -> str:
    """
    Computes a unique hash for the contents of a directory based on the list of items,
    their creation dates, and their modification dates.

    For each file or directory within the specified directory, a string is created combining:
    - The item name.
    - The creation timestamp.
    - The modification timestamp.
    
    The list of these strings is then sorted to ensure consistent ordering and hashed to produce
    a unique fingerprint representing the state of the directory.

    Parameters:
      directory (str): The path of the directory to hash.

    Returns:
      str: A hexadecimal string representing the SHA-256 hash of the directory's contents.
    """
    items = []
    for entry in os.listdir(directory):
        path = os.path.join(directory, entry)
        # Process both files and directories
        if os.path.isfile(path) or os.path.isdir(path):
            try:
                ctime = os.path.getctime(path)
                mtime = os.path.getmtime(path)
            except Exception:
                ctime = 0
                mtime = 0
            items.append(f"{entry}:{ctime}:{mtime}")
    items.sort()  # Ensure the order is consistent
    return hash_string_list(items)


def save_cache_quick(directory: str, cache_file: str) -> None:
    """
    Computes the directory hash and saves it to a pickle file.

    This function calculates a unique hash for the specified directory based on the list of its
    items along with their creation and modification dates. The hash is then saved to a pickle file,
    which can be later used to determine if the directory contents have changed.

    Parameters:
      directory (str): The path of the directory to hash.
      cache_file (str): The path to the pickle file where the computed hash is saved.

    Example:
      >>> save_cache_quick("/path/to/directory", "cache.pkl")
    """
    dir_hash = compute_directory_hash(directory)
    with open(cache_file, 'wb') as f:
        pickle.dump(dir_hash, f)


def is_cached(directory: str, cache_file: str) -> bool:
    """
    Checks if the current directory contents match the previously cached state.

    This function computes the current hash for the directory (based on the items, their creation
    dates, and modification dates) and compares it to the hash stored in the pickle file. It returns
    True if the hashes are identical (indicating no changes), or False otherwise.

    Parameters:
      directory (str): The path of the directory to check.
      cache_file (str): The path to the pickle file where the previous hash is stored.

    Returns:
      bool: True if the directory's current state matches the cached state, False if it has changed.

    Example:
      >>> if is_cached("/path/to/directory", "cache.pkl"):
      ...     tprint("Directory is unchanged.")
      ... else:
      ...     tprint("Directory has been modified.")
    """
    current_hash = compute_directory_hash(directory)
    try:
        with open(cache_file, 'rb') as f:
            cached_hash = pickle.load(f)
    except (FileNotFoundError, EOFError, pickle.UnpicklingError):
        # If the cache file doesn't exist or can't be read, consider the directory as changed.
        return False
    return current_hash == cached_hash

def cpu_pct_to_cores(pct: float) -> int:
    """
    Converts a CPU usage fraction into an equivalent number of CPU cores.

    This function calculates the number of CPU cores corresponding to a given percentage (as a float)
    of the total available cores on the system. It multiplies the percentage by the total core count
    obtained from os.cpu_count(), and ensures that at least one core is returned.

    Parameters:
      pct (float): A fractional value representing the desired percentage of CPU cores.
                   For example, 0.5 represents 50% of the available cores.

    Returns:
      int: The number of CPU cores corresponding to the provided percentage, with a minimum of 1.

    Example:
      >>> import os
      >>> os.cpu_count()  # Suppose this returns 8
      8
      >>> cpu_pct_to_cores(0.25)
      2
    """

    if pct < 0.0 or pct > 1.0:
        raise("Percentage must be a value between 0.0 and 1.0 for determining core count")

    return int(max(pct * os.cpu_count(), 1))


def lerp(start: float, end: float, t: float) -> float:
    """
    Computes the linear interpolation between two float values.

    This function returns a value that is a weighted average of the `start` and `end` parameters,
    based on the interpolation factor `t`. When `t` is 0.0, the result equals `start`; when `t` is 1.0,
    the result equals `end`. For values of `t` between 0.0 and 1.0, the function returns a linearly
    interpolated value between `start` and `end`.

    Parameters:
      start (float): The starting value.
      end (float): The ending value.
      t (float): The interpolation factor, typically in the range [0.0, 1.0]. Values outside this range
                 will extrapolate beyond the provided `start` and `end`.

    Returns:
      float: The interpolated value computed as (1 - t) * start + t * end.

    Example:
      >>> lerp(10.0, 20.0, 0.5)
      15.0
    """
    return (1 - t) * start + t * end


def is_mostly_text(contents: str, threshold: float = 0.95) -> bool:
    """
    Determines whether a string is predominantly text.

    Parameters:
      contents (str): The text to analyze.
      threshold (float): Fraction of characters that must be 'printable'.

    Returns:
      bool: True if >= threshold of chars are in string.printable.
    """
    if not contents:
        return True

    # string.printable already includes digits, letters, punctuation, and whitespace (\t\n\r\x0b\x0c)
    allowed_chars = set(string.printable)
    total = len(contents)
    text_like = sum(1 for ch in contents if ch in allowed_chars)
    return (text_like / total) >= threshold

def find_county_file(directory_to_search: str | None = None, is_dir: bool = False):
    """
    Searches for a county file or directory matching a specific pattern within a given directory.

    The function looks for an item that matches the pattern "tl_####_us_county" where "####" represents
    a four-digit year. If `is_dir` is False, it searches for a file ending with ".zip" (e.g., "tl_2018_us_county.zip");
    if `is_dir` is True, it searches for a directory whose name exactly matches the pattern
    (e.g., "tl_2018_us_county").

    Parameters:
        directory_to_search (str | None): The directory path to search. Defaults to the current directory if None.
        is_dir (bool): If True, searches for a directory; if False (default), searches for a file ending in ".zip".

    Returns:
        Optional[str]: The full path of the first matching county file or directory found, or None if no match exists.

    Example:
        >>> find_county_file(".", False)
        './tl_2018_us_county.zip'
    """
    if directory_to_search == None:
        directory_to_search = "."
    pattern = re.compile(r"tl_\d{4}_us_county" + (r"\.zip" if not is_dir else r"$"))

    for name in os.listdir(directory_to_search):
        full_path = os.path.join(directory_to_search, name)

        if is_dir and os.path.isdir(full_path) and pattern.fullmatch(name):
            return full_path
        elif not is_dir and os.path.isfile(full_path) and pattern.fullmatch(name):
            return full_path

    return None

def find_shp(directory_to_search: str):
    """
    Recursively searches for a shapefile (*.shp) in the specified directory.

    The function walks the directory tree starting from `directory_to_search` and returns the full
    path of the first file encountered with a ".shp" extension (case insensitive).

    Parameters:
        directory_to_search (str): The root directory to begin the search.

    Returns:
        Optional[str]: The full path to the found shapefile, or None if no shapefile is found.

    Example:
        >>> find_shp("/path/to/data")
        '/path/to/data/county/somefile.shp'
    """
    for root, _, files in os.walk(directory_to_search):
        for name in files:
            if name.lower().endswith(".shp"):
                return os.path.join(root, name)
    return None


def unzip_file(zip_path: str):
    """
    Extracts a zip file to a directory with the same base name as the zip file.

    Validates that the provided path refers to a valid zip file and then extracts its contents
    to a new directory named after the zip file (with the ".zip" extension removed).

    Parameters:
        zip_path (str): The full path of the zip file to be extracted.

    Returns:
        str: The path to the directory where the files were extracted.

    Raises:
        ValueError: If the provided file is not a valid zip archive.

    Example:
        >>> unzip_file("data_archive.zip")
        'data_archive'
    """
    if not zipfile.is_zipfile(zip_path):
        raise ValueError(f"Not a valid zip file: {zip_path}")
    
    extract_dir = os.path.splitext(zip_path)[0]  # Remove .zip extension
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    return extract_dir

def append_county(cartopy_paths: List[str]):
    """
    Attempts to locate a county shapefile and append its path to a list of cartopy shapefile paths.

    The function first tries to find a county directory (by searching for a pattern matching "tl_####_us_county").
    If such a directory is found, it searches within for a shapefile (*.shp) and, if found, appends its full path
    to the provided `cartopy_paths` list. If no directory is found, it then looks for a zip file matching the county
    pattern, unzips it, and then recurses to try to locate the shapefile again.

    Parameters:
        cartopy_paths (List[str]): A list of existing cartopy shapefile paths that may be updated with the county shapefile.

    Returns:
        List[str]: The updated list of cartopy shapefile paths, potentially including the county shapefile path.

    Example:
        >>> paths = []
        >>> append_county(paths)
        ['/path/to/county_shapefile.shp']
    """
    county_dir = find_county_file(is_dir=True)
    if county_dir:
        county_shp = find_shp(county_dir)
        if county_shp:
            cartopy_paths.append(county_shp)
    else:
        county_dir_zip = find_county_file(is_dir=False)
        if county_dir_zip:
            unzip_file(county_dir_zip)
            return append_county() # Try again
    return cartopy_paths
        
def split_into_groups(x: List[Any], num_workers: int):
    """
    Splits a list into nearly equal sublists, up to num_workers groups.

    This function partitions the input list x into a list of sublists where each sublist contains
    a nearly equal number of elements. The number of groups created is the minimum of num_workers
    and the length of x. The list is divided such that each group gets an average size, with any
    remainder elements distributed to the first groups to ensure the sizes differ by at most one.

    Parameters:
      x (List[Any]): The list of elements to be partitioned.
      num_workers (int): The maximum number of groups to split the list into.

    Returns:
      List[List[Any]]: A list containing the sublists of x split into nearly equal groups.

    Example:
      >>> x = list(range(1, 21))
      >>> split_into_groups(x, 3)
      [[1, 2, 3, 4, 5, 6, 7], [8, 9, 10, 11, 12, 13, 14], [15, 16, 17, 18, 19, 20]]
    """
    n_groups = min(num_workers, len(x))
    avg = len(x) // n_groups
    remainder = len(x) % n_groups
    groups = []
    start = 0
    for i in range(n_groups):
        size = avg + (1 if i < remainder else 0)
        if size == 0:
            break
        groups.append(x[start:start+size])
        start += size
    return groups