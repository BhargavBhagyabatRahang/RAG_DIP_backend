import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .serializers import FileUploadSerializer

from ingestion.chunking.chunker import chunk_markdown
from ingestion.chunking.chunk_writer import save_chunks
import json
from ingestion.embeddings.embedder import embed_texts

from .serializers import FileUploadSerializer
from ingestion.utils.file_detector import detect_file_category
from ingestion.processors.pdf_converter import convert_to_pdf

from ingestion.processors.pdf_to_md import pdf_to_markdown

from ingestion.utils.file_router import get_upload_subdir
from ingestion.vectorstore.qdrant_store import QdrantVectorStore

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ingestion.embeddings.embedder import embed_texts
from ingestion.vectorstore.qdrant_store import QdrantVectorStore
from ingestion.reranker.rerank import ONNXReranker

class QueryView(APIView):

    def post(self, request):
        try:
            query = request.data.get("query")

            if not query:
                return Response(
                    {"error": "Query is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 1) Embed Query
            query_vector = embed_texts([query])[0]

            # 2) Search Qdrant
            store = QdrantVectorStore(collection_name="refinery_docs")

            search_results = store.search(
                vector=query_vector,
                limit=10
            )

            if not search_results:
                return Response(
                    {"message": "No relevant documents found"},
                    status=status.HTTP_200_OK
                )

            # Extract texts
            documents = [
                result.payload.get("text", "")
                for result in search_results
            ]

            # 3️) Rerank
            model_dir = os.path.join(
                os.path.dirname(__file__),
                "..",
                "reranker"
            )

            reranker = ONNXReranker(model_dir=model_dir)

            top_results = reranker.rerank(query, documents, top_k=3)

            response_data = [
                {
                    "text": doc,
                    "score": float(score)
                }
                for doc, score in top_results
            ]

            return Response(
                {"results": response_data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    "error": "Query processing failed",
                    "reason": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class PdfToMarkdownView(APIView):
    
    def post(self, request):
        try:
            pdf_path = request.data.get("path")

            if not pdf_path:
                return Response(
                    {"error": "PDF path not provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not os.path.exists(pdf_path):
                return Response(
                    {"error": "PDF file does not exist"},
                    status=status.HTTP_404_NOT_FOUND
                )

            md_path = pdf_to_markdown(
                pdf_path,
                base_output_dir=os.path.join(
                    settings.BASE_DIR, "..", "data", "markdown"
                )
            )

            return Response(
                {
                    "message": "PDF converted to Markdown using MinerU",
                    "markdown_path": md_path
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    "error": "PDF to Markdown conversion failed",
                    "reason": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class UploadView(APIView):
    def post(self, request):
        try:
            uploaded_file = request.FILES.get("file")

            if not uploaded_file:
                return Response(
                    {"error": "No file uploaded"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            filename = uploaded_file.name
            category = detect_file_category(filename)

            # 1) Saving original file into categorized folder
            original_base = os.path.join(
                settings.BASE_DIR, "..","data", "uploads", "original", category
            )
            os.makedirs(original_base, exist_ok=True)

            original_path = os.path.join(original_base, filename)

            with open(original_path, "wb+") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            # 2) Handle PDF vs non-PDF
            converted_pdf_dir = os.path.join(
                settings.BASE_DIR, "..", "data", "uploads", "converted", "pdf"
            )
            os.makedirs(converted_pdf_dir, exist_ok=True)

            if category == "pdf":
                # PDF → directly usable
                final_pdf_path = os.path.join(converted_pdf_dir, filename)

                if not os.path.exists(final_pdf_path):
                    # copy instead of re-saving
                    with open(original_path, "rb") as src, open(final_pdf_path, "wb") as dst:
                        dst.write(src.read())

            else:
                # Non-PDF → convert to PDF
                final_pdf_path = convert_to_pdf(
                    original_path,
                    converted_pdf_dir
                )

            return Response(
                {
                    "message": "File uploaded successfully",
                    "original_category": category,
                    "original_path": original_path,
                    "converted_pdf_path": final_pdf_path
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {
                    "error": "File upload failed",
                    "reason": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class ChunkMarkdownView(APIView):
    def post(self, request):
        try:
            md_path = request.data.get("path")
            # Allowing dynamic control of chunk size for different doc types
            max_chars = int(request.data.get("max_chars", 500))
            overlap = int(request.data.get("overlap", 50))

            if not md_path or not os.path.exists(md_path):
                return Response({"error": "Valid Markdown path required"}, status=status.HTTP_400_BAD_REQUEST)

            with open(md_path, "r", encoding="utf-8", errors="replace") as f:
                markdown_text = f.read()

            base_name = os.path.splitext(os.path.basename(md_path))[0]
            chunk_dir = os.path.join(settings.BASE_DIR, "..", "data", "chunks", base_name)

            # Passing the new overlap parameter
            chunks = chunk_markdown(
                markdown_text=markdown_text,
                source_file=base_name,
                max_chars=max_chars,
                overlap=overlap
            )

            saved_files = save_chunks(chunks, base_name, chunk_dir)

            return Response({
                "message": "Processing complete",
                "stats": {
                    "total_chunks": len(saved_files),
                    "directory": chunk_dir,
                    "metadata_fields": ["source_file", "section", "chunk_index"]
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class EmbedChunksView(APIView):
    def post(self, request):
        try:
            chunk_dir = request.data.get("chunk_dir")

            if not chunk_dir or not os.path.exists(chunk_dir):
                return Response(
                    {"error": "Chunk directory not found"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            texts = []
            metas = []

            for fname in sorted(os.listdir(chunk_dir)):
                if fname.endswith(".json"):
                   path = os.path.join(chunk_dir, fname)

                with open(path, "r", encoding="utf-8") as f:
                   chunk = json.load(f)

                   chunk_text = chunk.get("text", "")
                   chunk_meta = chunk.get("metadata", {})

                   texts.append(chunk_text)

                   payload = {
                      "text": chunk_text,   
                       **chunk_meta          
                   }

                   metas.append(payload)

            if not texts:
                return Response(
                    {"error": "No chunks found"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            vectors = embed_texts(texts)
            dim = vectors.shape[1]

            # Using Qdrant
            store = QdrantVectorStore(
                collection_name="refinery_docs",
                vector_size=dim
            )

            store.add_vectors(
                embeddings=vectors.tolist(),
                metadatas=metas
            )

            return Response(
                {
                    "message": "Chunks embedded and stored successfully (Qdrant)",
                    "vectors_added": len(texts),
                    "vector_dimension": dim
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    "error": "Embedding failed",
                    "reason": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



