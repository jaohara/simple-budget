from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

from .models import Transaction

class TransactionForm(forms.ModelForm):

	value = forms.DecimalField(widget=forms.NumberInput(attrs={
														'class': 'form-control',
														'placeholder': 0.00,
													}))
	memo = forms.CharField(widget=forms.TextInput(attrs={
												  'class': 'form-control',
												  'placeholder': 'Memo',
												}))

	#date = forms.DateTimeField(widget=forms.DateInput(attrs={'class': 'form-control',}))


	class Meta:
		model = Transaction
		fields = ['value', 'memo']
		#fields = ['value', 'memo', 'date']
		#fields = ['category', 'memo', 'value',]
		#widgets = {'category': forms.TextInput()}


class BudgetAuthenticationForm(AuthenticationForm):

	username = forms.CharField(label="Username",
							   widget=forms.TextInput(attrs={
													  'class': 'form-control',
													  'placeholder': 'Username',
								}))
	password = forms.CharField(label="Password",
							   widget=forms.PasswordInput(attrs={
													  	  'class': 'form-control',
													  	  'placeholder': 'Password',
								}))



# considering this has the same widgets as above, is it possible to extend this from that?
class UserForm(forms.ModelForm):


	username = forms.CharField(label="Username",
							   widget=forms.TextInput(attrs={
													  'class': 'form-control',
													  'placeholder': 'Username',
								}))
	password = forms.CharField(label="Password",
							   widget=forms.PasswordInput(attrs={
													  	  'class': 'form-control budget-password',
													  	  'placeholder': 'Password',
								}))
	email = forms.CharField(label="Email",
							widget=forms.EmailInput(attrs={
													'class': 'form-control',
													'placeholder': 'Email',
								}))


	class Meta:
		model = get_user_model()
		fields = ['username', 'email', 'password',]

# this form extends the above user form to allow for a UserRecord to be created along with
# the User.
class UserRecordForm(UserForm):

	initial_funds = forms.FloatField(label="Initial Funds",
									 widget=forms.NumberInput(attrs={
														'class': 'form-control',
														'placeholder': 0.00,
									}))

	class Meta(UserForm.Meta):
		fields = UserForm.Meta.fields + ['initial_funds']