import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak, Paragraph, Spacer
from reportlab.platypus.flowables import KeepTogether
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.flowables import Flowable

print("NGS CRISPResso2 Report Generation Script started")

def find_png_files(directory):
    png_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.png'):
                png_files.append(os.path.join(root, file))
    return png_files

class HeaderImage(Flowable):
    def __init__(self, doc, img_path, width=None, height=None):
        Flowable.__init__(self)
        self.doc = doc
        self.img_path = img_path
        self.width = width
        self.height = height

    def draw(self):
        img = Image(self.img_path)
        if self.width and self.height:
            img.drawWidth = self.width
            img.drawHeight = self.height
        # Calculate the remaining space on the left and right sides of the canvas
        remaining_space = self.doc.width - img.drawWidth
        # Divide by 2 to center the image
        x = remaining_space / 2
        img.drawOn(self.canv, x, 0)

def generate_report(png_files, output_filename, title, header_image_path):
    doc_left_margin = 0  # Set the left margin to 0
    doc = BaseDocTemplate(output_filename, pagesize=letter, leftMargin=doc_left_margin)
    content = []

    # Add header image with no left margin
    header_img = HeaderImage(doc, header_image_path, width=doc.width, height=doc.topMargin)
    content.append(header_img)

    # Add title and spacing
    styles = getSampleStyleSheet()
    title_text = Paragraph(title, styles['Heading1'])
    content.append(title_text)
    content.append(Spacer(1, 0.5 * inch))

    # Sort the png_files list alphabetically
    png_files = sorted(png_files)

    # Set left margin for content after the header
    content_left_margin = inch / 2

    for png_file in png_files:
        try:
            img = Image(png_file)
            img_width, img_height = img.wrap(0, 0)
            img_ratio = img_width / img_height

            if img_width > 6*inch:
                img_width = 6*inch
                img_height = img_width / img_ratio

            img.drawWidth = img_width
            img.drawHeight = img_height

            img_and_title = KeepTogether([
                Paragraph(os.path.splitext(os.path.basename(png_file))[0], styles['BodyText']),
                Spacer(1, 0.1 * inch),
                img
            ])

            content.append(img_and_title)
            content.append(Spacer(1, 0.25 * inch))

            # Check if there is enough space for the next image
            if doc.height - doc.bottomMargin - doc.topMargin < img_height + 0.25 * inch:
                content.append(PageBreak())

        except Exception as e:
            print(f"Error processing {png_file}: {e}")

    # Create a Frame with the desired margins for the content
    content_frame = Frame(content_left_margin, doc.bottomMargin, doc.width - content_left_margin, doc.height, id='normal')

    # Create a PageTemplate with the Frame
    content_page_template = PageTemplate(id='content', frames=[content_frame])

    # Add the PageTemplate to the BaseDocTemplate instance
    doc.addPageTemplates([content_page_template])

    # Build the report
    doc.build(content)

input_directory = '/Users/chrischao/Desktop/MiSeqResults/extract_ngs_data/'
output_directory = '/Users/chrischao/Desktop/MiSeqResults/generated_ngs_reports/'
header_image_path = '/Users/chrischao/Desktop/MiSeqResults/dna.png'

for subdir, dirs, files in os.walk(input_directory):
    print(f"Processing directory: {subdir}")
    subdir_png_files = find_png_files(subdir)
    if subdir_png_files:
        subdir_name = os.path.basename(subdir)
        output_filename = os.path.join(output_directory, f"{subdir_name}_report.pdf")
        title = f"NGS Report for {subdir_name}"
        generate_report(subdir_png_files, output_filename, title, '/Users/chrischao/Desktop/MiSeqResults/dna.png')
        print(f"Generated NGS Report: {output_filename}")
