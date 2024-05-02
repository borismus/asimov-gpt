#!/usr/bin/env python3
import argparse
import csv
import os
import urllib.request

from test_vision import Invention
from openai import OpenAI

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

def generate_card_image(invention: Invention):
  prompt = f"""Title: {invention.title}
Description: {invention.summary}
Category: {invention.field}
Year: {invention.year}
Person: {invention.inventor}

Generate vibrant art nouveau for the invention/discovery described above. The image should be a single object or scene that represents the invention/discovery. Do not include any typography or text. Do not draw any people.
"""

  # print(prompt)
  response = client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size="1024x1024",
    quality="standard",
    n=1,
  )

  return response.data[0].url

def load_inventions(tsv_path) -> list[Invention]:
  with open(tsv_path, "r") as file:
    reader = csv.reader(file, delimiter="\t", quotechar='"')
    inventions = [Invention(**invention_from_tsv(row)) for row in reader]
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

def get_unique_path(invention: Invention, default=False) -> str:
  index = 0
  def get_path(i):
    suffix = f"-{i}" if i > 0 else ""
    return f"images/{invention.id}{suffix}.jpg"

  if default:
    return get_path(0)

  while os.path.exists(get_path(index)):
    index += 1

  return get_path(index)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("--one", help="The id of the entry to process.")
  parser.add_argument("--from_year", type=int, help="The year to start from.")
  parser.add_argument("--to_year", type=int, help="The year to end at.")
  parser.add_argument("--force", action="store_true", help="Force re-generation of images.")
  args = parser.parse_args()

  inventions = load_inventions("asimov-1850.tsv")
  # Scrap the header.
  inventions = inventions[1:]
  print(f"Loaded {len(inventions)} inventions.")

  if args.one:
    invention = next((i for i in inventions if i.id == args.one), None)
    if not invention:
      raise ValueError(f"Invention with id {args.one} not found.")
    inventions = [invention]

  if args.from_year:
    inventions = [i for i in inventions if i.year_number() >= args.from_year]

  if args.to_year:
    inventions = [i for i in inventions if i.year_number() <= args.to_year]

  print(f"Processing {len(inventions)} inventions.")
  for invention in inventions:
    try:
      # If force is not enabled, don't re-generate images.
      if not args.force and os.path.exists(get_unique_path(invention, default=True)):
        print(f"(Image already exists for {invention.id}. Skipping.)")
        continue
      print(f"Generating image for {invention.id} ({invention.year}).")
      image_url = generate_card_image(invention)
      saved_path = get_unique_path(invention)
      urllib.request.urlretrieve(image_url, saved_path)
      print(f"Saved image at {saved_path}.")
    except Exception as e:
      print(f"ERROR: Failed to generate image for {invention.id}. {e}")
      continue