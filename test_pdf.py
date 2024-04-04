import base64
from pypdf import PdfReader

def extract_page_image(reader, page_number, out_path=None):
  page = reader.pages[page_number - 1]
  assert len(page.images) == 1, "Expected exactly one image per page."
  for image_file_object in page.images:
    if out_path:
      with open(out_path, "wb") as fp:
        fp.write(image_file_object.data)
    return base64.b64encode(image_file_object.data).decode('utf-8')


if __name__ == '__main__':
  from pypdf import PdfReader
  reader = PdfReader("asimov.pdf")
  extract_page_image(reader, 5, "111_out.jpg")