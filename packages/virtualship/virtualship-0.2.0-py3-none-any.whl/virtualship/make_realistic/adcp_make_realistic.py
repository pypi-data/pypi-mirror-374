"""adcp_make_realistic function."""

from pathlib import Path

import numpy as np
import xarray as xr


def adcp_make_realistic(
    zarr_path: str | Path,
    out_dir: str | Path,
    prefix: str,
) -> Path:
    """
    Take simulated ADCP data, add noise, then save in (an inconvenient educational) CSV format.

    :param zarr_path: Input simulated data.
    :param out_dir: Output directory for CSV file.
    :param prefix: Prefix for CSV file.
    :returns: Path to created file.
    """
    original = xr.open_zarr(zarr_path)

    times = original.sel(trajectory=0)["time"].values
    depths = original.sel(obs=0)["z"].values
    lats = original.sel(trajectory=0)["lat"].values
    lons = original.sel(trajectory=0)["lon"].values
    all_us = original["U"].values
    all_vs = original["V"].values

    all_us, all_vs = _add_noise(times, depths, all_us, all_vs)

    csv = _to_csv(times, depths, lats, lons, all_us, all_vs)
    out_file = Path(out_dir) / f"{prefix}.csv"

    with open(out_file, "w") as out_cnv:
        out_cnv.write(csv)

    return out_file


def _add_noise(
    times: np.ndarray, depths: np.ndarray, all_us: np.ndarray, all_vs: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    return all_us, all_vs


def _to_csv(
    times: np.ndarray,
    depths: np.ndarray,
    lats: np.ndarray,
    lons: np.ndarray,
    all_us: np.ndarray,
    all_vs: np.ndarray,
) -> str:
    meta = "# depths (m): " + ",".join([str(d) for d in depths])
    header = f"time,lat,lon,{','.join(['u' + str(n) + ',v' + str(n) for n in range(len(depths))])}"
    data = [
        f"{time!s},{lat},{lon},{','.join([str(u) + ',' + str(v) for u, v in zip(us, vs, strict=False)])}"
        for time, lat, lon, us, vs in zip(
            times, lats, lons, all_us.T, all_vs.T, strict=False
        )
    ]

    lines = [meta, header] + data
    return "\n".join(lines)
