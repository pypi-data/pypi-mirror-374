#!/usr/bin/env python3
"""Test script for append_dof functionality."""

import numpy as np
import matplotlib.pyplot as plt
from smpl import plot, functions

# Generate test data
x = np.linspace(0, 5, 20)
y = 2 * x + 1 + np.random.normal(0, 0.5, len(x))  # Linear with noise

print("Testing append_dof functionality...")

# Test 1: Basic fit without DOF
print("Test 1: Basic fit without DOF")
params1 = plot.fit(x, y, functions.line, label="Without DOF", init=True)
plt.title("Without DOF")
plt.show()

# Test 2: Fit with DOF appended
print("Test 2: Fit with DOF appended")
params2 = plot.fit(x, y, functions.line, label="With DOF", append_dof=True, init=True)
plt.title("With DOF")
plt.show()

# Test 3: Fit with Chi2, R2, and DOF all appended
print("Test 3: Fit with Chi2, R2, and DOF all appended")
params3 = plot.fit(x, y, functions.line, label="Complete stats", 
                   append_chi2=True, append_r2=True, append_dof=True, init=True)
plt.title("With Chi2, R2, and DOF")
plt.show()

print("DOF test completed!")
