import logging
from fastapi import FastAPI
import inngest
import inngest.fast_api
from inngest.experimental import ai
from dotenv import load_dotenv
import uuid
import os
import ollama
import datetime
from data_loader import load_and_chunk_pdf, embed_texts
from vector_db import QdrantStorage
from custom_Type import RAGChunkAndSrc, RAGSearchResult,RAGUpsertResult,RAQQueryResult
load_dotenv()

inngest_client = inngest.Inngest(
    app_id="queryFIle",
    logger=logging.getLogger("uvicorn"),
    is_production=False,
    serializer=inngest.PydanticSerializer()
)




app = FastAPI()

@inngest_client.create_function(
    fn_id="RAG: INGEST FILE",
    trigger=inngest.TriggerEvent(event="rag/ingest_pdf")
)

async def rag_ingest_pdf(ctx: inngest.Context):
    
    def _load_pdf(ctx: inngest.Context) -> RAGChunkAndSrc:
        pdf_path = ctx.event.data["pdf_path"]
        source_id = ctx.event.data.get("source_id", pdf_path)
        chunks = load_and_chunk_pdf(pdf_path)
        print("chunks ",chunks)
        return RAGChunkAndSrc(chunks=chunks, source_id=source_id)
    
    def _upsert(chunks_and_src: RAGChunkAndSrc) -> RAGUpsertResult:
        chunks = chunks_and_src.chunks
        source_id=chunks_and_src.source_id
        vecs = embed_texts(chunks)
        ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{i}")) for i in range(len(chunks))]
        print("ids ",ids)
        payloads = [{"source": source_id, "text": chunks[i]} for i in range(len(chunks))]

        QdrantStorage().upsert(ids,vecs,payloads)
        return RAGUpsertResult(ingested=len(chunks))




    load_chunk = await ctx.step.run("load_chunk_pdf",lambda: _load_pdf(ctx),output_type=RAGChunkAndSrc)
    ingested = await ctx.step.run("embed-and-upsert",lambda: _upsert(load_chunk),output_type=RAGUpsertResult)


    return ingested.model_dump()

@inngest_client.create_function(
    fn_id="RAG Query PDF",
    trigger=inngest.TriggerEvent(event="rag/query_pdf_ai")

)
async def rag_query_pdf_ai(ctx: inngest.Context) -> RAGSearchResult:
    def _search(question: str,top_k: int = 5):
        query_vec = embed_texts([question])[0]
        print("query vecotor ", query_vec)
        store = QdrantStorage()
        found = store.search(query_vec,top_k)
        return RAGSearchResult(contexts=found["contexts"],sources=found["sources"])

    question = ctx.event.data["question"]
    found = await ctx.step.run("embed-and-search",lambda: _search(question), output_type=RAGSearchResult)        

    context_block = "\n\n".join(f"- {c}" for c in found.contexts)

    user_content = (
        "Use the following context to answer the questions.\n\n"
        f"Context: \n{context_block}\n\n"
        f"Question: {question}\n"
        "Answer concisely using the context above."
    )
    async def _ollama_chat():
        response = ollama.chat(
            model="llama3.2:1b",
            messages=[
                {"role": "system","content": "You answer questions using only the provided context."},
                {"role": "user","content":user_content}
            ],
            options={"temperature":0.2}
        )
        return response["message"]["content"]
    
    # adapter for OpenAI 
    # adapter = ai.openai.Adapter(
    #     auth_key=os.getenv("OPENAI_API_KEY"),
    #     model="gpt-40-mini"
    # )

    # res = await ctx.step.ai.infer(
    #     "llm-answer",
    #     adapter=adapter,
    #     body={
    #         "max_tokens": 1024m
    #         "temperature": 0.2,
    #         "messages":[
    #             {"role": "system","content": "You answer questions using only the provided context."},
    #             {"role": "user","content":user_content}
    #         ]
    #     }
    # )

    answer = await ctx.step.run("ollama-llm-answer",lambda: _ollama_chat())
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(answer)
    return {"answer": answer.strip(), "sources": list(set(found.sources)), "num_contexts": len(found.contexts)}

inngest.fast_api.serve(app, inngest_client, [rag_ingest_pdf, rag_query_pdf_ai])