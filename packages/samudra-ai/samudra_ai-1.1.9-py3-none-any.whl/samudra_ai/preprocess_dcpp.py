import xarray as xr

def preprocess_dcpp(file_path: str, var_name: str):

    ds = xr.open_dataset(file_path)

    if var_name not in ds:
        raise ValueError(f"Variabel {var_name} tidak ada dalam file {file_path}")

    da = ds[var_name]

    # Hapus dimensi yang tidak relevan
    for dim in ["initial_time", "ensemble", "member", "zlev"]:
        if dim in da.dims:
            da = da.isel({dim: 0})  # ambil indeks pertama
            da = da.squeeze(dim)    # buang dimensi 1

    # Jika masih ada dimensi extra
    while len(da.dims) > 3:
        for d in da.dims:
            if d not in ["time", "lat", "lon"]:
                da = da.isel({d: 0}).squeeze(d)

    # Pastikan urutan dimensi standar
    if set(["time", "lat", "lon"]).issubset(set(da.dims)):
        da = da.transpose("time", "lat", "lon")

    return da
