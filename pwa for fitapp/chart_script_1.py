import plotly.graph_objects as go
import plotly.io as pio
import numpy as np

# Create a cleaner circular flow diagram
fig = go.Figure()

# Define main circular positions for key components
angles = np.linspace(0, 2*np.pi, 9, endpoint=False)
radius = 3

# Main cycle nodes (circular arrangement)
main_nodes = [
    ("Running\n1.2$/km", '#1FB8CD'),
    ("Cycling\n0.8$/km", '#1FB8CD'), 
    ("Walking\n0.5$/km", '#1FB8CD'),
    ("Distance Rwds\n45k daily", '#2E8B57'),
    ("Milestone Bon\n+50% tokens", '#2E8B57'),
    ("NFT Purchase\n10-100 tokens", '#5D878F'),
    ("Marketplace\n2.5% fee", '#5D878F'),
    ("NFT Upgrades\n10-50 burned", '#DB4545'),
    ("Market Fees\n2.5% burned", '#DB4545')
]

# Plot main circular nodes
for i, (label, color) in enumerate(main_nodes):
    x = radius * np.cos(angles[i])
    y = radius * np.sin(angles[i])
    
    fig.add_trace(go.Scatter(
        x=[x], y=[y],
        mode='markers+text',
        marker=dict(size=60, color=color, line=dict(width=3, color='white')),
        text=label,
        textposition='middle center',
        textfont=dict(size=11, color='white', family="Arial Black"),
        showlegend=False,
        hoverinfo='skip'
    ))

# Add center hub for token economy
fig.add_trace(go.Scatter(
    x=[0], y=[0],
    mode='markers+text',
    marker=dict(size=100, color='#964325', line=dict(width=4, color='white')),
    text="$FIXIE<br>Economy<br>500k emit<br>200k burn",
    textposition='middle center',
    textfont=dict(size=12, color='white', family="Arial Black"),
    showlegend=False,
    hoverinfo='skip'
))

# Add external factors (outer ring)
external_radius = 4.5
external_angles = [np.pi/4, np.pi, 7*np.pi/4]
external_nodes = [
    ("Seasonal Bon\n+25%", '#D2BA4C'),
    ("Social Rwds\n+10%", '#D2BA4C'),
    ("Achievements\n+100 tokens", '#D2BA4C')
]

for i, (label, color) in enumerate(external_nodes):
    x = external_radius * np.cos(external_angles[i])
    y = external_radius * np.sin(external_angles[i])
    
    fig.add_trace(go.Scatter(
        x=[x], y=[y],
        mode='markers+text',
        marker=dict(size=45, color=color, line=dict(width=2, color='white')),
        text=label,
        textposition='middle center',
        textfont=dict(size=9, color='white', family="Arial Black"),
        showlegend=False,
        hoverinfo='skip'
    ))

# Add curved arrows showing flow direction (simplified)
# Main flow arrows
flow_arrows = [
    # Activities to earning (clockwise flow)
    (angles[0], angles[3], "15k"),  # Running to Distance
    (angles[1], angles[4], "10k"),  # Cycling to Milestone  
    (angles[2], angles[3], "8k"),   # Walking to Distance
    
    # Earning to utility
    (angles[3], angles[5], "20k"),  # Distance to NFT Purchase
    (angles[4], angles[6], "12k"),  # Milestone to Marketplace
    
    # Utility to burning
    (angles[5], angles[7], "15k"),  # NFT Purchase to Upgrades
    (angles[6], angles[8], "5k"),   # Marketplace to Fees
    
    # External to earning
    (external_angles[0], angles[3], "5k"),  # Seasonal to Distance
    (external_angles[1], angles[4], "3k"),  # Social to Milestone
]

for start_angle, end_angle, amount in flow_arrows:
    # Calculate arrow positions
    start_x = (radius - 0.3) * np.cos(start_angle)
    start_y = (radius - 0.3) * np.sin(start_angle)
    end_x = (radius - 0.3) * np.cos(end_angle)
    end_y = (radius - 0.3) * np.sin(end_angle)
    
    # Add arrow
    fig.add_annotation(
        x=end_x, y=end_y,
        ax=start_x, ay=start_y,
        arrowhead=3,
        arrowsize=1.5,
        arrowwidth=3,
        arrowcolor='#666666',
        showarrow=True
    )
    
    # Add flow amount label
    mid_x = (start_x + end_x) / 2
    mid_y = (start_y + end_y) / 2
    
    fig.add_trace(go.Scatter(
        x=[mid_x], y=[mid_y],
        mode='text',
        text=amount,
        textfont=dict(size=10, color='#333333', family="Arial Bold"),
        showlegend=False,
        hoverinfo='skip'
    ))

# Add section headers
section_headers = [
    (-4.5, 3.5, "EARN", '#1FB8CD'),
    (0, 5.5, "BOOST", '#D2BA4C'),
    (4.5, 3.5, "BURN", '#DB4545'),
    (0, -5.5, "SUPPLY", '#B4413C')
]

for x, y, text, color in section_headers:
    fig.add_trace(go.Scatter(
        x=[x], y=[y],
        mode='text',
        text=f"<b>{text}</b>",
        textfont=dict(size=16, color=color, family="Arial Black"),
        showlegend=False,
        hoverinfo='skip'
    ))

# Update layout for better presentation
fig.update_layout(
    title="$FIXIE M2E Token Economy",
    xaxis=dict(range=[-6, 6], visible=False, fixedrange=True),
    yaxis=dict(range=[-6, 6], visible=False, fixedrange=True),
    plot_bgcolor='white',
    showlegend=False,
    annotations=[
        dict(
            text="Net Daily Growth: +300k tokens",
            x=0, y=-6,
            xref="x", yref="y",
            font=dict(size=12, color='#333333'),
            showarrow=False
        )
    ]
)

# Ensure equal aspect ratio for proper circle
fig.update_yaxes(scaleanchor="x", scaleratio=1)

# Save the chart
fig.write_image("fixie_tokenomics_flow.png", width=1000, height=1000, scale=2)