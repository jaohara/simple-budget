from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

# this is needed to reference user model from setting
from django.contrib.auth import get_user_model

from django.utils import timezone

from decimal import Decimal

import datetime as dt

# might not need this, but just so I don't forget
# import uuid

# Model for category tags
class Category(models.Model):
	name = models.CharField(max_length=200)

	def __str__(self):
		return "Category - {}".format(self.name)

# Model for transaction log
class Transaction(models.Model):
	category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL)
	date = models.DateTimeField(default=timezone.now)
	memo = models.CharField(max_length=1000, blank=True, default="")
	user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
	value = models.DecimalField(default=Decimal(0.0), decimal_places=2, max_digits=64)

	def __str__(self):
		return "Transaction by {} on {}".format(self.user, self.date)


"""
	This model is currently running into an issue implementing the 'user' field.

	Because I haven't specified a default value for a non-nullable field, the 
	migration manager isn't allowing me to create it. Funny thing is, I seem to be
	doing the exact same thing in the above "Transaction" model, and I don't know
	what it was that made it so I was able to create that without any issue.

	Either way, the "Bill" model should be implemented in a similar way - it needs
	a user, and shouldn't default to an arbitrary one. My views should protect the
	model from being created without a currently authenticated user. 

	Seeing as I haven't implemented Bill functionality yet (12/2/17), I'm going
	to let this stand for now.
"""
class Bill(models.Model):
	category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
	date_due = models.DateTimeField(default=timezone.now)
	name = models.CharField(max_length=200)
	#user 		= models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
	value = models.IntegerField(default=0)

	def __str__(self):
		return "Bill '{}' for {}".format(self.name, self.user)

class UserRecord(models.Model):
	# hold a month of time delta?
	def_date_range = models.DurationField(default=dt.timedelta(weeks=4))
	max_display_categories = models.IntegerField(
		default=8,
		validators=[MaxValueValidator(64), MinValueValidator(2)]
	)
	initial_funds = models.DecimalField(default=Decimal(0.0), decimal_places=2, max_digits=64)
	user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)

	def __str__(self):
		return "{}'s UserRecord".format(self.user)