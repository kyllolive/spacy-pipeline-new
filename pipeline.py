import re
import csv
import spacy
from spacy_layout import spaCyLayout
from gliner import GLiNER
from pdf_helper import extract_first_page, get_pdf_files, extract_original_filename
from extract import process_document


class DocumentProcessor:
    def __init__(self, batch_type, pdf_dir, output_file="extracted_data.csv"):
        self.batch_type = batch_type
        self.pdf_dir = pdf_dir
        self.output_file = output_file
        self.csv_headers = None
        self.csv_file = None
        self.writer = None

        # Initialize GLiNER model
        self.model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")

        # Initialize spaCy model
        self.nlp = spacy.load("en_core_web_trf")

        # Initialize spaCy Layout model
        self.layout = spaCyLayout(self.nlp)

        # Process all PDFs
        self.process_pdfs()

        # Close CSV file if still open
        if self.csv_file and not self.csv_file.closed:
            self.csv_file.close()
            print(f"Results written to {self.output_file}")

    def process_pdfs(self):
        pdf_files = get_pdf_files(self.pdf_dir)

        if not pdf_files:
            print("No PDF files found in the directory")
            return

        for pdf_file in pdf_files:
            first_page = extract_first_page(pdf_file)
            original_filename = extract_original_filename(pdf_file)

            result = self.layout(first_page)
            text = result.text
            print(f"TEXT: {text}")

            result = process_document(
                text,
                self.model,
                original_filename,
                self.batch_type,
            )

            print(f"Extracted entities: {result}")

            # Write the result to CSV immediately
            self.write_result_to_csv(result)

    def write_result_to_csv(self, result):
        if not result:
            return

        # If this is the first result, set up the CSV file and headers
        if self.csv_file is None:
            self.csv_headers = list(result.keys())
            self.csv_file = open(self.output_file, "w", newline="")
            self.writer = csv.DictWriter(self.csv_file, fieldnames=self.csv_headers)
            self.writer.writeheader()

        # Write the current result
        self.writer.writerow(result)

        # Flush to ensure data is written to disk
        self.csv_file.flush()


if __name__ == "__main__":
    processor = DocumentProcessor(batch_type="ORDINANCE", pdf_dir="sample-dataset")
