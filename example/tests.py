is_odd = None or (lambda n: n % 2 == 1)
sarasa = None or (lambda x: x.get('lead', {}).get('signature'))

print (is_odd(3))
print (sarasa({'lead': {'signature': '123'}}))