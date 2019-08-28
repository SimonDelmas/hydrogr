import matplotlib.pyplot as plt
plt.style.use('ggplot')


def plot_hydrograph(output_data, reference_time_series=None):
    """
    Plot hydrograph using matplotlib.

    :param output_data: Model output data as pandas Dataframe.
    :param reference_time_series: (optional) Reference flow time series (observation).
    """
    fig, (ax0, ax1) = plt.subplots(nrows=2, sharex=True, gridspec_kw={'height_ratios': [1, 4]})

    ax0.invert_yaxis()
    output_data['Precip'].plot(ax=ax0, label='Rainfall', color='b')
    ax0.set_ylim([None, 0])
    ax0.set_ylabel('Rainfall depth (mm)')
    ax0.legend()

    output_data['Qsim'].plot(ax=ax1, label='Computed flow', color='b')
    if reference_time_series is not None:
        reference_time_series.plot(ax=ax1, label='Reference flow')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Flow (m3/s)')
    ax1.legend()

    plt.show()
