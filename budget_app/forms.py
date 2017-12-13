from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

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

class UserForm(forms.ModelForm):

	class Meta:
		model = get_user_model()
		fields = ['username', 'email', 'password',]
		widgets = {'password': forms.PasswordInput()}

# this form extends the above user form to allow for a UserRecord to be created along with
# the User.
class UserRecordForm(UserForm):

	initial_funds = forms.FloatField()

	class Meta(UserForm.Meta):
		fields = UserForm.Meta.fields + ['initial_funds']