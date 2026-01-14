import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

filenames = [
    "../db1_data/calibration_data/calibration_data_1.csv",
    "../db1_data/calibration_data/calibration_data_2.csv",
    "../db1_data/calibration_data/calibration_data_3.csv",
    "../db1_data/calibration_data/calibration_data_4.csv",
    "../db1_data/calibration_data/calibration_data_5.csv",
    "../db1_data/calibration_data/calibration_data_6.csv",
    "../db1_data/calibration_data/calibration_data_7.csv",
    "../db1_data/calibration_data/calibration_data_8.csv",
]

od_vals = [0, 0.09, 0.13, 0.36, 0.55, 0.72, 1.07, 1.44]

data = {}

for i in range(len(od_vals)):
    idx = od_vals[i]
    data[idx] = pd.read_csv(
        filenames[i],
        header=None,
        names=["voltage", "time"]
    )

rows = []

for i in range(8):
    avg = data[od_vals[i]]["voltage"].mean()
    rows.append({"od_val": od_vals[i], "average": avg})

averages = pd.DataFrame(rows)
print(averages)

averages.to_csv("averages.csv", index=False)


# make a graph!

# y = B * e ** (A * x)
# ln(y) = Ax + lnB

# convert to numpy arrays
od_vals = averages["od_val"].to_numpy()
voltages = averages["average"].to_numpy()

# then we calculate the y values
mask = voltages > 0
od_vals_lin = od_vals[mask]
voltages_lin = np.log(voltages[mask])

# then we do a linspace(), where m, b = linspace(x, y, degree)
A, lnB = np.polyfit(od_vals_lin, voltages_lin, 1)
B = np.exp(lnB)

# make new np arrays for x and y values
od_vals_exp_line = np.linspace(od_vals.min(), od_vals.max(), 100)
voltages_exp_line = B * np.exp(A * od_vals_exp_line)

# # now we plot
# plt.figure()
# plt.scatter(voltages, od_vals, label="Data")
# plt.plot(voltages_exp_line, od_vals_exp_line, label="Expirimental vals", color="red")
# plt.plot(voltages_exp_line,
#          od_vals_exp_line,
#          label="Predicted vals",
#          linestyle="--",
#          color="blue"
#         )
# plt.ylabel("OD_Val")
# plt.xlabel("Voltage")
# plt.title("Voltage vs OD Value")
# plt.legend()
# plt.grid(True)
# plt.show()

V_0 = voltages[0]

def v_to_OD(voltage):
    return -1 * np.log10(voltage / V_0)

voltages_calculated = voltages
od_vals_calculated = v_to_OD(voltages_calculated)

# make linear mapping from calculated to expirimental od vals

m, b = np.polyfit(od_vals, od_vals_calculated, 1)
fit_line_x = np.linspace(od_vals.min(), od_vals.max(), 100)
fit_line_y = m * fit_line_x + b

fitline_x_2 = np.linspace(0, 100, 100)
fitline_y_2 = fitline_x_2

# now we plot v2
plt.figure()
plt.scatter(od_vals, od_vals_calculated, label="Data")
plt.plot(fit_line_x, fit_line_y, label=f"y = {m:.3f} * x + {b:.3f}", color="black")
plt.plot(fitline_x_2, fitline_y_2, color="red")
plt.xlabel("OD Value (Expirimental)")
plt.ylabel("OD Value (Calculated)")
plt.title("OD vs OD")
plt.xlim(0, 1.5)
plt.ylim(0, 1.5)
plt.legend()
plt.grid(True)
plt.show()



