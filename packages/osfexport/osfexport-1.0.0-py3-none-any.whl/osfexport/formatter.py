import datetime
import os
import io
import html

import PIL
from fpdf import FPDF, Align
from fpdf.fonts import FontFace
from fpdf.image_parsing import get_img_info
from mistletoe import markdown, HTMLRenderer
import qrcode
import urllib


class HTMLImageSizeCapRenderer(HTMLRenderer):
    """Custom Markdown to HTML renderer which caps image size."""

    max_width = 300
    max_height = 300

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def render_image(self, token):
        """Render an image with a specified size."""

        template = '<img src="{}" alt="{}"{}{}{} />'

        # Cap image size if needed so they can fit on the page
        try:
            img_info = get_img_info(token.src)
        except (urllib.error.HTTPError, PIL.UnidentifiedImageError):
            return f'<a href="{html.escape(token.src)}">{token.src}</a>'

        if img_info['w'] > HTMLImageSizeCapRenderer.max_width:
            new_width = HTMLImageSizeCapRenderer.max_width
        else:
            new_width = img_info['w']
        width = ' width="{}"'.format(html.escape(str(new_width)))

        if img_info['h'] > HTMLImageSizeCapRenderer.max_height:
            new_height = HTMLImageSizeCapRenderer.max_height
        else:
            new_height = img_info['h']
        height = ' height="{}"'.format(html.escape(str(new_height)))

        if token.title:
            title = ' title="{}"'.format(html.escape(token.title))
        else:
            title = ""
        return template.format(token.src, self.render_to_plain(token), title, width, height)


class PDF(FPDF):
    """Custom PDF class to implement extra customisation.
    Attributes:
        date_printed: datetime
            Date and time when the project was exported.
        url: str
            Current URL to include in QR codes.
        parent_url: str
            URL of root project to use in component sections.
        parent_title: str
            Title of root project to use in component sections.
    """

    # Global styles for PDF
    BLUE = (173, 216, 230)
    HEADINGS_STYLE = FontFace(emphasis="BOLD", fill_color=BLUE)
    FONT_SIZES = {
        'h1': 16,  # Project titles
        'h2': 12,  # Section titles
        'h3': 10,  # Section sub-titles
        'h4': 9,  # Body
        'h5': 8  # Footer
    }
    LINK_STYLE = FontFace(emphasis="UNDERLINE", size_pt=FONT_SIZES['h5'])
    LINE_PADDING = -1  # Gaps between lines
    TITLE_CELL_WIDTH = 150  # Shorter width to avoid QR code clipping
    CELL_WIDTH = 180  # Width of text cells

    def __init__(self, url=''):
        super().__init__()
        self.date_printed = datetime.datetime.now(
            datetime.timezone.utc
        )
        self.url = url
        # Setup unicode font for use. Can have 4 styles
        self.font = 'dejavu-sans'
        self.add_font(self.font, style="", fname=os.path.join(
            os.path.dirname(__file__), 'font', 'DejaVuSans.ttf'))
        self.add_font(self.font, style="b", fname=os.path.join(
            os.path.dirname(__file__), 'font', 'DejaVuSans-Bold.ttf'))
        self.add_font(self.font, style="i", fname=os.path.join(
            os.path.dirname(__file__), 'font', 'DejaVuSans-Oblique.ttf'))
        self.add_font(self.font, style="bi", fname=os.path.join(
            os.path.dirname(__file__), 'font', 'DejaVuSans-BoldOblique.ttf'))

    def generate_qr_code(self):
        qr = qrcode.make(self.url)
        img_byte_arr = io.BytesIO()
        qr.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr

    def footer(self):
        self.set_y(-15)
        self.set_x(-30)
        self.set_font(self.font, size=PDF.FONT_SIZES['h5'])
        self.cell(0, 10, f"Page: {self.page_no()}", align="C")
        self.set_x(10)
        timestamp = self.date_printed.strftime(
            '%Y-%m-%d %H:%M:%S %Z'
        )
        self.cell(0, 10, f"Exported: {timestamp}", align="L")
        self.set_x(10)
        self.set_y(-15)
        qr_img = self.generate_qr_code()
        self.image(qr_img, w=15, h=15, x=Align.C)

    def _write_list_section(self, key, fielddict):
        """Handle writing fields of different types inplace to a PDF.
        Possible types are lists, strings or dictionaries.

        Parameters
        -----------
            key: str
                Name of the field to write.
            fielddict: dict
                Dictionary containing the field data.
        """

        # Set nicer display names for certain PDF fields
        pdf_display_names = {
            'identifiers': 'DOI',
            'funders': 'Support/Funding Information'
        }
        if key in pdf_display_names:
            field_name = pdf_display_names[key]
        else:
            field_name = key.replace('_', ' ').title()

        if isinstance(fielddict[key], list):
            # Create separate paragraphs for more complex attributes
            self.write(0, '\n')
            self.set_font(self.font, size=PDF.FONT_SIZES['h3'])
            self.multi_cell(
                w=PDF.CELL_WIDTH, h=None,
                text=f'**{field_name}**\n',
                align='L', markdown=True, padding=PDF.LINE_PADDING
            )
            self.set_font(self.font, size=PDF.FONT_SIZES['h4'])
            if len(fielddict[key]) > 0:
                for idx, item in enumerate(fielddict[key]):
                    for subkey in item.keys():
                        if subkey in pdf_display_names:
                            field_name = pdf_display_names[subkey]
                        else:
                            field_name = subkey.replace('_', ' ').title()

                        self.multi_cell(
                            w=PDF.CELL_WIDTH, h=None,
                            text=f'**{field_name}:** {item[subkey]}\n',
                            align='L', markdown=True, padding=PDF.LINE_PADDING
                        )
                    if idx < len(fielddict[key])-1:
                        self.ln()
                        self.set_x(9)
            else:
                self.multi_cell(
                    w=PDF.CELL_WIDTH, h=None,
                    text='NA',
                    align='L', markdown=True, padding=PDF.LINE_PADDING
                )
        else:
            # Simple key-value attributes can go on one-line
            self.multi_cell(
                w=PDF.CELL_WIDTH,
                h=None,
                text=f'**{field_name}:** {fielddict[key]}\n',
                align='L',
                markdown=True,
                padding=PDF.LINE_PADDING
            )

    def _write_project_body(self, project):
        """Write inplace the body of a project to the PDF.

        Parameters
        -----------
            project: dict
                Dictionary containing project data to write.
            parent_title: str
                Title of the parent project.
        """

        self.add_page()
        self.set_font(self.font, size=PDF.FONT_SIZES['h4'])
        wikis = project['wikis']

        # Start with parent, project headers and links
        parent = project['parent']
        if parent:
            self.set_font(self.font, size=PDF.FONT_SIZES['h1'], style='B')
            self.write(h=0, text=f'Parent: {parent[0]}\n')
            self.set_font(self.font, size=PDF.FONT_SIZES['h3'], style='U')
            self.write(h=0, text=f'{parent[1]}\n', link=parent[1])
            self.ln(h=5)

        # Pop URL field to avoid printing it out in Metadata section
        url = project['metadata'].pop('url', '')
        self.url = url  # Set current URL to use in QR codes
        qr_img = self.generate_qr_code()
        self.image(qr_img, w=30, x=180, y=5)
        title = project['metadata']['title']
        self.set_font(self.font, size=PDF.FONT_SIZES['h1'], style='B')
        self.write(
            h=0,
            text=f"{'Component: ' if parent else ''}{title} \n"
        )
        self.set_font(self.font, size=PDF.FONT_SIZES['h3'], style='U')
        self.write(h=0, text=f'{url}\n', link=url)
        self.ln(h=5)

        # Write title for metadata section, then actual fields
        self.set_font(self.font, size=PDF.FONT_SIZES['h2'], style='B')
        self.multi_cell(
            w=PDF.CELL_WIDTH, h=None, text='1. Project Metadata\n',
            align='L', padding=PDF.LINE_PADDING)
        self.set_font(self.font, size=PDF.FONT_SIZES['h4'])
        for key in project['metadata']:
            self._write_list_section(key, project['metadata'])
        self.ln(h=7)

        # Write Contributors in table
        self.set_x(8)
        self.set_font(self.font, size=PDF.FONT_SIZES['h2'], style='B')
        self.multi_cell(w=PDF.CELL_WIDTH, h=None, text='2. Contributors\n', align='L')
        self.set_font(self.font, size=PDF.FONT_SIZES['h4'])
        with self.table(
            headings_style=PDF.HEADINGS_STYLE,
            col_widths=(0.8, 0.5, 1.2), align="LEFT"
        ) as table:
            row = table.row()
            row.cell('Name')
            row.cell('Bibliographic?')
            row.cell('Profile Link')
            self.set_font(self.font, size=PDF.FONT_SIZES['h5'])
            for data_row in project['contributors']:
                row = table.row()
                for idx, datum in enumerate(data_row):
                    if datum is True:
                        datum = 'Yes'
                    if datum is False:
                        datum = 'No'
                    if idx == 2:
                        row.cell(text=datum, link=datum, style=self.LINK_STYLE)
                    else:
                        row.cell(datum)
        self.ln(h=7)

        # List files stored in storage providers
        # For now only OSF Storage is involved
        self.set_x(8)
        self.set_font(self.font, size=PDF.FONT_SIZES['h2'], style='B')
        self.multi_cell(w=PDF.CELL_WIDTH, h=None, text='3. Files in Main Project\n', align='L')
        self.set_font(self.font, size=PDF.FONT_SIZES['h3'], style='B')
        self.multi_cell(w=PDF.CELL_WIDTH, h=None, text='OSF Storage\n', align='L')
        self.set_font(self.font, size=PDF.FONT_SIZES['h4'])
        if len(project['files']) > 0:
            with self.table(
                headings_style=PDF.HEADINGS_STYLE,
                col_widths=(1, 0.3, 1.2), align="LEFT"
            ) as table:
                self.set_font(self.font, size=PDF.FONT_SIZES['h4'])
                row = table.row()
                row.cell('File Name')
                row.cell('Size (MB)')
                row.cell('Download Link')
                self.set_font(self.font, size=PDF.FONT_SIZES['h5'])
                for data_row in project['files']:
                    row = table.row()
                    for idx, datum in enumerate(data_row):
                        if datum is True:
                            datum = 'Yes'
                        if datum is False or datum is None:
                            datum = 'N/A'
                        if idx == 2:
                            row.cell(text=datum, link=datum, style=self.LINK_STYLE)
                        else:
                            row.cell(datum)
        else:
            self.write(0, '\n')
            self.multi_cell(
                w=PDF.CELL_WIDTH, h=None, text='No files found for this project.\n', align='L'
            )
            self.write(0, '\n')
        self.ln(h=10)

        # Write wikis separately to more easily handle Markdown parsing
        self._write_wiki_pages(
            wikis, parent=parent, title=project['metadata']['title']
        )

    def _write_wiki_pages(self, wikis, title, parent=None):
        """Write inplace the wiki pages to the PDF.

        Parameters
        -----------
            wikis: dict
                Dictionary containing wiki data to write.
        """

        for i, wiki in enumerate(wikis.keys()):
            self.add_page()
            if i == 0:
                self.set_font(self.font, size=PDF.FONT_SIZES['h2'], style='B')
                title_template = '4. Wiki ({}{}{})'
                if parent:
                    header = title_template.format(f'Parent: {parent[0]}', ' | ', title)
                else:
                    header = title_template.format('', '', title)
                self.multi_cell(
                    w=PDF.CELL_WIDTH, h=None, text=f'{header}\n',
                    align='L')
                self.ln()
            self.set_font(self.font, size=PDF.FONT_SIZES['h2'], style='B')
            self.multi_cell(w=PDF.CELL_WIDTH, h=None, text=f'{wiki}\n')
            self.set_font(self.font, size=PDF.FONT_SIZES['h4'])
            html = markdown(
                wikis[wiki],
                renderer=HTMLImageSizeCapRenderer
            )
            self.write_html(html)


def explore_project_tree(project, projects, pdf=None):
    """Recursively find child projects and write them to a PDF.

    Parameters
    -----------
        project: dict
            Dictionary containing project data to write.
        projects: list[dict]
            List of all projects to explore.
        pdf: PDF
            PDF object to write to. If None, a new PDF will be created.
        parent_title: str
            Title of the parent project.

    Returns
    -----------
        pdf: PDF
            PDF object with the project and its children written to it."""

    # Start with no PDF at root projects
    if not pdf:
        pdf = PDF()

    pdf.set_line_width(0.05)
    pdf.set_left_margin(10)
    pdf.set_right_margin(30)

    # Add current project to PDF
    pdf._write_project_body(project)

    # Do children last so that they come at end of the PDF
    children = project['children']
    for child_id in children:
        child_project = next(
            (p for p in projects if p['metadata']['id'] == child_id), None
        )
        if child_project:
            pdf = explore_project_tree(
                child_project, projects, pdf=pdf
            )

    return pdf


def write_pdf(projects, root_idx, folder=''):
    """Make PDF for each project.

    Parameters
    ------------
        projects: dict[str, str|tuple]
            Projects found to export into the PDF.
        root_idx: int
            Position of root node (no parent) in the projects list.
            This is used for accessing root projects without sorting the list.
        folder: str
            The path to the folder to output the project PDFs in.
            Default is the current working directory.

    Returns
    ------------
        pdfs: list
            List of created PDF files.
    """

    curr_project = projects[root_idx]
    title = curr_project['metadata']['title']
    pdf = explore_project_tree(curr_project, projects)

    # Remove spaces in file name for better behaviour on Linux
    # Add timestamp to allow distinguishing between PDFs at a glance
    timestamp = pdf.date_printed.strftime(
        '%Y-%m-%d %H-%M-%S %Z'
    ).replace(' ', '-')
    filename = f'{title.replace(' ', '-')}-{timestamp}.pdf'

    if folder:
        if not os.path.exists(folder):
            os.mkdir(folder)
        path = os.path.join(os.getcwd(), folder, filename)
    else:
        path = os.path.join(os.getcwd(), filename)
    pdf.output(path)

    return pdf, path
