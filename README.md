# SprayChart

Python project for generating spray chart PNGs over a user-generated stadium background image. The code uses Trackman distance and bearing to properly overlay the spray chart onto the desired field dimensions.

## Overview

- `overlaid-spraychart.py` — main script that opens a file-picker popup to select a CSV, filters valid hit outcomes, and exports one spray chart PNG per batter.
- `stadium-creator.py` — helper script that generates the desired stadium background image.
- `gossstadium.png` — the stadium image used as my default chart background/home stadium.


## How it Works

- The script loads the selected CSV file.
- It filters the records to include only these hit outcomes:
  - `Single`
  - `Double`
  - `Triple`
  - `Home Run`
- It groups data by batter name and generates a separate chart for each player.
- Players with no valid hits still receive a blank spray chart image.
- Charts are saved to `results/<team_name>/`.

## Customization

- Change `team_name` in `overlaid-spraychart.py` to target a different team.
- Update `png_path` in `overlaid-spraychart.py` if the stadium image is moved or renamed.
- Update 'wall_specs' in `overlaid-spraychart.py` to ensure proper overlay math is completed.
- If you want to regenerate the stadium background image, update 'wall_specs' in `stadium-creator.py` then run:

```powershell
python stadium-creator.py
```

## Output

- Charts are saved as PNG files.
- Filenames are based on player names and sanitized for file paths.
- Output folder structure is:

```text
results/<team_name>/
```

## Credits

- Author: Kellen Swanson
