"""
Main table widget for the urw-scroll-table package.

This module contains the UrwScrollTable class, which is the main scrollable
and editable table widget.
"""

import urwid
from .widgets import (
    SingleLineText,
    EditableCell,
    PopupDropdownCell,
)


class UrwScrollTable(urwid.WidgetWrap):
    """A scrollable table widget with editable cells."""

    def __init__(self, headers, data, max_width=80, max_height=20,
                 edit_color='yellow', column_types=None, colors=None,
                 dropdown_options=None):
        """
        Initialize the scrollable editable table widget.

        Args:
            headers: List of header strings
            data: List of lists containing row data
            max_width: Maximum width of the widget
            max_height: Maximum height of the widget
            edit_color: Background color for editing cells (default: 'yellow')
            column_types: List of column types ('text', 'editable', 'dropdown')
                         or dict mapping column indices to types
            colors: Dictionary of custom colors for various table elements
            dropdown_options: Dictionary mapping column indices to lists of
                               options
        """
        self.headers = headers
        self.data = data
        self.max_width = max_width
        self.max_height = max_height
        self.edit_color = edit_color
        self.horizontal_offset = 0
        self.vertical_offset = 0
        self.current_row = 0
        self.current_col = 0
        self.editing = False
        self.column_widths = self._calculate_column_widths()
        self.edit_widgets = {}  # Store edit widgets to maintain state

        # Process column types
        self.column_types = self._process_column_types(column_types)

        # Process dropdown options
        self.dropdown_options = dropdown_options or {}

        # Colors dictionary with keys: header_fg, header_bg, cell_fg, cell_bg,
        # active_cell_fg, active_cell_bg, editing_cell_fg, editing_cell_bg
        self.colors = colors or {}

        # Create table widgets
        self.table_widgets = []
        self.header_widget = None
        self._create_table_widgets()

        # Create the list box for data rows only
        self.listbox = urwid.ListBox(
            urwid.SimpleFocusListWalker(self.table_widgets)
        )

        # Create a custom widget that combines header and listbox
        self.main_widget = self._create_main_widget()

        super().__init__(self.main_widget)

    def _create_main_widget(self):
        """Create the main widget that combines header and listbox."""
        # Create a custom widget that handles header and listbox
        class TableWithHeader(urwid.WidgetWrap):
            def __init__(self, header_widget, listbox, table):
                self.header_widget = header_widget
                self.listbox = listbox
                self.table = table
                super().__init__(self.listbox)

            def render(self, size, focus=False):
                # Render header first
                if isinstance(size, tuple) and len(size) > 1:
                    width, height = size
                    header_size = (width, 1)
                    data_size = (width, height - 1)
                else:
                    width = size
                    header_size = (width, 1)
                    data_size = (width, 20)  # Default height

                # Render header
                header_canvas = self.header_widget.render(header_size, False)

                # Render listbox
                listbox_canvas = self.listbox.render(data_size, focus)

                # Combine canvases - ensure proper format
                canvas_info = []
                if header_canvas:
                    canvas_info.append((header_canvas, 0, 0))
                if listbox_canvas:
                    canvas_info.append((listbox_canvas, 0, 1))

                combined_canvas = urwid.CanvasCombine(canvas_info)

                return combined_canvas

            def keypress(self, size, key):
                # Delegate keypress to the main table
                return self.table.keypress(size, key)

        return TableWithHeader(self.header_widget, self.listbox, self)

    def _calculate_column_widths(self):
        """Calculate the width needed for each column."""
        widths = []
        for col_idx in range(len(self.headers)):
            # Start with header width
            max_width = len(self.headers[col_idx])

            # Check all data rows for this column
            for row_data in self.data:
                if col_idx < len(row_data):
                    cell_width = len(str(row_data[col_idx]))
                    max_width = max(max_width, cell_width)

            widths.append(max_width)
        return widths

    def _process_column_types(self, column_types):
        """Process column types and return a dictionary."""
        if column_types is None:
            return {i: 'text' for i in range(len(self.headers))}

        if isinstance(column_types, dict):
            return column_types

        if isinstance(column_types, list):
            # Convert list of types to a dict mapping indices to types
            return {i: t for i, t in enumerate(column_types)}

        raise ValueError(
            "column_types must be None, a dict, or a list of types."
        )

    def _get_visible_columns(self, available_width):
        """Get the list of columns that can be displayed
        with current offset.
        """
        visible_cols = []
        current_width = 0

        for col_idx in range(self.horizontal_offset, len(self.headers)):
            # +2 for padding
            col_width = self.column_widths[col_idx] + 2
            if current_width + col_width <= available_width:
                visible_cols.append(col_idx)
                current_width += col_width
            else:
                break

        return visible_cols

    def _create_cell_widget(self, row_idx, col_idx, cell_data):
        """Create a cell widget based on column type."""
        column_type = self.column_types.get(col_idx, 'text')

        if column_type == 'dropdown':
            # For dropdown, just return the current selection as text
            if isinstance(cell_data, list) and cell_data:
                return str(cell_data[0]) if cell_data else ""
            else:
                return str(cell_data)
        elif column_type == 'editable':
            # For editable cells, return the current text
            return str(cell_data)
        else:
            # For text cells, return the data as string
            return str(cell_data)

    def _get_dropdown_options(self, col_idx):
        """Get dropdown options for a specific column."""
        # Check if options are provided in dropdown_options
        if col_idx in self.dropdown_options:
            return self.dropdown_options[col_idx]

        # Fallback to default options for backward compatibility
        if col_idx == 2:  # Department column
            return ['Engineering Department', 'Marketing Department',
                    'Sales Department', 'Human Resources',
                    'Finance Department', 'IT Department',
                    'Operations Department', 'Legal Department']
        elif col_idx == 3:  # Status column
            return ['Active', 'Inactive', 'Pending']
        elif col_idx == 4:  # Priority Level column
            return ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        else:
            # Default options - you can customize this
            return []

    def _create_table_widgets(self):
        """Create table widgets with current offsets."""
        self.table_widgets = []

        # Estimate available width (we'll get actual size during render)
        available_width = self.max_width or 80

        # Get visible columns based on current horizontal offset
        visible_cols = self._get_visible_columns(available_width)

        # Create header row (always visible)
        if visible_cols:
            # Check if any visible columns are dropdowns
            has_dropdown = any(
                self.column_types.get(col_idx) == 'dropdown'
                for col_idx in visible_cols
            )

            if has_dropdown:
                # Use urwid.Columns for consistency with dropdown rows
                header_parts = []
                for col_idx in visible_cols:
                    header = self.headers[col_idx]
                    header_width = self.column_widths[col_idx]
                    header_text = header[:header_width].ljust(header_width + 2)
                    header_parts.append(urwid.Text(header_text))

                self.header_widget = urwid.AttrMap(
                    urwid.Columns(header_parts, dividechars=0),
                    'header'
                )
            else:
                # Use single text widget for text-only columns
                header_text = ""
                for col_idx in visible_cols:
                    header = self.headers[col_idx]
                    header_width = self.column_widths[col_idx]
                    header_text += header[:header_width].ljust(header_width + 2)  # noqa: E501

                self.header_widget = urwid.AttrMap(
                    SingleLineText(header_text),
                    'header'
                )

        # Create data rows (only visible ones)
        # -1 for header
        visible_rows = min(
            self.max_height - 1, len(self.data) - self.vertical_offset
        )
        for i in range(visible_rows):
            row_idx = self.vertical_offset + i
            if row_idx < len(self.data):
                row_data = self.data[row_idx]
                # Check if this row contains the currently editing cell
                is_editing_row = (row_idx == self.current_row and
                                  self.current_col in visible_cols and
                                  self.editing)

                if is_editing_row:
                    # Create a row with the editing widget
                    self._create_editing_row(row_idx, row_data, visible_cols)
                else:
                    # Create a normal text-based row
                    self._create_text_row(row_idx, row_data, visible_cols)

    def _create_editing_row(self, row_idx, row_data, visible_cols):
        """Create a row widget for editing."""
        # For editing, we need to create a special row that can handle input
        # We'll use a simple approach: create a text representation with the
        # editing cell highlighted
        row_text = ""
        edit_widget = None

        for col_idx in visible_cols:
            if col_idx < len(row_data):
                cell_data = row_data[col_idx]
                column_type = self.column_types.get(col_idx, 'text')

                if (col_idx == self.current_col and
                        row_idx == self.current_row and
                        self.editing):
                    # This is the cell being edited
                    if column_type == 'dropdown':
                        # Create dropdown widget
                        options = self._get_dropdown_options(col_idx)
                        edit_widget = PopupDropdownCell(
                            content=cell_data,
                            options=options,
                            on_change=lambda text: self._on_cell_change(
                                row_idx, col_idx, text
                            )
                        )
                    elif column_type == 'editable':
                        # Create editable text widget
                        edit_widget = EditableCell(
                            content=cell_data,
                            on_change=lambda text: self._on_cell_change(
                                row_idx, col_idx, text
                            )
                        )

                    # Store the edit widget
                    self.edit_widgets[(row_idx, col_idx)] = edit_widget

                    # Show a placeholder for the edit widget
                    cell_text = "[EDITING]"
                else:
                    # Show normal cell content
                    if column_type == 'dropdown':
                        # Show current selection
                        if isinstance(cell_data, list) and cell_data:
                            cell_text = str(cell_data[0])
                        else:
                            cell_text = str(cell_data)
                    elif column_type == 'editable':
                        # Show current text
                        cell_text = str(cell_data)
                    else:
                        # Show text data
                        cell_text = str(cell_data)

                # Truncate to fit column width
                cell_text = cell_text[:self.column_widths[col_idx]]
                cell_width = self.column_widths[col_idx]
                cell_text = cell_text.ljust(cell_width + 2)
                row_text += cell_text
            else:
                cell_width = self.column_widths[col_idx]
                row_text += " " * (cell_width + 2)

        # Create the row widget
        if edit_widget:
            # If we have an edit widget, use it
            row_widget = edit_widget
        else:
            # Otherwise use text
            row_widget = SingleLineText(row_text)

        row_widget = urwid.AttrMap(row_widget, 'edit')
        self.table_widgets.append(row_widget)

    def _create_text_row(self, row_idx, row_data, visible_cols):
        """Create a row widget for display."""
        row_parts = []

        for col_idx in visible_cols:
            if col_idx < len(row_data):
                cell_data = row_data[col_idx]
                column_type = self.column_types.get(col_idx, 'text')

                if column_type == 'dropdown':
                    # Create PopupDropdownCell for dropdown columns
                    options = self._get_dropdown_options(col_idx)

                    class CellCallback:
                        def __init__(self, table, row, col):
                            self.table = table
                            self.row = row
                            self.col = col

                        def __call__(self, text):
                            self.table._on_cell_change(
                                self.row,
                                self.col,
                                text)

                    dropdown_widget = PopupDropdownCell(
                        content=str(cell_data),
                        options=options,
                        on_change=CellCallback(self, row_idx, col_idx),
                        max_width=self.column_widths[col_idx] + 2
                    )

                    # Apply highlighting if this is the current cell
                    if (row_idx == self.current_row and col_idx == self.current_col):  # noqa: E501
                        dropdown_widget = urwid.AttrMap(
                            dropdown_widget,
                            'selected')

                    row_parts.append(dropdown_widget)
                else:
                    # Handle text-based columns
                    if column_type == 'editable':
                        cell_text = str(cell_data)
                    else:
                        cell_text = str(cell_data)

                    # Truncate to fit column width
                    cell_text = cell_text[:self.column_widths[col_idx]]
                    cell_width = self.column_widths[col_idx]
                    cell_text = cell_text.ljust(cell_width + 2)

                    # Create text widget for urwid.Columns
                    if (row_idx == self.current_row and
                            col_idx == self.current_col):
                        # Highlight the current cell
                        text_widget = urwid.AttrMap(
                            urwid.Text(cell_text), 'selected'
                        )
                    else:
                        # Normal cell
                        text_widget = urwid.Text(cell_text)

                    row_parts.append(text_widget)
            else:
                # Empty cell - create text widget
                cell_width = self.column_widths[col_idx]
                empty_text = " " * (cell_width + 2)
                empty_widget = urwid.Text(empty_text)
                row_parts.append(empty_widget)

        # Create the row widget
        has_dropdown = any(
            isinstance(part, PopupDropdownCell) or
            (hasattr(part, 'original_widget') and isinstance(part.original_widget, PopupDropdownCell))  # noqa: E501
            for part in row_parts
        )
        if has_dropdown:
            # Mixed content - use urwid.Columns for layout
            row_widget = urwid.Columns(row_parts, dividechars=0)
        else:
            # All text - extract text content from widgets
            row_text_parts = []
            for part in row_parts:
                if hasattr(part, 'text'):
                    # urwid.Text widget
                    row_text_parts.append(part.text)
                elif hasattr(part, 'original_widget') and hasattr(part.original_widget, 'text'):  # noqa: E501
                    # urwid.AttrMap wrapping urwid.Text
                    row_text_parts.append(part.original_widget.text)
                else:
                    # Fallback - convert to string
                    row_text_parts.append(str(part))
            row_text = "".join(row_text_parts)
            row_widget = SingleLineText(row_text)

        self.table_widgets.append(row_widget)

    def _get_half_page_size(self):
        """Calculate half the visible page size based on max_height."""
        # Use max_height as the page size, or default to 20 if not set
        page_size = self.max_height or 20
        # Return half the page size, but at least 1
        return max(1, page_size // 2)

    def _ensure_current_cell_visible(self, available_width=None):
        """Ensure the current cell is visible by adjusting offsets
        if needed.
        """
        if available_width is None:
            available_width = self.max_width or 80

        # Ensure current row is visible vertically (account for header)
        available_data_height = self.max_height - 1  # -1 for header
        if self.current_row < self.vertical_offset:
            # Current row is above visible area, scroll up
            self.vertical_offset = self.current_row
        elif self.current_row >= self.vertical_offset + available_data_height:
            # Current row is below visible area, scroll down
            self.vertical_offset = max(
                0, self.current_row - available_data_height + 1
            )

        # Get current visible columns
        visible_cols = self._get_visible_columns(available_width)

        # If current column is not visible, adjust horizontal offset
        if self.current_col not in visible_cols:
            if self.current_col < self.horizontal_offset:
                # Current column is to the left, scroll left
                self.horizontal_offset = max(0, self.current_col)
            else:
                # Current column is to the right, scroll right
                # Calculate how many columns we can show
                total_width = 0
                cols_to_show = []
                for col_idx in range(self.current_col, -1, -1):
                    col_width = self.column_widths[col_idx] + 2
                    if total_width + col_width <= available_width:
                        cols_to_show.insert(0, col_idx)
                        total_width += col_width
                    else:
                        break

                if cols_to_show:
                    self.horizontal_offset = cols_to_show[0]

    def _update_display(self, available_width=None):
        """Update the display with current offsets."""
        # Ensure current cell is visible
        self._ensure_current_cell_visible(available_width)

        # Recreate table widgets with new offsets
        self._create_table_widgets()

        # Update the listbox with new widgets
        self.listbox.body = urwid.SimpleFocusListWalker(self.table_widgets)

        # Recreate the main widget with updated header and listbox
        self.main_widget = self._create_main_widget()
        self._w = self.main_widget

        # Maintain current focus position (adjust for header)
        focus_row = self.current_row - self.vertical_offset
        if 0 <= focus_row < len(self.table_widgets):
            self.listbox.set_focus(focus_row)

    def render(self, size, focus=False):
        """Override render to get actual available width."""
        if len(size) > 0:
            available_width = size[0]
            # Only update display if width has changed
            if self.max_width != available_width:
                self.max_width = available_width
                self._update_display(available_width)
        return super().render(size, focus)

    def _on_cell_change(self, row, col, new_value):
        """Handle cell value changes."""
        if row < len(self.data) and col < len(self.data[row]):
            self.data[row][col] = new_value
            self.editing = False
            self._update_display()

    def selectable(self):
        """Return True to indicate this widget can receive focus."""
        return True

    def keypress(self, size, key):
        """Handle keypress events."""
        # Handle all keypress events ourselves since we have a custom structure
        if self.editing:
            # We're currently editing - handle edit-specific keys
            if key == 'esc':
                # Cancel editing
                self.editing = False
                self._update_display()
                return None
            elif key == 'enter':
                # Finish editing - get the current value and save it
                cell_key = (self.current_row, self.current_col)
                if cell_key in self.edit_widgets:
                    edit_widget = self.edit_widgets[cell_key]
                    # Get the current value from the edit widget
                    if hasattr(edit_widget, 'get_edit_text'):
                        current_value = edit_widget.get_edit_text()
                    else:
                        current_value = edit_widget.get_text()

                    # Save the value
                    self._on_cell_change(
                        self.current_row, self.current_col, current_value
                    )
                else:
                    # No edit widget found, just exit editing mode
                    self.editing = False
                    self._update_display()
                return None
            else:
                # Pass the key to the current edit widget
                cell_key = (self.current_row, self.current_col)
                if cell_key in self.edit_widgets:
                    edit_widget = self.edit_widgets[cell_key]

                    # Extract width from size tuple for edit widgets
                    edit_size = (
                        (size[0],) if isinstance(size, tuple) else (size,)
                    )
                    result = edit_widget.keypress(edit_size, key)
                    if result is None:
                        # Key was handled by the edit widget
                        return None
                    return result
                else:
                    # No edit widget found, cancel editing
                    self.editing = False
                    self._update_display()
                    return None
        else:
            # Check if a dropdown popup is open and
            # delegate keypress events to it
            dropdown_widget = self._get_current_dropdown_widget()
            if dropdown_widget \
               and hasattr(dropdown_widget, '_pop_up_widget') \
               and dropdown_widget._pop_up_widget:
                # Popup is open, delegate keypress events
                # to the dropdown widget
                result = dropdown_widget.keypress(size, key)
                if result is None:
                    return None
                # If the popup handled the key, we're done
                if key in \
                   ['up', 'down', 'page up', 'page down', 'enter', 'esc']:
                    return None

            # Normal navigation mode
            if key == 'enter':
                # Check if current cell is a dropdown
                column_type = self.column_types.get(self.current_col, 'text')
                if column_type == 'dropdown':
                    # For dropdown cells, we need to delegate
                    # to the PopupDropdownCell widget
                    # Since we can't easily access the widget directly,
                    # we'll trigger the popup by simulating
                    # the widget's behavior
                    self._trigger_dropdown_popup()
                    return None
                else:
                    # Start editing the current cell
                    self._start_editing_current_cell()
                    return None
            elif key == 'up':
                if self.current_row > 0:
                    self.current_row -= 1
                    self._ensure_current_cell_visible()
                    self._update_display()
                return None
            elif key == 'down':
                if self.current_row < len(self.data) - 1:
                    self.current_row += 1
                    self._ensure_current_cell_visible()
                    self._update_display()
                return None
            elif key == 'left':
                if self.current_col > 0:
                    self.current_col -= 1
                    self._ensure_current_cell_visible()
                    self._update_display()
                return None
            elif key == 'right':
                if self.current_col < len(self.headers) - 1:
                    self.current_col += 1
                    self._ensure_current_cell_visible()
                    self._update_display()
                return None
            elif key == 'page up':
                # Scroll up by half page
                half_page_size = self._get_half_page_size()
                self.vertical_offset = max(
                    0, self.vertical_offset - half_page_size
                )
                # Adjust current row to keep it visible
                self.current_row = max(
                    0, self.current_row - half_page_size
                )
                self._ensure_current_cell_visible()
                self._update_display()
                return None
            elif key == 'page down':
                # Scroll down by half page
                half_page_size = self._get_half_page_size()
                # -1 for header
                available_data_height = self.max_height - 1
                max_offset = max(0, len(self.data) - available_data_height)
                self.vertical_offset = min(
                    max_offset, self.vertical_offset + half_page_size
                )
                # Adjust current row to keep it visible
                self.current_row = min(
                    len(self.data) - 1, self.current_row + half_page_size
                )
                self._ensure_current_cell_visible()
                self._update_display()
                return None
            elif key == 'q':
                raise urwid.ExitMainLoop()

        return key

    def _get_current_dropdown_widget(self):
        """Get the dropdown widget for the current cell."""
        # Find the PopupDropdownCell widget for the current cell
        # The widget is in the listbox at the current row

        # Calculate the table widget index for the current row
        # table_widgets[i] corresponds to data row (vertical_offset + i)
        table_widget_index = self.current_row - self.vertical_offset

        if 0 <= table_widget_index < len(self.table_widgets):
            row_widget = self.table_widgets[table_widget_index]

            # If the row widget is a Columns widget, find the dropdown cell
            if hasattr(row_widget, 'contents'):
                # This is a urwid.Columns widget
                # We need to find the visible column index for current_col
                visible_cols = self._get_visible_columns(self.max_width or 80)
                try:
                    visible_col_index = visible_cols.index(self.current_col)
                    if visible_col_index < len(row_widget.contents):
                        widget, options = row_widget.contents[visible_col_index]  # noqa: E501
                        if hasattr(widget, 'open_pop_up'):
                            # This is a PopupDropdownCell
                            return widget
                        elif hasattr(widget, 'original_widget') and hasattr(widget.original_widget, 'open_pop_up'):  # noqa: E501
                            # This is a PopupDropdownCell wrapped in AttrMap
                            return widget.original_widget
                except ValueError:
                    # current_col is not in visible columns
                    pass
        return None

    def _trigger_dropdown_popup(self):
        """Trigger popup for dropdown cell at current position."""
        dropdown_widget = self._get_current_dropdown_widget()
        if dropdown_widget:
            dropdown_widget.open_pop_up()

    def _start_editing_current_cell(self):
        """Start editing the current cell."""
        if self.current_row >= len(self.data):
            return

        if self.current_col >= len(self.data[self.current_row]):
            return

        column_type = self.column_types.get(self.current_col, 'text')

        if column_type == 'text':
            # Text cells are not editable
            return

        # Start editing mode
        self.editing = True

        # Create an overlay with the edit widget
        self._show_edit_overlay()

        # Update the display
        self._update_display()

    def _show_edit_overlay(self):
        """Show an overlay for editing the current cell."""
        # Get the current cell data
        cell_data = self.data[self.current_row][self.current_col]
        column_type = self.column_types.get(self.current_col, 'text')

        if column_type == 'dropdown':
            # Create dropdown widget
            options = self._get_dropdown_options(self.current_col)
            edit_widget = PopupDropdownCell(
                content=cell_data,
                options=options,
                on_change=lambda text: self._on_cell_change(
                    self.current_row, self.current_col, text
                )
            )
        elif column_type == 'editable':
            # Create editable text widget
            edit_widget = EditableCell(
                content=cell_data,
                on_change=lambda text: self._on_cell_change(
                    self.current_row, self.current_col, text
                )
            )
        else:
            return

        # Store the edit widget
        self.edit_widgets[(self.current_row, self.current_col)] = edit_widget

        # For now, we'll just update the display to show the editing state
        # The actual editing will happen when the user interacts with
        # the edit widget

    def get_all_data(self):
        """
        Get all current table data.

        Returns:
            List of lists containing all row data
        """
        # Return a copy to prevent external modification
        return [row[:] for row in self.data]

    def get_row_data(self, row_index):
        """
        Get data for a specific row.

        Args:
            row_index: Index of the row to retrieve

        Returns:
            List containing the row data, or None if index is invalid
        """
        if 0 <= row_index < len(self.data):
            return self.data[row_index][:]  # Return a copy
        return None

    def get_cell_value(self, row_index, col_index):
        """
        Get value of a specific cell.

        Args:
            row_index: Index of the row
            col_index: Index of the column

        Returns:
            Cell value, or None if indices are invalid
        """
        if (0 <= row_index < len(self.data) and
                0 <= col_index < len(self.data[row_index])):
            return self.data[row_index][col_index]
        return None

    def get_headers(self):
        """
        Get the table headers.

        Returns:
            List of header strings
        """
        return self.headers[:]  # Return a copy

    def get_table_info(self):
        """
        Get comprehensive table information.

        Returns:
            Dictionary containing:
            - headers: List of header strings
            - data: List of lists containing all row data
            - dimensions: Tuple of (rows, columns)
            - current_position: Tuple of (current_row, current_col)
            - column_types: Dictionary mapping column indices to types
        """
        return {
            'headers': self.get_headers(),
            'data': self.get_all_data(),
            'dimensions': (len(self.data), len(self.headers)),
            'current_position': (self.current_row, self.current_col),
            'column_types': self.column_types.copy()
        }
