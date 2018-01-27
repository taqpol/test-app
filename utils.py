from django.contrib.auth import get_user_model

import string
import random

def change_user_permissions():
	user_model = get_user_model()
	selection = input('enter a username, type "all" to select a name from the list, or type "q" to quit:')
	selected_user = user_model.objects.filter(username=selection)
	while not selected_user.count and selection != 'q':
		selection = input('command not recognized or no user by that name was found. \
			enter a username, type "all" to select a name from the list, or type "q" to quit:')
		if selection == 'q':
			return 
		elif selected_user.count:
			break

	if selected_user.is_active:
		print('permissions for this user are currently set to allowed.')
		choice = input('change to revoked?: (y/n) type "q" to exit')
		while choice not in ('y', 'n', 'q'):
			input('input not recognized. revoke permissions (y/n) or quit (q): ')
		else:
			if choice == 'y':
				selected_user.is_active = False
			else:
				return

	if not selected_user.is_active:
		print('permissions for this user are currently set to revoked.')
		choice = input('change to allowed?: (y/n) type "q" to exit')
		while choice not in ('y', 'n', 'q'):
			input('input not recognized. allow permissions (y/n) or quit (q): ')
		else:
			if choice == 'y':
				selected_user.is_active = True
			else:
				return


def create_user(username):
	alphabet = string.ascii_letters
	password = ''
	for _ in range(10):
		password += random.randint(0, len(alphabet)-1)
	get_user_model().create_user(username=username, password=password)
	return 