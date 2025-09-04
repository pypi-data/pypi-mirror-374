from ._impl import cPrefixTrie
import pickle
import multiprocessing.shared_memory as shm
import weakref
import atexit

try:
    from ._version import __version__
except ImportError:
    # Fallback version if _version.py doesn't exist yet
    __version__ = "unknown"


# Global registry to track shared memory blocks for cleanup
_shared_memory_registry = weakref.WeakSet()
_cleanup_registered = False


def _cleanup_shared_memory():
    """Clean up any remaining shared memory blocks on exit"""
    for shm_block in list(_shared_memory_registry):
        try:
            shm_block.unlink()
        except:
            pass  # Ignore errors during cleanup


class PrefixTrie:
    """
    Thin wrapper around the cPrefixTrie class to provide a Python interface.
    """

    __slots__ = ("_trie", "allow_indels", "immutable", "_entries", "_shared_memory", "_is_shared_owner", "_exact_set")

    def __init__(self, entries: list[str], allow_indels: bool=False, immutable: bool=True, shared_memory_name: str=None):
        """
        Initialize the PrefixTrie with the given arguments.

        :param entries: List of strings to be added to the trie.
        :param allow_indels: If True, allows insertions and deletions in the trie
        :param immutable: If True, the trie cannot be modified after creation
        :param shared_memory_name: If provided, load from existing shared memory block
        """
        global _cleanup_registered

        if shared_memory_name:
            # Load from shared memory
            self._load_from_shared_memory(shared_memory_name)
        else:
            # Normal initialization
            self.allow_indels = allow_indels
            self.immutable = immutable
            if not isinstance(entries, list):
                entries = list(entries)  # Ensure entries is a list
            self._entries = entries  # Store original entries for pickle support
            self._trie = cPrefixTrie(entries, allow_indels, immutable)
            self._shared_memory = None
            self._is_shared_owner = False
            # Create Python set for ultra-fast exact matching
            self._exact_set = set(entries)

        # Register cleanup handler once
        if not _cleanup_registered:
            atexit.register(_cleanup_shared_memory)
            _cleanup_registered = True

    def create_shared_memory(self, name: str=None) -> str:
        """
        Create a shared memory block containing this trie's data.
        Returns the name of the shared memory block.
        Note: Shared memory requires the trie to be immutable.

        :param name: Optional name for the shared memory block
        :return: Name of the created shared memory block
        """
        if not self.immutable:
            raise RuntimeError("Cannot create shared memory for mutable trie. Only immutable tries support shared memory.")

        # Serialize the trie data
        data = {
            'entries': self._entries,
            'allow_indels': self.allow_indels,
            'immutable': self.immutable
        }
        serialized_data = pickle.dumps(data)

        # Create shared memory block
        try:
            if name:
                shm_block = shm.SharedMemory(name=name, create=True, size=len(serialized_data))
            else:
                shm_block = shm.SharedMemory(create=True, size=len(serialized_data))

            # Copy data to shared memory
            shm_block.buf[:len(serialized_data)] = serialized_data

            # Track for cleanup
            _shared_memory_registry.add(shm_block)

            # Store reference for potential cleanup
            self._shared_memory = shm_block
            self._is_shared_owner = True

            return shm_block.name

        except Exception as e:
            raise RuntimeError(f"Failed to create shared memory: {e}")

    def _load_from_shared_memory(self, name: str):
        """Load trie data from shared memory block"""
        try:
            # Connect to existing shared memory
            shm_block = shm.SharedMemory(name=name, create=False)

            # Deserialize data
            serialized_data = bytes(shm_block.buf)
            data = pickle.loads(serialized_data)

            # Initialize trie - shared memory tries are always immutable
            self.allow_indels = data['allow_indels']
            self.immutable = data.get('immutable', True)  # Default to immutable for backward compatibility
            self._entries = data['entries']
            self._trie = cPrefixTrie(self._entries, self.allow_indels, self.immutable)
            # Create Python set for ultra-fast exact matching
            self._exact_set = set(self._entries)

            # Store reference (but not as owner)
            self._shared_memory = shm_block
            self._is_shared_owner = False

        except Exception as e:
            raise RuntimeError(f"Failed to load from shared memory '{name}': {e}")

    def cleanup_shared_memory(self):
        """
        Clean up shared memory if this instance owns it
        """
        if hasattr(self, '_shared_memory') and self._shared_memory and hasattr(self, '_is_shared_owner') and self._is_shared_owner:
            try:
                self._shared_memory.unlink()
                _shared_memory_registry.discard(self._shared_memory)
            except:
                pass  # Ignore errors
            finally:
                self._shared_memory = None
                self._is_shared_owner = False

    def __getstate__(self):
        """
        Support for pickle serialization.
        Returns the state needed to reconstruct the object.
        """
        return {
            'entries': self._entries,
            'allow_indels': self.allow_indels,
            'immutable': self.immutable
        }

    def __setstate__(self, state):
        """
        Support for pickle deserialization.
        Reconstructs the object from the pickled state.
        """
        self.allow_indels = state['allow_indels']
        self.immutable = state.get('immutable', True)  # Default to immutable for backward compatibility
        self._entries = state['entries']
        self._trie = cPrefixTrie(self._entries, self.allow_indels, self.immutable)
        self._shared_memory = None
        self._is_shared_owner = False
        # Create Python set for ultra-fast exact matching
        self._exact_set = set(self._entries)

    def __del__(self):
        """
        Clean up shared memory on deletion if we own it
        """
        try:
            self.cleanup_shared_memory()
        except AttributeError:
            # Object may not be fully initialized
            pass

    def search(self, item: str, correction_budget: int=0) -> tuple[str | None, int]:
        """
        Search for an item in the trie with optional corrections.

        :param item: The string to search for in the trie.
        :param correction_budget: Maximum number of corrections allowed (default is 0).
        :return: A tuple containing the found item and the number of corrections, or (None, -1) if not found.
        """
        # Ultra-fast exact matching using Python set (bypasses all Cython overhead)
        if correction_budget == 0:
            # For exact matching, use pure Python set lookup - fastest possible
            return (item, 0) if item in self._exact_set else (None, -1)

        # For fuzzy matching, first check if it's an exact match in the set
        if item in self._exact_set:
            return (item, 0)

        # Use trie for fuzzy matching only when needed
        found, corrections = self._trie.search(item, correction_budget)
        return found, corrections

    def search_substring(self, target_string: str, correction_budget: int=0) -> tuple[str | None, int, int, int]:
        """
        Search for fuzzy substring matches of trie entries within a target string.

        This method finds any entry from the trie that appears as a fuzzy substring
        within the target string, allowing for insertions, deletions, and substitutions.

        :param target_string: The string to search within for trie entries
        :param correction_budget: Maximum number of edits allowed (default is 0)
        :return: Tuple of (found_string, corrections, start_pos, end_pos) or (None, -1, -1, -1)
                 where start_pos and end_pos indicate the location of the match in target_string
        """
        return self._trie.search_substring(target_string, correction_budget)

    def longest_prefix_match(self, target: str, min_match_length: int, correction_budget: int = 0) -> tuple[str | None, int, int]:
        """
        Find the longest prefix match in the trie for the given target string.

        :param target: The target string to find the longest prefix match for.
        :param min_match_length: Minimum length of the match to be considered valid.
        :param correction_budget: Maximum number of corrections allowed (default is 0 for exact matching).
        :return: A tuple containing the longest matching prefix, the target start index, and the match length.
        """
        return self._trie.longest_prefix_match(target, min_match_length, correction_budget)

    def search_count(self, query: str, correction_budget: int = 0) -> int:
        """
        Count the number of entries that fit a query string within a correction budget.

        This method is optimized for efficiently counting all possible matches
        without returning the actual strings.

        :param query: The query string to match against the trie entries.
        :param correction_budget: Maximum number of corrections allowed (default is 0).
        :return: The count of matching entries within the correction budget.
        """
        return self._trie.search_count(query, correction_budget)

    def __contains__(self, item: str) -> bool:
        """
        Check if the trie contains the given item.

        :param item: The string to check for presence in the trie.
        :return: True if the item is in the trie, False otherwise.
        """
        # First check in the exact set for ultra-fast exact matching
        if item in self._exact_set:
            return True

        found, _ = self._trie.search(item)
        return found is not None

    def __iter__(self):
        """
        Iterate over the items in the trie.

        :return: An iterator over the items in the trie.
        """
        return self._trie.__iter__()

    def __len__(self):
        """
        Get the number of items in the trie.

        :return: The number of items in the trie.
        """
        return self._trie.n_values()

    def __repr__(self):
        """
        String representation of the PrefixTrie.

        :return: A string representation of the PrefixTrie.
        """
        return f"PrefixTrie(n_entries={len(self)}, allow_indels={self.allow_indels})"

    def __str__(self):
        """
        String representation of the PrefixTrie.

        :return: A string representation of the PrefixTrie.
        """
        return f"PrefixTrie with {len(self)} entries, allow_indels={self.allow_indels}"

    def __getitem__(self, item: str) -> str:
        """
        Get the item from the trie.

        :param item: The string to retrieve from the trie.
        :return: The item if found, otherwise raises KeyError.
        """
        found, _ = self._trie.search(item)
        if found is None:
            raise KeyError(f"{item} not found in PrefixTrie")
        return found

    def add(self, entry: str) -> bool:
        """
        Add a new entry to the trie (only if mutable).

        :param entry: The string to add
        :return: True if added successfully, False if already exists or trie is immutable
        """
        if self.immutable:
            raise RuntimeError("Cannot modify immutable trie")

        # Use the Cython implementation
        result = self._trie.add(entry)

        # Update the Python set for fast exact matching
        if result:
            self._exact_set.add(entry)
            # Update entries list for pickle support
            if entry not in self._entries:
                self._entries.append(entry)

        return result

    def remove(self, entry: str) -> bool:
        """
        Remove an entry from the trie (only if mutable).

        :param entry: The string to remove
        :return: True if removed successfully, False if not found or trie is immutable
        """
        if self.immutable:
            raise RuntimeError("Cannot modify immutable trie")

        # Use the Cython implementation
        result = self._trie.remove(entry)

        # Update the Python set and entries list
        if result:
            self._exact_set.discard(entry)
            # Update entries list for pickle support
            if entry in self._entries:
                self._entries.remove(entry)

        return result

    def is_immutable(self) -> bool:
        """
        Check if the trie is immutable.

        :return: True if immutable, False if mutable
        """
        return self._trie.is_immutable()


# Convenience function for shared memory multiprocessing
def create_shared_trie(entries: list[str], allow_indels: bool=False, name: str=None) -> tuple[PrefixTrie, str]:
    """
    Create a PrefixTrie and put it in shared memory for multiprocessing.
    Note: Shared memory tries are always immutable.

    :param entries: List of strings to add to the trie
    :param allow_indels: Whether to allow insertions/deletions
    :param name: Optional name for shared memory block
    :return: Tuple of (trie_instance, shared_memory_name)
    """
    # Shared memory tries must be immutable
    trie = PrefixTrie(entries, allow_indels, immutable=True)
    shm_name = trie.create_shared_memory(name)
    return trie, shm_name


def load_shared_trie(shared_memory_name: str) -> PrefixTrie:
    """
    Load a PrefixTrie from shared memory.

    :param shared_memory_name: Name of the shared memory block
    :return: PrefixTrie instance loaded from shared memory
    """
    return PrefixTrie([], shared_memory_name=shared_memory_name)


__all__ = ["PrefixTrie", "create_shared_trie", "load_shared_trie"]
