#!/usr/bin/env python3
"""
DOOM RPN: Where Reverse Polish Notation Meets Classic Gaming

If Doom and RPN had a baby, this would be it! 
Featuring hardcore calculations, explosive computations, and stack-based mayhem.
"""

from pydantic_rpn import RPN, RPNBuilder
import math


def doom_header():
    print("""
██████╗  ██████╗  ██████╗ ███╗   ███╗    ██████╗ ██████╗ ███╗   ██╗
██╔══██╗██╔═══██╗██╔═══██╗████╗ ████║    ██╔══██╗██╔══██╗████╗  ██║
██║  ██║██║   ██║██║   ██║██╔████╔██║    ██████╔╝██████╔╝██╔██╗ ██║
██║  ██║██║   ██║██║   ██║██║╚██╔╝██║    ██╔══██╗██╔═══╝ ██║╚██╗██║
██████╔╝╚██████╔╝╚██████╔╝██║ ╚═╝ ██║    ██║  ██║██║     ██║ ╚████║
╚═════╝  ╚═════╝  ╚═════╝ ╚═╝     ╚═╝    ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═══╝

    🔥 REVERSE POLISH NOTATION MEETS CLASSIC GAMING 🔥
    """)


def main():
    doom_header()
    
    # =============================================================================
    # DOOM-Style Health/Armor Calculations
    # =============================================================================
    print("💀 DOOM Health & Armor System:")
    
    # Health calculation: damage reduction with armor
    # effective_damage = damage × (1 - armor_absorption)
    damage_calc = RPN("base_damage 1 armor_percent - *")
    
    # Shotgun blast (64 damage) vs 50% armor
    effective_damage = damage_calc.eval(base_damage=64, armor_percent=0.5)
    print(f"  Shotgun blast (64 dmg) vs 50% armor: {effective_damage} effective damage")
    
    # Plasma rifle damage over time: 40 dmg × 10 shots per second × 3 seconds
    plasma_dps = RPN("damage_per_shot shots_per_second * duration *")
    total_damage = plasma_dps.eval(damage_per_shot=40, shots_per_second=10, duration=3)
    print(f"  Plasma rifle (3 sec burst): {total_damage} total damage")
    
    # Health pack efficiency: health_gained / health_missing
    health_efficiency = RPN("health_gained max_health current_health - /")
    efficiency = health_efficiency.eval(health_gained=25, max_health=100, current_health=30)
    print(f"  Medkit efficiency (30→55 health): {efficiency:.2f} (100% = perfect)")
    
    # =============================================================================
    # Ballistics & Physics (DOOM-Style)
    # =============================================================================
    print("\n🚀 DOOM Ballistics & Physics:")
    
    # Rocket launcher splash damage: damage × (1 - distance/radius)²
    splash_damage = RPN("max_damage 1 distance splash_radius / - 2 ** *")
    
    # Direct hit (distance=0) vs edge hit (distance=128, radius=128) 
    direct_hit = splash_damage.eval(max_damage=200, distance=0, splash_radius=128)
    edge_hit = splash_damage.eval(max_damage=200, distance=120, splash_radius=128)
    print(f"  Rocket direct hit: {direct_hit} damage")
    print(f"  Rocket edge damage: {edge_hit:.1f} damage")
    
    # Projectile trajectory: y = x×tan(θ) - (g×x²)/(2×v²×cos²(θ))
    # Simplified for DOOM physics (no gravity in original!)
    trajectory_y = RPN("x angle_rad tan * g x 2 ** * 2 velocity 2 ** * angle_rad cos 2 ** * / -")
    
    # BFG shot trajectory (theoretical)
    y_pos = trajectory_y.eval(x=500, angle_rad=0.1, g=9.8, velocity=1000)
    print(f"  BFG trajectory at 500 units: {y_pos:.1f} units high")
    
    # =============================================================================
    # Monster Stats & AI Calculations  
    # =============================================================================
    print("\n👹 Monster Stats & AI:")
    
    # Demon spawn rate: base_rate × difficulty_multiplier × player_progress
    spawn_rate = RPN("base_rate difficulty_mult * progress_mult *")
    
    # Hell on Earth difficulty
    demons_per_minute = spawn_rate.eval(base_rate=2.0, difficulty_mult=1.5, progress_mult=2.0)
    print(f"  Demon spawn rate (Hell on Earth): {demons_per_minute} demons/minute")
    
    # Cyberdemon health scaling: base_health × (1 + 0.1×level)
    cyberdemon_health = RPN("base_health 1 0.1 level * + *")
    scaled_health = cyberdemon_health.eval(base_health=4000, level=5)
    print(f"  Cyberdemon health (level 5): {scaled_health} HP")
    
    # Accuracy calculation: base_accuracy × (1 - distance_penalty) × skill_modifier  
    demon_accuracy = RPN("base_acc 1 distance 100 / - * skill_mod *")
    hit_chance = demon_accuracy.eval(base_acc=0.8, distance=200, skill_mod=1.2)
    print(f"  Demon accuracy at 200 units: {hit_chance:.1%} hit chance")
    
    # =============================================================================
    # Speedrun Calculations (DOOM Community Classic)
    # =============================================================================
    print("\n⚡ Speedrun Mathematics:")
    
    # Straferunning speed: √(forward² + strafe²) = √(50² + 50²) ≈ 70.7 units/sec
    strafe_speed = RPN("forward_speed 2 ** strafe_speed 2 ** + sqrt")
    max_speed = strafe_speed.eval(forward_speed=50, strafe_speed=50)
    print(f"  Straferunning speed: {max_speed:.1f} units/sec (vs 50 normal)")
    
    # SR-50 glitch speed calculation (legendary DOOM speedrun trick)
    sr50_speed = RPN("base_speed 50 40 + * 50 /")  # Simplified formula
    glitch_speed = sr50_speed.eval(base_speed=50)
    print(f"  SR-50 glitch speed: {glitch_speed} units/sec (INSANE!)")
    
    # Level completion time: (distance / average_speed) + combat_time + secret_time
    completion_time = RPN("total_distance avg_speed / combat_time + secret_time +")
    level_time = completion_time.eval(total_distance=5000, avg_speed=60, combat_time=45, secret_time=15)
    print(f"  E1M1 speedrun time: {level_time:.1f} seconds")
    
    # =============================================================================
    # Resource Management (Ammo, Health, Armor)
    # =============================================================================
    print("\n📦 Resource Management:")
    
    # Ammo efficiency: damage_per_ammo = total_damage / ammo_consumed
    ammo_efficiency = RPN("total_damage ammo_used /")
    
    # Shotgun vs Chaingun efficiency
    shotgun_eff = ammo_efficiency.eval(total_damage=64, ammo_used=1)  # 1 shell
    chaingun_eff = ammo_efficiency.eval(total_damage=10, ammo_used=1)  # 1 bullet
    print(f"  Shotgun efficiency: {shotgun_eff} damage/ammo")
    print(f"  Chaingun efficiency: {chaingun_eff} damage/ammo")
    
    # Inventory optimization: value = (utility × quantity) / weight
    item_value = RPN("utility quantity * weight /")
    
    # Health potion vs Stimpack
    potion_value = item_value.eval(utility=10, quantity=1, weight=1)    # +10 health
    stimpack_value = item_value.eval(utility=10, quantity=1, weight=0.5) # +10 health, lighter
    print(f"  Health potion value: {potion_value}")
    print(f"  Stimpack value: {stimpack_value} (better!)")
    
    # =============================================================================
    # NIGHTMARE Mode Calculations
    # =============================================================================
    print("\n😈 NIGHTMARE Mode:")
    
    # Nightmare difficulty multipliers: damage × 2, speed × 1.5, spawn × 3
    nightmare_damage = RPN("base_damage 2 *")
    nightmare_speed = RPN("base_speed 1.5 *")
    nightmare_spawn = RPN("base_spawn 3 *")
    
    # Imp stats on Nightmare
    imp_dmg = nightmare_damage.eval(base_damage=8)
    imp_speed = nightmare_speed.eval(base_speed=30)
    imp_spawn = nightmare_spawn.eval(base_spawn=0.5)
    
    print(f"  Nightmare Imp: {imp_dmg} damage, {imp_speed} speed, {imp_spawn} spawn rate")
    print("  💀 NIGHTMARE MODE: Where angels fear to tread! 💀")
    
    # =============================================================================
    # Classic DOOM Number Sequences
    # =============================================================================
    print("\n🔢 DOOM Number Sequences:")
    
    # IDKFA code (God mode items): 666 (Devil's number in DOOM lore)
    idkfa_sum = RPN("6 6 6 + +")  # 6+6+6 = 18 (but 666 is the famous one)
    print(f"  IDKFA demon sum: 6+6+6 = {idkfa_sum.eval()}")
    
    # Level progression: E1M1 → E1M2 → ... → E1M9
    episode_calc = RPN("episode 10 * level +")  # E1M1 = 11, E1M2 = 12, etc.
    e1m1 = episode_calc.eval(episode=1, level=1)
    e4m9 = episode_calc.eval(episode=4, level=9)
    print(f"  Level codes: E1M1 = {e1m1}, E4M9 = {e4m9}")
    
    # Classic cheat codes in decimal
    # IDDQD = god mode, IDCHOPPERS = chainsaw
    print("  Classic cheats: IDDQD, IDKFA, IDCHOPPERS (legendary!)")
    
    # =============================================================================
    # Builder Pattern: Complex Combat Scenario
    # =============================================================================
    print("\n🏗️  Ultimate DOOM Combat Calculator:")
    
    # Multi-target combat: calculate total damage across multiple enemies
    # with weapon switching and ammo management
    combat_scenario = (RPNBuilder()
        .push(64).push(3).mul()           # Shotgun: 64×3 shots = 192 damage
        .push(10).push(20).mul().add()    # Chaingun: 10×20 shots = 200 damage  
        .push(200).add()                  # Rocket: 200 damage
        .push(40).push(15).mul().add())   # Plasma: 40×15 shots = 600 damage
    
    total_damage = combat_scenario.eval()
    print(f"  Multi-weapon combo damage: {total_damage} (enough for Cyberdemon!)")
    
    # Speedrun optimization: minimize time = distance/speed + reload_time + aim_time
    speedrun_optimize = (RPNBuilder()
        .var("distance").var("speed").div()    # Movement time
        .var("reload").add()                   # Reload time
        .var("aim").add())                     # Aim time
    
    optimal_time = speedrun_optimize.eval(distance=1000, speed=70.7, reload=0.5, aim=0.3)
    print(f"  Speedrun segment time: {optimal_time:.2f} seconds")
    
    print("\n🔥 RIP AND TEAR THROUGH THOSE CALCULATIONS! 🔥")
    print("💀 DOOM RPN: Where mathematics meets mayhem! 💀")
    
    # =============================================================================
    # DOOM RPN Easter Egg
    # =============================================================================
    print("\n🥚 DOOM RPN Easter Egg:")
    
    # The ultimate DOOM calculation: 
    # Total demons killed in all DOOM games combined!
    ultimate_doom = RPN("demons_per_level levels_per_episode * episodes_total * players_worldwide * years_active *")
    total_demons = ultimate_doom.eval(
        demons_per_level=50,      # Average demons per level
        levels_per_episode=9,     # 9 levels per episode  
        episodes_total=4,         # 4 episodes in Ultimate DOOM
        players_worldwide=10000,  # Conservative estimate
        years_active=30           # 30+ years of DOOM
    )
    
    print(f"  Total demons slain (estimated): {total_demons:,.0f}")
    print("  🎯 The most important calculation in gaming history! 🎯")


if __name__ == "__main__":
    main()