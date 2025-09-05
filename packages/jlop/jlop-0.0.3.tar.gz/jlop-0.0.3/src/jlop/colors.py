import matplotlib as mpl

def set_colorcycle(name='default'):
	
	if name == 'default':
		# 
		color_cycle = ['ffff00','ff6500','dc0000','ff0097','360097','0000ca','0097ff','00a800','006500','653600','976536','b9b9b9','868686','454545','000000']
	elif name =='titipipi':
		color_cycle = ['#4A4842', '#56a8d5', '#5b8c5a', '#dc851f', '#c45845']
	elif name == 'catppuccin':
		#
		color_cycle = ['8caaee', 'ef9f76', 'a6d189', 'e78284', 'ca9ee6', 'ea999c', 'f4b8e4', 'f2d5cf', '81c8be', 'babbf1']
	elif name == 'cga':
		#
		color_cycle = ['000000', '3322ff', '660033', 'ff0033', '770088', 'ff33dd', '007722', '00ff33', '227788', '22eeff', '996600', 'ffee33', '777799']        
	elif name == 'pc-88':
		# https://lospec.com/palette-list/pc-88
		color_cycle = ['0000db', '00b6db', '00db6d', 'ffb600', 'ff926d', 'db0000', '000000']
	elif name == 'coldwood':
		# https://lospec.com/palette-list/coldwood8
		color_cycle = ['372e4d', '5f699c', '65aed6', 'a4ebcc', 'f0b38d', 'b56d7f', '614363']
	elif name == 'clement-8':
		# https://lospec.com/palette-list/clement-8
		color_cycle = ['000871','8854f3','639bff','63ffba','ff8c5c','ff79ae','fff982']
	elif name == 'sweethope':
		# https://lospec.com/palette-list/sweethope
		color_cycle = ['615e85','9c8dc2','d9a3cd','ebc3a7','e0e0dc','a3d1af','90b4de','717fb0']
	elif name == 'vivid-memory':
		color_cycle = ['381631','e21c61','e26159','fea85f','d8dcb4','5eb6ad','1b958d','105390']
	elif name == 'pastel-qt':
		# https://lospec.com/palette-list/pastel-qt
		color_cycle = ['cb8175', 'e2a97e', 'f0cf8e', 'f6edcd', 'a8c8a6', '6d8d8a', '655057']
	elif name == 'fairydust':
		# https://lospec.com/palette-list/fairydust-8
		color_cycle = ['f0dab1','e39aac','c45d9f','634b7d','6461c2','2ba9b4','93d4b5']
	elif name == 'secam':
		# https://lospec.com/palette-list/secam
		color_cycle = ['000000','2121ff','f03c79','ff50ff','7fff00','7fffff','ffff3f']
	else:
		raise KeyError(
		"pallete '{}' not found. ".format(name) + "Pallete must be one of the following: ['default', 'cga', 'pc-88', 'coldwood', 'clement-8', 'sweethope', 'vivid-memory', 'pastel-qt', 'fairydust' ]")
			
	#Set color cycle
	mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=color_cycle) 

	#Turn cycle into hex color
	out_cycle = ['#'+ color for color in color_cycle]

	return out_cycle
