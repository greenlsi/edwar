

def get_user_input(prompt):
    try:
        return raw_input(prompt)
    except NameError:
        return input(prompt)


answer = get_user_input("Di algo\n")
while answer != '':
    answer = get_user_input(answer+'\n')

