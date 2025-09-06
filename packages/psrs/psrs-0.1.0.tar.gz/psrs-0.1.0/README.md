# PSRS — Procrustes Similarity with Reconstructed Space

This is a PyTorch-based toolkit for PSRS method for quantifying relative information content 
between two embedding spaces. It works by reconstructing one space from the other with a flexible neural network and then measuring their alignment under Procrustes analysis (rotation, scaling, translation).
PSRS can be understood as a generalized form of Procrustes analysis: instead of comparing spaces directly, PSRS first learns a non-linear mapping before alignment, allowing it to capture more complex relationships between representations.

## Installation

```bash
pip install psrs
```

## Usage
Here is how to use the package.

```python
import numpy as np
from psrs import PSRS

# toy spaces
n_samples, n_dimensions = 100, 16
space_a = np.random.randn(n_samples, n_dimensions)
space_b = np.random.randn(n_samples, n_dimensions)

model = PSRS(space_a=space_a, space_b=space_b)
model.reconstruct(epochs=10)  

# similarity after Procrustes alignment (0 to 1)
score = model.calculate_procrustes_similarity()
print(f"PSRS similarity: {score:.3f}")
```

All configurations at your disposal
```python
psrs = PSRS(space_a, space_b, random_state=0, verbose=True)

# You can leave everything at defaults:
model.reconstruct(
    epochs=10,                  # training steps
    learning_rate=5e-3,         # Adam lr
    hidden_dims_list=None,      # None → sensible defaults based on dims of A and B
    test_size=0.3,              # 70/30 split (scaled to [0,1])
    loss_fn="mse",              # "procrustes" or "mse" (see note below)
    checkpoint_interval=5,      # logging cadence when verbose=True
    batch_size=50,              # mini-batch size
    activation_function="ReLU"  # 'ReLU' or 'GELU'
)

print("Test PSRS:", model.calculate_procrustes_similarity())
```
**Note on loss choice**: `loss_fn="procrustes"` is usually fast and works well, but in rare cases it can be less stable for backprop. If training diverges, switch to `loss_fn="mse"` 

## API at a Glance

### `PSRS(space_a, space_b, random_state=None, verbose=False)`

- **`space_a`, `space_b`**: `np.ndarray` or `torch.Tensor` with the same number of rows (paired observations).  
- **`random_state`**: integer seed for reproducibility.  
- **`verbose`**: if `True`, logs training progress during reconstruction.  

Internally, inputs are **min–max scaled per feature**, and data is split into **train/test** sets.

---

### `PSRS.reconstruct(...)`

Fit a DeepShallow model to reconstruct space **B** from space **A**.  

Arguments (all optional, with robust defaults):

- **`epochs`** *(int, default=100)* — training iterations.  
- **`learning_rate`** *(float, default=0.005)* — Adam step size.  
- **`hidden_dims_list`** *(list[int] or None, default=None)* — hidden layer widths. If `None`, picks a dimension-aware stack automatically.  
- **`random_state`** *(int or None, default=None)* — seed for reproducibility.  
- **`test_size`** *(float, default=0.3)* — fraction of data held out for testing, the similarity is calculated on test data.  
- **`loss_fn`** *{"procrustes", "mse"}, default="procrustes"* — the choice of loss function. `procrustes` converges much faster, but it sometimes is unstable.
- **`checkpoint_interval`** *(int, default=50)* — logging interval when `verbose=True`.  
- **`loss_reduction_method`** *{"mean", "sum"}, default="mean"* — reduction method for the loss.  
- **`activation_function`** *{"ReLU", "GELU"}, default="ReLU"* — non-linear activation in the deep network.  
- **`batch_size`** *(int, default=128)* — mini-batch size. If length of the training data is smaller than the `batch_size`, the size is adjusted to the length of the training data.    
- **`optimizer`** *(torch.optim.Optimizer or None, default=None)* — custom optimizer. If `None`, uses Adam with `learning_rate`.  

---

### `PSRS.calculate_procrustes_similarity() -> float`

Returns the **test-set Procrustes similarity** between predicted and true representations:  

- Values closer to **1.0** indicate higher structural similarity after optimal rotation, scaling, and translation.  


## License
See the [LICENSE](LICENSE) file for details.


