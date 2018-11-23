## Jay Doherty (jld60)
# Script for modelling Field-Effect Transistors.

# === Imports =======================================
import math
import numpy as np
import scipy.optimize as optimize

# === Lambdas =======================================
exp = lambda x: np.exp(x)
ln = lambda x: np.log(x)
log = lambda x: np.log(x)
log10 = lambda x: np.log10(x)
sqrt = lambda x: np.sqrt(x)
sinh = lambda x: np.sinh(x)
cosh = lambda x: np.cosh(x)
tanh = lambda x: np.tanh(x)
pi = math.pi



# === Constants [with units] ========================
q = 1.602177e-19;       #[C]
k_B_eV = 8.617385e-5;   #[eV/K]
k_B_J = 1.38058e-23;    #[J/K]
h_eV = 4.135669e-15;    #[eV*s]
h_J = 6.626075e-34;     #[J*s]
h_bar_eV = 6.582122e-16;#[eV*s]
h_bar_J = 1.054572e-34; #[J*s]
eps_0 = 8.854187e-14;   #[F/cm]
kB_T = 0.025852;        #[eV]
kB_T_q = 0.025852;      #[V] (T=300K)
beta = 1/kB_T_q;        #[V^-1] (T=300K)
m_0 = 9.109389e-31;     #[kg]

## Silicon Physical Properties
E_gsi = 1.1242;         #[eV] (T=300K)
q_chi_si = 4.050;       #[eV] (T=300K)
N_si = 5e22;            #[cm^-3]
n_i = 1.07e10;          #[cm^-3]
eps_si = 11.7 * eps_0;  #[F/cm]
eps_sio2 = 3.9 * eps_0;   #[F/cm]
N_c = 2.86e19;          #[cm^-3]
N_v = 3.10e19;          #[cm^-3]
t_inv = 45e-8			#[cm] Inversion Layer Thickness (Howard and Stern Nov. 15, 1967)



# === Models ========================================

### MOSFETS ###

# Level 1 SPICE NMOSFET Model
NMOSFET_V_DSat_fn = lambda V_GS, V_TN: (V_GS - V_TN)
NMOSFET_g_m_fn = lambda V_GS, V_DS, V_TN, K_N: ( (K_N*V_DS) if(V_DS < NMOSFET_V_DSat_fn(V_GS, V_TN)) else (K_N)*(V_GS - V_TN) )
NMOSFET_I_D_subth_fn = lambda V_GS, V_DS, V_TN, K_N, SS_mV_dec: ((1.1*K_N) * ((SS_mV_dec/1000)/(ln(10)*kB_T_q) - 1) * ((kB_T_q)**2) * exp((V_GS - V_TN) * ln(10)/(SS_mV_dec/1000)) * (1 - exp(-V_DS/kB_T_q)))
NMOSFET_I_D_lin_fn = lambda V_GS, V_DS, V_TN, K_N: ((K_N)*((V_GS - V_TN)*V_DS - 0.5*(V_DS**2)))
NMOSFET_I_D_sat_fn = lambda V_GS, V_TN, K_N: ((K_N/2)*((V_GS - V_TN)**2))
NMOSFET_I_D_on_fn = lambda V_GS, V_DS, V_TN, K_N: (NMOSFET_I_D_lin_fn(V_GS, V_DS, V_TN, K_N) if (V_DS < NMOSFET_V_DSat_fn(V_GS, V_TN)) else NMOSFET_I_D_sat_fn(V_GS, V_TN, K_N))
NMOSFET_I_D_fn = lambda V_GS, V_DS, V_TN, K_N, SS_mV_dec, I_OFF: (max(NMOSFET_I_D_subth_fn(V_GS, V_DS, V_TN, K_N, SS_mV_dec) if(V_GS < V_TN + 2*(SS_mV_dec/1000)/ln(10)) else NMOSFET_I_D_on_fn(V_GS, V_DS, V_TN, K_N), I_OFF))
#NMOSFET_I_D_ChLenMod_fn = lambda V_GS, V_DS, V_TN, K_N, SS_mV_dec, I_OFF, lambda_N: (NMOSFET_I_D_fn(V_GS, V_DS, V_TN, K_N, SS_mV_dec, I_OFF) * (1 + lambda_N*V_DS))

# Level 1 SPICE PMOSFET Model
PMOSFET_V_DSat_fn = lambda V_GS, V_TP: (V_GS - V_TP)
PMOSFET_g_m_fn = lambda V_GS, V_DS, V_TP, K_P: ( (K_P*V_DS) if(V_DS > PMOSFET_V_DSat_fn(V_GS, V_TP)) else (K_P)*(V_GS - V_TP) )
PMOSFET_I_D_subth_fn = lambda V_GS, V_DS, V_TP, K_P, SS_mV_dec: ((-1.1*K_P) * ((SS_mV_dec/1000)/(ln(10)*kB_T_q) - 1) * ((kB_T_q)**2) * exp(-(V_GS - V_TP) * ln(10)/(SS_mV_dec/1000)) * (1 - exp(-abs(V_DS)/kB_T_q)))
PMOSFET_I_D_lin_fn = lambda V_GS, V_DS, V_TP, K_P: ((-K_P)*((V_GS - V_TP)*V_DS - 0.5*(V_DS**2)))
PMOSFET_I_D_sat_fn = lambda V_GS, V_TP, K_P: ((-K_P/2)*((V_GS - V_TP)**2))
PMOSFET_I_D_on_fn = lambda V_GS, V_DS, V_TP, K_P: (PMOSFET_I_D_lin_fn(V_GS, V_DS, V_TP, K_P) if (V_DS > PMOSFET_V_DSat_fn(V_GS, V_TP)) else PMOSFET_I_D_sat_fn(V_GS, V_TP, K_P))
PMOSFET_I_D_fn = lambda V_GS, V_DS, V_TP, K_P, SS_mV_dec, I_OFF: (min(PMOSFET_I_D_subth_fn(V_GS, V_DS, V_TP, K_P, SS_mV_dec) if(V_GS > V_TP - 2*(SS_mV_dec/1000)/ln(10)) else PMOSFET_I_D_on_fn(V_GS, V_DS, V_TP, K_P), -abs(I_OFF)))
#PMOSFET_I_D_ChLenMod_fn = lambda  V_GS, V_DS, V_TP, K_P, SS_mV_dec, lambda_P: (PMOSFET_I_D_fn(V_GS, V_DS, V_TP, K_P, SS_mV_dec) * (1 + lambda_P*V_DS))



def NMOSFET_Fit(V_GS_data, I_D_data, V_DS, V_TN_guess=0, V_TN_min=-50, V_TN_max=50, I_OFF_guess=100e-12, I_OFF_min=100e-15, I_OFF_max=1e-6):
	# Find steepest region - on a linear and log scale - to estimate K_N and SS respectively
	SS_mV_dec_steepest_region = _max_subthreshold_swing(V_GS_data, I_D_data)
	g_m_steepest_region = _max_transconductance(V_GS_data, I_D_data)
	K_N_steepest_region = g_m_steepest_region/V_DS
			
	# Set initial guess for the model parameters and choose some bounds on min/max values
	initial_fit_conditions = [V_TN_guess, K_N_steepest_region, SS_mV_dec_steepest_region, I_OFF_guess]
	fit_absolute_boundaries = ([V_TN_min, K_N_steepest_region/10, SS_mV_dec_steepest_region/5, I_OFF_min], [V_TN_max, K_N_steepest_region*10, SS_mV_dec_steepest_region*5, I_OFF_max])
					
	# Fit on a linear scale to find V_T and K_N
	NMOSFET_Full_Model_linear = lambda v_gs_data, v_tn, k_n, ss_mv_dec, i_off: [NMOSFET_I_D_fn(v_gs, V_DS, v_tn, k_n, ss_mv_dec, i_off) for v_gs in v_gs_data]
	(V_TN_linear_fitted, K_N_linear_fitted, SS_mV_dec_linear_estimate, I_OFF_linear_estimate), covariance = optimize.curve_fit(NMOSFET_Full_Model_linear, V_GS_data, I_D_data, p0=initial_fit_conditions, bounds=fit_absolute_boundaries)
	linear_fitted_model_parameters = [V_TN_linear_fitted, K_N_linear_fitted, SS_mV_dec_steepest_region, I_OFF_guess]
	
	# Fit on a log scale to find I_OFF and SS
	I_D_data_logarithmic = np.log10(np.abs(np.array(I_D_data)))
	NMOSFET_Full_Model_logarithmic = lambda v_gs_data, v_tn, k_n, ss_mv_dec, i_off: [np.log10(NMOSFET_I_D_fn(v_gs, V_DS, v_tn, k_n, ss_mv_dec, i_off)) for v_gs in v_gs_data]
	(V_TN_log_estimate, K_N_log_estimate, SS_mV_dec_log_fitted, I_OFF_log_fitted), log_covariance = optimize.curve_fit(NMOSFET_Full_Model_logarithmic, V_GS_data, I_D_data_logarithmic, p0=linear_fitted_model_parameters, bounds=fit_absolute_boundaries)
				
	# Compute g_m from K_N and V_T
	NMOSFET_transconductance = [NMOSFET_g_m_fn(v_gs, V_DS, V_TN_linear_fitted, K_N_linear_fitted) for v_gs in V_GS_data]
	g_m_linear_fitted = max(NMOSFET_transconductance)
	
	fitted_model_parameters = [V_TN_linear_fitted, K_N_linear_fitted, SS_mV_dec_log_fitted, I_OFF_log_fitted]
	fitted_model_parameters_kw = {'V_T':V_TN_linear_fitted, 'mu_Cox_W_L':K_N_linear_fitted, 'SS_mV_dec':SS_mV_dec_log_fitted, 'I_OFF':I_OFF_log_fitted, 'g_m_max':g_m_linear_fitted}
	fitted_yvals = [NMOSFET_I_D_fn(vgs, V_DS, *fitted_model_parameters) for vgs in V_GS_data]
	return (fitted_yvals, fitted_model_parameters, fitted_model_parameters_kw, log_covariance)

def PMOSFET_Fit(V_GS_data, I_D_data, V_DS, V_TP_guess=0, V_TP_min=-50, V_TP_max=50, I_OFF_guess=100e-12, I_OFF_min=100e-15, I_OFF_max=1e-6):
	# Find steepest region - on a linear and log scale - to estimate K_N and SS respectively
	SS_mV_dec_steepest_region = _max_subthreshold_swing(V_GS_data, I_D_data)
	g_m_steepest_region = _max_transconductance(V_GS_data, I_D_data)
	K_P_steepest_region = abs(g_m_steepest_region/V_DS)
		
	# Set initial guess for the model parameters and choose some bounds on min/max values
	initial_fit_conditions = [V_TP_guess, K_P_steepest_region, SS_mV_dec_steepest_region, I_OFF_guess]
	fit_absolute_boundaries = ([V_TP_min, K_P_steepest_region/10, SS_mV_dec_steepest_region/5, I_OFF_min], [V_TP_max, K_P_steepest_region*10, SS_mV_dec_steepest_region*5, I_OFF_max])
	
	# Fit on a linear scale to find V_T and K_P
	PMOSFET_Full_Model_linear = lambda v_gs_data, v_tp, k_p, ss_mv_dec, i_off: [PMOSFET_I_D_fn(v_gs, V_DS, v_tp, k_p, ss_mv_dec, i_off) for v_gs in v_gs_data]
	(V_TP_linear_fitted, K_P_linear_fitted, SS_mV_dec_linear_estimate, I_OFF_linear_estimate), covariance = optimize.curve_fit(PMOSFET_Full_Model_linear, V_GS_data, I_D_data, p0=initial_fit_conditions, bounds=fit_absolute_boundaries)
	linear_fitted_model_parameters = [V_TP_linear_fitted, K_P_linear_fitted, SS_mV_dec_steepest_region, I_OFF_guess]
	
	# Fit (absolute value) on a log scale to find I_OFF and SS
	I_D_data_abs_logarithmic = np.log10(abs(np.array(I_D_data)))
	PMOSFET_Full_Model_logarithmic = lambda v_gs_data, v_tp, k_p, ss_mv_dec, i_off: [np.log10(abs(PMOSFET_I_D_fn(v_gs, V_DS, v_tp, k_p, ss_mv_dec, i_off))) for v_gs in v_gs_data]
	(V_TP_log_estimate, K_P_log_estimate, SS_mV_dec_log_fitted, I_OFF_log_fitted), log_covariance = optimize.curve_fit(PMOSFET_Full_Model_logarithmic, V_GS_data, I_D_data_abs_logarithmic, p0=linear_fitted_model_parameters, bounds=fit_absolute_boundaries)
		
	# Compute g_m from K_P
	PMOSFET_transconductance = [PMOSFET_g_m_fn(v_gs, V_DS, V_TP_linear_fitted, K_P_linear_fitted) for v_gs in V_GS_data]
	g_m_linear_fitted = max(PMOSFET_transconductance)
	
	fitted_model_parameters = [V_TP_linear_fitted, K_P_linear_fitted, SS_mV_dec_linear_estimate, I_OFF_log_fitted]
	fitted_model_parameters_kw = {'V_T':V_TP_linear_fitted, 'mu_Cox_W_L':K_P_linear_fitted, 'SS_mV_dec':SS_mV_dec_log_fitted, 'I_OFF':I_OFF_log_fitted, 'g_m_max':g_m_linear_fitted}
	fitted_yvals = [PMOSFET_I_D_fn(vgs, V_DS, *fitted_model_parameters) for vgs in V_GS_data]
	return (fitted_yvals, fitted_model_parameters, fitted_model_parameters_kw, covariance)

def _max_subthreshold_swing(V_GS_data, I_D_data):
	startIndex, endIndex = _find_steepest_region(np.log10(np.abs(I_D_data)), int(len(I_D_data)/10))
	V_GS_steepest_region = V_GS_data[startIndex:endIndex]
	I_D_steepest_region = I_D_data[startIndex:endIndex]
	fitted_steepest_region = _semilogFit(V_GS_steepest_region, I_D_steepest_region)['fitted_data']
	SS_mV_dec = (abs( (V_GS_steepest_region[0] - V_GS_steepest_region[-1]) / (np.log10(np.abs(fitted_steepest_region[0])) - np.log10(np.abs(fitted_steepest_region[-1]))) ) * 1000)
	return SS_mV_dec

def _max_transconductance(V_GS_data, I_D_data):
	startIndex, endIndex = _find_steepest_region(np.abs(I_D_data), int(len(I_D_data)/10))
	V_GS_steepest_region = V_GS_data[startIndex:endIndex]
	I_D_steepest_region = I_D_data[startIndex:endIndex]
	fitted_steepest_region = _semilogFit(V_GS_steepest_region, I_D_steepest_region)['fitted_data']
	g_m_max = abs( (fitted_steepest_region[0] - fitted_steepest_region[-1]) / (V_GS_steepest_region[0] - V_GS_steepest_region[-1]) )  
	return g_m_max

def _find_steepest_region(data, numberOfPoints):
	maxSlope = 0
	index = 0
	for i in range(len(data) - numberOfPoints):
		diff = abs(data[i] - data[i+numberOfPoints])
		if(diff > maxSlope):
			maxSlope = diff
			index = i
	regionStart = max(0, index)
	regionEnd = min(len(data)-1, index + numberOfPoints)
	return (int(regionStart), int(regionEnd))

def _linearFit(x, y):
	slope, intercept = np.polyfit(x, y, 1)
	fitted_data = [slope*x[i] + intercept for i in range(len(x))]
	return {'fitted_data': fitted_data,'slope':slope, 'intercept':intercept}

def _semilogFit(x, y):
	fit_results = _linearFit(x, np.log10(np.abs(y)))
	fitted_data = [10**(fit_results['fitted_data'][i]) for i in range(len(fit_results['fitted_data']))]
	return {'fitted_data': fitted_data}


if __name__ == '__main__':
	import matplotlib as mpl
	from matplotlib import pyplot as plt
	
	fig, ax = plt.subplots(1,1, figsize=(3,3))
	
	V_GS_data = np.linspace(-10, 10, 200)
	V_DS = -1.5
	
	import random
	
	I_D = (np.array([PMOSFET_I_D_fn(vgs, V_DS, -5, 50e-6, 400, 1e-10)*(1+random.random()/2) for vgs in V_GS_data]))
	
	fitted_vals, fitted_model_parameters, fitted_model_parameters_kw, cov = PMOSFET_Fit(V_GS_data, I_D, V_DS)
		
	print(fitted_model_parameters_kw)
	
	ax.plot(V_GS_data, abs(I_D), marker='o', markersize=2, linewidth=1)
	ax.plot(V_GS_data, abs(np.array(fitted_vals)))
	ax.set_ylabel('$I_{{D}}$ ($\\mu A$)')
	ax.set_xlabel('$V_{{GS}}$ ($V$)')
	ax.set_yscale('log')
	plt.show()







