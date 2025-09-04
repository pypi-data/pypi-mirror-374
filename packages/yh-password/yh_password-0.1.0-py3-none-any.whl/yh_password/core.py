#Password Generator Project
import random


def generate_password():

  letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
  c_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
  numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
  symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

  nr_letters = random.randint(8, 10)
  nr_c_letters = random.randint(1, 2)
  nr_symbols = random.randint(2, 4)
  nr_numbers = random.randint(2, 4)

  password_list = []

  letter_list = [random.choice(letters) for _ in range(nr_letters)]
  c_letter_list = [random.choice(c_letters) for _ in range(nr_c_letters)]
  symbol_list = [random.choice(symbols) for _ in range(nr_symbols)]
  number_list = [random.choice(numbers) for _ in range(nr_numbers)]

  password_list = letter_list + c_letter_list + symbol_list + number_list

  random.shuffle(password_list)

  password = "".join(password_list)
  
  return password
  # print(f"Your password is: {password}")
