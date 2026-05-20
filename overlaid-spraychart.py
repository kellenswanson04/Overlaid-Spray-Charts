import os
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==============================================================================
# CONFIGURATION AND PARAMETERS
# ==============================================================================
team_name = "ORE_BEA" 

OUTCOME_COLORS = {
    'Single':   (255/255.0, 193/255.0, 7/255.0),    # Yellow
    'Double':   (33/255.0,  150/255.0, 243/255.0),   # Blue
    'Triple':   (156/255.0, 39/255.0,  176/255.0),   # Purple
    'Home Run': (244/255.0, 67/255.0,  54/255.0),    # Red
    'Out':      (158/255.0, 158/255.0, 158/255.0)     # Gray
}

def get_file_path_via_popup():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    print("Please select your Trackman CSV file...")
    file_path = filedialog.askopenfilename(
        title="Select Trackman CSV Data File",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )
    root.destroy()
    return file_path

def sanitize_name_for_path(name):
    sanitized = "".join([char if char.isalnum() or char in (' ', '_', '-') else '_' for char in name])
    return sanitized.strip().replace(' ', '_')

# ==============================================================================
# VECTOR STADIUM GENERATOR (Bypasses background PNG scaling drift)
# ==============================================================================
def draw_goss_stadium_wireframe(ax):
    """Draws a mathematically true vector profile of Goss Stadium onto the canvas."""
    # Custom fence distances parsed out by direct field tracking angles
    wall_specs = [
        (-45, 326),    # Left Field Line
        (-22.5, 365),  # Left Center
        (-11.25, 402), # Deep Left Center
        (0, 396),      # Dead Center
        (11.25, 402),  # Deep Right Center
        (22.5, 365),   # Right Center
        (45, 326)      # Right Field Line
    ]
    
    wall_x = [dist * np.sin(np.radians(ang)) for ang, dist in wall_specs]
    wall_y = [dist * np.cos(np.radians(ang)) for ang, dist in wall_specs]
    
    # Fill Outfield Grass Area Poly structure
    outline_x = [0] + wall_x + [0]
    outline_y = [0] + wall_y + [0]
    ax.fill(outline_x, outline_y, color='#f1f8e9', zorder=1) 
    ax.plot(wall_x, wall_y, color='#263238', lw=3.5, zorder=3)
    
    # Foul Lines execution
    ax.plot([0, wall_x[0]], [0, wall_y[0]], color='#263238', lw=1.5, zorder=2)
    ax.plot([0, wall_x[-1]], [0, wall_y[-1]], color='#263238', lw=1.5, zorder=2)
    
    # Infield Diamond Profile setup (90ft baselines)
    base_dist = 90
    coord = base_dist * np.sin(np.radians(45))
    infield_x = [0, coord, 0, -coord, 0]
    infield_y = [0, coord, base_dist * np.sqrt(2), coord, 0]
    ax.plot(infield_x, infield_y, color='#d7ccc8', lw=2, zorder=2)
    
    # Annotate fence depths
    for ang, dist in wall_specs:
        rad = np.radians(ang)
        ax.text(dist * np.sin(rad) * 1.05, dist * np.cos(rad) * 1.05, f"{dist}'", 
                ha='center', va='center', fontweight='bold', fontsize=9, color='#37474f', zorder=4)

# ==============================================================================
# PIPELINE EXECUTION ENGINE
# ==============================================================================
def generate_team_spray_charts():
    csv_path = get_file_path_via_popup()
    if not csv_path:
        print("Operation cancelled: No file selected.")
        return

    df = pd.read_csv(csv_path)

    # Normalize outcome data syntax
    df['PlayResult'] = (
        df['PlayResult']
            .astype(str)
            .str.strip()
            .replace({
                'HomeRun': 'Home Run',
                'home run': 'Home Run',
                'homerun': 'Home Run'
            })
    )

    team_filtered_df = df[df['BatterTeam'].astype(str).str.upper() == team_name.upper()]
    if team_filtered_df.empty:
        print(f"Warning: No data matched target team label '{team_name}'")
        return

    allowed_results = {'Single', 'Double', 'Triple', 'Home Run'}
    hit_df = team_filtered_df[team_filtered_df['PlayResult'].isin(allowed_results)]

    result_folder = os.path.join('results', sanitize_name_for_path(team_name))
    os.makedirs(result_folder, exist_ok=True)

    player_groups = team_filtered_df.groupby('Batter')
    print(f"Processing data pipeline for {len(player_groups)} batters on team '{team_name}'...")

    for batter_name, data_slice in player_groups:
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Draw the field cleanly via code vectors (Guarantees perfect pixel scaling every loop)
        draw_goss_stadium_wireframe(ax)
        
        # Filter down hits
        batter_hits = hit_df[hit_df['Batter'] == batter_name]

        if not batter_hits.empty:
            for _, ball in batter_hits.iterrows():
                # Correcting for Surveyor Trackman Angular Vectors
                angle_rad = np.radians(ball['Bearing'])
                distance_ft = ball['Distance']
                outcome = ball['PlayResult']
                
                # Polar conversion to structural cartesian plane 
                x_coord = distance_ft * np.sin(angle_rad)
                y_coord = distance_ft * np.cos(angle_rad)
                
                rgb_color = OUTCOME_COLORS.get(outcome, (0.0, 0.0, 0.0))
                marker_size = 110 if outcome == 'Home Run' else 65
                marker_shape = '*' if outcome == 'Home Run' else 'o'
                
                ax.scatter(
                    x_coord, y_coord, 
                    color=rgb_color, 
                    s=marker_size, 
                    marker=marker_shape, 
                    edgecolors='#212121', 
                    linewidths=1.2, 
                    zorder=5, 
                    label=outcome
                )

            # Standardize Legend Box without duplicates
            legend_handles, legend_labels = ax.get_legend_handles_labels()
            unique_labels = dict(zip(legend_labels, legend_handles))
            ax.legend(
                unique_labels.values(), unique_labels.keys(), 
                loc='upper left', 
                framealpha=0.95, 
                fontsize=10
            )
        
        # Enforce strict viewing geometry profiles
        ax.set_aspect('equal')
        ax.set_xlim(-300, 300)
        ax.set_ylim(-20, 450)
        ax.axis('off') 
        
        ax.set_title(f"{batter_name} — Spray Chart Overlay", fontsize=15, fontweight='bold', pad=12)
        
        sanitized_filename = "".join([char for char in batter_name if char.isalnum() or char.isspace()])
        sanitized_filename = sanitized_filename.replace(" ", "-")
        output_filename = os.path.join(result_folder, f"{sanitized_filename}-spraychart.png")
        
        # Safe structural writing
        plt.savefig(output_filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f" Saved: {output_filename}")

if __name__ == "__main__":
    generate_team_spray_charts()