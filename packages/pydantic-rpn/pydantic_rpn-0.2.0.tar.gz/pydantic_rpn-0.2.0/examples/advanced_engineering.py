#!/usr/bin/env python3
"""
🔬 Advanced Engineering RPN Examples
Inspired by HP Museum forum discussions and real-world engineering applications
"""

from pydantic_rpn import RPN, RPNBuilder
import math

def newton_cooling_law():
    """
    Newton's Law of Cooling: T(t) = T_ambient + (T_initial - T_ambient) * e^(-kt)
    
    Inspired by Ron Ross's HP calculator program for thermal engineering.
    Used in heat exchanger design and process monitoring.
    """
    print("🌡️  NEWTON'S LAW OF COOLING")
    print("=" * 50)
    
    # Temperature after cooling time
    # T(t) = T_amb + (T_0 - T_amb) * e^(-k*t)
    cooling_temp = RPN("T_amb T_0 T_amb - k t * neg exp * +")
    
    # Example: Coffee cooling from 80°C to room temperature (20°C)
    # k = 0.1 (cooling constant), t = 10 minutes
    temp_10min = cooling_temp.eval(T_amb=20, T_0=80, k=0.1, t=10)
    print(f"☕ Coffee temp after 10 min: {temp_10min:.1f}°C")
    
    # Heat exchanger example: Steam cooling with k=0.05
    temp_20min = cooling_temp.eval(T_amb=25, T_0=150, k=0.05, t=20)
    print(f"🏭 Steam temp after 20 min: {temp_20min:.1f}°C")
    
    # Time to reach target temperature: t = -ln((T_target - T_amb)/(T_0 - T_amb)) / k
    time_to_target = RPN("T_target T_amb - T_0 T_amb - / ln neg k /")
    time_needed = time_to_target.eval(T_target=30, T_amb=20, T_0=80, k=0.1)
    print(f"⏱️  Time to reach 30°C: {time_needed:.1f} minutes")

def base_conversion():
    """
    Base conversion algorithms inspired by Ben Salinas's educational program.
    Demonstrates stack manipulation and algorithmic thinking.
    """
    print("\n🔢 BASE CONVERSION ALGORITHMS")
    print("=" * 45)
    
    # Convert decimal to binary (simple powers of 2 method)
    print("📱 Decimal to Binary Conversion:")
    
    # Example: Convert 42 to binary
    # Using successive division method with RPN
    n = 42
    print(f"Converting {n} to binary:")
    
    # Manual demonstration of the algorithm
    binary_digits = []
    temp = n
    while temp > 0:
        remainder = RPN("n 2 %").eval(n=temp)
        quotient = RPN("n 2 /").eval(n=temp) 
        binary_digits.append(int(remainder))
        print(f"  {temp} ÷ 2 = {int(quotient)} remainder {int(remainder)}")
        temp = int(quotient)
    
    binary_result = ''.join(str(d) for d in reversed(binary_digits))
    print(f"✨ {n} in binary: {binary_result}")
    
    # Hexadecimal conversion example
    print(f"\n🔢 {n} in hex: {hex(n)} (using Python built-in)")
    
    # Base conversion verification
    binary_to_decimal = RPN("1 0 * 2 ** 0 + 1 1 * 2 1 ** * + 0 1 * 2 2 ** * + 1 1 * 2 3 ** * + 0 1 * 2 4 ** * + 1 1 * 2 5 ** * +")
    # This represents: 1*2^5 + 0*2^4 + 1*2^3 + 0*2^2 + 1*2^1 + 0*2^0 = 42
    decimal_check = binary_to_decimal.eval()
    print(f"✅ Binary verification: {decimal_check}")

def random_number_analysis():
    """
    Random number distribution analysis inspired by Larry Corrado's HP-25 program.
    Tests digit frequency distribution and randomness quality.
    """
    print("\n🎲 RANDOM NUMBER ANALYSIS")
    print("=" * 40)
    
    # Chi-square test for randomness (simplified)
    # X² = Σ((observed - expected)² / expected)
    chi_square = RPN("obs1 exp - 2 ** exp / obs2 exp - 2 ** exp / + obs3 exp - 2 ** exp / +")
    
    # Example: Testing digit frequency in random numbers
    # Expected frequency = 100 (for 1000 numbers, each digit should appear ~100 times)
    observed_counts = [98, 103, 95, 107, 99]  # Counts for digits 1-5
    expected = 100
    
    print("🔍 Digit Frequency Analysis:")
    chi_sq_value = 0
    for i, obs in enumerate(observed_counts):
        contribution = RPN("obs exp - 2 ** exp /").eval(obs=obs, exp=expected)
        chi_sq_value += contribution
        print(f"  Digit {i+1}: observed={obs}, contribution={contribution:.3f}")
    
    print(f"📊 Chi-square value: {chi_sq_value:.3f}")
    print("📋 Lower values indicate better randomness")

def compressible_flow():
    """
    Compressible flow calculations inspired by Frank B's thermodynamic calculator.
    Essential for aerospace and process engineering.
    """
    print("\n✈️  COMPRESSIBLE FLOW CALCULATIONS")
    print("=" * 50)
    
    # Isentropic flow relations
    # Pressure ratio: P/P0 = (1 + (γ-1)/2 * M²)^(-γ/(γ-1))
    pressure_ratio = RPN("1 gamma 1 - 2 / M 2 ** * + gamma gamma 1 - / neg **")
    
    # Example: Air flow (γ = 1.4) at Mach 0.8
    p_ratio = pressure_ratio.eval(gamma=1.4, M=0.8)
    print(f"🌪️  Pressure ratio at Mach 0.8: P/P₀ = {p_ratio:.4f}")
    
    # Temperature ratio: T/T0 = (1 + (γ-1)/2 * M²)^(-1)
    temperature_ratio = RPN("1 gamma 1 - 2 / M 2 ** * + -1 **")
    t_ratio = temperature_ratio.eval(gamma=1.4, M=0.8)
    print(f"🌡️  Temperature ratio at Mach 0.8: T/T₀ = {t_ratio:.4f}")
    
    # Density ratio: ρ/ρ0 = (1 + (γ-1)/2 * M²)^(-1/(γ-1))
    density_ratio = RPN("1 gamma 1 - 2 / M 2 ** * + 1 gamma 1 - / neg **")
    rho_ratio = density_ratio.eval(gamma=1.4, M=0.8)
    print(f"💨 Density ratio at Mach 0.8: ρ/ρ₀ = {rho_ratio:.4f}")

def smith_chart_calculations():
    """
    Smith Chart companion calculations inspired by David Brunell's RF engineering tool.
    Converts between impedance and reflection coefficients.
    """
    print("\n📡 SMITH CHART RF CALCULATIONS")
    print("=" * 45)
    
    # Reflection coefficient magnitude: |Γ| = |Z - Z0| / |Z + Z0|
    # For normalized impedance z = Z/Z0
    reflection_magnitude = RPN("z_real 1 - 2 ** z_imag 2 ** + sqrt z_real 1 + 2 ** z_imag 2 ** + sqrt /")
    
    # Example: Impedance Z = 75 + j25 Ω, Z0 = 50 Ω
    # Normalized: z = (75 + j25)/50 = 1.5 + j0.5
    gamma_mag = reflection_magnitude.eval(z_real=1.5, z_imag=0.5)
    print(f"📊 Reflection coefficient |Γ|: {gamma_mag:.4f}")
    
    # VSWR calculation: VSWR = (1 + |Γ|) / (1 - |Γ|)
    vswr_calc = RPN("1 gamma + 1 gamma - /")
    vswr = vswr_calc.eval(gamma=gamma_mag)
    print(f"📈 VSWR: {vswr:.2f}:1")
    
    # Return loss: RL = -20 * log10(|Γ|)
    return_loss = RPN("20 gamma log * neg")
    rl = return_loss.eval(gamma=gamma_mag)
    print(f"📉 Return Loss: {rl:.2f} dB")

def process_control_pid():
    """
    PID controller calculations for process control.
    Inspired by real-world industrial applications.
    """
    print("\n🏭 PID CONTROLLER CALCULATIONS")
    print("=" * 45)
    
    # PID output: u(t) = Kp*e(t) + Ki*∫e(t)dt + Kd*de(t)/dt
    # Discrete form: u[n] = Kp*e[n] + Ki*sum(e[i]) + Kd*(e[n]-e[n-1])
    pid_output = RPN("Kp error * Ki error_sum * + Kd error error_prev - * +")
    
    # Example: Temperature control system
    # Kp=2.0, Ki=0.1, Kd=0.5
    # Current error = 5°C, accumulated error = 20°C, previous error = 3°C
    control_output = pid_output.eval(
        Kp=2.0, Ki=0.1, Kd=0.5,
        error=5, error_sum=20, error_prev=3
    )
    print(f"🎛️  PID Control Output: {control_output:.2f}")
    
    # Process response time constant
    # First-order response: y(t) = K * (1 - e^(-t/τ))
    process_response = RPN("K 1 t tau / neg exp - *")
    response_60s = process_response.eval(K=100, t=60, tau=30)
    print(f"📊 Process response at 60s: {response_60s:.1f}%")

if __name__ == "__main__":
    print("🔬 ADVANCED ENGINEERING RPN EXAMPLES")
    print("Inspired by HP Museum forum discussions")
    print("=" * 60)
    
    newton_cooling_law()
    base_conversion()
    random_number_analysis()
    compressible_flow()
    smith_chart_calculations()
    process_control_pid()
    
    print(f"\n🎉 All advanced engineering examples completed!")
    print("🏗️  These examples showcase RPN in real-world engineering applications!")
    print("💡 From thermal engineering to RF design - RPN handles it all!")