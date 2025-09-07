# Integration with Restaurant Delivery Demo

This pydantic-rpn package can be integrated with the restaurant delivery demo to add powerful RPN-based conditional logic to the branching system.

## Enhanced Branching with RPN

Instead of simple field-based branching:

```python
BranchOp(field_to_check="cuisine_choice", branches={
    "pizza": [ElicitOp("Pizza places:", "PizzaRestaurant")],
    "tacos": [ElicitOp("Taco places:", "TacoRestaurant")]
})
```

You can now use complex RPN expressions:

```python
from pydantic_rpn import rpn

# Complex conditional branching
BranchOp(
    rpn_expression="cuisine_choice KEY == user_type premium == AND",
    branches={
        "pizza": [ElicitOp("Premium pizza restaurants:", "PremiumPizzaRestaurant")],
        "tacos": [ElicitOp("Premium taco places:", "PremiumTacoRestaurant")],
        "fallback": [ElicitOp("Standard restaurants:", "StandardRestaurant")]
    }
)

# Distance and user-based logic
BranchOp(
    rpn_expression="delivery_distance 10 <= user_type premium == delivery_distance 5 <= OR AND",
    branches={
        "true": [ElicitOp("We deliver to your area!", "DeliveryFlow")],
        "false": [ElicitOp("Try pickup instead?", "PickupFlow")]
    }
)
```

## Real-World Usage Examples

### Premium User Detection
```python
# Premium users OR high-value orders get special treatment
BranchOp(
    rpn_expression="user_type premium == order_total 75 > OR",
    branches={
        "true": [ElicitOp("Premium service available!", "PremiumFlow")],
        "false": [ElicitOp("Standard service", "StandardFlow")]
    }
)
```

### Time-Based Restaurant Availability
```python
# Different restaurants based on time and cuisine
BranchOp(
    rpn_expression="cuisine_choice pizza == current_hour 22 < AND",
    branches={
        "true": [ElicitOp("Pizza places open:", "PizzaRestaurant")],
        "false": [ElicitOp("24/7 options:", "LateNightRestaurant")]
    }
)
```

### Multi-Criteria Logic
```python
# Budget-conscious customers with dietary restrictions
BranchOp(
    rpn_expression="budget low == dietary_prefs vegetarian == OR",
    branches={
        "true": [ElicitOp("Healthy budget options:", "BudgetHealthy")],
        "false": [ElicitOp("All restaurants:", "AllRestaurants")]
    }
)
```

## Benefits

1. **More Expressive**: Complex conditions that would require nested branching
2. **Maintainable**: Clear logical expressions vs complex nested structures  
3. **Flexible**: Easy to modify conditions without changing code structure
4. **Testable**: RPN expressions can be unit tested independently
5. **Debuggable**: Clear evaluation traces for complex decision logic

## Migration Path

The enhanced branching system maintains backward compatibility:

```python
# Legacy (still works)
BranchOp(field_to_check="cuisine_choice", branches={"pizza": [...]})

# Enhanced (new capability)
BranchOp(rpn_expression="cuisine_choice pizza == user_type premium == AND", 
         branches={"true": [...]})
```

This allows gradual migration from simple field matching to sophisticated RPN-based conditional logic as your forms become more complex.