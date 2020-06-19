import getpass


def check_binary_answer(question, *args):
    def check_valid(answer):
        valid_list = list(args) + ['y', 'n', 'Y', 'N', '']
        if answer not in valid_list:
            answer = None
        return answer
    ans = check_valid(input(question).lstrip().rstrip())
    while ans is None:
        print("\n\t(!) Something went wrong: Invalid input\n")
        ans = check_valid(input(question))
    return ans.lower()


def check_answer(question, password=False, in_list=None, out_list=None, substitute_dict=None, option_list=None,
                 not_an_option_list=None, extra_info_invalid=None, extra_info_not_found=None, extra_info_exists=None):
    in_list = list() if in_list is None else in_list
    out_list = list() if out_list is None else out_list
    substitute_dict = dict() if substitute_dict is None else substitute_dict
    option_list = list() if option_list is None else option_list
    not_an_option_list = list() if not_an_option_list is None else not_an_option_list
    extra_info_invalid = '' if extra_info_invalid is None else ' ' + extra_info_invalid
    extra_info_not_found = '' if extra_info_not_found is None else ' ' + extra_info_not_found
    extra_info_exists = '' if extra_info_exists is None else ' ' + extra_info_exists
    name = None
    while name is None:
        if password:
            name = getpass.getpass(question, stream=None)
        else:
            name = input(question)
            name = name.lstrip().rstrip()
        for v in substitute_dict.keys():
            if name == v:
                name = substitute_dict[v]
        if name in option_list:
            pass
        elif any([o in name for o in not_an_option_list]):
            print("\n\t(!) Something went wrong: Invalid input '{}'.".format(name) + extra_info_invalid + "\n")
            name = None
        elif in_list and name not in in_list:
            print("\n\t(!) Something went wrong: '{}' not found.".format(name) + extra_info_not_found + "\n")
            name = None
        elif name in out_list:
            print("\n\t(!) Something went wrong: '{}' already exists.".format(name) + extra_info_exists + "\n")
            name = None
        else:
            pass
    return name
