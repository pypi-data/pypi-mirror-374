
# Core Python imports.
from enum import Enum
import math
import sys

#------------------------------------------------------------------------------
# Constants.
pi2 = (2 * math.pi)
ft_per_metre = 3.28084

class EUnits(Enum):
    Degrees = 1
    Radians = 2

#------------------------------------------------------------------------------
# Trig identities.

def Cos2(angle):
    return math.pow(math.cos(angle), 2)

def Cos3(angle):
    return math.pow(math.cos(angle), 3)

def Cos4(angle):
    return math.pow(math.cos(angle), 4)

def Cos5(angle):
    return math.pow(math.cos(angle), 5)

def Sin2(angle):
    return math.pow(math.sin(angle), 2)

def Tan2(angle):
    return math.pow(math.tan(angle), 2)

def Tan3(angle):
    return math.pow(math.tan(angle), 3)

def Tan4(angle):
    return math.pow(math.tan(angle), 4)

def Tan5(angle):
    return math.pow(math.tan(angle), 5)

def Tan6(angle):
    return math.pow(math.tan(angle), 6)

def Sec(angle):
    return 1 / math.cos(angle)

def Cosec(angle):
    return 1 / math.sin(angle)

def Cot(angle):
    return 1 / math.tan(angle)

#------------------------------------------------------------------------------
# Miscellaneous.

def DegToRad(degrees):
    """ Convert degrees to radians.
    """
    return (degrees / 180) * math.pi

def RadToDeg(radians):
    """ Convert radians to degrees.
    """
    return (radians / math.pi) * 180

def Circumference(radius):
    """ Circumference of a circle.
    """
    return 2 * math.pi * radius

def MetresToFeet(metres):
    return metres * ft_per_metre

def FeetToMetres(feet):
    return feet / ft_per_metre

def ConvertAngle(angle, signed=True, units=EUnits.Degrees):
    """ Convert angle to signed or unsigned.
    """

    # Convert to degrees.
    _angle = angle
    if units == EUnits.Radians:
        _angle = RadToDeg(angle)

    # Check if we need to do anything.
    if signed:
        if (-180 < _angle) and (_angle < 180):
            return angle
    else:
        if (0 < _angle) and (_angle < 360):
            return angle

    # Convert to unsigned, 0 to 360 first.
    angle = _angle
    while angle < 0:
        angle += 360
    while angle >= 360:
        angle -= 360

    # Do requested sign-ness.
    if signed:
        if angle > 180:
            angle -= 360

    # Back to original units.
    if units == EUnits.Radians:
        angle = DegToRad(angle)

    return angle

#------------------------------------------------------------------------------
# Grid type implementation.
class Grid:
    def __init__(self, rows, cols):
        """ Constructor.
        Initialise grid size of rows x cols.
        """

        # Initialise data structure.
        self.rows = []
        while len(self.rows) < rows:
            self.rows.append([None] * (cols))

        # Initialise iterators.
        self.row_iter = 0
        self.col_iter = -1

        # Initialise auto fill indeces.
        self.af_row = 0
        self.af_col = 0

    def __iter__(self):
        """ Python iterator implementation.
        Object used for iterating.
        """
        return self

    def __next__(self):
        """ Python next implementation.
        Get next data element.
        """

        # Increment column.
        self.col_iter += 1

        # If we've reached the last column, go to the next row and reset
        # column iter.
        if self.col_iter >= len(self.rows[self.row_iter]):
            self.row_iter += 1
            self.col_iter = 0

        # If we've gone past the last row, stop iteration and reset iterators.
        if self.row_iter >= len(self.rows):
            self.row_iter = 0
            self.col_iter = -1
            raise StopIteration
        # Otherwise, return the next value.
        else:
            return self.rows[self.row_iter][self.col_iter]

    def __str__(self):
        """ Python string implementation.
        Used when you call str() on object.
        e.g. this is called when you print() the object.
        """

        # String to output.
        out_str = ""

        # If empty, tell users its an empty grid.
        if len(self.rows) == 0:
            out_str = "Size = 0 x 0 (no data)"
        # Otherwise, tell users grid size, then print data.
        else:

            # Grid dimensions.
            out_str = f"Size = {len(self.rows)} x {len(self.rows[0])}\n\n"

            # Grid data.
            for row in self.rows:
                for cell in row:
                    out_str += str(cell)
                out_str += "\n"

        # Return the string.
        return out_str

    def Height(self):
        """ Grid height.
        """
        return self.RowCount()

    def RowCount(self):
        """ Number of rows in grid.
        """
        return len(self.rows)

    def Width(self):
        """ Grid width.
        """
        return self.ColCount()

    def ColCount(self):
        """ number of columns in grid.
        """
        if self.RowCount() == 0:
            return 0
        else:
            return len(self.rows[0])

    def Set(self, row_ind, col_ind, value):
        """ Set cell in grid to value.
        We address grid positions with indexes e.g. The first cell is 0,0.
        If the grid isn't big enough, we'll expand it as necessary.
        """

        # Lengths need to be 1 more than index.
        row_len = row_ind + 1
        col_len = col_ind + 1

        # Make sure existing rows are long enough.
        # Would be quicker to keep a list of row lengths.
        for row in self.rows:
            if len(row) < col_len:
                row.extend([None] * (col_len - len(row)))

        # Make sure we have enough rows.
        while len(self.rows) < row_len:
            self.rows.append([None] * col_len)

        # Now set value.
        self.rows[row_ind][col_ind] = value

    def Get(self, row_ind, col_ind):
        """ Get value at grid cell.
        Return None if index doesn't exist.
        """

        # If row index is greater than the number of rows, nothing to get.
        if (row_ind < 0) or (row_ind >= len(self.rows)):
            return None
        elif (col_ind < 0) or (col_ind >= len(self.rows[row_ind])):
            return None
        else:
            return self.rows[row_ind][col_ind]

    def GetRows(self):
        """ Get all rows in the grid.
        """
        return self.rows

    def GetCols(self):
        """ Get all columns in the grid.
        Iterate over the rows and create lists of columns then return them.
        """
        columns = []
        index = 0
        while index < self.Width():
            columns.append([row[index] for row in self.rows])
            index += 1
        return columns

    def GetRow(self, row_ind):
        """ Get row at index.
        """

        # Make sure row exists.
        if row_ind < len(self.rows):

            # Return row.
            return self.rows[row_ind]

        # Otherwise None.
        return None

    def GetCol(self, col_ind):
        """ Get column at index.
        """

        # If we have at least 1 row.
        if len(self.rows) > 0:

            # If the column index refers to a real column.
            if col_ind < len(self.rows[0]):

                # Build the column of data.
                column = []
                for row in self.rows:
                    column.append(row[col_ind])
                return column

        # Otherwise None.
        return None

    def ResetAutoFill(self):
        """ Res
        """
        self.af_row = 0
        self.af_col = 0

    def AutoFill(self, value):
        """ Auto fill allows us to pass values to the grid which will be
        stored sequentially in the grid layout.

        Make sure to reset auto fill first.

        If we go past the end, we'll start filling the grid again from the
        beginning.
        """

        # Insert value.
        self.Set(self.af_row, self.af_col, value)

        # Increment.
        self.af_col += 1
        if self.af_col >= self.Width():
            self.af_col = 0
            self.af_row += 1

        # If we've gone past the end of the grid, reset.
        if self.af_row >= self.RowCount():
            self.ResetAutoFill()

    def InsertRow(self, row_index, row_data = [], default_value=None):
        """ Insert a row at the specified index.
        Can specify a default value to insert.

        NB. Cannot currently insert a pre-made set of values!
        """

        # TODO: Want to add insert row of populated data mechanism, and append row convenicnce function!

        # If we have a pre-made row of data.
        # If it's the same width as the current grid width, append it.
        # Or if grid width is 0, append it.
        if (len(row_data) == self.Width()) or (self.Width() == 0):
            self.rows.insert(row_index, row_data)
        


        # Insert empty row.
        self.rows.insert(row_index, [default_value] * self.Width())

    def InsertCol(self, col_index, default_value=None):
        """ Insert a column at the specified index.
        Can specify a default value to insert.

        NB. Cannot currently insert a pre-made set of values!
        """

        # Increase length of each row.
        for row in self.rows:
            row.insert(col_index, default_value)

    def GetPositions(self, value):
        """ Get a list of grid positions for the given value.

        For every location on the grid that the value of the grid equals the
        provided value. return the location.

        A location is [row_index , col_index].
        """
        items = []
        for row_index, row in enumerate(self.GetRows()):
            for col_index, item in enumerate(row):
                if item == value:
                    items.append([row_index, col_index])
        return items

#------------------------------------------------------------------------------

class LoadingBar:
    """
    A terminal loading bar.

    Example code, how to use:

    import time
    bar = LoadingBar()
    percent = 0
    while True:
        bar.update(percent)
        percent += 1
        time.sleep(0.3)
        if percent >= 100:
            break
    """

    def __init__(self):
        self.percent:float = 0

    def update_percent(self, percent):
        """Update and display."""
        self.percent = percent
        self.display()

    def display(self):
        """Display the loading bar."""

        # Clear the current line.
        sys.stdout.write("\033[2K")

        # Go to start of line.
        sys.stdout.write("\033[1000D")

        # Work out how many symbols to draw.
        symbols = int((self.percent / 100) * 50)

        # Draw loading bar.
        sys.stdout.write("[" + (symbols * "=") + ((50 - symbols) * " ") + f"] ({self.percent}%)")

        # Flush to display.
        sys.stdout.flush()
