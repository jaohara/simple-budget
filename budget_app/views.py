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
import datetime as dt

import pdb

"""
	=========================
	TRANSACTION RELATED VIEWS
	=========================
"""
@login_required
def transaction_log(request, sort_order="-date", date_range_start=None, date_range_end=None):

	form = TransactionForm()

	date_range 	= request.user.userrecord.def_date_range
	user_joined = timezone.localtime(request.user.date_joined)
	initial_funds = request.user.userrecord.initial_funds

	max_display_categories = request.user.userrecord.max_display_categories

	curr_datetime = timezone.localtime(timezone.now())
	today_start	= dt.datetime(year=curr_datetime.year,
							  month=curr_datetime.month,
							  day=curr_datetime.day,
							  tzinfo=timezone.get_current_timezone())

	if date_range_start is None:
		date_range_start = user_joined if user_joined > curr_datetime - date_range \
							  		   else curr_datetime - date_range
	date_range_end = curr_datetime if date_range_end is None else date_range_end
	applied_date_range = date_range_end.date() - date_range_start.date()

	dates_in_range = []
	# weird edge case if user joined today
	if date_range_start.date() == date_range_end.date():
		dates_in_range.append(user_joined.strftime("%-m/%-d"))
	else:
		for day in range(applied_date_range.days + 1):
			date_added = date_range_start + dt.timedelta(days=day)
			dates_in_range.append(date_added.strftime("%-m/%-d"))

 
	all_transactions = Transaction.objects.filter(user__pk=request.user.pk)
	range_transactions = all_transactions.filter(date__gte=date_range_start, 
						  date__lte=date_range_end).order_by(sort_order)

	funds_change = sum(transaction.value for transaction in all_transactions) 
	current_funds = initial_funds + funds_change
	daily_change_dict = {date:{"pos":0, "neg":0} for date in dates_in_range}

	category_dict = {"pos":{}, "neg":{}}

	for transaction in range_transactions:
		sign = "pos" if transaction.value > 0 else "neg"
		category = transaction.category.name if transaction.category.name is not "" else "Uncategorized"
		date = timezone.localtime(transaction.date).strftime("%-m/%-d")

		#pdb.set_trace()

		# daily_change_dict = {"xx/yy":{"pos":0, "neg":0}...}
		# category_dict = {"pos":{}, "neg":{}}
		daily_change_dict[date][sign] += transaction.value

		if category in category_dict[sign].keys():
			category_dict[sign][category] += transaction.value
		else:
			category_dict[sign][category] = transaction.value
	
	sorted_expense_cat = sorted(category_dict["neg"], key=category_dict["neg"].get, reverse=False)
	sorted_income_cat = sorted(category_dict["pos"], key=category_dict["pos"].get, reverse=False)
	# make values positive for proper display in pie chart
	sorted_expense_val = [float(category_dict["neg"][k]) * -1.0 for k in sorted_expense_cat]
	sorted_income_val = [float(category_dict["pos"][k]) for k in sorted_income_cat] 

	pos_change_dict = {date:daily_change_dict[date]["pos"] for date in daily_change_dict.keys()}
	neg_change_dict = {date:daily_change_dict[date]["neg"] for date in daily_change_dict.keys()}

	# Decimals converted to floats for display in charts.js
	conv_pos_change = list(map(float, pos_change_dict.values()))
	conv_neg_change = list(map(float, neg_change_dict.values()))

	daily_sums = [0+conv_pos_change[i]+conv_neg_change[i] for i in range(len(conv_pos_change))]

	#include a request.is_ajax() check to return this data as a JSON object to update the 
	# charts without reloading the page

	# pdb.set_trace()

	render_context = {'current_funds': current_funds,
				  	  'daily_sums': daily_sums,
				  	  'date_range_start': date_range_start.strftime("%-m/%-d/%y"),
				  	  'date_range_end': date_range_end.strftime("%-m/%-d/%y"),
					  'dates_in_range': dates_in_range,
					  'funds_change': funds_change,
					  'initial_funds': initial_funds,
				  	  'neg_change_vals': conv_neg_change,
				  	  'pos_change_vals': conv_pos_change,
					  'sorted_expense_cat': sorted_expense_cat[:max_display_categories],
					  'sorted_expense_val': sorted_expense_val[:max_display_categories],
					  'sorted_income_cat': sorted_income_cat[:max_display_categories],
					  'sorted_income_val': sorted_income_val[:max_display_categories],
				  	  'username': request.user.username,
				  	  #"failure": fail_snail,
				  	  }

	if request.is_ajax():
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

		transaction.user 	= request.user
		category_name 		= request.POST.get("category_string")
		existing_category 	= Category.objects.filter(name=category_name).first()

		transaction.category = existing_category if existing_category is not None else Category.objects.create(name=category_name)

		transaction.save()

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
				transaction_to_delete.delete()

				# let the ajax method know we succeeded
				return JsonResponse({
					'success': True,
					'message': "Transaction deleted successfully."
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

# returns categories similar to the query, used to populate auto-complete list
# below category input field
def category_display(request, date_range_start=None, date_range_end=None):
	

	return redirect("/")

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
										 initial_funds=form.cleaned_data.get('initial_funds'),)
			new_user_record.save()

			login(request, new_user)
			return redirect("/")


	else:
		form = UserRecordForm()

	return render(request, 'registration/user_create.html', {'form': form})
