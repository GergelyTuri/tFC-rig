from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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
        story.append(Paragraph("Mouse ID: {}".format(mouse_id), styles['Heading4']))
        for param in get_trial_settings(events):
            story.append(Paragraph(param, styles['Normal']))
        
        story.append(Spacer(1, 12))

        for trial, count in count_licks(events).items():
            story.append(Paragraph("Trial: {}, Number of licks: {}".format(trial, count), styles['Normal']))
        story.append(Spacer(1, 6))

    # Build the PDF
    doc.build(story)

    print(f"PDF report saved to {pdf_file}")
