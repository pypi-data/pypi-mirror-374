#!/usr/bin/env python3
"""
Retro Computing & Vintage Tech RPN Examples

A nostalgic journey through computing history via RPN calculations!
From punch cards to pixels, assembly to algorithms.
"""

from pydantic_rpn import RPN, RPNBuilder
import math


def retro_header():
    print("""
╦═╗╔═╗╔╦╗╦═╗╔═╗  ╔═╗╔═╗╔╦╗╔═╗╦ ╦╔╦╗╦╔╗╔╔═╗  ╦═╗╔═╗╔╗╔
╠╦╝║╣  ║ ╠╦╝║ ║  ║  ║ ║║║║╠═╝║ ║ ║ ║║║║║ ╦  ╠╦╝╠═╝║║║
╩╚═╚═╝ ╩ ╩╚═╚═╝  ╚═╝╚═╝╩ ╩╩  ╚═╝ ╩ ╩╝╚╝╚═╝  ╩╚═╩  ╝╚╝

    🕰️ VINTAGE TECHNOLOGY MEETS REVERSE POLISH NOTATION 🕰️
    """)


def main():
    retro_header()
    
    # =============================================================================
    # Punch Card & Mainframe Era (1940s-1960s)
    # =============================================================================
    print("🕳️  Punch Card & Mainframe Era:")
    
    # IBM punch card capacity: 80 columns × 12 rows = 960 holes max
    punch_card_capacity = RPN("columns rows *")
    holes = punch_card_capacity.eval(columns=80, rows=12)
    print(f"  IBM punch card capacity: {holes} possible holes")
    
    # ENIAC power consumption: 150kW (enough to dim Philadelphia!)
    eniac_bulbs = RPN("power_kw 1000 * bulb_watts /")
    bulbs = eniac_bulbs.eval(power_kw=150, bulb_watts=60)  # 60W bulbs
    print(f"  ENIAC = {bulbs:.0f} light bulbs worth of power!")
    
    # Vacuum tube MTBF (Mean Time Between Failures)
    # With 17,468 tubes, failure every 2 minutes on average!
    tube_mtbf = RPN("total_tubes tube_life_hours * total_tubes /")
    mtbf_minutes = tube_mtbf.eval(total_tubes=17468, tube_life_hours=2000) * 60 / 17468
    print(f"  ENIAC tube failure rate: ~{mtbf_minutes:.1f} minutes between failures")
    
    # =============================================================================
    # Minicomputer Era (1960s-1970s) 
    # =============================================================================
    print("\n🖥️  Minicomputer Era:")
    
    # PDP-8 word size: 12 bits = 4096 possible values
    pdp8_range = RPN("2 bits **")
    range_vals = pdp8_range.eval(bits=12)
    print(f"  PDP-8 12-bit range: 0 to {range_vals-1}")
    
    # Core memory cost: $1 per bit in 1970!
    core_memory_cost = RPN("bits_total cost_per_bit *")
    memory_cost = core_memory_cost.eval(bits_total=4096, cost_per_bit=1)  # 4K core
    print(f"  4K core memory cost (1970): ${memory_cost:,}")
    
    # Teletype speed: 110 baud = ~10 characters per second
    teletype_time = RPN("message_length baud_rate 10 / /")
    seconds = teletype_time.eval(message_length=80, baud_rate=110)  # 80 char line
    print(f"  Teletype line (80 chars): {seconds:.1f} seconds to print")
    
    # =============================================================================
    # Personal Computer Revolution (1970s-1980s)
    # =============================================================================
    print("\n💻 Personal Computer Revolution:")
    
    # Apple II memory map: $0000-$BFFF (48K RAM) 
    apple2_ram = RPN("end_addr start_addr - 1024 /")
    ram_k = apple2_ram.eval(end_addr=0xBFFF, start_addr=0x0000)
    print(f"  Apple II RAM: {ram_k:.0f}K addressable space")
    
    # Commodore 64 color palette: 16 colors, 3-bit RGB-ish
    c64_colors = RPN("2 color_bits **")
    colors = c64_colors.eval(color_bits=4)  # Actually 4-bit for 16 colors
    print(f"  Commodore 64 palette: {colors} colors (iconic!)")
    
    # Floppy disk capacity: 5.25" disk = 360KB
    # Files per disk (assuming 4KB average file size)
    files_per_disk = RPN("disk_capacity_kb avg_file_size_kb /")
    files = files_per_disk.eval(disk_capacity_kb=360, avg_file_size_kb=4)
    print(f"  5.25\" floppy capacity: ~{files:.0f} files (4KB each)")
    
    # =============================================================================
    # Home Computing Specs & Comparisons
    # =============================================================================
    print("\n🏠 Home Computer Specifications:")
    
    # ZX Spectrum 48K: How many BASIC program lines fit?
    # Average line ~40 bytes (line number + BASIC tokens)
    spectrum_lines = RPN("ram_bytes line_bytes /")
    basic_lines = spectrum_lines.eval(ram_bytes=49152, line_bytes=40)  # 48K
    print(f"  ZX Spectrum BASIC: ~{basic_lines:.0f} lines possible")
    
    # Atari 2600 cart size: 4KB was standard
    # How many 6502 instructions? (avg 2 bytes per instruction)
    atari_instructions = RPN("cart_bytes 2 /")
    instructions = atari_instructions.eval(cart_bytes=4096)
    print(f"  Atari 2600 cart: ~{instructions} 6502 instructions")
    
    # BBS modem speed progression: 300 → 1200 → 2400 → 9600 baud
    # Time to download 1MB file at each speed
    download_time = RPN("file_size_bits baud_rate /")
    
    file_mb = 1
    file_bits = file_mb * 8 * 1024 * 1024  # 1MB in bits
    
    for baud in [300, 1200, 2400, 9600]:
        seconds = download_time.eval(file_size_bits=file_bits, baud_rate=baud)
        minutes = seconds / 60
        hours = minutes / 60
        if hours > 1:
            print(f"  1MB download @ {baud} baud: {hours:.1f} hours")
        elif minutes > 1:
            print(f"  1MB download @ {baud} baud: {minutes:.1f} minutes")
        else:
            print(f"  1MB download @ {baud} baud: {seconds:.1f} seconds")
    
    # =============================================================================
    # Gaming Console Mathematics
    # =============================================================================
    print("\n🎮 Gaming Console Mathematics:")
    
    # NES PPU (Picture Processing Unit) calculations
    # 256×240 resolution, 60 FPS
    nes_pixels_per_second = RPN("width height * fps *")
    pixels_sec = nes_pixels_per_second.eval(width=256, height=240, fps=60)
    print(f"  NES pixels/second: {pixels_sec:,}")
    
    # Sprite limits: NES could show 8 sprites per scanline
    max_sprites_screen = RPN("sprites_per_line scanlines *")
    max_sprites = max_sprites_screen.eval(sprites_per_line=8, scanlines=240)
    print(f"  NES theoretical max sprites: {max_sprites} (if no overlap)")
    
    # Game Boy battery life: ~30 hours on 4 AA batteries
    gameboy_power = RPN("battery_life_hours aa_capacity_mah * 4 * / 1000 *")
    avg_power = gameboy_power.eval(battery_life_hours=30, aa_capacity_mah=2000)
    print(f"  Game Boy power consumption: ~{avg_power:.1f}W average")
    
    # =============================================================================
    # Assembly Language & Low-Level Programming
    # =============================================================================
    print("\n⚙️  Assembly Language & Low-Level:")
    
    # 6502 addressing modes: How many clock cycles for different operations?
    # LDA immediate = 2 cycles, LDA absolute = 4 cycles
    cycles_per_second = RPN("cpu_mhz 1000000 *")
    cycles_sec = cycles_per_second.eval(cpu_mhz=1)  # 1MHz 6502
    print(f"  1MHz 6502: {cycles_sec:,} cycles/second")
    
    # Instructions per second (assuming avg 3 cycles per instruction)
    instructions_per_sec = RPN("cycles_per_sec avg_cycles /")
    ips = instructions_per_sec.eval(cycles_per_sec=1000000, avg_cycles=3)
    print(f"  6502 instructions/second: ~{ips:,}")
    
    # Stack size: 6502 has 256-byte stack ($0100-$01FF)
    stack_depth = RPN("256 bytes_per_call /")
    max_calls = stack_depth.eval(bytes_per_call=3)  # Return addr + locals
    print(f"  6502 max call depth: ~{max_calls:.0f} subroutines")
    
    # =============================================================================
    # Graphics & Display Technology
    # =============================================================================
    print("\n🖼️  Graphics & Display Technology:")
    
    # CGA graphics: 320×200 in 4 colors = how many bits?
    cga_bits = RPN("width height * colors log2")
    # Simplified: 2 bits per pixel for 4 colors
    cga_memory = RPN("320 200 * 2 * 8 /")  # bits to bytes
    cga_bytes = cga_memory.eval()
    print(f"  CGA 320×200×4: {cga_bytes:.0f} bytes (16KB graphics card)")
    
    # VGA memory: 640×480×256 colors = 256 colors = 8 bits per pixel
    vga_memory = RPN("640 480 * 8 * 8 / 1024 /")  # Convert to KB
    vga_kb = vga_memory.eval()
    print(f"  VGA 640×480×256: {vga_kb:.0f}KB video memory needed")
    
    # Refresh rate calculations: 60Hz = screen redrawn 60 times per second
    refresh_bandwidth = RPN("width height * bits_per_pixel * refresh_hz *")
    bandwidth = refresh_bandwidth.eval(width=640, height=480, bits_per_pixel=8, refresh_hz=60)
    bandwidth_mbps = bandwidth / (1024*1024)
    print(f"  VGA refresh bandwidth: {bandwidth_mbps:.1f} Mbps")
    
    # =============================================================================
    # Storage Technology Evolution
    # =============================================================================
    print("\n💾 Storage Technology Evolution:")
    
    # Cassette tape storage: ~1500 baud for programs
    # How long to load a 16KB program?
    cassette_load_time = RPN("program_size_bits baud_rate /")
    load_seconds = cassette_load_time.eval(program_size_bits=16*1024*8, baud_rate=1500)
    print(f"  Cassette load (16KB): {load_seconds/60:.1f} minutes")
    
    # Hard drive evolution: 10MB in 1980 cost $3000
    # Cost per MB over time
    hdd_cost_per_mb = RPN("total_cost capacity_mb /")
    cost_per_mb_1980 = hdd_cost_per_mb.eval(total_cost=3000, capacity_mb=10)
    cost_per_mb_1990 = hdd_cost_per_mb.eval(total_cost=500, capacity_mb=100)  # 100MB for $500
    print(f"  HDD cost/MB: 1980=${cost_per_mb_1980:.0f}, 1990=${cost_per_mb_1990:.0f}")
    
    # CD-ROM capacity vs floppy: 650MB vs 1.44MB
    cd_vs_floppy = RPN("cd_capacity floppy_capacity /")
    ratio = cd_vs_floppy.eval(cd_capacity=650, floppy_capacity=1.44)
    print(f"  CD-ROM vs Floppy: {ratio:.0f}× more storage!")
    
    # =============================================================================
    # Retro Gaming Performance Metrics
    # =============================================================================
    print("\n🕹️  Retro Gaming Performance:")
    
    # Pac-Man maze: 28×31 tiles = how many possible positions?
    pacman_positions = RPN("width height *")
    positions = pacman_positions.eval(width=28, height=31)
    print(f"  Pac-Man maze positions: {positions} tiles")
    
    # Space Invaders: 55 invaders, each worth points based on row
    # Bottom row = 10pts, middle = 20pts, top = 30pts
    space_invaders_max = RPN("bottom_invaders bottom_points * middle_invaders middle_points * + top_invaders top_points * +")
    max_points = space_invaders_max.eval(
        bottom_invaders=11*2, bottom_points=10,  # 2 rows of 11
        middle_invaders=11*2, middle_points=20,  # 2 rows of 11  
        top_invaders=11*1, top_points=30         # 1 row of 11
    )
    print(f"  Space Invaders max score (1 wave): {max_points} points")
    
    # Tetris scoring: Lines cleared exponentially more valuable
    # Single=40, Double=100, Triple=300, Tetris=1200
    tetris_efficiency = RPN("tetris_score single_score /")
    efficiency = tetris_efficiency.eval(tetris_score=1200, single_score=40)
    print(f"  Tetris efficiency: 4-line clear = {efficiency}× single lines")
    
    # =============================================================================
    # Builder Pattern: Retro System Spec Calculator
    # =============================================================================
    print("\n🏗️  Retro System Builder:")
    
    # Build the ultimate 1980s home computer spec
    retro_system = (RPNBuilder()
        .var("ram_kb").push(1024).mul()           # RAM in bytes
        .var("cpu_mhz").push(1000000).mul().add() # Add CPU cycles/sec  
        .var("storage_kb").push(1024).mul().add() # Add storage bytes
        .push(1000000).div())                     # Scale to reasonable number
    
    system_score = retro_system.eval(ram_kb=64, cpu_mhz=4, storage_kb=360)  # C64-ish spec
    print(f"  Retro system score (C64-era): {system_score:.1f} RetroPoints™")
    
    # Compare with modern system
    modern_score = retro_system.eval(ram_kb=16*1024*1024, cpu_mhz=3000, storage_kb=1024*1024*1024)
    ratio = modern_score / system_score if system_score > 0 else float('inf')
    print(f"  Modern system improvement: {ratio:.0f}× more powerful!")
    
    print("\n🕰️ Time travel through computing history complete! 🕰️")
    print("💾 From punch cards to pixels - RPN calculated it all! 💾")
    
    # =============================================================================
    # Easter Egg: The Ultimate Retro Computing Question
    # =============================================================================
    print("\n🥚 Ultimate Retro Computing Question:")
    
    # How many Commodore 64s would you need to equal one modern smartphone?
    # C64: 1MHz CPU, 64KB RAM
    # iPhone: ~3GHz CPU, 6GB RAM (very simplified comparison)
    
    cpu_ratio = RPN("modern_mhz retro_mhz /")
    ram_ratio = RPN("modern_ram_mb retro_ram_kb 1024 / /") 
    
    cpu_mult = cpu_ratio.eval(modern_mhz=3000, retro_mhz=1)
    ram_mult = ram_ratio.eval(modern_ram_mb=6*1024, retro_ram_kb=64)
    
    print(f"  CPU power: {cpu_mult:,.0f} C64s = 1 smartphone")
    print(f"  RAM amount: {ram_mult:,.0f} C64s = 1 smartphone")
    print("  📱 Your phone > entire 1980s computer store! 📱")


if __name__ == "__main__":
    main()