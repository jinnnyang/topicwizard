from typing import Any, List

import dash_mantine_components as dmc
import numpy as np
import pandas as pd
from dash_extensions.enrich import DashBlueprint, dcc, html
from plotly import colors

import topicwizard.prepare.groups as prepare
from topicwizard.components.groups.group_barplot import create_group_barplot
from topicwizard.components.groups.group_map import create_group_map
from topicwizard.components.groups.group_wordcloud import create_group_wordcloud


def create_blueprint(
    vocab: np.ndarray,
    document_term_matrix: np.ndarray,
    document_topic_matrix: np.ndarray,
    topic_term_matrix: np.ndarray,
    corpus: List[str],
    group_labels: List[str],
    **kwargs,
) -> DashBlueprint:
    # --------[ Preparing data ]--------
    group_id_labels, group_names = pd.factorize(group_labels)
    n_groups = group_names.shape[0]
    (
        group_importances,
        group_term_importances,
        group_topic_importances,
    ) = prepare.group_importances(
        document_topic_matrix, document_term_matrix, group_id_labels, n_groups
    )
    group_positions = prepare.group_positions(group_term_importances)
    dominant_topics = prepare.dominant_topic(
        group_topic_importances=group_topic_importances
    )
    # Creating unified color scheme
    color_scheme = colors.get_colorscale("Portland")
    n_topics = topic_term_matrix.shape[0]
    topic_colors = colors.sample_colorscale(
        color_scheme, np.arange(n_topics) / n_topics, low=0.25, high=1.0
    )
    topic_colors = np.array(topic_colors)
    # --------[ Collecting blueprints ]--------
    group_map = create_group_map(
        group_positions, group_importances, group_names, dominant_topics, topic_colors
    )
    group_wordcloud = create_group_wordcloud(group_term_importances, vocab)
    group_barchart = create_group_barplot(group_topic_importances, topic_colors)
    blueprints = [
        group_map,
        group_wordcloud,
        group_barchart,
    ]

    # --------[ Creating app blueprint ]--------
    app_blueprint = DashBlueprint()
    app_blueprint.layout = html.Div(
        [
            dcc.Store("selected_group", data=0),
            dmc.Group(
                [
                    group_map.layout,
                    dmc.Stack(
                        [group_barchart.layout, group_wordcloud.layout],
                        align="stretch",
                        justify="space-around",
                        className="flex-1",
                    ),
                ],
                grow=1,
                align="stretch",
                position="apart",
                className="flex-1 p-3",
            ),
        ],
        className="""
        hidden
        """,
        id="groups_container",
    )

    # --------[ Registering callbacks ]--------
    for blueprint in blueprints:
        blueprint.register_callbacks(app_blueprint)
    return app_blueprint
