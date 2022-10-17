import importlib


test = importlib.__import__('Test1').Test()

a = 'jean mich'
b = a.replace(' ', '_')
print(b)