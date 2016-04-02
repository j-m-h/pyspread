from apiclient import errors

class scriptError(Exception):
	"""An error caused by the script failing to run."""
	pass # everything can be inherited from Exception


def _call_script(service, function_name, params):
	"""Calls a given function from the background google apps script.

	Params:
		service: the object returned by a call of the form discovery.build('script', 'v1', http=http)
		function_name: the name of the function to be called, as a string
		params: the parameters that the function takes, as a list
			For example, if your function takes parameters x and y, passing in params as [1, 7] will set x to 1 and y to 7.

	Returns:
		Whatever the google apps script returns if the run is successful


	"""
	# Create an execution request object.
	request = {"function": "getUserFromID", "parameters": [str(id_num)]}
	# NOTE: Turn OFF devMode once this is out of the testing phase

	try:
		# Make the API request.
		response = service.scripts().run(body=request,
			scriptId=SCRIPT_ID).execute()

		if 'error' in response:
			# The API executed, but the script returned an error.

			# Extract the first (and only) set of error details. The values of
			# this object are the script's 'errorMessage' and 'errorType', and
			# an list of stack trace elements.
			error = response['error']['details'][0]
			print("Script error message: {0}".format(error['errorMessage']))

			if 'scriptStackTraceElements' in error:
				# There may not be a stacktrace if the script didn't start
				# executing.
				print("Script error stacktrace:")
				for trace in error['scriptStackTraceElements']:
					print("\t{0}: {1}".format(trace['function'],
					    trace['lineNumber']))
			return "" # if an error occured, can't get the name back
		else:
			# means the request went through without error, so return what the request returned --> a name or the empty string
			return str(response['response']['result'])

	except errors.HttpError as e:
		# The API encountered a problem before the script started executing.
		print(e.content)