"""
History Manager Module
Handles undo/redo functionality for image editing operations

This module implements the HistoryManager class which maintains
a history stack of image states for undo/redo operations.
"""

import numpy as np
from typing import List, Optional
from collections import deque


class HistoryManager:
    """
    Manages the history of image edits for undo/redo functionality.

    This class implements a command pattern-like history system that
    maintains a stack of image states, allowing users to undo and redo
    their editing operations.

    Attributes:
        _history_stack: Stack of previous image states
        _redo_stack: Stack of undone image states
        _max_history: Maximum number of states to maintain
        _current_state: Current image state
    """

    def __init__(self, max_history: int = 20):
        """
        Initialize the HistoryManager

        Args:
            max_history: Maximum number of history states to maintain
        """
        self._history_stack: deque = deque(maxlen=max_history)
        self._redo_stack: deque = deque(maxlen=max_history)
        self._max_history = max_history
        self._current_state: Optional[np.ndarray] = None

    @property
    def can_undo(self) -> bool:
        """Check if undo operation is available"""
        return len(self._history_stack) > 0

    @property
    def can_redo(self) -> bool:
        """Check if redo operation is available"""
        return len(self._redo_stack) > 0

    @property
    def history_count(self) -> int:
        """Get the number of states in history"""
        return len(self._history_stack)

    def add_state(self, image: np.ndarray) -> None:
        """
        Add a new state to the history

        This method saves the current state before a new operation,
        allowing it to be restored later via undo.

        Args:
            image: The image state to save
        """
        if self._current_state is not None:
            # Add current state to history before replacing it
            self._history_stack.append(self._current_state.copy())

        # Set new current state
        self._current_state = image.copy()

        # Clear redo stack when new action is performed
        self._redo_stack.clear()

    def undo(self) -> Optional[np.ndarray]:
        """
        Undo the last operation

        Returns:
            The previous image state, or None if no history available
        """
        if not self.can_undo:
            return None

        # Save current state to redo stack
        if self._current_state is not None:
            self._redo_stack.append(self._current_state.copy())

        # Restore previous state from history
        self._current_state = self._history_stack.pop()
        return self._current_state.copy()

    def redo(self) -> Optional[np.ndarray]:
        """
        Redo the last undone operation

        Returns:
            The redone image state, or None if no redo available
        """
        if not self.can_redo:
            return None

        # Save current state to history stack
        if self._current_state is not None:
            self._history_stack.append(self._current_state.copy())

        # Restore state from redo stack
        self._current_state = self._redo_stack.pop()
        return self._current_state.copy()

    def clear_history(self) -> None:
        """Clear all history and redo stacks"""
        self._history_stack.clear()
        self._redo_stack.clear()
        self._current_state = None

    def get_current_state(self) -> Optional[np.ndarray]:
        """
        Get the current image state

        Returns:
            Copy of the current image state, or None if no state exists
        """
        if self._current_state is not None:
            return self._current_state.copy()
        return None

    def initialize_state(self, image: np.ndarray) -> None:
        """
        Initialize the history with a starting state

        This is typically called when a new image is loaded.

        Args:
            image: The initial image state
        """
        self.clear_history()
        self._current_state = image.copy()

    def get_memory_usage(self) -> dict:
        """
        Get memory usage statistics for the history

        Returns:
            Dictionary containing memory usage information
        """
        total_size = 0
        history_size = sum(img.nbytes for img in self._history_stack if img is not None)
        redo_size = sum(img.nbytes for img in self._redo_stack if img is not None)
        current_size = self._current_state.nbytes if self._current_state is not None else 0

        total_size = history_size + redo_size + current_size

        return {
            'history_count': len(self._history_stack),
            'redo_count': len(self._redo_stack),
            'history_size_mb': history_size / (1024 * 1024),
            'redo_size_mb': redo_size / (1024 * 1024),
            'current_size_mb': current_size / (1024 * 1024),
            'total_size_mb': total_size / (1024 * 1024)
        }

    def __str__(self) -> str:
        """String representation of the history manager state"""
        return (
            f"HistoryManager(history={len(self._history_stack)}, "
            f"redo={len(self._redo_stack)}, max={self._max_history})"
        )

    def __repr__(self) -> str:
        """Detailed representation of the history manager"""
        return self.__str__()