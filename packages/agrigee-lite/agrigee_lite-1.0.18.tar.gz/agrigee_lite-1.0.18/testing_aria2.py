import pathlib
import time
from functools import partial

import aria2p
import ee
import geopandas as gpd
import numpy as np
import pandas as pd
import pandera as pa
from tqdm.std import tqdm

import agrigee_lite as agl
from agrigee_lite.ee_utils import ee_gdf_to_feature_collection
from agrigee_lite.misc import (
    add_indexnum_column,
    create_gdf_hash,
    quadtree_clustering,
)

aria2 = aria2p.API(aria2p.Client(host="http://localhost", port=6800, secret=""))


def build_chunk_download_urls(
    gdf,
    satellite,
    reducers: list[str] | None = None,
    subsampling_max_pixels: float = 1_000,
    chunksize: int = 100,
    max_parallel_downloads: int = 25,
) -> list[str]:
    schema = pa.DataFrameSchema({
        "geometry": pa.Column("geometry", nullable=False),
        "start_date": pa.Column(
            pa.DateTime,
            nullable=False,
        ),
        "end_date": pa.Column(
            pa.DateTime,
            nullable=False,
        ),
    })
    schema.validate(gdf, lazy=True)

    if len(gdf) == 0:
        return []

    gdf = gdf.copy()
    add_indexnum_column(gdf)
    gdf = quadtree_clustering(gdf, max_size=1000)
    hashname = create_gdf_hash(gdf)

    not_sent_to_server = 0

    output_path = pathlib.Path("data/temp") / "aria2" / f"{satellite.shortName}_{hashname}_{chunksize}"
    output_path.mkdir(parents=True, exist_ok=True)

    num_chunks = (len(gdf) + chunksize - 1) // chunksize

    total_rows = len(gdf)
    pbar = tqdm(
        total=total_rows,
        desc=f"Building download URLs ({satellite.shortName}_{hashname}_{chunksize})",
        unit="feature",
        smoothing=0,
    )

    for i in range(num_chunks):
        if not (output_path / f"{i}.csv").exists():
            while (
                int(aria2.get_stats()._struct["numActive"]) + int(aria2.get_stats()._struct["numWaiting"])
            ) >= max_parallel_downloads:
                time.sleep(5)

            sub = gdf.iloc[i * chunksize : (i + 1) * chunksize]

            fc = ee_gdf_to_feature_collection(sub)
            ee_expression = ee.FeatureCollection(
                fc.map(
                    partial(
                        satellite.compute,
                        reducers=reducers,
                        subsampling_max_pixels=subsampling_max_pixels,
                    )
                )
            ).flatten()

            try:
                url = ee_expression.getDownloadURL(
                    filetype="csv",
                    selectors=[
                        "00_indexnum",
                        "01_timestamp",
                        *[numeral_band_name for _, numeral_band_name in satellite.selectedBands],
                        *[numeral_indice_name for _, _, numeral_indice_name in satellite.selectedIndices],
                        "99_validPixelsCount",
                    ],
                    filename=f"{i}",
                )

                aria2.add_uris([url], options={"dir": str(output_path.absolute()) + "/"})
            except Exception as _:
                print(_)
                not_sent_to_server += 1
                pass

            # Atualiza barra para chunks enviados para download
            pbar.update(min(chunksize, total_rows - i * chunksize))

        else:
            print(f"Chunk {i} already exists, skipping download.")
            # Atualiza barra também para chunks JÁ BAIXADOS (arquivo já existe)
            pbar.update(min(chunksize, total_rows - i * chunksize))

    error_count = sum(d.status == "error" for d in aria2.get_downloads())
    pbar.set_postfix({"not_sent_to_server": not_sent_to_server, "aria2_errors": error_count})

    pbar.close()


gdf = gpd.read_parquet("data/varda_brazil/TO.parquet")


gdf = gdf.iloc[0:100_000].reset_index(drop=True)
gdf["start_date"] = pd.to_datetime(gdf.year.apply(lambda x: "2022-10-01"))
gdf["end_date"] = pd.to_datetime(gdf.year.apply(lambda x: "2026-10-01"))

s2_sat = agl.sat.Sentinel2(use_sr=False)
build_chunk_download_urls(gdf, s2_sat, chunksize=3)

# aria2c --enable-rpc=true --rpc-listen-port=6800 --rpc-allow-origin-all=true --continue=true --max-concurrent-downloads=50 --max-connection-per-server=1 --split=1 --min-split-size=100M --timeout=120 --connect-timeout=60 --max-tries=0 --retry-wait=20 --always-resume=true --auto-file-renaming=false --file-allocation=none --max-file-not-found=0 --log=aria2.log --log-level=notice --save-session=aria2.session --save-session-interval=30
