import m5
import sys
from m5.objects import (
    System,
    Root,
    SrcClockDomain,
    VoltageDomain,
    SystemXBar,
    O3CPU,
    Process,
    AddrRange,
    LocalBP,
    TournamentBP
)

# -----------------------------
# Branch predictor from command line
# -----------------------------
if len(sys.argv) > 1:
    branch_predictor = sys.argv[1]  # "LocalBP" or "TournamentBP"
else:
    branch_predictor = "LocalBP"  # default

print("Branch predictor selected:", branch_predictor)

# -----------------------------
# System setup
# -----------------------------
system = System()
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]
system.membus = SystemXBar()

# -----------------------------
# CPU setup
# -----------------------------
cpu = O3CPU()
system.cpu = cpu

# Branch predictor assignment
if branch_predictor == "LocalBP":
    cpu.branchPred = LocalBP()
elif branch_predictor == "TournamentBP":
    cpu.branchPred = TournamentBP()
else:
    print("Invalid predictor! Using LocalBP as baseline.")
    cpu.branchPred = LocalBP()

# -----------------------------
# Connect CPU ports (gem5 25)
# -----------------------------
cpu.icache_port = system.membus.cpu_side_ports
cpu.dcache_port = system.membus.cpu_side_ports
system.system_port = system.membus.cpu_side_ports

# -----------------------------
# Workload
# -----------------------------
process = Process()
process.cmd = ["/home/anna/gem5/tests/test-progs/hello/bin/x86/linux/hello"]  # verify path
system.cpu.workload = process
system.cpu.createThreads()

# -----------------------------
# Root and simulation
# -----------------------------
root = Root(full_system=False, system=system)

m5.instantiate()
print("Starting simulation...")
exit_event = m5.simulate()
print("Simulation finished @ tick", m5.curTick(), "because", exit_event.getCause())

# -----------------------------
# Print key stats
# -----------------------------
m5.stats.print_stats()
