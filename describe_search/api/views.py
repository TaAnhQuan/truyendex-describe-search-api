# api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Manga
from .serializers import MangaSerializer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np

class MangaSearchView(APIView):
    def get(self, request):
        # Get the 'desribe' parameter from the request query
        describe = request.GET.get('describe', None)

        # Serialize the records
        mangas = Manga.objects.all()
        serializer = MangaSerializer(mangas, many=True)

        embedding_data = []
        
        for i in range(0, len(mangas)):
            embedding_data.append(np.array([float(x.split('(')[-1].split(')')[0]) for x in mangas[i].embedding.split(',')]))
        
        embedding_data = np.array(embedding_data)

        model = SentenceTransformer('..\\semantic_model')
        describe_embedding = model.encode(describe)
        describe_embedding = describe_embedding.reshape(1, -1)


        cosine_similarities = cosine_similarity(describe_embedding, embedding_data).flatten()
        top_n_indices = cosine_similarities.argsort()[-5:][::-1]
        top_describes = top_n_indices[0].item()
        
        title = mangas.filter(title=mangas[top_describes])
                
        if not describe:
            return Response({"error": "describe parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Serialize the results
        serializer = MangaSerializer(title, many=True)
    
        return Response(serializer.data, status=status.HTTP_200_OK)
