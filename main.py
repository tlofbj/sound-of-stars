# Hi crew, this is a minimal implementation to fetch star data from the Gaia DR3 database.

# INSTALLATION:
# ! pip install -r requirements.txt
# ! python3 main.py

# TASK FROM MITCH:
# Make a distribution histogram of the 2000 star data with parallaxes and periods (use intensity as alt)
# Agnes, try to understand this script and try to implement the histogram and understand what it means
# To push your changes to GitHub: ! git add . && git commit -m "Name of your change" && git push
# To pull the latest changes from GitHub: ! git pull
# Note: "!" means run the command in the terminal

from astroquery.gaia import Gaia
import matplotlib.pyplot as plt
import numpy as np

# Set the main Gaia table to the Gaia DR3 table
Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"

# Fetch 2000 variable stars with parallax and period information.
# We use the Gaia RR Lyrae variability table because it contains period data (pf) and intensity information.
query = """
SELECT TOP 2000
    gs.source_id,
    gs.ra,
    gs.dec,
    gs.parallax,
    vr.pf AS period_days,
    vr.int_average_g AS intensity
FROM gaiadr3.gaia_source AS gs
JOIN gaiadr3.vari_rrlyrae AS vr
    ON gs.source_id = vr.source_id
WHERE gs.parallax IS NOT NULL
  AND vr.pf > 0
ORDER BY gs.parallax DESC
"""

# Launch the job to fetch the star data
job = Gaia.launch_job(query)
results = job.get_results()

# Convert the result columns into numpy arrays for plotting
parallaxes = np.array([row["parallax"] for row in results], dtype=float)
periods = np.array([row["period_days"] for row in results], dtype=float)
intensity = np.array([row["intensity"] for row in results], dtype=float)

# Filter out any invalid measurements
valid = (
    (parallaxes > 0)
    & (periods > 0)
    & np.isfinite(parallaxes)
    & np.isfinite(periods)
)
parallaxes = parallaxes[valid]
periods = periods[valid]
intensity = intensity[valid]

print(f"Fetched {len(parallaxes)} stars with parallax, period, and intensity data.")
print("Sample star records:\n")
for i, row in enumerate(results[:5], start=1):
    print(f"Star #{i}")
    print(f"  source_id: {row['source_id']}")
    print(f"  ra_deg: {row['ra']:.6f}")
    print(f"  dec_deg: {row['dec']:.6f}")
    print(f"  parallax: {row['parallax']:.3f} mas")
    print(f"  period: {row['period_days']:.5f} days")
    print(f"  intensity (mean G): {row['intensity']:.3f}")
    print("-" * 30)

# Plot distribution histograms of parallax and period.
fig, axs = plt.subplots(1, 3, figsize=(18, 5), constrained_layout=True)

axs[0].hist(parallaxes, bins=30, color="cornflowerblue", edgecolor="black")
axs[0].set_title("Parallax distribution")
axs[0].set_xlabel("Parallax (mas)")
axs[0].set_ylabel("Star count")

axs[1].hist(periods, bins=30, color="salmon", edgecolor="black")
axs[1].set_title("Period distribution")
axs[1].set_xlabel("Period (days)")
axs[1].set_ylabel("Star count")

# Use intensity as an alternate visual encoding in the scatter plot.
axs[2].scatter(periods, parallaxes, c=intensity, cmap="plasma", s=20, alpha=0.8)
axs[2].set_title("Parallax vs Period with intensity")
axs[2].set_xlabel("Period (days)")
axs[2].set_ylabel("Parallax (mas)")
colorbar = fig.colorbar(axs[2].collections[0], ax=axs[2])
colorbar.set_label("Intensity (mean G)")

output_file = "gaia_parallax_period_histograms.png"
fig.savefig(output_file, dpi=150)
print(f"Saved histogram figure to {output_file}")
plt.show()


