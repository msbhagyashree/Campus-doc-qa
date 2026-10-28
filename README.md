# Campus Document Q&A

Upload a university PDF (syllabus, notice, fee sheet, or timetable) and ask questions about it in plain English. The app finds the most relevant lines in the document and uses a local AI model to write an answer, with the sources shown below it.

## Features

- Upload any PDF and ask questions about its content
- Meaning-based search, so you don't need the exact words from the document
- A relevance cutoff that says "no answer found" instead of showing unrelated text
- Answers written by a local LLM, grounded only in the document
- Every answer shows its source lines and page numbers
- Custom dark theme styled with CSS

## How It Works

1. **Upload:** The PDF is read page by page, and each useful line is kept with its page number.
2. **Embed and search:** A sentence-transformer model (`all-MiniLM-L6-v2`) converts each line and your question into vectors. Cosine similarity finds the closest lines.
3. **Cutoff:** Lines scoring below 0.4 are ignored.
4. **Answer:** The top matching lines are sent to a local model (`llama3.2` through Ollama) with instructions to answer only from that context.
5. **Sources:** The matching lines and their page numbers are displayed under the answer.

## Tech Stack

- Python
- Streamlit (web interface)
- sentence-transformers (embeddings and similarity search)
- pypdf (PDF reading)
- Ollama with llama3.2 (answer generation)

## Setup

1. Install Ollama from https://ollama.com and open it.
2. Download the model:

   ```
   ollama pull llama3.2
   ```

3. Install the Python packages:

   ```
   pip install streamlit sentence-transformers pypdf ollama
   ```

4. Run the app from the project folder:

   ```
   streamlit run app.py
   ```

The first run downloads the embedding model, which can take a few minutes.

## Test Results

| Document | Question | Result |
|---|---|---|
| OS Syllabus | Which chapter contains deadlock concepts? | Correct topic and page. The model described the page but did not name a chapter number, which the document does not state. |
| OS Syllabus | What is the capital of France? | "No relevant answer found" shown correctly. |
| Notice | *(add your question)* | *(add your result)* |
| Fee sheet | *(add your question)* | *(add your result)* |
| Timetable | *(add your question)* | *(add your result)* |

## Known Limitations

- **Tables and multi-column pages** can come out jumbled, since text extraction reads lines in order.
- **The 0.4 cutoff** was chosen by testing on a few documents. It may need tuning for others.
- **Answers can be vague.** A small local model sometimes describes where the answer is instead of stating it. The Sources section lets users check.
- **Local only.** The app runs on one computer and needs Ollama running in the background.

## Next Steps

- Improve PDF parsing for tables and columns
- Tune the cutoff using a larger set of test questions
- Add chapter-heading detection so answers can name chapters directly
- Host the app online so others can use it, with a separate hosted model

## Project Structure

```
PROJECT - 1/
├── app.py        # the full application
├── notes.txt     # sample notes (from the first version)
└── README.md     # this file
```