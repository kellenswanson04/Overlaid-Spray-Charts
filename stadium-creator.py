import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def create_goss_stadium_chart(batted_balls=None):
    """
    Plots a 2D spray chart overlay of Goss Stadium.
    batted_balls: List of dicts containing 'distance', 'angle' (0=center, negative=left, positive=right), and optional 'type'
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # 1. Define Goss Stadium Outfield Wall Measurements
    # Format: (Angle in degrees from center line, Distance in feet)
    # Left is negative angle, Right is positive angle
    wall_specs = [
        (-45, 326),    # Left Field Line
        (-22.5, 365),  # Left Center
        (-11.25, 402), # Deep Left Center
        (0, 396),      # Dead Center
        (11.25, 402),  # Deep Right Center
        (22.5, 365),   # Right Center
        (45, 326)      # Right Field Line
    ]
    
    # Convert wall specs to X, Y coordinates for plotting
    wall_x = [dist * np.sin(np.radians(ang)) for ang, dist in wall_specs]
    wall_y = [dist * np.cos(np.radians(ang)) for ang, dist in wall_specs]
    
    # 2. Draw the Outfield Wall
    ax.plot(wall_x, wall_y, color='black', lw=3, label='Goss Stadium Wall')
    
    # Fill the outfield grass area roughly
    outline_x = [0] + wall_x + [0]
    outline_y = [0] + wall_y + [0]
    ax.fill(outline_x, outline_y, color='#e8f5e9', zorder=0) 
    
    # 3. Draw Foul Lines
    ax.plot([0, wall_x[0]], [0, wall_y[0]], color='black', lw=1.5)
    ax.plot([0, wall_x[-1]], [0, wall_y[-1]], color='black', lw=1.5)
    
    # 4. Draw Infield Diamond (90 ft basepaths)
    # Home plate is at (0,0)
    # First base: (90*sin(45), 90*cos(45)) -> approx (63.64, 63.64)
    # Second base: (0, 90*sqrt(2)) -> approx (0, 127.28)
    # Third base: (-63.64, 63.64)
    base_dist = 90
    coord = base_dist * np.sin(np.radians(45))
    
    infield_x = [0, coord, 0, -coord, 0]
    infield_y = [0, coord, base_dist * np.sqrt(2), coord, 0]
    ax.plot(infield_x, infield_y, color='#bcaaa4', lw=2, zorder=1) # Dirt color line
    
    # 5. Label the Wall Distances
    for ang, dist in wall_specs:
        rad = np.radians(ang)
        x = dist * np.sin(rad)
        y = dist * np.cos(rad)
        # Push labels slightly outside the wall
        ax.text(x * 1.03, y * 1.03, f"{dist}'", ha='center', va='center', fontweight='bold', fontsize=9)

    # 6. Plot the Ball Landing Positions
    if batted_balls:
        for ball in batted_balls:
            b_rad = np.radians(ball['angle'])
            bx = ball['distance'] * np.sin(b_rad)
            by = ball['distance'] * np.cos(b_rad)
            
            # Color code based on hit type
            color = 'red' if ball.get('hit_type') == 'Home Run' else 'blue'
            ax.scatter(bx, by, c=color, s=50, edgecolors='black', zorder=5)
            
    # Chart Styling
    ax.set_aspect('equal')
    ax.set_xlim(-300, 300)
    ax.set_ylim(-20, 450)
    ax.axis('off') # Hide grid lines for a clean look
    plt.title("Goss Stadium", fontsize=16, fontweight='bold', pad=20)
    
    return fig

fig = create_goss_stadium_chart()
fig.savefig('gossstadium.png', dpi=300, bbox_inches='tight')
plt.show()