import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score

adc_blank = 2879.0
od_init = 0.11
dil_fact = 10000
vol_on_plt = 0.1 # mL
cell_cult_vol = 3 # mL

filename = "data/ex_pt_1.csv"
data = pd.read_csv(filename, header=0, usecols=[0, 1])
data.rename(columns={
    "Time (s)": "time",
    "ADC (t)": "adc"
},
inplace=True)

print(data.head())
print(data.columns)

def adc_to_od(voltage, v_0):
    return -1 * np.log10(voltage/v_0)

data["od_val"] = adc_to_od(data["adc"], adc_blank)

print(data.head())

x = data["time"].to_numpy()
y = np.log(data["od_val"].to_numpy())
mask = (x > 25000) & (x < 40000)
x = x[mask]
y = y[mask]

window_size = 1000

m, b = np.polyfit(x, y, 1)
x_fit = np.linspace(x.min(), x.max(), 100)
y_fit = m * x_fit + b

r2 = r2_score(y_true, y_pred)

plt.figure()
plt.scatter(x, y, label="Data")
plt.plot(x_fit, y_fit, label="Data")
plt.xlabel("Time (s)")
plt.ylabel("OD Value")
plt.title("OD Value Over Time")
plt.show()