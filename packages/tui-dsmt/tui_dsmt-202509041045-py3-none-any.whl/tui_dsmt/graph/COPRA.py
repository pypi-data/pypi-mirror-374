import random

import networkx as nx

from .html import graph_to_html
from .. import color_primary, color_error
from ..jpanim import JupyterAnimation


class COPRA(JupyterAnimation):
    def __init__(self, graph: nx.Graph, pos: dict = None, v: int = 3):
        self._graph: nx.Graph = graph
        self._layout: dict = pos or nx.spring_layout(graph)
        self.v: int = v

        html, css = graph_to_html(graph, self._layout,
                                  display_height='26rem', node_width='10rem', node_height='6rem')
        frames = self._alg()

        super().__init__(html, frames, css)

    def _alg(self) -> dict[str, dict]:
        random.seed(5)
        frames = {}

        # initialization
        frames['Graph'] = {
            **{
                f'name_{n}': n
                for n in self._graph.nodes
            },
            **{
                f'node_{n}': self._node_style(n)
                for n in self._graph.nodes
            },
            **{
                f'edge_{source}_{target}': {
                    'backgroundColor': '#eaeaea'
                }
                for source in self._graph.nodes
                for target in self._graph.nodes
            }
        }

        # labels
        labels: dict[str, dict[str, float]] = {
            n: {n: 1.}
            for n in self._graph.nodes
        }

        frames['Initiale Labels'] = {
            **{
                f'name_{n}': f'{n}<br>{self._label_set_str(n, labels)}'
                for n in self._graph.nodes
            }
        }

        # iterations
        for round in range(1, 50):
            old_labels: dict[str, dict[str, float]] = {
                node: {
                    label: value
                    for label, value in label_values.items()
                }
                for node, label_values in labels.items()
            }

            nodes = list(self._graph.nodes)
            random.shuffle(nodes)

            for node in nodes:
                neighbors = tuple(self._graph.neighbors(node))

                # frames[f'Iteration {round}, Knoten {node}: Nachbarn'] = {
                #     **{
                #         f'node_{n}': {
                #             'backgroundColor': self._node_color(n, node, neighbors)
                #         }
                #         for n in self._graph.nodes
                #     }
                # }

                all_neighbor_labels: dict[str, list[float]] = {}
                for neighbor in neighbors:
                    for label, value in labels[neighbor].items():
                        if label not in all_neighbor_labels:
                            all_neighbor_labels[label] = [value]
                        else:
                            all_neighbor_labels[label].append(value)

                labels[node] = {
                    label: sum(values) / len(neighbors)
                    for label, values in all_neighbor_labels.items()
                }

                frames[f'Iteration {round}, Knoten {node}: Labelmenge der Nachbarn'] = {
                    **{
                        f'name_{n}': f'{n}<br>{self._label_set_str(n, labels)}'
                        for n in self._graph.nodes
                    },
                    **{
                        f'node_{n}': self._node_style(n, node, neighbors)
                        for n in self._graph.nodes
                    }
                }

                if any(value >= 1 / self.v for value in labels[node].values()):
                    filtered_labels = {
                        label: value
                        for label, value in labels[node].items()
                        if value >= 1 / self.v
                    }
                    labels[node] = {
                        label: value / sum(filtered_labels.values())
                        for label, value in filtered_labels.items()
                    }

                    frames[f'Iteration {round}, Knoten {node}: Gefilterte Labels'] = {
                        **{
                            f'name_{n}': f'{n}<br>{self._label_set_str(n, labels)}'
                            for n in self._graph.nodes
                        },
                        **{
                            f'node_{n}': self._node_style(n, node)
                            for n in self._graph.nodes
                        }
                    }

                else:
                    max_value = max(labels[node].values())
                    labels[node] = {
                        random.choice([
                            k
                            for k in labels[node]
                            if labels[node][k] == max_value
                        ]): 1.
                    }

                    frames[f'Iteration {round}, Knoten {node}: Zufälliges Label mit Wert {max_value}'] = {
                        **{
                            f'name_{n}': f'{n}<br>{self._label_set_str(n, labels)}'
                            for n in self._graph.nodes
                        },
                        **{
                            f'node_{n}': self._node_style(n, node)
                            for n in self._graph.nodes
                        }
                    }

            if all((
                           len(old_labels[node]) == len(labels[node])
                           and all(key in labels[node] for key in old_labels[node])
                           and all(abs(labels[node][key] - old_labels[node][key]) < 1e-10 for key in old_labels[node])
                   ) for node in labels):
                break

        # end
        frames[f'Ende des Algorithmus'] = {
            **{
               f'node_{n}': self._node_style(n)
               for n in self._graph.nodes
            }
        }

        return frames

    @staticmethod
    def _label_set_str(n: str, all_labels: dict[str, dict[str, float]]):
        labels = list(all_labels[n].items())
        sorted_labels = sorted(labels, key=lambda l: (-l[1], l[0]))
        sorted_labels_str = ', '.join(f'({a},{b:.02})' for a, b in sorted_labels)
        return f'{{{sorted_labels_str}}}'

    @staticmethod
    def _node_style(n, current=None, neighbors=()):
        if n == current:
            return {
                'backgroundColor': f'rgb({color_error})',
                'color': 'whitesmoke'
            }
        elif n in neighbors:
            return {
                'backgroundColor': f'rgb({color_primary})',
                'color': 'whitesmoke'
            }
        else:
            return {
                'backgroundColor': '#eaeaea',
                'color': 'black'
            }
