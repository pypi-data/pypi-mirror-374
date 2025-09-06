# urw-scroll-table

A scrollable and editable table widget for urwid terminal applications.

## Features

- **Scrollable**: Both horizontal and vertical scrolling support
- **Editable**: In-place editing of table cells
- **Multiple Cell Types**: Support for text, editable, and dropdown cell types
- **Keyboard Navigation**: Full keyboard navigation with arrow keys
- **Customizable Styling**: Customizable colors and appearance
- **Compact Display**: Efficient use of terminal space

## Installation

This package uses Poetry for dependency management. To install:

```bash
pip install urw-scroll-table
```

or manually:

```bash
# Clone the repository
git clone https://github.com/zhum/urw-scroll-table.git
cd urw-scroll-table

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

## Quick Start

```python
import urwid
from urw_scroll_table import UrwScrollTable

# Define your data
headers = ['Name', 'Age', 'City', 'Status']
data = [
    ['Alice', 25, 'New York', 'Active'],
    ['Bob', 30, 'Los Angeles', 'Active'],
    ['Charlie', 35, 'Chicago', 'Inactive'],
]

# Define column types
column_types = {
    0: 'editable',    # Name - editable text
    1: 'editable',    # Age - editable text
    2: 'editable',    # City - editable text
    3: 'dropdown',    # Status - dropdown
}

# Create the table widget
table = UrwScrollTable(
    headers=headers,
    data=data,
    column_types=column_types
)

# Create and run the application
frame = urwid.Frame(body=table)
loop = urwid.MainLoop(frame)
loop.run()
```

## Usage

### Basic Table Creation

```python
from urw_scroll_table import UrwScrollTable

table = UrwScrollTable(
    headers=['Name', 'Age', 'City'],
    data=[
        ['Alice', 25, 'New York'],
        ['Bob', 30, 'Los Angeles'],
    ]
)
```

### Column Types

The table supports three column types:

- `'text'`: Read-only text display (default)
- `'editable'`: Editable text cells
- `'dropdown'`: Dropdown selection cells

```python
column_types = {
    0: 'editable',    # Column 0 is editable
    1: 'dropdown',    # Column 1 is a dropdown
    2: 'text',        # Column 2 is read-only
}
```

### Customization

#### Colors

You can customize the appearance using the `colors` parameter.
Available options are: 'header', 'active_cell', 'editing_cell', and 'status'.
`colors` parameter accepts a dictionary with options as keys, and tuples for foreground color and background color. Available colors are:

- for background: 'black', 'dark red', 'dark green', 'brown', 'dark blue', 'dark magenta', 'dark cyan', 'light gray'.
- for foreground: as above, and 'dark gray', 'light red', 'light green', 'yellow', 'light blue', 'light magenta', 'light cyan', 'white'.
- you may use 'default' to use default terminal colors.

```python
colors = {
    'header': ('white', 'dark blue'),
    'active_cell': ('black', 'white'),
    'editing_cell': ('black', 'yellow'),
}

table = UrwScrollTable(
    headers=headers,
    data=data,
    colors=colors
)
```

You may use 24-bit colors like below. 4-th and 5-th fields are foreground and background colors.
If terminal does not support 24 bit color, 1-st and 2-nd fields are used.

```python
custom_colors = {
    'header': ('dark blue', 'light red', 'default', '#00f', '#ff0'),
    'active_cell': ('white', 'light green', 'default', '#999', '#12f'),
    'editing_cell': ('dark blue', 'dark green', 'default', '#005', '#0f0'),
}
```

#### Size Constraints

```python
table = UrwScrollTable(
    headers=headers,
    data=data,
    max_width=100,    # Maximum width
    max_height=20,    # Maximum height
)
```

### Keyboard Controls

- **Arrow Keys**: Navigate between cells
- **Enter**: Start editing the current cell (opens popup for dropdowns)
- **Esc**: Cancel editing
- **Up/Down** (in dropdown popup): Navigate dropdown options
- **Enter** (in dropdown popup): Select option and close popup
- **Esc** (in dropdown popup): Cancel selection and close popup
- **q**: Quit the application

## Examples

### Complete Example

See `examples/demo.py` for a complete working example:

```bash
cd examples
python demo.py
```

### Custom Dropdown Options

You can customize dropdown options by modifying the `_get_dropdown_options` method in the `UrwScrollTable` class:

```python
def _get_dropdown_options(self, col_idx):
    """Get dropdown options for a specific column."""
    if col_idx == 0:  # Status column
        return ['Active', 'Inactive', 'Pending', 'Suspended']
    elif col_idx == 1:  # Priority column
        return ['Low', 'Medium', 'High', 'Critical']
    else:
        return []
```

## API Reference

### UrwScrollTable

The main table widget class.

#### Constructor Parameters

- `headers` (list): List of header strings
- `data` (list): List of lists containing row data
- `max_width` (int, optional): Maximum width of the widget (default: 80)
- `max_height` (int, optional): Maximum height of the widget (default: 20)
- `edit_color` (str, optional): Background color for editing cells (default: 'yellow')
- `column_types` (dict/list, optional): Column type definitions
- `colors` (dict, optional): Custom color definitions

#### Methods

- `keypress(size, key)`: Handle keyboard input
- `render(size, focus)`: Render the widget
- `_on_cell_change(row, col, new_value)`: Handle cell value changes

### Widget Classes

- `SafeText`: Text widget with safe size parameter handling
- `EditableCell`: Editable text cell widget
- `DropdownCell`: Dropdown selection cell widget

Supplimental classes

- `SingleLineText`: Single-line text widget
- `HeightEnforcer`: Widget wrapper that enforces single-row height

### Reading Table Data

The `UrwScrollTable` class provides several methods to read current table values:

```python
# Get all table data
all_data = table.get_all_data()

# Get specific row data
row_data = table.get_row_data(row_index)

# Get specific cell value
cell_value = table.get_cell_value(row_index, col_index)

# Get table headers
headers = table.get_headers()

# Get comprehensive table information
info = table.get_table_info()
```

All methods return copies of the data to prevent external modification of the table's internal state.

## Development

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
poetry run black src/ examples/
```

### Type Checking

```bash
poetry run mypy src/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## Requirements

- Python 3.8+
- urwid 3.0.0+
