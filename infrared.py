import time,board,busio
import numpy as np
import adafruit_mlx90640
import matplotlib.pyplot as plt
from scipy import ndimage
import argparse

parser = argparse.ArgumentParser(description='Thermal Camera Program')
parser.add_argument('--mirror', dest='imageMirror', action='store_const', default='false',
                    const='imageMirror', help='Flip the image for selfie (default: false)')
args = parser.parse_args()
imageMirror = args.imageMirror

if(imageMirror == 'false'):
    print('Mirror mode: false')
else:
    imageMirror = 'true'
    print('Mirror mode: true')

i2c = busio.I2C(board.SCL, board.SDA, frequency=400000) 
mlx = adafruit_mlx90640.MLX90640(i2c) 
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_16_HZ 
mlx_shape = (24,32) 

mlx_interp_val = 10 
mlx_interp_shape = (mlx_shape[0]*mlx_interp_val,
                    mlx_shape[1]*mlx_interp_val) 

fig = plt.figure(figsize=(12,9)) 
ax = fig.add_subplot(111) 
fig.subplots_adjust(0.05,0.05,0.95,0.95) 
therm1 = ax.imshow(np.zeros(mlx_interp_shape),interpolation='none',
                   cmap=plt.cm.bwr,vmin=25,vmax=45) 
cbar = fig.colorbar(therm1) # setup colorbar
cbar.set_label('Temperature [$^{\circ}$C]',fontsize=16) 

fig.canvas.draw() 
ax_background = fig.canvas.copy_from_bbox(ax.bbox) 
ax.text(-75, 125, 'Max:', color='yellow')
textMaxValue = ax.text(-75, 150, 'test1', color='black')
fig.show() 

frame = np.zeros(mlx_shape[0]*mlx_shape[1])
def plot_update():
    fig.canvas.restore_region(ax_background)
    mlx.getFrame(frame)
    data_array = np.fliplr(np.reshape(frame,mlx_shape))
    if(imageMirror == 'true'):
        data_array = np.flipud(data_array)
    data_array = ndimage.zoom(data_array,mlx_interp_val)
    therm1.set_array(data_array) # set data
    therm1.set_clim(vmin=np.min(data_array),vmax=np.max(data_array))
    cbar.on_mappable_changed(therm1)
    plt.pause(0.001)
    ax.draw_artist(therm1)
    textMaxValue.set_text(str(np.round(np.max(data_array), 1)))
    fig.canvas.blit(ax.bbox)
    fig.canvas.flush_events()
    fig.show()
    return

t_array = []
while True:
    t1 = time.monotonic()
    try:
        plot_update()
    except:
        continue
    
    t_array.append(time.monotonic()-t1)
    if len(t_array)>10:
        t_array = t_array[1:]
    print('Frame Rate: {0:2.1f}fps'.format(len(t_array)/np.sum(t_array)))