from rich.console import Console
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .table import Table

console = Console()

class BorderCharSet:
    """
    Class for the characters used when printing rich. Instances preferably end with SET (e.g. LIGHTSET)

    Abbreviations:

    b: bottom

    t: top

    h: horizontal

    v: vertical

    l: left

    r:right
    """
    def __init__(self, row: str, col: str, corner_b_l: str, corner_b_r: str, corner_t_l: str, corner_t_r: str, junc_h_d: str, junc_h_u: str, junc_v_l: str, junc_v_r: str, junc_v_l_r: str):
        self.row = row
        self.col = col
        self.corner_b_l = corner_b_l
        self.corner_b_r = corner_b_r
        self.corner_t_l = corner_t_l
        self.corner_t_r = corner_t_r
        self.junc_h_d = junc_h_d
        self.junc_h_u = junc_h_u
        self.junc_v_l = junc_v_l
        self.junc_v_r = junc_v_r
        self.junc_v_l_r = junc_v_l_r

LIGHTSET = BorderCharSet(
    row="─",
    col="│",
    corner_b_l="└",
    corner_b_r="┘",
    corner_t_l="┌",
    corner_t_r="┐",
    junc_h_d="┬",
    junc_h_u="┴",
    junc_v_l="┤",
    junc_v_r="├",
    junc_v_l_r="┼"
)

HEAVYSET = BorderCharSet(
    row="━",
    col="┃",
    corner_b_l="┗",
    corner_b_r="┛",
    corner_t_l="┏",
    corner_t_r="┓",
    junc_h_d="┳",
    junc_h_u="┻",
    junc_v_l="┫",
    junc_v_r="┠",
    junc_v_l_r="╋"
)

DOUBLESET = BorderCharSet(
    row="═",
    col="║",
    corner_b_l="╚",
    corner_b_r="╝",
    corner_t_l="╔",
    corner_t_r="╗",
    junc_h_d="╦",
    junc_h_u="╩",
    junc_v_l="╣",
    junc_v_r="╠",
    junc_v_l_r="╬"
)

FORMSSET = BorderCharSet( # Onlt works with certain shells as some have different alignments for these symbols
    row="▬",
    col="▮",
    corner_b_l="◺",
    corner_b_r="◿",
    corner_t_l="◸",
    corner_t_r="◹",
    junc_h_d="▼",
    junc_h_u="▲",
    junc_v_l="◀",
    junc_v_r="▶",
    junc_v_l_r="◆"
)

SLEEKSET = BorderCharSet(
    row="─",
    col=" ",
    corner_b_l="─",
    corner_b_r="─",
    corner_t_l="─",
    corner_t_r="─",
    junc_h_d="─",
    junc_h_u=" ",
    junc_v_l="─",
    junc_v_r="─",
    junc_v_l_r=" "
)

PRESETS = {
    "light": LIGHTSET,
    "heavy": HEAVYSET,
    "double": DOUBLESET,
    "forms": FORMSSET,
    "sleek": SLEEKSET
}

def print_plain(table: 'Table', output_to_list: Optional[list]=None):
    number_cols = table.cols

    output = []

    for index, row in enumerate(table.data):
        p = ""
        for index, col in enumerate(row):
            p += "| " + col.content + " "
            if index == number_cols-1:
                p += "|"
        output.append(p)

    if output_to_list is not None:
        output_to_list.append(output) # Append to given List instead of printing (for print_tables/add_table_to_print)
    else:
        for line in output:
            print(line)

class Richrows:
    def __init__(self, top_row: str, divider_row: str, bottom_row: str, spacer: str, column_length: list):
        self.top_row = top_row
        self.divider_row = divider_row
        self.bottom_row = bottom_row
        self.spacer = spacer
        self.column_length = column_length

def get_rich_elements(table: 'Table', border_charset: BorderCharSet=PRESETS['heavy'], column_length: Optional[list]=None):
    """
    Generates all elements needed for printing rich. Returns a Richrows Obj.
    """
    if column_length is None:
        column_length = []
        for _ in range(table.cols): # Fill with 0 per column
            column_length.append(0)

        for row in range(table.rows): # Actually get the cell length
            for cell in range(table.cols):
                cell_size = len(table.data[row][cell].content) if table.data[row][cell].content else 0
                if cell_size > column_length[cell]: # Only set if the cell is currently the largest of the column
                    column_length[cell] = cell_size

        if table.style and table.style.equal_width: # If equal_width is true fix every column to the biggest length
            max_length = max(column_length)
            column_length = [max_length] * table.cols

    GRIDCHARSIZE = 1 # Size of the border symbols
    spacing = table.style.spacing if table.style and table.style.spacing else 1 # Space between content and border (both sides)

    spacer = ""
    for _ in range(spacing):
        spacer += " "

    top_row = border_charset.corner_t_l # Before top row
    divider_row = border_charset.junc_v_r # Between rows
    bottom_row = border_charset.corner_b_l # After bottom row

    for col_length in column_length:
        cell_length = col_length
        cell_length += (spacing*2) # Add the spacing

        for _ in range(cell_length):
            top_row += border_charset.row # Fill with horizontal bars
            divider_row += border_charset.row
            bottom_row += border_charset.row

        top_row += border_charset.junc_h_d # Add junction
        divider_row += border_charset.junc_v_l_r
        bottom_row += border_charset.junc_h_u

    top_row = top_row[:-1] # Remove last char and add correct end
    top_row += border_charset.corner_t_r

    divider_row = divider_row[:-1]
    divider_row += border_charset.junc_v_l

    bottom_row = bottom_row[:-1]
    bottom_row += border_charset.corner_b_r

    return Richrows(
        top_row=top_row,
        divider_row=divider_row,
        bottom_row=bottom_row,
        spacer=spacer,
        column_length=column_length
    )

def print_rich(table: 'Table', output_to_list: Optional[list]=None):
    border_charset = table.style.border_charset if table.style else None
    border_charset_name = table.style.border_charset_name if table.style else None

    if border_charset is None:
        charset_key = border_charset_name.lower() if border_charset_name else 'heavy'
        border_charset = PRESETS.get(charset_key, HEAVYSET)

    number_rows = table.rows
    number_cols = table.cols

    output = []

    elements = get_rich_elements(table=table, border_charset=border_charset)
    
    output.append(elements.top_row) # Actual Content
    row = ""
    for r in range(number_rows):
        row += border_charset.col
        for c in range(number_cols):
            row += elements.spacer
            row += table.data[r][c].content

            cell_length = len(table.data[r][c].content) # Make sure all cells in one column are the same size
            size_difference = elements.column_length[c] - cell_length
            for _ in range(size_difference):
                row += " "

            row += elements.spacer
            row += border_charset.col
        output.append(row)
        row = ""
        if not r == number_rows-1:
            output.append(elements.divider_row)
    output.append(elements.bottom_row)


    print_style = table.style.style if table.style else ""

    if output_to_list is not None:
        output_to_list.append(output) # Append to given List instead of printing (for print_tables/add_table_to_print)
    else:
        for line in output:
            console.print(line, style=print_style)

def print_tables(tables: list, spacing_between: int=0):
    """
    Print all given tables side by side with the specified spacing between.
    NOTE: Currently printing_tables only works when you order them consistently (e.g. longest to shortest or vice versa).
    Multiple tables with the same size after another also work, but the order can not fluctuate (e.g. long, medium, long, short (2. long breaks))
    """
    output = [""]

    spacing = ""
    for _ in range(spacing_between):
        spacing += " "

    print_list = []
    for table in tables:
        print_rich(table=table, output_to_list=print_list)

    before = "" # Ensure alignment e.g. when 2. table is longer than 1.
    for index, table in enumerate(print_list):
        print_style = tables[index].style.style if tables[index].style else None
        for line_idx, line in enumerate(table):
            while (len(output) - 1) < line_idx: # Make sure output list is long enough and next write is not out of range
                output.append(before)

            styled_line = f"[{print_style}]{line}[/{print_style}]" if print_style else line
            output[line_idx] += styled_line
            output[line_idx] += spacing

        for _ in range(len(table[0])):
            before += " "
        before += spacing

    for line in output:
        console.print(line)