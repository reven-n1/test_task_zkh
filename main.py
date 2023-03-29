from asyncio import run
from database import Database

def first_task() -> int:
    """
    Returns difference between string dates (days) with date format validation without using libs

    Raises:
        ValueError: if date format does not match the specified

    Returns:
        int: dif between dates (days)
    """
    from re import match

    def is_leap(year: int) -> bool:
        return ((year) % 4 == 0 and ((year) % 100 != 0 or (year) % 400 == 0))

    def calculate(year: int, month: int, day: int) -> int:
        y = year - 1
        return int(day + (214 * month + 20) / 7 - 35 + 2 * (month < 3) + (is_leap(year) and month > 2) + y * 365 + y/4 - y/100 + y/400)
    
    def parse_date(date: str) -> tuple:
        year, month, day = [int(item[1:]) if item.startswith('0') else int(item) for item in date.split("-")]
        return year, month, day
    
    def validate_date(date: str) -> bool:  
        if match("([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))", date): return parse_date(date)
        else: raise ValueError
    
    first_date = validate_date(input("first date: "))
    second_date = validate_date(input("second date: "))

    return abs(calculate(*first_date) - calculate(*second_date))

def second_task() -> int:
    """
    Return minimum possible number obtained after removal from strings of k digits

    Returns:
        int: min number
    """
    try:
        num = input("num: ")
        k = int(input("k: "))
        
        for _ in range(k):
            num = str(min(int(num[:i] + num[i+1:]) for i in range(len(num))))
        
        return num
    except ValueError:
        print("not correct value")


async def get_resul_collection() -> dict:
    """
    Correlates Accrual and payments by terms
    """
    def find_payment(payment, accruals):
        try:
            accruals_month = [item.month for item in accruals]
            if payment.month in accruals_month:
                return payments.pop(accruals_month.index(payment.month))
            elif payment.date >= accruals[-1].date:
                return accruals.pop(-1)
            else:
                return None
                
        except:
            return None
    
    async with Database.get_class_session() as session:
        accruals = (await session.execute(select(Accrual.id, Accrual.date, Accrual.month).order_by(Accrual.date))).all()
        
        payments = (await session.execute(select(Payment.id, Accrual.date, Accrual.month))).all()
    
     
    result = {}
    
    for payment in payments:
        result[payment.id] = find_payment(payment, accruals)
    
    return result
        


if __name__ == "__main__":
    print(f"diff: {first_task()}")
    print(f"result: {second_task()}")
    
    # sorry, im too busy and lazy to generate models, specify dependency imports etc.
    # if value is none -> no payment to accrual
    run(get_resul_collection())