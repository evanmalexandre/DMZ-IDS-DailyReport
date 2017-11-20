import matplotlib
matplotlib.use('Agg')
import pandas as pd, MySQLdb, matplotlib.pyplot as plt, numpy as np
from matplotlib.backends.backend_pdf import PdfPages


# Define MySQL queries
queries = {'counts': """SELECT calendar.datefield AS date,
                          IFNULL(COUNT(event.signature),0) AS event_count
                        FROM event RIGHT JOIN calendar 
                          ON (date(event.timestamp) = calendar.datefield)
                        WHERE (calendar.datefield 
                          BETWEEN DATE_SUB(NOW(), INTERVAL 1 WEEK) and NOW())
                        GROUP BY date
                        ORDER BY date DESC""",


           'noise': """SELECT signature,
                           COUNT(*) as cnt
                       FROM event
                       WHERE timestamp > DATE_SUB(NOW(), INTERVAL 1 DAY)
                       GROUP BY signature
                       ORDER BY cnt DESC""",


           'priority': """SELECT signature,
                                 priority
                          FROM event
                          WHERE timestamp > DATE_SUB(NOW(), INTERVAL 1 DAY)
                          ORDER BY priority DESC
                          LIMIT 10"""}


# Gather MySQL data into pandas dataframes
def query_to_df(query):
    conn = MySQLdb.connect(host="localhost", user="root", db="securityonion_db")
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    df = pd.DataFrame([i for i in rows])
    return df


counts_df = query_to_df(queries['counts'])
noise_df = query_to_df(queries['noise'])
priority_df = query_to_df(queries['priority'])


# Parse dataframes before graphing
def parse_df(df):
    df_stats = {}
    df_stats['x'] = df[0]
    df_stats['y'] = df[1]
    df_stats['yrange'] = np.arange(len(df_stats['x']))
    return df_stats


counts_stats = parse_df(counts_df)
priority_stats = parse_df(priority_df)
noise_stats = parse_df(noise_df)

# Conditional coloring functions
def avg_conditional_color(i, avg, std):
    if i >= avg + 1.5 * std:
        color = 'r'
    elif i >= avg + .75 * std:
        color = 'y'
    else:
        color = 'g'
    return color


def gen_conditional_colors(y):
    colors = []
    avg = y.mean()
    std = y.std()
    for i in y:
        colors.append(avg_conditional_color(i, avg, std))
    return colors


def gen_colors_first_item_only(y):
    colors = []
    avg = y.mean()
    std = y.std()
    colors.append(avg_conditional_color(y[0], avg, std))
    for i in y[1:]:
            colors.append('b')
    return colors


def gen_priority_colors(priorities):
    colors = []
    for priority in priorities:
        if priority >= 8:
            colors.append('r')
        elif priority >= 5:
            colors.append('y')
        else:
            colors.append('g')
    return colors


# Generate coloring schemes
counts_colors = gen_colors_first_item_only(counts_stats['y'])
priority_colors = gen_priority_colors(priority_stats['y'])
noise_colors = gen_conditional_colors(noise_stats['y'])


# Plotting charts
def plotGraph(x, y, y_pos, x_label, title, colors):
    fig = plt.figure()
    ax = plt.subplot()
    ax.barh(y_pos, y, align='center',
            color=colors, ecolor='black')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(x)
    ax.invert_yaxis()
    ax.set_xlabel(x_label)
    ax.set_title(title)
    plt.tight_layout()
    return fig


counts_chart = plotGraph(counts_stats['x'],
                        counts_stats['y'],
                        counts_stats['yrange'],
                        'Daily Event Counts',
                        'Event Level Comparison',
                        counts_colors)

priority_chart = plotGraph(priority_stats['x'],
                          priority_stats['y'],
                          priority_stats['yrange'],
                          'Priority by Signature',
                          'Top 10 Events',
                          priority_colors)

noise_chart = plotGraph(noise_stats['x'],
                       noise_stats['y'],
                       noise_stats['yrange'],
                       'Past 24hrs Noisiest Alerts',
                       'Event Count by Signature',
                       noise_colors)


# Make pdf
pp = PdfPages('/home/monitor/Desktop/Commands/test.pdf')
pp.savefig(counts_chart)
pp.savefig(priority_chart)
pp.savefig(noise_chart)
pp.close()



