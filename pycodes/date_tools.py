from datetime import date

def isValidDate(year, month, day):
    try:
        date(year, month, day)
    except:
        return False
    else:
        return True