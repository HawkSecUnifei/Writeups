import numpy as np
from secret import flag, quotes

prizes = quotes + ['missingno'] * 4 + [flag] * 24

if __name__ == '__main__':
	print('Welcome to our playground for powerful people where you can pump yourself up and get awesome prizes!\n')
	player_count = int(input('How many players participate?\n'))
	power = np.zeros(player_count, dtype = np.int32)
	for i in range(player_count):
		power[i] = int(input(f'Player {i}, how strong are you right now?\n'))
	ready = False

	while True:
		print('What do you want to do?\n1) pump up\n2) cash in')
		option = int(input())
		if option == 1:
			power = power**2
			ready = True
		elif option == 2:
			if not ready:
				raise Exception('Nope, too weak')
			for i in range(player_count):
				if power[i] < len(quotes):
					print(f'You got an inspiration: {prizes[power[i]]}')
			exit()
		else:
			raise Exception('What?')
