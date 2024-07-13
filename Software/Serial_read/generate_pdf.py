from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import FigureCanvasPdf
import io

def simple_lick_plot(df):
    """
    Plot for lick rate over time.
    TODO: Replace with better plot from Analysis and sync with live plot

    """
    df['absolute_time'] = pd.to_datetime(df['absolute_time'], format='%Y-%m-%d_%H-%M-%S.%f')
    df['elapsed_time'] = (df['absolute_time'] - df['absolute_time'].min()).dt.total_seconds()

    df['lick'] = df['message'].apply(lambda x: 'Lick' in x)
    lick_df = df[df['lick']]

    lick_df.set_index(pd.to_timedelta(lick_df['elapsed_time'], unit='s'), inplace=True)
    lick_df

    lick_rate = lick_df['lick'].resample('S').sum()

    lick_rate

    fig = plt.figure(figsize=(10, 5))
    plt.plot(lick_rate.index, lick_rate.values, marker='.', linestyle='-')
    plt.xlabel('Time (s)')
    plt.ylabel('Lick Rate (licks/s)')
    plt.title('Lick Rate Over Time')
    plt.grid(True)
    return fig

def count_licks(events):
    lick_counts = {}
    trial = 0
    for event in events:
        message = event['message']
        if "Trial has started" in message:
            trial += 1
            lick_counts[trial] = 0
        elif "Lick" in message:
            lick_counts[trial] += 1
    return lick_counts

def get_trial_settings(events):
    out = []
    for event in events:
        message = event['message']
        if ("CS-" in message) or ("trialTypes" in message):
            out.append(message.rsplit(':', 1)[-1])
    return out


def generate_pdf(file_path, header, data_list):
    pdf_file = file_path.with_suffix('.pdf')
    doc = SimpleDocTemplate(str(pdf_file), pagesize=letter)
    styles = getSampleStyleSheet()

    # Build content
    story = []

    # Title and header information
    title = Paragraph("Session Report", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Start Time: {}".format(header['Start_time']), styles['Bullet']))
    story.append(Paragraph("Primary Port: {}".format(header['primary_port']), styles['Bullet']))
    if header['secondary_port']:
        story.append(Paragraph("Secondary Port: {}".format(header['secondary_port']), styles['Bullet']))
    if 'camera1' in header:
        story.append(Paragraph("Primary Camera: {}".format(header['camera1']), styles['Bullet']))
    if 'camera2' in header:
        story.append(Paragraph("Secondary Camera: {}".format(header['camera2']), styles['Bullet']))

    story.append(Spacer(1, 12))

    # Mouse Data
    story.append(Paragraph("Data:", styles['Heading2']))
    story.append(Spacer(1, 12))

    for mouse_id, events in data_list.items():
        print('events: ', events)
        story.append(Paragraph("Mouse ID: {}".format(mouse_id), styles['Heading4']))
        for param in get_trial_settings(events):
            story.append(Paragraph(param, styles['Normal']))
        
        story.append(Spacer(1, 12))

        for trial, count in count_licks(events).items():
            story.append(Paragraph("Trial: {}, Number of licks: {}".format(trial, count), styles['Normal']))
        story.append(Spacer(1, 6))
    
        df = pd.DataFrame(events)
        fig = simple_lick_plot(df)

        img_data = io.BytesIO()
        fig.savefig(img_data, format='png')
        img_data.seek(0)
        img_width = 550
        img_height = 300

        # Add image to PDF
        story.append(Image(img_data, width=img_width, height=img_height))
        plt.close(fig)  # Close the figure to free up memory


    # Build the PDF
    doc.build(story)

    print(f"PDF report saved to {pdf_file}")
