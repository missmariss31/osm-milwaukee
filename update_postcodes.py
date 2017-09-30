def change_zip(zip_code):
    """Isolate first 5 digits in value attribute"""
    find_zip_re = re.compile(r'(53\d{3})')
    m = find_zip_re.search(zip_code)
    if m:
        new_zip = m.group()
        return new_zip
    else:
        return zip_code
    
def update_postal_codes(fix_pc):
    for zip_code in fix_pc.keys():
        print zip_code, "=>", change_zip(zip_code)