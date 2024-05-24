#!/usr/bin/env python3
import argparse
import os
import urllib.request

from utils import Invention, load_inventions
from openai import OpenAI

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

def generate_card_image(invention: Invention):
  prompt = f"""Title: {invention.title}
Description: {invention.summary}
Category: {invention.field}
Year: {invention.year}
Person: {invention.inventor}

Generate vibrant art nouveau for the invention/discovery described above. The image should be a single object or scene that represents the invention/discovery. Please do not include any typography or text. Please do not draw any people.
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

  inventions = load_inventions("asimov.tsv")
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