from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Donation, RescueCenter
from .serializers import DonationSerializer, DonationCreateSerializer, RescueCenterSerializer


class DonationCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in ['donor', 'admin']:
            return Response({'error': 'Only donors can donate food'}, status=status.HTTP_403_FORBIDDEN)
        serializer = DonationCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(donor=request.user)
            return Response({
                'message': 'Donation submitted successfully!',
                'donation': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyDonationsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DonationSerializer

    def get_queryset(self):
        return Donation.objects.filter(donor=self.request.user).order_by('-created_at')


class AllDonationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'admin':
            return Response({'error': 'Admin access only'}, status=status.HTTP_403_FORBIDDEN)
        donations = Donation.objects.all().order_by('-created_at')
        serializer = DonationSerializer(donations, many=True)
        return Response(serializer.data)


class UpdateDonationStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        if request.user.role != 'admin':
            return Response({'error': 'Admin access only'}, status=status.HTTP_403_FORBIDDEN)
        try:
            donation = Donation.objects.get(id=pk)
            donation.status = request.data.get('status', donation.status)
            donation.admin_note = request.data.get('admin_note', donation.admin_note)
            donation.save()
            return Response({
                'message': 'Donation status updated',
                'donation': DonationSerializer(donation).data
            })
        except Donation.DoesNotExist:
            return Response({'error': 'Donation not found'}, status=status.HTTP_404_NOT_FOUND)


class RescueCenterListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = RescueCenterSerializer
    queryset = RescueCenter.objects.filter(is_active=True)


class RescueCenterCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'admin':
            return Response({'error': 'Admin access only'}, status=status.HTTP_403_FORBIDDEN)
        serializer = RescueCenterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)