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
        self.results = []

        # Initialize GLiNER model
        self.model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")

        # Initialize spaCy model
        self.nlp = spacy.blank("en")

        # Initialize spaCy Layout model
        self.layout = spaCyLayout(self.nlp)

        # Process all PDFs
        self.process_pdfs()

        # Write results to CSV
        self.write_to_csv()

    def process_pdfs(self):
        for pdf_file in get_pdf_files(self.pdf_dir):
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

            # Store the result for CSV output
            self.results.append(result)

            # Set headers based on the first result if not already set
            if self.csv_headers is None and result:
                self.csv_headers = list(result.keys())

    def write_to_csv(self):
        if not self.results:
            print("No results to write to CSV")
            return

        with open(self.output_file, "w", newline="") as csvfile:
            writer = None

            # Initialize writer with headers
            if self.csv_headers:
                writer = csv.DictWriter(csvfile, fieldnames=self.csv_headers)
                writer.writeheader()
            else:
                # Fallback if no headers were found
                writer = csv.writer(csvfile)

            # Write each result to the CSV
            for result in self.results:
                if writer.__class__ == csv.DictWriter:
                    writer.writerow(result)
                else:
                    writer.writerow(result.values())

        print(f"Results written to {self.output_file}")


if __name__ == "__main__":
    processor = DocumentProcessor(batch_type="ORDINANCE", pdf_dir="sample-dataset")
