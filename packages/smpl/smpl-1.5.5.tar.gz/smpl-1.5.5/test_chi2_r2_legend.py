#!/usr/bin/env python3
"""Test script for append_chi2 and append_r2 functionality."""

import numpy as np
import matplotlib.pyplot as plt
from smpl import plot, functions

# Generate some test data
np.random.seed(42)
x = np.linspace(0, 10, 50)
y_true = 2 * x + 3  # linear function: y = 2x + 3
y = y_true + np.random.normal(0, 1, len(x))  # add some noise

# Test 1: Basic fit without chi2/r2
print("Test 1: Basic fit without chi2/r2")
plt.figure(figsize=(12, 4))

# Test 2: Fit with chi2 appended
print("Test 2: Fit with chi2 appended")
params2 = plot.fit(x, y, functions.line, label="With Chi2", append_chi2=True, init=True,fselector=lambda x,y : (x<2))
plt.title("With Chi2")
plt.legend()


plt.tight_layout()
plt.savefig("test_chi2_r2_legend.png", dpi=150, bbox_inches='tight')
plt.show()

print("Test completed successfully!")
