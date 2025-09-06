# Causara: AI-powered Optimization

**Support:** [support@causara.com](mailto:support@causara.com)

**Website:** https://www.causara.com

Causara is a Python package for optimizing **ANY** function using mathematical solvers. We specialize in highly complex problems that involve simulations or other non-standard objectives. Additionally, for existing Pyomo models, we can leverage our technology to significantly accelerate the optimization process and to fine-tune the models on real-world data.
We use artificial intelligence and machine learning to create high-precision surrogate models. These models are significantly easier and faster to optimize than the original, complex systems, without sacrificing accuracy. The result: faster, better, and more robust solutions.

### Installation

Install Causara via pip:

```bash
pip install causara
```


### Creating a free licence key

```bash
import causara
causara.create_key("your_email@example.com")
```


### Quickstart

Simple proof of concept demo:

```python
from causara import *
import numpy as np


def simple_demo(p, c, x):
    coef = p["coef"]
    var = x["var"]
    assert var[0] < var[1] and np.sum(var) == 10
    return coef * var[0] + var[0] * var[1]


def get_decision_vars(p, c):
    decision_vars = DecisionVars()
    # Here we create two integer variables with name "var" and bounds [-10,+10]
    decision_vars.add_integer_vars("var", 2, minimum=-10, maximum=+10)
    return decision_vars


model = Model(key="your_key", model_name="demo", solver="scip")          # insert your key here and provide a model name
model.compile(decision_vars_func=get_decision_vars,                      # the decision_vars_func
              obj_func=simple_demo,                                      # the objective function
              P_val=[{"coef": 1.0}],                                     # a list of problems p for validating the correctness
              sense=MINIMIZE)                                            # the sense (either causara.MINIMIZE or causara.MAXIMIZE)

# After compiling we can solve a new problem instance p={"coef": 1.5}
data = model.optimize(p={"coef": 1.5})                                   # Return value of the optimize(.) method is an object of type Data
print(f"Optimal x: {data.list_of_x[0]}")
print(f"Optimal value: {data.pyomo_values[0]}")

```

### LICENSE

This project is licensed under the terms provided in LICENSE.txt

