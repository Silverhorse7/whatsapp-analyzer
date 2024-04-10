import re
import pandas as pd
from collections import defaultdict
from datetime import datetime

from pywebio.input import *
from pywebio.output import *
from pywebio.session import *
from pywebio.pin import *
from pywebio import start_server
from pyg2plot import Plot
import plotly.express as px


class Analyzer:

    def __init__(self):
        # self.file_path = file_path
        self.frequency_days = defaultdict(int)
        self.frequency_month = defaultdict(int)
        self.frequency_year = defaultdict(int)
        self.first_date = None
        self.person_frequency = defaultdict(int)
        self.frequency_day_month_year = defaultdict(int)

    def analyze(self, file):
        content = file['content']
        if isinstance(content, bytes):
            content = content.decode('utf-8')  # decode bytes to string
        lines = content.split('\n')
        for i in range(0, len(lines)):
            line = lines[i]

            if len(line) == 0 or line[0] != '[':
                continue

            date_time = line.split(',')[0].split('[')[1]
            DAY = date_time.split('/')[0]
            MONTH = date_time.split('/')[1]
            YEAR = date_time.split('/')[2].split(',')[0]
            person = re.findall(r'\](.*?):', line)[0]

            self.frequency_days[YEAR + '/' + DAY] += 1
            self.frequency_month[YEAR + '/' + MONTH] += 1
            self.frequency_year[YEAR] += 1
            self.person_frequency[person] += 1
            self.frequency_day_month_year[YEAR + '-' + MONTH + '-' + DAY] += 1

            if i == 0:
                self.first_date = date_time

        return self.frequency_days, self.frequency_month, self.frequency_year, self.first_date, self.person_frequency, self.frequency_day_month_year


def days_plot(frequency_month):

    df = pd.DataFrame(frequency_month.items(), columns=['date', 'frequency'])
    
    print(df)

    fig = px.line(df, x='date', y='frequency', title='Messages Frequency by Date')

    html = fig.to_html(include_plotlyjs="require", full_html=False)
    
    return html

def year_plot(frequency_year):

    data = []

    for year, freq in frequency_year.items():
        data.append({"year": year, "frequency": freq})

    pie = Plot("Pie")

    pie.set_options({
        "appendPadding": 32,
        "data": data,
        "angleField": "frequency",
        "colorField": "year",
        "radius": 0.8,
        "label": {
            "type": "outer",
        },
        "interactions": [{"type": "element-active"}],
    })

    return pie


def main():
    analyser = Analyzer()

    file = file_upload("Upload your WhatsApp chat file", accept=".txt")

    if file:
        file_path = file['content']
        frequency_days, frequency_month, frequency_year, first_date, person_frequency, frequency_day_month_year = analyser.analyze(
            file)
        put_markdown(f"First message was sent on {first_date}")

        for e in person_frequency:
            put_markdown(f"{e} sent {person_frequency[e]} messages")

        put_html(days_plot(frequency_day_month_year))
        
        put_html(year_plot(frequency_year).render_notebook())

    else:
        put_markdown('No file was uploaded')


if __name__ == '__main__':
    start_server(main, port=8080, debug=True)
    # main()
