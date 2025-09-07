# ForgeNN Dynamic Activation Functions

## Overview

Instead of hardcoding activation functions directly in the `Value` class, ForgeNN now uses a dynamic activation system that allows you to easily add and use activation functions from your `functions.activation` library.

## How It Works

### 1. Core Method: `apply_activation()`

The `Value` class now has a generic `apply_activation()` method that can work with any activation function class:

```python
def apply_activation(self, activation_class, *args, **kwargs):
    """Apply an activation function from the functions library"""
    # Forward pass using the activation class
    activated_data = activation_class.forward(self.data, *args, **kwargs)
    out = Value(activated_data, (self,), f'{activation_class.__name__}')
    
    def _backward():
        # Backward pass using the activation class
        grad_input = activation_class.backward(self.data, *args, **kwargs)
        self.grad += grad_input * out.grad
    out._backward = _backward
    
    return out
```

### 2. Convenience Methods

For commonly used activations, convenience methods are provided:

```python
# Instead of hardcoding:
def relu(self):
    out = Value(0 if self.data < 0 else self.data, (self,), 'ReLU')
    def _backward():
        self.grad += (out.data > 0) * out.grad
    out._backward = _backward
    return out

# Now you can use:
def relu(self):
    return self.apply_activation(RELU)
```

## Available Activation Functions

### Current Library (`functions/activation.py`):

1. **RELU** - Rectified Linear Unit
   - `forward(x)`: Returns `x if x > 0 else 0`
   - `backward(x)`: Returns `1.0 if x > 0 else 0.0`

2. **LRELU** - Leaky ReLU
   - `forward(x, alpha=0.01)`: Returns `x if x > 0 else alpha * x`
   - `backward(x, alpha=0.01)`: Returns `1.0 if x > 0 else alpha`

3. **TANH** - Hyperbolic Tangent
   - `forward(x)`: Returns `math.tanh(x)`
   - `backward(x)`: Returns `1 - tanh(x)²`

4. **SIGMOID** - Sigmoid Function
   - `forward(x)`: Returns `1 / (1 + exp(-x))`
   - `backward(x)`: Returns `sigmoid(x) * (1 - sigmoid(x))`

5. **SWISH** - Swish Activation
   - `forward(x)`: Returns `x * sigmoid(x)`
   - `backward(x)`: Returns `sigmoid(x) + x * sigmoid(x) * (1 - sigmoid(x))`

## Usage Examples

### Basic Usage
```python
from forgeNN.core import Value

x = Value(1.5)

# Using convenience methods
y1 = x.relu()
y2 = x.sigmoid()
y3 = x.tanh()
y4 = x.lrelu(alpha=0.1)  # with parameters

# Using the generic method directly
from forgeNN.functions.activation import SWISH
y5 = x.apply_activation(SWISH)
```

### Chaining Activations
```python
x = Value(0.5)
h1 = x.tanh()
h2 = h1 * Value(2.0)
h3 = h2.sigmoid()
h3.backward()  # Computes gradients through the entire chain
```

## Adding New Activation Functions

To add a new activation function, simply create a new class in `functions/activation.py`:

```python
class YOUR_ACTIVATION:
    @staticmethod
    def forward(x, param1=default_val, param2=default_val):
        # Implement forward pass
        return result
    
    @staticmethod
    def backward(x, param1=default_val, param2=default_val):
        # Implement gradient computation
        return gradient
```

Then add it to the imports in `core.py` and optionally create a convenience method:

```python
# In core.py imports
from functions.activation import RELU, LRELU, TANH, SIGMOID, SWISH, YOUR_ACTIVATION

# Add convenience method to Value class
def your_activation(self, param1=default_val, param2=default_val):
    return self.apply_activation(YOUR_ACTIVATION, param1=param1, param2=param2)
```

## Benefits

1. **Modularity**: Activation functions are separated from the core Value class
2. **Extensibility**: Easy to add new activation functions without modifying core logic
3. **Consistency**: All activations follow the same pattern
4. **Reusability**: Activation classes can be used in other parts of your neural network library
5. **Maintainability**: Each activation function is self-contained with its forward and backward passes

## Migration from Hardcoded Methods

**Before:**
```python
def relu(self):
    out = Value(0 if self.data < 0 else self.data, (self,), 'ReLU')
    def _backward():
        self.grad += (out.data > 0) * out.grad
    out._backward = _backward
    return out
```

**After:**
```python
def relu(self):
    return self.apply_activation(RELU)
```

The new system provides the same functionality with much cleaner, more maintainable code!
