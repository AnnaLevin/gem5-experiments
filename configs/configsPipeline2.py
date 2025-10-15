import m5
from m5.objects import *

# Create the system
system = System()
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# Create CPU
system.cpu = MinorCPU()

# Create memory bus
system.membus = SystemXBar()

# Connect CPU ports to memory bus
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports

# Create memory controller
system.mem_ctrl = SimpleMemory()
system.mem_ctrl.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Create interrupt controller
system.cpu.createInterruptController()

# Create process
process = Process()
process.cmd = ['tests/test-progs/hello/bin/x86/linux/hello']
system.cpu.workload = process

# Create root
root = Root(full_system=False, system=system)

# Instantiate and run
m5.instantiate()
print("Starting simulation...")
exit_event = m5.simulate()
print(f"Exited at tick {m5.curTick()} because {exit_event.getCause()}")