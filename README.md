# LOLHealthExaminer

I asked ChatGPT to help me come up with a catchy or humerous name for this project and this is what I got. Proof the naming is hard, even for LLMs!

This tool can be run from the command line with `python main.py [input file location] [output file location]`.

## What it does

- Read text from a .txt or .pdf file
- Pass that text to Open AI's API with questions
  - Extract key information
  - If there is a predefined set of questions for the chief complaint: Ask them
  - Else: Ask the LLM for a sensible list of questions, then ask it to answer them
- Write results to file as json

## TODOs:

- Define and enforce json schema of results
- Paralellise requests
- Make docker work
- Input data cleaning
- Enable alternative APIs
- Enable local open source model
