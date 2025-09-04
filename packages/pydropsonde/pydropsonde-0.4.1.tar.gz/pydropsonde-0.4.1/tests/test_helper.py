import pydropsonde.helper as hh
import numpy as np
import xarray as xr

p = np.linspace(100000, 10000, 10)
T = np.linspace(300, 200, 10)
q = np.linspace(0.02, 0.002, 10)
alt = np.linspace(0, 17000, 10)
rh = np.repeat(0.8, 10)

ds = xr.Dataset(
    data_vars=dict(
        ta=(["alt"], T, {"units": "kelvin"}),
        p=(["alt"], p, {"units": "Pa"}),
        rh=(["alt"], rh),
        q=(["alt"], q),
    ),
    coords=dict(
        alt=("alt", alt),
    ),
    attrs={
        "example_attribute_(lines_of_code)": "23",
        "launch_time_(UTC)": "20240903T04:00.000",
    },
)


def test_q2rh2q():
    rh2q = hh.calc_q_from_rh(ds)
    q2rh = hh.calc_rh_from_q(rh2q)
    assert np.all(np.round(ds.rh.values, 3) == np.round(q2rh.rh.values, 3))


def test_t2theta2t():
    t2theta = hh.calc_theta_from_T(ds)
    theta2t = hh.calc_T_from_theta(t2theta)
    assert np.all(np.round(ds.ta.values, 2) == np.round(theta2t.ta.values, 2))


def test_rh2q_range():
    rh2q = hh.calc_q_from_rh(ds)
    assert rh2q.q.isel(alt=0).values > 0.01
    assert rh2q.q.isel(alt=0).values < 0.02
    assert rh2q.q.isel(alt=-1).values < 1e-4
