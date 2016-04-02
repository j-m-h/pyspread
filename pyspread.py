from apiclient import errors
from apiclient import discovery
import httplib2

class ScriptCallError(Exception):
	"""An error caused by the script failing to run."""
	pass # everything can be inherited from Exception
class ScriptRuntimeError(Exception):
	"""An error raised by the script during execution."""
	pass # everything can be inherited from Exception

def authorize(credentials):
	"""Given a set of credentials, creates a service object and returns
	a user object that has these credentials.

	Params:
		credentials: a set of OAuth2 credentials

	Returns:
		A User object, which will have the proper permissions.
	"""
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('script', 'v1', http=http)
	return User(service)


class User:
	"""A class representing a user.  Used to create spreadsheet objects."""
	def __init__(self, service):
		"""Initialize a new User object.

		Params:
			service: a service object, returned by discovery.build

		Note: this constructor should not be called by the user.  The user should
		instead call pyspread.authorize, which will return a new User object.
		"""
		self.service = service

	def open_by_url(self, url):
		"""Open a spreadsheet by url, returning a new Spreadsheet object.

		Params:
			url: the URL of the spreadsheet to open.

		Possible errors:
			Raises a ValueError if the URL is invalid, or if the user doesn't
			  have the proper permissions.
			Raises a ScriptRuntimeError if the script fails to run properly.

		Returns:
			A new Spreadsheet object.
		"""
		return Spreadsheet(url, self)

	def open_by_key(self, key):
		"""Same as open_by_url, but takes the spreadsheet's key instead of the full URL.
		eg, for the url https://docs.google.com/spreadsheets/d/1eevXLI0wlE05lG9hTV_TS288An3vHB6danVWv9thiJI/edit
		 the key would be 1eevXLI0wlE05lG9hTV_TS288An3vHB6danVWv9thiJI
		"""
		return open_by_url("https://docs.google.com/spreadsheets/d/" + key + "/edit")

class Spreadsheet:
	"""A class representing a spreadsheet.  Mostly used to create sheet objects."""
	def __init__(self, url, user):
		"""Initialize a new Spreadsheet object.

		Params:
			url: the URL of the Spreadsheet to open.
			user: the User object used to create this Spreadsheet

		Possible errors:
			Raises a ValueError if the Spreadsheet does not exist or the user has no permission.

		Note: this constructor should not be called by the user.  The user should
		instead call one of User's open methods, which will return a new Spreadsheet.
		"""
		self._url = url
		self.user = user
		self._check_exists_and_permissions()

	@property
	def url(self):
		return self._url

	@url.setter
	def url(self, url):
		self._url = url
		self._check_exists_and_permissions()

	@property
	def service(self):
		return self.user.service

	def _check_exists_and_permissions(self):
		"""Checks to make sure that url passed into the constructor actually links
		to a real spreadsheet that the user has access to.

		Possible errors:
			Raises a ValueError if the Spreadsheet does not exist or the user has no permission.

		Note: This should not be called by the user, and should only be called
		internally from the constructor.
		"""
		try:
			_call_script(self.service, "checkSSExists", [self.url])
		except(ScriptRuntimeError):
			raise ValueError('Sheet does not exist or user does not have permission')

	def get_sheet_names(self):
		"""Returns a list of all the names of sheets in this spreadsheet.

		Returns:
			A list containing all the names of sheets.
		"""
		return _call_script(self.service, "getSheetNames", [self.url])

	def get_sheet(self, sheet_name):
		"""Returns a sheet object corresponding to the sheet on the current
		spreadsheet with the name sheet_name.

		Params:
			sheet_name: the name of the sheet to find.

		Possible errors:
			Raises a ValueError if the sheet does not exist.

		Returns:
			A new sheet object.
		"""
		return Sheet(sheet_name, self)



class Sheet:
	"""Class representing a sheet within a spreadsheet."""
	@property
	def service(self):
		return self.spreadsheet.user.service
	@property
	def url(self):
		return self.spreadsheet.url

	def __init__(self, sheet_name, parent_spreadsheet):
		"""Initialize a new sheet object.

		Params:
			sheet_name: the name of the sheet you want to open.
			parent_spreadsheet: the Spreadsheet object used to create this sheet.

		Possible errors:
			Raises a ValueError if the sheet does not exist.

		Note: This constructor should not be called by the user.  The user should instead call one of the 
		open sheet functions from a spreadsheet object, which will then call this constructor.
		"""
		self._name = sheet_name
		self._spreadsheet = parent_spreadsheet
		self._check_exists()

	@property
	def name(self):
		return self._name

	@property
	def spreadsheet(self):
		return self._spreadsheet

	@name.setter
	def name(self, name):
		self._name = name
		self._check_exists()


	def _check_exists(self):
		"""Checks to make sure that name passed into the constructor is actually a
		sheet in the parent spreadsheet.

		Possible errors:
			Raises a ValueError if the sheet does not exist.

		Note: This should not be called by the user, and should only be called
		internally from the constructor.
		"""
		try:
			_call_script(self.service, "checkSheetExists", [self.url, self.name])
		except(ScriptRuntimeError):
			raise ValueError("Spreadsheet at URL " + self.url + " does not have a sheet called " + self.name + ".")

	def get_range(self, start_row, start_col, num_rows, num_cols):
		"""Returns the value within the range (start_row, start_col) to (start_row + num_rows, start_col + num_cols)
		Note that, to stay consistent with the spreadsheet, rows and columns are 1 indexed.

		Params:
			start_row: The first row to pull data from
			start_col: The first column to pull data from
			num_rows: The number of rows to pull from
			num_cols: The number of columns to pull from

		Returns:
			A 2D list with the sheet's values, where each sublist corresponds to a row in the sheet.
			  This means that the list will contain num_rows sublists, each containing num_cols values.
			  Empty cells are represented by the empty string.
		"""
		return _call_script(self.service, 'getMatrix', [self.url, self.name, start_row, start_col, num_rows, num_cols])

	def get_column(self, col):
		"""Returns the values stored in column col.

		Params:
			col: The column to get data from

		Returns:
			A list containing all the values stored in that column.
			  This list only includes values up to the last cell in the column with data in it,
			  so an empty column will return an empty list.
		"""
		col = _call_script(self.service, 'getColumn', [self.url, self.name, col])
		col = list(tuple(zip(*col))[0])
		return col

	def get_row(self, row):
		"""Returns the values stored in row row.

		Params:
			row: The row to get data from

		Returns:
			A list containing all the values stored in that row.
			  This list only includes values up to the last cell in the row with data in it,
			  so an empty row will return an empty list.
		"""
		return _call_script(self.service, 'getRow', [self.url, self.name, row])

	def get_cell_value(self, row, col):
		"""Returns the values stored in the cell at row row and column col.

		Params:
			row: The row the cell is in
			col: The column the cell is in

		Returns:
			The value stored in that cell.  Empty cells will return the empty string.
		"""
		return _call_script(self.service, 'getCellValue', [self.url, self.name, row, col])

	def set_cell_value(self, row, col, val):
		"""Sets the value of the cell at (row, col) to val.

		Params:
			row: The row the cell is in
			col: The column the cell is in
			val: The value to set the cell to
		"""
		_call_script(self.service, "setCellValue", [self.url, self.name, row, col, val])

	def set_range(self, start_row, start_col, num_rows, num_cols, vals):
		"""Sets the values of the cells in the range to the values specified in vals.

		Params:
			start_row: The first row to add data to
			start_col: The first column to add data to
			num_rows: The number of rows to add to
			num_cols: The number of columns to add to
			vals: A 2D list of values, where each sub list is a row

		Possible errors:
			Raises a ValueError if vals has the wrong dimensions.
		"""
		if len(vals) != num_rows:
			raise ValueError("set_range expected vals with " + num_rows + " rows, but found " + len(vals) + ".")
		for row in range(num_rows):
			curr_len = len(vals[row])
			if curr_len != num_cols:
				raise ValueError("set_range expected vals with " + num_cols + " cols, but row " + row + " had " + curr_len + ".")
		_call_script(self.service, "setRange", [self.url, self.name, start_row, start_col, num_rows, num_cols, vals])

	def get_max_row(self):
		"""Returns the last row in the spreadsheet with any values in it."""
		return _call_script(self.service, "getMaxRow", [self.url, self.name])

	def get_max_col(self):
		"""Returns the last col in the spreadsheet with any values in it."""
		return _call_script(self.service, "getMaxCol", [self.url, self.name])

	def insert_rows_at_end(self, n):
		"""Inserts n new rows at the end of the sheet.

		Params:
			n: The number of new rows to insert
		"""
		return _call_script(self.service, "insertRowAtEnd", [self.url, self.name, n])

	def insert_cols_at_end(self, n):
		"""Inserts n new columns at the right of the sheet.

		Params:
			n: The number of new columns to insert
		"""
		return _call_script(self.service, "insertColAtEnd", [self.url, self.name, n])


def _call_script(service, function_name, params):
	"""Calls a given function from the background google apps script.
	Adapted from the google tutorial on calling scripts: https://developers.google.com/apps-script/guides/rest/quickstart/python#step_3_set_up_the_sample

	Params:
		service: the object returned by a call of the form discovery.build('script', 'v1', http=http)
		function_name: the name of the function to be called, as a string
		params: the parameters that the function takes, as a list
			For example, if your function takes parameters x and y, passing in params as [1, 7] will set x to 1 and y to 7.

	Returns:
		Whatever the google apps script returns if the run is successful (or nothing if the script returns nothing)

	Possible errors:
		Raises a ScriptCallError if the script errors before running
		Raises a ScriptRuntimeError if the script errors while running

	Note that this function should only be called internally.
	"""
	# Create an execution request.
	request = {"function": function_name, "parameters": params}
	# NOTE: Turn OFF devMode once this is out of the testing phase
	try:
		# Make the API request.
		response = service.scripts().run(body=request, scriptId="Mp_xsj65X7Eguu6LJl6VeZkDr5LHPQgOS").execute()

		if 'error' in response:
			# The API executed, but the script returned an error.
			error = response['error']['details'][0]
			error_message = error['errorMessage']

			if 'scriptStackTraceElements' in error:
				# There may not be a stacktrace if the script didn't start executing.
				error_message += "\nStacktrace:"
				for trace in error['scriptStackTraceElements']:
					error_message += "\n\t{0}: {1}".format(trace['function'], trace['lineNumber'])
			raise ScriptRuntimeError("Error while calling function " + function_name + " with parameters (" 
				+ ",".join(str(e) for e in params) + ")\nError message: " + error_message)
		else:
			# means the request went through without error, so return what the request returned
			if 'result' in response['response']:
				return response['response']['result']

	except errors.HttpError as e:
		# The API encountered a problem before the script started executing.
		raise ScriptCallError("Failed to call function " + function_name + " with parameters (" 
			+ ",".join(str(e) for e in params) + ")\nError message: " + e.content)
