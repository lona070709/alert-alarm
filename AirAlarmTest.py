from datetime import time
from main import alarm_status

W, B, L = time(6, 30), time(7, 0), time(8, 0)
assert alarm_status(W, B, L, False, time(6, 29)) == False
assert alarm_status(W, B, L, False, time(6, 30)) == True
assert alarm_status(W, B, L, True,  time(6, 45)) == False

assert alarm_status(W, B, L, False, time(6, 46)) == True
assert alarm_status(W, B, L, False, time(7, 10)) == True
assert alarm_status(W, B, L, False, time(8, 0))  == True
assert alarm_status(W, B, L, True,  time(8, 30)) == False
assert alarm_status(W, B, L, False, time(8, 31)) == True

assert alarm_status(W, B, L, None, time(7,23)) == True
print("passed")