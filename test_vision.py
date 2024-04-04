#!/usr/bin/env python3
import argparse
import base64
import json
import requests
import os
from pydantic import BaseModel, ConfigDict

# OpenAI API Key
api_key = os.getenv('OPENAI_API_KEY')

class Invention(BaseModel):
  model_config = ConfigDict(strict=True)
  title: str
  year: int
  summary: str
  description: str
  inventor: str
  location: str
  field: str
  related: str

def summarize_inventions_from_image(base64_image: str) -> list[Invention]:
  headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
  }

  payload = {
    "model": "gpt-4-vision-preview",
  #   "response_format": {"type": "json_object"},
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": """Summarize the inventions on the following page. Provide the following information for each invention:

  - Title
  - Year
  - Summary (Two sentence summary without mentioning the name of the inventor, focusing on what the invention does, how it works, and its impact)
  - Description (Full description)
  - Name of the inventor
  - Country where the invention was made
  - Field (one of Math, Science, Culture, War, General, Design, Geography, Space)
  - A single related previous invention (if something influenced this invention, list it here)

  Output should be described as an array of JSON objects with the following keys: title, summary, description, year, inventor, location, field, related.
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
    "max_tokens": 1000
  }

  response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

  # print(response.json())
  content = response.json()["choices"][0]["message"]["content"]
  # print(content)

  # Extract the JSON bit from the response.
  try:
    content = content.split("```json")[1].split("```")[0]
  except Exception as e:
    print(content)
    print("Something went wrong", e)

  parsed = json.loads(content)
  for invention in parsed:
    invention["year"] = int(invention["year"])
  # print(parsed)

  return [Invention(**invention) for invention in parsed]



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

