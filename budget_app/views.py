from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.template.loader import render_to_string

from django.http import JsonResponse
from django.core.serializers import serialize

from django.contrib.auth.models import User
from .models import Category, Transaction, Bill, UserRecord
from .forms import TransactionForm, UserForm, UserRecordForm

from django.utils import timezone

from decimal import Decimal
import datetime as dt
import pdb


"""
	=========================
	TRANSACTION RELATED VIEWS
	=========================
"""
@login_required
def transaction_log(request, sort_order="-date", date_range_start=None, date_range_end=None, all_boolean=None):

	"""
		I'm running into headaches when I strip the datetime down to just a date object as the 
		date object is always naive. When I pass these to the JS Date constructor in the frontend 
		they are manually adding the timezone offset (in my case, -8 for pacific time) to midnight
		of the giving date, making every datetime represent 4pm on the previous date which is
		causing the bounds to not be accurate.
	"""

	# this is a bit wonky - I need the beginning of the day for the timezone-aware version of the date
	# when the user joined. This seems like the best way to make this happen. 
	user_joined = timezone.localtime(request.user.date_joined).replace(hour=0, minute=0, second=0, microsecond=0)


	"""
		Here's another issue that I need to flesh out - the original design for this was poor, and now I'm running 
		into problems with the graphs for ranges of time that aren't the entire span of the user's lifetime.

		The offsets for each day are being calculated based on the initial funds, so they're inaccurate when
		the funds at the start of the range aren't equal to the intial funds. This is the case for pretty
		much any day besides the first day that the user registered.

		What's the solution to this? Maybe I should always grab the entire set of transacions so all of the 
		calculations are accurate and simply slice out the proper range. This will be accurate but inefficient.

		I could also work backwards from current funds, but this will create the same problem in the reverse
		order. Funds will be inaccurate if current_funds on the last day selected doesn't equal the most current
	"""
	initial_funds = request.user.userrecord.initial_funds
	
	form = TransactionForm()





	#	=================================
	#	Begin Date selection related code
	#	=================================

	curr_datetime = timezone.localtime(timezone.now())

	if "all_boolean" in request.GET and request.GET["all_boolean"] != 'false':
		all_boolean = request.GET["all_boolean"]

	if (bool(all_boolean)):
		date_range_start = user_joined

	else:
		if "date_range_start" in request.GET:
			date_range_start = dt.datetime.strptime(request.GET["date_range_start"][:10], "%Y-%m-%d")
			date_range_start.replace(tzinfo=timezone.get_current_timezone())

		if "date_range_end" in request.GET:
			date_range_end = dt.datetime.strptime(request.GET["date_range_end"][:10], "%Y-%m-%d")
			date_range_end.replace(tzinfo=timezone.get_current_timezone())


	date_range 	= request.user.userrecord.def_date_range

	if date_range_start is None:
		date_range_start = user_joined if user_joined > curr_datetime - date_range \
							  		   else curr_datetime - date_range
	date_range_end = curr_datetime if date_range_end is None else date_range_end

	# date_range_start and date_range_end need to equal their .date() values by now
	applied_date_range = date_range_end.date() - date_range_start.date()

	dates_in_range = []
	# weird edge case if user joined today
	if date_range_start.date() == date_range_end.date():
		dates_in_range.append(user_joined.strftime("%-m/%-d"))
	else:
		for day in range(applied_date_range.days + 1):
			date_added = date_range_start + dt.timedelta(days=day)
			dates_in_range.append(date_added.strftime("%-m/%-d"))


	#	==================
	#	End Date Selection
	#	==================





	all_transactions = Transaction.objects.filter(user__pk=request.user.pk)
	range_transactions = all_transactions.filter(date__gte=date_range_start.date(), 
						  date__lte=date_range_end).order_by(sort_order, "-created_date")


	# this is used for the charts so they have an accurate starting point for the collection of offsets
	range_start_funds = initial_funds + sum(transaction.value for \
						transaction in all_transactions.filter(date__lt=date_range_start.date()))
	




	# ==================================================
	# Check to make sure if funds difference is accurate
	# ==================================================

	funds_change = sum(transaction.value for transaction in all_transactions)
	current_funds_check = initial_funds + funds_change

	if request.user.userrecord.current_funds != current_funds_check:
		request.user.userrecord.current_funds = current_funds_check
		request.user.userrecord.save()

	# =========
	# End Check
	# =========





	daily_change_dict = {date:{"pos":0, "neg":0} for date in dates_in_range}

	for transaction in range_transactions:
		sign = "pos" if transaction.value > 0 else "neg"

		category = "Uncategorized" if transaction.category is None or transaction.category.name is "" \
			else transaction.category.name
		date = timezone.localtime(transaction.date).strftime("%-m/%-d")

		daily_change_dict[date][sign] += transaction.value
	

	pos_change_dict = {date:daily_change_dict[date]["pos"] for date in daily_change_dict.keys()}
	neg_change_dict = {date:daily_change_dict[date]["neg"] for date in daily_change_dict.keys()}

	# Decimals converted to floats for display in charts.js
	conv_pos_change = list(map(float, pos_change_dict.values()))
	conv_neg_change = list(map(float, neg_change_dict.values()))

	# is there a prettier way to do this? Maybe make a method?
	# Also those names are gross
	# Currency formatting also isn't determined by locale but hardcoded to USD
	statistics_list = []
	statistics_list.append({"name": "Cumulative Daily In: ",
							"id": "cumulative-daily-in",
							"value": "${:,.2f}".format(sum(conv_pos_change))})
	statistics_list.append({"name": "Cumulative Daily Out: ",
							"id": "cumulative-daily-out", 
							"value": "${:,.2f}".format(sum(conv_neg_change))})
	statistics_list.append({"name": "Average Daily In: ",
							"id": "avg-daily-in", 
							"value": "${:,.2f}".format(sum(conv_pos_change)/len(conv_pos_change))})
	statistics_list.append({"name": "Average Daily Out: ",
							"id": "avg-daily-out", 
							"value": "${:,.2f}".format(sum(conv_neg_change)/len(conv_neg_change))})


	daily_sums = [0+conv_pos_change[i]+conv_neg_change[i] for i in range(len(conv_pos_change))]

	"""
		Something to think about - I explicitly format the date in the US m/d/y format here,
		and I assume that it's formatted that way in the javascript when I parse the string
		to construct date objects. This doesn't account for someone using a european d/m/y format.
	"""

	render_context = {
					  'all_boolean': bool(all_boolean),
					  'daily_sums': daily_sums,
				  	  'date_range_start': date_range_start.strftime("%-m/%d/%y"),
				  	  'date_range_end': date_range_end.strftime("%-m/%d/%y"),
				  	  'date_end_iso': date_range_end.isoformat(),
				  	  'date_start_bound': user_joined.isoformat(),
				  	  'date_start_iso': date_range_start.isoformat(),
					  'dates_in_range': dates_in_range,
				  	  'neg_change_vals': conv_neg_change,
				  	  'pos_change_vals': conv_pos_change,
				  	  'range_start_funds': range_start_funds,
				  	  'username': request.user.username,
				  	  }

	if len(statistics_list) > 0:
		render_context['statistics_list'] = statistics_list

	if request.is_ajax():
		table_html = render_to_string('budget_app/transaction_table.html', 
									 {'transactions': range_transactions})
		render_context['table_html'] = table_html
		return JsonResponse(render_context)
	else:
		# add in the non-Json-serializable objects for actual render
		render_context['transaction_form'] = form
		render_context['transactions'] = range_transactions
		return render(request, 'budget_app/transaction_log.html', render_context) 


@login_required
def transaction_add(request):
	if request.method == "POST":

		if request.is_ajax():
			transaction = Transaction(value=request.POST.get("value"),
									  memo=request.POST.get("memo"),)

		else:
			transaction_form = TransactionForm(request.POST)
			if transaction_form.is_valid():
				transaction = Transaction(value=transaction_form.cleaned_data['value'],
									  	  memo=transaction_form.cleaned_data['memo'],)
			else:
				# this should be a form is not valid error state
				return redirect("/")

		transaction.user = request.user
		category_name = request.POST.get("category_string")
		existing_category = Category.objects.filter(name=category_name).first()

		transaction.category = existing_category if existing_category is not None else Category.objects.create(name=category_name)

		if "date_string" in request.POST:
			received_date = dt.datetime.strptime(request.POST.get("date_string")[:10], "%Y-%m-%d")
			received_date.replace(tzinfo=timezone.get_current_timezone())
			transaction.date = received_date

		transaction.save()

		#update user current funds
		request.user.userrecord.current_funds += Decimal(transaction.value)
		request.user.save()

		# right now we're all good

		if request.is_ajax():
			transaction_html = render_to_string("budget_app/transaction_table_row.html",{
												"hidden_initially": False,
												"transaction": transaction,
												})

			# return json object
			return JsonResponse({
					'success': True,
					'message': "Transaction created successfully.",
					'current_funds': request.user.userrecord.current_funds,
					'transactionDate': transaction.date,
					'transactionHtml': transaction_html,
				})
		else:
			return redirect("/")

	# this should be changed to return some sort of error due to incorrect http method
	else:
		if request.is_ajax():
			return JsonResponse({
				'success': False,
				'message': "Request was not submitted via POST.",
			})

		return render(request, 'budget_app/transaction_form_debug.html', {})

@login_required
def transaction_delete(request):
	if request.method == "POST":
		if request.is_ajax():
			transaction_to_delete = Transaction.objects.get(pk=request.POST["transaction_pk"])

			if transaction_to_delete.user == request.user:
				request.user.userrecord.current_funds -= transaction_to_delete.value
				request.user.userrecord.save()
				transaction_to_delete.delete()

				# let the ajax method know we succeeded
				return JsonResponse({
					'success': True,
					'message': "Transaction deleted successfully.",
					'current_funds': request.user.userrecord.current_funds,
				})
			else:
				return JsonResponse({
					'success': False,
					'message': "User {} does not own this transaction.".format(request.user.username),
					'submitted-pk': request.POST["transaction_pk"], 
				})

		else:
			# again, should be more graceful
			return redirect("/")

	else: 
		# this should exit more gracefully
		return redirect("/")

def transaction_form_debug(request):
	if request.method == "POST":

		trans_form = TransactionForm(request.POST)

		render_context = {
			"memo": request.POST.get("memo"),
			"value": request.POST.get("value"),
			"category": request.POST.get("custom_input"),
			"form_valid": trans_form.is_valid(),
		}

		return render(request, 'budget_app/transaction_form_debug.html', render_context)

	else:
		return render(request, 'budget_app/transaction_form_debug.html', {"not_post": True,})

"""
	======================
	CATEGORY RELATED VIEWS
	======================
"""

@login_required
def category_display(request, date_range_start=None, date_range_end=None):

	"""
		This is going to have to reuse a lot of the same code from the transactions - 
		how I grab the range of dates and how I sum up the income and expense totals
		for each of the categories. 

		Right off the bat we're going to need to rethink some stuff there.

		Should I put these common tasks in a separate utils.py file, or should
		I make a generic view that these both inherit from?
	"""



	return render(request, 'budget_app/categories.html', {})

"""
	==================
	USER PROFILE VIEWS
	==================
"""

def user_create(request):
	if request.method == "POST":
		# handle submitted data
		form = UserRecordForm(request.POST)
		if form.is_valid():
			new_user = User.objects.create_user(username=form.cleaned_data.get('username'),
												email=form.cleaned_data.get('email'),
												password=form.cleaned_data.get('password'),)
			new_user.save()

			new_user_record = UserRecord(user=new_user,
										 initial_funds=form.cleaned_data.get('initial_funds'),
										 current_funds=form.cleaned_data.get('initial_funds'),)
			new_user_record.save()

			login(request, new_user)
			return redirect("/")


	else:
		form = UserRecordForm()

	return render(request, 'registration/user_create.html', {'form': form})

@login_required
def user_settings(request):
	return redirect("/")