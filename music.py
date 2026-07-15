#!/usr/bin/env python3

from math import log2

import mido
import numpy as np
from astroquery.gaia import Gaia


RA_MIN = 0.000
RA_MAX = 0.100
RA_BIN_SIZE = 0.001
STEP_SECONDS = 0.1
N_STARS = 1000

FREQ_MIN_HZ = 27.5
FREQ_MAX_HZ = 4186.0

OUTPUT_MIDI = "gaia_ra_music.mid"


def parallax_to_frequency(parallax_value: float, p_min: float, p_max: float) -> float:
    if p_max == p_min:
        return (FREQ_MIN_HZ + FREQ_MAX_HZ) / 2.0

    normalized = (parallax_value - p_min) / (p_max - p_min)
    return FREQ_MIN_HZ + normalized * (FREQ_MAX_HZ - FREQ_MIN_HZ)


def frequency_to_midi_note(freq_hz: float) -> int:
    midi_note = int(round(69 + 12 * log2(freq_hz / 440.0)))
    return max(0, min(127, midi_note))


def build_midi(stars):
    midi = mido.MidiFile(ticks_per_beat=480)
    track = mido.MidiTrack()
    midi.tracks.append(track)

    bpm = 120
    tempo = mido.bpm2tempo(bpm)
    track.append(mido.MetaMessage("set_tempo", tempo=tempo, time=0))

    ticks_per_second = midi.ticks_per_beat * bpm / 60.0
    step_ticks = int(round(STEP_SECONDS * ticks_per_second))

    # 0.100 / 0.001 -> 100 bins from [0.000, 0.100)
    n_bins = int(round((RA_MAX - RA_MIN) / RA_BIN_SIZE))

    bins = [[] for _ in range(n_bins)]
    for star in stars:
        ra = float(star["ra"])
        if not (RA_MIN <= ra < RA_MAX):
            continue
        bin_index = int((ra - RA_MIN) / RA_BIN_SIZE)
        bins[bin_index].append(star["midi_note"])

    pending_rest_ticks = 0
    active_bins = 0
    max_polyphony = 0

    for notes_in_bin in bins:
        if not notes_in_bin:
            pending_rest_ticks += step_ticks
            continue

        unique_notes = sorted(set(notes_in_bin))
        active_bins += 1
        max_polyphony = max(max_polyphony, len(unique_notes))

        for idx, note in enumerate(unique_notes):
            track.append(
                mido.Message(
                    "note_on",
                    note=note,
                    velocity=90,
                    time=pending_rest_ticks if idx == 0 else 0,
                )
            )

        pending_rest_ticks = 0

        for idx, note in enumerate(unique_notes):
            track.append(
                mido.Message(
                    "note_off",
                    note=note,
                    velocity=0,
                    time=step_ticks if idx == 0 else 0,
                )
            )

    midi.save(OUTPUT_MIDI)
    return active_bins, max_polyphony


def main():
    Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"

    query = f"""
    SELECT TOP {N_STARS}
        source_id,
        ra,
        parallax,
        phot_g_mean_mag
    FROM gaiadr3.gaia_source
    WHERE ra >= {RA_MIN}
      AND ra < {RA_MAX}
      AND parallax IS NOT NULL
      AND parallax > 0
    ORDER BY phot_g_mean_mag ASC
    """

    job = Gaia.launch_job(query)
    results = job.get_results()

    if len(results) == 0:
        print("No stars returned for the requested RA/parallax filter.")
        return

    parallax_values = np.array([float(row["parallax"]) for row in results], dtype=float)
    p_min = float(np.min(parallax_values))
    p_max = float(np.max(parallax_values))

    stars = []
    for row in results:
        parallax = float(row["parallax"])
        freq_hz = parallax_to_frequency(parallax, p_min, p_max)
        midi_note = frequency_to_midi_note(freq_hz)
        stars.append(
            {
                "source_id": int(row["source_id"]),
                "ra": float(row["ra"]),
                "parallax": parallax,
                "frequency_hz": freq_hz,
                "midi_note": midi_note,
            }
        )

    active_bins, max_polyphony = build_midi(stars)

    print(f"Fetched stars: {len(stars)}")
    print(f"Parallax range: {p_min:.6f} .. {p_max:.6f} mas")
    print(f"Frequency range mapped to: {FREQ_MIN_HZ} .. {FREQ_MAX_HZ} Hz")
    print(f"Saved MIDI: {OUTPUT_MIDI}")
    print(f"Active RA bins: {active_bins}")
    print(f"Max simultaneous notes in a bin: {max_polyphony}")


if __name__ == "__main__":
    main()
