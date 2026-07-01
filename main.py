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

# Import the database query tool library
from astroquery.gaia import Gaia

# Set the main Gaia table to the Gaia DR3 table
Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"

# Define the SQL query to fetch the star data
query = """
SELECT source_id, ra, dec, phot_g_mean_mag
FROM gaiadr3.gaia_source
WHERE ra > 0 AND ra < 10
ORDER BY phot_g_mean_mag ASC
"""

# Launch the job to fetch the star data
job = Gaia.launch_job(query)

# Get the results from the job
results = job.get_results()

# Print some sample star data
for i, row in enumerate(results, start=1):
    print(f"Star #{i}")
    print(f"  source_id: {row['source_id']}")
    print(f"  ra_deg: {row['ra']:.6f}")
    print(f"  dec_deg: {row['dec']:.6f}")
    print(f"  g_mag: {row['phot_g_mean_mag']:.3f}")
    print("-" * 30)


