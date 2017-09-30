#change periods to dashes
def update_number(num):
    new_num = num.replace(".","-",3)
    return new_num

def change_numbers(num_list):
    for num in num_list:
        print num, "=>", update_number(num)