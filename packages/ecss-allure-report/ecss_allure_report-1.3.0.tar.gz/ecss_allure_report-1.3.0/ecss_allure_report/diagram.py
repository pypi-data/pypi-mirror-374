import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv()

DIAGRAM_NAME = f'{os.getenv("DIAGRAM_NAME", "chart")}.png'


def create_diagram():
    current_dir = Path.cwd()
    report_dir = os.getenv('ALLURE_REPORT', 'allure_report')
    summary_path = current_dir / report_dir / 'widgets' / 'summary.json'
    output_path = current_dir / report_dir / DIAGRAM_NAME

    with open(summary_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    statistic = data['statistic']

    labels = []
    sizes = []
    colors = []
    explode = []

    color_map = {
        'passed': '#97CC64',
        'failed': '#FD5A3E',
        'broken': '#FBB03B',
        'skipped': '#AAAAAA',
        'unknown': '#A0A0A0',
    }

    for status, count in statistic.items():
        if status != 'total' and count > 0:
            labels.append(status)
            sizes.append(count)
            colors.append(color_map.get(status, '#CCCCCC'))
            explode.append(0.05 if status == 'failed' else 0)

    if not sizes and statistic['total'] > 0:
        labels = ['no data']
        sizes = [statistic['total']]
        colors = ['#E0E0E0']
        explode = [0]

    plt.figure(figsize=(8, 8), tight_layout=True)

    if len(set(statistic.values()) - {0, statistic['total']}) <= 1:
        status = next(
            (s for s in statistic if s != 'total' and statistic[s] > 0),
            'unknown',
        )
        plt.pie([1], colors=[color_map.get(status, '#CCCCCC')],
                shadow=False, startangle=90,
                wedgeprops=dict(width=0.5))
    else:
        plt.pie(sizes, explode=explode, colors=colors,
                shadow=False, startangle=90, labels=None, autopct=None,
                wedgeprops=dict(width=0.5))

    circle = plt.Circle((0, 0), 0.45, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(circle)

    statuses = ['passed', 'failed', 'broken', 'skipped']
    active_statuses = [s for s in statuses if statistic.get(s, 0) > 0]
    total_statuses = len(active_statuses)

    vertical_spacing = 0.4 / (total_statuses + 1)
    start_y = vertical_spacing * (total_statuses - 1) / 2

    for i, status in enumerate(statuses):
        if statistic.get(status, 0) > 0:
            y_pos = start_y - i * vertical_spacing
            plt.text(
                0, y_pos,
                f'{status.capitalize()}: {statistic[status]}',
                ha='center', va='center',
                fontsize=14,
                fontweight='bold',
                color=color_map.get(status, '#000000'),
            )

    plt.axis('off')
    plt.savefig(output_path, bbox_inches='tight', dpi=300, pad_inches=0.1)
    plt.close()


if __name__ == '__main__':
    create_diagram()
