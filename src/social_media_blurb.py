#!/usr/bin/env python3
import argparse
import os
import requests
from openai import OpenAI
from utils import load_inventions

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("--id", help="The id of the card to process.")
  args = parser.parse_args()

  inventions = load_inventions("asimov.tsv")

  invention = next((i for i in inventions if i.id == args.id), None)
  if not invention:
    raise ValueError(f"Invention with id {args.id} not found.")

  prompt = f"""Title: {invention.title}
Description: {invention.summary}
Category: {invention.field}
Year: {invention.year}
Person: {invention.inventor}

Your task is to write a tweet that will generate interest in my visual chronology of science & technology project. Don't use the word "our". The tweet should be engaging and informative. It should be no longer than 200 characters. Make it sound scientific and not too promotional, and include popular and relevant hashtags, but not more than three."""

  headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
  }

  payload = {
    "model": "gpt-4o",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": prompt
          }
        ]
      }
    ]
   }
  response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
  response_json = response.json()
  if "error" in response_json:
    print(response_json["error"]["message"])
  content = response_json["choices"][0]["message"]["content"]
  content += " #AiArt"
  print(content)
  print(f"https://invention.cards/{invention.id}")
  print('---')
  print(f"https://invention.cards/{invention.id}/card.jpg")

