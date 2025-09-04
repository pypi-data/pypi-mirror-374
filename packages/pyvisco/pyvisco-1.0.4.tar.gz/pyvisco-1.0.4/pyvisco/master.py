"""
Collection of functions to prepare the master curve for the identification 
of the Prony series parameters. Methods are provided to shift the raw 
measurement data into a master curve and remove measurement outliers through
smoothing of the master curve.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit

"""
--------------------------------------------------------------------------------
Methods to shift raw data into master curve based on shift factors
--------------------------------------------------------------------------------
"""
def pwr_y(x, a, b, e):
    """
    Calculate the Power Law relation with a deviation term.
    
    Parameters
    ----------
    x : numeric
        Input to Power Law relation.
    a : numeric
        Constant.
    b : numeric
        Exponent.
    e : numeric
        Deviation term.

    Returns
    -------
    numeric
        Output of Power Law relation.

    Notes
    -----
    Power Law relation: :math:`y = a x^b + e`
    """
    return a*x**b+e


def pwr_x(y, a, b, e):
    r"""
    Calculate the inverse Power Law relation with a deviation term.
    
    Parameters
    ----------
    y : numeric
        Output of Power Law relation.
    a : numeric
        Constant.
    b : numeric
        Exponent.
    e : numeric
        Deviation term.

    Returns
    -------
    numeric
        Input to Power Law relation.

    Notes
    -----
    Inverse Power Law relation: :math:`x=\left(\frac{y-e}{a}\right)^{\frac{1}{b}}`
    """
    base = (y-e)/a
    power = 1/b
    x = np.sign(base) * (np.abs(base)) ** (power)
    return x


def fit_pwr(xdata, ydata):
    """
    Define bounds for curve fitting routine and fit power law.
    
    Parameters
    ----------
    xdata : array-like
        x data to be fitted.
    ydata : array-like
        y data to be fitted.

    Returns
    -------
    popt : array-like
        Optimal values for the parameters.
    pcov : 2D array
        The estimated covariance of popt. The diagonals provide the variance 
        of the parameter estimate.

    See also
    --------
    scipy.optimize.curve_fit :  Non-linear least squares fit to a function.
    """
    bnd = ([-np.inf, -np.inf, -ydata.max()], [np.inf, np.inf, ydata.max()])
    popt, pcov = curve_fit(pwr_y, xdata, ydata, bounds = bnd)
    return popt, pcov


def fit_at_pwr(df_raw, gb_ref, gb_shift):
    """
    Obtain shift factor between two measurement sets at different tempeatures.

    The raw measurement data at each temperature level are fitted by a Power Law
    function. These Power Law functions improve the robustness of the
    shifting algorithm, because they functions smooth outliers and bridge 
    possible gaps between the data sets. The intersection of the functions
    is calculated and used to obtain the shift factor.
    
    Parameters
    ----------
    df_raw : pandas.DataFrame
        Contains the processed raw measurement data.
    gb_ref : int
        Dataframe 'Set' number of the reference measurement set.
    gb_shift : int
        Dataframe 'Set' number of the measurement set that is shifted.
    
    Returns
    -------
    log_aT : numeric
        The decadic logarithm of the shift factor between the two measurement
        sets.

    Notes
    -----
    In certain circumstances the equilibration time between measurements at 
    different temperature levels can be too short to reach a steady state 
    leading to errors in the first data point of the measurement set. 
    To account for such situation, tow Power law fits are conducted. The first
    fit contains all data points and the second fit drops the first data point.
    If dropping the data point increased the goodness of fit, this 
    Power Law fit is used to calculate the shift factor.
    """
    modul = df_raw.modul
    if df_raw.domain == 'freq':
        _modul = '{}_stor'.format(modul)
    elif df_raw.domain == 'time':
        _modul = '{}_relax'.format(modul)

    #Get data for the reference set and the set to be shifted
    gb = df_raw.groupby('Set')
    ref_xdata   = gb.get_group(gb_ref)['f_set'].values
    ref_ydata   = gb.get_group(gb_ref)[_modul].values
    shift_xdata = gb.get_group(gb_shift)['f_set'].values
    shift_ydata = gb.get_group(gb_shift)[_modul].values

    #Curve fit power law
    ref_popt, ref_pcov = fit_pwr(ref_xdata, ref_ydata)
    shift_popt, shift_pcov = fit_pwr(shift_xdata, shift_ydata)

    #Check and remove first measurement point if outlier
    ref_popt_rem, ref_pcov_rem = fit_pwr(ref_xdata[1:], ref_ydata[1:]) 
    ref_perr = np.sqrt(np.abs(np.diag(ref_pcov)))
    ref_perr_rem = np.sqrt(np.abs(np.diag(ref_pcov_rem)))
    ref_drop_first = False
    #if all(ref_perr_rem < ref_perr):
    if ref_perr_rem[1] < ref_perr[1]:
        ref_popt = ref_popt_rem
        ref_xdata = ref_xdata[1:] 
        ref_ydata = ref_ydata[1:]
        ref_drop_first = True

    shift_popt_rem, shift_pcov_rem = fit_pwr(shift_xdata[1:], shift_ydata[1:]) 
    shift_perr = np.sqrt(np.abs(np.diag(shift_pcov)))
    shift_perr_rem = np.sqrt(np.abs(np.diag(shift_pcov_rem)))
    shift_drop_first = False
    #if all(shift_perr_rem < shift_perr):
    if shift_perr_rem[1] < shift_perr[1]:
        shift_popt = shift_popt_rem
        shift_xdata = shift_xdata[1:] 
        shift_ydata = shift_ydata[1:]
        shift_drop_first = True

    #Calculate fit
    ref_ydata_fit = pwr_y(ref_xdata, *ref_popt)
    shift_ydata_fit = pwr_y(shift_xdata, *shift_popt)

    #Get interpolation or extrapolation range
    if (ref_ydata_fit.max() > shift_ydata_fit.max() and
        ref_ydata_fit.min() > shift_ydata_fit.min()):
        #Ref is on top
        top_xdata = ref_xdata
        top_ydata = ref_ydata_fit
        top_popt = ref_popt
        bot_xdata = shift_xdata
        bot_ydata = shift_ydata_fit
        bot_popt = shift_popt
        sign = 1
    elif(ref_ydata_fit.max() < shift_ydata_fit.max() and
         ref_ydata_fit.min() < shift_ydata_fit.min()):
        #Shift is on top
        top_xdata = shift_xdata
        top_ydata = shift_ydata_fit   
        top_popt = shift_popt
        bot_xdata = ref_xdata
        bot_ydata = ref_ydata_fit
        bot_popt = ref_popt
        sign = -1
    else:
        #Ref and Shift are intersecting
        if ref_ydata_fit.max() > shift_ydata_fit.max():
            top_xdata = shift_xdata
            top_ydata = shift_ydata_fit   
            top_popt = shift_popt
            bot_xdata = ref_xdata
            bot_ydata = ref_ydata_fit
            bot_popt = ref_popt
            sign = -1
        else:
            top_xdata = ref_xdata
            top_ydata = ref_ydata_fit
            top_popt = ref_popt
            bot_xdata = shift_xdata
            bot_ydata = shift_ydata_fit
            bot_popt = shift_popt
            sign = 1

    if top_ydata.min() < bot_ydata.max():
        #overlap range
        ymin = top_ydata.min()
        ymax = bot_ydata.max()
    else:
        #gap range
        ymin = bot_ydata.max()
        ymax = top_ydata.min()   
        
    #Define three points along inter/extrapolation range
    y = np.linspace(ymin, ymax, 10)

    #Compute average shift factor for the three points
    x_top = pwr_x(y, *top_popt)
    x_bot = pwr_x(y, *bot_popt)

    #Calculate shift factor
    log_aT = sign * np.log10(x_top/x_bot).mean()

    #Collect data to debug shift algorithm
    dshift = {'ref_xdata':ref_xdata, 
              'ref_ydata':ref_ydata,
              'ref_ydata_fit':ref_ydata_fit, 
              'shift_xdata':shift_xdata, 
              'shift_ydata':shift_ydata,
              'shift_ydata_fit':shift_ydata_fit,
              'x_top' : x_top,
              'x_bot' : x_bot,
              'y' : y,
              'log_aT': log_aT,
              'shifted_xdata':10**log_aT*shift_xdata,
              'ref_drop_first':ref_drop_first,
              'shift_drop_first':shift_drop_first,
              'ref_perr' : ref_perr,
              'ref_perr_rem' : ref_perr_rem,
              'shift_perr' : shift_perr,
              'shift_perr_rem' : shift_perr_rem}

    return log_aT, dshift 




def get_aT(df_raw, RefT):
    """
    Get shift factors for each temperature level in the raw measurement data.

    A reference temperature is specified for which the master curve is created.
    Measurement sets below the desired reference temperatures are shifted to 
    lower frequencies (longer time periods), whereas measurement sets at 
    temperatures higher than the reference temperature are shifted to higher 
    frequencies (shorter time periods). 

    Parameters
    ----------
    df_raw : pandas.DataFrame
        Contains the processed raw measurement data.
    RefT : int or float
        Reference tempeature of the master curve in Celsius.

    Returns
    -------
    df_aT : pandas.DataFrame
        Contains the decadic logarithm of the shift factors 'log_aT'
        and the corresponding temperature values 'T' in degree Celsius.

    See also
    --------
    load.Eplexor_raw : Returns df_raw from Eplexor Excel file.
    load.user_raw: Returns df_raw from csv file.
    """
    #Create df_aT
    Temp = []
    for i, df_set in df_raw.groupby('Set'):
        T = df_set['T_round'].iloc[0]
        Temp.append(T)
        if T == RefT:
            idx = i
    df_aT = pd.DataFrame(Temp, columns=['T'])
    df_aT['log_aT'] = np.nan 

    #Set shift factor at RefT
    df_aT.loc[idx]['log_aT'] = 0

    #Create debug data dictionary
    dshift ={}

    #Shift below RefT
    for i in range(idx, 0, -1):
        log_aT, shift = fit_at_pwr(df_raw, i, i-1) 
        df_aT.loc[i-1]['log_aT'] = log_aT + df_aT.loc[i]['log_aT']
        dshift[df_aT.loc[i-1]['T']] = shift
        
    #Shift above RefT
    for i in range(idx, df_aT.shape[0]-1, 1):
        log_aT, shift = fit_at_pwr(df_raw, i, i+1) 
        df_aT.loc[i+1]['log_aT'] = log_aT + df_aT.loc[i]['log_aT']
        dshift[df_aT.loc[i+1]['T']] = shift
    return df_aT, dshift


def get_curve(df_raw, df_aT, RefT):
    """
    Get master curve by shifting the individual measurement sets.

    The master curve is created from the raw measurement data based on the
    provided shift factors for the specified reference temperature. 

    Parameters
    ----------
    df_raw : pandas.DataFrame
        Contains the processed raw measurement data.
    df_aT : pandas.DataFrame
        Contains the decadic logarithm of the shift factors 'log_aT'
        and the corresponding temperature values 'T' in degree Celsius.
    RefT : int or float
        Reference tempeature of the master curve in Celsius.

    Returns
    -------
    df_master : pandas.DataFrame
        Contains the master curve data.

    See also
    --------
    load.Eplexor_raw : Returns df_raw from Eplexor Excel file.
    load.user_raw: Returns df_raw from csv file.
    master.get_aT : Returns df_aT.
    """
    modul = df_raw.modul
    stor = '{}_stor'.format(modul)
    loss = '{}_loss'.format(modul)
    comp = '{}_comp'.format(modul)
    relax = '{}_relax'.format(modul)

    df_shift = pd.DataFrame() 
    for S, df in df_raw.groupby('Set'):  
        aT = 10**(df_aT[df_aT['T'] == df['T_round'].iloc[0]]['log_aT'].values)
        fshift = aT * df['f_set']
        df_shift = pd.concat([df_shift, fshift.to_frame()])

    if df_raw.domain == 'freq':
        df_master = df_raw[[stor, loss, "Set"]].copy()
        df_master['f'] = df_shift
        if comp in df_raw:
            df_master[comp] = df_raw[comp]
            df_master['tan_del'] = df_raw['tan_del']
        df_master = df_master.sort_values(by=['f']).reset_index(drop=True)
        df_master.RefT = RefT
        df_master.domain = df_raw.domain
        df_master.modul = modul
        df_master['omega'] = 2*np.pi*df_master['f']
        df_master['t'] = 1/df_master['f'] 
    elif df_raw.domain == 'time':
        df_master = df_raw[[relax, "Set"]].copy()
        df_master['t'] = 1/df_shift
        df_master = df_master.sort_values(by=['t']).reset_index(drop=True)
        df_master.RefT = RefT
        df_master.domain = df_raw.domain
        df_master.modul = modul
        df_master['f'] = 1/df_master['t']
        df_master['omega'] = 2*np.pi*df_master['f'] 
    return df_master


def plot(df_master, units):
    """
    Plot master curve.

    Parameters
    ----------
    df_master : pandas.DataFrame
        Contains the master curve data.
    units : dict of {str : str}
        Contains the names of the physical quantities as key and 
        the corresponding names of the units as item.

    Returns
    -------
    fig : matplotlib.pyplot.figure
        Domain dependent plot of master curve.
    """
    modul = df_master.modul
    stor = '{}_stor'.format(modul)
    loss = '{}_loss'.format(modul)
    relax = '{}_relax'.format(modul)

    if df_master.domain == 'freq':
        fig, (ax1, ax2) = plt.subplots(1,2, figsize=(8,0.75*4))
        ax1.set_xlabel('Frequency (Hz)')
        ax1.set_ylabel('Storage modulus ({})'.format(units[stor]))
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Loss modulus ({})'.format(units[stor])) 
        df_master.plot(x='f', y=[stor], ax=ax1, logx=True, logy=True)
        df_master.plot(x='f', y=[loss], ax=ax2, logx=True, logy=True)
        fig.show()
        return fig
    elif df_master.domain == 'time':
        fig, ax1 = plt.subplots(figsize=(4,0.75*4))
        df_master.plot(x='f', y=[relax], ax=ax1, logx=True, logy=True)
        ax1.set_xlabel('Time ({})'.format(units['t']))
        ax1.set_ylabel('Relaxation modulus ({})'.format(units[stor]))
        fig.show()
        return fig


def plot_shift(df_raw, df_master, units):
    """
    Plot raw measurement data and shifted master curve.

    Parameters
    ----------
    df_raw : pandas.DataFrame
        Contains the processed raw measurement data.
    df_master : pandas.DataFrame
        Contains the master curve data.
    units : dict of {str : str}
        Contains the names of the physical quantities as key and 
        the corresponding names of the units as item.

    Returns
    -------
    fig : matplotlib.pyplot.figure
        Plot of raw measurement data and master curve.

    ax : tuple
        Frequency domain: (ax1, lax1, ax2, lax2)
            ax1 : matplotlib.axes.Axes
                Axes object of storage modulus plot
            lax1 : list of matplotlib.lines.Line2D
                Line2D instances for easy update of xdata and ydata in 
                storage modulus plot
            ax2 : matplotlib.axes.Axes
                Axes object of loss modulus plot
            lax2 : list of matplotlib.lines.Line2D
                Line2D instances for easy update of xdata and ydata in 
                loss modulus plot
        Time domain: (ax1, lax1)
            ax1 : matplotlib.axes.Axes
                Axes object of relaxation modulus plot
            lax1 : list of matplotlib.lines.Line2D
                Line2D instances for easy update of xdata and ydata in 
                relaxation modulus plot

    See also
    --------
    master.plot_shift_update : Updates figure data.
    """
    modul = df_raw.modul
    stor = '{}_stor'.format(modul)
    loss = '{}_loss'.format(modul)
    relax = '{}_relax'.format(modul)

    if df_master.domain == 'freq':
        fig, (ax1, ax2) = plt.subplots(1,2, figsize=(8,0.75*4))
        ax1.set_xlabel('Frequency (Hz)')
        ax1.set_ylabel('Storage modulus ({})'.format(units[stor]))
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Loss modulus ({})'.format(units[stor])) 

        gb_raw = df_raw.groupby('Set')
        gb_master = df_master.groupby('Set')
        colors1 = np.flip(plt.cm.Blues(np.linspace(0,1,int(gb_raw.ngroups*1.25))),axis=0)
        colors2 = np.flip(plt.cm.Oranges(np.linspace(0,1,int(gb_raw.ngroups*1.25))),axis=0)

        lax1 = []
        lax2 = []
        for i, (group, df_set) in enumerate(gb_master):
            line1, = ax1.loglog(df_set["f"], df_set[stor], 
                ls='', marker='.', color=colors1[int(group)])
            line2, = ax2.loglog(df_set["f"], df_set[loss], 
                ls='', marker='.', color=colors2[int(group)])
            lax1.append(line1)
            lax2.append(line2)
        for i, (group, df_set) in enumerate(gb_raw):
            if i in np.linspace(0, gb_raw.ngroups-1, num=5, dtype=int):
                ax1.loglog(df_set["f_set"], df_set[stor], 
                    ls='', marker='.', color=colors1[int(group)], 
                    label = '$T$={}\N{DEGREE SIGN}C'.format(df_set['T_round'].iloc[0]))
                ax2.loglog(df_set["f_set"], df_set[loss], 
                    ls='', marker='.', color=colors2[int(group)], 
                    label = '$T$={}\N{DEGREE SIGN}C'.format(df_set['T_round'].iloc[0]))
            else:
                ax1.loglog(df_set["f_set"], df_set[stor], 
                ls='', marker='.', color=colors1[int(group)])
                ax2.loglog(df_set["f_set"], df_set[loss], 
                ls='', marker='.', color=colors2[int(group)])
        ax = (ax1, lax1, ax2, lax2)

        legend1 = ax1.legend(handlelength=1, handletextpad=0.1, fontsize=8)
        legend2 = ax2.legend(handlelength=1, handletextpad=0.1, fontsize=8)
        # for legend_handle in legend1.legendHandles:
        #     legend_handle._legmarker.set_markersize(8)
        # for legend_handle in legend2.legendHandles:
        #     legend_handle._legmarker.set_markersize(8)
        fig.show()
        return fig, ax

    elif df_master.domain == 'time':
        fig, ax1 = plt.subplots(figsize=(4,0.75*4))
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Relaxation modulus ({})'.format(units[relax])) 
        
        gb_raw = df_raw.groupby('Set')
        gb_master = df_master.groupby('Set')
        colors1 = np.flip(plt.cm.Blues(np.linspace(0,1,int(gb_raw.ngroups*1.25))), axis=0)

        lax1 = []
        for i, (group, df_set) in enumerate(gb_master):
            line1, = ax1.loglog(df_set["t"], df_set[relax], 
                ls='', marker='.', color=colors1[int(group)])
            lax1.append(line1)
        for i, (group, df_set) in enumerate(gb_raw):
            if i in np.linspace(0, gb_raw.ngroups-1, num=5, dtype=int):
                ax1.loglog(df_set["t_set"], df_set[relax], 
                ls='', marker='.', color=colors1[int(group)], 
                label = '$T$={}\N{DEGREE SIGN}C'.format(df_set['T_round'].iloc[0]))
            else:
                ax1.loglog(df_set["t_set"], df_set[relax], 
                ls='', marker='.', color=colors1[int(group)])
        ax = (ax1, lax1)

        legend = ax1.legend(handlelength=1, handletextpad=0.1, fontsize=8)
        # for legend_handle in legend.legendHandles:
        #     legend_handle._legmarker.set_markersize(8)
        fig.show()
        return fig, ax


def plot_shift_update(df_master, fig, ax):
    """
    Upadate plot of raw measurement data and shifted master curve.

    Parameters
    ----------
    df_master : pandas.DataFrame
        Contains the master curve data.
    fig : matplotlib.pyplot.figure
        Matplotlib figure instance.
    ax : tuple
        Frequency domain: (ax1, lax1, ax2, lax2)
            ax1 : matplotlib.axes.Axes
                Axes object of storage modulus plot
            lax1 : list of matplotlib.lines.Line2D
                Line2D instances for easy update of xdata and ydata in 
                storage modulus plot
            ax2 : matplotlib.axes.Axes
                Axes object of loss modulus plot
            lax2 : list of matplotlib.lines.Line2D
                Line2D instances for easy update of xdata and ydata in 
                loss modulus plot
        Time domain: (ax1, lax1)
            ax1 : matplotlib.axes.Axes
                Axes object of relaxation modulus plot
            lax1 : list of matplotlib.lines.Line2D
                Line2D instances for easy update of xdata and ydata in 
                relaxation modulus plot

    See also
    --------
    master.plot_shift : Creates figure that is updated with this function.
    """
    modul = df_master.modul
    stor = '{}_stor'.format(modul)
    loss = '{}_loss'.format(modul)

    gb_master = df_master.groupby('Set')

    if len(ax) == 2:
        ax1, lax1 = ax
    elif len(ax) == 4:
        ax1, lax1, ax2, lax2 = ax

    for i, (group, df_set) in enumerate(gb_master):
        line1 = lax1[i]
        line1.set_xdata(df_set["f"])
        line1.set_ydata(df_set[stor])
        if len(ax) == 4:
            line2 = lax2[i]
            line2.set_xdata(df_set["f"])
            line2.set_ydata(df_set[loss])
    ax1.relim()
    ax1.autoscale_view()
    if len(ax) == 4:
        ax2.relim()
        ax2.autoscale_view()
    fig.canvas.draw_idle()
    return fig


"""
--------------------------------------------------------------------------------
Methods to smooth master curve and remove outliers
--------------------------------------------------------------------------------
"""
def smooth(df_master, win = 1):
    """
    Remove outliers in measurement data by smoothing master curve.

    A moving median filter with variable window size is applied to remove 
    outliers from the measurement data. 
    
    Parameters
    ----------
    df_master : pandas.DataFrame
        Contains the master curve data.
    win : int, default = 1 
        Window size of the median filter. A window size of 1 means that no 
        filtering procedure is performed and the input data are returned.

    Return
    ------
    df_master : pandas.DataFrame
        Contains the master curve data, including the filtered arrays.
    """
    modul = df_master.modul
    stor = '{}_stor'.format(modul)
    loss = '{}_loss'.format(modul)
    relax = '{}_relax'.format(modul)
    stor_filt = '{}_stor_filt'.format(modul)
    loss_filt = '{}_loss_filt'.format(modul)
    relax_filt = '{}_relax_filt'.format(modul)

    if df_master.domain == 'freq':
        df_master[stor_filt] = df_master[stor].rolling(win, center=True, min_periods=1).median()
        df_master[loss_filt] = df_master[loss].rolling(win, center=True, min_periods=1).median()
    elif df_master.domain == 'time':
        df_master[relax_filt] = df_master[relax].rolling(win, center=True, min_periods=1).median()
    return df_master


def plot_smooth(df_master, units):
    """
    Plot filtered and unfilterd master curve.
   
    Parameters
    ----------
    df_master : pandas.DataFrame
        Contains the filtered and unfiltered master curve data.
    units : dict of {str : str}
        Contains the names of the physical quantities as key and 
        the corresponding names of the units as item.

    Return
    ------
    fig : matplotlib.pyplot.figure
        Plot displaying the filtered and unfilterd master curve data.
    """
    modul = df_master.modul
    stor = '{}_stor'.format(modul)
    loss = '{}_loss'.format(modul)
    relax = '{}_relax'.format(modul)
    stor_filt = '{}_stor_filt'.format(modul)
    loss_filt = '{}_loss_filt'.format(modul)
    relax_filt = '{}_relax_filt'.format(modul)

    if df_master.domain == 'freq':
        fig, (ax1, ax2) = plt.subplots(1,2, figsize=(8,0.75*4))
        df_master.plot(x='f', y=[stor], label=["{}'(raw)".format(modul)], 
            ax=ax1, logx=True, logy=True, color=['C0'], marker='o', ls='', alpha=0.5)
        df_master.plot(x='f', y=[stor_filt], label=["{}'(filter)".format(modul)], 
            ax=ax1, logx=True, logy=True, color=['C0'])
        df_master.plot(x='f', y=[loss], label=["{}''(raw)".format(modul)], 
            ax=ax2, logx=True, logy=True, color=['C1'], marker='o', ls='', alpha=0.5)
        df_master.plot(x='f', y=[loss_filt], label=["{}''(filter)".format(modul)], 
            ax=ax2, logx=True, logy=True, color=['C1'])
        ax1.set_xlabel('Frequency (Hz)')
        ax1.set_ylabel('Storage modulus ({})'.format(units[stor]))
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Loss modulus ({})'.format(units[stor])) 
        ax1.legend()
        ax2.legend()
        fig.show()
        return fig
    elif df_master.domain == 'time':
        fig, ax1 = plt.subplots(figsize=(4,0.75*4))
        df_master.plot(x='t', y=[relax], label = [relax], 
            ax=ax1, logx=True, logy=True, ls='', marker='o', color=['gray'])
        df_master.plot(x='t', y=[relax_filt], label=['filter'], 
            ax=ax1, logx=True, logy=True, color=['r'])
        ax1.set_xlabel('Time ({})'.format(units['t']))
        ax1.set_ylabel('Relaxation modulus ({})'.format(units[relax])) 
        ax1.legend()
        fig.show()
        return fig
    

def plot_shift_debug(dshift):
    """
    Plot shifted measurement sets. Helpful for manual adjustment of master curve.
   
    Parameters
    ----------
    dshift : dictionary
        Contains data of the shifted measurement sets.

    Return
    ------
    fig : matplotlib.pyplot.figure
        Plot displaying the fitted and shifted measurement data sets.
    """
    for T, shift in sorted(dshift.items()):
        fig, (ax1, ax2) = plt.subplots(1,2, figsize=(8, 0.75*4))    
        
        #Input data
        ax1.loglog(shift['ref_xdata'], shift['ref_ydata_fit'], label='ref-fit', c='k', ls='--')
        ax1.loglog(shift['shift_xdata'], shift['shift_ydata_fit'], label='shift-fit', c='gray', ls='--')
        
        ax1.loglog(shift['ref_xdata'], shift['ref_ydata'], label='ref-data', c='k', ls='', marker='x', markersize=5)
        ax1.loglog(shift['shift_xdata'], shift['shift_ydata'], label='shift-data', c='gray', ls='', marker='x', markersize=5)
        
        ax1.loglog(shift['x_bot'], shift['y'], label='bot dis', marker='o', c='firebrick', ls='', markersize=3)
        ax1.loglog(shift['x_top'], shift['y'], label='top dis', marker='d', c='firebrick', ls='', markersize=3)
        
        #Shifted data
        ax2.loglog(shift['ref_xdata'], shift['ref_ydata_fit'], label='ref-fit', c='k', ls='--')
        ax2.loglog(shift['ref_xdata'], shift['ref_ydata'], label='ref-data', c='k', ls='', marker='x', markersize=5)
        
        ax2.loglog(shift['shifted_xdata'], shift['shift_ydata'], label='shift-data', c='gray', ls='', marker='x', markersize=5)
        ax2.loglog(shift['shifted_xdata'], shift['shift_ydata_fit'], label='shift-fit', c='gray', ls='--')
        
        ax1.legend(fontsize=7)
        ax2.legend(fontsize=7)
        fig.suptitle('Shift data set at T = {}°C'.format(T), fontsize=10)
        ax1.set_title('measurement set', fontsize=8)
        ax2.set_title('shifted set'.format(T), fontsize=8)
        fig.show()
        
        #First data point dropped?
        print('ref-drop-first: {} | perr: {} | perr_rem : {}'.format(
            shift['ref_drop_first'], 
            np.array2string(shift['ref_perr'], precision=2, separator=','), 
            np.array2string(shift['ref_perr_rem'], precision=2, separator=',')))
        print('shift-drop-first: {} | perr: {} | perr_rem : {}'.format(
            shift['shift_drop_first'],
            np.array2string(shift['shift_perr'], precision=2, separator=','), 
            np.array2string(shift['shift_perr_rem'], precision=2, separator=',')))