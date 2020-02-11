#! /anaconda3/bin/python

import polariton_processing as pp
import argparse
import csv
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import AutoMinorLocator
from scipy import constants

def get_splitting_results(splitting_file):
	"""These parameters were generated by nonlinear least squares fitting."""
	params = {}
	with open(splitting_file, 'r') as sf:
		csvreader = csv.reader(sf)
		for row in csvreader:
			try:
				params[row[0]] = float(row[1])
			except ValueError:
				params[row[0]] = row[1]
	
	return params

# Unit conversions
def wavenum_to_wavelen(wavenum):
	"""cm^-1 to micrometers"""
	wavelength = 10000 / wavenum
	return wavelength
	
def joules_to_ev(joules):
	ev = joules / constants.elementary_charge
	return ev
	
def wavenum_to_joules(wavenum):
	"""cm^-1 to photon energy"""
	cm_to_m = 1/100
	joules = constants.h * constants.c * (wavenum / cm_to_m)
	return joules

def set_units(unit_data, set_units):
	#TODO: Handle arbitrary units from input data.
	# Assume input unit_data in cm^-1
	cm_to_m = 1/100
	energy = [wavenum_to_joules(d) for d in unit_data]
	energy_to_ev = [joules_to_ev(en) for en in energy]
	wavenumber_to_wavelength = [wavenum_to_wavelen(d) for d in unit_data]

	if set_units == 'ev':
		new_units = energy_to_ev
	elif set_units == 'wn':
		new_units = unit_data
	elif set_units == 'wl':
		new_units = wavenumber_to_wavelength
	return new_units

# Plotting functions

def TRA_plots(inputfile, outputfile):
	wavelength = []
	wavenumber = []
	transmittance = []
	reflectance = []
	absorptance = []
	field = []

	with open(inputfile, 'r') as f:
		reader = csv.reader(f)
		next(reader, None)
		for row in reader:
			wavelength.append(float(row[0]))
			transmittance.append(float(row[1]))
			reflectance.append(float(row[2]))
			absorptance.append(float(row[3]))

	wavenumber = [10**4/wl for wl in wavelength]

	print("Generating plots...")
# 	fig, axs = plt.subplots(3, 1, sharex=True)
	fig, ax = plt.subplots()
	gs1 = gridspec.GridSpec(3, 1)
	gs1.update(wspace=0.025, hspace=0.005)

# 	ax = axs[0]
	ax.plot(wavenumber, transmittance,
			color='b',
			linewidth=0.8,
			label="transfer matrix")
	if args.transmission:
		ax.plot(wl_T_data, T_data, linestyle="dashed", color='#FF5733', label="downloaded data")
	ax.set_ylabel('Transmittance %', fontsize=12)
	ax.set_xlabel(r'Wavenumber (cm$^{-1}$)', fontsize=12)
	ax.tick_params(axis='both', labelsize=12)
	ax.set_xlim(2300, 1600)
	ax.set_ylim(0.0, 0.06)
	ax.axvline(2173, color='r', linestyle='dashed')
# 	ax.xaxis.set_ticks(np.arange(2500, 1000, 5))


# 	ax = axs[1]
# 	ax.plot(wavelength, reflectance,
# 			color='b',
# 			linewidth=0.8,
# 			label="transfer matrix")
# 	if args.reflection:
# 		ax.plot(wl_R_data, R_data, linestyle="dashed", color='#FF5733', label="downloaded data")
# 	ax.set_ylabel('Reflectance %', fontsize=12)
# 
# 
# 	ax = axs[2]
# 	ax.plot(wavelength, absorptance,
# 			color='b',
# 			linewidth=0.8,
# 			label="transfer matrix")
# 	if args.absorbance:
# 		ax.plot(wl_A_data, A_data, linestyle="dashed", color="#FF5733", label="downloaded data")
# 	ax.set_ylabel('Absorptance %', fontsize=12)
# 	ax.set_xlabel('Wavelength ($\mu$m)', fontsize=12)
	

	title = "Transfer Matrix Method"
	plt.suptitle(title, fontsize=18)
	plt.subplots_adjust(top=0.9)
# 	plt.tight_layout()

	if args.savedir:
		print("Saving figure as pdf")
		file_name = outputfile
# 		output_file = os.path.join(args.savedir, outputfile)
		fig.savefig(outputfile, bbox_inches='tight')

	else:
		plt.show()


def reference_data(data_file):
	"""Gets reference data downloaded from
	websites. Filmetrics.com data are in nanometers"""
	wavelength = []
	Y = []
	unit = 1  # sets order of magnitude (nm or um)
	with open(data_file, 'r') as ref:
	
		reader = None
		if 'filmetrics' in str(ref):
			print('Filmetrics data. Units in nm')
			unit = 10**-3
			reader = csv.reader(ref, delimiter="\t")
		else:
			print("Refractiveindex.info data. Units in um")
			reader = csv.reader(ref)
		next(reader, None)  # Skip header
		for row in reader:
			wl = float(row[0]) * unit  # MAKE SURE UNITS ARE CORRECT
			wavelength.append(wl)
			Y.append(float(row[1]))
	return wavelength, Y


# ====== Plot Polariton Data and Dispersion Curves ====== #

def plot_spectra(file_prefix, spectra_file, excitation=None):
	"""Takes csv file with spectral data produced by
	   write_angle_spec_to_file or write_dispersion_to_file functions in
	   polariton_processing module"""
	
	wavenumbers = []
	intensities = []
	angles = []

	with open(spectra_file) as sfile:
		csvreader = csv.reader(sfile)
		header = next(csvreader)
		deg_str = 'deg'
		
		for deg in header[1:]:
			ang_start = deg.find(deg_str) + len(deg_str)
			ang_end = deg.find(' ', ang_start)
			ang = int(deg[ang_start:ang_end])
			angles.append(ang)
			intensities.append([ang, []])

		for row in csvreader:
			wavenumbers.append(float(row[0]))
			
			inten_data = row[1:]
			for idx, a in enumerate(intensities):
				a[1].append(float(inten_data[idx]))

	fig, ax = plt.subplots()
	
	y_offset = 0.
	i = len(angles) - 1
	while i >= 0:

		y_vals = intensities[i][1]
		y_vals = [y+y_offset for y in y_vals]

		deg_label = str(angles[i])
		ax.plot(wavenumbers, y_vals,
				color='black',
				linewidth=0.5,
				label=deg_label)
		y_offset += 0.25
		i-=1
		
	if excitation:
		ax.axvline(x=excitation)
	
	#TODO: Don't hard code these labels or xlim, ylim.
	xy_pt1 = (2350, 0.09)
	xy_pt2 = (2350, 2.7)
	theta1 = str(angles[0])
	theta2 = str(angles[-1])

	ax.annotate(r'$\theta$ = {}$\degree$'.format(theta1), xy=xy_pt1)
	ax.annotate(r'$\theta$ = {}$\degree$'.format(theta2), xy=xy_pt2)
	ax.set_xlim([2000, 2400])
	ax.set_ylim([0, 4])
	
	ax.set_xlabel(r'Wavenumber (cm$^{-1}$)')
	ax.set_ylabel('Transmission %')

	if args.savedir:
		file_name = file_prefix + '_cascade_plot.pdf'
		output_file = os.path.join(args.savedir, file_name)
		fig.savefig(output_file, bbox_inches='tight')
		print("Saved cascade plot to {}".format(output_file))
	else:
		plt.show()
	
	return 0
	

def plot_dispersion(file_prefix, dispersion_file):
	"""Takes dispersion curve file and plots wavenumber vs angle
	   for UP, LP, vibration mode, cavity mode"""
	
	UNIT = args.units[0]
	
	if UNIT.lower() == 'ev':
		ylabel = 'Energy (eV)'
		unit_str = 'eV'
	elif UNIT.lower() == 'wl':
		ylabel = r'Wavelength ($\mu$m)'
		unit_str = 'wavelength'
	elif UNIT.lower() == 'wn':
		ylabel = r'Wavenumber (cm$^{-1}$)'
		unit_str = 'wavenumber'

	
	angles = []
	up = []
	lp = []
	vibration = []
	cavity = []
	
	with open(dispersion_file, 'r') as dfile:
		csvreader = csv.reader(dfile)
		next(csvreader)
		for row in csvreader:
			angles.append(int(row[0]))
			up.append(float(row[1]))
			lp.append(float(row[2]))
			vibration.append(float(row[3]))
			cavity.append(float(row[4]))

	up = set_units(up, UNIT)
	lp = set_units(lp, UNIT)
	cavity = set_units(cavity, UNIT)
	vibration = set_units(vibration, UNIT)

	fig, ax = plt.subplots()

	mark_size = 10
	color1 = 'dimgray'
	color2 = 'black'
	color3 = 'navy'
	
	vib_label = 'molecular stretch'
	vib_xy = (0.89, vibration[0])
		
	cav_label = 'cavity dispersion'
	cav_xy = (0.89, cavity[-1])

	# Generate theoretical data
	n_points = 100
	t_min = -35
	t_max = 35
	theta_plot = np.linspace(t_min, t_max, n_points)
	theta_rad = [a * np.pi/180 for a in theta_plot]
	
	# Nonlinear least squares results labeling
	if args.splitting_results:
		
		# Get fitting params from text file and convert units
		params = get_splitting_results(args.splitting_results)
		E_cav0 = params['E_cav_0']
		n_eff = params['n']
		Rabi = params['Rabi']
		E_vib = params['E_vib']
		E_cav0, E_vib, Rabi = set_units([E_cav0, E_vib, Rabi], UNIT)
		
		# Generate curve from fitting data
		Ec = pp.cavity_mode_energy(theta_rad, E_cav0, n_eff)
		E_lp = pp.coupled_energies(theta_rad, E_cav0, E_vib, Rabi, n_eff, 0)
		E_up = pp.coupled_energies(theta_rad, E_cav0, E_vib, Rabi, n_eff, 1)

		e_vib_plot = np.full((n_points, ), E_vib)
		ax.plot(theta_plot, Ec, color=color2)
		ax.plot(theta_plot, E_up, color=color2)
		ax.plot(theta_plot, E_lp, color=color2)
		ax.plot(theta_plot, e_vib_plot, linestyle='dashed', color=color2)
		
		textstr = '\n'.join((
				  'Least Squares Fit',
				   r'$\Omega_R = %.5f$' % (Rabi),
				   r'$E_{cav,0} = %.4f$' % (E_cav0),
				   r'$E_{vib} = %.4f$' % (E_vib),
				   r'$n = %.3f$' % (n_eff)))
		if not args.savedir:
			ax.text(0.45, 1.0, textstr, fontsize=10,
					horizontalalignment='left', verticalalignment='top',
					transform=ax.transAxes,
					bbox=dict(boxstyle='square', facecolor='white'))
	else:
		vibration = np.full((n_points, ), vibration[0])
		ax.plot(theta_plot, vibration,
			linestyle='dashed',
			color=color1,
			label=vib_label)

	#Plot experimental data
	ax.scatter(angles, up, s=mark_size, color=color3)
	ax.scatter(angles, lp, s=mark_size, color=color3)

	# Figure formatting
	ax.tick_params(axis='both', which='both', direction='in')
	angle_ticks = [-30, -20, -10, 0, 10, 20, 30]
	ax.set_xticks(angle_ticks, minor=True)
	ax.xaxis.set_minor_locator(AutoMinorLocator(5))
	ax.yaxis.set_minor_locator(AutoMinorLocator(5))
	ax.set_xlabel(r'Incident angle (deg)')
	ax.set_ylabel(ylabel)

	# Some settings for saving to PDF
	if args.savedir:
		ax.text(1.01, 0.5, textstr, fontsize=10,
				horizontalalignment='left', verticalalignment='top',
				transform=ax.transAxes,
				bbox=dict(boxstyle='square', facecolor='white'))
		file_name = file_prefix + '_dispersion_curve.pdf'
		output_file = os.path.join(args.savedir, file_name)
		print(output_file)
		fig.savefig(output_file, bbox_inches='tight')
		print("Saved dispersion plot to {}".format(output_file))
	else:
		plt.show()
	
	return 0


def main():

	if args.simulation:
		TRA_plots(args.simulation, args.savedir)
# 	field_profile_data = sys.argv[2]

	if args.dispersion:
		#TODO: Use parameter strings to title plots
		dispersion_data = args.dispersion
		sample_name, params = pp.get_sample_params(dispersion_data)
		file_prefix = params[0] + '_' + params[1]
		plot_dispersion(file_prefix, dispersion_data)

	if args.angle:
		angle_data = args.angle
		sample_name, params = pp.get_sample_params(angle_data)
		
		file_prefix = params[0] + '_' + params[1]
		
# 		plot_spectra(file_prefix, angle_data, excitation=2171)
		plot_spectra(file_prefix, angle_data)
	
	
	# ===== Plotting FTIR data ===== #
# 	x_file = "/Users/garrek/Desktop/fpi0xwave.txt"
# 	y_file = "/Users/garrek/Desktop/trans0.txt"
# 	x_data = []
# 	y_data = []
# 	
# 	with open(x_file, 'r') as xf:
# 		lines = xf.readlines()
# 		for line in lines:
# 			x_data.append(float(line))
# 	with open(y_file, 'r') as yf:
# 		lines = yf.readlines()
# 		for line in lines:
# 			y_data.append(float(line))
# ============================== #


if __name__ == "__main__":
	
	#TODO: Make flag to toggle powerpoint and paper font settings
	parser = argparse.ArgumentParser()
	
	simulation_help = "Input file from transfer_matrix.py with transmittance, \
					   reflectance, absorptance data \
					   (not necessarily all three)."
	reference_help = "Input file from reference data (filmetrics, refractiveindex, etc.)"
	reflectance_help = "For testing: path for reflectance data downloaded from filmetrics."
	transmittance_help = "For testing: path for transmittance data downloaded from filmetrics"
	absorptance_help = "For testing: path for absorptance data downloaded from filmetrics"
	dispersion_help = "Plot dispersion curves from experimental angle-tuned data. \
					   Input path to dispersion data from polariton fitting."
	angle_help = "Plot cascading angle-tuned data on a single axis. \
						   Input path to angle-tuned data for a given sample concentration."
	splitting_help = "Results of nonlinear least squares to label dispersion plot. \
					  Input path to splitting data from polariton fitting."
	save_help = "Saves plot to a pdf instead of sending to the python viewer. \
				 Requires output path."
	units_help = "Sets the units for plotting. Valid units are: \
				  ev (eV), wn (wavenumber cm-1), wl (wavelength um)"


	parser.add_argument('-SIM', '--simulation', help=simulation_help)
	parser.add_argument('-T', '--transmission',help=transmittance_help)
	parser.add_argument('-R', '--reflection',help=reflectance_help)
	parser.add_argument('-A', '--absorbance', help=absorptance_help)
	parser.add_argument('-D', '--dispersion', help=dispersion_help)
	parser.add_argument('-ANG', '--angle', help=angle_help)
	parser.add_argument('-S', '--savedir', help=save_help)
	parser.add_argument('-SP', '--splitting_results', help=splitting_help)
	parser.add_argument('units', type=str, nargs='*', help=units_help)
	
	args = parser.parse_args()

	if args.transmission:
		print("Using transmission reference data.")
		wl_T_data, T_data = reference_data(args.transmission)
	if args.reflection:
		print("Using reflection reference data.")
		wl_R_data, R_data = reference_data(args.reflection)
	if args.absorbance:
		print("Using absorbance reference data.")
		wl_A_data, A_data = reference_data(args.absorbance)

	main()

