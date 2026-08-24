import os
from gpx_loader import load_gpx_to_df


REQUIRED_COLS = ["lat", "lon", "elev_m"]



def has_required_columns(df):
    if df.empty:
        return False

    valid_points = df[REQUIRED_COLS].dropna()

    return len(valid_points) >= 2



def load_valid_riderx(folder_path):
    if not os.path.exists(folder_path):
        raise Exception(f"Mapa ne obstaja: {folder_path}")

    gpx_files = [
        file
        for file in os.listdir(folder_path)
        if file.lower().startswith("riderx")
        and file.lower().endswith(".gpx")
    ]

    if not gpx_files:
        raise Exception("V mapi ni riderx GPX datotek.")

    valid_trainings = []

    for file in gpx_files:
        full_path = os.path.join(folder_path, file)

        try:
            df = load_gpx_to_df(full_path)
        except Exception as e:
            print(f"Napaka pri nalaganju {file}: {e}")
            continue

        if has_required_columns(df):
            valid_trainings.append((file, df))

            has_hr = df["hr_bpm"].notna().any()
            has_cadence = df["cadence"].notna().any()

            print(
                f"Sprejet: {file} "
                f"(HR: {'DA' if has_hr else 'NE'}, "
                f"CAD: {'DA' if has_cadence else 'NE'})"
            )

        else:
            print(
                f"Preskočen: {file} - "
                f"premalo veljavnih GPS podatkov"
            )

    if not valid_trainings:
        raise Exception(
            "Noben trening ne vsebuje dovolj veljavnih GPS podatkov."
        )

    return valid_trainings