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
NMOSFET_I_D_subth_fn = lambda V_GS, V_DS, V_TN, K_N, SS_mV_dec: ((K_N) * ((SS_mV_dec/1000)/(ln(10)*kB_T_q) - 1) * ((kB_T_q)**2) * exp((V_GS - V_TN) * ln(10)/(SS_mV_dec/1000)) * (1 - exp(-V_DS/kB_T_q)))
NMOSFET_I_D_lin_fn = lambda V_GS, V_DS, V_TN, K_N: ((K_N)*((V_GS - V_TN)*V_DS - 0.5*(V_DS**2)))
NMOSFET_I_D_sat_fn = lambda V_GS, V_TN, K_N: ((K_N/2)*((V_GS - V_TN)**2))
NMOSFET_I_D_on_fn = lambda V_GS, V_DS, V_TN, K_N: (NMOSFET_I_D_lin_fn(V_GS, V_DS, V_TN, K_N) if (V_DS < NMOSFET_V_DSat_fn(V_GS, V_TN)) else NMOSFET_I_D_sat_fn(V_GS, V_TN, K_N))
NMOSFET_I_D_ChLenMod_fn = lambda V_GS, V_DS, V_TN, K_N, SS_mV_dec, I_OFF, lambda_N: (NMOSFET_I_D_fn(V_GS, V_DS, V_TN, K_N, SS_mV_dec, I_OFF) * (1 + lambda_N*V_DS))
NMOSFET_I_D_fn = lambda V_GS, V_DS, V_TN, K_N, SS_mV_dec, I_OFF: (max(NMOSFET_I_D_subth_fn(V_GS, V_DS, V_TN, K_N, SS_mV_dec) if(V_GS < V_TN + 2*(SS_mV_dec/1000)/ln(10)) else NMOSFET_I_D_on_fn(V_GS, V_DS, V_TN, K_N), I_OFF))

# Level 1 SPICE PMOSFET Model
PMOSFET_V_DSat_fn = lambda V_GS, V_TP: (V_GS - V_TP)
PMOSFET_g_m_fn = lambda V_GS, V_DS, V_TP, K_P: ( (K_P*V_DS) if(V_DS > PMOSFET_V_DSat_fn(V_GS, V_TP)) else (K_P)*(V_GS - V_TP) )
PMOSFET_I_D_subth_fn = lambda V_GS, V_DS, V_TP, K_P, SS_mV_dec: ((-K_P) * ((SS_mV_dec/1000)/(ln(10)*kB_T_q) - 1) * ((kB_T_q)**2) * exp(-(V_GS - V_TP) * ln(10)/(SS_mV_dec/1000)) * (1 - exp(-abs(V_DS)/kB_T_q)))
PMOSFET_I_D_lin_fn = lambda V_GS, V_DS, V_TP, K_P: ((-K_P)*((V_GS - V_TP)*V_DS - 0.5*(V_DS**2)))
PMOSFET_I_D_sat_fn = lambda V_GS, V_TP, K_P: ((-K_P/2)*((V_GS - V_TP)**2))
PMOSFET_I_D_on_fn = lambda V_GS, V_DS, V_TP, K_P: (PMOSFET_I_D_lin_fn(V_GS, V_DS, V_TP, K_P) if (V_DS > PMOSFET_V_DSat_fn(V_GS, V_TP)) else PMOSFET_I_D_sat_fn(V_GS, V_TP, K_P))
PMOSFET_I_D_ChLenMod_fn = lambda  V_GS, V_DS, V_TP, K_P, SS_mV_dec, lambda_P: (PMOSFET_I_D_fn(V_GS, V_DS, V_TP, K_P, SS_mV_dec) * (1 + lambda_P*V_DS))
PMOSFET_I_D_fn = lambda V_GS, V_DS, V_TP, K_P, SS_mV_dec, I_OFF: (min(PMOSFET_I_D_subth_fn(V_GS, V_DS, V_TP, K_P, SS_mV_dec) if(V_GS > V_TP - 2*(SS_mV_dec/1000)/ln(10)) else PMOSFET_I_D_on_fn(V_GS, V_DS, V_TP, K_P), -abs(I_OFF)))



def NMOSFET_Fit(V_GS_data, I_D_data, V_DS, V_TN_guess=0, K_N_guess=50e-6, SS_mV_dec_guess=1000, I_OFF_guess=500e-12, V_TN_min=-50, V_TN_max=50, K_N_min=1e-9, K_N_max=1e-3, SS_mV_dec_min=50, SS_mV_dec_max=1e5, I_OFF_min=100e-15, I_OFF_max=1e-6):
	# Fit on a log scale first to find and fix I_OFF and SS
	I_D_data_logarithmic = np.log10(np.array(I_D_data))
	NMOSFET_Full_Model_logarithmic = lambda v_gs_data, v_tn, k_n, ss_mv_dec, i_off: [np.log10(NMOSFET_I_D_fn(v_gs, V_DS, v_tn, k_n, ss_mv_dec, i_off)) for v_gs in v_gs_data]
	(V_TN_estimate, K_N_estimate, SS_mV_dec_fitted, I_OFF_fitted), log_covariance = optimize.curve_fit(NMOSFET_Full_Model_logarithmic, V_GS_data, I_D_data_logarithmic, p0=[V_TN_guess, K_N_guess, SS_mV_dec_guess, I_OFF_guess] , bounds=([V_TN_min, K_N_min, SS_mV_dec_min, I_OFF_min], [V_TN_max, K_N_max, SS_mV_dec_max, I_OFF_max]))
	
	# Fit on a linear scale to find V_TN and K_N
	NMOSFET_Full_Model_linear = lambda v_gs_data, v_tn, k_n: [NMOSFET_I_D_fn(v_gs, V_DS, v_tn, k_n, SS_mV_dec_fitted, I_OFF_fitted) for v_gs in v_gs_data]
	(V_TN_fitted, K_N_fitted), covariance = optimize.curve_fit(NMOSFET_Full_Model_linear, V_GS_data, I_D_data, p0=[V_TN_estimate, K_N_estimate], bounds=([V_TN_min, K_N_min], [V_TN_max, K_N_max]))
	
	fitted_model_parameters = [V_TN_fitted, K_N_fitted, SS_mV_dec_fitted, I_OFF_fitted]
	fitted_model_parameters_kw = {'V_TN':V_TN_fitted, 'K_N':K_N_fitted, 'SS_mV_dec':SS_mV_dec_fitted, 'I_OFF':I_OFF_fitted}
	fitted_yvals = [NMOSFET_I_D_fn(vgs, V_DS, *fitted_model_parameters) for vgs in V_GS_data]
	return (fitted_yvals, fitted_model_parameters, fitted_model_parameters_kw, covariance)

def PMOSFET_Fit(V_GS_data, I_D_data, V_DS, V_TP_guess=0, K_P_guess=50e-6, SS_mV_dec_guess=1000, I_OFF_guess=500e-12, V_TP_min=-50, V_TP_max=50, K_P_min=1e-9, K_P_max=1e-3, SS_mV_dec_min=50, SS_mV_dec_max=1e5, I_OFF_min=100e-15, I_OFF_max=1e-6):
	# Fit the absolute value of the data on a log scale first to find and fix I_OFF and SS
	I_D_data_abs_logarithmic = np.log10(abs(np.array(I_D_data)))
	PMOSFET_Full_Model_logarithmic = lambda v_gs_data, v_tp, k_p, ss_mv_dec, i_off: [np.log10(abs(PMOSFET_I_D_fn(v_gs, V_DS, v_tp, k_p, ss_mv_dec, i_off))) for v_gs in v_gs_data]
	(V_TP_estimate, K_P_estimate, SS_mV_dec_fitted, I_OFF_fitted), log_covariance = optimize.curve_fit(PMOSFET_Full_Model_logarithmic, V_GS_data, I_D_data_abs_logarithmic, p0=[V_TP_guess, K_P_guess, SS_mV_dec_guess, I_OFF_guess], bounds=([V_TP_min, K_P_min, SS_mV_dec_min, I_OFF_min], [V_TP_max, K_P_max, SS_mV_dec_max, I_OFF_max]))
		
	# Fit on a linear scale to find V_TP and K_P
	PMOSFET_Full_Model_linear = lambda v_gs_data, v_tp, k_p: [PMOSFET_I_D_fn(v_gs, V_DS, v_tp, k_p, SS_mV_dec_fitted, I_OFF_fitted) for v_gs in v_gs_data]
	(V_TP_fitted, K_P_fitted), covariance = optimize.curve_fit(PMOSFET_Full_Model_linear, V_GS_data, I_D_data, p0=[V_TP_estimate, K_P_estimate], bounds=([V_TP_min, K_P_min], [V_TP_max, K_P_max]))
	
	fitted_model_parameters = [V_TP_fitted, K_P_fitted, SS_mV_dec_fitted, I_OFF_fitted]
	fitted_model_parameters_kw = {'V_TP':V_TP_fitted, 'K_P':K_P_fitted, 'SS_mV_dec':SS_mV_dec_fitted, 'I_OFF':I_OFF_fitted}
	fitted_yvals = [PMOSFET_I_D_fn(vgs, V_DS, *fitted_model_parameters) for vgs in V_GS_data]
	return (fitted_yvals, fitted_model_parameters, fitted_model_parameters_kw, covariance)



if __name__ == '__main__':
	import matplotlib as mpl
	from matplotlib import pyplot as plt
	
	fig, ax = plt.subplots(1,1, figsize=(3,3))
	
	V_GS_data = np.linspace(-2, 2, 200)
	V_DS = 1.0
	
	import random
	
	I_D =  (np.array([NMOSFET_I_D_fn(vgs, V_DS, 0, 50e-6, 100, 1e-10)*(1+random.random()/8) for vgs in V_GS_data]))
	
	fitted_vals, fitted_model_parameters, fitted_model_parameters_kw, cov = NMOSFET_Fit(V_GS_data, I_D, V_DS)
		
	print(fitted_model_parameters_kw)
	
	ax.plot(V_GS_data+0.1, (10**6) * abs(I_D), marker='o', markersize=2, linewidth=1)
	#ax.plot(V_GS_data, (10**6) * abs(np.array(fitted_vals)))
	ax.set_ylabel('$I_{{D}}$ ($\\mu A$)')
	ax.set_xlabel('$V_{{GS}}$ ($V$)')
	ax.set_yscale('log')
	plt.show()







