from apiclient import errors

class scriptCallError(Exception):
	"""An error caused by the script failing to run."""
	pass # everything can be inherited from Exception
class scriptRuntimeError(Exception):
	"""An error raised by the script during execution."""
	pass # everything can be inherited from Exception

class sheet:
	"""Class representing a sheet within a spreadsheet."""
	@property
	def service(self):
		return self.spreadsheet.user.service
	@property:
	def url(self):
		return self.spreadsheet.url

	def __init__(self, sheet_name, parent_spreadsheet):
		"""Initialize a new sheet object.

		Params:
			sheet_name: the name of the sheet you want to open
			parent_spreadsheet: the spreadsheet object corresponding to the spreadsheet this sheet is a part of

		Possible errors:
			Raises a valueError if the sheet does not exist.

		Note: This constructor should not be called by the user.  The user should instead call one of the 
		open sheet functions from a spreadsheet object, which will then call this constructor.
		"""
		self.name = sheet_name
		self.spreadsheet = parent_spreadsheet

	def _check_exists(self):
		"""Checks to make sure that name passed into the constructor is actually a
		sheet in the parent spreadsheet.

		Possible errors:
			Raises a valueError if the sheet does not exist.

		Note: This should not be called by the user, and should only be called
		internally from the constructor.
		"""
		_call_script(self.service, "checkSheetExists", [self.url, self.service])


def _call_script(service, function_name, params):
	"""Calls a given function from the background google apps script.
	Adapted from the google tutorial on calling scripts: https://developers.google.com/apps-script/guides/rest/quickstart/python#step_3_set_up_the_sample

	Params:
		service: the object returned by a call of the form discovery.build('script', 'v1', http=http)
		function_name: the name of the function to be called, as a string
		params: the parameters that the function takes, as a list
			For example, if your function takes parameters x and y, passing in params as [1, 7] will set x to 1 and y to 7.

	Returns:
		Whatever the google apps script returns if the run is successful

	Possible errors:
		Raises a scriptCallError if the script errors before running
		Raises a scriptRuntimeError if the script errors while running

	Note that this function should only be called internally.
	"""
	# Create an execution request.
	request = {"function": function_name, "parameters": params, "devMode": True}
	# NOTE: Turn OFF devMode once this is out of the testing phase

	try:
		# Make the API request.
		response = service.scripts().run(body=request, scriptId=SCRIPT_ID).execute()

		if 'error' in response:
			# The API executed, but the script returned an error.
			error = response['error']['details'][0]
			error_message = error['errorMessage']

			if 'scriptStackTraceElements' in error:
				# There may not be a stacktrace if the script didn't start executing.
				error_message += "\nStacktrace:"
				for trace in error['scriptStackTraceElements']:
					error_message += "\n\t{0}: {1}".format(trace['function'], trace['lineNumber'])
			raise scriptRuntimeError("Error while calling function " + function_name + " with parameters " + params + "\nError message: " + error_message)
		else:
			# means the request went through without error, so return what the request returned
			return response['response']['result']

	except errors.HttpError as e:
		# The API encountered a problem before the script started executing.
		raise scriptCallError("Failed to call function " + function_name + " with parameters " + params + "\nError message: " + e.content)