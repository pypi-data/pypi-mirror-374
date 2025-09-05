#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions required to extract signal features.

Created on Thu Apr  3 10:10:59 2025
@author: thibaut
"""


import numpy as np
from numpy import ma
import pandas as pd
from scipy.integrate import trapezoid
from scipy.signal import find_peaks, periodogram, welch, windows

from .utils import scientific_round


def compute_sampling_rate(x):
    """
    To get the sampling rate of a time vector x.

    Args:
    ----
        x (array): a time vector in seconds format ([0.001, 0.002, 0.003, ..]).

    Returns:
    -------
        int: the sampling rate in Hz (s-1) = the number of points in 1 s.

    """
    time_delta = pd.to_timedelta(x, unit="s")
    diff = time_delta.diff().value_counts().index.tolist()[0]

    return int(pd.Timedelta(seconds=1) / diff)


def zero_interpolation(x, y):
    """
    To find the 'True' zeros of a discretized signal.

    Args:
    ----
        x (array): a discretized vector of floats.
        y (array): a discretized vector y such that y = f(x).

    Returns:
    -------
        x_truncated (array): the input vector x to which have been added
                             all the x0 such that f(x0) = 0.
        y_truncated (array): the input vector y to which have been added
                             all the true zeros.

    Note:
    ----
        the 'y' vector must contains positive and negative values.

    """

    if np.all(np.sign(y) == np.sign(y[0])):
        raise ValueError(
            "Single-sign air flow rate detected. Please use 'detrend_y=True' "
            "or provide a valid air flow rate.")

    crossing_indices = np.where(
        np.array([0 if e in (-1, 1) else e for e in np.diff(np.sign(y))])
    )[0]

    x_zeros, y_zeros = [], []
    for i in crossing_indices:
        x_upstream, x_downstream = x[i], x[i + 1]
        y_upstream, y_downstream = y[i], y[i + 1]

        zero = x_upstream - y_upstream * (x_downstream - x_upstream) / (
            y_downstream - y_upstream
        )
        x_zeros.append(zero)
        y_zeros.append(0.0)

    x_extended = np.concatenate((x, x_zeros))
    y_extended = np.concatenate((y, y_zeros))

    sorted_indices = np.argsort(x_extended)
    x_interpolated = x_extended[sorted_indices]
    y_interpolated = y_extended[sorted_indices]

    # Truncation to start and end with a 'True' zero.
    first_zero = np.where(y_interpolated == 0)[0][0]
    lasy_zero = np.where(y_interpolated == 0)[0][-1] + 1

    x_truncated = x_interpolated[first_zero:lasy_zero]
    y_truncated = y_interpolated[first_zero:lasy_zero]

    return x_truncated, y_truncated


def get_segments(x, y):
    """
    To get positive and negative segments of a signal.

    Args:
    ----
        x (array): a discretised vector of floats.
        y (array): a discretized vector y such that y = f(x).

    Returns:
    -------
        positive_segments (array): pairs (x, y) for which y is positive.
        negative_segments (array): pairs (x, y) for which y in negative.

    """
    positive_segments, negative_segments = [], []
    pos_x, pos_y, neg_x, neg_y = [], [], [], []

    for i, yi in enumerate(y):
        if yi > 0:
            if len(neg_x) > 0:
                negative_segments.append((neg_x, neg_y))
                neg_x, neg_y = [], []

            pos_x.append(x[i])
            pos_y.append(yi)

        elif yi < 0:
            if len(pos_x) > 0:
                positive_segments.append((pos_x, pos_y))
                pos_x, pos_y = [], []

            neg_x.append(x[i])
            neg_y.append(yi)

        else:
            if len(pos_x) > 0:
                positive_segments.append((pos_x, pos_y))
                pos_x, pos_y = [], []

            if len(neg_x) > 0:
                negative_segments.append((neg_x, neg_y))
                neg_x, neg_y = [], []

    if len(pos_x) > 0:
        positive_segments.append((pos_x, pos_y))

    if len(neg_x) > 0:
        negative_segments.append((neg_x, neg_y))

    def add_zeros(x, y, segments):
        """
        To make the positive and negative segments begin and end with 0.

        Args:
        ----
            x (array): a discretised vector of floats.
            y (array): a discretized vector y such that y = f(x).
            segments (list): list of arrays where the values of y
                             have always the same sign.

        Returns:
        -------
            segments (array): pairs (x, y) where y begins and ends with a 0.

        """
        for s in segments:
            first_point = s[0][0]
            last_point = s[0][-1]

            first_index_zero = np.where(x == first_point)[0][0] - 1
            last_index_zero = np.where(x == last_point)[0][0]

            last_index_zero += 1 if (last_index_zero != (len(y) - 1)) else 0

            first_xzero = x[first_index_zero]
            first_yzero = y[first_index_zero]

            last_xzero = x[last_index_zero]
            last_yzero = y[last_index_zero]

            s[0].insert(0, first_xzero)
            s[0].append(last_xzero)
            s[1].insert(0, first_yzero)  # supposed to be 0.
            s[1].append(last_yzero)  # supposed to be 0.

        return segments

    positive_segments = add_zeros(x, y, positive_segments)
    negative_segments = add_zeros(x, y, negative_segments)

    return positive_segments, negative_segments


def get_segment_axis(segments, axis):
    """
    To get only the x or y values of the positive or negative segments.

    Args:
    ----
        segments (list): pairs (x, y) for which y is a single sign (> 0 or < 0).
        axis (str): to get only the x values or the y values (or both).

    Returns:
    -------
        list: list of values (x or y) of positive or negative segments.

    """

    match axis:
        case "x":
            return [x for x, _ in segments]
        case "y":
            return [y for _, y in segments]
        case "both":
            return segments
        case _:
            raise ValueError(
                "axis should be either 'x, 'y' or 'both'. "
                f"Not {axis}."
            )


def get_peaks(x, y, which_peaks, distance):
    """
    To get the top or bottom peaks of a signal.

    Args:
    ----
        x (array): a discretised vector of floats.
        y (array): a discretized vector y such that y = f(x).
        which_peaks (str): To get the top or bottom peaks.
                           Should be "top" or "bottom".
        distance (int): distance between two neighboring peaks.

    Returns:
    -------
        array: values of x such that y[x] is a peak.

    """
    if not (isinstance(distance, int) and distance > 0):
        raise ValueError(
            "To get top or bottom peaks, distance should be a "
            f"positive integer. Not '{distance}'. "
            "Please use 'test_distance method to set the right distance."
        )
    top_peaks, _ = find_peaks(y, distance=distance)
    bottom_peaks, _ = find_peaks(-y, distance=distance)

    if which_peaks == "top":
        return x[top_peaks]
    if which_peaks == "bottom":
        return x[bottom_peaks]
    return None


def frequency(signal, sampling_rate, method, which_peaks, distance, n_digits):
    """Get the frequency of a given signal.

    Args:
    ----
        signal (array): signal to test (list of numbers = discretized signal).
        sampling_rate (int): the sampling rate of the discretized signal.
        method (str): method to commpute frequency.
        which_peaks (str): if the method is 'peaks', which peaks should be
                           considered (top or bottom) ?
        distance (int): the minimum distance between two neighbouring peaks.
        n_digits (int): to round freq to n_digits significant digits.

    Returns:
    -------
        dominant_freq (float): breathing frequency (in respirations per min.)

    """
    match method:
        case "welch":
            fft_length = len(signal) // 3
            window = windows.hamming(fft_length)
            f, Pxx_den = welch(
                x=signal, fs=sampling_rate, window=window, nperseg=fft_length
            )

            dominant_freq = f[np.argmax(Pxx_den)]

        case "peaks":
            if not (isinstance(distance, int) and distance > 0):
                raise ValueError(
                    "To use the peak method, distance should be a "
                    f"positive integer. Not '{distance}'."
                    "Please use 'test_distance' method to set the right distance."
                )

            if which_peaks == "top":
                peaks, _ = find_peaks(x=signal, distance=distance)
            elif which_peaks == "bottom":
                peaks, _ = find_peaks(x=-signal, distance=distance)
            else:
                raise ValueError(
                    "Argument 'which_peaks' must be either 'top' or 'bottom'. "
                    f"Not '{which_peaks}'."
                )

            dominant_freq = sampling_rate / np.mean(np.diff(peaks))

        case "periodogram":
            window = windows.hamming(len(signal))
            f, Pxx_den = periodogram(x=signal, fs=sampling_rate, window=window)
            dominant_freq = f[np.argmax(Pxx_den)]

        case "fft":
            data_len = len(signal)
            sp = np.fft.fft(signal)
            freq = np.fft.fftfreq(data_len, d=1 / sampling_rate)
            dominant_freq = abs(freq[np.argmax(np.abs(sp[: data_len // 2]))])
        case _:
            raise ValueError(
                "'method' should be either 'welch', 'peaks', 'periodogram' or "
                f"'fft'. Not '{method}'."
            )

    # The frequency is in rpm.s-1; we want it in min.-1.
    dominant_freq *= 60

    return scientific_round(dominant_freq, n_digits=n_digits)


def get_auc_time(
    segments, return_mean, verbose, n_digits, lower_threshold, upper_threshold
):
    """
    To get the mean duration of segments when AUC is positive or negative.

    Args:
    ----
        segments (tuple): segments ([x0, x1, ...], [y0, y1, ...], ...) where
                          [y0, y1, ...] contains only values of the same sign.
        return_mean (bool): to return all values or only the mean.
        verbose (bool): to print (or not) results in human readable format.
        n_digits (int): to round time to n_digits significant digits.
        lower_threshold (float): to ignore values below the threshold.
        upper_threshold (float): to ignore values above the threshold.

    Returns:
    -------
        int: the mean duration of AUC
             (or array: all durations if return_mean = False).

    Note:
    ----
        To get segments, please use the 'get_segments' function.

    """
    points_of_interest = [s[0] for s in segments]
    all_durations = np.array([(p[-1] - p[0]) for p in points_of_interest])

    duration = ma.masked_outside(
        all_durations, lower_threshold, upper_threshold
    ).compressed()

    if return_mean:
        mean_duration = scientific_round(np.mean(duration), n_digits=n_digits)
        std_duration = scientific_round(np.std(duration), n_digits=n_digits)
        n_duration = len(duration)
        variability = scientific_round(std_duration/mean_duration*100, n_digits=n_digits)

        if verbose:
            print(f"mean = {mean_duration} ± {std_duration} "
                  f"(n = {n_duration}; var = {variability} %).")
        return mean_duration, std_duration, n_duration, variability

    return scientific_round(duration, n_digits=n_digits)


def get_auc_value(
    segments, return_mean, verbose, n_digits, lower_threshold, upper_threshold
):
    """
    To get the mean AUC of segments when AUC is positive or negative.

    Args:
    ----
        segments (tuple): segments ([x0, x1, ...], [y0, y1, ...], ...) where
                          [y0, y1, ...] contains only values of the same sign.
        return_mean (bool): to return all values or only the mean.
        verbose (bool) : to print (or not) results in human readable format.
        n_digits (int): to round auc value to n_digits significant digits.
        lower_threshold (float): to ignore values below the threshold.
        upper_threshold (float): to ignore values above the threshold.

    Returns:
    -------
        int: the mean of AUC (or array: all AUC if return_mean = False).

    Note:
    ----
        To get segments, please use the 'get_segments' function.

    """
    aucs = np.array([trapezoid(y=y, x=x) for x, y in segments])
    auc = ma.masked_outside(aucs, lower_threshold, upper_threshold).compressed()

    if return_mean:
        mean_auc = scientific_round(np.mean(auc), n_digits=n_digits)
        std_auc = scientific_round(np.std(auc), n_digits=n_digits)
        n_auc = len(auc)
        variability = scientific_round(std_auc/abs(mean_auc)*100, n_digits=n_digits)

        if verbose:
            print(f"mean = {mean_auc} ± {std_auc} (n = {n_auc}; var = {variability} %).")
        return mean_auc, std_auc, n_auc, variability

    return scientific_round(auc, n_digits=n_digits)
