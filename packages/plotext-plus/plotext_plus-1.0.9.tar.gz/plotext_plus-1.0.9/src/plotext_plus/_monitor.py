from plotext_plus._default import default_monitor_class
from plotext_plus._matrix import matrix_class
from plotext_plus._build import build_class
import plotext_plus._utility as ut
from copy import deepcopy
import math

# This file defines the monitor class, i.e. the plot, where actual data is plotted; the plot is build separately in the build class for clarity; here only the main tools and drawing methods are written

class monitor_class(build_class):
    
    def __init__(self):
        self.default = default_monitor_class() # default values
        self.labels_init()
        self.axes_init()
        self.color_init()
        self.data_init()
        self.matrix = matrix_class()

    def copy(self): # to deep copy 
        return deepcopy(self)

    def set_size(self, size): # called externally by the figure containing it, to pass the size
        self.size = size

    def set_date(self, date): # called externally by the figure containing it, to pass the date tools so that they share the same settings
        self.date = date

##############################################
#########    Internal Variables    ###########
##############################################

    def labels_init(self):
        self.title = None
        self.xlabel = [None, None]
        self.ylabel = [None, None]

    def axes_init(self):
        self.xscale = [self.default.xscale[0]] * 2 # the scale on x axis
        self.yscale = [self.default.xscale[0]] * 2

        self.xticks = self.default.xticks # xticks coordinates for both axes
        self.xlabels = self.default.xticks[:] # xlabels for both axes
        self.xfrequency = self.default.xfrequency # lower and upper xaxes ticks frequency
        self.xdirection = self.default.xdirection
        
        self.yticks = self.default.yticks
        self.ylabels = self.default.yticks[:]
        self.yfrequency = self.default.yfrequency # left and right yaxes ticks frequency
        self.ydirection = self.default.ydirection

        self.xaxes = self.default.xaxes # whatever to show the lower and upper x axis
        self.yaxes = self.default.yaxes # whatever to show the left and right y axis

        self.grid = self.default.grid # whatever to show the horizontal and vertical grid lines

    def color_init(self):
        self.set_theme('default')

    def data_init(self):
        self.xlim = [[None, None], [None, None]] # the x axis plot limits for lower and upper xside
        self.ylim = [[None, None], [None, None]] # the y axis plot limits for left and right yside

        self.fast_plot = False
        self.lines_init()
        self.text_init()
        self.draw_init()

    def lines_init(self):
        self.vcoord = [[], []] # those are user defined extra grid lines, vertical or horizontal, for each axis
        self.hcoord = [[], []]
        self.vcolors = [[], []] # their color
        self.hcolors = [[], []]

    def text_init(self):
        self.text = []
        self.tx = []
        self.ty = []
        self.txside = []
        self.tyside = []
        self.torien = []
        self.talign = []
        self.tfull = []
        self.tback = []
        self.tstyle = []

    def draw_init(self):  # Variables Set with Draw internal Arguments
        self.xside = [] # which side the x axis should go, for each plot (lower or upper)
        self.yside = [] # which side the y axis should go, for each plot (left or right)
        
        self.x = [] # list of x coordinates 
        self.y = [] # list of y coordinates
        self.x_date = [False, False] # True if x axis is for date time plots
        self.y_date = [False, False]
        self.signals = 0 # number of signals to plot

        self.lines = [] # whatever to draw lines between points

        self.marker = [] # list of markers used for each plot
        self.color = [] # list of marker colors used for each plot
        self.past_colors = []
        self.style = []

        self.fillx = [] # fill data vertically (till x axis)
        self.filly = [] # fill data horizontally (till y axis)

        self.label = [] # subplot list of labels

##############################################
#######    External Set Functions    #########
##############################################

    def set_title(self, title = None):
        self.title = self.set_label(title)

    def set_xlabel(self, label = None, xside = None):
        pos = self.xside_to_pos(xside)
        self.xlabel[pos] = self.set_label(label)
        
    def set_ylabel(self, label = None, yside = None):
        pos = self.yside_to_pos(yside)
        self.ylabel[pos] = self.set_label(label)
        
    def set_xlim(self, left = None, right = None, xside = None):
        left = self.date.string_to_time(left) if isinstance(left, str) else left
        right = self.date.string_to_time(right) if isinstance(right, str) else right
        left = None if left is None else float(left)
        right = None if right is None else float(right)
        xlim = [left, right]
        xlim = xlim if None in xlim else [min(xlim), max(xlim)]
        pos = self.xside_to_pos(xside)
        self.xlim[pos] = xlim

    def set_ylim(self, lower = None, upper = None, yside = None):
        lower = self.date.string_to_time(lower) if isinstance(lower, str) else lower
        upper = self.date.string_to_time(upper) if isinstance(upper, str) else upper
        lower = None if lower is None else float(lower)
        upper = None if upper is None else float(upper)
        ylim = [lower, upper]
        ylim = ylim if None in ylim else [min(ylim), max(ylim)]
        pos = self.yside_to_pos(yside)
        self.ylim[pos] = ylim

    def set_xscale(self, scale = None, xside = None):
        default_case = (scale is None or scale not in self.default.xscale)
        scale = self.default.xscale[0] if default_case else scale
        pos = self.xside_to_pos(xside)
        self.xscale[pos] = scale

    def set_yscale(self, scale = None, yside = None):
        default_case = (scale is None or scale not in self.default.yscale)
        scale = self.default.yscale[0] if default_case else scale
        pos = self.yside_to_pos(yside)
        self.yscale[pos] = scale

    def set_xticks(self, ticks = None, labels = None, xside = None):
        pos = self.xside_to_pos(xside)
        ticks = self.default.xticks[pos] if ticks is None else list(ticks)
        string_ticks = any([isinstance(el, str) for el in ticks])
        labels = ticks if string_ticks and labels is None else labels
        ticks = self.date.strings_to_time(ticks) if string_ticks else ticks
        labels = ut.get_labels(ticks) if labels is None else list(labels)
        labels = list(map(str, labels))
        ticks, labels = ut.brush(ticks, labels)
        self.xticks[pos] = ticks
        self.xlabels[pos] = labels
        self.xfrequency[pos] = self.xfrequency[pos] if ticks is None else len(ticks)

    def set_yticks(self, ticks = None, labels = None, yside = None):
        pos = self.yside_to_pos(yside)
        ticks = self.default.yticks[pos] if ticks is None else list(ticks)
        string_ticks = any([isinstance(el, str) for el in ticks])
        labels = ticks if string_ticks and labels is None else labels
        ticks = self.date.strings_to_time(ticks) if string_ticks else ticks
        labels = ut.get_labels(ticks) if labels is None else list(labels)
        labels = list(map(str, labels))
        ticks, labels = ut.brush(ticks, labels)
        self.yticks[pos] = ticks
        self.ylabels[pos] = labels
        self.yfrequency[pos] = self.yfrequency[pos] if ticks is None else len(ticks)

    def set_xfrequency(self, frequency = None, xside = None):
        pos = self.xside_to_pos(xside)
        frequency = self.default.xfrequency[pos] if frequency is None else int(frequency)
        self.xfrequency[pos] = frequency
        
    def set_yfrequency(self, frequency = None, yside = None):
        pos = self.yside_to_pos(yside)
        frequency = self.default.yfrequency[pos] if frequency is None else int(frequency)
        self.yfrequency[pos] = frequency

    def set_xreverse(self, reverse = None, xside = None):
        pos = self.xside_to_pos(xside)
        direction = self.default.xdirection[pos] if reverse is None else 2 * int(not reverse) - 1
        self.xdirection[pos] = direction

    def set_yreverse(self, reverse = None, yside = None):
        pos = self.yside_to_pos(yside)
        direction = self.default.ydirection[pos] if reverse is None else 2 * int(not reverse) - 1
        self.ydirection[pos] = direction
        
    def set_xaxes(self, lower = None, upper = None):
        self.xaxes[0] = self.default.xaxes[0] if lower is None else bool(lower)
        self.xaxes[1] = self.default.xaxes[1] if upper is None else bool(upper)
        
    def set_yaxes(self, left = None, right = None):
        self.yaxes[0] = self.default.yaxes[0] if left is None else bool(left)
        self.yaxes[1] = self.default.yaxes[1] if right is None else bool(right)

    def set_frame(self, frame = None):
        self.set_xaxes(frame, frame)
        self.set_yaxes(frame, frame)

    def set_grid(self, horizontal = None, vertical = None):
        horizontal = self.default.grid[0] if horizontal is None else bool(horizontal)
        vertical = self.default.grid[1] if vertical is None else bool(vertical)
        self.grid = [horizontal, vertical]

    def set_color(self, color = None):
        color = color if ut.is_color(color) else None
        return self.default.canvas_color if color is None else color

    def set_canvas_color(self, color = None):
        self.canvas_color = self.set_color(color)
        
    def set_axes_color(self, color = None):
        self.axes_color = self.set_color(color)
        
    def set_ticks_color(self, color = None):
        self.ticks_color = self.set_color(color)

    def set_ticks_style(self, style = None):
        style = style if ut.is_style(style) else None
        style = self.default.ticks_style if style is None else ut.clean_styles(style)
        self.ticks_style = style

    def set_theme(self, theme = None):
        theme = 'default' if theme is None or theme not in ut.themes else theme
        self._set_theme(*ut.themes[theme])

    def clear_color(self):
        self.set_theme('clear')

##############################################
#######    Set Functions Utilities    ########
##############################################

    def set_label(self, label = None): 
        label = None if label is None else str(label).strip()
        spaces = ut.only_spaces(label)
        label = None if spaces else label 
        return label

    def correct_xside(self, xside = None): # from axis side to position
        xaxis = self.default.xside
        xside = xaxis[xside - 1] if isinstance(xside, int) and 1 <= xside <= 2 else xaxis[0] if xside is None or xside.strip() not in xaxis else xside.strip()
        return xside

    def correct_yside(self, yside = None):
        yaxis = self.default.yside
        yside = yaxis[yside - 1] if isinstance(yside, int) and 1 <= yside <= 2 else yaxis[0] if yside is None or yside.strip() not in yaxis else yside.strip()
        return yside

    def xside_to_pos(self, xside = None): # from axis side to position
        xside = self.correct_xside(xside)
        pos = self.default.xside.index(xside)
        return pos

    def yside_to_pos(self, yside = None):
        yside = self.correct_yside(yside)
        pos = self.default.yside.index(yside)
        return pos

    def _set_theme(self, canvas_color, axes_color, ticks_color, ticks_style, color_sequence):
        self.canvas_color = canvas_color
        self.axes_color = axes_color
        self.ticks_color = ticks_color
        self.ticks_style = ticks_style
        self.color_sequence = color_sequence
        
##############################################
##########    Draw() Function    #############
##############################################

    def draw(self, *args, **kwargs): # from draw() comes directly the functions scatter() and plot()
        self.add_xside(kwargs.get("xside"))
        self.add_yside(kwargs.get("yside"))
        self.add_data(*args)
        self.add_lines(kwargs.get("lines"))
        self.add_markers(kwargs.get("marker"))
        self.add_colors(kwargs.get("color"))
        self.add_styles(kwargs.get("style"))
        self.add_fillx(kwargs.get("fillx"))
        self.add_filly(kwargs.get("filly"))
        self.add_label(kwargs.get("label"))
        
##############################################
#######    Draw() Called Functions    ########
##############################################

    def add_xside(self, xside = None):
        xside = self.correct_xside(xside)
        self.xside.append(xside)

    def add_yside(self, yside = None):
        yside = self.correct_yside(yside)
        self.yside.append(yside)

    def add_data(self, *args):
        x, y = ut.set_data(*args)
        x, x_date = self.to_time(x)
        y, y_date = self.to_time(y)
        self.x_date[self.xside_to_pos(self.xside[-1])] = x_date
        self.y_date[self.yside_to_pos(self.yside[-1])] = y_date
        self.x.append(x)
        self.y.append(y)
        self.signals += 1

    def add_lines(self, lines):
        lines = self.default.lines if lines is None else bool(lines) 
        self.lines.append(lines)
        
    def add_markers(self, marker = None):
        single_marker = isinstance(marker, str) or marker is None
        marker = self.check_marker(marker) if single_marker else list(map(self.check_marker, marker))
        length = len(self.x[-1])
        marker = ut.to_list(marker, length)
        self.marker.append(marker)

    def add_colors(self, color = None):
        list_color = isinstance(color, list) 
        color = list(map(self.check_color, color)) if list_color else self.check_color(color)
        length = len(self.x[-1])
        self.past_colors = self.past_colors + [color] if color not in self.past_colors else self.past_colors
        color = ut.to_list(color, length)
        self.color.append(color)

    def add_styles(self, style = None):
        single_style = isinstance(style, str) or style is None
        style = self.check_style(style) if single_style else list(map(self.check_style, style))
        length = len(self.x[-1])
        style = ut.to_list(style, length)
        self.style.append(style)

    def add_fillx(self, fillx = None):
        fillx = self.check_fill(fillx)
        self.fillx.append(fillx)

    def add_filly(self, filly = None):
        filly = self.check_fill(filly)
        self.filly.append(filly)

    def add_label(self, label = None):
        spaces = ut.only_spaces(label)
        label = self.default.label if label is None or spaces else str(label).strip() # strip to remove spaces before and after
        self.label.append(label)
        #figure.subplot.label_show.append(default.label_show)
    
##############################################
######    Draw() Functions Utilities   #######
##############################################

    def to_time(self, data):
        dates = any([isinstance(el, str) for el in data])
        data = self.date.strings_to_time(data) if dates else data
        return data, dates
    
    def check_marker(self, marker = None):
        marker = None if marker is None else str(marker)
        marker = self.default.marker if marker is None else marker
        marker = ut.marker_codes[marker] if marker in ut.marker_codes else marker
        marker = marker if marker in ut.hd_symbols else marker[0]
        return marker

    def check_color(self, color = None):
        color = color if ut.is_color(color) else None
        color = self.next_color() if color is None else color
        return color

    def next_color(self):
        color = ut.difference(self.color_sequence, self.past_colors)
        color = color[0] if len(color) > 0 else self.color_sequence[0]
        return color

    def check_style(self, style = None):
        style = None if style is None else str(style)
        style = style if ut.is_style(style) else ut.no_color
        return style

    def check_fill(self, fill = None):
        fill = self.default.fill if fill is None else fill
        fill = False if isinstance(fill, str) and fill != self.default.fill_internal else fill
        fill = 0 if fill is True else fill
        return fill

##############################################
######    Other Plotting Functions    ########
##############################################

    def draw_bar(self, *args, marker = None, color = None, fill = None, width = None, orientation = None, minimum = None, offset = None, reset_ticks = None, xside = None, yside = None, label = None):
        x, y = ut.set_data(*args)
        marker = self.default.bar_marker if marker is None else marker
        fill = self.default.bar_fill if fill is None else fill
        width = self.default.bar_width if width is None else width
        width = 1 if width > 1 else 0 if width < 0 else width
        orientation = self.check_orientation(orientation, 1)
        minimum = 0 if minimum is None else minimum 
        offset = 0 if offset is None else offset
        reset_ticks = True if reset_ticks is None else reset_ticks

        x_string = any([type(el) == str for el in x]) # if x are strings
        l = len(x)
        xticks = range(1, l + 1) if x_string else x
        xlabels = x if x_string else map(str, x)
        x = xticks if x_string else x
        x = [el + offset for el in x]
        xbar, ybar = ut.bars(x, y, width, minimum)
        xbar, ybar = [xbar, ybar]  if orientation[0] == 'v' else [ybar, xbar]
        (self.set_xticks(xticks, xlabels, xside) if orientation[0] == 'v' else self.set_yticks(xticks, xlabels, yside)) if reset_ticks else None


        firstbar = min([b for b in range(len(x)) if ybar[b][1] != 0], default = 0) # finds the position of the first non zero bar

        for b in range(len(x)):
            xb = xbar[b]; yb = ybar[b]
            plot_label = label if b == firstbar else None
            plot_color = color if b == 0 else self.color[-1]
            nobar = (yb[1] == 0 and orientation[0] == 'v') or (xb[1] == 0 and orientation[0] == 'h')
            plot_marker = " " if nobar else marker
            plot_color = color if b == 0 else self.color[-1][-1]
            self.draw_rectangle(xb, yb,
                                xside = xside, 
                                yside = yside,
                                lines = True,
                                marker = plot_marker,
                                color = plot_color,
                                fill = fill,
                                label = plot_label)

    def draw_multiple_bar(self, *args, marker = None, color = None, fill = None, width = None, orientation = None, minimum = None, offset = None, reset_ticks = None, xside = None, yside = None, labels = None):
        x, Y = ut.set_multiple_bar_data(*args)
        ly = len(Y)
        width = self.default.bar_width if width is None else width
        marker = [marker] * ly if marker is None or type(marker) != list else marker
        color = [color] * ly if color is None else color
        labels = [labels] * ly if labels is None else labels
        width = width / ly if ly != 0 else 0
        offset = ut.linspace(-1 / 2 + 1 / (2 * ly), 1 / 2 - 1 / (2 * ly), ly) if ly != 0 else []
        
        for i in range(ly):
            self.draw_bar(x, Y[i],
                          marker = marker[i],
                          color = color[i],
                          fill = fill,
                          width = width,
                          orientation = orientation,
                          minimum = minimum,
                          offset = offset[i],
                          xside = xside,
                          yside = yside,
                          label = labels[i],
                          reset_ticks = reset_ticks)

    def draw_stacked_bar(self, *args, marker = None, color = None, fill = None, width = None, orientation = None, minimum = None, offset = None, reset_ticks = None, xside = None, yside = None, labels = None):
        x, Y = ut.set_multiple_bar_data(*args)
        ly = len(Y)
        marker = [marker] * ly if marker is None or type(marker) != list else marker
        color = [color] * ly if color is None else color
        labels = [labels] * ly if labels is None else labels
        Y = ut.transpose([ut.cumsum(el) for el in ut.transpose(Y)])
        for i in range(ly - 1, -1, -1):
            self.draw_bar(x, Y[i],
                          xside = xside, 
                          yside = yside,
                          marker = marker[i],
                          color = color[i],
                          fill = fill,
                          width = width,
                          orientation = orientation,
                          label = labels[i],
                          minimum = minimum,
                          reset_ticks = reset_ticks)

    def draw_hist(self, data, bins = None, marker = None, color = None, fill = None, norm = None, width = None, orientation = None, minimum = None, xside = None, yside = None, label = None):
        bins = self.default.hist_bins if bins is None else bins
        norm = False if norm is None else norm
        x, y = ut.hist_data(data, bins, norm)
        self.draw_bar(x, y,
                      xside = xside, 
                      yside = yside,
                      marker = marker,
                      color = color,
                      fill = fill,
                      width = width,
                      orientation = orientation,
                      label = label,
                      minimum = None,
                      reset_ticks = False)

    def draw_candlestick(self, dates, data, colors = None, orientation = None, xside = None, yside = None, label = None):
        orientation = self.check_orientation(orientation, 1)
        markers = ['sd', '│', '─'] #if markers is None else markers
        colors = ['green', 'red'] if colors is None else colors
        x = []; y = []; color = []
        ln = len(dates)
        data = {"Open": [], "Close": [], "High": [], "Low": []} if len(data) == 0 else data
        Open = data["Open"]; Close = data["Close"]; High = data["High"]; Low = data["Low"]
        for i in range(ln):
            d = dates[i]
            o, c, h, l = Open[i], Close[i], High[i], Low[i]
            color = colors[0] if c > o else colors[1]
            m, M = min(o, c), max(o, c)
            lab = label if i == 0 else None
            if orientation in ['v', 'vertical']:
                self.draw([d, d], [M, h], xside = xside, yside = yside, color = color, marker = markers[1], lines = True)
                self.draw([d, d], [l, m], xside = xside, yside = yside, color = color, marker = markers[1], lines = True)
                self.draw([d, d], [m, M], xside = xside, yside = yside, color = color, marker = markers[0], lines = True, label = lab)
            elif orientation in ['h', 'horizontal']:
                self.draw([M, h], [d, d], xside = xside, yside = yside, color = color, marker = markers[2], lines = True)
                self.draw([l, m], [d, d], xside = xside, yside = yside, color = color, marker = markers[2], lines = True)
                self.draw([m, M], [d, d], xside = xside, yside = yside, color = color, marker = markers[0], lines = True, label = lab)

    def draw_box(self, *args, xside = None, yside = None, orientation = None, colors = None, label = None, fill = None, width = None, minimum = None, offset = None, reset_ticks = None, quintuples = None):
        x, y = ut.set_data(*args)
        fill = self.default.bar_fill if fill is None else fill
        width = self.default.bar_width if width is None else width
        width = 1 if width > 1 else 0 if width < 0 else width
        orientation = self.check_orientation(orientation, 1)
        minimum = 0 if minimum is None else minimum
        offset = 0 if offset is None else offset
        reset_ticks = True if reset_ticks is None else reset_ticks
        colors = ['green', 'red'] if colors is None else colors
        quintuples = False if quintuples is None else quintuples

        x_string = any([type(el) == str for el in x]) # if x are strings
        l = len(x)
        xticks = range(1, l + 1) if x_string else x
        xlabels = x if x_string else map(str, x)
        x = xticks if x_string else x
        x = [el + offset for el in x]
        (self.set_xticks(xticks, xlabels, xside) if orientation[0] == 'v' else self.set_yticks(xticks, xlabels, yside)) if reset_ticks else None
        if quintuples:
            # todo: check y is aligned.
            _, _, _, _, _, c, xbar = ut.box(x, y, width, minimum)
            q1, q2, q3, max_, min_ = [], [], [], [], []
            for d in y:
                max_.append(d[0])
                q3.append(d[1])
                q2.append(d[2])
                q1.append(d[3])
                min_.append(d[4])
        else:
            q1, q2, q3, max_, min_, c, xbar = ut.box(x, y, width, minimum)
        markers = ['sd', '│', '─'] #if markers is None else markers
        
        for i in range(l):
            lab = label if i == 0 else None
            color = colors[0]
            mcolor = colors[1]
            d, l, h, m, E, M = c[i], min_[i], max_[i], q1[i], q2[i], q3[i]
            Ew = (M - m) / 30
            if orientation in ['v', 'vertical']:
                self.draw([d, d], [M, h], xside = xside, yside = yside, color = color, marker = markers[1], lines = True)
                self.draw([d, d], [l, m], xside = xside, yside = yside, color = color, marker = markers[1], lines = True)
                self.draw_rectangle(xbar[i], [m, M], xside = xside, yside = yside,
                    lines = True, color = color, fill = fill, marker = markers[0], label = lab)
                self.draw_rectangle(xbar[i], [E, E], xside = xside, yside = yside,
                    lines = True, color = mcolor, fill = fill, marker = markers[2])
                #self.draw([d, d], [m, M], xside = xside, yside = yside, color = color, marker = markers[0], lines = True, label = lab)
                #self.draw(xbar[i], [E, E], xside = xside, yside = yside, color = mcolor, marker = markers[0], lines = False)
            elif orientation in ['h', 'horizontal']:
                self.draw([M, h], [d, d], xside = xside, yside = yside, color = color, marker = markers[2], lines = True)
                self.draw([l, m], [d, d], xside = xside, yside = yside, color = color, marker = markers[2], lines = True)
                self.draw_rectangle([m, M], xbar[i], xside = xside, yside = yside,
                    lines = True, color = color, fill = fill, marker = markers[0], label = lab)
                self.draw_rectangle([E, E], xbar[i], xside = xside, yside = yside,
                    lines = True, color = mcolor, fill = fill, marker = markers[1])
                #self.draw([m, M], [d, d], xside = xside, yside = yside, color = color, marker = markers[0], lines = True, label = lab)
                #self.draw([E, E], [d, d], xside = xside, yside = yside, color = 'red', marker = markers[0], lines = True)
        
##############################################
###########    Plotting Tools    #############
##############################################
        
    def draw_error(self, *args, xerr = None, yerr = None, color = None, xside = None, yside = None, label = None):
        x, y = ut.set_data(*args)
        l = len(x)
        xerr = [0] * l if xerr is None else xerr
        yerr = [0] * l if yerr is None else yerr
        for i in range(l):
            col = self.color[-1][-1] if i > 0 else color
            self.draw([x[i], x[i]], [y[i] - yerr[i] / 2, y[i] + yerr[i] / 2], xside = xside, yside = yside, marker = "│", color = col, lines = True)
            col = self.color[-1][-1] if i == 0 else col
            self.draw([x[i] - xerr[i] / 2, x[i] + xerr[i] / 2], [y[i], y[i]], xside = xside, yside = yside, marker = "─", color = col, lines = True)
            self.draw([x[i]], [y[i]], xside = xside, yside = yside, marker = "┼", color = col, lines = True)

    def draw_event_plot(self, data, marker = None, color = None, orientation = None, side = None):
        x, y = data, [1.1] * len(data)
        orientation = self.check_orientation(orientation, 1)
        if orientation in ['v', 'vertical']:
            self.draw(x, y, xside = side, marker = marker, color = color, fillx = True)
            self.set_ylim(0, 1)
            self.set_yfrequency(0)
        else:
            self.draw(y, x, yside = side, marker = marker, color = color, filly = True)
            self.set_xlim(0, 1)
            self.set_xfrequency(0)

    def draw_vertical_line(self, coordinate, color = None, xside = None):
        coordinate = self.date.string_to_time(coordinate) if isinstance(coordinate, str) else coordinate
        pos = self.xside_to_pos(xside)
        self.vcoord[pos].append(coordinate)
        color = self.ticks_color if color is None else color
        self.vcolors[pos].append(self.check_color(color))

    def draw_horizontal_line(self, coordinate, color = None, yside = None):
        coordinate = self.date.string_to_time(coordinate) if isinstance(coordinate, str) else coordinate
        pos = self.xside_to_pos(yside)
        self.hcoord[pos].append(coordinate)
        color = self.ticks_color if color is None else color
        self.hcolors[pos].append(self.check_color(color))

    def draw_text(self, text, x, y, xside = None, yside = None, color = None, background = None, style = None, orientation = None, alignment = None):
        orientation = self.check_orientation(orientation)
        text = text if orientation is self.default.orientation[0] else text[::-1]
        self.text.append(str(text))
        x = self.date.string_to_time(x) if isinstance(x, str) else x
        y = self.date.string_to_time(y) if isinstance(y, str) else y
        self.tx.append(x)
        self.ty.append(y) 
        self.txside.append(self.correct_xside(xside))
        self.tyside.append(self.correct_yside(yside))
        color = self.next_color() if color is None or not ut.is_color(color) else color
        background = self.canvas_color if background is None or not ut.is_color(background) else background
        self.tfull.append(color)
        self.tback.append(background)
        self.tstyle.append(self.check_style(style))
        alignment = self.check_alignment(alignment)
        self.torien.append(orientation)
        self.talign.append(alignment)

    def draw_rectangle(self, x = None, y = None, marker = None, color = None, lines = None, fill = None, reset_lim = False, xside = None, yside = None, label = None):
        x = [0, 1] if x is None or len(x) < 2 else x  
        y = [0, 1] if y is None or len(y) < 2 else y  
        xpos = self.xside_to_pos(xside)
        ypos = self.yside_to_pos(yside)
        lines = True if lines is None else lines
        fill = False if fill is None else fill
        xm = min(x); xM = max(x);
        ym = min(y); yM = max(y);
        dx = abs(xM - xm); dy = abs(yM - ym);
        if reset_lim:
            self.xlim[xpos] = [xm - 0.5 * dx, xM + 0.5 * dx]
            self.ylim[xpos] = [ym - 0.5 * dy, yM + 0.5 * dy]
        x, y = [xm, xm, xM, xM, xm], [ym, yM, yM, ym, ym]
        self.draw(x, y,
                  xside = xside, 
                  yside = yside,
                  lines = True if fill else lines,
                  marker = marker,
                  color = color,
                  fillx = "internal" if fill else False,
                  filly = False,
                  label = label)

    def draw_polygon(self, x = None, y = None,  radius = None, sides = None, marker = None, color = None, lines = None, fill = None, reset_lim = False, xside = None, yside = None, label = None):
        x = 0 if x is None else x
        y = 0 if y is None else y
        radius = 1 if radius is None else abs(int(radius))
        sides = 3 if sides is None else max(3, int(abs(sides)))
        xpos = self.xside_to_pos(xside)
        ypos = self.yside_to_pos(yside)
        lines = True if lines is None else lines
        fill = False if fill is None else fill
        
        alpha = 2 * math.pi / sides
        init = alpha / 2 + math.pi / 2 if sides % 2 == 0 else alpha / 4 * ((-1) ** (sides // 2))# * math.pi #- ((-1) ** (sides)) * alpha / 4
        #init = 0 * init
        get_point = lambda i: [x + math.cos(alpha * i + init) * radius, y + math.sin(alpha * i + init) * radius]
        # the rounding is needed so that results like 9.9999 are rounded to 10 and display as same coordinate in the plot, otherwise the floor function will turn 9.999 into 9
        points = [get_point(i) for i in range(sides + 1)]
        if reset_lim:
            self.xlim[xpos] = [x - 1.5 * radius, x + 1.5 * radius]
            self.ylim[xpos] = [y - 1.5 * radius, y + 1.5 * radius]
        self.draw(*ut.transpose(points),
                  xside = xside, 
                  yside = yside,
                  lines = True if fill else lines,
                  marker = marker,
                  color = color,
                  fillx = "internal" if fill else False,
                  filly = False,
                  label = label)
        
    def draw_confusion_matrix(self, actual, predicted, color = None, style = None, labels = None):
        color = self.default.cmatrix_color if color is None else self.check_color(color)
        style = self.default.cmatrix_style if style is None else self.check_style(style)
        
        L = len(actual)
        n_labels = sorted(ut.no_duplicates(actual))
        labels = n_labels if labels is None else list(labels)
        l = len(n_labels)

        get_sum = lambda a, p: sum([actual[i] == a and predicted[i] == p for i in range(L)])
        cmatrix = [[get_sum(n_labels[r], n_labels[c]) for c in range(l)] for r in range(l)]
        cm = ut.join(cmatrix); m, M, t = min(cm), max(cm), sum(cm)

        lm = 253; lM = 80
        to_255 = lambda l: round(lm + (lM - lm) * (l - m) / (M - m)) # l=m -> lm; l=M->lM
        to_color = lambda l: tuple([to_255(l)] * 3)
        to_text = lambda n: str(round(n, 2)) + ' - ' + str(round(100 * n / t, 2)) + '%'
        for r in range(l):
            for c in range(l):
                count = cmatrix[r][c]
                col = to_color(count)
                self.draw_rectangle([c - 0.5, c + 0.5], [r - 0.5, r + 0.5], color = col, fill = True)
                self.draw_text(to_text(count), c, r, color = color, background = col, style = style)

        self.set_yreverse(True)
        self.set_xticks(n_labels, labels)
        self.set_yticks(n_labels, labels)
        self.set_ticks_color(color); self.set_ticks_style(style);
        self.set_axes_color('default'); self.set_canvas_color('default');
        self.set_title('Confusion Matrix')
        self.set_xlabel('Predicted')
        self.set_ylabel('Actual')

    def draw_indicator(self, value, label = None, color = None, style = None):
        color = self.default.cmatrix_color if color is None else self.check_color(color)
        style = self.default.cmatrix_style if style is None else self.check_style(style)

        self.set_title(label)
        self.set_ticks_color(color);
        self.set_ticks_style(style);
        self.set_axes_color('default')
        self.set_canvas_color('default')
        self.set_xfrequency(0)
        self.set_yfrequency(0)

        self.draw_text(str(value), 0, 0, color = color, style = style, alignment = 'center')

##############################################
##############    2D Plots    ################
############################################## 
    
    def draw_matrix(self, matrix, marker = None, style = None, fast = False):
        matrix = [l.copy() for l in matrix]
        marker = [marker] if type(marker) != list else marker
        marker = [self.check_marker("sd") if el in ut.join([None, ut.hd_symbols]) else self.check_marker(el) for el in marker]
        style = ut.no_color if style is None else self.check_style(style)
        cols, rows = ut.matrix_size(matrix)
        rows = 0 if cols == 0 else rows
        matrix = matrix if rows * cols != 0 and ut.is_rgb_color(matrix[0][0]) else ut.turn_gray(matrix)
        marker = ut.repeat(marker, cols)
        if not fast:
            for r in range(rows):
                xyc = [(c, r, matrix[rows - 1 - r][c]) for c in range(cols)]
                x, y, color = ut.transpose(xyc, 3)
                self.draw(x, y, marker = marker, color = color, style = style)
            self.set_canvas_color("black")
            self.set_xlabel('column') 
            self.set_ylabel('row')
            xf, yf = min(self.xfrequency[0], cols), min(self.yfrequency[0], rows)
            xt = ut.linspace(0, cols - 1, xf)
            xl = ut.get_labels([el + 1 for el in xt])
            yt = ut.linspace(0, rows - 1, yf)
            yl = ut.get_labels([rows - el for el in yt])
            self.set_xticks(xt, xl)
            self.set_yticks(yt, yl)
        else: # if fast
            for r in range(rows):
                for c in range(cols):
                    ansi = ut.colors_to_ansi(matrix[r][c], style, "black")
                    matrix[r][c] = ansi + marker[c] + ut.ansi_end
            self.matrix.canvas = '\n'.join([''.join(row) for row in matrix])
            self.fast_plot = True

    def draw_pie(self, labels, values, colors = None, radius = None, show_values = True, show_percentages = True, title = None, show_values_on_slices = False, donut = False, remaining_color = None):
        """
        Draw a pie chart using filled colored segments and a legend.
        
        Args:
            donut (bool): If True, creates a doughnut chart with hollow center (inner radius = 1/3 outer radius)
            remaining_color (str): If specified, colors the remaining slice with this color instead of leaving it as spaces
        """
        import math
        
        # Input validation
        if len(labels) != len(values):
            raise ValueError("Labels and values must have the same length")
        
        # Calculate total and percentages
        total = sum(values)
        if total == 0:
            raise ValueError("Total of values cannot be zero")
            
        percentages = [(value / total) * 100 for value in values]
        
        # Default colors if not provided
        if colors is None:
            color_cycle = ['red', 'blue', 'green', 'orange', 'magenta', 'cyan', 'white']
            colors = [color_cycle[i % len(color_cycle)] for i in range(len(labels))]
        
        # Default radius - calculate based on available plot space
        if radius is None:
            # Get the actual plot area dimensions 
            plot_width, plot_height = self.size
            
            # Set radius to half of the smaller dimension minus 4 for border margin
            radius = (min(plot_width, plot_height) - 4) / 2.0
            radius = max(radius, 3)  # Ensure minimum radius of 3
        
        # Center the pie chart
        center_x = 0
        center_y = 0
        
        # Terminal characters have an aspect ratio of approximately 1.5:1 (height:width)
        # To make circles appear circular, we need to adjust the x-axis scaling
        aspect_ratio = 1.5
        
        # Remove axes - pie charts don't have them
        self.set_xfrequency(0)
        self.set_yfrequency(0)
        self.set_axes_color('default')
        self.set_canvas_color('default')
        
        # Collect all points for each segment, then draw each segment in one call
        # Use efficient scanning - just slightly beyond the actual pie radius
        # For doughnuts, use denser scanning to ensure solid ring
        if donut:
            scan_radius_x = int(radius * aspect_ratio * 1.5 + 3)
            scan_radius_y = int(radius * 1.5 + 3)
        else:
            scan_radius_x = int(radius * aspect_ratio * 1.2 + 2)
            scan_radius_y = int(radius * 1.2 + 2)
        
        # Pre-calculate cumulative angles for segment boundaries
        segment_boundaries = []
        current_cumulative = 0
        for value in values:
            slice_angle = (value / total) * 2 * math.pi
            segment_boundaries.append((current_cumulative, current_cumulative + slice_angle))
            current_cumulative += slice_angle
        
        # Collect all points for each segment using sets to avoid duplicates
        segment_points = [set() for _ in range(len(labels))]  # One set per segment
        
        # Use FLOOD FILL approach - systematically fill every position in concentric circles
        # This ensures no gaps by filling from center outward
        for y_offset in range(-scan_radius_y, scan_radius_y + 1):
            for x_offset in range(-scan_radius_x, scan_radius_x + 1):
                # Calculate distance from center with aspect ratio correction
                # Since terminal chars are ~1.5x taller than wide, compress x coordinate
                adjusted_x = x_offset / aspect_ratio
                distance = math.sqrt(adjusted_x * adjusted_x + y_offset * y_offset)
                
                # For doughnut inner boundary, use elliptical check to create circular appearance
                # The inner boundary should be elliptical in terminal coordinates to appear circular
                inner_radius = radius / 3.0 if donut else 0
                
                # Check if point is outside the inner ellipse (for circular appearance)
                if donut:
                    # Create elliptical inner boundary: x^2/a^2 + y^2/b^2 > r^2
                    # where a = inner_radius * aspect_ratio, b = inner_radius
                    ellipse_x_term = (x_offset * x_offset) / (inner_radius * aspect_ratio * inner_radius * aspect_ratio)
                    ellipse_y_term = (y_offset * y_offset) / (inner_radius * inner_radius)
                    ellipse_value = ellipse_x_term + ellipse_y_term
                    outside_inner = ellipse_value > 1.0
                    
                else:
                    outside_inner = True
                
                # Use exact radius to stay within plot boundaries
                threshold = radius
                
                if distance <= threshold and outside_inner:
                    # Calculate angle for this position using adjusted coordinates
                    angle = math.atan2(y_offset, adjusted_x)
                    if angle < 0:
                        angle += 2 * math.pi
                    
                    # Find which segment this position belongs to using robust angle detection
                    segment_idx = 0
                    found_segment = False
                    epsilon = 0.02  # Even larger epsilon for maximum boundary coverage
                    
                    for i, (start_angle, end_angle) in enumerate(segment_boundaries):
                        # Handle wraparound case for segments that cross 0 degrees
                        if end_angle > 2 * math.pi:
                            wrap_end = end_angle - 2 * math.pi
                            if angle >= start_angle - epsilon or angle <= wrap_end + epsilon:
                                segment_idx = i
                                found_segment = True
                                break
                        else:
                            # Use very generous boundary detection
                            # For the last segment, use <= to include the boundary
                            if i == len(segment_boundaries) - 1:
                                if start_angle - epsilon <= angle <= end_angle + epsilon:
                                    segment_idx = i
                                    found_segment = True
                                    break
                            else:
                                if start_angle - epsilon <= angle < end_angle + epsilon:
                                    segment_idx = i
                                    found_segment = True
                                    break
                    
                    # If no segment found (due to floating point precision), assign based on closest angle
                    if not found_segment:
                        # Find the segment with the smallest angle distance
                        min_distance = float('inf')
                        for i, (start_angle, end_angle) in enumerate(segment_boundaries):
                            mid_angle = (start_angle + end_angle) / 2
                            # Handle wraparound for mid angle calculation
                            if end_angle > 2 * math.pi:
                                mid_angle = start_angle + ((end_angle - start_angle) / 2)
                                if mid_angle > 2 * math.pi:
                                    mid_angle -= 2 * math.pi
                            
                            # Calculate angular distance (accounting for circular nature)
                            angle_diff = abs(angle - mid_angle)
                            if angle_diff > math.pi:
                                angle_diff = 2 * math.pi - angle_diff
                            
                            if angle_diff < min_distance:
                                min_distance = angle_diff
                                segment_idx = i
                    
                    # Add this exact character position to the appropriate segment
                    char_x = center_x + x_offset  
                    char_y = center_y + y_offset
                    segment_points[segment_idx].add((char_x, char_y))
        
        # SECOND PASS: Fill any potential gaps by adding adjacent positions
        # This ensures complete coverage by adding neighboring positions to existing points
        additional_points = [set() for _ in range(len(labels))]
        for segment_idx, points in enumerate(segment_points):
            for (x, y) in points:
                # Add neighboring positions to ensure no gaps
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        neighbor_x = x + dx
                        neighbor_y = y + dy
                        
                        # Check if this neighbor is within the circular area using same logic as main pass
                        x_offset = neighbor_x - center_x
                        y_offset = neighbor_y - center_y
                        adjusted_x = x_offset / aspect_ratio  
                        neighbor_distance = math.sqrt(adjusted_x * adjusted_x + y_offset * y_offset)
                        
                        # Use same boundary checks as main algorithm
                        inner_radius = radius / 3.0 if donut else 0
                        
                        # Check if point is outside the inner ellipse (for circular appearance)
                        if donut:
                            # Use same elliptical inner boundary as main pass
                            ellipse_x_term = (x_offset * x_offset) / (inner_radius * aspect_ratio * inner_radius * aspect_ratio)
                            ellipse_y_term = (y_offset * y_offset) / (inner_radius * inner_radius)
                            outside_inner = ellipse_x_term + ellipse_y_term > 1.0
                        else:
                            outside_inner = True
                        
                        # Use exact radius to stay within plot boundaries (same as main pass)
                        threshold = radius
                        
                        if neighbor_distance <= threshold and outside_inner:
                            additional_points[segment_idx].add((neighbor_x, neighbor_y))
        
        # Merge additional points with main points
        for segment_idx in range(len(labels)):
            segment_points[segment_idx].update(additional_points[segment_idx])
        
        # Draw each segment using a different approach - draw filled shapes row by row
        # This ensures complete filling without gaps
        for segment_idx, (points, color) in enumerate(zip(segment_points, colors)):
            if points:  # Only draw if segment has points
                # Handle remaining_color for single-value pie charts
                if color == "default":
                    if remaining_color is not None:
                        # Use the specified remaining_color instead of default
                        color = remaining_color
                    else:
                        # Skip drawing - leave as spaces (current behavior)
                        continue
                    
                points_list = list(points)
                
                # Group points by y-coordinate to draw horizontal filled lines
                y_groups = {}
                for x, y in points_list:
                    if y not in y_groups:
                        y_groups[y] = []
                    y_groups[y].append(x)
                
                # For doughnut charts, use smart filling that avoids the hollow center
                # For regular pie charts, use full horizontal line filling
                if donut:
                    # Smart filling for doughnut charts: fill gaps within ring segments but avoid center
                    for y_coord, x_coords in y_groups.items():
                        if x_coords:
                            x_coords.sort()  # Sort x coordinates
                            
                            # Find continuous segments, avoiding the center gap
                            fill_x_coords = []
                            x_step = 0.5
                            
                            # Determine if this y_coord passes through the hollow center
                            y_offset = y_coord - center_y
                            center_x_range = []
                            
                            # Calculate the x-range that should be hollow at this y-coordinate
                            if abs(y_offset) < inner_radius:
                                # This y-line passes through the hollow center
                                # Calculate x-bounds of the elliptical hollow area
                                ellipse_y_term = (y_offset * y_offset) / (inner_radius * inner_radius)
                                if ellipse_y_term < 1.0:
                                    ellipse_x_term_needed = 1.0 - ellipse_y_term
                                    max_x_offset = math.sqrt(ellipse_x_term_needed) * inner_radius * aspect_ratio
                                    center_x_min = center_x - max_x_offset
                                    center_x_max = center_x + max_x_offset
                                    center_x_range = [center_x_min, center_x_max]
                            
                            # Fill between consecutive x-coordinates, but avoid the center region
                            i = 0
                            while i < len(x_coords):
                                segment_start = x_coords[i]
                                
                                # Find the end of this continuous segment
                                j = i
                                while j < len(x_coords) - 1:
                                    gap = x_coords[j + 1] - x_coords[j]
                                    # If there's a large gap, this segment ends
                                    if gap > 2.0:  # Allow small gaps but break on large ones
                                        break
                                    j += 1
                                
                                segment_end = x_coords[j]
                                
                                # Fill this segment, but avoid the center region
                                if center_x_range:
                                    # Split segment around the hollow center
                                    center_min, center_max = center_x_range
                                    
                                    # Fill left part (before center)
                                    if segment_start < center_min:
                                        left_end = min(segment_end, center_min)
                                        current_x = segment_start
                                        while current_x <= left_end:
                                            fill_x_coords.append(current_x)
                                            current_x += x_step
                                    
                                    # Fill right part (after center)
                                    if segment_end > center_max:
                                        right_start = max(segment_start, center_max)
                                        current_x = right_start
                                        while current_x <= segment_end:
                                            fill_x_coords.append(current_x)
                                            current_x += x_step
                                else:
                                    # No center interference, fill entire segment
                                    current_x = segment_start
                                    while current_x <= segment_end:
                                        fill_x_coords.append(current_x)
                                        current_x += x_step
                                
                                i = j + 1
                            
                            # Draw the filled segments
                            if fill_x_coords:
                                fill_y_coords = [y_coord] * len(fill_x_coords)
                                self.draw(fill_x_coords, fill_y_coords, marker='sd', color=color)
                else:
                    # For regular pie charts, use full horizontal line filling
                    for y_coord, x_coords in y_groups.items():
                        if x_coords:
                            x_coords.sort()  # Sort x coordinates
                            x_min, x_max = min(x_coords), max(x_coords)
                            
                            # Create a continuous range of x coordinates to fill the gap
                            if x_max > x_min:
                                # Draw filled horizontal line from x_min to x_max
                                fill_x_coords = []
                                x_step = 0.5  # Smaller step for better coverage
                                current_x = x_min
                                while current_x <= x_max:
                                    fill_x_coords.append(current_x)
                                    current_x += x_step
                                fill_y_coords = [y_coord] * len(fill_x_coords)
                                self.draw(fill_x_coords, fill_y_coords, marker='sd', color=color)
                            else:
                                # Single point
                                self.draw([x_min], [y_coord], marker='sd', color=color)
        
        # Reset cumulative_angle for label drawing
        cumulative_angle = 0
        for i, (label, value, percentage, color) in enumerate(zip(labels, values, percentages, colors)):
            slice_angle = (value / total) * 2 * math.pi
            
            # Add value labels on the pie slice (only if show_values_on_slices is True)
            if show_values_on_slices and (show_values or show_percentages):
                # Calculate middle angle of the slice for label placement
                middle_angle = cumulative_angle + slice_angle / 2
                # Position label at 70% of radius for better visibility
                label_radius = radius * 0.7
                label_x = center_x + (label_radius * math.cos(middle_angle)) * aspect_ratio
                label_y = center_y + label_radius * math.sin(middle_angle)
                
                # Build label text for the slice
                slice_label = ""
                if show_values and show_percentages:
                    slice_label = f"{value}\n({percentage:.1f}%)"
                elif show_values:
                    slice_label = str(value)
                elif show_percentages:
                    slice_label = f"{percentage:.1f}%"
                
                # Draw the label on the slice
                self.draw_text(slice_label, label_x, label_y, color='white', alignment='center')
            
            cumulative_angle += slice_angle
        
        # Extend the plot area to accommodate legend (calculate before filtering)
        max_text_length = max(len(f"{label}: {value} ({percentage:.1f}%)") 
                              for label, value, percentage in zip(labels, values, percentages)
                              if label.lower() != "remaining") if any(label.lower() != "remaining" for label in labels) else 20
        
        # Set plot limits to include legend area (adjust x for aspect ratio)
        x_radius = radius * aspect_ratio
        self.set_xlim(-x_radius - 1, x_radius + max_text_length + 2)
        self.set_ylim(-radius - 1, radius + 1)
        
        # Create legend positioned in the bottom right corner of the chart
        legend_start_x = x_radius + 1.5
        legend_start_y = -radius + len(labels) * 1.0 - 0.5
        
        # Filter out "Remaining" labels and default colors for single-value pie charts
        legend_items = []
        for i, (label, value, percentage, color) in enumerate(zip(labels, values, percentages, colors)):
            # Handle remaining_color logic for legend
            if color == "default":
                if remaining_color is not None:
                    # Show "Remaining" in legend when remaining_color is specified
                    legend_items.append((label, value, percentage, remaining_color))
                # Skip if no remaining_color (leave as spaces)
            else:
                # Always show non-default colors
                legend_items.append((label, value, percentage, color))
        
        # Adjust legend positioning for filtered items
        legend_start_y = -radius + len(legend_items) * 1.0 - 0.5
        
        for i, (label, value, percentage, color) in enumerate(legend_items):
            legend_x = legend_start_x
            legend_y = legend_start_y - i * 1.2  # Space between legend items
            
            # Draw colored square for legend matching pie chart blocks
            self.draw([legend_x], [legend_y], marker='sd', color=color)
            
            # Build legend text with colored block prefix
            block_char = "█"  # Solid block character
            legend_text = f"{block_char} {label}"
            if show_values and show_percentages:
                legend_text += f": {value} ({percentage:.1f}%)"
            elif show_values:
                legend_text += f": {value}"
            elif show_percentages:
                legend_text += f": {percentage:.1f}%"
            
            # Use draw_text for the legend with the same color as the segment
            self.draw_text(legend_text, legend_x, legend_y, color=color)
        
        # Set title if provided
        if title:
            self.set_title(title)
        
        # Remove axis labels since pie charts don't need them
        self.set_xlabel('')
        self.set_ylabel('')

    def draw_heatmap(self, dataframe, color = None, style=None):
        color = self.default.cmatrix_color if color is None else self.check_color(color)
        style = self.default.cmatrix_style if style is None else self.check_style(style)

        xlabels = dataframe.columns.tolist()
        ylabels = dataframe.index.tolist()

        cmatrix = dataframe.values.tolist()
        cm = ut.join(cmatrix)
        m, M, t = min(cm), max(cm), sum(cm)

        lm = 253
        lM = 80
        to_255 = lambda l: round(lm + (lM - lm) * (l - m) / (M - m))  # l=m -> lm; l=M->lM
        to_color = lambda l: tuple([to_255(l)] * 3)

        for r in range(len(dataframe.index.tolist())):
            for c in range(len(dataframe.columns.tolist())):
                count = cmatrix[r][c]
                col = to_color(count)
                self.draw_rectangle([c - 0.5, c + 0.5], [r - 0.5, r + 0.5], marker= 'sd', color=col, fill=True)

        y_labels = list(set(range(len(dataframe.columns))))
        x_labels = list(set(range(len(dataframe.columns))))

        self.set_yreverse(True)
        self.set_xticks(x_labels, xlabels)
        self.set_yticks(y_labels, ylabels)
        self.set_ticks_color(color);
        self.set_ticks_style(style);
        self.set_axes_color('default');
        self.set_canvas_color('default');
        self.set_title('Heatmap')
        print(dataframe)

    def draw_image(self, path, marker = None, style = None, fast = False, grayscale = False):
        from PIL import Image        
        path = ut.correct_path(path)
        if not ut.is_file(path):
            return
        image = Image.open(path)
        self._draw_image(image, marker = marker, style = style, grayscale = grayscale, fast = fast)
        
##############################################
#######    Plotting Tools Utilities    #######
##############################################

    def check_orientation(self, orientation = None, default_index = 0):
        default = self.default.orientation
        default_first_letter = [el[0] for el in default]
        orientation = default[default_first_letter.index(orientation)] if orientation in default_first_letter else orientation
        orientation = default[default_index] if orientation not in default else orientation
        return orientation

    def check_alignment(self, alignment = None):
        default = self.default.alignment[0:-1]
        default_first_letter = [el[0] for el in default]
        alignment = default[default_first_letter.index(alignment)] if alignment in default_first_letter else alignment
        alignment = default[1] if alignment not in default else alignment
        return alignment

    def _draw_image(self, image, marker = None, style = None, fast = False, grayscale = False):
        from PIL import ImageOps
        image = ImageOps.grayscale(image) if grayscale else image
        image = image.convert('RGB')
        size = ut.update_size(image.size, self.size)
        image = image.resize(size, resample = True)
        matrix = ut.image_to_matrix(image)
        self.set_xfrequency(0); self.set_yfrequency(0);
        self.draw_matrix(matrix, marker = marker, style = style, fast = fast)
        self.set_xlabel(); self.set_ylabel()