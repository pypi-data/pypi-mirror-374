"""
Definition of all telescopes constraints. This is where to update the each telescope constraints.

"""
import numpy as np

# %% VLT constraints


def vlt_zenith_constraint(TimeArray, AltitudeArray):
    np.where(
        AltitudeArray.target.alt.value > 87
    )
    ...
