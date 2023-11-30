# LOLHealthExaminer

I asked ChatGPT to help me come up with a catchy or humerous name for this project and this is what I got. Proof that good naming is really hard, even for LLMs!

## Running it

This tool can be run from the command line with `python src/main.py [input file location] [output file location]`. Input data must be in a `.txt` or `.pdf` file, and pdfs must contain text (not just an image of text - we're not doing any OCR here). Currently it will only operate on one file at a time.
It will try to pick up two environment variables:

- `LOG_LEVEL` (which defaults to `WARNING`)
- `OPENAI_API_KEY` - you'll need to have set this in your environment in advance

You can also run LOLHealthExaminer with Docker (from the LOLHealthExaminer project root directory):

```bash
docker build -t lol-health-examiner .
docker run \
    -e LOG_LEVEL=[chosen log level (optional)] \
    -e OPENAI_API_KEY=[your open ai api key] \
    -v [absolute path to the directory containing your data]:/app/data \
    lol-health-examiner \
    /app/data/[medical record filename] /app/data/[output filename]
```

## What it does

- Read text from a .txt or .pdf file
- Pass that text to Open AI's API with questions
  - Extract key information
  - If side effects are missing: Ask again
  - If there is a predefined set of questions for the chief complaint: Ask them
  - Else: Ask the LLM for a sensible list of questions, then ask it to answer them
  - Ask for a final assessment of the treatment plan
- Write results to file as json

## TODOs:

- Tests
- Proper handling of response validation errors
- Parallelise requests / set up for serverless inference
- Input data cleaning
- Enable alternative LLM APIs
- Enable local open source model
- More prompt engineering

## Notes on the approach

Thanks for setting me this task - I really enjoyed it and learned a lot! I thought here I would take you through some of my thinking as I put my solution together.

### Extracting key information

The approach here was fairly straightforward - give the model the medical record and ask it to extract the requested information in a defined format. One thing that was immediately obvious was that side effects were not usually returned, so I put in some logic to go back to the model and request them again. The problem with this is in interpreting the response - the model finds new and ingenious ways to return the equivalent of an empty list and I am not immediately sure the best way to make a closed solution for this - waiting to see a new failure case and then adding it to a list isn't very scalable or maintainable, but it should still cover the majority fairly quickly.

### Answer the following questions

Again, asking these follow up questions of the model and providing a defined format for its answers is straightforward. The obvious question that posed itself was what to do in a scenario where the patient's chief complaint is different, and therefore not relevant to these questions?

To handle this scenario I created a library of questions for specific complaints (for now with just the one complaint-questions pair). If the complaint is not in this library then the app asks the model to come up with a suitable set of follow up questions. This is a nice way of handling edge cases, but it might not actually be appropriate for a real product. I think the final accuracy would likely be lower in cases where this approach was used. Three alternatives that might be more realistic:

1. Use this approach but flag to the human reviewing the final decision that there may be more uncertainty in it (either explicitly, or by down-weighting a confidence measure of the final decision)
2. Choose to limit the product's coverage to a set of complaints with follow up questions which have been approved by a doctor, and look to expand this coverage over time
3. Have an extra step in the process for cases where pre-approved questions do not exist, where a human user reviews the extracted key information and is asked to enter their own set of follow up questions

#### Justification and confidence

This part of the solution definitely needs some work. The model seems very confident in its answers, and largely ignored my prompt that it shouldn't take absence of information as confirmation of a negative - answers like this are quite common:

```json
{
    "question": "Has the patient had significant loss of blood?",
    "answer": "No, there is no indication of significant loss of blood.",
    "confidence": 9,
    "justification": "The medical record does not mention any significant loss of blood."
},
```

Similarly, the model consistently ignores my definition of a first-degree relative. Interestingly I found that when prompting the model directly in Open AI's API and specifiying the output format in text this didn't seem to be a problem - it laregely acknowledged and stuck to my definition, but when I switched to Langchain + Pydantic I achieved better structure but worse adherence to other things in my instruction, such as this definition (e.g. below). I'm not yet sure of the best way to give a more detailed prompt of what is expected in each element of the specified data structure.

```json
{
    "question": "Does the patient have a family history of colon cancer in their first-degree relatives? (a first-degree relative is only a parent, sibling, or child)",
    "answer": "Yes, the patient has a family history of colon cancer in a first-degree relative (grandfather).",
    "confidence": 9,
    "justification": "The patient's family history indicates a grandfather with colon cancer, which constitutes a first-degree relative."
},
```

### Final decision

For the final decision as to whether or not the doctor's proposed treatment plan is appropriate, the application asks the LLM for its opionion, based on the patient record and the answers it has already given. I think this is fine as an example, but could probably be improved upon.

We could make the decision more quantifiable if we had a metric based on the answers to the follow up questions. In order for this to be medically rigorous I think the scoring mechanism might need to be hand crafted for each illness, which would be laborious, unless maybe it is something that could be extracted from medical literature.

Alternatively, if we have a large enough dataset of previous records, questions asked, answers, and approval decisions, we should be able to train a model with supervised learning to make this decision (this will be easier if questions are standardised and have structured (boolean/categorical/numerical) answers). The viability of this approach would likely depend on both the volume and quality of data available and the accuracy and explainability requirements of the customer.

### Other points

- I thought about setting this up to run in parallel on all files provided in a directory, but could not immediately find an answer to whethere the client was thread safe. Then I also thought that this might actually be better implemented on a serverless architecture (e.g. AWS lambda) so parallelisation there wouldn't be an issue.
- I am new to langchain, but hopefully it's use and this approach in general should make it fairly easy to extend this solution to utilise additional LLM APIs and / or locally hosted models.
- I didn't do any kind of cleaning of the data (apart from warning the LLM that it might have transcription errors and it should correct them if it found any). I think this is something that would be worth doing if time allowed.
- Maybe if I wasn't such a cheapskate and upgraded to GPT-4 all of these issues would magically melt away!
