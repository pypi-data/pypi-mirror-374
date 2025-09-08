from typing import Optional, TYPE_CHECKING, Union, Any
from enum import Enum

if TYPE_CHECKING:
    from .print_table import BorderCharSet

GERROR = "Error with Gridlines: "
def raise_value_error(msg: str):
    raise ValueError(GERROR + msg)

class ResizingException(Exception):
    pass

class TableCell:
    def __init__(self, content: str, value):
        self.content = content
        self.value = value

class TableStyling:
    def __init__(self, charset: Optional['BorderCharSet']=None, charset_name: Optional[str]="heavy", spacing: Optional[int]=1, equal_width: Optional[bool]=False, style: Optional[str]="", highlight: Optional[str]="black on white"):
        self.border_charset = charset
        self.border_charset_name = charset_name
        self.spacing = spacing
        self.equal_width = equal_width
        self.style = style # rich console styling
        self.highlight = highlight # rich styling for highlighting

class WriteMode(Enum):
    CONTENT = "content",
    VALUE = "value",
    BOTH = "both",
    CELL = "cell"

class ToolBarItem():
    def __init__(self, name: str, value: Any, key):
        self.name = name
        self.value = value
        #self.key = key if key else None WIP: hotkeys (could be implemented right now but rather when it would also work cross plattform)

class Table:
    def __init__(self, rows: int, cols: int, interactive: bool=False, selection: tuple=(0,0), resize: bool=False, style: Optional[TableStyling]=None):
        self.rows = rows
        self.cols = cols
        self.interactive = interactive
        self.selection = selection
        self.resize = resize
        self.style = style
        self.toolbar = []
        self.data = [[TableCell(content="", value=None) for _ in range(cols)] for _ in range(rows)]

    def print_table(self, plain: bool=False, debug: bool=False):
        """
        Prints the table, either by standard rich or plain
        """
        from .print_table import print_plain, print_rich
        if plain:
            print_plain(self)
        else:
            if self.interactive:
                from .interactive import print_interactive
                return print_interactive(self, debug=debug)
            else:
                print_rich(self)

    def set_styling(self, styling: TableStyling):
        """
        Sets the added TableStyling Obj to the table
        """
        self.style = styling

    def check_position(self, row_pos: Optional[int]=None, col_pos: Optional[int]=None, raise_error: Optional[bool]=True, start_error: Optional[str]=None):
        """
        Checks if the position could be written to. Note that it will still return True if resize is enabled and the position is positive
        even when the position does not yet exist.
        """
        if row_pos is None and col_pos is None:
            raise_value_error("could not check position in table as both the row_pos and col_pos were None")

        output = True

        def output_error(msg):
            nonlocal output
            if raise_error:
                start = ""
                if start_error:
                    start = str(start_error) + " "
                raise_value_error(start + " " + msg + f" (col_pos:{col_pos}, row_pos:{row_pos})")
            output = False

        if col_pos:
            if col_pos < 0:
                output_error("position in table is invalid as col_pos was negative")

            if col_pos > self.cols - 1 and not self.resize:
                output_error("position in table is invalid as col_pos was out of bounds")

        if row_pos:
            if row_pos < 0:
                output_error("position in table is invalid as row_pos was negative")

            if row_pos > self.rows - 1 and not self.resize:
                output_error("position in table is invalid as row_pos was out of bounds")

        return output

    def expand_rows(self, total_rows: int):
        """
        Add empty rows to the table
        """
        if total_rows == self.rows: # Is already that size
            return
        
        if not self.resize: # resize is not enabled
            raise ResizingException("could not expand rows, as table is not resizable. Enable resize if you want to enable this behavior")

        if total_rows < self.rows: # table already has more rows
            raise_value_error("could not expand rows, as total_rows is less than current rows")

        single_row = []
        for _ in range(self.cols): # append a cell to single_row per column 
            single_row.append(TableCell(content="", value=None))

        new_rows = total_rows - self.rows
        for _ in range(new_rows): # Add the new rows to the table
            self.data.append(single_row.copy())

        self.rows = total_rows

    def expand_cols(self, total_cols: int):
        """
        Add empty columns to the table
        """
        if total_cols == self.cols: # Is already that size
            return

        if not self.resize: # resize is not enabled
            raise ResizingException("could not expand columns, as table is not resizable. Enable resize if you want to enable this behavior")

        if total_cols < self.cols: # table already has more columns
            raise_value_error("could not expand columns, as total_cols is less than current cols")

        new_cols = total_cols - self.cols
        for row in self.data: # append a cell to the existing rows per new column
            for _ in range(new_cols):
                row.append(TableCell(content="", value=None))

        self.cols = total_cols

    def expand(self, total_cols: Optional[int]=None, total_rows: Optional[int]=None, new_cols: Optional[int]=None, new_rows: Optional[int]=None):
        """
        Main method for expanding the table. Adds rows and columns to the table.
        """
        if not total_cols and not total_rows and not new_cols and not new_rows: # no argument was set
            raise_value_error("Could not expand, as no argument was set")

        if (total_cols or total_rows) and (new_cols or new_rows): # both a total_ and a new_ argument was set
            raise_value_error("Could not expand, as both total and new were set. Only set either new_x or total_x.")
        
        if new_cols or new_rows: # Handle new rows
                total_cols_to_add = self.cols + (new_cols if new_cols else 0) # Calculate the total cols and rows
                total_rows_to_add = self.rows + (new_rows if new_rows else 0)
                self.expand_cols(total_cols=total_cols_to_add)
                self.expand_rows(total_rows=total_rows_to_add)
                return

        if total_cols:
            self.expand_cols(total_cols=total_cols)
        
        if total_rows:
            self.expand_rows(total_rows=total_rows)

    def write_cell(self, row_pos: int, col_pos: int, data, mode: WriteMode=WriteMode.CONTENT, erase: bool=True):
        """
        Write to specified cell, expands if necessary and possible. If erase is set False no previously set data will get overwritten.
        """
        self.check_position(row_pos=row_pos, col_pos=col_pos, start_error="could not write to cell,")

        if mode == WriteMode.CELL and not isinstance(data, TableCell):
            raise_value_error('Couldnt write cell as WriteMode was set to cell, but the data wasnt a TableCell Obj')

        if isinstance(data, TableCell):
            mode = WriteMode.CELL

        try:
            current_cell = self.data[row_pos][col_pos]
        except IndexError: # Cell doesnt exist -> empty
            current_cell = None

        if not erase:
            if current_cell is None: # Cell doesnt exist -> empty
                pass

            elif mode == WriteMode.CONTENT or mode == WriteMode.CELL or mode == WriteMode.BOTH:
                if current_cell.content and not current_cell.content == '': # Exists and is not empty
                    raise_value_error('Could not write to cell as content was not empty and erase was false')

            elif mode == WriteMode.VALUE or mode == WriteMode.CELL or mode == WriteMode.BOTH:
                if current_cell.value: # Exists
                    raise_value_error('Could not write to cell as value was not empty and erase was false')

        if row_pos > (self.rows - 1): # expand rows if necessary
            rows_needed = row_pos - (self.rows - 1)
            self.expand(new_rows=rows_needed)
        
        if col_pos > (self.cols - 1): # expand cols if necessary
            cols_needed = col_pos - (self.cols - 1)
            self.expand(new_cols=cols_needed)

        current_content = getattr(current_cell, 'content', "")
        current_value = getattr(current_cell, 'value', None)

        if mode == WriteMode.CELL:
            new_cell = data
        elif mode == WriteMode.CONTENT:
            new_cell = TableCell(content=str(data), value=current_value)
        elif mode == WriteMode.VALUE:
            new_cell = TableCell(content=current_content, value=data)
        elif mode == WriteMode.BOTH:
            new_cell = TableCell(content=str(data), value=data)
        
        self.data[row_pos][col_pos] = new_cell # Set the data

    def write_row(self, row_pos: int, data, starting_col: int=0, mode: WriteMode=WriteMode.CONTENT):
        """
        Writes in the specified row starting from specified column (default 0).
        """
        if not isinstance(data, list):
            data = [data]
        
        if (len(data) + starting_col) > self.cols: # Expand if data has more entries than there are cells left in the row
            self.expand(total_cols=len(data))

        if row_pos > (self.rows - 1): # Expand if row does not exist
            self.expand(total_rows=row_pos+1)

        for index, cell in enumerate(data):
            current_col = index + starting_col
            self.write_cell(row_pos=row_pos, col_pos=current_col, data=cell, mode=mode)

    def write_col(self, col_pos: int, data, starting_row: int=0, mode: WriteMode=WriteMode.CONTENT):
        """
        Writes in the specified column starting from specified row (default 0)
        """
        if not isinstance(data, list):
            data = [data]

        if (len(data) + starting_row) > self.rows: # Expand if data has more entries than there are cells left in the col
            self.expand(total_rows=len(data))

        if col_pos > (self.cols - 1): # Expand if column does not exist
            self.expand(total_cols=col_pos+1)

        for index, cell in enumerate(data):
            current_row = index + starting_row
            self.write_cell(row_pos=current_row, col_pos=col_pos, data=cell, mode=mode)

    def write_list(self, user_list: list, mode: WriteMode=WriteMode.CONTENT):
        """
        Write the given two dimensional list to the table.
        """
        if len(user_list) > self.rows:
            if not self.resize:
                raise_value_error("could not write user_list to table, as number of rows in fed user_list does not match table")
            self.expand(total_rows=len(user_list))

        if any(len(row) > self.cols for row in user_list):
            if not self.resize:
                raise_value_error("could not write user_list to table, as number of columns in fed user_list does not match table")
            self.expand(total_cols=len(user_list[0]))

        if any(not isinstance(row, list) for row in user_list): # check whether every row in the given list is actually a list, if not it is not two dimensional
            raise_value_error("could not write user_list to table, as each row must be a list. Fed user_list might not be 2 dimensional")

        user_list_rows = len(user_list)
        user_list_cols = len(user_list[0])

        for row in range(user_list_rows):
            for col in range(user_list_cols): # Write to table from the list
                try:
                    user_cell = user_list[row][col]
                    self.write_cell(row_pos=row, col_pos=col, data=user_cell, mode=mode)
                except IndexError as e:
                    raise IndexError(f"Gridlines: Whilst writing a list to a table, there was an IndexError, are you sure your list is two dimensional and every row has the same number of cell's? Error:{e}")

    def write_next_row(self, data: list, mode: WriteMode=WriteMode.CONTENT):
        """
        Write to the next availible/empty row. Wont write to a row with data, even when given data would fit. Expands if possible and needed.
        """
        if len(data) > self.cols: # Check whether provided list is longer than there are cells in a row
            cols_to_extend = len(data) - self.cols
            self.expand(new_cols=cols_to_extend)

        next_free_row = None
        for index, row in enumerate(self.data):
            for c in row:
                if c.content is not None and not c.content == "": # Check if content has something writen in it
                    next_free_row = None
                    break
                if not c.value is None:
                    next_free_row = None
                    break
                next_free_row = index

            if next_free_row == index:
                break
        
        if next_free_row is None: # there are no free rows. Try expanding it
            self.expand(new_rows=1)
            next_free_row = self.rows - 1

        self.write_row(row_pos=next_free_row, data=data, mode=mode)

    def write_next_col(self, data: list, mode: WriteMode=WriteMode.CONTENT):
        """
        Write to the next availible/empty column. Wont write to a column with data, even when given data would fit. Expands if possible and needed.
        """
        if len(data) > self.rows: # Check whether provided list is longer than there are cells in a column
            rows_to_extend = len(data) - self.rows
            self.expand(new_rows=rows_to_extend)

        next_free_col = None
        for column in range(self.cols): # Get the next free column
            for row in self.data: # Check each row at the same index
                if row[column].content is not None and not row[column].content == "": # Check if content has something writen in it
                    next_free_col = None
                    break
                elif row[column].value is not None:
                    next_free_col = None
                    break
                next_free_col = column

            if next_free_col == column:
                break
        
        if next_free_col is None: # there are no free columns. Try expanding it
            self.expand(new_cols=1)
            next_free_col = self.cols - 1

        self.write_col(col_pos=next_free_col, data=data, mode=mode)

    def add_tool(self, data: Union[ToolBarItem, list[ToolBarItem]]):
        if not isinstance(data, list):
            data = [data]

        for item in data:
            if not isinstance(item, ToolBarItem):
                raise_value_error(f'Could not add item to toolbar, as it was not a ToolBarItem Obj, but a {type(item)}')
            if not getattr(item, 'name', None):
                raise_value_error('Could not add item to toolbar, as it had no name specified')

        for item in data:
            self.toolbar.append(item)

    def print_all_tools(self):
        for index, item in enumerate(self.toolbar):
            name = getattr(item, 'name', 'None set')
            try:
                value = str(getattr(item, 'value', 'None'))
            except IndexError:
                value = 'Not convertible to string'
            key = getattr(item, 'key', 'None')
            
            tool_string = f"{index} | name: {name} | value: {value}"
            print(tool_string)

def create_empty_table(rows: int=1, cols: int=1, interactive: bool=False, resize: bool=True, styling: Optional[TableStyling]=None):
    """
    Create and return an empty table instance.
    """
    return Table(
        rows=rows,
        cols=cols,
        interactive=interactive,
        resize=resize,
        style=styling if styling else None
        )