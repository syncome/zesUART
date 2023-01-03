from ZesAntaris import ZesAntarisOperator
import time

input('Please connect power.  Press any key to continue...')
input('Please set NRST to LOW.  Press any key to continue...')
input('Please set NRST to HIGH.  Press any key to continue...')

print('Trying UART...')

while True:
	msg = ZesAntarisOperator.test_operation_A(0)
	ZesAntarisOperator.test()
	time.sleep(1)