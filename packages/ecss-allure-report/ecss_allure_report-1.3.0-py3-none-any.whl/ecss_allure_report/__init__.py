import os
from pathlib import Path

from dotenv import load_dotenv

from ecss_chat_client import Client

from .diagram import create_diagram
from .summary import generate_summary

load_dotenv()

DIAGRAM_NAME = f'{os.getenv("DIAGRAM_NAME", "chart")}.png'


def send_report(proto='https', port='3443',  ssl_verify: bool = False):
    current_dir = Path.cwd()
    report_dir = os.getenv('ALLURE_REPORT', 'allure_report')
    output_path = current_dir / report_dir / os.getenv('REPORT_DIAGRAM_NAME')
    create_diagram()
    client = Client(
        server=os.getenv('REPORT_ELPH_SERVER'),
        username=os.getenv('REPORT_ELPH_USER'),
        password=os.getenv('REPORT_ELPH_PASSWORD'),
        proto=os.getenv('REPORT_ELPH_PROTOCOL'),
        port=os.getenv('REPORT_ELPH_PORT'),
        verify=ssl_verify,
    )

    summary = generate_summary(
        project_name=os.getenv('REPORT_PROJECT_NAME', 'elph-chat-server'),
    )

    client.rooms.upload_file(
        room_id=os.getenv('REPORT_ELPH_ROOM_ID'),
        file_path=str(output_path),
        text=summary,
    )


if __name__ == '__main__':
    send_report()


__all__ = ['send_report']
