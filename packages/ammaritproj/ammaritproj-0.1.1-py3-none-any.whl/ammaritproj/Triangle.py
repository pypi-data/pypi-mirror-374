from math import sqrt
def Area(a,b,c): 
    if a+b < c or a+c < b or b+c < a:
        return "Triangle is invalid"
    s = (a+b+c)/2
    return sqrt(s*(s-a)*(s-b)*(s-c))

def Perimeter(a,b,c):
    if a+b < c or a+c < b or b+c < a:
        return "Triangle is invalid"
    return a+b+c

def Type_by_Side(a, b, c):
    if a+b < c or a+c < b or b+c < a:
        return "Triangle is invalid"
    elif a == b == c :
        return "Equilateral triangle"
    elif a == b and a != c or b == c and b != a or a == c and a != b :
        return "Isosceles triangle"
    elif a != b != c :
        return "Scalene triangle"