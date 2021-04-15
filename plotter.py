from datetime import datetime
import matplotlib.pyplot as plt
import numpy


def dist(point1, point2):
    return (((point1[0] - point2[0]) ** 2) +
            ((point1[1] - point2[1]) ** 2) +
            ((point1[2] - point2[2]) ** 2)) ** 0.5

time = []
speed = []
direction = []
acceleration = []
distance = []
old_loc = [0, 0, 0]
all = []
with open("logs/Parsed-Apr-15-2021_01-38-16.txt") as openfileobject:
    for line in openfileobject:
        q = line.split(',')
        if q[1] == '0337':
            all.append(q)
            time.append(float(q[0]))
            speed.append((float(q[5])))
            direction.append(q[6])
            loc = [float(q[2]), float(q[3]), float(q[4])]
            distance.append(dist(old_loc, loc))
            acceleration.append(float(q[7]))
            old_loc = loc


class ZoomPan:
    def __init__(self):
        self.press = None
        self.cur_xlim = None
        self.cur_ylim = None
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.xpress = None
        self.ypress = None

    def zoom_factory(self, ax, base_scale=2.):
        def zoom(event):
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()

            xdata = event.xdata  # get event x location
            ydata = event.ydata  # get event y location

            if event.button == 'down':
                # deal with zoom in
                scale_factor = 1 / base_scale
            elif event.button == 'up':
                # deal with zoom out
                scale_factor = base_scale
            else:
                # deal with something that should never happen
                scale_factor = 1
                # print(event.button)

            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

            relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

            ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * (relx)])
            ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * (rely)])
            ax.figure.canvas.draw()

        fig = ax.get_figure()  # get the figure of interest
        fig.canvas.mpl_connect('scroll_event', zoom)

        return zoom

    def pan_factory(self, ax):
        def onPress(event):
            if event.inaxes != ax: return
            self.cur_xlim = ax.get_xlim()
            self.cur_ylim = ax.get_ylim()
            self.press = self.x0, self.y0, event.xdata, event.ydata
            self.x0, self.y0, self.xpress, self.ypress = self.press

        def onRelease(event):
            self.press = None
            ax.figure.canvas.draw()

        def onMotion(event):
            if self.press is None: return
            if event.inaxes != ax: return
            dx = event.xdata - self.xpress
            dy = event.ydata - self.ypress
            self.cur_xlim -= dx
            self.cur_ylim -= dy
            ax.set_xlim(self.cur_xlim)
            ax.set_ylim(self.cur_ylim)

            ax.figure.canvas.draw()

        fig = ax.get_figure()  # get the figure of interest

        # attach the call back
        fig.canvas.mpl_connect('button_press_event', onPress)
        fig.canvas.mpl_connect('button_release_event', onRelease)
        fig.canvas.mpl_connect('motion_notify_event', onMotion)

        # return the function
        return onMotion

index = 0
for a in all:
    # print(index, a)
    index += 1
fig = plt.figure()

ax = fig.add_subplot(111, autoscale_on=True)

ax.set_title('Click to zoom')
first_t = time[0]
x = [(t - first_t) for t in time]
# x = range(len(time))
y = speed

ax.plot(x, y)
scale = 5
zp = ZoomPan()
figZoom = zp.zoom_factory(ax, base_scale=scale)
figPan = zp.pan_factory(ax)
plt.show()
