import gpxpy
import pandas as pd
from pathlib import Path



def get_extension_value(point, tag_name):
    for extension in point.extensions:
        for elem in extension.iter():
            tag = elem.tag.split("}")[-1]

            if tag == tag_name and elem.text is not None:
                return elem.text

    return None



def load_gpx_to_df(gpx_path):
    gpx_path = Path(gpx_path)
    rows = []

    with open(gpx_path, "r", encoding="utf-8") as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                hr = get_extension_value(point, "hr")
                cadence = get_extension_value(point, "cad")
                temp = get_extension_value(point, "atemp")

                rows.append({
                    "file": gpx_path.name,
                    "time": point.time,
                    "lat": point.latitude,
                    "lon": point.longitude,
                    "elev_m": point.elevation,
                    "hr_bpm": int(hr) if hr else None,
                    "cadence": int(cadence) if cadence else None,
                    "temp_C": float(temp) if temp else None
                })

    df = pd.DataFrame(rows)

    if not df.empty:
        df["time"] = pd.to_datetime(
            df["time"],
            errors="coerce"
        )

    return df



def load_all_gpx(folder):
    folder = Path(folder)
    all_data = []

    gpx_files = list(folder.glob("*.gpx"))

    print(
        f"Najdenih {len(gpx_files)} GPX datotek v mapi {folder}"
    )

    for gpx_file in gpx_files:
        print(f"Berem: {gpx_file.name}")
        all_data.append(
            load_gpx_to_df(gpx_file)
        )

    if all_data:
        return pd.concat(
            all_data,
            ignore_index=True
        )

    print("V mapi ni GPX datotek.")
    return pd.DataFrame()