from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Category, FoodItem
from .serializers import CategorySerializer, FoodItemSerializer, FoodItemCreateSerializer


class CategoryListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(is_active=True)


class CategoryCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'admin':
            return Response({'error': 'Admin access only'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FoodItemListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = FoodItemSerializer

    def get_queryset(self):
        queryset = FoodItem.objects.filter(is_available=True)
        category = self.request.query_params.get('category')
        is_veg = self.request.query_params.get('is_veg')
        status_filter = self.request.query_params.get('status')
        search = self.request.query_params.get('search')

        if category:
            queryset = queryset.filter(category__id=category)
        if is_veg:
            queryset = queryset.filter(is_veg=is_veg.lower() == 'true')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset


class FoodItemDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = FoodItemSerializer
    queryset = FoodItem.objects.all()


class FoodItemCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'admin':
            return Response({'error': 'Admin access only'}, status=status.HTTP_403_FORBIDDEN)
        serializer = FoodItemCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FoodItemUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FoodItemCreateSerializer
    queryset = FoodItem.objects.all()

    def update(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({'error': 'Admin access only'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({'error': 'Admin access only'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class RescueFoodListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = FoodItemSerializer
    queryset = FoodItem.objects.filter(status='rescue', is_available=True)