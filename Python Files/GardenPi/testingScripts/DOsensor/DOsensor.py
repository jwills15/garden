import i2cPy3

device = i2cPy3.main()
print(device)
test = float(device)
if test > 5:
    print('turn on the valve')
