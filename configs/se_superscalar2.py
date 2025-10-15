# se_superscalar_clean.py
# Minimal SE-mode superscalar config with stats dump

import argparse
import m5
from m5.objects import *

# -----------------------------
# Arguments
# -----------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--bench", type=str,
                    help="Path to binary to run")
parser.add_argument("--width", type=int, default=1,
                    help="Issue width for fetch/decode/rename/issue/commit")
parser.add_argument("--stats-file", type=str, default="stats.txt",
                    help="Stats output file")
args = parser.parse_args()

# -----------------------------
# System setup
# -----------------------------
system = System()
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "3GHz"
system.clk_domain.voltage_domain = VoltageDomain()

system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MB")]
system.membus = SystemXBar()

# -----------------------------
# CPU (DerivO3CPU with tunable widths)
# -----------------------------
width = args.width
cpu = DerivO3CPU()
cpu.fetchWidth = width
cpu.decodeWidth = width
cpu.renameWidth = width
cpu.issueWidth = width
cpu.commitWidth = width

# Increase ROB and queues
cpu.numROBEntries = 192
cpu.numIQEntries = 64
cpu.LQEntries = 64
cpu.SQEntries = 64

system.cpu = cpu


# -----------------------------
# Memory controller
# -----------------------------
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8(range=system.mem_ranges[0])  # remove size parameter
system.mem_ctrl.port = system.membus.mem_side_ports


system.system_port = system.membus.cpu_side_ports
cpu.icache_port = system.membus.cpu_side_ports
cpu.dcache_port = system.membus.cpu_side_ports

# -----------------------------
# Workload
# -----------------------------
process = Process()
process.cmd = [args.bench] if args.bench else ["/bin/ls"]

system.workload = SEWorkload.init_compatible(process.cmd[0])
system.cpu.workload = process
system.cpu.createThreads()
cpu.createInterruptController()

cpu.interrupts[0].pio = system.membus.mem_side_ports
cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# -----------------------------
# Root & simulate
# -----------------------------
root = Root(full_system=False, system=system)
m5.instantiate()

print(f"Running {process.cmd} with issue width = {width}")
exit_event = m5.simulate()
print('Exit @ tick', m5.curTick(), 'because', exit_event.getCause())

# -----------------------------
# Dump stats explicitly
# -----------------------------
m5.stats.dump()
print(f"Stats dumped to {args.stats_file}")

