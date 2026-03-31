"""Visualization: charts and themes."""

from human_condition.viz.charts import (
    emotion_heatmap,
    topic_scatter,
    similarity_matrix,
    compression_curve,
    source_distribution,
    emotion_timeline_chart,
    topic_barchart,
    word_cloud_data,
    radar_chart,
    summary_stats,
    apply_theme,
    save_chart,
)
from human_condition.viz.theme import (
    BG_PRIMARY,
    ACCENT_GOLD,
    ACCENT_CYAN,
    PLOTLY_TEMPLATE,
    FONT_FAMILY,
    PALETTE,
)

__all__ = [
    "emotion_heatmap",
    "topic_scatter",
    "similarity_matrix",
    "compression_curve",
    "source_distribution",
    "emotion_timeline_chart",
    "topic_barchart",
    "word_cloud_data",
    "radar_chart",
    "summary_stats",
    "apply_theme",
    "save_chart",
    "BG_PRIMARY",
    "ACCENT_GOLD",
    "ACCENT_CYAN",
    "PLOTLY_TEMPLATE",
    "FONT_FAMILY",
    "PALETTE",
]
