import base64
import io
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import jinja2
import matplotlib.pyplot as plt
import pdfkit
from IPython.display import HTML, display

from .PathValidator import PathValidator


class OutputGenerator:
    """
    This class provides methods to create PDF and HTML files from a plot with the LOGS-PY style.

    """

    def __init__(self, template_folder: str, template_name: str):
        """Initialization

        :param template_folder: Path to the folder containing the template files.
        """

        self.__template_folder = PathValidator.validate_path(template_folder)
        self.__template_name = template_name
        self.__template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.__template_folder)
        )

    def create_pdf(self, path: str, pdf_name: str, plot: plt.Figure):
        """Creates a PDF file from a plot with the LOGS-PY Style.

        :param path:Path where the PDF should be saved.
        :param pdf_name: Name of the PDF file.
        :param plot: Plot that should be saved as PDF.
        """

        try:
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            print(f"Error creating directory: {e}")
            return

        # Set up Jinja2 for template rendering
        template = self.__template_env.get_template(self.__template_name)

        # Create tmpfile for HTML and PDF
        tmp_dir_name = tempfile.mkdtemp()

        # Save the plot as an image
        pdf_title = plot.axes[0].get_title() if plot.axes else ""
        pdf_title = pdf_title.replace("\n", "<br>")
        plot.axes[0].set_title("")
        plot_image_path = os.path.join(tmp_dir_name, "plot.png")
        plot.savefig(plot_image_path, dpi=100, bbox_inches="tight")
        plt.show()
        plt.close(plot)
        plot_image_path_obj = Path(plot_image_path).resolve()
        pdf_plot_url = plot_image_path_obj.as_uri()
        logo_path = os.path.join(self.__template_folder, "Logs_py_Logo_white.png")
        plot_logo_path_obj = Path(logo_path).resolve()
        pdf_logo_url = plot_logo_path_obj.as_uri()

        # Render the template to an HTML file
        temp_html_path = os.path.join(tmp_dir_name, "temp_report.html")
        with open(temp_html_path, "w") as bf:
            bf.write(
                template.render(
                    date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    pdf_title=pdf_title,
                    pdf_plot=pdf_plot_url,
                    logo=pdf_logo_url,
                )
            )

        # Convert the HTML to PDF
        pdf_path = os.path.join(path, pdf_name + ".pdf")
        options = {
            "enable-local-file-access": True,
            "page-size": "A4",
            "margin-top": "0in",
            "margin-right": "0in",
            "margin-bottom": "0in",
            "margin-left": "0in",
            "encoding": "UTF-8",
            "no-outline": None,  # Removes the outline (border) around the PDF content
            "disable-smart-shrinking": None,  # Disables the feature that shrinks content to fit the page
        }

        pdfkit.from_file(temp_html_path, pdf_path, options=options)
        link = f'<a href="{pdf_path}" target="_blank">Open the folder {pdf_path}</a>'
        display(HTML(link))
        shutil.rmtree(tmp_dir_name)

    def create_html(self, path: str, html_name: str, plot: plt.Figure):
        """Creates a HTML file from a plot with the LOGS-PY Style.

        :param path:Path where the HTML should be saved.
        :param plot: Plot that should be saved as HTML.
        """

        try:
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            print(f"Error creating directory: {e}")
            return

        # Set up Jinja2 for template rendering
        template = self.__template_env.get_template(self.__template_name)

        # Save the plot as an image and convert it to base64
        pdf_title = plot.axes[0].get_title() if plot.axes else ""
        pdf_title = pdf_title.replace("\n", "")
        plot.axes[0].set_title("")
        plot_buffer = io.BytesIO()
        plot.savefig(plot_buffer, format="png", dpi=100, bbox_inches="tight")
        plot_buffer.seek(0)
        plot_base64 = base64.b64encode(plot_buffer.read()).decode("utf-8")
        plot_buffer.close()
        plt.close(plot)

        logo_path = os.path.join(self.__template_folder, "Logs_py_Logo_white.png")

        with open(logo_path, "rb") as image_file:
            # Encode the image in base64
            encoded_logo = base64.b64encode(image_file.read()).decode("utf-8")

        # Render the template to an HTML file
        html_path = os.path.join(path, html_name + ".html")
        with open(html_path, "w") as bf:
            bf.write(
                template.render(
                    date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    pdf_title=pdf_title,
                    pdf_plot=f"data:image/png;base64,{plot_base64}",
                    logo=f"data:image/png;base64,{encoded_logo}",
                )
            )

        # link = f'<a href="{html_path}" target="_blank">Open the folder {html_path}</a>'
        # display(HTML(link))
