import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Create the comprehensive PWA-Blockchain diagram
fig = go.Figure()

# Define colors
colors = {
    "PWA": "#1FB8CD",
    "Blockchain": "#DB4545", 
    "Bridge": "#2E8B57",
    "Performance": "#5D878F",
    "Background": "#D2BA4C"
}

# Add background rectangles for grouping
fig.add_shape(
    type="rect",
    x0=0.2, y0=-0.5, x1=2.3, y1=6,
    fillcolor="rgba(31,184,205,0.1)",
    line=dict(color="#1FB8CD", width=2),
    layer="below"
)

fig.add_shape(
    type="rect", 
    x0=4.2, y0=-0.5, x1=6.3, y1=6,
    fillcolor="rgba(219,69,69,0.1)",
    line=dict(color="#DB4545", width=2),
    layer="below"
)

# PWA Features (left side) - better spaced
pwa_data = [
    {"name": "Service Worker", "detail": "Cache Strategy", "x": 1.25, "y": 5.2},
    {"name": "Offline Mode", "detail": "Full Function", "x": 1.25, "y": 4.4},
    {"name": "Push Notifs", "detail": "Workout Alert", "x": 1.25, "y": 3.6},
    {"name": "Background Sync", "detail": "Data Queue", "x": 1.25, "y": 2.8},
    {"name": "App Install", "detail": "Native Feel", "x": 1.25, "y": 2.0},
    {"name": "Performance", "detail": "95+ Score", "x": 1.25, "y": 1.2}
]

# Blockchain Features (right side) - better spaced
blockchain_data = [
    {"name": "Polygon zkEVM", "detail": "Chain 1101", "x": 5.25, "y": 5.2},
    {"name": "Smart Contract", "detail": "$FIXIE Token", "x": 5.25, "y": 4.4},
    {"name": "Wallet Connect", "detail": "MetaMask+", "x": 5.25, "y": 3.6},
    {"name": "NFT Metadata", "detail": "IPFS Store", "x": 5.25, "y": 2.8},
    {"name": "Token Transfer", "detail": "Staking", "x": 5.25, "y": 2.0},
    {"name": "TX Confirm", "detail": "$0.001 Cost", "x": 5.25, "y": 1.2}
]

# Add PWA feature nodes
for i, item in enumerate(pwa_data):
    fig.add_trace(go.Scatter(
        x=[item["x"]],
        y=[item["y"]],
        mode='markers',
        marker=dict(size=30, color=colors["PWA"], line=dict(width=2, color='white')),
        showlegend=False,
        hovertext=f"{item['name']}<br>{item['detail']}",
        hoverinfo='text'
    ))
    
    # Add text labels to the right of PWA nodes
    fig.add_annotation(
        text=f"{item['name'][:15]}",
        x=item["x"] + 0.4, y=item["y"],
        showarrow=False,
        font=dict(size=11, color="#1FB8CD"),
        xanchor="left"
    )

# Add Blockchain feature nodes
for i, item in enumerate(blockchain_data):
    fig.add_trace(go.Scatter(
        x=[item["x"]],
        y=[item["y"]],
        mode='markers',
        marker=dict(size=30, color=colors["Blockchain"], line=dict(width=2, color='white')),
        showlegend=False,
        hovertext=f"{item['name']}<br>{item['detail']}",
        hoverinfo='text'
    ))
    
    # Add text labels to the left of Blockchain nodes
    fig.add_annotation(
        text=f"{item['name'][:15]}",
        x=item["x"] - 0.4, y=item["y"],
        showarrow=False,
        font=dict(size=11, color="#DB4545"),
        xanchor="right"
    )

# Add central Web3 Bridge with larger prominence
fig.add_trace(go.Scatter(
    x=[3.25],
    y=[3.2],
    mode='markers',
    marker=dict(size=50, color=colors["Bridge"], line=dict(width=3, color='white')),
    name="Web3 Bridge",
    hovertext="Web3 APIs<br>Bridge Layer",
    hoverinfo='text'
))

fig.add_annotation(
    text="Web3 APIs",
    x=3.25, y=3.2,
    showarrow=False,
    font=dict(size=12, color="white"),
    xanchor="center"
)

# Add directional arrows from PWA to Web3 Bridge
for item in pwa_data:
    fig.add_annotation(
        ax=item["x"] + 0.15, ay=item["y"],
        x=2.9, y=3.2,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#5D878F",
        showarrow=True,
        text=""
    )

# Add directional arrows from Web3 Bridge to Blockchain
for item in blockchain_data:
    fig.add_annotation(
        ax=3.6, ay=3.2,
        x=item["x"] - 0.15, y=item["y"],
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#5D878F",
        showarrow=True,
        text=""
    )

# Add section headers
fig.add_annotation(
    text="PWA Features",
    x=1.25, y=6.2,
    showarrow=False,
    font=dict(size=16, color="#1FB8CD"),
    bgcolor="white",
    bordercolor="#1FB8CD",
    borderwidth=2
)

fig.add_annotation(
    text="Blockchain",
    x=5.25, y=6.2,
    showarrow=False,
    font=dict(size=16, color="#DB4545"),
    bgcolor="white",
    bordercolor="#DB4545",
    borderwidth=2
)

# Add improved performance metrics boxes
fig.add_shape(
    type="rect",
    x0=0.3, y0=0.3, x1=2.2, y1=0.8,
    fillcolor="rgba(31,184,205,0.2)",
    line=dict(color="#1FB8CD", width=2)
)

fig.add_annotation(
    text="PWA Metrics:<br>Load <2s | Score 95+<br>Size <500KB",
    x=1.25, y=0.55,
    showarrow=False,
    font=dict(size=10, color="#1FB8CD"),
    xanchor="center"
)

fig.add_shape(
    type="rect",
    x0=4.3, y0=0.3, x1=6.2, y1=0.8,
    fillcolor="rgba(219,69,69,0.2)",
    line=dict(color="#DB4545", width=2)
)

fig.add_annotation(
    text="Chain Metrics:<br>Block 2-3s | Fee $0.001<br>Network 1101",
    x=5.25, y=0.55,
    showarrow=False,
    font=dict(size=10, color="#DB4545"),
    xanchor="center"
)

# Update layout
fig.update_layout(
    title="FixieRun PWA & Blockchain Integration",
    xaxis=dict(
        range=[0, 6.5],
        showgrid=False,
        showticklabels=False,
        zeroline=False
    ),
    yaxis=dict(
        range=[0, 6.8],
        showgrid=False,
        showticklabels=False,
        zeroline=False
    ),
    legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='center', x=0.5),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='white'
)

fig.update_traces(cliponaxis=False)

# Save the chart
fig.write_image("fixierun_pwa_blockchain_architecture.png")