"""
This submodule comprises various transforms designed to represent signal impairments.
These transforms take a recording as input and return a corresponding recording with
the impairment model applied; we call the latter an impaired recording.

Signals travel through transmission media, which are not perfect. The imperfection
causes signal impairment, meaning that the signal at the beginning of the medium is
not the same as the signal at the end of the medium. What is sent is not what is received.
Three causes of impairment are attenuation, distortion, and noise.
"""

from typing import Optional

import numpy as np
from numpy.typing import ArrayLike
from scipy.signal import resample_poly

from ria_toolkit_oss.datatypes import Recording
from ria_toolkit_oss.transforms import iq_augmentations


def add_awgn_to_signal(signal: ArrayLike | Recording, snr: Optional[float] = 1) -> np.ndarray | Recording:
    """Generates additive white gaussian noise (AWGN) relative to the signal-to-noise ratio (SNR) of the
    provided `signal` array or `Recording`.

    This function calculates the root mean squared (RMS) power of `signal` and then finds the RMS power of the noise
    which matches the specified SNR. Then, the AWGN is generated after calculating the variance and randomly
    calculating the amplitude and phase of the noise. Then, this generated AWGN is added to the original signal and
    returned.

    :param signal: Input IQ data as a complex ``C x N`` array or `Recording`, where ``C`` is the number of channels
        and ``N`` is the length of the IQ examples.
    :type signal: array_like or ria_toolkit_oss.datatypes.Recording
    :param snr: The signal-to-noise ratio in dB. Default is 1.
    :type snr: float, optional

    :raises ValueError: If `signal` is not CxN complex.

    :return: A numpy array which is the sum of the noise (which matches the SNR) and the original signal. If `signal`
        is a `Recording`, returns a `Recording object` with its `data` attribute containing the noisy signal array.
    :rtype: np.ndarray or ria_toolkit_oss.datatypes.Recording

    >>> rec = Recording(data=[[1+1j, 2+2j]])
    >>> new_rec = add_awgn_to_signal(rec)
    >>> new_rec.data
    array([[0.83141973+0.32529242j, -1.00909846+2.39282713j]])
    """

    if isinstance(signal, Recording):
        data = signal.data
    else:
        data = np.asarray(signal)

    if data.ndim != 2 or not np.iscomplexobj(data):
        raise ValueError("signal must be CxN complex.")

    noise = iq_augmentations.generate_awgn(signal=data, snr=snr)
    print(f"noise is {noise}")

    noisy_signal = data + noise

    if isinstance(signal, Recording):
        return Recording(data=noisy_signal, metadata=signal.metadata)
    else:
        return noisy_signal


def time_shift(signal: ArrayLike | Recording, shift: Optional[int] = 1) -> np.ndarray | Recording:
    """Apply a time shift to a signal.

    After the time shift is applied, we fill any empty regions with zeros.

    :param signal: Input IQ data as a complex CxN array or `Recording`, where C is the number of channels and N
        is the length of the IQ examples.
    :type signal: array_like or ria_toolkit_oss.datatypes.Recording
    :param shift: The number of indices to shift by. Default is 1.
    :type shift: int, optional

    :raises ValueError: If `signal` is not CxN complex.
    :raises UserWarning: If `shift` is greater than length of `signal`.

    :return: A numpy array which represents the time-shifted signal. If `signal` is a `Recording`,
        returns a `Recording object` with its `data` attribute containing the time-shifted array.
    :rtype: np.ndarray or ria_toolkit_oss.datatypes.Recording

    >>> rec = Recording(data=[[1+1j, 2+2j, 3+3j, 4+4j, 5+5j]])
    >>> new_rec = time_shift(rec, -2)
    >>> new_rec.data
    array([[3+3j, 4+4j, 5+5j, 0+0j, 0+0j]])
    """
    # TODO: Additional info needs to be added to docstring description

    if isinstance(signal, Recording):
        data = signal.data
    else:
        data = np.asarray(signal)

    if data.ndim == 2 and np.iscomplexobj(data):
        c, n = data.shape
    else:
        raise ValueError("signal must be CxN complex.")

    if shift > n:
        raise UserWarning("shift is greater than signal length")

    shifted_data = np.zeros_like(data)

    if c == 1:
        # New iq array shifted left or right depending on sign of shift
        # This should work even if shift > iqdata.shape[1]
        if shift >= 0:
            # Shift to right
            shifted_data[:, shift:] = data[:, :-shift]

        else:
            # Shift to the left
            shifted_data[:, :shift] = data[:, -shift:]
    else:
        raise NotImplementedError

    if isinstance(signal, Recording):
        return Recording(data=shifted_data, metadata=signal.metadata)
    else:
        return shifted_data


def frequency_shift(signal: ArrayLike | Recording, shift: Optional[float] = 0.5) -> np.ndarray | Recording:
    """Apply a frequency shift to a signal.

    .. note::

        The frequency shift is applied relative to the sample rate.

    :param signal: Input IQ data as a complex CxN array or `Recording`, where C is the number of channels and N
        is the length of the IQ examples.
    :type signal: array_like or ria_toolkit_oss.datatypes.Recording
    :param shift: The frequency shift relative to the sample rate. Must be in the range ``[-0.5, 0.5]``.
        Default is 0.5.
    :type shift: float, optional

    :raises ValueError: If the provided frequency shift is not in the range ``[-0.5, 0.5]``.
    :raises ValueError: If `signal` is not CxN complex.

    :return: A numpy array which represents the frequency-shifted signal. If `signal` is a `Recording`,
        returns a `Recording object` with its `data` attribute containing the frequency-shifted array.
    :rtype: np.ndarray or ria_toolkit_oss.datatypes.Recording

    >>> rec = Recording(data=[[1+1j, 2+2j, 3+3j, 4+4j]])
    >>> new_rec = frequency_shift(rec, -0.4)
    >>> new_rec.data
    array([[1+1j, -0.44246348-2.79360449j, -1.92611857+3.78022053j, 5.04029404-2.56815809j]])
    """
    # TODO: Additional info needs to be added to docstring description

    if shift > 0.5 or shift < -0.5:
        raise ValueError("Frequency shift must be in the range [-0.5, 0.5]")

    if isinstance(signal, Recording):
        data = signal.data
    else:
        data = np.asarray(signal)

    if data.ndim == 2 and np.iscomplexobj(data):
        c, n = data.shape
    else:
        raise ValueError("signal must be CxN complex.")

    shifted_data = np.zeros_like(data)

    if c == 1:
        # Calculate the phase shift for the frequency shift
        phase_shift_ = 2.0 * np.pi * shift * np.arange(n)

        # Use trigonometric identities to apply the frequency shift
        shifted_data.real = data.real * np.cos(phase_shift_) - data.imag * np.sin(phase_shift_)
        shifted_data.imag = data.real * np.sin(phase_shift_) + data.imag * np.cos(phase_shift_)
    else:
        raise NotImplementedError

    if isinstance(signal, Recording):
        return Recording(data=shifted_data, metadata=signal.metadata)
    else:
        return shifted_data


def phase_shift(signal: ArrayLike | Recording, phase: Optional[float] = np.pi) -> np.ndarray | Recording:
    """Apply a phase shift to a signal.

    :param signal: Input IQ data as a complex CxN array or `Recording`, where C is the number of channels and N
        is the length of the IQ examples.
    :type signal: array_like or ria_toolkit_oss.datatypes.Recording
    :param phase: The phase angle by which to rotate the IQ samples, in radians. Must be in the range ``[-π, π]``.
        Default is π.
    :type phase: float, optional

    :raises ValueError: If the provided phase rotation is not in the range ``[-π, π]``.
    :raises ValueError: If `signal` is not CxN complex.

    :return: A numpy array which represents the phase-shifted signal. If `signal` is a `Recording`,
        returns a `Recording object` with its `data` attribute containing the phase-shifted array.
    :rtype: np.ndarray or ria_toolkit_oss.datatypes.Recording

    >>> rec = Recording(data=[[1+1j, 2+2j, 3+3j, 4+4j]])
    >>> new_rec = phase_shift(rec, np.pi/2)
    >>> new_rec.data
    array([[-1+1j, -2+2j -3+3j -4+4j]])
    """
    # TODO: Additional info needs to be added to docstring description

    if phase > np.pi or phase < -np.pi:
        raise ValueError("Phase rotation must be in the range [-π, π]")

    if isinstance(signal, Recording):
        data = signal.data
    else:
        data = np.asarray(signal)

    if data.ndim == 2 and np.iscomplexobj(data):
        c, n = data.shape
    else:
        raise ValueError("signal must be CxN complex.")

    if c == 1:
        shifted_data = data * np.exp(1j * phase)
    else:
        raise NotImplementedError

    if isinstance(signal, Recording):
        return Recording(data=shifted_data, metadata=signal.metadata)
    else:
        return shifted_data


def iq_imbalance(
    signal: ArrayLike | Recording,
    amplitude_imbalance: Optional[float] = 1.5,
    phase_imbalance: Optional[float] = np.pi,
    dc_offset: Optional[float] = 1.5,
) -> np.ndarray | Recording:
    """Apply an IQ Imbalance to a signal.

    .. note::

        Based on MathWorks' `I/Q Imbalance <https://www.mathworks.com/help/comm/ref/iqimbalance.html>`_.

    :param signal: Input IQ data as a complex CxN array or `Recording`, where C is the number of channels and N
        is the length of the IQ examples.
    :type signal: array_like or ria_toolkit_oss.datatypes.Recording
    :param amplitude_imbalance: The IQ amplitude imbalance to apply, in dB. Default is 1.5.
    :type amplitude_imbalance: float, optional
    :param phase_imbalance: The IQ phase imbalance to apply, in radians. Default is π.
         Must be in the range ``[-π, π]``.
    :type phase_imbalance: float, optional
    :param dc_offset: The IQ DC offset to apply, in dB. Default is 1.5.
    :type dc_offset: float, optional

    :raises ValueError: If the phase imbalance is not in the range ``[-π, π]``.
    :raises ValueError: If `signal` is not CxN complex.

    :return: A numpy array which is the original signal with an applied IQ imbalance. If `signal` is a `Recording`,
        returns a `Recording object` with its `data` attribute containing the IQ imbalanced signal array.
    :rtype: np.ndarray or ria_toolkit_oss.datatypes.Recording

    >>> rec = Recording(data=[[2+18j, -34+2j, 3+9j]])
    >>> new_rec = iq_imbalance(rec, 1, np.pi, 2)
    >>> new_rec.data
    array([[-38.38613587-4.78555031j, -4.26512621+81.35435535j, -19.19306793-7.17832547j]])
    """
    # TODO: Additional info needs to be added to docstring description

    if phase_imbalance > np.pi or phase_imbalance < -np.pi:
        raise ValueError("Phase imbalance must be in the range [-π, π].")

    if isinstance(signal, Recording):
        data = signal.data
    else:
        data = np.asarray(signal)

    if data.ndim == 2 and np.iscomplexobj(data):
        c, n = data.shape
    else:
        raise ValueError("signal must be CxN complex.")

    if c == 1:
        # Apply amplitude imbalance
        data = (
            10 ** (0.5 * amplitude_imbalance / 20.0) * data.real
            + 1j * 10 ** (-0.5 * amplitude_imbalance / 20.0) * data.imag
        )

        # Apply phase imbalance
        data = (
            np.exp(-1j * phase_imbalance / 2.0) * data.real
            + np.exp(1j * (np.pi / 2.0 + phase_imbalance / 2.0)) * data.imag
        )

        # Apply DC offset
        imbalanced_data = data + (10 ** (dc_offset / 20.0) * data.real + 1j * 10 ** (dc_offset / 20.0) * data.imag)
    else:
        raise NotImplementedError

    if isinstance(signal, Recording):
        return Recording(data=imbalanced_data, metadata=signal.metadata)
    else:
        return imbalanced_data


def resample(signal: ArrayLike | Recording, up: Optional[int] = 4, down: Optional[int] = 2) -> np.ndarray | Recording:
    """Resample a signal using polyphase filtering.

    Uses scipy.signal.resample_poly to upsample the signal by the
    factor *up*, apply a zero-phase low-pass FIR filter, and downsample the
    signal by the factor *down*.

    :param signal: Input IQ data as a complex CxN array or `Recording`, where C is the number of channels and N
        is the length of the IQ examples.
    :type signal: array_like or ria_toolkit_oss.datatypes.Recording
    :param up: The upsampling factor. Default is 4.
    :type up: int, optional
    :param down: The downsampling factor. Default is 2.
    :type down: int, optional

    :raises ValueError: If `signal` is not CxN complex.

    :return: A numpy array which represents the resampled signal If `signal` is a `Recording`,
        returns a `Recording object` with its `data` attribute containing the resampled array.
    :rtype: np.ndarray or ria_toolkit_oss.datatypes.Recording

    >>> rec = Recording(data=[[1+1j, 2+2j]])
    >>> new_rec = resample(rec, 2, 1)
    >>> new_rec.data
    array([[1.00051747+1.00051747j, 1.90020207+1.90020207j]])
    """
    # TODO: Additional info needs to be added to docstring description

    if isinstance(signal, Recording):
        data = signal.data
    else:
        data = np.asarray(signal)

    if data.ndim == 2 and np.iscomplexobj(data):
        c, n = data.shape
    else:
        raise ValueError("signal must be CxN complex.")

    if c == 1:
        data = np.squeeze(data)
        resampled_iqdata = resample_poly(x=data, up=up, down=down)

        # Reshape array so that slicing operations work on resampled data
        resampled_iqdata = np.reshape(resampled_iqdata, newshape=(1, len(resampled_iqdata)))

        if resampled_iqdata.shape[1] > n:
            resampled_iqdata = resampled_iqdata[:, :n]

        else:
            empty_array = np.zeros(resampled_iqdata.shape, dtype=resampled_iqdata.dtype)
            empty_array[:, : resampled_iqdata.shape[1]] = resampled_iqdata
    else:
        raise NotImplementedError

    if isinstance(signal, Recording):
        return Recording(data=resampled_iqdata, metadata=signal.metadata)
    else:
        return resampled_iqdata
