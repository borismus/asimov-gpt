import argparse
from test_pdf import extract_page_image
from test_vision import summarize_inventions_from_image, Invention
from pypdf import PdfReader

parser = argparse.ArgumentParser()
parser.add_argument("--fr", "--from", help="The first page to process.", type=int)
parser.add_argument("--to", help="The last page to process.", type=int)
args = parser.parse_args()

reader = PdfReader("asimov.pdf")
print(f"Loaded PDF with {len(reader.pages)} pages.")


def invention_to_tsv(invention: Invention):
  slug = invention.title.lower().replace(" ", "-")
  separated_fields = [slug, invention.year, invention.title, invention.summary, invention.inventor, invention.location, invention.related, invention.field, invention.description]
  return "\t".join([str(field) for field in separated_fields])

if __name__ == "__main__":
  if args.fr is None or args.to is None:
    raise ValueError("Please provide --from and --to arguments.")
  for page_number in range(args.fr, args.to + 1):
    page_image = extract_page_image(reader, page_number)
    print(f"Extracting image from page {page_number}.")
    inventions = summarize_inventions_from_image(page_image)

    for invention in inventions:
      tsv = invention_to_tsv(invention)
      print(tsv)