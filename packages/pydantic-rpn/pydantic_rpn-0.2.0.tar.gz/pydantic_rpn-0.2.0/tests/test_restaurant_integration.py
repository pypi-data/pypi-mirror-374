#!/usr/bin/env python3
"""
Integration Testing with Restaurant Delivery Demo

Tests the integration between our battle-tested pydantic-rpn library
and the existing restaurant delivery elicitation system.
"""

import sys
import os
import json
from pathlib import Path

# Add the restaurant demo to the path
restaurant_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(restaurant_path))

from pydantic_rpn import RPN, RPNBuilder
from rpn_evaluator import RPNEvaluator, rpn_evaluate


class TestRestaurantIntegration:
    """Test integration with restaurant delivery system"""
    
    def test_rpn_evaluator_compatibility(self):
        """Test that restaurant's RPN evaluator works alongside ours"""
        print("\n🍕 Restaurant RPN Evaluator Compatibility:")
        
        # Restaurant's boolean logic evaluator
        restaurant_evaluator = RPNEvaluator()
        
        # Test basic boolean logic
        context = {"cuisine_choice": "pizza", "total": 75, "user_type": "premium"}
        
        # Boolean expression
        result = restaurant_evaluator.evaluate("cuisine_choice pizza ==", context)
        print(f"  cuisine_choice == pizza: {result}")
        assert result == True
        
        # Complex boolean expression
        result = restaurant_evaluator.evaluate("total 50 > user_type premium == AND", context)  
        print(f"  total > 50 AND user_type == premium: {result}")
        assert result == True
        
        # Our mathematical RPN for order calculations
        math_rpn = RPN("item_price quantity * tax_rate 1 + * tip +")
        total_cost = math_rpn.eval(item_price=12.99, quantity=2, tax_rate=0.08, tip=3.00)
        print(f"  Order total (2×$12.99 + 8% tax + $3 tip): ${total_cost:.2f}")
        
        assert abs(total_cost - 31.06) < 0.01  # (12.99 * 2) * 1.08 + 3.00 = 31.0584
    
    def test_delivery_cost_calculator(self):
        """Test RPN for delivery fee calculations"""
        print("\n🚚 Delivery Cost Calculator:")
        
        # Simplified delivery calculation that works with our current operations
        delivery_simple = RPN("base_fee distance_surcharge + time_multiplier *")
        
        # Close delivery (< 2 miles)
        close_cost = delivery_simple.eval(base_fee=2.99, distance_surcharge=0, time_multiplier=1.0)
        print(f"  Close delivery cost: ${close_cost:.2f}")
        assert close_cost == 2.99
        
        # Far delivery (5 miles = 3 miles over base)
        far_cost = delivery_simple.eval(base_fee=2.99, distance_surcharge=1.50, time_multiplier=1.2)  # Peak time
        print(f"  Far delivery cost (peak time): ${far_cost:.2f}")
        assert abs(far_cost - 5.39) < 0.01  # (2.99 + 1.50) * 1.2 = 5.388
    
    def test_order_summary_calculations(self):
        """Test comprehensive order calculations"""
        print("\n🧾 Order Summary Calculations:")
        
        # Multi-item order with different calculations
        items = [
            {"name": "Large Pizza", "price": 18.99, "quantity": 1},
            {"name": "Garlic Bread", "price": 4.99, "quantity": 2}, 
            {"name": "Soda", "price": 1.99, "quantity": 3}
        ]
        
        # Calculate subtotal using RPN
        subtotal_rpn = RPN("pizza_total garlic_total + soda_total +")
        subtotal = subtotal_rpn.eval(
            pizza_total=18.99 * 1,
            garlic_total=4.99 * 2,
            soda_total=1.99 * 3
        )
        
        print(f"  Order subtotal: ${subtotal:.2f}")
        expected_subtotal = 18.99 + (4.99 * 2) + (1.99 * 3)  # 18.99 + 9.98 + 5.97 = 34.94
        assert abs(subtotal - expected_subtotal) < 0.01
        
        # Tax calculation (8.25%)
        tax_rpn = RPN("subtotal tax_rate *")
        tax = tax_rpn.eval(subtotal=subtotal, tax_rate=0.0825)
        print(f"  Tax (8.25%): ${tax:.2f}")
        
        # Tip calculation (18% of subtotal)
        tip_rpn = RPN("subtotal tip_rate *")
        tip = tip_rpn.eval(subtotal=subtotal, tip_rate=0.18)
        print(f"  Tip (18%): ${tip:.2f}")
        
        # Total calculation
        total_rpn = RPN("subtotal tax + tip + delivery_fee +")
        total = total_rpn.eval(subtotal=subtotal, tax=tax, tip=tip, delivery_fee=2.99)
        print(f"  Grand total: ${total:.2f}")
        
        # Verify total is reasonable
        expected_total = subtotal + tax + tip + 2.99
        assert abs(total - expected_total) < 0.01
    
    def test_restaurant_business_logic(self):
        """Test business logic calculations for restaurant operations"""
        print("\n📊 Restaurant Business Logic:")
        
        # Discount eligibility: order > $25 AND (loyalty_member OR first_time)
        # Using restaurant's boolean evaluator for conditions
        order_context = {
            "order_total": 32.50,
            "loyalty_member": True,
            "first_time": False
        }
        
        # Check discount eligibility
        discount_eligible = rpn_evaluate("order_total 25 > loyalty_member first_time OR AND", order_context)
        print(f"  Discount eligible (${order_context['order_total']}, loyal={order_context['loyalty_member']}): {discount_eligible}")
        assert discount_eligible == True
        
        # Calculate discount using our math RPN
        discount_rpn = RPN("total discount_rate *")
        discount = discount_rpn.eval(total=32.50, discount_rate=0.10)  # 10% off
        print(f"  Discount amount (10%): ${discount:.2f}")
        
        final_total = RPN("total discount -").eval(total=32.50, discount=discount)
        print(f"  Final total after discount: ${final_total:.2f}")
        assert abs(final_total - 29.25) < 0.01
    
    def test_delivery_time_estimation(self):
        """Test delivery time estimation using RPN"""
        print("\n⏰ Delivery Time Estimation:")
        
        # Base time + prep time + travel time + buffer
        time_estimate_rpn = RPN("base_prep_minutes distance_miles travel_speed / 60 * + buffer_minutes +")
        
        # Restaurant scenarios
        scenarios = [
            {"name": "Quick Pizza", "base_prep": 15, "distance": 2.5, "speed": 25, "buffer": 5},
            {"name": "Custom Sushi", "base_prep": 25, "distance": 4.0, "speed": 20, "buffer": 10}, 
            {"name": "Rush Hour Tacos", "base_prep": 12, "distance": 3.2, "speed": 15, "buffer": 8}
        ]
        
        for scenario in scenarios:
            estimated_time = time_estimate_rpn.eval(
                base_prep_minutes=scenario["base_prep"],
                distance_miles=scenario["distance"],
                travel_speed=scenario["speed"],
                buffer_minutes=scenario["buffer"]
            )
            print(f"  {scenario['name']}: {estimated_time:.1f} minutes")
            
            # Verify reasonable estimates (15-60 minutes)
            assert 15 <= estimated_time <= 60, f"Unreasonable time estimate: {estimated_time}"
    
    def test_loyalty_points_calculation(self):
        """Test loyalty points system using RPN"""
        print("\n⭐ Loyalty Points System:")
        
        # Points calculation: base points + bonus multipliers
        points_rpn = RPN("order_total 100 * base_multiplier * loyalty_bonus + special_bonus +")
        
        # Different customer tiers
        customers = [
            {"tier": "Bronze", "order": 25.00, "base_mult": 1.0, "loyalty": 0, "special": 0},
            {"tier": "Silver", "order": 45.50, "base_mult": 1.2, "loyalty": 100, "special": 0},
            {"tier": "Gold", "order": 78.25, "base_mult": 1.5, "loyalty": 200, "special": 500}  # Special promotion
        ]
        
        for customer in customers:
            points = points_rpn.eval(
                order_total=customer["order"],
                base_multiplier=customer["base_mult"],
                loyalty_bonus=customer["loyalty"],
                special_bonus=customer["special"]
            )
            print(f"  {customer['tier']} (${customer['order']:.2f}): {points:.0f} points")
            
            # Verify points are positive and reasonable
            assert points >= customer["order"] * 100, "Points should be at least 1 per dollar"
    
    def test_integrated_workflow_calculations(self):
        """Test end-to-end workflow with both RPN systems"""
        print("\n🔄 Integrated Workflow Test:")
        
        # Simulate a complete order flow
        order_data = {
            "cuisine_choice": "pizza", 
            "restaurant": "Tony's Pizza",
            "items": [{"name": "Large Pepperoni", "price": 19.99, "qty": 1}],
            "distance": 3.2,
            "user_type": "gold",
            "order_total": 19.99
        }
        
        # 1. Use restaurant's boolean RPN for business logic
        is_pizza_order = rpn_evaluate("cuisine_choice pizza ==", order_data)
        is_premium_customer = rpn_evaluate("user_type gold ==", order_data)
        is_large_order = rpn_evaluate("order_total 20 >", order_data)
        
        print(f"  Pizza order: {is_pizza_order}")  
        print(f"  Premium customer: {is_premium_customer}")
        print(f"  Large order: {is_large_order}")
        
        # 2. Use our math RPN for calculations  
        # Simplified: if premium customer, no delivery fee
        delivery_fee = 0.0 if is_premium_customer else 2.99
        
        # Calculate final total
        final_calc = RPN("subtotal tax + delivery +")
        final_total = final_calc.eval(
            subtotal=19.99,
            tax=19.99 * 0.08,
            delivery=delivery_fee
        )
        
        print(f"  Delivery fee: ${delivery_fee:.2f}")
        print(f"  Final total: ${final_total:.2f}")
        
        # 3. Verify the integration works correctly
        expected_total = 19.99 + (19.99 * 0.08) + delivery_fee
        assert abs(final_total - expected_total) < 0.01
        
        print(f"  ✅ Integration successful! Both RPN systems working together.")


def main():
    """Run all integration tests"""
    print("🔗 pydantic-rpn ↔ Restaurant Demo Integration Tests")
    print("=" * 60)
    
    integration_test = TestRestaurantIntegration()
    
    try:
        integration_test.test_rpn_evaluator_compatibility()
        integration_test.test_delivery_cost_calculator()
        integration_test.test_order_summary_calculations()
        integration_test.test_restaurant_business_logic()
        integration_test.test_delivery_time_estimation()
        integration_test.test_loyalty_points_calculation()
        integration_test.test_integrated_workflow_calculations()
        
        print(f"\n🎉 All integration tests passed!")
        print("🚀 pydantic-rpn integrates perfectly with the restaurant demo!")
        print("📊 Mathematical RPN + Boolean RPN = Complete solution!")
        
    except ImportError as e:
        print(f"\n⚠️  Integration test skipped - restaurant demo not available:")
        print(f"   {e}")
        print("   Run from the correct directory with restaurant demo installed.")
        return False
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)