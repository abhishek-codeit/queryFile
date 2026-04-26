import ollama
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv

load_dotenv()



reader = PDFReader()
EMBED_MODEL = "mxbai-embed-large"
EMBED_DIM = 1024

splitter = SentenceSplitter(chunk_size=256,chunk_overlap=50)

def load_and_chunk_pdf(path: str):
    docs = PDFReader().load_data(file=path)
    texts = [d.text for d in docs if getattr(d,"text",None)]
    chunks = []
    for t in texts:
        chunks.extend(splitter.split_text(t))
    print("chunks ",chunks) 
    return chunks


def embed_texts(texts: list[str]) -> list[list[float]]:
    embeddings = []
    for text in texts:
        response = ollama.embeddings(
            model = EMBED_MODEL,
            prompt = text
        )
        embeddings.append(response['embedding'])

    print("response embedding",embeddings)
    return embeddings