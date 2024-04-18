import matplotlib.pyplot as plt
import numpy as np

def plot_radar_chart(features):
    # トラックのオーディオ特性に基づいてレーダーチャートを描画する
    labels = np.array(['Danceability', 'Energy', 'Speechiness', 'Acousticness', 'Instrumentalness', 'Liveness', 'Valence'])
    stats = np.array([features['danceability'], features['energy'], features['speechiness'],
                      features['acousticness'], features['instrumentalness'], features['liveness'], features['valence']])
    
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    stats = np.concatenate((stats,[stats[0]]))
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, stats, color='red', alpha=0.25)
    ax.plot(angles, stats, color='red', linewidth=2)  # Plot the data
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    
    return fig