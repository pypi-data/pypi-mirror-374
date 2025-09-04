# sharkpy/test.py

import pandas as pd
from sharkpy import Shark

# Simple test
data = pd.DataFrame({'x': [1, 2, 3], 'y': [10, 20, 30]})
shark = Shark()
shark.learn(data, target='y', model_choice='linear_regression')
pred = shark.predict({'x': 5})
print(f"Prediction: {pred}")