import numpy as np
import matplotlib.pyplot as plt
from matplotlib.transforms import BlendedGenericTransform

def stylize(ax,
		xlabel = '$\\alpha$',
		ylabel = '$\\beta$' ,
		xlim   = [-8 , 8]   ,
		ylim   = [-8 , 8]   ,
		aspect = 'equal'    ,
		ticks_frequency = 1 ,
		ticks='all'	        ):
	
	#Set min-max values
	xmin, xmax = xlim
	ymin, ymax = ylim
	ax.set(xlim=(xmin-1, xmax+1), ylim=(ymin-1, ymax+1), aspect=aspect)
	
	#Setup spines
	ax.spines["left"]  .set_position(("data", 0))
	ax.spines["bottom"].set_position(("data", 0))
	ax.spines["top"]   .set_visible(False)
	ax.spines["right"] .set_visible(False)
	
	#Setup arrows
	arrow_fmt = dict(markersize=4, color='black', clip_on=False)
	ax.plot((1), (0), marker='>', transform=ax.get_yaxis_transform(), **arrow_fmt)
	ax.plot((0), (1), marker='^', transform=ax.get_xaxis_transform(), **arrow_fmt)

	#Setup labels
	ax.text(1.03, 0, xlabel, transform=BlendedGenericTransform(ax.transAxes, ax.transData), va='center',size=12)
	ax.text(0, 1.05, ylabel, transform=BlendedGenericTransform(ax.transData, ax.transAxes), ha='center', size=12)

	# Create custom major ticks to determine position of tick labels
	x_ticks = np.arange(int(xmin), int(xmax)+1, ticks_frequency)
	y_ticks = np.arange(int(ymin), int(ymax)+1, ticks_frequency)
	
	if ticks=='all':
		ax.set_xticks(x_ticks[ (x_ticks != 0) ])
		ax.set_yticks(y_ticks[ (y_ticks != 0) ])
	elif ticks=='even':
		ax.set_xticks(x_ticks[ ((x_ticks%2) != 1) & (x_ticks != 0) ])
		ax.set_yticks(y_ticks[ ((y_ticks%2) != 1) & (y_ticks != 0) ])
	elif ticks=='odd':
		ax.set_xticks(x_ticks[ (((x_ticks-1)%2) != 1) & (x_ticks != 0) ])
		ax.set_yticks(y_ticks[ (((y_ticks-1)%2) != 1) & (y_ticks != 0) ])
	elif ticks=='none':
		ax.set_xticks([])
		ax.set_yticks([])
	
	# Draw major and minor grid lines
	ax.grid(False)
	plt.tight_layout(w_pad=2)
	return

def cross_plot(*,
		xlabel = '$\\alpha$',
		ylabel = '$\\beta$' ,
		xlim   = [-8 , 8] ,
		ylim   = [-8 , 8] ,
		aspect = 'equal',
		ticks_frequency = 1,
		ticks='all'	
):
	
	
	#Create style cheat
	config = {
    'xlabel' : xlabel    				,
	'ylabel' : ylabel    				,
	'xlim'   : xlim      				,
	'ylim'   : ylim      				,
	'aspect' : aspect    				,
	'ticks_frequency' : ticks_frequency ,
	'ticks': ticks	
	}

	fig, ax = plt.subplots( figsize = ((3+3/8),(3+3/8)))
	
	stylize(ax, **config)

	return fig, ax

def double_cross_plot(*, config1, config2):
	
	try:
		plt.style.use('jlop')
	except:
		print('Could not find \'jlop\' matploblib theme. Falling back to Default')
	
	fig, (ax1,ax2) = plt.subplots( ncols=2, figsize = (2*(3+3/8),(3+3/8)))
	
	stylize(ax1, **config1)
	stylize(ax2, **config2)

	circle2 = plt.Circle((0, 0),1, color='black', fill=False)
	ax2.add_patch(circle2)

	return fig, ax1,ax2

def add_direction(ax, angle, label, rrange):

	line = np.array(rrange)*np.exp(1j*(angle*np.pi/180+np.pi/2))        
	ax.plot(line.real,line.imag,ls = '-.', lw = 0.8, c = 'gray')
	ax.annotate(label, xy = (1.08*line.real[1],1.08*line.imag[1]), rotation=-(180-angle),ha='center',va='center')
	ax.annotate('$ {angle} \\degree$'.format(angle = angle), xy = (1.2*line.real[1],1.2*line.imag[1]), rotation=-(180-angle),ha='center',va='center')

	return