from ZesAntaris import ZesAntarisOperator, read_STATUS_pin, set_NRESET_pin
import RPi.GPIO as GPIO
import time

PI_STATUS_LED = 30
GPIO.setmode(GPIO.BCM)
GPIO.setup(PI_STATUS_LED, GPIO.OUT)

# Blinking LED
times = 0
while times < 3:
	GPIO.output(PI_STATUS_LED, False)
	time.sleep(0.3)
	GPIO.output(PI_STATUS_LED, True)
	time.sleep(0.3)
	times += 1


status = read_STATUS_pin()
print(f'FLAG is {status}')

input('Connect power, then press any key to continue...')


set_NRESET_pin(False)
print('NRSET is now set LOW...')

time.sleep(1)
status = read_STATUS_pin()
print(f'FLAG is {status}')
time.sleep(1)

set_NRESET_pin(True)
print('NRSET is now set HIGH...')

time.sleep(1)
status = read_STATUS_pin()
print(f'FLAG is {status}')
time.sleep(1)

while True:
	msg = ZesAntarisOperator.test_operation_A(0)
	if msg:
		GPIO.output(PI_STATUS_LED, True)
	else:
		GPIO.output(PI_STATUS_LED, False)
	ZesAntarisOperator.test()
	time.sleep(1)
