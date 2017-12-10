"""
	File to define decorators and other helper functions for the budget_app
"""

"""
	Called after a function wrapped with @login_required from django.contrib.auth.decorators,
	ensures that the logged-in user has an appropriate userrecord associated with them and
	creates one if not. 
"""
def userrecord_required(target_function):

	"""
		We're going to use the "hasattr(obj, attr)" builtin to handle this, as recommended in the 
		django docs.

		I need to work out how we're going to grab the currently logged in user - can we use
		the request object in this if we specify it as an argument?

		it will be like this:

		if hasattr(request.user, 'userrecord'):
			# all good, continue to view
		else:
			# not good, create a userrecord with default settings and then continue to viwe
	"""
	# just garbarge for now
	return ""