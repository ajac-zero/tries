"""Terminal User Interface for try experiment selector."""

import curses
from pathlib import Path
from typing import Optional

from .directories import get_all_experiments, touch_experiment
from .scoring import ScoredDirectory, score_directories


class TUISelector:
    """Interactive fuzzy selector for try experiments."""

    def __init__(self):
        self.query = ""
        self.selected_idx = 0
        self.results: list[ScoredDirectory] = []
        self.all_dirs: list[Path] = []

    def run(self, initial_query: str = "") -> Optional[Path]:
        """Run the TUI selector.

        Args:
            initial_query: Initial search query

        Returns:
            Selected directory path or None if cancelled
        """
        self.query = initial_query
        self.all_dirs = get_all_experiments()

        # If initial query provided, update results and check for auto-select
        if initial_query:
            self._update_results()
            # Auto-select if top result is a perfect fuzzy match
            if self.results and self.results[0].fuzzy_score >= 0.99:
                selected_path = self.results[0].path
                touch_experiment(selected_path)
                return selected_path
            # If no fuzzy matches (query doesn't match any directory), return None to let caller decide
            if not self.results or self.results[0].fuzzy_score == 0.0:
                return None

        try:
            result = curses.wrapper(self._run_curses)
            return result
        except KeyboardInterrupt:
            return None

    def _run_curses(self, stdscr: "curses.window") -> Optional[Path]:
        """Main TUI loop (requires curses context)."""
        # Configure curses
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(True)  # Non-blocking input

        # Color pairs
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Selected
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Normal
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Query
        curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # Match highlight

        self._update_results()

        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            # Draw search box
            stdscr.addstr(0, 0, "Search: ", curses.color_pair(3))
            stdscr.addstr(0, 8, self.query, curses.color_pair(3))
            stdscr.addstr(
                0, min(8 + len(self.query), width - 1), "█", curses.color_pair(3)
            )

            # Draw results
            result_start = 2
            result_height = height - result_start - 2

            for i, scored_dir in enumerate(self.results[:result_height]):
                if i >= result_height:
                    break

                y = result_start + i
                is_selected = i == self.selected_idx

                # Build display line
                line = self._format_result_line(scored_dir, width - 2)

                attr = curses.color_pair(1) if is_selected else curses.color_pair(2)
                if is_selected:
                    attr |= curses.A_BOLD

                stdscr.addstr(y, 0, line, attr)

            # Draw footer
            footer = "↑/↓ or Ctrl-P/N to navigate | Enter to select | ESC to cancel | Ctrl-D to delete"
            if height > result_start + result_height + 1:
                footer_line = height - 1
                stdscr.addstr(
                    footer_line,
                    0,
                    footer[: width - 1],
                    curses.color_pair(2) | curses.A_DIM,
                )

            stdscr.refresh()

            # Handle input
            key = stdscr.getch()

            if key == -1:  # No input
                continue
            elif key == 27:  # ESC
                return None
            elif (
                key == curses.KEY_UP or key == ord("p") - 96 or key == ord("k")
            ):  # Ctrl-P, Ctrl-N, j/k
                self.selected_idx = max(0, self.selected_idx - 1)
            elif key == curses.KEY_DOWN or key == ord("n") - 96 or key == ord("j"):
                self.selected_idx = min(len(self.results) - 1, self.selected_idx + 1)
            elif key == curses.KEY_BACKSPACE or key == 127:  # Backspace
                if self.query:
                    self.query = self.query[:-1]
                    self._update_results()
                    self.selected_idx = 0
            elif key == curses.KEY_ENTER or key == ord("\n") or key == ord("\r"):
                if self.results:
                    selected_path = self.results[self.selected_idx].path
                    touch_experiment(selected_path)
                    return selected_path
                return None
            elif key == ord("d") - 96:  # Ctrl-D
                if self.results:
                    # Would trigger delete (handled by caller)
                    return None
            elif 32 <= key <= 126:  # Printable ASCII
                self.query += chr(key)
                self._update_results()
                self.selected_idx = 0

    def _update_results(self) -> None:
        """Update scored results based on current query."""
        if self.query:
            self.results = score_directories(
                self.query,
                self.all_dirs,
                min_score=0.1,  # Only show decent matches
            )
        else:
            # Show all directories sorted by recency
            self.results = score_directories("", self.all_dirs)

        self.selected_idx = min(self.selected_idx, max(0, len(self.results) - 1))

    def _format_result_line(self, scored: ScoredDirectory, max_width: int) -> str:
        """Format a result line for display."""
        # Highlight matched characters in the name
        name = scored.name
        score_pct = int(scored.score * 100)

        # Simple format: name [score]
        score_str = f" [{score_pct}%]"
        available_width = max_width - len(score_str)

        if len(name) > available_width:
            name = name[: available_width - 3] + "..."

        line = name.ljust(available_width) + score_str
        return line[:max_width]
