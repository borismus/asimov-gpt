#!/usr/bin/env python3
import argparse
import base64
import json
import requests
import os

from utils import Invention

# OpenAI API Key
api_key = os.getenv('OPENAI_API_KEY')

def summarize_inventions_from_image(base64_image: str) -> list[Invention]:
  headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
  }

  payload = {
    "model": "gpt-4o",
  #   "response_format": {"type": "json_object"},
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": """Summarize the inventions or discoveries on the following page. Please ignore sections entitled "In Addition".

Provide the following information for each invention or discovery. Output should be described as an array of JSON objects with the following keys (the values should all be strings):

  - title: One to three words describing the invention or discovery.
  - year: The year the invention or discovery was made.
  - description: The full text of the invention or discovery, as written in the provided image.
  - summary: Three sentences; the first describes necessary context to understand the invention. The second describes what the invention is, and the last sentence describes its implications. DO NOT MENTION PEOPLE OR DATES. Do not exceed 150 characters for this field.
  - inventor: The full name of the inventor or discoverer.
  - location: In which country was the invention or discovery made? In the case of Great Britain or the United Kingdom, use "England".
  - field: Should be one of Math, Science, Culture, War, General, Design, Geography, Space. Sub-fields can be indicated with a colon (e.g. "Science: Physics or Science: Biology"). Instead of "Science: Astronomy", use "Space"
  - related: One or more related previous invention or discovery, separated by commas. If there are no related inventions or discoveries, use "".

Remember to escape quotes in JSON strings, and ensure the JSON is valid.
  """
          },
          {
            "type": "image_url",
            "image_url": {
              "url": f"data:image/jpeg;base64,{base64_image}"
            }
          }
        ]
      }
    ],
    "max_tokens": 4000
  }

  response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
  response_json = response.json()

  # print(response.json())
  if "error" in response_json:
    print(response_json["error"]["message"])
    return []
  content = response_json["choices"][0]["message"]["content"]
  # print(content)

  # Extract the JSON bit from the response.
  try:
    if content.find("```json") == -1:
      json_content = content
    else:
      json_content = content.split("```json")[1].split("```")[0]
  except Exception as e:
    print("ERROR extracing JSON from response:", e)
    print(content)

  try:
    parsed = json.loads(json_content)
  except Exception as e:
    print("ERROR parsing extracted JSON:", e)
    print(json_content)

  for invention in parsed:
    invention["year"] = str(invention["year"])
    # Format the title so that only the first letter of the first word is capitalized.
    title = invention["title"]
    invention["title"] = title[0].upper() + title[1:].lower()

  return [Invention(**invention) for invention in parsed]


def summarize_inventions_from_two_page_context(base64_image1: str, base64_image2: str) -> list[Invention]:
  # Use the first page to get a list of headings.
  # Use both pages to get the content for each heading.
  pass


# Function to encode the image
def encode_image(image_path: str):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')



if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("file", help="The image file to be processed.")
  args = parser.parse_args()

  # Getting the base64 string
  base64_image = encode_image(args.file)
  result = summarize_inventions_from_image(base64_image)

