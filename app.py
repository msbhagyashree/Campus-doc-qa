import io
import html
import streamlit as st
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer, util
import ollama

MODEL_NAME = "llama3.2"  # the local model Ollama runs
RELEVANCE_CUTOFF = 0.4   # matches below this score are ignored

st.set_page_config(page_title="Campus Doc Q&A", page_icon="🎓", layout="centered")

st.markdown("""
<style>
    .stApp {
        background-color: #3A0F34;
        background-image:
            radial-gradient(rgba(234, 170, 0, 0.15) 1px, transparent 1px),
            linear-gradient(135deg, rgba(221, 227, 235, 0.04) 25%, transparent 25%);
        background-size: 22px 22px, 44px 44px;
        color: #DDE3EB;
    }
    h1 {
        color: #EAAA00;
        border-bottom: 3px solid #EAAA00;
        padding-bottom: 0.3rem;
    }
    [data-testid="stContainer"] {
        background-color: #DDE3EB;
        color: #3A0F34;
        border: 2px solid #EAAA00;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
    }
    .stAlert { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# Load the embedding model once and reuse it
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

# Read an uploaded PDF, split it into lines, and convert each line to a vector.
@st.cache_data(show_spinner="Reading and indexing your document...")
def build_index(file_bytes):
    model = load_model()
    reader = PdfReader(io.BytesIO(file_bytes))

    passages = []  # each item is (text, page number)
    for page_number, page in enumerate(reader.pages, start=1):
        for line in (page.extract_text() or "").split("\n"):
            line = line.strip()
            if len(line) > 15:  # skip tiny fragments like page numbers
                passages.append((line, page_number))

    texts = [text for text, _ in passages]
    vectors = model.encode(texts, convert_to_tensor=True)
    return passages, vectors

# Send the matching passages to the local LLM and get a written answer
def generate_answer(question, matches):
    context = "\n".join(f"[Page {page}] {text}" for text, page in matches)
    prompt = f"""You are answering questions about a university document.
Use ONLY the context below. Do not use outside knowledge.
If the context does not state a fact (such as a chapter number), do not invent it.
Say what the context shows and mention the page numbers.

Context:
{context}

Question: {question}
Answer:"""
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"]

st.title("🎓 Campus Document Q&A")
st.write("Upload a PDF from your university, then ask questions about it.")

uploaded = st.file_uploader("Upload a PDF", type="pdf")

if uploaded is None:
    st.info("Upload a PDF to get started.")
else:
    passages, vectors = build_index(uploaded.getvalue())
    st.success(f"Ready. Indexed {len(passages)} lines from {uploaded.name}")

    question = st.text_input("Ask a question:", placeholder="e.g. Which chapter covers deadlocks?")

    if question:
        model = load_model()
        question_vector = model.encode(question, convert_to_tensor=True)

        # Score every line against the question, then keep the top 3
        scores = util.cos_sim(question_vector, vectors)[0]
        best = scores.topk(min(3, len(passages)))

        # Keep only the matches that pass the cutoff
        matches = []
        for score, index in zip(best.values, best.indices):
            s = float(score)
            if s >= RELEVANCE_CUTOFF:
                text, page = passages[int(index)]
                matches.append((text, page, s))

        if not matches:
            st.warning("No relevant answer found in this document.")
        else:
            with st.spinner("Writing an answer with the local AI model..."):
                answer = generate_answer(
                    question, [(text, page) for text, page, _ in matches]
                )
            st.subheader("Answer")
            st.write(answer)

            st.subheader("Sources")
            for text, page, s in matches:
                with st.container(border=True):
                    st.markdown(f"**Match {s:.0%}** · Page {page}")
                    st.write(text)