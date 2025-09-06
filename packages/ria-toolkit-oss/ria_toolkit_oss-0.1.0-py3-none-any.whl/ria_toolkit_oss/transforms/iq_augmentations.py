"""
This submodule comprises the functionals of various transforms designed to create new training examples by augmenting
existing examples or recordings using a variety of techniques These transforms take an ArrayLike object as input
and return a corresponding numpy.ndarray with the impairment model applied;
we call the latter the impaired data.
"""

from typing import Optional

import numpy as np
from numpy.typing import ArrayLike

from ria_toolkit_oss.datatypes.recording import Recording
from ria_toolkit_oss.utils.array_conversion import convert_to_2xn

# TODO: For round 2 of index generation, should j be at min 2 spots away from where it was to prevent adjacent patches.

# TODO: All the transforms with some randomness need to be refactored to use a random generator.


def generate_awgn(signal: ArrayLike | Recording, snr: Optional[float] = 1) -> np.ndarray | Recording:
    """Generates additive white gaussian noise (AWGN) relative to the signal-to-noise ratio (SNR) of the
    provided `signal` array or `Recording`.

    This function calculates the root mean squared (RMS) power of `signal` and then finds the RMS power of
    the noise which matches the specified SNR. Then, the AWGN is generated after calculating the variance and
    randomly calculating the amplitude and phase of the noise.

    :param signal: Input IQ data as a complex CxN array or `Recording`, where C is the number of channels and N
        is the length of the IQ examples.
    :type signal: array_like or ria_toolkit_oss.datatypes.Recording
    :param snr: The signal-to-noise ratio in dB. Default is 1.
    :type snr: float, optional

    :raises ValueError: If `signal` is not CxN complex.

    :return: A numpy array representing the generated noise which matches the SNR of `signal`. If `signal` is a
        Recording, returns a Recording object with its `data` attribute containing the generated noise array.
    :rtype: np.ndarray or ria_toolkit_oss.datatypes.Recording

    >>> rec = Recording(data=[[2 + 5j, 1 + 8j]])
    >>> new_rec = generate_awgn(rec)
    >>> new_rec.data
    array([[2.15991777 + 0.69673915j, 0.2814541 - 0.12111976j]])
    """

    if isinstance(signal, Recording):
        data = signal.data
    else:
        data = np.asarray(signal)

    if data.ndim == 2 and np.iscomplexobj(data):
        c, n = data.shape
    else:
        raise ValueError("signal must be CxN complex.")

    snr_linear = 10 ** (snr / 10)

    # Calculate the RMS power of the signal to solve for the RMS power of the noise
    signal_rms_power = np.sqrt(np.mean(np.abs(data) ** 2))
    noise_rms_power = signal_rms_power / snr_linear

    # Generate the AWGN noise which has the same shape as data
    variance = noise_rms_power**2
    magnitude = np.random.normal(loc=0, scale=np.sqrt(variance), size=(c, n))
    phase = np.random.uniform(low=0, high=2 * np.pi, size=(c, n))
    complex_awgn = magnitude * np.exp(1j * phase)

    if isinstance(signal, Recording):
        return Recording(data=complex_awgn, metadata=signal.metadata)
    else:
        return complex_awgn


def time_reversal(signal: ArrayLike | Recording) -> np.ndarray | Recording:
    """Reverses the order of the I (In-phase) and Q (Quadrature) data samples along the time axis of the provided
    `signal` array or `Recording`.

    :param signal: Input IQ data as a complex CxN array or `Recording`, where C is the number of channels and N
        is the length of the IQ examples.
    :type signal: array_like or ria_toolkit_oss.datatypes.Recording

    :raises ValueError: If `signal` is not CxN complex.

    :return: A numpy array containing the reversed I and Q data samples if `signal` is an array.
        If `signal` is a `Recording`, returns a `Recording` object with its `data` attribute containing the
        reversed array.
    :rtype: np.ndarray or ria_toolkit_oss.datatypes.Recording

    >>> rec = Recording(data=[[1+2j, 3+4j, 5+6j]])
    >>> new_rec = time_reversal(rec)
    >>> new_rec.data
    array([[5+6j, 3+4j, 1+2j]])
    """

    if isinstance(signal, Recording):
        data = signal.data
    else:
        data = np.asarray(signal)

    if data.ndim == 2 and np.iscomplexobj(data):
        c, n = data.shape
    else:
        raise ValueError("signal must be CxN complex.")

    if c == 1:
        # If 1xN complex
        reversed_data = np.squeeze(data)[::-1]
    else:
        raise NotImplementedError

    if isinstance(signal, Recording):
        return Recording(data=reversed_data, metadata=signal.metadata)
    else:
        return reversed_data.reshape(c, n)


def spectral_inversion(signal: ArrayLike | Recording) -> np.ndarray | Recording:
    """Negates the imaginary components (Q, Quadrature) of the data samples contained within the
    provided `signal` array or `Recording`.

    :param signal: Input IQ data as a complex CxN array or `Recording`, where C is the number of channels and N
        is the length of the IQ examples.
    :type signal: array_like or ria_toolkit_oss.datatypes.Recording

    :raises ValueError: If `signal` is not CxN complex.

    :return: A numpy array containing the original I and negated Q data samples if `signal` is an array.
        If `signal` is a `Recording`, returns a `Recording` object with its `data` attribute containing the
        inverted array.
    :rtype: np.ndarray or ria_toolkit_oss.datatypes.Recording

    >>> rec = Recording(data=[[0+45j, 2-10j]])
    >>> new_rec = spectral_inversion(rec)
    >>> new_rec.data
    array([[0-45j, 2+10j]])
    """

    if isinstance(signal, Recording):
        data = signal.data
    else:
        data = np.asarray(signal)

    if data.ndim == 2 and np.iscomplexobj(data):
        c, n = data.shape
    else:
        raise ValueError("signal must be CxN complex.")

    if c == 1:
        new_data = np.squeeze(data).real - 1j * np.squeeze(data).imag
    else:
        raise NotImplementedError

    if isinstance(signal, Recording):
        return Recording(data=new_data, metadata=signal.metadata)
    else:
        return new_data.reshape(c, n)


def channel_swap(signal: ArrayLike | Recording) -> np.ndarray | Recording:
    """Switches the I (In-phase) with the and Q (Quadrature) data samples for each sample within the
    provided `signal` array or `Recording`.

    :param signal: Input IQ data as a complex CxN array or `Recording`, where C is the number of channels and N
        is the length of the IQ examples.
    :type signal: array_like or ria_toolkit_oss.datatypes.Recording

    :raises ValueError: If `signal` is not CxN complex.

    :return: A numpy array containing the swapped I and Q data samples if `signal` is an array.
        If `signal` is a `Recording`, returns a `Recording` object with its `data` attribute containing the
        swapped array.
    :rtype: np.ndarray or ria_toolkit_oss.datatypes.Recording

    >>> rec = Recording(data=[[10+20j, 7+35j]])
    >>> new_rec = channel_swap(rec)
    >>> new_rec.data
    array([[20+10j, 35+7j]])
    """

    if isinstance(signal, Recording):
        data = signal.data
    else:
        data = np.asarray(signal)

    if data.ndim == 2 and np.iscomplexobj(data):
        c, n = data.shape
    else:
        raise ValueError("signal must be CxN complex.")

    if c == 1:
        swapped_data = np.squeeze(data).imag + 1j * np.squeeze(data).real
    else:
        raise NotImplementedError

    if isinstance(signal, Recording):
        return Recording(data=swapped_data, metadata=signal.metadata)
    else:
        return swapped_data.reshape(c, n)


def amplitude_reversal(signal: ArrayLike | Recording) -> np.ndarray | Recording:
    """Negates the amplitudes of both the I (In-phase) and Q (Quadrature) data samples contained within the
    provided `signal` array or `Recording`.

    :param signal: Input IQ data as a complex CxN array or `Recording`, where C is the number of channels and N
        is the length of the IQ examples.
    :type signal: array_like or ria_toolkit_oss.datatypes.Recording

    :raises ValueError: If `signal` is not CxN complex.

    :return: A numpy array containing the negated I and Q data samples if `signal` is an array.
        If `signal` is a `Recording`, returns a `Recording` object with its `data` attribute containing the
        negated array.
    :rtype: np.ndarray or ria_toolkit_oss.datatypes.Recording

    >>> rec = Recording(data=[[4-3j, -5-2j, -9+1j]])
    >>> new_rec = amplitude_reversal(rec)
    >>> new_rec.data
    array([[-4+3j, 5+2j, 9-1j]])
    """

    if isinstance(signal, Recording):
        data = signal.data
    else:
        data = np.asarray(signal)

    if data.ndim == 2 and np.iscomplexobj(data):
        c, n = data.shape
    else:
        raise ValueError("signal must be CxN complex.")

    if c == 1:
        reversed_data = -1 * np.squeeze(data).real - 1j * np.squeeze(data).imag
    else:
        raise NotImplementedError

    if isinstance(signal, Recording):
        return Recording(data=reversed_data, metadata=signal.metadata)
    else:
        return reversed_data.reshape(c, n)


def drop_samples(  # noqa: C901  # TODO: Simplify function
    signal: ArrayLike | Recording, max_section_size: Optional[int] = 2, fill_type: Optional[str] = "zeros"
) -> np.ndarray | Recording:
    """Randomly drops IQ data samples contained within the provided `signal` array or `Recording`.

    This function randomly selects sections of the signal and replaces the current data samples in the specified
    section with another value dependent on the fill type.

    :param signal: Input IQ data as a complex CxN array or `Recording`, where C is the number of channels and N
        is the length of the IQ examples.
    :type signal: array_like or ria_toolkit_oss.datatypes.Recording
    :param max_section_size: Maximum allowable size of the section to be dropped and replaced. Default is 2.
    :type max_section_size: int, optional
    :param fill_type: Fill option used to replace dropped section of data (back-fill, front-fill, mean, zeros).
        Default is "zeros".


        "back-fill": replace dropped section with the data sample occuring before the section.

        "front-fill": replace dropped section with the data sample occuring after the section.

        "mean": replace dropped section with mean of the entire signal.

        "zeros": replace dropped section with constant value of 0+0j.
    :type fill_type: str, optional

    :raises ValueError: If `signal` is not CxN complex.
    :raises ValueError: If `max_section_size` is less than 1 or greater than or equal to length of `signal`.

    :return: A numpy array containing the I and Q data samples with replaced subsections if
        `signal` is an array. If `signal` is a `Recording`, returns a `Recording` object with its `data`
        attribute containing the array with dropped samples.
    :rtype: np.ndarray or ria_toolkit_oss.datatypes.Recording

    >>> rec = Recording(data=[[2+5j, 1+8j, 6+4j, 3+7j, 4+9j]])
    >>> new_rec = drop_samples(rec)
    >>> new_rec.data
    array([[2+5j, 0, 0, 0, 4+9j]])
    """
    if isinstance(signal, Recording):
        data = signal.data
    else:
        data = np.asarray(signal)

    if data.ndim == 2 and np.iscomplexobj(data):
        c, n = data.shape
    else:
        raise ValueError("signal must be CxN complex.")

    if max_section_size < 1 or max_section_size >= n:
        raise ValueError("max_section_size must be at least 1 and must be less than the length of signal.")

    if c == 1:
        data = np.squeeze(data)

        if fill_type == "mean":
            mean = np.mean(data)

        i = -1
        j = -1

        # Pointers i and j point to exact positions
        while i < n:
            # Generate valid starting point so that at least 1 drop occurs
            i = np.random.randint(j + 1, j + n - max_section_size + 2)
            j = np.random.randint(i, i + max_section_size)

            if j > n - 1:  # Check that the full drop is within the dataset
                break

            # Generate fill based on fill_type
            if fill_type == "back-fill":
                fill = data[i - 1] if i > 0 else data[i]
            elif fill_type == "front-fill":
                fill = data[j + 1] if j < n - 1 else data[j]
            elif fill_type == "mean":
                fill = mean
            elif fill_type == "zeros":
                fill = 0 + 0j
            else:
                raise ValueError(f"fill_type {fill_type} not recognized.")

            # Replaces dropped samples with fill values
            data[i : j + 1] = fill
    else:
        raise NotImplementedError

    if isinstance(signal, Recording):
        return Recording(data=data, metadata=signal.metadata)
    else:
        return data.reshape(c, n)


def quantize_tape(
    signal: ArrayLike | Recording, bin_number: Optional[int] = 4, rounding_type: Optional[str] = "floor"
) -> np.ndarray | Recording:
    """Quantizes the IQ data of the provided `signal` array or `Recording` by a few bits.

    This function emulates an analog-to-digital converter (ADC) which is commonly seen in digital RF systems.
    The relationship between the number of bins and number of bits is: log(# of bins) / log(2) = # of bits.

    :param signal: Input IQ data as a complex CxN array or `Recording`, where C is the number of channels and N
        is the length of the IQ examples.
    :type signal: array_like or ria_toolkit_oss.datatypes.Recording
    :param bin_number: The number of bins the signal should be divided into. Default is 4.
    :type bin_number: int, optional
    :param rounding_type: The type of rounding applied during processing. Default is "floor".

        "floor": rounds down to the lower bound of the bin.

        "ceiling": rounds up to the upper bound of the bin.
    :type rounding_type: str, optional

    :raises ValueError: If `signal` is not CxN complex.
    :raises UserWarning: If `rounding_type` is not "floor" or "ceiling", "floor" is selected by default.

    :return: A numpy array containing the quantized I and Q data samples if `signal` is an array.
        If `signal` is a `Recording`, returns a `Recording` object with its `data` attribute containing
        the quantized array.
    :rtype: np.ndarray or ria_toolkit_oss.datatypes.Recording

    >>> rec = Recording(data=[[1+1j, 4+4j, 1+2j, 1+4j]])
    >>> new_rec = quantize_tape(rec)
    >>> new_rec.data
    array([[4+4j, 3+3j, 4+1j, 4+3j]])
    """
    if isinstance(signal, Recording):
        data = signal.data
    else:
        data = np.asarray(signal)

    if data.ndim == 2 and np.iscomplexobj(data):
        c, n = data.shape
    else:
        raise ValueError("signal must be CxN complex.")

    if rounding_type not in {"ceiling", "floor"}:
        raise UserWarning('rounding_type must be either "floor" or "ceiling", floor has been selected by default')

    if c == 1:
        iq_data = convert_to_2xn(data)
        maximum, minimum = iq_data.max(), iq_data.min()
        bin_edges = np.linspace(minimum, maximum, bin_number + 1)
        indices = np.digitize(iq_data, bin_edges, right=True)

        # If data falls outside the first bin, map it back into the first bin, data will not fall outside of last bin
        indices[indices == 0] = 1

        # Map the data points to the correct bins
        if rounding_type == "ceiling":
            modified_iq_data = bin_edges[indices]
        else:
            modified_iq_data = bin_edges[indices - 1]

        new_data = modified_iq_data[0] + 1j * modified_iq_data[1]
    else:
        raise NotImplementedError

    if isinstance(signal, Recording):
        return Recording(data=new_data, metadata=signal.metadata)
    else:
        return new_data.reshape(c, n)


def quantize_parts(
    signal: ArrayLike | Recording,
    max_section_size: Optional[int] = 2,
    bin_number: Optional[int] = 4,
    rounding_type: Optional[str] = "floor",
) -> np.ndarray | Recording:
    """Quantizes random parts of the IQ data within the provided `signal` array or `Recording` by a few bits.

    This function emulates an analog-to-digital converter (ADC) which is commonly seen in digital RF systems.
    The relationship between the number of bins and number of bits is: log(# of bins) / log(2) = # of bits.

    :param signal: Input IQ data as a complex CxN array or `Recording`, where C is the number of channels and N
        is the length of the IQ examples.
    :type signal: array_like or ria_toolkit_oss.datatypes.Recording
    :param max_section_size: Maximum allowable size of the section to be quantized. Default is 2.
    :type max_section_size: int, optional
    :param bin_number: The number of bins the signal should be divided into. Default is 4.
    :type bin_number: int, optional
    :param rounding_type: Type of rounding applied during processing. Default is "floor".

        "floor": rounds down to the lower bound of the bin.

        "ceiling": rounds up to the upper bound of the bin.
    :type rounding_type: str, optional

    :raises ValueError: If `signal` is not CxN complex.
    :raises UserWarning: If `rounding_type` is not "floor" or "ceiling", "floor" is selected by default.

    :return: A numpy array containing the I and Q data samples with quantized subsections if `signal`
        is an array. If `signal` is a `Recording`, returns a `Recording` object with its `data` attribute
        containing the partially quantized array.
    :rtype: np.ndarray or ria_toolkit_oss.datatypes.Recording

    >>> rec = Recording(data=[[2+5j, 1+8j, 6+4j, 3+7j, 4+9j]])
    >>> new_rec = quantize_parts(rec)
    >>> new_rec.data
    array([[2+5j, 1+8j, 3.66666667+3.66666667j, 3+7j, 4+9j]])
    """

    if isinstance(signal, Recording):
        data = signal.data
    else:
        data = np.asarray(signal)

    if data.ndim == 2 and np.iscomplexobj(data):
        c, n = data.shape
    else:
        raise ValueError("signal must be CxN complex.")

    if rounding_type not in {"ceiling", "floor"}:
        raise UserWarning('rounding_type must be either "floor" or "ceiling", floor has been selected by default')

    if c == 1:
        iq_data = convert_to_2xn(data)
        i_data, q_data = iq_data
        maximum, minimum = iq_data.max(), iq_data.min()
        bin_edges = np.linspace(minimum, maximum, bin_number + 1)
        indices = np.digitize(iq_data, bin_edges, right=True)

        # Map everything from bin 0 to bin 1
        indices[indices == 0] = 1

        i = -1
        j = -1

        # Pointers i and j point to exact positions
        while i < n:
            # Generate valid starting point so that at least 1 drop occurs
            i = np.random.randint(j + 1, j + n - max_section_size + 2)
            j = np.random.randint(i, i + max_section_size)

            if j > n - 1:  # Check that the full drop is within the dataset
                break

            if rounding_type == "ceiling":
                i_data[i : j + 1] = bin_edges[indices[0][i : j + 1]]
                q_data[i : j + 1] = bin_edges[indices[1][i : j + 1]]
            else:
                i_data[i : j + 1] = bin_edges[indices[0][i : j + 1] - 1]
                q_data[i : j + 1] = bin_edges[indices[1][i : j + 1] - 1]

        quantized_data = i_data + 1j * q_data
    else:
        raise NotImplementedError

    if isinstance(signal, Recording):
        return Recording(data=quantized_data, metadata=signal.metadata)
    else:
        return quantized_data.reshape(c, n)


def magnitude_rescale(
    signal: ArrayLike | Recording,
    starting_bounds: Optional[tuple] = None,
    max_magnitude: Optional[int] = 1,
) -> np.ndarray | Recording:
    """Selects a random starting point from within the specified starting bounds and multiplies IQ data of the
    provided `signal` array or `Recording` by a random constant.

    :param signal: Input IQ data as a complex CxN array or `Recording`, where C is the number of channels and N
        is the length of the IQ examples.
    :type signal: array_like or ria_toolkit_oss.datatypes.Recording
    :param starting_bounds: The bounds (inclusive) as indices in which the starting position of the rescaling occurs.
        Default is None, but if user does not assign any bounds, the bounds become (random index, N-1).
    :type starting_bounds: tuple, optional
    :param max_magnitude: The maximum value of the constant that is used to rescale the data. Default is 1.
    :type max_magnitude: int, optional

    :raises ValueError: If `signal` is not CxN complex.

    :return: A numpy array containing the I and Q data samples with the rescaled magnitude after the random
        starting point if `signal` is an array. If `signal` is a `Recording`, returns a `Recording`
        object with its `data` attribute containing the rescaled array.
    :rtype: np.ndarray or ria_toolkit_oss.datatypes.Recording

    >>> rec = Recording(data=[[2+5j, 1+8j, 6+4j, 3+7j, 4+9j]])
    >>> new_rec = magniute_rescale(rec)
    >>> new_rec.data
    array([[2+5j, 1+8j, 6+4j, 3+7j, 3.03181761+6.82158963j]])
    """

    if isinstance(signal, Recording):
        data = signal.data
    else:
        data = np.asarray(signal)

    if data.ndim == 2 and np.iscomplexobj(data):
        c, n = data.shape
    else:
        raise ValueError("signal must be CxN complex.")

    if starting_bounds is None:
        starting_bounds = (np.random.randint(0, n), n - 1)

    if starting_bounds[0] < 0 or starting_bounds[1] > n - 1:
        raise ValueError("starting_bounds must be valid indices for the dataset.")

    if c == 1:
        data = np.squeeze(data)
        starting_point = np.random.randint(starting_bounds[0], starting_bounds[1] + 1)
        magnitude = np.random.rand() * max_magnitude

        rescaled_section = data[starting_point:] * magnitude
        rescaled_data = np.concatenate((data[:starting_point], rescaled_section))
    else:
        raise NotImplementedError

    if isinstance(signal, Recording):
        return Recording(data=rescaled_data, metadata=signal.metadata)
    else:
        return rescaled_data.reshape(c, n)


def cut_out(  # noqa: C901  # TODO: Simplify function
    signal: ArrayLike | Recording, max_section_size: Optional[int] = 3, fill_type: Optional[str] = "ones"
) -> np.ndarray | Recording:
    """Cuts out random sections of IQ data and replaces them with either 0s, 1s, or low, average, or high
    sound-to-noise ratio (SNR) additive white gausssian noise (AWGN) within the provided `signal` array or
    `Recording`.

    :param signal: Input IQ data as a complex CxN array or `Recording`, where C is the number of channels and N
        is the length of the IQ examples.
    :type signal: array_like or ria_toolkit_oss.datatypes.Recording
    :param max_section_size: Maximum allowable size of the section to be quantized. Default is 3.
    :type max_section_size: int, optional
    :param fill_type: Fill option used to replace cutout section of data (zeros, ones, low-snr, avg-snr-1, avg-snr-2).
        Default is "ones".

        "zeros": replace cutout section with 0s.

        "ones": replace cutout section with 1s.

        "low-snr": replace cutout section with AWGN with an SNR of 0.5.

        "avg-snr": replace cutout section with AWGN with an SNR of 1.

        "high-snr": replace cutout section with AWGN with an SNR of 2.
    :type fill_type: str, optional

    :raises ValueError: If `signal` is not CxN complex.
    :raises UserWarning: If fill_type is not "zeros", "ones", "low-snr", "avg-snr", or "high-snr", "ones" is selected
        by default.
    :raises ValueError: If `max_section_size` is less than 1 or greater than or equal to length of `signal`.

    :return: A numpy array containing the I and Q data samples with random sections cut out and replaced according to
        `fill_type` if `signal` is an array. If `signal` is a `Recording`, returns a `Recording` object
        with its `data` attribute containing the cut out and replaced array.
    :rtype: np.ndarray or ria_toolkit_oss.datatypes.Recording

    >>> rec = Recording(data=[[2+5j, 1+8j, 6+4j, 3+7j, 4+9j]])
    >>> new_rec = cut_out(rec)
    >>> new_rec.data
    array([[2+5j, 1+8j, 1+1j, 1+1j, 1+1j]])
    """
    if isinstance(signal, Recording):
        data = signal.data
    else:
        data = np.asarray(signal)

    if data.ndim == 2 and np.iscomplexobj(data):
        c, n = data.shape
    else:
        raise ValueError("signal must be CxN complex.")

    if fill_type not in {"zeros", "ones", "low-snr", "avg-snr", "high-snr"}:
        raise UserWarning(
            """fill_type must be "zeros", "ones", "low-snr", "avg-snr", or "high-snr",
            "ones" has been selected by default"""
        )

    if max_section_size < 1 or max_section_size >= n:
        raise ValueError("max_section_size must be at least 1 and must be less than the length of signal.")

    if c == 1:
        data = np.squeeze(data)

        i = -1
        j = -1

        # Pointers i and j point to exact positions
        while i < n:
            # Generate valid starting point so that at least 1 drop occurs
            i = np.random.randint(j + 1, j + n - max_section_size + 2)
            j = np.random.randint(i, i + max_section_size)

            if j > n - 1:  # Check that the full drop is within the dataset
                break

            # TODO: Check if we can collapse last three options which depends on what snr value the user enters
            if fill_type == "zeros":
                fill = 0 + 0j
            elif fill_type == "ones":
                fill = 1 + 1j
            elif fill_type == "low-snr":
                fill = generate_awgn([data[i : j + 1]], 0.5)
            elif fill_type == "avg-snr":
                fill = generate_awgn([data[i : j + 1]], 1)
            else:
                fill = generate_awgn([data[i : j + 1]], 2)

            data[i : j + 1] = fill
    else:
        raise NotImplementedError

    if isinstance(signal, Recording):
        return Recording(data=data, metadata=signal.metadata)
    else:
        return data.reshape(c, n)


def patch_shuffle(signal: ArrayLike | Recording, max_patch_size: Optional[int] = 3) -> np.ndarray | Recording:
    """Selects random patches of the IQ data and randomly shuffles the data samples within the specified patch of
    the provided `signal` array or `Recording`.

    :param signal: Input IQ data as a complex CxN array or `Recording`, where C is the number of channels and N
        is the length of the IQ examples.
    :type signal: array_like or ria_toolkit_oss.datatypes.Recording
    :param max_patch_size: Maximum allowable patch size of the data that can be shuffled. Default is 3.
    :type max_patch_size: int, optional

    :raises ValueError: If `signal` is not CxN complex.
    :raises ValueError: If `max_patch_size` is less than or equal to 1 or greater than length of `signal`.

    :return: A numpy array containing the I and Q data samples with randomly shuffled regions if `signal` is
        an array. If `signal` is a `Recording`, returns a `Recording` object with its `data` attribute containing
        the shuffled array.
    :rtype: np.ndarray or ria_toolkit_oss.datatypes.Recording

    >>> rec = Recording(data=[[2+5j, 1+8j, 6+4j, 3+7j, 4+9j]])
    >>> new_rec = patch_shuffle(rec)
    >>> new_rec.data
    array([[2+5j, 1+8j, 3+4j, 6+9j, 4+7j]])
    """
    if isinstance(signal, Recording):
        data = signal.data.copy()  # Cannot shuffle read-only array.
    else:
        data = np.asarray(signal)

    if data.ndim == 2 and np.iscomplexobj(data):
        c, n = data.shape
    else:
        raise ValueError("signal must be CxN complex.")

    if max_patch_size > n or max_patch_size <= 1:
        raise ValueError("max_patch_size must be less than or equal to the length of signal and greater than 1.")

    if c == 1:
        data = np.squeeze(data)

        i = -1
        j = -1

        # Pointers i and j point to exact positions
        while i < n:
            # Generate valid starting point so that at least 1 drop occurs
            i = np.random.randint(j + 1, j + n - max_patch_size + 2)
            j = np.random.randint(i, i + max_patch_size)

            if j > n - 1:  # Check that the full drop is within the dataset
                break

            np.random.shuffle(data.real[i : j + 1])
            np.random.shuffle(data.imag[i : j + 1])
    else:
        raise NotImplementedError

    if isinstance(signal, Recording):
        return Recording(data=data, metadata=signal.metadata)
    else:
        return data.reshape(c, n)
