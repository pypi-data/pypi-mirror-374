import numpy as np
import xarray as xr
from samudra_ai import SamudraAI

# Fungsi pembuat data dummy
def create_dummy_data(time=20, lat=3, lon=4):
    coords = {
        "time": np.arange(time),
        "lat": np.linspace(-10, 10, lat),
        "lon": np.linspace(100, 120, lon),
    }
    data = np.random.rand(time, lat, lon)
    return xr.DataArray(data, coords=coords, dims=("time", "lat", "lon"))

def test_fit_and_predict():
    x = create_dummy_data()
    y = create_dummy_data()

    model = SamudraAI(time_seq=5)
    model.fit(x, y, epochs=1)  # cepat karena epoch 1

    corrected = model.predict(x)
    assert isinstance(corrected, xr.DataArray)
    assert "time" in corrected.dims
