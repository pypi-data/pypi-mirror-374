"""
Widget classes for the urw-scroll-table package.

This module contains all the supporting widget classes used by the main table.
"""

import urwid


class SafeText(urwid.Text):
    """A text widget that safely handles size parameters."""

    def render(self, size, focus=False):
        """Override render to handle size parameter correctly."""
        if isinstance(size, tuple) and len(size) > 1:
            # If we get a tuple with multiple values, use only the first one
            size = (size[0],)
        return super().render(size, focus)

    def rows(self, size, focus=False):
        """Override rows to handle size parameter correctly."""
        if isinstance(size, tuple) and len(size) > 1:
            # Use only the width for calculating rows
            size = (size[0],)
        return super().rows(size, focus)

    def pack(self, size=None, focus=False):
        """Override pack to handle size parameter correctly."""
        if isinstance(size, tuple) and len(size) > 1:
            # If we get a tuple with multiple values, use only the first one
            size = (size[0],)
        return super().pack(size, focus)


class SingleLineText(urwid.Text):
    """A text widget that always renders as a single line."""

    def __init__(self, text):
        # Replace newlines with spaces to ensure single line
        if isinstance(text, str):
            text = text.replace('\n', ' ')
        super().__init__(text)

    def rows(self, size, focus=False):
        """Always return 1 row."""
        return 1

    def render(self, size, focus=False):
        """Render the widget, ensuring only width is considered."""
        # Extract width from size tuple
        if isinstance(size, tuple) and len(size) > 1:
            size = (size[0],)
        return super().render(size, focus)


class HeightEnforcer(urwid.WidgetWrap):
    """
    A wrapper that forces any widget to always return
    exactly 1 row height.
    """

    def __init__(self, widget):
        super().__init__(widget)

    def rows(self, size, focus=False):
        """Always return 1 row, regardless of the wrapped widget."""
        return 1


class EditableCell(urwid.Edit):
    """A cell widget that can be edited."""

    def __init__(self, content="", on_change=None):
        # Convert content to string if it's not already
        if not isinstance(content, str):
            content = str(content)

        super().__init__("", content)
        self._original_content = content
        self.on_change = on_change

    def get_edit_text(self):
        """Get the current edit text."""
        return super().get_edit_text()

    def set_edit_text(self, text):
        """Set the edit text."""
        # Convert text to string if it's not already
        if not isinstance(text, str):
            text = str(text)
        super().set_edit_text(text)

    def keypress(self, size, key):
        """Handle keypress events."""
        # Let the parent Edit widget handle all keypresses
        # Enter and Esc are handled at the table level
        result = super().keypress(size, key)
        if result is None:
            # Key was handled, update original content
            self._original_content = self.get_edit_text()
        return result

    def render(self, size, focus=False):
        """Render the widget."""
        # Ensure size is a single value for width
        if isinstance(size, tuple) and len(size) > 1:
            size = (size[0],)
        return super().render(size, focus)

    def rows(self, size, focus=False):
        """Return the number of rows."""
        # Always return 1 row
        return 1

    def pack(self, size, focus=False):
        """Pack the widget."""
        # Ensure size is a single value for width
        if isinstance(size, tuple) and len(size) > 1:
            size = (size[0],)
        return super().pack(size, focus)


class DropdownCell(urwid.WidgetWrap):
    """A dropdown cell widget with compact inline display."""

    def __init__(self, content="", options=None, on_change=None):
        """
        Initialize dropdown cell.

        Args:
            content: Current selected value
            options: List of available options
            on_change: Callback function when selection changes
        """
        self.options = options or []
        self.on_change = on_change
        self._original_content = content
        self.current_index = self._get_index_for_content(content)
        self.expanded = False

        # Create the main text widget
        self.text_widget = SingleLineText(content)
        self._update_display()

        # Start with the text widget
        super().__init__(self.text_widget)

    def _get_index_for_content(self, content):
        """Get the index for the given content."""
        try:
            return self.options.index(content)
        except ValueError:
            return 0 if self.options else -1

    def _update_display(self):
        """Update the display text."""
        if self.expanded:
            # Show compact dropdown display
            self._show_compact_dropdown()
        else:
            # Show single line with current selection
            if self.options and 0 <= self.current_index < len(self.options):
                display_text = self.options[self.current_index]
            else:
                display_text = self._original_content

            display_text += " ▶"
            self.text_widget.set_text(display_text)
            self._w = self.text_widget

    def _show_compact_dropdown(self):
        """Show a compact dropdown display that fits in the cell."""
        if not self.options:
            self.text_widget.set_text("No options ▶")
            self._w = self.text_widget
            return

        # Show current selection and navigation hint
        if 0 <= self.current_index < len(self.options):
            current_text = f"▶ {self.options[self.current_index]}"
        else:
            current_text = "▶ No selection"

        # Add navigation hint
        hint = f" (↑↓ {self.current_index + 1}/{len(self.options)})"

        # Truncate if too long
        max_len = 35  # Adjust based on typical cell width
        if len(current_text) + len(hint) > max_len:
            current_text = current_text[:max_len - len(hint)] + "..."

        display_text = current_text + hint
        self.text_widget.set_text(display_text)
        self._w = self.text_widget

    def keypress(self, size, key):
        """Handle keypress events."""
        if not self.options:
            return key

        if key == 'enter':
            if self.expanded:
                # Select current option and close dropdown
                if 0 <= self.current_index < len(self.options):
                    selected_value = self.options[self.current_index]
                    self._original_content = selected_value
                    # Don't call on_change here - handled by table
                self.expanded = False
                self._update_display()
                return None
            else:
                # Open dropdown
                self.expanded = True
                self._update_display()
                return None
        elif key == 'esc':
            # Cancel editing - restore original content
            self.expanded = False
            self.current_index = self._get_index_for_content(
                self._original_content
            )
            self._update_display()
            # Don't call on_change here - handled by table
            return None
        elif key == 'up' and self.expanded:
            # Move up in dropdown
            if self.current_index > 0:
                self.current_index -= 1
                self._update_display()
            return None
        elif key == 'down' and self.expanded:
            # Move down in dropdown
            if self.current_index < len(self.options) - 1:
                self.current_index += 1
                self._update_display()
            return None
        else:
            return key

    def render(self, size, focus=False):
        """Override render to handle size parameter correctly."""
        if isinstance(size, tuple) and len(size) > 1:
            # If we get a tuple with multiple values, use only the first one
            size = (size[0],)
        return super().render(size, focus)

    def rows(self, size, focus=False):
        """Override rows to handle size parameter correctly."""
        if isinstance(size, tuple) and len(size) > 1:
            # Use only the width for calculating rows
            size = (size[0],)

        # Always return 1 row - compact display
        return 1

    def get_edit_text(self):
        """Get the current selected value."""
        if self.expanded and 0 <= self.current_index < len(self.options):
            return self.options[self.current_index]
        else:
            return self._original_content


# Create a custom listbox that handles cursor keys, page up/down, Enter and Esc
class DropdownListBox(urwid.ListBox):
    def __init__(self, body, dropdown):
        super().__init__(body)
        self.dropdown = dropdown

    def keypress(self, size, key):
        if key == 'enter':
            # Select current option
            try:
                focus_widget = self.get_focus()[0]
                if hasattr(focus_widget, 'original_widget'):
                    # Handle SelectableIcon wrapped in AttrMap
                    selectable_icon = focus_widget.original_widget
                    if hasattr(selectable_icon, 'text'):
                        option_text = selectable_icon.text.strip()
                        # Clean up markers
                        if option_text.startswith('▶'):
                            option_text = option_text[2:].strip()
                        elif option_text.startswith('  '):
                            option_text = option_text[2:].strip()

                        # Find the option index
                        try:
                            option_index = (
                                self.dropdown.options.index(option_text)
                            )
                            self.dropdown._select_option(
                                option_index, option_text
                            )
                        except ValueError:
                            pass
            except Exception:
                pass
            return None
        elif key == 'esc':
            # Cancel selection
            self.dropdown.close_pop_up()
            return None
        else:
            # Handle navigation (up/down arrow keys)
            result = super().keypress(size, key)
            if result is None:
                # Key was handled, update display to show current selection
                self._update_selection_display()
            return result

    def _update_selection_display(self):
        """Update the display to show current selection with ▶ marker."""
        try:
            focus_index = self.get_focus()[1]
            for i, widget in enumerate(self.body):
                if hasattr(widget, 'original_widget'):
                    selectable_icon = widget.original_widget
                    if hasattr(selectable_icon, 'text'):
                        # Get the option text without markers
                        option_text = selectable_icon.text.strip()
                        if option_text.startswith('▶'):
                            option_text = option_text[2:].strip()
                        elif option_text.startswith('  '):
                            option_text = option_text[2:].strip()

                        # Update the text with proper marker
                        if i == focus_index:
                            selectable_icon.set_text(f"▶ {option_text}")
                            widget.set_attr_map({None: 'popup_selected'})
                        else:
                            selectable_icon.set_text(f"  {option_text}")
                            widget.set_attr_map({None: 'popup'})
        except Exception:
            # If there's an error updating display, just continue
            pass


class PopupDropdownCell(urwid.PopUpLauncher):
    """A dropdown cell widget using urwid's popup functionality."""

    def __init__(self,
                 content="",
                 options=None,
                 on_change=None,
                 max_width=None):
        """
        Initialize popup dropdown cell.

        Args:
            content: Current selected value
            options: List of available options
            on_change: Callback function when selection changes
            max_width: Maximum width for the display text
        """
        self.options = options or []
        self.on_change = on_change
        self._original_content = content
        self.current_index = self._get_index_for_content(content)
        self.max_width = max_width

        # Create the main text widget showing current selection
        self.text_widget = urwid.Text(self._get_display_text(max_width))

        # Initialize the PopUpLauncher with our text widget
        super().__init__(self.text_widget)

    def _get_index_for_content(self, content):
        """Get the index for the given content."""
        try:
            return self.options.index(content)
        except ValueError:
            return 0 if self.options else -1

    def _get_display_text(self, max_width=None):
        """Get the display text for the current selection."""
        if self.options and 0 <= self.current_index < len(self.options):
            text = self.options[self.current_index] + " ▼"
        else:
            text = self._original_content + " ▼"

        # Truncate if max_width is specified
        if max_width is not None and len(text) > max_width:
            # Leave space for the ▼ symbol
            content_width = max_width - 2
            if content_width > 0:
                text = text[:content_width] + " ▼"
            else:
                text = " ▼"

        return text

    def create_pop_up(self):
        """Create the popup list widget."""
        if not self.options:
            # Return empty popup if no options
            empty_text = urwid.Text("No options available")
            return urwid.AttrMap(empty_text, 'popup')

        # Create selectable widgets for each option
        widgets = []
        for i, option in enumerate(self.options):
            if i == self.current_index:
                # Use SelectableIcon with cursor at end for full highlighting
                widget = urwid.SelectableIcon(
                    f"▶ {option}", cursor_position=len(f"▶ {option}")
                    )
                widget = urwid.AttrMap(widget, 'popup_selected')
            else:
                # Use SelectableIcon for other options
                widget = urwid.SelectableIcon(
                    f"  {option}", cursor_position=len(f"  {option}")
                    )
                widget = urwid.AttrMap(widget, 'popup')
            widgets.append(widget)

        # Create listbox with the widgets
        listbox = DropdownListBox(urwid.SimpleFocusListWalker(widgets), self)

        # Set focus to current selection
        if 0 <= self.current_index < len(widgets):
            listbox.set_focus(self.current_index)

        # Return the listbox directly - let urwid handle the keypress events
        return listbox

    def get_pop_up_parameters(self):
        """Get parameters for popup positioning."""
        # Calculate popup size based on options
        max_width = (
            max(len(opt) for opt in self.options) if self.options else 10
        )
        popup_width = min(max_width + 6, 40)  # Add more padding, cap at 40
        popup_height = max(len(self.options), 1)  # At least 1 row

        return {
            'left': 0,
            'top': 1,
            'overlay_width': popup_width,
            'overlay_height': popup_height
        }

    def _select_option(self, option_index, option_value):
        """Select an option and close the popup."""
        self._original_content = option_value
        self.current_index = option_index
        self.text_widget.set_text(self._get_display_text(self.max_width))

        # Call the change callback if provided
        if self.on_change:
            self.on_change(option_value)

        # Close the popup
        self.close_pop_up()

    def _option_selected(self, button):
        """Handle option selection from popup."""
        if hasattr(button, '_option_value'):
            self._original_content = button._option_value
            self.current_index = button._option_index
            self.text_widget.set_text(self._get_display_text())

            # Call the change callback if provided
            if self.on_change:
                self.on_change(button._option_value)

            # Close the popup
            self.close_pop_up()

    def selectable(self):
        """Return True to indicate this widget can receive focus."""
        return True

    def keypress(self, size, key):
        """Handle keypress events."""

        # If popup is open, handle navigation keys
        if hasattr(self, '_pop_up_widget') and self._pop_up_widget:
            if key in ['up', 'down', 'page up', 'page down']:
                # Delegate to the popup's listbox
                popup_widget = self._pop_up_widget
                if hasattr(popup_widget, 'keypress'):
                    result = popup_widget.keypress(size, key)
                    if result is None:
                        return None
                return key
            elif key == 'enter':
                # Handle selection in popup
                popup_widget = self._pop_up_widget
                if hasattr(popup_widget, 'keypress'):
                    result = popup_widget.keypress(size, key)
                    return result
                return None
            elif key == 'esc':
                # Close popup
                self.close_pop_up()
                return None

        # Handle normal cell keypress events
        if key == 'enter':
            # Open popup
            self.open_pop_up()
            return None
        elif key == 'esc':
            # Cancel - restore original content
            self.current_index = self._get_index_for_content(
                self._original_content
            )
            self.text_widget.set_text(self._get_display_text(self.max_width))
            return None
        else:
            # Let parent handle other keys
            return super().keypress(size, key)

    def render(self, size, focus=False):
        """Override render to handle size parameter correctly."""
        if isinstance(size, tuple) and len(size) > 1:
            # If we get a tuple with multiple values, use only the first one
            size = (size[0],)
        return super().render(size, focus)

    def rows(self, size, focus=False):
        """Override rows to handle size parameter correctly."""
        if isinstance(size, tuple) and len(size) > 1:
            # Use only the width for calculating rows
            size = (size[0],)

        # Always return 1 row - compact display
        return 1

    def pack(self, size, focus=False):
        """Pack the widget."""
        # Ensure size is a single value for width
        if isinstance(size, tuple) and len(size) > 1:
            size = (size[0],)
        return super().pack(size, focus)

    def get_edit_text(self):
        """Get the current selected value."""
        return self._original_content
