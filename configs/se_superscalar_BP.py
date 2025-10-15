

import argparse
import m5
from m5.objects import *
from m5.objects import Process, SEWorkload

print("Script loaded")
# Argument parser
parser = argparse.ArgumentParser()
parser.add_argument("--bench", type=str, help="Path to binary to run")
parser.add_argument("--width", type=int, default=1, help="CPU widths")
parser.add_argument("--bp", type=bool, help="Enable branch prediction")
args = parser.parse_args()

# System setup
system = System()
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "3GHz"
system.clk_domain.voltage_domain = VoltageDomain()
system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MB")]
system.membus = SystemXBar()

# CPU setup
width = args.width
cpu = DerivO3CPU()
cpu.fetchWidth = width
cpu.decodeWidth = width
cpu.renameWidth = width
cpu.issueWidth = width
cpu.commitWidth = width

cpu.numROBEntries = 192
cpu.numIQEntries = 64
cpu.LQEntries = 64
cpu.SQEntries = 64

if args.bp:
    print("Branch prediction ENABLED")
    cpu.branchPred = BiModeBP()
else:
    print("Branch prediction DISABLED")

system.cpu = cpu

# Memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8(range=system.mem_ranges[0])
system.mem_ctrl.port = system.membus.master

system.system_port = system.membus.slave
cpu.icache_port = system.membus.slave
cpu.dcache_port = system.membus.slave

# Workload
process = Process()
process.cmd = [args.bench] if args.bench else ["/bin/ls"]
system.workload = SEWorkload.init_compatible(process.cmd[0])
system.cpu.workload = process
system.cpu.createThreads()
cpu.createInterruptController()

try:
    cpu.interrupts[0].pio = system.membus.mem_side_ports
    cpu.interrupts[0].int_master = system.membus.cpu_side_ports
    cpu.interrupts[0].int_slave = system.membus.mem_side_ports
except AttributeError:
    cpu.interrupts[0].pio = system.membus.mem_side_ports
    cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
    cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# Root & run
root = Root(full_system=False, system=system)
m5.instantiate()

print(f"Running {process.cmd} with issue width = {width}")
exit_event = m5.simulate()
print('Exit @ tick', m5.curTick(), 'because', exit_event.getCause())

m5.stats.dump()
