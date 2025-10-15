#!/usr/bin/env python3
"""
se_superscalar_v25.py

SE-mode superscalar example for gem5 v25 (DerivO3CPU).
Usage example:
  build/X86/gem5.opt --outdir=out/ss1 experiments/configs/se_superscalar_v25.py \
    --bench=tests/test-progs/hello/bin/x86/linux/hello --width=1
"""

import argparse
import sys
import m5
from m5.objects import (
    System, SrcClockDomain, VoltageDomain, AddrRange, SystemXBar,
    DerivO3CPU, MemCtrl, DDR3_1600_8x8, Process, SEWorkload, Root
)

def connect_cpu_bus_ports(cpu, membus):
    # Connect cpu cache ports to the membus. API names vary; try modern names first.
    try:
        cpu.icache_port = membus.cpu_side_ports
        cpu.dcache_port = membus.cpu_side_ports
    except Exception:
        # fallback to deprecated names if needed
        try:
            cpu.icache_port = membus.slave
            cpu.dcache_port = membus.slave
        except Exception:
            print("Warning: couldn't attach icache/dcache ports using known names.", file=sys.stderr)

def connect_system_port(system, membus):
    # Connect system.system_port to the bus (try mem_side_ports / cpu_side_ports fallback)
    try:
        system.system_port = membus.cpu_side_ports
    except Exception:
        try:
            system.system_port = membus.slave
        except Exception:
            print("Warning: couldn't attach system_port using known names.", file=sys.stderr)

def connect_memctrl(mem_ctrl, membus):
    # attach MemCtrl to membus (port name may be 'port')
    try:
        mem_ctrl.port = membus.mem_side_ports
    except Exception:
        try:
            mem_ctrl.port = membus.master
        except Exception:
            print("Warning: couldn't attach mem_ctrl port using known names.", file=sys.stderr)

def connect_interrupts(cpu, membus):
    # Ensure interrupt controller created already.
    # Try a couple of possible attribute name patterns for interrupt port wiring.
    try:
        cpu.interrupts[0].pio = membus.mem_side_ports
    except Exception:
        try:
            cpu.interrupts[0].pio = membus.master
        except Exception:
            pass

    # Now try to wire the interrupt request/respond ports (names vary by build)
    wired = False
    try:
        cpu.interrupts[0].int_master = membus.cpu_side_ports
        cpu.interrupts[0].int_slave = membus.mem_side_ports
        wired = True
    except Exception:
        pass

    if not wired:
        try:
            cpu.interrupts[0].int_requestor = membus.cpu_side_ports
            cpu.interrupts[0].int_responder = membus.mem_side_ports
            wired = True
        except Exception:
            pass

    if not wired:
        # Last-ditch fallback to deprecated names
        try:
            cpu.interrupts[0].int_master = membus.master
            cpu.interrupts[0].int_slave = membus.slave
            wired = True
        except Exception:
            pass

    if not wired:
        print("Warning: couldn't wire CPU interrupt ports with known attribute names.", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bench", type=str, help="Path to binary to run (ELF)", required=False)
    parser.add_argument("--width", type=int, default=1, help="Issue width (fetch/decode/rename/issue/commit)")
    parser.add_argument("--memsize", type=str, default="512MB", help="Physical memory size (e.g. 512MB, 2GB)")
    args = parser.parse_args()

    # ----------------------------------------------------------------
    # Basic system
    # ----------------------------------------------------------------
    system = System()
    system.clk_domain = SrcClockDomain()
    system.clk_domain.clock = "3GHz"
    system.clk_domain.voltage_domain = VoltageDomain()

    system.mem_mode = "timing"
    system.mem_ranges = [AddrRange(args.memsize)]
    system.membus = SystemXBar()

    # ----------------------------------------------------------------
    # CPU (DerivO3 with tunable widths)
    # ----------------------------------------------------------------
    cpu = DerivO3CPU()
    w = args.width
    cpu.fetchWidth = w
    cpu.decodeWidth = w
    cpu.renameWidth = w
    cpu.issueWidth = w
    cpu.commitWidth = w

    # back-end resources sized for wider issue
    cpu.numROBEntries = 256
    cpu.numIQEntries = 64
    cpu.numPhysIntRegs = 256
    cpu.numPhysFloatRegs = 256
    cpu.LQEntries = 64
    cpu.SQEntries = 64

    system.cpu = cpu

    # ----------------------------------------------------------------
    # Memory controller + DRAM device (gem5 v25 pattern)
    # ----------------------------------------------------------------
    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR3_1600_8x8(range=system.mem_ranges[0])
    # connect memctrl to membus (use helper that handles name variants)
    connect_memctrl(system.mem_ctrl, system.membus)

    # Connect system and cpu cache ports to membus (helpers handle name differences)
    connect_system_port(system, system.membus)
    connect_cpu_bus_ports(cpu, system.membus)

    # ----------------------------------------------------------------
    # Workload (SE mode) — use SEWorkload to init compatible binary
    # ----------------------------------------------------------------
    if args.bench:
        # Init SEWorkload (ensures loader/ELF info is set up)
        try:
            system.workload = SEWorkload.init_compatible(args.bench)
        except Exception as e:
            print("Warning: SEWorkload.init_compatible failed:", e, file=sys.stderr)
            # still continue - some builds accept system.workload = SEWorkload([...])
            try:
                system.workload = SEWorkload()
            except Exception:
                pass

        process = Process()
        process.cmd = [args.bench]
    else:
        # fallback: run /bin/ls from host (must be compatible)
        process = Process()
        process.cmd = ["/bin/ls"]

    # attach to cpu
    try:
        system.cpu.workload = process
    except Exception:
        # fallback (older configs did cpu.workload = process)
        cpu.workload = process

    # create thread contexts
    cpu.createThreads()

    # ----------------------------------------------------------------
    # Interrupt controller (required for x86 O3 CPU in SE)
    # ----------------------------------------------------------------
    cpu.createInterruptController()
    connect_interrupts(cpu, system.membus)

    # ----------------------------------------------------------------
    # Root and start simulation
    # ----------------------------------------------------------------
    root = Root(full_system=False, system=system)
    m5.instantiate()

    print(f"Starting simulation: bench={process.cmd} width={w} memsize={args.memsize}")
    exit_event = m5.simulate()
    print("Exited @ tick", m5.curTick(), "because", exit_event.getCause())

if __name__ == "__main__":
    main()

import m5
from m5 import stats


print("Beginning simulation!")
exit_event = m5.simulate()

print("Exiting @ tick {} because {}"
      .format(m5.curTick(), exit_event.getCause()))

# Dump and finalize stats
m5.stats.dump()
m5.stats.reset()
