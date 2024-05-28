from pydantic import BaseModel, ConfigDict
import csv


class Invention(BaseModel):
  model_config = ConfigDict(strict=True)
  title: str
  year: str
  summary: str
  inventor: str
  location: str
  field: str
  related: str
  description: str = None
  id: str = None

  def year_number(self):
    if self.year.endswith("BCE"):
      return -int(self.year[:-3])

    return int(self.year)


def load_inventions(tsv_path) -> list[Invention]:
  with open(tsv_path, "r") as file:
    reader = csv.reader(file, delimiter="\t", quotechar='"')
    inventions = [Invention(**invention_from_tsv(row)) for row in reader]
    # Skip the header.
    inventions = inventions[1:]
    return inventions


def invention_from_tsv(fields: list[str]) -> dict:
  if len(fields) <= 8:
    # print(fields)
    print(f"Warning: Invalid TSV format. Only {len(fields)} fields found.")
    if len(fields) == 7:
      # Unknown field.
      fields.append("Unknown")
  return {
    "id": fields[0],
    "year": fields[1],
    "title": fields[2],
    "summary": fields[3],
    "inventor": fields[4],
    "location": fields[5],
    "related": fields[6],
    "field": fields[7],
  }
