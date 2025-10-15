import m5
from m5.objects import *
import os


system = System()
system.clk_domain = SrcClockDomain(clock='1GHz', voltage_domain=VoltageDomain())
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# CPU
system.cpu = TimingSimpleCPU()
system.cpu.createInterruptController()

# System bus
system.membus = SystemXBar()
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports

# Simple memory
system.mem_ctrl = SimpleMemory()
system.mem_ctrl.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Connect the interrupt controller to the memory bus
if hasattr(system.cpu, "interrupts"):
    system.cpu.interrupts[0].pio = system.membus.mem_side_ports
    system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
    system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# Workload
hello_path = os.path.abspath("./tests/test-progs/hello/bin/x86/linux/hello")
assert os.path.exists(hello_path), f"{hello_path} not found"
assert os.access(hello_path, os.X_OK), f"{hello_path} not executable"

system.workload = SEWorkload.init_compatible(hello_path)

process = Process()
process.cmd = [hello_path]
system.cpu.workload = process
system.cpu.createThreads()

# Root and instantiate
root = Root(full_system=False, system=system)
m5.instantiate()

print("Starting simulation...")
exit_event = m5.simulate()
print(f"Simulation ended at tick {m5.curTick()} because {exit_event.getCause()}")
