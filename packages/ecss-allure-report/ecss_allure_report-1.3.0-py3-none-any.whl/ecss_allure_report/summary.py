import json
import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def generate_summary(
        project_name: str,
) -> str:
    current_dir = Path.cwd()
    report_dir = os.getenv('ALLURE_REPORT', 'allure_report')
    summary_path = current_dir / report_dir / 'widgets' / 'summary.json'
    with open(summary_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        statistic = data['statistic']
        duration = timedelta(milliseconds=data['time']['duration'])
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted_duration = f'{hours:02d}:{minutes:02d}:{seconds:02d}'

    allure_server = 'http://voip-allure.eltex.loc/'
    proj_link = f'allure-docker-service-ui/projects/{os.getenv("PROJECT_ID")}'

    text = (
        f'Проект: {project_name}\n'
        f'Продолжительность: {formatted_duration}\n'
        f'Всего: {statistic["total"]}\n'
        f'Успешно: {statistic["passed"]}\n'
        f'Пропущено: {statistic["skipped"]}\n'
        f'Провалено: {statistic["failed"]}\n'
        f'Сломано: {statistic["broken"]}\n'
        f'[Report Link]({allure_server}{proj_link})'
    )

    return text


if __name__ == '__main__':
    print(
        generate_summary(
            project_name=str(os.environ.get('REPORTER_PROJECT')),
        ),
    )
