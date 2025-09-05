---
title: 'pybreathe: a python package for respiratory airflow rates analysis'
tags:
    - Python
    - bioinformatics
    - plethysmography
    - breathing
    - respiration
    - airflow rate
    - time series
authors:
    - name: Thibaut Coustillet
      orcid: 0000-0002-7945-0519
      affiliation: "1, 2"
affiliations:
    - index: 1
      name: Sorbonne Université, CNRS, Inserm, Development, Adaptation and Ageing, Dev2A, F-75005 Paris, France
      ror: 02en5vm52
    - index: 2
      name: Sorbonne Université, CNRS, Inserm, Institut de Biologie Paris-Seine, IBPS, F-75005 Paris, France
      ror: 02en5vm52
date: 29 July 2025
bibliography: paper.bib
---

# Summary

Breathing is the vital function that enables air to flow into the lungs during inhalation and out during exhalation. Inhalation delivers (di)oxygen to the tissues, while exhalation flushes out carbon dioxide. In physiology, breathing is widely studied to investigate a whole range of respiratory diseases as well as physical abilities. A consistent and robust analytical framework is essential to cope with the large volume of data and to address the often time-consuming nature of routine analysis procedures. `pybreathe` is a python package that allows breathing to be formally analysed. It lets users to extract features such as the volume inhaled and exhaled, the inspiratory and expiratory times, and the breathing frequency. The package has been designed to be user-friendly, relying solely on a user-supplied discretised air flow rate considered as a time series (instantaneous flow rate).

# Statement of need

In 2017, half a billion people worldwide lived with a chronic respiratory disease [@soriano2020]. Concurrently, the role of breathing has garnered growing attention in research focused on both athletic/sport performance [@contreras-briceno2024; @harbour2022] and overall well-being [@fincham2023]. Recently, new algorithms have been developed to structure analysis and open up new insights. Such tools complement commercial analysis software used historically [@lusk2023].

On the one hand, most of the open source software relies heavily on peak/hollow detection [@bishop2022; @brammer2020; @makowski2021] to extract features such as amplitude and breathing period. However, such local extrema detection approaches often require human correction or complementary algorithms to guarantee the accuracy of the results [@vanegas2020]. Besides, they are more suited for the characterization of instantaneous volume than of instantaneous flow. Although the former can be deduced from the latter (\autoref{fig:flowVSvol}), it is generally flow rates, themselves derived from pressure differences that are supplied [@criee2011]. In some cases, however, signals and related algorithms may also originate from chest/abdominal belts [@holm2024].

![Relationship between instantaneous flow rate (a) and instantaneous volume (b). The volume is obtained by integrating the flow rate over time. Thus, when the flow rate is positive (inhalation; blue areas), the volume increases, whereas when the flow rate is negative (exhalation; yellow areas), the volume decreases. \label{fig:flowVSvol}](fig_flowVSvol.pdf)

On the other hand, some advanced algorithms use cutting-edge clustering methods to detect respiratory patterns that go beyond the features mentioned above [@germain2023]. While offering deeper physiological insights, they require advanced programming skills and knowledge and may be complicated to set up in practice for non-computer users.

Here, we sought to implement an easy-to-use framework specially designed to facilitate respiratory analyses derived from instantaneous air flow rates (recorded by plethysmography). Users can acquire their respiratory data using any standard software. A necessary and sufficient condition for using `pybreathe` is to export the data and discretise it into a classic text format (*e.g.*, .txt, .csv) as shown in \autoref{tbl:table1}.

| time   | values |
|--------|--------|
| 0.0    | 0.0650 |
| 0.004  | 0.0660 |
| 0.008  | 0.0671 |
| 0.012  | 0.0681 |
| 0.016  | 0.0692 |
| ...    | ...    |

Table: Example of a two-column table depicting the instantaneous discretised air flow rate (time series) required for the use of `pybreathe`. \label{tbl:table1}

In contrast to other respiratory algorithms, `pybreathe` operates on ventilatory flow rather than volume. The fundamental feature of a respiratory signal being the tidal volume (*i.e.*, the volume passing through the lungs during a single breath), peak/hollow analysis cannot be applied in the case of air flow rates because the amplitude (*i.e.*, height) depends on the 'speed' at which the air flows in and out: for the same exhaled or inhaled volume, the faster the airflow, the greater the amplitude (\autoref{fig:calibrations}).

![Manual injection (blue) and aspiration (purple) of different quantities of air into a chamber with a syringe at three different speeds. (a) 2 mL; (b) 3 mL; (c) 4 mL; (d) 5 mL. \label{fig:calibrations}](fig_calibrations.pdf)

In this situation, to really grasp the tidal volume, we need to get the Area Under the Curve (AUC) instead of the amplitude (\autoref{tbl:table2}).

| actual volume  | speed        | positive integral | negative integral | positive amplitude | negative amplitude |
|----------------|--------------|-------------------|-------------------|--------------------|--------------------|
| $\approx$ 2 mL | slow         | 1.90              | - 2.02            | 1.70               | - 2.26             |
| $\approx$ 2 mL | moderate     | 1.90              | - 1.96            | 2.66               | - 2.54             |
| $\approx$ 2 mL | fast         | 1.81              | - 1.86            | 4.79               | - 3.75             |
|                |              |                   |                   |                    |                    |
| $\approx$ 3 mL | slow         | 2.99              | - 3.10            | 3.04               | - 3.19             |
| $\approx$ 3 mL | moderate     | 2.94              | - 2.93            | 3.98               | - 5.07             |
| $\approx$ 3 mL | fast         | 2.53              | - 2.52            | 9.24               | - 5.2              |
|                |              |                   |                   |                    |                    |
| $\approx$ 4 mL | slow         | 3.90              | - 4.05            | 2.91               | - 3.71             |
| $\approx$ 4 mL | moderate     | 3.92              | - 4.02            | 6.46               | - 4.81             |
| $\approx$ 4 mL | fast         | 3.12              | - 3.13            | 12.03              | - 7.09             |
|                |              |                   |                   |                    |                    |
| $\approx$ 5 mL | slow         | 4.99              | - 5.08            | 4.21               | - 5.76             |
| $\approx$ 5 mL | moderate     | 4.93              | - 5.08            | 6.58               | - 6.70             |
| $\approx$ 5 mL | fast         | 4.24              | - 4.16            | 14.88              | - 9.04             |

Table: Comparison of the integral (Area Under the Curve) and amplitude (height) of several volumes of air manually injected/aspirated into a chamber. \label{tbl:table2}

# pybreathe fundamentals

For a given respiratory signal, `pybreathe` detects zero-crossings (\autoref{fig:flowVSvol}a). AUC (integral) of these zero-separated segments therefore corresponds to the volume inhaled or exhaled (depending on the configuration of the primary acquisition software). The duration of these segments (time between two zeros) corresponds to the inspiratory or expiratory time.

The `pybreathe` package is accompagnied by a *BreathingFlow* object which is the core of the algorithm. Users should instantiate a *BreathingFlow* object with their own data (*e.g.*, \autoref{tbl:table1}).

```python
from pybreathe import BreathingFlow

my_signal = BreathingFlow.from_file(
  filename="path_to_your_discretised_flow.txt", 
  identifier="my data"
)
```

The package comes with an [example script](https://github.com/tcoustillet/pybreathe/tree/main/examples) based on simulated breathing signals. It explains the milestones involved in carrying out a complete analysis and it supplies useful documentation. To get started with `pybreathe` API, users are strongly advised to refer to this script.

# Proof

To ensure that the package worked correctly, we checked the volumes extracted by `pybreathe` when we injected/aspirated known quantities of air (\autoref{fig:calibrations} and \autoref{tbl:table2}). The AUC values matched well with the corresponding injected volumes. However, because the manual experiment can be imprecise due to the experimenter and the precision of the syringe (especially at high speed), we also created an artifical respiratory signal corresponding to the sine function (\autoref{fig:sinus}). 

![Graph of the sine function on the interval $[0, 10\pi]$. \label{fig:sinus}](fig_sinus.pdf)

Based on the sine, we checked that the signal features obtained with `pybreathe` were indeed the same as those obtained *mathematically*. Users can access these demonstrations in the [validation notebook](https://github.com/tcoustillet/pybreathe/blob/main/examples/validation.ipynb).

For example, `pybreathe` exactly identified that the duration of each of the segments in which the sine function is positive is exactly $\pi$, and that the AUC of these same segments is exactly $2$.

# Acknowledgements

This work was supported by SATT Lutech under Grant *Algostim*. The author acknowledges the NeAR team and Isabelle Vivodtzev for the opportunity to disseminate this work. Warm thanks are also due to \mbox{Eugénie} \mbox{Faure} and \mbox{Alexandre} \mbox{Palazzi} for their valuable feedback throughout the development of `pybreathe`.

# References
