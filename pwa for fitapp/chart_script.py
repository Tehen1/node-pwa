import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Architecture data with exact brand colors and correct components
architecture_data = {
    "architecture_layers": [
        {
            "layer": "UI Layer",
            "components": ["Service Work", "Web Manifest", "Offline Stor", "Push Notif", "Background", "Responsive"],
            "color": "#1FB8CD",
            "y_pos": 5
        },
        {
            "layer": "App Logic", 
            "components": ["Fitness Track", "Tokenomics", "NFT Mgmt", "Social", "Gamification", "Profile Mgmt"],
            "color": "#DB4545",
            "y_pos": 4
        },
        {
            "layer": "Blockchain",
            "components": ["Smart Contr", "Wallet Conn", "Token Mgmt", "NFT Market", "Tx Process"],
            "color": "#2E8B57",
            "y_pos": 3
        },
        {
            "layer": "Data Store",
            "components": ["IndexedDB", "Cache Stor", "Local State", "Sync Engine", "Offline Q"],
            "color": "#5D878F",
            "y_pos": 2
        },
        {
            "layer": "External API",
            "components": ["Google Fit", "Apple Health", "GPS Service", "Push Service", "IPFS Stor"],
            "color": "#D2BA4C",
            "y_pos": 1
        }
    ]
}

# Create the figure
fig = go.Figure()

# Add layer backgrounds and components
for layer_data in architecture_data["architecture_layers"]:
    layer_name = layer_data["layer"]
    components = layer_data["components"]
    color = layer_data["color"]
    y_pos = layer_data["y_pos"]
    
    # Add layer background rectangle
    fig.add_shape(
        type="rect",
        x0=0, y0=y_pos-0.45, x1=8, y1=y_pos+0.45,
        fillcolor=color,
        opacity=0.15,
        line=dict(color=color, width=3)
    )
    
    # Add layer title box
    fig.add_shape(
        type="rect",
        x0=0.1, y0=y_pos-0.2, x1=1.2, y1=y_pos+0.2,
        fillcolor=color,
        opacity=0.9,
        line=dict(color="white", width=2)
    )
    
    # Add layer title text
    fig.add_trace(go.Scatter(
        x=[0.65],
        y=[y_pos],
        mode='text',
        text=[layer_name],
        textfont=dict(size=11, color='white', family="Arial Black"),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Add components as prominent boxes
    for i, component in enumerate(components):
        x_pos = i + 1.8
        
        # Component box with high opacity
        fig.add_shape(
            type="rect",
            x0=x_pos-0.4, y0=y_pos-0.25, x1=x_pos+0.4, y1=y_pos+0.25,
            fillcolor=color,
            opacity=0.95,
            line=dict(color="white", width=2)
        )
        
        # Component text with good contrast
        fig.add_trace(go.Scatter(
            x=[x_pos],
            y=[y_pos],
            mode='text',
            text=[component],
            textfont=dict(size=10, color='white', family="Arial"),
            showlegend=False,
            hovertemplate=f'<b>{component}</b><br>Layer: {layer_name}<extra></extra>'
        ))

# Add data flow arrows using shapes instead of annotations
arrow_configs = [
    {"x": 2.5, "from_y": 4.55, "to_y": 4.45, "color": "#333333"},  # UI to App
    {"x": 3.5, "from_y": 3.55, "to_y": 3.45, "color": "#333333"},  # App to Blockchain
    {"x": 4.5, "from_y": 3.55, "to_y": 2.45, "color": "#333333"},  # App to Data
    {"x": 5.5, "from_y": 1.55, "to_y": 3.45, "color": "#333333"},  # External to App
    {"x": 6.5, "from_y": 2.55, "to_y": 4.45, "color": "#333333"}   # Data to UI
]

for arrow in arrow_configs:
    # Arrow line
    fig.add_shape(
        type="line",
        x0=arrow["x"], y0=arrow["from_y"], 
        x1=arrow["x"], y1=arrow["to_y"],
        line=dict(color=arrow["color"], width=4)
    )
    
    # Arrow head (triangle)
    if arrow["from_y"] > arrow["to_y"]:  # Downward arrow
        fig.add_shape(
            type="path",
            path=f"M {arrow['x']-0.05},{arrow['to_y']+0.05} L {arrow['x']},{arrow['to_y']} L {arrow['x']+0.05},{arrow['to_y']+0.05} Z",
            fillcolor=arrow["color"],
            line=dict(color=arrow["color"], width=0)
        )
    else:  # Upward arrow
        fig.add_shape(
            type="path",
            path=f"M {arrow['x']-0.05},{arrow['to_y']-0.05} L {arrow['x']},{arrow['to_y']} L {arrow['x']+0.05},{arrow['to_y']-0.05} Z",
            fillcolor=arrow["color"],
            line=dict(color=arrow["color"], width=0)
        )

# Update layout
fig.update_layout(
    title="FixieRun PWA Architecture",
    xaxis=dict(
        range=[0, 8],
        showticklabels=False,
        showgrid=False,
        zeroline=False,
        visible=False
    ),
    yaxis=dict(
        range=[0, 5.5],
        showticklabels=False,
        showgrid=False,
        zeroline=False,
        visible=False
    ),
    showlegend=False,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family="Arial")
)

fig.update_traces(cliponaxis=False)

# Save the chart
fig.write_image("fixie_architecture.png")