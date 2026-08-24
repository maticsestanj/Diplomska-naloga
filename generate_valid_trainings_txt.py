import os

from riderx_filter import load_valid_riderx


base_folder = r"C:\Users\Matic\Desktop\Diplomska\Diplomska_naloga\DiplomskaNaloga\diplomskanaloga"

athlete_numbers = [1, 3, 6, 7]


#Filtriranje aktivnosti za izbrane športnike
for athlete_number in athlete_numbers:
    athlete_name = f"Athlete{athlete_number}"
    athlete_folder = os.path.join(base_folder, athlete_name)

    print(f"\nFiltriram: {athlete_name}")

    try:
        valid_trainings = load_valid_riderx(athlete_folder)
    except Exception as e:
        print(f"Napaka pri {athlete_name}: {e}")
        continue

    
    output_file = os.path.join(
        base_folder,
        f"valid_trainings_{athlete_name}.txt"
    )

    with open(output_file, "w", encoding="utf-8") as f:
        for file, _ in valid_trainings:
            f.write(file + "\n")

    print(
        f"Shranjeno: {output_file} "
        f"({len(valid_trainings)} aktivnosti)"
    )

print("\nFiltriranje končano.")