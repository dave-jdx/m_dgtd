import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as Axes3D
from numpy import sin,cos,pi, exp,log
from tqdm import tqdm
# import mpl_toolkits.mplot3d.axes3d as Axes3D
from matplotlib import cm, colors

filepath = 'D:\\project\\cae\\emx\\src\\data\\data.txt'

vals_theta = []
vals_phi = []
vals_r = []
with open(filepath) as f:
  for s in f.readlines()[2:]:
    print(s.strip().split())
    vals_theta.append(float(s.strip().split()[0]))
    vals_phi.append(float(s.strip().split()[1]))
    vals_r.append(float(s.strip().split()[6]))


theta1d = vals_theta
theta = np.array(theta1d)/180*pi;

phi1d = vals_phi
phi = np.array(phi1d)/180*pi;

power1d = vals_r
power = np.array(power1d);
# power = power-min(power)
power = 10**(power/10) # I used linscale

X = power*sin(phi)*sin(theta)
Y = power*cos(phi)*sin(theta)
Z = power*cos(theta)

X = X.reshape([91,91])
Y = Y.reshape([91,91])
Z = Z.reshape([91,91])

def interp_array(N1):  # add interpolated rows and columns to array
    N2 = np.empty([int(N1.shape[0]), int(2*N1.shape[1] - 1)])  # insert interpolated columns
    N2[:, 0] = N1[:, 0]  # original column
    for k in range(N1.shape[1] - 1):  # loop through columns
        N2[:, 2*k+1] = np.mean(N1[:, [k, k + 1]], axis=1)  # interpolated column
        N2[:, 2*k+2] = N1[:, k+1]  # original column
    N3 = np.empty([int(2*N2.shape[0]-1), int(N2.shape[1])])  # insert interpolated columns
    N3[0] = N2[0]  # original row
    for k in range(N2.shape[0] - 1):  # loop through rows
        N3[2*k+1] = np.mean(N2[[k, k + 1]], axis=0)  # interpolated row
        N3[2*k+2] = N2[k+1]  # original row
    return N3

interp_factor=1

for counter in range(interp_factor):  # Interpolate between points to increase number of faces
    X = interp_array(X)
    Y = interp_array(Y)
    Z = interp_array(Z)

N = np.sqrt(X**2 + Y**2 + Z**2)
Rmax = np.max(N)
N = N/Rmax

fig = plt.figure(figsize=(10,8))

ax = fig.add_subplot(1,1,1, projection='3d')
axes_length = 0.65
ax.plot([0, axes_length*Rmax], [0, 0], [0, 0], linewidth=2, color='red')
ax.plot([0, 0], [0, axes_length*Rmax], [0, 0], linewidth=2, color='green')
ax.plot([0, 0], [0, 0], [0, axes_length*Rmax], linewidth=2, color='blue')

# Find middle points between values for face colours
N = interp_array(N)[1::2,1::2]

mycol = cm.jet(N)

surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, facecolors=mycol, linewidth=0.5, antialiased=True, shade=False)  # , alpha=0.5, zorder = 0.5)

ax.set_xlim([-axes_length*Rmax, axes_length*Rmax])
ax.set_ylim([-axes_length*Rmax, axes_length*Rmax])
ax.set_zlim([-axes_length*Rmax, axes_length*Rmax])

m = cm.ScalarMappable(cmap=cm.jet)
m.set_array(power)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

fig.colorbar(m, shrink=0.8)
ax.view_init(azim=300, elev=30)

plt.show()
print("1")