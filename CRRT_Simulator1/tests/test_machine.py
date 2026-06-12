from models.crrt_machine import CRRTMachine

machine = CRRTMachine()

print("\nInitial Status")
print(machine.get_status())

machine.start()

print("\nAfter Starting")
print(machine.get_status())

machine.stop()

print("\nAfter Stopping")
print(machine.get_status())