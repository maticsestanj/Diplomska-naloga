import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from math import radians, sin, cos, asin
from matplotlib.patches import Patch
from gpx_loader import load_gpx_to_df



base_folder = r"C:\Users\Matic\Desktop\Diplomska\Diplomska_naloga\DiplomskaNaloga\diplomskanaloga"

#Velikost intervala
BIN_SIZE = 100


def haversine(lat1, lon1, lat2, lon2):
    

    R = 6371000  # polmer Zemlje v metrih

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    return 2 * R * asin(np.sqrt(a))

# Klasifikacija odsekov glede na naklon
def classify(g):
    
    
    if pd.isna(g):
        return None

    if g > 1:
        return "vzpon"

    if g < -1:
        return "spust"

    return "ravnina"

#Glajenje podatkov
def smooth_series(series, window=5):
    

    return series.rolling(
        window=window,
        center=True,
        min_periods=1
    ).mean()

#Priprava podatkov
def prepare_activity_dataframe(df):
    

    
    df = (
        df.dropna(subset=["lat", "lon", "elev_m"])
        .reset_index(drop=True)
        .copy()
    )

    
    if len(df) < 2:
        raise ValueError(
            "Aktivnost nima vsaj dveh veljavnih GPS-točk."
        )

    distances = [0.0]
    segment_lengths = [0.0]
    grades = [np.nan]

    # Izračun razdalje
    for i in range(1, len(df)):
        d = haversine(
            df.loc[i - 1, "lat"],
            df.loc[i - 1, "lon"],
            df.loc[i, "lat"],
            df.loc[i, "lon"]
        )

        
        distances.append(distances[-1] + d)

        
        segment_lengths.append(d)

        
        elev_diff = (
            df.loc[i, "elev_m"]
            - df.loc[i - 1, "elev_m"]
        )

        
        grades.append(
            elev_diff / d * 100
            if d > 0
            else np.nan
        )

    df["dist_m"] = distances
    df["segment_length_m"] = segment_lengths
    df["grade_%"] = grades

    
    df["segment"] = (
        df["grade_%"]
        .apply(classify)
    )

    
    df["dist_bin"] = (
        df["dist_m"] // BIN_SIZE
    ).astype(int)

    
    df_avg = (
        df.groupby("dist_bin")
        .agg({
            "dist_m": "mean",
            "elev_m": "mean",
            "hr_bpm": "mean",
            "cadence": "mean"
        })
    )

   
    length_records = []

    for i in range(1, len(df)):
        segment_class = df.loc[i, "segment"]

        
        if segment_class is None or pd.isna(segment_class):
            continue

        start_dist = df.loc[i - 1, "dist_m"]
        end_dist = df.loc[i, "dist_m"]

        if end_dist <= start_dist:
            continue

        
        first_bin = int(start_dist // BIN_SIZE)
        last_bin = int((end_dist - 1e-9) // BIN_SIZE)

        for bin_id in range(first_bin, last_bin + 1):
            bin_start = bin_id * BIN_SIZE
            bin_end = (bin_id + 1) * BIN_SIZE

            
            overlap = max(
                0.0,
                min(end_dist, bin_end)
                - max(start_dist, bin_start)
            )

            if overlap > 0:
                length_records.append({
                    "dist_bin": bin_id,
                    "segment": segment_class,
                    "length_m": overlap
                })

    
    if length_records:
        length_df = pd.DataFrame(length_records)

        length_by_class = (
            length_df
            .groupby(["dist_bin", "segment"])["length_m"]
            .sum()
            .reset_index()
        )

        dominant_idx = (
            length_by_class
            .groupby("dist_bin")["length_m"]
            .idxmax()
        )

        dominant_segments = (
            length_by_class
            .loc[
                dominant_idx,
                ["dist_bin", "segment"]
            ]
            .set_index("dist_bin")
        )

        df_avg["segment"] = (
            dominant_segments["segment"]
            .reindex(df_avg.index)
        )

    else:
        df_avg["segment"] = None

    df_avg = df_avg.reset_index()

    
    df_avg["dist_km"] = (
        df_avg["dist_m"] / 1000.0
    )

   
    df_avg["elev_smooth"] = smooth_series(
        df_avg["elev_m"],
        7
    )

   
    df_avg["hr_smooth"] = smooth_series(
        df_avg["hr_bpm"],
        5
    )

    
    df_avg["cadence_smooth"] = smooth_series(
        df_avg["cadence"],
        5
    )

    return df, df_avg


def get_activity_stats(df, df_avg):
    
    elev_diff = (
        df_avg["elev_smooth"]
        .diff()
    )

    # Skupni  višinski prirastek
    elevation_gain = (
        elev_diff
        .clip(lower=0)
        .sum()
    )

    return {
        
        "gps_points": len(df),

        
        "distance_km": (
            df["dist_m"].iloc[-1]
            / 1000.0
        ),

        
        "elevation_gain": elevation_gain,

        
        "hr": (
            "Da"
            if df["hr_bpm"].notna().any()
            else "Ne"
        ),

        
        "cadence": (
            "Da"
            if df["cadence"].notna().any()
            else "Ne"
        )
    }

#Grafi
def plot_activity(df_avg, file_name):
    

    colors = {
        "vzpon": "#d62828",
        "spust": "#277da1",
        "ravnina": "#6c757d"
    }

    x = df_avg["dist_km"]

    
    fig, (ax1, ax2, ax3) = plt.subplots(
        3,
        1,
        figsize=(15, 10),
        sharex=True,
        gridspec_kw={
            "height_ratios": [2.2, 1.2, 1.2]
        }
    )

    fig.suptitle(
        f"Analiza vožnje: {file_name}",
        fontsize=18,
        y=0.98
    )

    
    ax1.plot(
        x,
        df_avg["elev_smooth"],
        color="black",
        linewidth=2.2,
        zorder=3
    )

    ymin = max(
        0,
        df_avg["elev_smooth"].min() - 20
    )

    
    for segment in ["vzpon", "spust", "ravnina"]:
        mask = (
            df_avg["segment"]
            == segment
        )

        ax1.fill_between(
            x,
            ymin,
            df_avg["elev_smooth"],
            where=mask,
            interpolate=True,
            alpha=0.30,
            color=colors[segment],
            zorder=1
        )

    ax1.set_title("Višinski profil poti")
    ax1.set_ylabel("Višina (m)")
    ax1.set_ylim(bottom=ymin)
    ax1.grid(True, linestyle="--", alpha=0.35)

    
    ax1.legend(
        handles=[
            Patch(
                facecolor=colors["vzpon"],
                alpha=0.30,
                label="Vzpon"
            ),
            Patch(
                facecolor=colors["spust"],
                alpha=0.30,
                label="Spust"
            ),
            Patch(
                facecolor=colors["ravnina"],
                alpha=0.30,
                label="Ravnina"
            )
        ],
        loc="upper right"
    )

    
    if df_avg["hr_bpm"].notna().any():
        ax2.plot(
            x,
            df_avg["hr_smooth"],
            color="#c1121f",
            linewidth=1.8
        )

    ax2.set_title("Srčni utrip med vožnjo")
    ax2.set_ylabel("bpm")
    ax2.grid(True, linestyle="--", alpha=0.35)

    
    if df_avg["cadence"].notna().any():
        ax3.plot(
            x,
            df_avg["cadence_smooth"],
            color="#2a9d8f",
            linewidth=1.8
        )

    ax3.set_title("Kadenca med vožnjo")
    ax3.set_ylabel("obr/min")
    ax3.set_xlabel("Razdalja (km)")
    ax3.grid(True, linestyle="--", alpha=0.35)

   
    for ax in (ax1, ax2, ax3):
        ax.spines["top"].set_alpha(0.2)
        ax.spines["right"].set_alpha(0.2)

    plt.tight_layout(
        rect=[0, 0, 1, 0.96]
    )

    plt.show()



athletes = [
    "Athlete1",
    "Athlete3",
    "Athlete6",
    "Athlete7"
]

print("\n----IZBERI ATLETE!----\n")

for i, athlete_name in enumerate(athletes, start=1):
    print(f"{i}: {athlete_name}")

# Izbira športnika
choice = int(
    input("\nVnesi številko izbire: ")
)

if choice < 1 or choice > len(athletes):
    raise Exception(
        "Neveljavna izbira atleta."
    )

athlete = athletes[choice - 1]

athlete_folder = os.path.join(
    base_folder,
    athlete
)


txt_path = os.path.join(
    base_folder,
    f"valid_trainings_{athlete}.txt"
)

if not os.path.exists(txt_path):
    raise Exception(
        f"TXT datoteka ne obstaja: {txt_path}"
    )


with open(txt_path, encoding="utf-8") as f:
    valid_files = [
        line.strip()
        for line in f
        if line.strip()
    ]

print(
    f"\nNajdenih {len(valid_files)} "
    f"veljavnih treningov za {athlete}"
)


rider_number = input(
    "Vnesi številko riderx aktivnosti: "
).strip()

wanted_file = (
    f"riderx{rider_number}.gpx"
)


if wanted_file not in valid_files:
    raise Exception(
        f"Aktivnost {wanted_file} ni med "
        f"veljavnimi treningi za {athlete}."
    )

file_path = os.path.join(
    athlete_folder,
    wanted_file
)

print(
    f"\n Analiza: "
    f"{athlete} / {wanted_file} "
)


df = load_gpx_to_df(file_path)


df, df_avg = prepare_activity_dataframe(df)


stats = get_activity_stats(
    df,
    df_avg
)


print("\n ----PODATKI ZA TABELO ----")
print(f"Datoteka: {wanted_file}")
print(f"GPS-točke: {stats['gps_points']}")
print(f"Dolžina: {stats['distance_km']:.1f} km")
print(f"Višinski metri: {stats['elevation_gain']:.0f} m")
print(f"HR: {stats['hr']}")
print(f"Kadenca: {stats['cadence']}")
print("------------------------------\n")


plot_activity(
    df_avg,
    wanted_file
)