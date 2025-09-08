from typing import Optional, TYPE_CHECKING
from rich.console import Console
from readchar import readkey, key

from functools import partial
import types

import sys

if TYPE_CHECKING:
    from .table import Table

console = Console()

def clear_single_line():
    sys.stdout.write("\033[K")
    sys.stdout.flush()

def moveCursorUp(lines=1):
    for _ in range(lines):
        sys.stdout.write("\033[1A")
    sys.stdout.flush()

def clear_lines(lines):
    for _ in range(lines):
        moveCursorUp() # Move up 1 Line
        clear_single_line()  # Clear
    sys.stdout.flush()

def return_cell(table: 'Table'):
    selected_row, selected_col = table.selection
    if selected_row == -1:
        cell = table.toolbar[selected_col]
    else:
        cell = table.data[selected_row][selected_col]
    cell_value = cell.value
    if cell_value:
        if isinstance(cell_value, types.FunctionType) or isinstance(cell_value, partial):
            cell_value()
        else:
            return cell_value

def print_interactive(table: 'Table', debug: Optional[bool]=False):
    from .print_table import PRESETS, get_rich_elements, HEAVYSET

    number_tools = len(table.toolbar)
    toolbar_exists = True if number_tools > 0 else False # More than 0 tools = there is a tool bar

    selected_row, selected_col = table.selection
    number_rows = table.rows
    number_cols = table.cols
    max_selected_row = number_rows - 1
    min_selected_row = -1 if toolbar_exists else 0 # Only allow going up to -1 if the toolbar exists
    max_selected_col = number_cols -1
    min_selected_col = 0
    max_selected_col_tool = number_tools - 1

    # Getting the border elements
    border_charset = table.style.border_charset if table.style else None
    border_charset_name = table.style.border_charset_name if table.style else None
    if border_charset is None:
        charset_key = border_charset_name.lower() if border_charset_name else 'heavy'
        border_charset = PRESETS.get(charset_key, HEAVYSET)

    elements = get_rich_elements(table=table, border_charset=border_charset)
    
    bb_highlight = table.style.highlight if table.style else "black on white"
    print_style = table.style.style if table.style else ""

    table_lines = None
    while True:
        output = []

        # Debug
        if debug:
            if selected_row == -1:
                current_cell_value = str(getattr(table.toolbar[selected_col], 'value', 'None'))
            else:
                current_cell_value = str(getattr(table.data[selected_row][selected_col], 'value', 'None'))
            output.append(f'row: {selected_row}, col: {selected_col}, cell value: {current_cell_value}')

        # Toolbar
        tool_row = ' '
        for index, tool in enumerate(table.toolbar):
            selected = False
            if selected_row == -1 and selected_col == index: # Check if highlighted
                selected = True
                tool_row += f"[{bb_highlight}]"
            tool_row += tool.name
            if selected:
                tool_row += f"[/{bb_highlight}]"

            if index < (number_tools - 1): # Dont print on last tool
                tool_row += ' | '
        output.append(tool_row)

        # Table Content
        output.append(elements.top_row)
        row = ""
        for r in range(number_rows):
            row += border_charset.col
            for c in range(number_cols):
                if r == selected_row and c == selected_col:
                    row += f"[{bb_highlight}]"

                row += elements.spacer
                row += getattr(table.data[r][c], 'content', '')

                cell_length = len(getattr(table.data[r][c], 'content', '')) # Make sure all cells in one column are the same size
                size_difference = elements.column_length[c] - cell_length
                for _ in range(size_difference):
                    row += " "

                row += elements.spacer
                if r == selected_row and c == selected_col:
                    row += f"[/{bb_highlight}]"

                row += border_charset.col
            output.append(row)
            row = ""
            if not r == number_rows-1:
                output.append(elements.divider_row)
        output.append(elements.bottom_row)

        table_lines = len(output)

        for line in output:
            console.print(line, style=print_style)

        user_input = None
        while not user_input:
            user_input = readkey()

            inToolbar = False
            if selected_row == -1:
                inToolbar = True

            # Navigation Keys
            if user_input == key.UP:
                selected_row -= 1
                if selected_row < min_selected_row:
                    selected_row = max_selected_row

            elif user_input == key.DOWN:
                selected_row += 1
                if selected_row > max_selected_row: # selection is over the last row
                    selected_row = min_selected_row

            elif user_input == key.LEFT:
                selected_col -= 1
                if selected_col < 0: # selection is before the first col
                    if inToolbar:
                        selected_col = max_selected_col_tool
                    else:
                        selected_col = max_selected_col

            elif user_input == key.RIGHT:
                selected_col += 1
                if inToolbar:
                    if selected_col > max_selected_col_tool: # selection is over the last col and we are in the toolbar
                        selected_col = min_selected_col
                else:
                    if selected_col > max_selected_col: # selection is over the last col
                        selected_col = min_selected_col

            # Non navigating Keys
            elif user_input == key.ENTER:
                table.selection = (selected_row, selected_col)
                clear_lines(table_lines)
                return return_cell(table=table)

        clear_lines(table_lines)
        table_lines = None