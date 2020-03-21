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
NMOSFET_body_factor_fn = lambda SS_mV_dec: ((SS_mV_dec/1000)/(ln(10)*kB_T_q))
NMOSFET_I_D0_fn = lambda K_N, SS_mV_dec: (10 * (K_N) * sqrt(SS_mV_dec/1000)*(NMOSFET_body_factor_fn(SS_mV_dec)-1) * ((kB_T_q)**2))		# Cannonical: ((K_N) * ((SS_mV_dec/1000)/(ln(10)*kB_T_q) - 1) * ((kB_T_q)**2))
NMOSFET_I_D_subth_fn = lambda V_GS, V_DS, V_TN, K_N, SS_mV_dec: (NMOSFET_I_D0_fn(K_N, SS_mV_dec) * exp((V_GS - V_TN) * ln(10)/(SS_mV_dec/1000)) * (1 - exp(-V_DS/kB_T_q)))
NMOSFET_I_D_lin_fn = lambda V_GS, V_DS, V_TN, K_N: ((K_N)*((V_GS - V_TN)*V_DS - 0.5*(V_DS**2)))
NMOSFET_I_D_sat_fn = lambda V_GS, V_TN, K_N: ((K_N/2)*((V_GS - V_TN)**2))
NMOSFET_I_D_on_fn = lambda V_GS, V_DS, V_TN, K_N: (NMOSFET_I_D_lin_fn(V_GS, V_DS, V_TN, K_N) if (V_DS < NMOSFET_V_DSat_fn(V_GS, V_TN)) else NMOSFET_I_D_sat_fn(V_GS, V_TN, K_N))
NMOSFET_I_D_intermed_fn = lambda V_GS, V_DS, V_TN, K_N, SS_mV_dec, smooth_over: (((exp(-(V_GS-V_TN)/(smooth_over*SS_mV_dec/1000)))*NMOSFET_I_D_subth_fn(V_GS, V_DS, V_TN, K_N, SS_mV_dec) + (1-exp(-(V_GS-V_TN)/(smooth_over*SS_mV_dec/1000)))*(NMOSFET_I_D_subth_fn(0, V_DS, 0, K_N, SS_mV_dec) + NMOSFET_I_D_on_fn(V_GS, V_DS, V_TN, K_N))) if(smooth_over > 0) else (NMOSFET_I_D_subth_fn(0, V_DS, 0, K_N, SS_mV_dec)))
NMOSFET_I_D_fn = lambda V_GS, V_DS, V_TN, K_N, SS_mV_dec, I_OFF, smooth_over=0.5: (max(NMOSFET_I_D_subth_fn(V_GS, V_DS, V_TN, K_N, SS_mV_dec) if(V_GS < V_TN) else ((NMOSFET_I_D_intermed_fn(V_GS, V_DS, V_TN, K_N, SS_mV_dec, smooth_over=smooth_over)) if(V_GS < V_TN + smooth_over*SS_mV_dec/1000) else((NMOSFET_I_D_intermed_fn(V_TN + smooth_over*SS_mV_dec/1000, V_DS, V_TN, K_N, SS_mV_dec, smooth_over=smooth_over) - NMOSFET_I_D_on_fn(V_TN + smooth_over*SS_mV_dec/1000, V_DS, V_TN, K_N)) + NMOSFET_I_D_on_fn(V_GS, V_DS, V_TN, K_N))), I_OFF))
#NMOSFET_I_D_ChLenMod_fn = lambda V_GS, V_DS, V_TN, K_N, SS_mV_dec, I_OFF, lambda_N: (NMOSFET_I_D_fn(V_GS, V_DS, V_TN, K_N, SS_mV_dec, I_OFF) * (1 + lambda_N*V_DS))
NMOSFET_TransferCurve_fn = lambda V_GS_list, V_DS, V_TN, K_N, SS_mV_dec, I_OFF: ([NMOSFET_I_D_fn(vgs, V_DS, V_TN, K_N, SS_mV_dec, I_OFF) for vgs in V_GS_list])
NMOSFET_OutputCurve_fn   = lambda V_GS, V_DS_list, V_TN, K_N, SS_mV_dec, I_OFF: ([NMOSFET_I_D_fn(V_GS, vds, V_TN, K_N, SS_mV_dec, I_OFF) for vds in V_DS_list])


# Level 1 SPICE PMOSFET Model
PMOSFET_V_DSat_fn = lambda V_GS, V_TP: (V_GS - V_TP)
PMOSFET_g_m_fn = lambda V_GS, V_DS, V_TP, K_P: ( (K_P*V_DS) if(V_DS > PMOSFET_V_DSat_fn(V_GS, V_TP)) else (K_P)*(V_GS - V_TP) )
PMOSFET_body_factor_fn = lambda SS_mV_dec: ((SS_mV_dec/1000)/(ln(10)*kB_T_q))
PMOSFET_I_D0_fn = lambda K_P, SS_mV_dec: (10 * (K_P) * sqrt(SS_mV_dec/1000)*(PMOSFET_body_factor_fn(SS_mV_dec)-1) * ((kB_T_q)**2))		# Cannonical: ((K_P) * ((SS_mV_dec/1000)/(ln(10)*kB_T_q) - 1) * ((kB_T_q)**2))
PMOSFET_I_D_subth_fn = lambda V_GS, V_DS, V_TP, K_P, SS_mV_dec: (-PMOSFET_I_D0_fn(K_P, SS_mV_dec) * exp(-(V_GS - V_TP) * ln(10)/(SS_mV_dec/1000)) * (1 - exp(-abs(V_DS)/kB_T_q)))
PMOSFET_I_D_lin_fn = lambda V_GS, V_DS, V_TP, K_P: ((-K_P)*((V_GS - V_TP)*V_DS - 0.5*(V_DS**2)))
PMOSFET_I_D_sat_fn = lambda V_GS, V_TP, K_P: ((-K_P/2)*((V_GS - V_TP)**2))
PMOSFET_I_D_on_fn = lambda V_GS, V_DS, V_TP, K_P: (PMOSFET_I_D_lin_fn(V_GS, V_DS, V_TP, K_P) if (V_DS > PMOSFET_V_DSat_fn(V_GS, V_TP)) else PMOSFET_I_D_sat_fn(V_GS, V_TP, K_P))
PMOSFET_I_D_intermed_fn = lambda V_GS, V_DS, V_TP, K_P, SS_mV_dec, smooth_over: (((exp((V_GS-V_TP)/(smooth_over*SS_mV_dec/1000)))*PMOSFET_I_D_subth_fn(V_GS, V_DS, V_TP, K_P, SS_mV_dec) + (1-exp((V_GS-V_TP)/(smooth_over*SS_mV_dec/1000)))*(PMOSFET_I_D_subth_fn(0, V_DS, 0, K_P, SS_mV_dec) + PMOSFET_I_D_on_fn(V_GS, V_DS, V_TP, K_P))) if(smooth_over > 0) else (NMOSFET_I_D_subth_fn(0, V_DS, 0, K_N, SS_mV_dec)))
PMOSFET_I_D_fn = lambda V_GS, V_DS, V_TP, K_P, SS_mV_dec, I_OFF, smooth_over=0.5: (min(PMOSFET_I_D_subth_fn(V_GS, V_DS, V_TP, K_P, SS_mV_dec) if(V_GS > V_TP) else ((PMOSFET_I_D_intermed_fn(V_GS, V_DS, V_TP, K_P, SS_mV_dec, smooth_over=smooth_over)) if(V_GS > V_TP - smooth_over*SS_mV_dec/1000) else((PMOSFET_I_D_intermed_fn(V_TP - smooth_over*SS_mV_dec/1000, V_DS, V_TP, K_P, SS_mV_dec, smooth_over=smooth_over) - PMOSFET_I_D_on_fn(V_TP - smooth_over*SS_mV_dec/1000, V_DS, V_TP, K_P)) + PMOSFET_I_D_on_fn(V_GS, V_DS, V_TP, K_P))), -abs(I_OFF)))
#PMOSFET_I_D_ChLenMod_fn = lambda  V_GS, V_DS, V_TP, K_P, SS_mV_dec, lambda_P: (PMOSFET_I_D_fn(V_GS, V_DS, V_TP, K_P, SS_mV_dec) * (1 + lambda_P*V_DS))
PMOSFET_TransferCurve_fn = lambda V_GS_list, V_DS, V_TP, K_P, SS_mV_dec, I_OFF: ([PMOSFET_I_D_fn(vgs, V_DS, V_TP, K_P, SS_mV_dec, I_OFF) for vgs in V_GS_list])
PMOSFET_OutputCurve_fn   = lambda V_GS, V_DS_list, V_TP, K_P, SS_mV_dec, I_OFF: ([PMOSFET_I_D_fn(V_GS, vds, V_TP, K_P, SS_mV_dec, I_OFF) for vds in V_DS_list])

fet_mobility_fn = lambda g_m_max, V_DS, C_ox, W_ch, L_ch: (g_m_max/(C_ox * W_ch/L_ch * V_DS))

# ===================================================



# === Metrics ===
# Fast metric extraction from simple linear fits in the linear and subthreshold regions
def FET_Metrics_Multiple(V_GS_data_list, I_D_data_list, gm_region_length_override=None, ss_region_length_override=None, extraction_mode_VT=None):
	metrics = [FET_Metrics(V_GS_data_list[i], I_D_data_list[i], gm_region_length_override=gm_region_length_override, ss_region_length_override=ss_region_length_override, extraction_mode_VT=extraction_mode_VT) for i in range(len(V_GS_data_list))]
	V_T_list = [entry['V_T'] for entry in metrics]
	g_m_list = [entry['g_m_max'] for entry in metrics]
	SS_mV_dec_list = [entry['SS_mV_dec'] for entry in metrics]
	return {'V_T':V_T_list, 'g_m_max':g_m_list, 'SS_mV_dec':SS_mV_dec_list, 'metrics_all':metrics}

def FET_Metrics(V_GS_data, I_D_data, gm_region_length_override=None, ss_region_length_override=None, extraction_mode_VT=None):
	# Find steepest region metrics
	SS_mV_dec_steepest_region, log_steepest_region = _max_subthreshold_swing(V_GS_data, I_D_data, ss_region_length_override)
	g_m_steepest_region, V_T_steepest_region, linear_steepest_region = _max_transconductance(V_GS_data, I_D_data, gm_region_length_override, includedFittedData=False)
	if(isinstance(extraction_mode_VT, list) and (extraction_mode_VT[0] == 'byDrainCurrent')):
		drainCurrentValue = extraction_mode_VT[1] if((len(extraction_mode_VT) > 1) and (extraction_mode_VT[1] is not None)) else (I_D_data[int((_find_steepest_region(V_GS_data, I_D_data, None)[0] + _find_steepest_region(V_GS_data, I_D_data, None)[1])/2)])
		V_T_by_drain_current = _getXValueAtYValue(V_GS_data, I_D_data, y_value=drainCurrentValue)
		return {'V_T':V_T_by_drain_current, 'g_m_max':g_m_steepest_region, 'SS_mV_dec':SS_mV_dec_steepest_region}
	return {'V_T':V_T_steepest_region, 'g_m_max':g_m_steepest_region, 'SS_mV_dec':SS_mV_dec_steepest_region}

def FET_Hysteresis(V_GS_data1, I_D_data1, V_GS_data2, I_D_data2, trim_ends=5, max_percentile=99, min_percentile=5, noise_floor=1e-12):
	# Get the upper and lower limits of the range of current values to consider
	I_D_data1_min, I_D_data1_max, I_D_data2_min, I_D_data2_max = np.percentile(I_D_data1, 5), np.percentile(I_D_data1, 99), np.percentile(I_D_data2, 5), np.percentile(I_D_data2, 99)
	I_D_data1_min = max(noise_floor, abs(I_D_data1_min)) * ((-1) if(I_D_data1_min < 0) else (1))
	I_D_data2_min = max(noise_floor, abs(I_D_data2_min)) * ((-1) if(I_D_data2_min < 0) else (1))
				
	# Obtain the list of drain currents (and relevant gate voltages) that exist in both I_D_data1 and I_D_data2
	index_fwd_extraction_points = [i for i in range(trim_ends, len(I_D_data1) - trim_ends) if(I_D_data1[i] > I_D_data2_min and I_D_data1[i] < I_D_data2_max)]
	index_rev_extraction_points = [i for i in range(trim_ends, len(I_D_data2) - trim_ends) if(I_D_data2[i] > I_D_data1_min and I_D_data2[i] < I_D_data1_max)]
	I_D_data1_extraction_points  = [ I_D_data1[i] for i in index_fwd_extraction_points]
	V_GS_data1_extraction_points = [V_GS_data1[i] for i in index_fwd_extraction_points]
	I_D_data2_extraction_points  = [ I_D_data2[i] for i in index_rev_extraction_points]
	V_GS_data2_extraction_points = [V_GS_data2[i] for i in index_rev_extraction_points]
		
	# Extract hysteresis for points from I_D_data1 and I_D_data2 and remove points where extraction failed
	hysteresis_data1 = [FET_Hysteresis_Value(V_GS_data1, I_D_data1, V_GS_data2, I_D_data2, id_val) for id_val in I_D_data1_extraction_points]
	hysteresis_data2 = [FET_Hysteresis_Value(V_GS_data1, I_D_data1, V_GS_data2, I_D_data2, id_val) for id_val in I_D_data2_extraction_points]
	V_GS_data1_extraction_points = [V_GS_data1_extraction_points[i] for i in range(len(V_GS_data1_extraction_points)) if((hysteresis_data1[i] is not None))]
	V_GS_data2_extraction_points = [V_GS_data2_extraction_points[i] for i in range(len(V_GS_data2_extraction_points)) if((hysteresis_data2[i] is not None))]
	hysteresis_data1    		 = [hysteresis_data1[i]				for i in range(len(hysteresis_data1))			  if((hysteresis_data1[i] is not None))]
	hysteresis_data2			 = [hysteresis_data2[i] 			for i in range(len(hysteresis_data2)) 			  if((hysteresis_data2[i] is not None))]

	# Use linear interpolation to make both sets of hysteresis data have as many of the same V_GS values as possible
	V_GS_hysteresis_data1, hysteresis_data1 = _includeAdditionalXValues(V_GS_data1_extraction_points, hysteresis_data1, V_GS_data2_extraction_points)
	V_GS_hysteresis_data2, hysteresis_data2 = _includeAdditionalXValues(V_GS_data2_extraction_points, hysteresis_data2, V_GS_data1_extraction_points)
	
	# Combine into a single list of points and sort by V_GS
	V_GS_combined = V_GS_hysteresis_data1 + V_GS_hysteresis_data2
	hysteresis_combined = hysteresis_data1 + hysteresis_data2
	V_GS_combined, hysteresis_combined = zip(*sorted(zip(V_GS_combined, hysteresis_combined)))
	
	# Take final Hysteresis to be average of the two different extraction techniques (forward-sweep-mapped-to-reverse-sweep averaged w/ reverse-sweep-mapped-to-forward-sweep)
	V_GS_hysteresis, hysteresis = _averageDuplicateX(V_GS_combined, hysteresis_combined, removePointsThatDoNotHaveDuplicate=True)
		
	return {'V_GS':V_GS_hysteresis, 'H':hysteresis}

def FET_Hysteresis_Value(V_GS_data1, I_D_data1, V_GS_data2, I_D_data2, I_D_extraction_point):
	try:
		V_GS1 = _getXValueAtYValue(V_GS_data1, I_D_data1, I_D_extraction_point)
		index_VGS1 = _indexOfValue(V_GS_data1, V_GS1) 
		V_GS2 = _getXValueAtYValue(V_GS_data2, I_D_data2, I_D_extraction_point, index_guess=len(V_GS_data2) - index_VGS1) # if V_GS1 near start of of V_GS_data1, then guess near the end of V_GS_data2 since everything is flipped between the forward/reverse
		return abs(V_GS1 - V_GS2)
	except:
		return None
	
def FET_Gate_Voltage_From_Current(V_GS_reference_data, I_D_reference_data, I_D_value):
	return _getXValueAtYValue(V_GS_reference_data, I_D_reference_data, I_D_value)
## ===============


	
## === Fitting ===
# Condition for classifying data belonging to NMOS or PMOS transistors
def FET_Type(V_GS_data, I_D_data):
	if((V_GS_data[0] < V_GS_data[-1]) and abs(I_D_data[0]) > abs(I_D_data[-1]) or (V_GS_data[0] > V_GS_data[-1]) and (abs(I_D_data[0]) < abs(I_D_data[-1]))):
		return 'PMOS'
	else:
		return 'NMOS'

# Generic fit function for NMOSFET and PMOSFET
def FET_Fit(V_GS_data, I_D_data, V_DS, I_OFF_guess=100e-12, gm_region_length_override=None, ss_region_length_override=None):
	if(FET_Type(V_GS_data, I_D_data) == 'PMOS'):
		print('Fitting to PMOSFET Model.')
		return PMOSFET_Fit(V_GS_data, -abs(np.array(I_D_data)), -abs(V_DS), I_OFF_guess=abs(I_OFF_guess), I_OFF_min=abs(I_OFF_guess)/2, I_OFF_max=abs(I_OFF_guess)*2, gm_region_length_override=gm_region_length_override, ss_region_length_override=ss_region_length_override)
	else:
		print('Fitting to NMOSFET Model.')
		return NMOSFET_Fit(V_GS_data,  abs(np.array(I_D_data)),  abs(V_DS), I_OFF_guess=abs(I_OFF_guess), I_OFF_min=abs(I_OFF_guess)/2, I_OFF_max=abs(I_OFF_guess)*2, gm_region_length_override=gm_region_length_override, ss_region_length_override=ss_region_length_override)

def NMOSFET_Fit(V_GS_data, I_D_data, V_DS, V_TN_guess=0, V_TN_min=-100, V_TN_max=100, I_OFF_guess=100e-12, I_OFF_min=100e-15, I_OFF_max=1e-6, gm_region_length_override=None, ss_region_length_override=None):
	# Find steepest region - on a linear and log scale - to estimate K_N and SS respectively
	SS_mV_dec_steepest_region, log_steepest_region = _max_subthreshold_swing(V_GS_data, I_D_data, ss_region_length_override)
	g_m_steepest_region, V_TN_steepest_region, linear_steepest_region = _max_transconductance(V_GS_data, I_D_data, gm_region_length_override, includedFittedData=True)
	K_N_steepest_region = abs(g_m_steepest_region/V_DS)
			
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
	
	# From the large collection of parameters fitted, choose the ones that best approximate the real data
	fitted_model_parameters = [V_TN_steepest_region, K_N_steepest_region, SS_mV_dec_steepest_region, I_OFF_log_fitted]
	fitted_model_parameters_kw = {'V_T':V_TN_steepest_region, 'mu_Cox_W_L':K_N_steepest_region, 'SS_mV_dec':SS_mV_dec_steepest_region, 'I_OFF':I_OFF_log_fitted, 'g_m_max':g_m_steepest_region}
	fitted_yvals = [NMOSFET_I_D_fn(vgs, V_DS, *fitted_model_parameters) for vgs in V_GS_data]
	return (fitted_yvals, fitted_model_parameters, fitted_model_parameters_kw)

def PMOSFET_Fit(V_GS_data, I_D_data, V_DS, V_TP_guess=0, V_TP_min=-100, V_TP_max=100, I_OFF_guess=100e-12, I_OFF_min=100e-15, I_OFF_max=1e-6, gm_region_length_override=None, ss_region_length_override=None):
	# Find steepest region - on a linear and log scale - to estimate K_N and SS respectively
	SS_mV_dec_steepest_region, log_steepest_region = _max_subthreshold_swing(V_GS_data, I_D_data, ss_region_length_override)
	g_m_steepest_region, V_TP_steepest_region, linear_steepest_region = _max_transconductance(V_GS_data, I_D_data, gm_region_length_override, includedFittedData=True)
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
	
	# From the large collection of parameters fitted, choose the ones that best approximate the real data
	fitted_model_parameters = [V_TP_steepest_region, K_P_steepest_region, SS_mV_dec_steepest_region, I_OFF_log_fitted]
	fitted_model_parameters_kw = {'V_T':V_TP_steepest_region, 'mu_Cox_W_L':K_P_steepest_region, 'SS_mV_dec':SS_mV_dec_steepest_region, 'I_OFF':I_OFF_log_fitted, 'g_m_max':g_m_steepest_region}
	fitted_yvals = [PMOSFET_I_D_fn(vgs, V_DS, *fitted_model_parameters) for vgs in V_GS_data]
	return (fitted_yvals, fitted_model_parameters, fitted_model_parameters_kw)

# Simple model for a MOSFET with metrics that match the given data
def FET_Fit_Simple(V_GS_data, I_D_data, V_DS, I_OFF_guess=100e-12, gm_region_length_override=None, ss_region_length_override=None):
	metrics = FET_Metrics(V_GS_data, I_D_data, gm_region_length_override=gm_region_length_override, ss_region_length_override=gm_region_length_override)
	
	V_T = metrics['V_T']
	gm = metrics['g_m_max']
	SS_mV_dec = metrics['SS_mV_dec']
	K = abs(gm/V_DS)
	
	if(FET_Type(V_GS_data, I_D_data) == 'PMOS'):
		print('Fitting to PMOSFET Model.')
		return PMOSFET_TransferCurve_fn(V_GS_data, -abs(V_DS), V_T, K, SS_mV_dec, I_OFF_guess)
	else:
		print('Fitting to NMOSFET Model.')
		return NMOSFET_TransferCurve_fn(V_GS_data, abs(V_DS), V_T, K, SS_mV_dec, I_OFF_guess)
	
## ================



## === Internal ===
def _max_subthreshold_swing(V_GS_data, I_D_data, region_length_override=None):
	region_length = int(3 + 2*int(len(I_D_data)/20)) if(region_length_override is None) else (region_length_override)
	#print('SS region length: ' + str(region_length))
	startIndex, endIndex = _find_steepest_region(V_GS_data, np.log10(np.abs(I_D_data)), region_length)
	V_GS_steepest_region = V_GS_data[startIndex:endIndex+1]
	I_D_steepest_region = I_D_data[startIndex:endIndex+1]
	fitted_steepest_region = _semilogFit(V_GS_steepest_region, I_D_steepest_region)['fitted_data']
	SS_mV_dec = (abs( (V_GS_steepest_region[0] - V_GS_steepest_region[-1]) / (np.log10(np.abs(fitted_steepest_region[0])) - np.log10(np.abs(fitted_steepest_region[-1]))) ) * 1000)
	return SS_mV_dec, (V_GS_steepest_region, fitted_steepest_region)

def _max_transconductance(V_GS_data, I_D_data, region_length_override=None, includedFittedData=True):
	region_length = int(3 + 2*int(len(I_D_data)/20)) if(region_length_override is None) else (region_length_override)
	#print('gm region length: ' + str(region_length))
	startIndex, endIndex = _find_steepest_region(V_GS_data, np.abs(I_D_data), region_length)
	V_GS_steepest_region = V_GS_data[startIndex:endIndex+1]
	I_D_steepest_region = I_D_data[startIndex:endIndex+1]
	fit = _linearFit(V_GS_steepest_region, I_D_steepest_region, includedFittedData=includedFittedData)
	fitted_steepest_region = fit['fitted_data']
	V_T_approx = fit['x_intercept']
	g_m_max = abs( fit['slope'] )  
	return g_m_max, V_T_approx, (V_GS_steepest_region, fitted_steepest_region)

def _find_steepest_region(V_GS_data, I_D_data, region_length): 
	numberOfPoints = int(3 + 2*int(len(I_D_data)/20)) if(region_length is None) else (int(region_length))
	numberOfPoints = max(2, numberOfPoints)
	maxSlope = 0
	index = 0
	for i in range(len(I_D_data) + 1 - numberOfPoints):
		slope = abs(_linearFit(V_GS_data[i:i+numberOfPoints], I_D_data[i:i+numberOfPoints])['slope'])
		if(slope > maxSlope):
			maxSlope = slope
			index = i
	regionStart = index
	regionEnd = index + (numberOfPoints-1)
	return (int(regionStart), int(regionEnd))

def _getXValueAtYValue(x_data, y_data, y_value, index_guess=0):
	# Find index of data where y_data is closest to target y_value
	index = _indexOfValue(y_data, y_value, guess=index_guess)
	if(index == -1):
		raise NotImplementedError('Unable to find gate voltage for the given drain current value.')
	elif((index < 1) or (index > len(y_data) - 2)):
		raise NotImplementedError('Drain current value was too close to edge of data for VT extraction.')
		
	# Perform a local linear fit to increase effective measurement resolution at the point of interest, then solve for x_value analytically
	fit = _linearFit(x_data[index-1:index+2], y_data[index-1:index+2])
	x_value = (y_value - fit['y_intercept'])/fit['slope']
	
	return x_value

def _includeAdditionalXValues(x_data, y_data, x_values_to_add):
	x_values_added = []
	y_values_added = []
	for xval in x_values_to_add:
		if(xval not in x_data):
			try:
				yval = _getXValueAtYValue(y_data, x_data, xval)
				x_values_added.append(xval)
				y_values_added.append(yval)
			except:
				pass
	x_full = x_data + x_values_added
	y_full = y_data + y_values_added
	x_full, y_full = zip(*sorted(zip(x_full, y_full)))
	return x_full, y_full

def _averageDuplicateX(x_data, y_data, removePointsThatDoNotHaveDuplicate=False):
	value_dict = {}
	for i in range(len(x_data)):
		x = x_data[i]
		y = y_data[i]
		if(x in value_dict.keys()):
			value_dict[x].append(y)
		else:
			value_dict[x] = [y]
	x_combined = [key for key in value_dict.keys() if((not removePointsThatDoNotHaveDuplicate) or len(value_dict[key]) >= 2)]
	y_combined = [sum(value_dict[xval])/len(value_dict[xval]) for xval in x_combined]
	return x_combined, y_combined

def _indexOfValue(y, value, guess=0):
	guess = min(max(0, int(guess)), len(y)-1)
	part1 = list(reversed(range(0,guess)))
	part2 = list(range(guess, len(y) - 1))
	woven = [item for pair in zip(part2, part1) for item in pair]
	longer = part1 if(len(part1) >= len(part2)) else part2
	indices = woven + longer[len(longer) - abs(len(part1)-len(part2)):]
		
	index = -1
	for i in indices:
		if(((y[i] < value) and (y[i+1] >= value)) or ((y[i] > value) and (y[i+1] <= value))):
			distance1 = abs(y[i]-value)
			distance2 = abs(y[i+1]-value)
			index = i if(distance1 < distance2) else i+1
			break
	return index

def _linearFit(x, y, includedFittedData=False):
	slope, intercept = np.polyfit(x, y, 1)
	return {'slope':slope, 'y_intercept':intercept, 'x_intercept':-intercept/slope, 'fitted_data': [slope*x[i] + intercept for i in range(len(x))] if(includedFittedData) else None}

def _semilogFit(x, y):
	fit_results = _linearFit(x, np.log10(np.abs(y)), includedFittedData=True)
	fitted_data = [10**(fit_results['fitted_data'][i]) for i in range(len(fit_results['fitted_data']))]
	return {'slope':fit_results['slope'], 'y_intercept':fit_results['y_intercept'], 'x_intercept':fit_results['x_intercept'], 'fitted_data': fitted_data}



if __name__ == '__main__':
	if(False):
		import matplotlib as mpl
		from matplotlib import pyplot as plt
		import random
			
		V_DS_data = np.linspace(0, 4, 500)
		V_GS = 1.0	
		V_GS_data = np.linspace(-3, 3, 500)
		V_DS = 1.0
		
		if(True):
			I_DN = (np.array([NMOSFET_I_D_fn(vgs,  abs(V_DS), 0, 1e-6, 500, 1e-10)*(1+random.random()/10) for vgs in V_GS_data]))
			I_DP = (np.array([PMOSFET_I_D_fn(vgs, -abs(V_DS), 0, 1e-6, 300, 1e-10)*(1+random.random()/10) for vgs in V_GS_data]))
			
			fitted_vals_N, fitted_model_parameters_N, fitted_model_parameters_kw_N = NMOSFET_Fit(V_GS_data, I_DN, abs(V_DS))
			fitted_vals_P, fitted_model_parameters_P, fitted_model_parameters_kw_P = PMOSFET_Fit(V_GS_data, I_DP, -abs(V_DS))

			print(fitted_model_parameters_kw_N)
			print(fitted_model_parameters_kw_P)
			
			plot_data = I_DP
			plot_model = fitted_vals_P
			xvals = V_GS_data
			
			fig1, ax1 = plt.subplots(1,1, figsize=(4,4))
			ax1.plot(xvals, abs(plot_data), marker='o', markersize=2, linewidth=1)
			ax1.plot(xvals, abs(np.array(plot_model)))
			ax1.set_ylabel('$I_{{D}}$ ($\\mu A$)')
			ax1.set_xlabel('$V_{{GS}}$ ($V$)')
			ax1.set_yscale('log')
			fig1.tight_layout()
			plt.show()
		else:
			I_DN_1 = (np.array([NMOSFET_I_D_fn(vgs, V_DS, 0, 5e-6, 300, 1e-10)*(1) for vgs in V_GS_data]))
			I_DN_2 = (np.array([NMOSFET_I_D_fn(vgs, V_DS, 0, 5e-6, 500, 1e-10)*(1) for vgs in V_GS_data]))*10
			I_DN_3 = (np.array([NMOSFET_I_D_fn(vgs, V_DS, 0, 5e-6, 1000, 1e-10)*(1) for vgs in V_GS_data]))*100
			I_DN_4 = (np.array([NMOSFET_I_D_fn(vgs, V_DS, 0, 5e-6, 2000, 1e-10)*(1) for vgs in V_GS_data]))*1000
			I_DN_5 = (np.array([NMOSFET_I_D_fn(vgs, V_DS, 0, 5e-6, 4000, 1e-10)*(1) for vgs in V_GS_data]))*10000
			
			fig1, ax1 = plt.subplots(1,1, figsize=(4,4))
			ax1.plot(V_DS_data, abs(I_DN_1), marker='o', markersize=2, linewidth=1)
			ax1.plot(V_DS_data, abs(I_DN_2), marker='o', markersize=2, linewidth=1)
			ax1.plot(V_DS_data, abs(I_DN_3), marker='o', markersize=2, linewidth=1)
			ax1.plot(V_DS_data, abs(I_DN_4), marker='o', markersize=2, linewidth=1)
			ax1.plot(V_DS_data, abs(I_DN_5), marker='o', markersize=2, linewidth=1)
			ax1.set_ylabel('$I_{{D}}$ ($\\mu A$)')
			ax1.set_xlabel('$V_{{GS}}$ ($V$)')
			ax1.set_yscale('log')
			fig1.tight_layout()
			plt.show()
		
	
	x = [1,2,2,3,4,4,5]
	y = [1,2,3,4,5,6,7]
	
	print(_indexOfValue(x,3,guess=6))
	
		
	
	






