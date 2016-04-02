# pyspread
A utility for writing to google spreadsheets from Python

### Dependencies
You must have the python libraries apiclient and httplib2 installed.

### How to use pyspread
1. Obtain OAuth 2.0 Credentials, as explained [here](http://gspread.readthedocs.org/en/latest/oauth2.html).
2. Create a User object by calling pyspread.authorize on your credentials.
3. Create a Spreadsheet object by calling open_by_url or open_by_key from your User object.
  * Once you have a Spreadsheet, you can call get_sheet_names to get a list of all the sheets.
4. Create a Sheet object by calling get_sheet from your Spreadsheet object.
  * Now that you have a sheet, you can start using any of the public facing methods (described below).

An example of how to use pyspread, once you have your credentials:
```python
user = pyspread.authorize(credentials) # Create the User object
ss = user.open_by_key("1VB8V2MdhyBQdvxMxssjGkk_8Yq9OY60VtNiOfTJXJsc") # Create the Spreadsheet object
sheet_names = ss.get_sheet_names() # Fetch all sheet names from the Spreadsheet
print("Sheet names:")
for(name in sheet_names):
	print("   " + name)
sheet = ss.get_sheet("Example Sheet") # Create the Sheet object
print(sheet.get_cell_value(1, 2)) # Print out the value in cell B1
```

### Important notes
* In order to stay consistent with the indexing of the spreadsheet, all row and column values are 1-indexed, unless otherwise noted.
* In get methods, empty cells are represented by the empty string.
* All methods may raise a ScriptCallError.  Most of the time, this will be caused by having credentials without the right scopes or permissions.  If rerunning the program doesn't work, and don't think it's an issue with your credentials, file a bug report on the issues tracker with as much information as possible.
* Most methods may raise a ScriptRuntimeError.  If rerunning the program doesn't fix this, file a bug report on the issues tracker.
  * Neither of these errors should occur very often.  If they do, the first thing to try is always rerunning your program and seeing if it happens again.

### Public facing methods
###### pyspread
`authorize(credentials)`: Used to create a User object, given a set of OAuth2.0 credentials.  
  Returns: A User object

###### User
`open_by_url(url)`: Used to create a Spreadsheet object that corresponds to the Google spreadsheet at the given url.  
  Returns: A Spreadsheet object.  
  Will raise a ValueError if there is no spreadsheet with that URL, or if the User doesn't have access to it.  

`open_by_key(key)`: Used to create a Spreadsheet object that corresponds to the Google spreadsheet with the given key.  
  For example, a spreadsheet with the url https://docs.google.com/spreadsheets/d/1VB8V2MdhyBQdvxMxssjGkk_8Yq9OY60VtNiOfTJXJsc/edit would have the key 1VB8V2MdhyBQdvxMxssjGkk_8Yq9OY60VtNiOfTJXJsc.  
  Returns: A Spreadsheet object.  
  Will raise a ValueError if there is no spreadsheet with that key, or if the User doesn't have access to it.  

###### Spreadsheet
`get_sheet_names()`: Used to get a list of names of sheets within a spreadsheet.  
  Returns: A list containing all the names of the sheets.  

`get_sheet(sheet_name)`: Used to get a sheet with the given name.  
  Returns: A Sheet object.  
  Will raise a ValueError if there is no sheet with that name in the current spreadsheet.  

###### Sheet
`get_range_values(start_row, start_col, num_rows, num_cols)`: Used to get a 2D list of values from a range in the sheet.  
  For example, calling with parameters (1, 2, 3, 4) will get the values in the rectangle with upper left corner B1 and lower right corner F4.  
  Returns: A 2D list with the sheet's values, where each sublist corresponds to a row in the sheet.  

`get_column_values(col)`: Used to get a list of values from the column col.  
  For example, calling with parameter 3 will return all the values in column C, up to the last cell with anything in it.  
    This means that an empty column will give back an empty list.  
  Returns: A list containing all the values stored in the column.  

`get_row_values(row)`: Used to get a list of values from the row row.  
  For example, calling with parameter 2 will return all the values in row 2, up to the last cell with anything in it.  
    This means that an empty row will give back an empty list.  
  Returns: A list containing all the values stored in the row.  

`get_cell_value(row, col)`: Used to get the value from the cell in row row and column col.  
  For example, calling with parameters (2, 3) will return the value stored in cell C2.  
  Returns: The value stored in the cell.  

`set_cell_value(row, col, val)`: Used to set the value in the cell at row row and column col to val.  
  For example, calling with parameters (2, 3, "Hello World!") will set the value in cell C2 to "Hello World!".  

`set_range_values(start_row, start_col, num_rows, num_cols, vals)`: Used to set the values in a range.  
  vals should be a 2D list, where each sublist is a row.  So there should be num_rows sublists, each with num_cols values.  
  For example, calling with parameters (1, 2, 1, 2, [["Hello", "World"]]) will set cell B1 to "Hello" and cell C1 to "World".  
  Will raise a ValueError if vals has incorrect dimensions.  

`get_max_row()`: Used to get the last row in a sheet with any data in it.  
  Returns: the number of the last row with any values stored in it.  

`get_max_col()`: Used to get the last column in a sheet with any data in it.  
  Returns: the number of the last column with any values stored in it.  

`insert_rows(n)`: Used to insert n rows to the bottom of the sheet.

`insert_cols(n)`: Used to insert n columns to the bottom of the sheet.
