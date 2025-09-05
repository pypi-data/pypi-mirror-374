#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script handling 'BreathingFlow' object: a discretized air flow rate.

Created on Wed Apr  2 08:40:50 2025
@author: CoustilletT
"""

from importlib.resources import files, as_file
import os
import re

import numpy as np
import pandas as pd
from scipy.signal import detrend

from .utils import enforce_type_arg, scientific_round, print_source
from . import featureextraction as features
from . import visualization


class BreathingFlow:
    """Breathing Air Flow rate."""

    @enforce_type_arg(identifier=str, detrend_y=bool)
    def __init__(self, identifier, raw_time, raw_flow, detrend_y):
        """
        Class constructor.

        Args:
        ----
            identifier (str): breathing signal identifier.
            raw_time (array): discretized time vector.
            raw_flow (array): discretized breathing signal (air flow rate).
            detrend_y (bool): to set the mean of the air flow rate at 0.

        Returns:
        -------
            None.

        """
        self.identifier = identifier
        self.raw_time = raw_time
        self.raw_flow = raw_flow

        time_len = len(self.raw_time)
        self.absolute_time = np.linspace(
            0, time_len / self.get_hz(), time_len, endpoint=False
        )

        if detrend_y:
            self.detrended_flow = detrend(self.raw_flow, type="constant")
            self.detrended_flow[np.isclose(self.detrended_flow, 0, atol=1e-12)] = 0

        y_to_be_interpolated = getattr(self, "detrended_flow", self.raw_flow)

        self.time, self.flow = features.zero_interpolation(
            x=self.raw_time, y=y_to_be_interpolated
        )

        self._distance = None

        # Features
        self._frequency = None
        self._positive_time = None
        self._negative_time = None
        self._positive_auc = None
        self._negative_auc = None
        self._positive_minute_ventilation = None
        self._negative_minute_ventilation = None

    @classmethod
    @enforce_type_arg(identifier=str, filename=str, detrend_y=bool)
    def from_file(cls, identifier, filename, detrend_y=False):
        """
        To instantiate a 'BreathingFlow' objet from a file path.

        Args:
        ----
            identifier (str): breathing signal identifier.
            filename (str): path to the two-column file representing
                            discretized time and discretized air flow rate.
            detrend_y (bool, optional): to set the mean of the air flow rate at 0.
                                        Defaults to False.

        Returns:
        -------
            BreathingFlow: instantiate an objet of type 'BreathingFlow'.

        """
        col_names = ["time", "values"]
        time_pattern_1 = r"^\d{2}:\d{2}:\d{2}([.:])\d+$"
        time_pattern_2 = r"^[+-]?\d+([.,]\d+)?([eE+][+-]?\d+)?$"
        time_pattern = f"(?:{time_pattern_1})|(?:{time_pattern_2})"

        match filename:
            case _ if filename.endswith("txt"):
                raw_data = pd.read_csv(
                    filename, sep=r"\s+", usecols=[0, 1], names=col_names, dtype=str
                )
            case _ if filename.endswith(("xlsx", "xls")):
                raw_data = pd.read_excel(
                    filename, names=col_names, dtype=str, header=None
                )

        data = raw_data[raw_data["time"].str.match(time_pattern, na=False)].reset_index(
            drop=True
        )
        if not data["time"].str.contains(":").any():
            data["time"] = data["time"].str.replace(",", ".")
        if data["values"].str.contains(",").any():
            data["values"] = data["values"].str.replace(",", ".")

        data["values"] = data["values"].astype(float)

        is_wrong_format = data["time"].str.match(r"^\d{2}:\d{2}:\d{2}:\d+$").all()
        if is_wrong_format:
            data["time"] = data["time"].str.replace(r":(?=\d+$)", ".", regex=True)

        # To instantiate an object even if the time vector is not in absolute seconds.
        # Required format : HH:MM:SS.XXX
        if not all(
            re.match(time_pattern_2, time) for time in data["time"].values.astype(str)
        ):
            data["time"] = pd.to_timedelta(data["time"]).dt.total_seconds()

        data["time"] = data["time"].astype(float)

        return cls(
            identifier=identifier,
            raw_time=data["time"].values,
            raw_flow=data["values"].values,
            detrend_y=detrend_y,
        )

    @classmethod
    @enforce_type_arg(identifier=str, detrend_y=bool)
    def from_dataframe(cls, identifier, df, detrend_y=False):
        """
        To instantiate a 'BreathingFlow' objet from a dataframe.

        Args:
        ----
            identifier (str): breathing signal identifier.
            df (pandas.DataFrame): two-column dataframe representing discretized
                                   time and discretized air flow rate.
            detrend_y (bool, optional): to set the mean of the air flow rate at 0.
                                        Defaults to False.

        Returns:
        -------
            BreathingFlow: instantiate an objet of type 'BreathingFlow'.

        """
        if not {"time", "values"}.issubset(df.columns):
            raise ValueError(
                "DataFrame must contain a 'time' column and a 'values' column."
            )
        return cls(
            identifier=identifier,
            raw_time=df["time"].values,
            raw_flow=df["values"].values,
            detrend_y=detrend_y,
        )

    @classmethod
    def load_sinus(cls):
        """
        Load and return a BreathingFlow object from the "sinus" dataset.

        Returns:
        -------
            BreathingFlow: a BreathingFlow object = the sinus function.

        Note:
        ----
            is used to demonstrate the 'proof of concept'.
        """
        sinus_resource = files("pybreathe.datasets").joinpath("sinus.txt")

        with as_file(sinus_resource) as sinus_path:
            with open(sinus_path, encoding="utf-8") as f:
                sinus = pd.read_csv(
                    f, sep="\t", names=["time", "values"], dtype=float
                )

        return cls(
            identifier="example_sinus",
            raw_time=sinus["time"].values,
            raw_flow=sinus["values"].values,
            detrend_y=False,
        )

    @classmethod
    def load_breathing_like_signal_01(cls):
        """
        Load and return a BreathingFlow object from the "breathing-like signal 01" dataset.

        Returns:
        -------
            BreathingFlow: a BreathingFlow object.
        """
        breathing_resource_01 = (
            files("pybreathe.datasets")
            .joinpath("breathing_like_signal_01.txt")
        )

        with as_file(breathing_resource_01) as breathing_01_path:
            with open(breathing_01_path, encoding="utf-8") as f:
                breathing_01 = pd.read_csv(
                    f, sep="\t", names=["time", "values"], dtype=float
                )

        print(print_source()["breathing-like 01"])

        return cls(
            identifier="example_breathing-like_signal_01",
            raw_time=breathing_01["time"].values,
            raw_flow=breathing_01["values"].values,
            detrend_y=False,
        )

    @classmethod
    def load_breathing_like_signal_02(cls):
        """
        Load and return a BreathingFlow object from the "breathing-like signal 02" dataset.

        Returns:
        -------
            BreathingFlow: a BreathingFlow object.
        """
        breathing_resource_02 = (
            files("pybreathe.datasets")
            .joinpath("breathing_like_signal_02.txt")
        )

        with as_file(breathing_resource_02) as breathing_02_path:
            with open(breathing_02_path, encoding="utf-8") as f:
                breathing_02 = pd.read_csv(
                    f, sep="\t", names=["time", "values"], dtype=float
                )

        print(print_source()["breathing-like 02"])

        return cls(
            identifier="example_breathing-like_signal_02",
            raw_time=breathing_02["time"].values,
            raw_flow=breathing_02["values"].values,
            detrend_y=False,
        )

    def __getitem__(self, key):
        """
        To allow a 'BreathingFlow' object to be sliced and used as a new object.

        Args:
        ----
            key (list): slice of shape [start:stop:steps].

        Returns:
        -------
            A new 'BreathingFlow' sliced object.

        """
        sliced_object = self.__class__(
            identifier=self.identifier,
            raw_time=self.time[key],
            raw_flow=self.flow[key],
            detrend_y=False,
        )

        if hasattr(self, "distance"):
            sliced_object._distance = self._distance

        return sliced_object

    def __len__(self):
        """To get the length of the signal (in number of points)."""
        return len(self.flow)

    @property
    def distance(self):
        """Getter."""
        return self._distance

    @property
    def frequency(self):
        """Getter."""
        return self._frequency

    @property
    def positive_time(self):
        """Getter."""
        return self._positive_time

    @property
    def negative_time(self):
        """Getter."""
        return self._negative_time

    @property
    def positive_auc(self):
        """Getter."""
        return self._positive_auc

    @property
    def negative_auc(self):
        """Getter."""
        return self._negative_auc

    @property
    def positive_minute_ventilation(self):
        """Getter."""
        return self._positive_minute_ventilation

    @property
    def negative_minute_ventilation(self):
        """Getter."""
        return self._negative_minute_ventilation

    def get_hz(self):
        """To get the sampling rate of the discretized breathing signal."""
        return features.compute_sampling_rate(x=self.raw_time)

    @enforce_type_arg(
        y=str,
        show_segments=bool,
        show_auc=bool,
        highlight_time=tuple,
        highlight_auc=tuple,
        output_path=str,
    )
    def plot(
        self,
        y="flow",
        show_segments=False,
        show_auc=False,
        highlight_time=(),
        highlight_auc=(),
        output_path="",
    ):
        """
        To plot the air flow rate.

        Args:
        ----
            y (str, optional): the values for the y-axis.
            show_segments (bool, optional): to distinguish between the positive and negative
                                            parts of the curve. Defaults to False.
            show_auc (bool, optional): to distinguish between the positive and negative
                                       areas of the curve. Defaults to False.
            highlight_time (tuple, optional): to highlight breathing cycles with a specific time.
            highlight_auc (tuple, optional): to highlight breathing cycles with a specific area.
            output_path (str, optional): to choose where to save the figure, if applicable.
                                         Defaults to "" (figure not saved).

        Returns:
        -------
            None. Plot the figure.

        """
        match y:
            case "flow":
                x, y = self.time, self.flow
            case "raw_flow":
                x, y = self.absolute_time, self.raw_flow
            case "detrended_flow":
                x, y = self.absolute_time, self.detrended_flow
            case _:
                raise AttributeError(
                    f"{self.__class__.__name__} object has no attribute '{y}'"
                )

        visualization.plot_signal(
            x=x,
            y=y,
            show_segments=show_segments,
            show_auc=show_auc,
            highlight_time=highlight_time,
            highlight_auc=highlight_auc,
            output_path=output_path,
        )

    @enforce_type_arg(axis=str)
    def get_positive_segments(self, axis="both"):
        """To get the pairs (x,y) for which the air flow rate is positive."""
        return features.get_segment_axis(
            segments=features.get_segments(self.time, self.flow)[0],
            axis=axis
        )

    @enforce_type_arg(axis=str)
    def get_negative_segments(self, axis="both"):
        """To get the pairs (x,y) for which the air flow rate is negative."""
        return features.get_segment_axis(
            segments=features.get_segments(self.time, self.flow)[1],
            axis=axis
        )

    @enforce_type_arg(which_peaks=str, distance=int, set_dist=bool, output_path=str)
    def test_distance(
        self, which_peaks="top", distance=0, set_dist=False, output_path=""
    ):
        """
        Calibration of peaks detection
        = test which distance should be assigned to the 'distance' attribute.

        Args:
        ----
            which_peaks (str, optional): to consider either top or bottom peaks. Defaults to 'top'.
            distance (int): the minimum distance between two neighbouring peaks.
            set_dist (bool, optionnal): to set the distance or not. Defaults to False.
            output_path (str, optional): to choose where to save the figure, if applicable.
                                         Defaults to "" (figure not saved).

        Returns:
        -------
            None. Plots a control figure.

        Note:
        ----
            You will probably have to test several distance values
            to find the one that detects all the peaks.

        """
        visualization.plot_peaks(
            x=self.time,
            y=self.flow,
            which_peaks=which_peaks,
            distance=distance,
            output_path=output_path,
        )

        if set_dist:
            self._distance = distance

    def get_top_peaks(self):
        """To get the top peaks of the air flow rate."""
        return features.get_peaks(
            x=self.time, y=self.flow, which_peaks="top", distance=self.distance
        )

    def get_bottom_peaks(self):
        """To get the bottom peaks of the air flow rate."""
        return features.get_peaks(
            x=self.time, y=self.flow, which_peaks="bottom", distance=self.distance
        )

    @enforce_type_arg(method=str, n_digits=int, save=bool)
    def get_frequency(self, method="welch", which_peaks=None, n_digits=3, save=False):
        """
        Get breathing frequency of the air flow rate (in respirations.min-1).

        Args:
        ----
            method (str, optional): method used to calculate the frequency.
                                    Defaults to "welch".
                                    Possible choices: 'welch', 'peaks', 'periodogram' or 'fft'.
            which_peaks (str, optional): if the method is 'peaks', which peaks should be considered?.
                                         Defaults to None.
            n_digits (int, optional): to round freq to n_digits significant
                                      digits. Defaults to 3.
            save (bool, optional): save (bool, optional): to memorise or not the value obtained.
                                   Defaults to False.

        Returns:
        -------
            freq (float): breathing frequency in rpm.min-1.

        """
        freq = features.frequency(
            signal=self.flow,
            sampling_rate=self.get_hz(),
            method=method,
            which_peaks=which_peaks,
            distance=self.distance,
            n_digits=n_digits,
        )

        if save:
            self._frequency = freq

        return freq

    @enforce_type_arg(
        return_mean=bool,
        verbose=bool,
        n_digits=int,
        lower_threshold=float,
        upper_threshold=float,
        save=bool,
    )
    def get_positive_time(
        self,
        return_mean=True,
        verbose=True,
        n_digits=3,
        lower_threshold=-np.inf,
        upper_threshold=np.inf,
        save=False,
    ):
        """To get the mean duration of positive segments (when AUC > 0).

        Args:
        ----
            return_mean (bool, optional): to return all values or only the mean.
                                          Defaults to True (= the mean).
            verbose (bool, optional): to print (or not) results in human
                                      readable format. Defaults to True.
            n_digits (int, optional): to round time to n_digits significant
                                      digits. Defaults to 3.
            lower_threshold (float, optional): to ignore values below the threshold.
                                         Defaults to - ∞.
            upper_threshold (float, optional): to ignore values above the threshold.
                                         Defaults to + ∞.
            save (bool, optional): to memorise or not the value obtained.
                                   Defaults to False.

        Returns:
        -------
            positive_time: mean duration of positive segments (when AUC > 0)
                           (or all durations if return_mean = False).

        Note:
        ----
            AUC = Area Under the Curve.

        """
        pos_auc_time = features.get_auc_time(
            segments=self.get_positive_segments(),
            return_mean=return_mean,
            verbose=verbose,
            n_digits=n_digits,
            lower_threshold=lower_threshold,
            upper_threshold=upper_threshold,
        )

        if save:
            self._positive_time = pos_auc_time

        return pos_auc_time

    @enforce_type_arg(
        return_mean=bool,
        verbose=bool,
        n_digits=int,
        lower_threshold=float,
        upper_threshold=float,
        save=bool,
    )
    def get_negative_time(
        self,
        return_mean=True,
        verbose=True,
        n_digits=3,
        lower_threshold=-np.inf,
        upper_threshold=np.inf,
        save=False,
    ):
        """
        To get the mean duration of negative segments (when AUC < 0).

        Args:
        ----
            return_mean (bool, optional): to return all values or only the mean.
                                          Defaults to True (= the mean).
            verbose (bool, optional): to print (or not) results in human
                                      readable format. Defaults to True.
            n_digits (int, optional): to round time to n_digits significant
                                      digits. Defaults to 3.
            lower_threshold (float, optional): to ignore values below the threshold.
                                         Defaults to - ∞.
            upper_threshold (float, optional): to ignore values above the threshold.
                                         Defaults to + ∞.
            save (bool, optional): to memorise or not the value obtained.
                                   Defaults to False.

        Returns:
        -------
            negative_time: mean duration of negative segments (when AUC < 0).
                           (or all durations if return_mean = False).

        Note:
        ----
            AUC = Area Under the Curve.

        """
        neg_auc_time = features.get_auc_time(
            segments=self.get_negative_segments(),
            return_mean=return_mean,
            verbose=verbose,
            n_digits=n_digits,
            lower_threshold=lower_threshold,
            upper_threshold=upper_threshold,
        )

        if save:
            self._negative_time = neg_auc_time

        return neg_auc_time

    @enforce_type_arg(
        return_mean=bool,
        verbose=bool,
        n_digits=int,
        lower_threshold=float,
        upper_threshold=float,
        save=bool,
    )
    def get_positive_auc(
        self,
        return_mean=True,
        verbose=True,
        n_digits=3,
        lower_threshold=-np.inf,
        upper_threshold=np.inf,
        save=False,
    ):
        """
        To get the mean AUC of positive segments (when AUC > 0).

        Args:
        ----
            return_mean (bool, optional): to return all values or only the mean.
                                          Defaults to True (= the mean).
            verbose (bool, optional): to print (or not) results in human
                                      readable format. Defaults to True.
            n_digits (int, optional): to round auc value to n_digits significant
                                      digits. Defaults to 3.
            lower_threshold (float, optional): to ignore values below the threshold.
                                         Defaults to - ∞.
            upper_threshold (float, optional): to ignore values above the threshold.
                                         Defaults to + ∞.
            save (bool, optional): to memorise or not the value obtained.
                                   Defaults to False.

        Returns:
        -------
            positive_auc: mean AUC of positive segments (when AUC > 0).
                          (or each AUC of each segment if return_mean = False).

        Note:
        ----
            AUC = Area Under the Curve.

        """
        pos_auc_val = features.get_auc_value(
            segments=self.get_positive_segments(),
            return_mean=return_mean,
            verbose=verbose,
            n_digits=n_digits,
            lower_threshold=lower_threshold,
            upper_threshold=upper_threshold,
        )

        if save:
            self._positive_auc = pos_auc_val

        return pos_auc_val

    @enforce_type_arg(
        return_mean=bool,
        verbose=bool,
        n_digits=int,
        lower_threshold=float,
        upper_threshold=float,
        save=bool,
    )
    def get_negative_auc(
        self,
        return_mean=True,
        verbose=True,
        n_digits=3,
        lower_threshold=-np.inf,
        upper_threshold=np.inf,
        save=False,
    ):
        """
        To get the mean AUC of negative segments (when AUC < 0).

        Args:
        ----
            return_mean (bool, optional): to return all values or only the mean.
                                          Defaults to True (= the mean).
            verbose (bool, optional): to print (or not) results in human
                                      readable format. Defaults to True.
            n_digits (int, optional): to round auc value to n_digits significant
                                      digits. Defaults to 3.
            lower_threshold (float, optional): to ignore values below the threshold.
                                         Defaults to - ∞.
            upper_threshold (float, optional): to ignore values above the threshold.
                                         Defaults to + ∞.
            save (bool, optional): to memorise or not the value obtained.
                                   Defaults to False.

        Returns:
        -------
            negative_auc: mean AUC of negative segments (when AUC < 0).
                          (or each AUC of each segment if return_mean = False).

        Note:
        ----
            AUC = Area Under the Curve.
            'threshold' must be negative as AUC is also negative, e.g.,
            if AUC values = [- 0.2, - 0.18, - 0.23, - 0.01], then to remove the
            - 0.01 value, threshold should be - 0.05 for example.

        """
        neg_auc_val = features.get_auc_value(
            segments=self.get_negative_segments(),
            return_mean=return_mean,
            verbose=verbose,
            n_digits=n_digits,
            lower_threshold=lower_threshold,
            upper_threshold=upper_threshold,
        )

        if save:
            self._negative_auc = neg_auc_val

        return neg_auc_val

    @enforce_type_arg(verbose=bool, n_digits=int, save=bool)
    def get_minute_ventilation(self, verbose=True, n_digits=3, save=False):
        """
        To get minute ventilation of positive and negative segments.

        Args:
        ----
            verbose (bool, optional): to print (or not) results in human
                                      readable format. Defaults to True.
            n_digits (int, optional): to round minute ventilation to n_digits
                                      significant digits. Defaults to 3.
            save (bool, optional): to memorise or not the value obtained.
                                   Defaults to False.

        Raises:
        ------
            ValueError: The frequency and tidal volume must have been
                        set by calling up the corresponding methods.

        Returns:
        -------
            pos_mv (float): minute ventilation of positive segments
                            (in unit of tidal volume .min-1).
            neg_mv (float): minute ventilation of negative segments
                            (in unit of tidal volume .min-1).

        Note:
        ----
            Minute Ventilation is the product of frequency and tidal volume.

        """
        if self.frequency and self.positive_auc:
            pos_mv = scientific_round(
                (self.frequency * self.positive_auc[0]), n_digits=n_digits
            )
            if verbose:
                print(f"Minute ventilation of positive segments: {pos_mv}.")
        else:
            raise ValueError(
                "Please save the frequency and tidal volume by setting the "
                "'save' argument to 'True' in the method call. "
                "(get_frequency() and get_positive_auc())"
            )

        if self.frequency and self.negative_auc:
            neg_mv = scientific_round(
                (self.frequency * self.negative_auc[0]), n_digits=n_digits
            )
            if verbose:
                print(f"Minute ventilation of negative segments: {neg_mv}.")
        else:
            raise ValueError(
                "Please save the frequency and tidal volume by setting the "
                "'save' argument to 'True' in the method call. "
                "(get_frequency() and get_negative_auc())"
            )

        if save:
            self._positive_minute_ventilation = pos_mv
            self._negative_minute_ventilation = neg_mv

        return pos_mv, neg_mv

    @enforce_type_arg(stat=str, output_path=str)
    def plot_distribution(self, stat="probability", output_path=""):
        """
        To get distribution of each feature of the 'BreathingFlow' object.

        Args:
        ----
            stat (int, optional): aggregate statistic to compute in each bin.
                                  Defaults to "probability".
            output_path (str, optional): to choose where to save the figure,
                                         if applicable. Defaults to "" (figure not saved)

        Returns:
        -------
            None. Plots the distribution.

        Note:
        ----
            stat should be 'count', 'frequency', 'probability', 'percent' or
            'density'.

        """
        if stat not in ("count", "frequency", "probability", "percent", "density"):
            raise ValueError(
                "stat should be either 'count', 'frequency', 'probability', "
                f"'percent' or 'density'. Not {stat}."
            )

        visualization.plot_features_distribution(
            self.get_positive_time(return_mean=False),
            self.get_negative_time(return_mean=False),
            self.get_positive_auc(return_mean=False),
            self.get_negative_auc(return_mean=False),
            stat=stat,
            output_path=output_path,
        )

    @enforce_type_arg(time_delay=float, color_scheme=str)
    def plot_phase_portrait(self, time_delay=-1.0, color_scheme="time"):
        """
        To plot the phase portrait of the air flow rate.

        Args:
        ----
            time_delay (float, optional):
                parameter for phase portrait offset: y(x) vs. y(x+t). Defaults to -1.0.
                The default value -1 is then converted into a tailor-made value.
            color_scheme (str, optional):
                whether the color is defined from time or respiratory phases. Defaults to "time".

        Returns:
        -------
            None. Plots the phase portrait.

        """
        if time_delay == -1.0:
            time_delay = (
                self.get_positive_time(verbose=False)[0] +
                self.get_negative_time(verbose=False)[0]) * 1/15

        visualization.plot_phase_portrait(
            x=self.time,
            y=self.flow,
            time_delay=time_delay,
            hz=self.get_hz(),
            color_scheme=color_scheme
        )

    @enforce_type_arg(output_directory=str)
    def get_overview(self, output_directory=""):
        """
        To summarize the features of the 'BreathingFlow' object in a DataFrame.

        Args:
        ----
            output_directory (str, optional): where to save the backup file.
                                              It should not be the full path
                                              but just a path to a directory.
                                              Defaults to "" (no backup).

        Returns:
        -------
            pandas.DataFrame: dataframe summarising the features.

        """
        metrics = ["mean", "std", "n cycle(s)"]
        dict_data = {}
        dict_data["Bf (rpm)"] = {"mean": self._frequency, "std": "-", "n cycle(s)": "-"}
        dict_data["time (AUC > 0) (s)"] = dict(zip(metrics, self.positive_time))
        dict_data["time (AUC < 0) (s)"] = dict(zip(metrics, self.negative_time))
        dict_data["AUC value (AUC > 0)"] = dict(zip(metrics, self.positive_auc))
        dict_data["AUC value (AUC < 0)"] = dict(zip(metrics, self.negative_auc))
        dict_data["Min. ventilation (AUC > 0)"] = {
            "mean": self._positive_minute_ventilation
        }
        dict_data["Min. ventilation (AUC < 0)"] = {
            "mean": self._negative_minute_ventilation
        }

        def to_dataframe(overview_dict):
            """
            To convert the dictionary into a specially formatted Dataframe.

            Args:
            ----
                overview_dict (dict): dictionary hosting all the signal features.

            Returns:
            -------
                multicols_df (pandas.DataFrame): dataframe summarising the
                                                 features (freq, auc, times).

            """
            data_tuples = [
                ((key, sub_key), value)
                for key, sub_dict in overview_dict.items()
                for sub_key, value in sub_dict.items()
            ]
            multicols_df = pd.DataFrame.from_dict(dict(data_tuples), orient="index").T
            multicols_df.columns = pd.MultiIndex.from_tuples(multicols_df.columns)
            multicols_df.index.name = "identifier"
            multicols_df.index = [self.identifier]

            return multicols_df

        formatted_dataframe = to_dataframe(overview_dict=dict_data)

        if output_directory:
            output_path = os.path.join(output_directory, f"overview_{self.identifier}")
            formatted_dataframe.to_excel(excel_writer=f"{output_path}.xlsx")

        return formatted_dataframe
