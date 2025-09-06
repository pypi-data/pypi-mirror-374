import numpy as np
import plotly.graph_objects as go
import scipy.signal as signal
from plotly.graph_objs import Figure
from scipy.fft import fft, fftshift

from ria_toolkit_oss.datatypes import Recording


def spectrogram(rec: Recording, thumbnail: bool = False) -> Figure:
    """Create a spectrogram for the recording.

    :param rec: Signal to plot.
    :type rec: ria_toolkit_oss.datatypes.Recording
    :param thumbnail: Whether to return a small thumbnail version or full plot.
    :type thumbnail: bool

    :return: Spectrogram, as a Plotly Figure.
    """
    complex_signal = rec.data[0]
    sample_rate = int(rec.metadata.get("sample_rate", 1))
    plot_length = len(complex_signal)

    # Determine FFT size
    if plot_length < 2000:
        fft_size = 64
    elif plot_length < 10000:
        fft_size = 256
    elif plot_length < 1000000:
        fft_size = 1024
    else:
        fft_size = 2048

    frequencies, times, Sxx = signal.spectrogram(
        complex_signal,
        fs=sample_rate,
        nfft=fft_size,
        nperseg=fft_size,
        noverlap=fft_size // 8,
        scaling="density",
        mode="complex",
        return_onesided=False,
    )

    # Convert complex values to amplitude and then to log scale for visualization
    Sxx_magnitude = np.abs(Sxx)
    Sxx_log = np.log10(Sxx_magnitude + 1e-6)

    # Normalize spectrogram values between 0 and 1 for plotting
    Sxx_log_shifted = Sxx_log - np.min(Sxx_log)
    Sxx_log_norm = Sxx_log_shifted / np.max(Sxx_log_shifted)

    # Shift frequency bins and spectrogram rows so frequencies run from negative to positive
    frequencies_shifted = np.fft.fftshift(frequencies)
    Sxx_shifted = np.fft.fftshift(Sxx_log_norm, axes=0)

    fig = go.Figure(
        data=go.Heatmap(
            z=Sxx_shifted,
            x=times / 1e6,
            y=frequencies_shifted,
            colorscale="Viridis",
            zmin=0,
            zmax=1,
            reversescale=False,
            showscale=False,
        )
    )

    if thumbnail:
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)
        fig.update_layout(
            template="plotly_dark",
            width=200,
            height=100,
            margin=dict(l=5, r=5, t=5, b=5),
            xaxis=dict(scaleanchor=None),
            yaxis=dict(scaleanchor=None),
        )
    else:
        fig.update_layout(
            title="Spectrogram",
            xaxis_title="Time [s]",
            yaxis_title="Frequency [Hz]",
            template="plotly_dark",
            height=300,
            width=800,
        )

    return fig


def iq_time_series(rec: Recording) -> Figure:
    """Create a time series plot of the real and imaginary parts of signal.

    :param rec: Signal to plot.
    :type rec: ria_toolkit_oss.datatypes.Recording

    :return: Time series plot, as a Plotly Figure.
    """
    complex_signal = rec.data[0]
    sample_rate = int(rec.metadata.get("sample_rate", 1))
    plot_length = len(complex_signal)
    t = np.arange(0, plot_length, 1) / sample_rate

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=complex_signal.real, mode="lines", name="I (In-phase)", line=dict(width=0.6)))
    fig.add_trace(go.Scatter(x=t, y=complex_signal.imag, mode="lines", name="Q (Quadrature)", line=dict(width=0.6)))

    fig.update_layout(
        title="IQ Time Series",
        xaxis_title="Time [s]",
        yaxis_title="Amplitude",
        template="plotly_dark",
        height=300,
        width=800,
        showlegend=True,
    )

    return fig


def frequency_spectrum(rec: Recording) -> Figure:
    """Create a frequency spectrum plot from the recording.

    :param rec: Input signal to plot.
    :type rec: ria_toolkit_oss.datatypes.Recording

    :return: Frequency spectrum, as a Plotly figure.
    """
    complex_signal = rec.data[0]
    center_frequency = int(rec.metadata.get("center_frequency", 0))
    sample_rate = int(rec.metadata.get("sample_rate", 1))

    epsilon = 1e-10
    spectrum = np.abs(fftshift(fft(complex_signal)))
    freqs = np.linspace(-sample_rate / 2, sample_rate / 2, len(complex_signal)) + center_frequency
    log_spectrum = np.log10(spectrum + epsilon)
    scaled_log_spectrum = (log_spectrum - log_spectrum.min()) / (log_spectrum.max() - log_spectrum.min())

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=freqs, y=scaled_log_spectrum, mode="lines", name="Spectrum", line=dict(width=0.4)))

    fig.update_layout(
        title="Frequency Spectrum",
        xaxis_title="Frequency [Hz]",
        yaxis_title="Magnitude",
        yaxis_type="log",
        template="plotly_dark",
        height=300,
        width=800,
        showlegend=False,
    )

    return fig


def constellation(rec: Recording) -> Figure:
    """Create a constellation plot from the recording.

    :param rec: Input signal to plot.
    :type rec: ria_toolkit_oss.datatypes.Recording

    :return: Constellation, as a Plotly Figure.
    """
    complex_signal = rec.data[0]

    # Downsample the IQ samples to a target number of points. This reduces the amount of data plotted,
    #  improving performance and interactivity without losing significant detail in the constellation visualization.
    target_number_of_points = 5000
    step = max(1, len(complex_signal) // target_number_of_points)
    i_ds = complex_signal.real[::step]
    q_ds = complex_signal.imag[::step]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=i_ds, y=q_ds, mode="lines", name="Constellation", line=dict(width=0.2)))

    fig.update_layout(
        title="Constellation",
        xaxis_title="In-phase (I)",
        yaxis_title="Quadrature (Q)",
        template="plotly_dark",
        height=400,
        width=400,
        showlegend=False,
        xaxis=dict(range=[-1.1, 1.1]),
        yaxis=dict(range=[-1.1, 1.1]),
    )

    return fig
