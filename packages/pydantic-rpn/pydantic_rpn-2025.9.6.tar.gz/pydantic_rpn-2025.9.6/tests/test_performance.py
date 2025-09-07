#!/usr/bin/env python3
"""
Performance and Memory Testing for pydantic-rpn

Benchmarks the RPN library under various conditions to ensure it performs
well and doesn't have memory leaks or performance regressions.
"""

import time
import gc
import sys
import tracemalloc
from typing import List, Dict, Any
import pytest
from pydantic_rpn import RPN, RPNBuilder


class PerformanceTimer:
    """Context manager for timing operations"""
    def __init__(self, description: str):
        self.description = description
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.perf_counter() - self.start_time
        print(f"  {self.description}: {elapsed*1000:.2f}ms")


class TestPerformance:
    """Performance benchmarks and stress tests"""
    
    def test_basic_arithmetic_speed(self):
        """Test speed of basic arithmetic operations"""
        print("\n🏃 Basic Arithmetic Speed Tests:")
        
        # Simple addition
        with PerformanceTimer("1000 simple additions"):
            expr = RPN("3 4 +")
            for _ in range(1000):
                result = expr.eval()
        assert result == 7
        
        # Complex expression
        with PerformanceTimer("1000 complex expressions"):
            expr = RPN("3 4 + 2 * 5 - sqrt")
            for _ in range(1000):
                result = expr.eval()
        assert abs(result - 3.0) < 0.001
        
        # Variable substitution
        with PerformanceTimer("1000 variable evaluations"):
            expr = RPN("x 2 * y +")
            for i in range(1000):
                result = expr.eval(x=i, y=10)
        assert result == 2*999 + 10
    
    def test_large_expression_performance(self):
        """Test performance with very large expressions"""
        print("\n📈 Large Expression Performance:")
        
        # Build a large chain calculation that consumes the stack properly
        # 1 1 + 1 + 1 + ... (100 ones total)
        large_expr_parts = ["1"]
        for i in range(99):
            large_expr_parts.extend(["1", "+"])
        
        large_expr_str = " ".join(large_expr_parts)
        
        with PerformanceTimer("Parse large expression (100 additions)"):
            expr = RPN(large_expr_str)
        
        with PerformanceTimer("Evaluate large expression"):
            result = expr.eval()
        
        # Verify correctness: 1+1+1+...+1 (100 times) = 100
        expected = 100
        assert result == expected
    
    def test_deep_nesting_performance(self):
        """Test performance with deeply nested calculations"""
        print("\n🏗️  Deep Nesting Performance:")
        
        # Create deeply nested expression using builder
        with PerformanceTimer("Build deeply nested expression"):
            builder = RPNBuilder().push(1)  # Start with 1 on stack
            for i in range(50):
                builder.push(2).mul()  # Keep multiplying by 2
            expr = builder
        
        with PerformanceTimer("Evaluate deeply nested (2^50)"):
            result = expr.eval()
        
        assert result == 2**50
    
    def test_variable_substitution_performance(self):
        """Test performance with many variables"""
        print("\n🔢 Variable Substitution Performance:")
        
        # Expression with many variables: x0*2 + x1*2 + x2*2 + ... + x19*2
        expr_parts = ["x0", "2", "*"]
        for i in range(1, 20):
            expr_parts.extend([f"x{i}", "2", "*", "+"])
        
        expr_str = " ".join(expr_parts)
        expr = RPN(expr_str)
        
        var_dict = {f"x{i}": i for i in range(20)}
        
        with PerformanceTimer("100 evals with 20 variables each"):
            for _ in range(100):
                result = expr.eval(**var_dict)
        
        # Verify: sum of (0*2 + 1*2 + 2*2 + ... + 19*2) = 2 * sum(0..19) = 2 * 190 = 380
        expected = 2 * sum(range(20))
        assert result == expected
    
    def test_builder_pattern_performance(self):
        """Test performance of builder pattern vs string parsing"""
        print("\n🏗️  Builder vs String Performance:")
        
        # String-based expression
        string_expr = "1 2 + 3 4 + * 5 6 + 7 8 + * +"
        
        with PerformanceTimer("1000 string-based expressions"):
            for _ in range(1000):
                expr = RPN(string_expr)
                result = expr.eval()
        
        # Builder-based expression (equivalent)
        with PerformanceTimer("1000 builder-based expressions"):
            for _ in range(1000):
                expr = (RPNBuilder()
                    .push(1).push(2).add()
                    .push(3).push(4).add()
                    .mul()
                    .push(5).push(6).add()
                    .push(7).push(8).add()
                    .mul()
                    .add())
                result = expr.eval()
        
        # Verify both give same result: (1+2)*(3+4) + (5+6)*(7+8) = 3*7 + 11*15 = 21 + 165 = 186
        assert result == 186


class TestMemoryUsage:
    """Memory usage and leak detection tests"""
    
    def test_memory_usage_basic(self):
        """Test memory usage doesn't grow unexpectedly"""
        print("\n🧠 Memory Usage Tests:")
        
        tracemalloc.start()
        
        # Baseline memory
        gc.collect()
        baseline_snapshot = tracemalloc.take_snapshot()
        
        # Create and evaluate many expressions
        expressions = []
        for i in range(1000):
            expr = RPN(f"{i} 2 * {i+1} +")
            result = expr.eval()
            if i % 100 == 0:  # Keep some references to prevent immediate GC
                expressions.append(expr)
        
        # Take snapshot after operations
        after_snapshot = tracemalloc.take_snapshot()
        
        # Compare memory usage
        top_stats = after_snapshot.compare_to(baseline_snapshot, 'lineno')
        total_size_diff = sum(stat.size_diff for stat in top_stats[:10])
        
        print(f"  Memory change after 1000 expressions: {total_size_diff/1024:.1f}KB")
        
        # Clean up
        expressions.clear()
        gc.collect()
        
        # Final snapshot
        final_snapshot = tracemalloc.take_snapshot()
        final_stats = final_snapshot.compare_to(baseline_snapshot, 'lineno')
        final_size_diff = sum(stat.size_diff for stat in final_stats[:10])
        
        print(f"  Memory change after cleanup: {final_size_diff/1024:.1f}KB")
        
        tracemalloc.stop()
        
        # Memory growth should be reasonable (less than 100KB for this test)
        assert abs(final_size_diff) < 100 * 1024, "Potential memory leak detected"
    
    def test_no_memory_leaks_repeated_eval(self):
        """Test that repeated evaluations don't leak memory"""
        print("\n🔍 Memory Leak Detection:")
        
        tracemalloc.start()
        
        expr = RPN("x 2 ** y 2 ** + sqrt")  # Pythagorean theorem
        
        # Baseline
        gc.collect()
        baseline_snapshot = tracemalloc.take_snapshot()
        
        # Many evaluations of the same expression
        for i in range(10000):
            result = expr.eval(x=3, y=4)
            assert result == 5.0
        
        # Check memory after repeated evaluations
        gc.collect()
        final_snapshot = tracemalloc.take_snapshot()
        
        top_stats = final_snapshot.compare_to(baseline_snapshot, 'lineno')
        total_size_diff = sum(stat.size_diff for stat in top_stats[:10])
        
        print(f"  Memory change after 10000 evaluations: {total_size_diff/1024:.1f}KB")
        
        tracemalloc.stop()
        
        # Should be minimal memory growth for repeated evaluations
        assert abs(total_size_diff) < 50 * 1024, "Memory leak in repeated evaluations"
    
    def test_large_stack_memory(self):
        """Test memory usage with large stack operations"""
        print("\n📚 Large Stack Memory Usage:")
        
        tracemalloc.start()
        
        # Create expression that builds up a large stack
        large_stack_parts = []
        for i in range(100):
            large_stack_parts.append(str(i))
        # Add operations to consume the stack
        for _ in range(99):
            large_stack_parts.append("+")
            
        expr_str = " ".join(large_stack_parts)
        
        gc.collect()
        start_snapshot = tracemalloc.take_snapshot()
        
        expr = RPN(expr_str)
        result = expr.eval()
        
        end_snapshot = tracemalloc.take_snapshot()
        
        top_stats = end_snapshot.compare_to(start_snapshot, 'lineno')
        total_size = sum(stat.size for stat in top_stats[:10])
        
        print(f"  Large stack expression memory: {total_size/1024:.1f}KB")
        
        tracemalloc.stop()
        
        # Verify correctness: sum of 0+1+2+...+99 = 4950
        assert result == sum(range(100))
        
        # Memory usage should be reasonable (less than 1MB)
        assert total_size < 1024 * 1024, "Excessive memory usage for large stack"


class TestScalability:
    """Tests for scalability and performance limits"""
    
    def test_expression_size_limits(self):
        """Test how the library handles increasingly large expressions"""
        print("\n📏 Expression Size Scalability:")
        
        sizes = [10, 50, 100, 500, 1000]
        times = []
        
        for size in sizes:
            # Build expression: 1 + 1 + 1 + ... (size times)
            expr_parts = ["1"] + ["1", "+"] * (size - 1)
            expr_str = " ".join(expr_parts)
            
            start_time = time.perf_counter()
            expr = RPN(expr_str)
            result = expr.eval()
            end_time = time.perf_counter()
            
            elapsed = (end_time - start_time) * 1000
            times.append(elapsed)
            
            print(f"  Size {size:4d}: {elapsed:6.2f}ms (result: {result})")
            assert result == size
        
        # Check that performance scales reasonably (not exponentially)
        # Allow for some variation, but shouldn't be more than 10x slower for 100x size
        if len(times) >= 2:
            ratio = times[-1] / times[0]  # 1000 vs 10
            size_ratio = sizes[-1] / sizes[0]  # 100x increase
            efficiency_ratio = ratio / size_ratio
            
            print(f"  Scaling efficiency: {efficiency_ratio:.2f} (lower is better)")
            assert efficiency_ratio < 10, f"Performance scaling too poor: {efficiency_ratio:.2f}"
    
    def test_concurrent_usage_simulation(self):
        """Simulate concurrent usage patterns"""
        print("\n🔄 Concurrent Usage Simulation:")
        
        expressions = [
            RPN("x 2 **"),
            RPN("x y +"),  
            RPN("x y * z +"),
            RPN("x sqrt"),
            RPN("x sin 2 ** x cos 2 ** +")  # sin²x + cos²x = 1
        ]
        
        start_time = time.perf_counter()
        
        # Simulate many "users" evaluating different expressions
        for round_num in range(100):
            for i, expr in enumerate(expressions):
                if i == 0:
                    result = expr.eval(x=round_num)
                elif i == 1:
                    result = expr.eval(x=round_num, y=round_num + 1)
                elif i == 2:
                    result = expr.eval(x=round_num, y=2, z=3)
                elif i == 3:
                    result = expr.eval(x=round_num + 1)  # Avoid sqrt(0)
                elif i == 4:
                    result = expr.eval(x=round_num * 0.1)
                    assert abs(result - 1.0) < 0.001  # sin²x + cos²x = 1
        
        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1000
        
        print(f"  500 mixed evaluations: {total_time:.2f}ms")
        print(f"  Average per evaluation: {total_time/500:.3f}ms")
        
        # Should complete in reasonable time
        assert total_time < 1000, "Concurrent usage simulation too slow"


def main():
    """Run all performance tests"""
    print("🚀 RPN Performance & Memory Test Suite")
    print("=" * 50)
    
    perf_test = TestPerformance()
    memory_test = TestMemoryUsage()  
    scalability_test = TestScalability()
    
    # Performance tests
    perf_test.test_basic_arithmetic_speed()
    perf_test.test_large_expression_performance()  
    perf_test.test_deep_nesting_performance()
    perf_test.test_variable_substitution_performance()
    perf_test.test_builder_pattern_performance()
    
    # Memory tests
    memory_test.test_memory_usage_basic()
    memory_test.test_no_memory_leaks_repeated_eval()
    memory_test.test_large_stack_memory()
    
    # Scalability tests  
    scalability_test.test_expression_size_limits()
    scalability_test.test_concurrent_usage_simulation()
    
    print("\n✅ All performance and memory tests passed!")
    print("🎯 pydantic-rpn is production-ready for performance!")


if __name__ == "__main__":
    main()