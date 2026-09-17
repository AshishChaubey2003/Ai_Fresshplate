from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsAdminRole, IsDonorOrAdmin

from .models import Donation, RescueCenter
from .serializers import (
    DonationCreateSerializer,
    DonationSerializer,
    RescueCenterSerializer,
    UpdateDonationStatusSerializer,
)


class DonationCreateView(APIView):
    permission_classes = [IsDonorOrAdmin]
    serializer_class = DonationCreateSerializer

    def post(self, request):
        serializer = DonationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(donor=request.user)
        return Response(
            {"message": "Donation submitted successfully!", "donation": serializer.data},
            status=status.HTTP_201_CREATED,
        )


class MyDonationsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DonationSerializer

    def get_queryset(self):
        # select_related pulls the donor in the same query (no N+1)
        return Donation.objects.select_related("donor").filter(donor=self.request.user)


class AllDonationsView(generics.ListAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = DonationSerializer

    def get_queryset(self):
        queryset = Donation.objects.select_related("donor")
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset


class UpdateDonationStatusView(APIView):
    permission_classes = [IsAdminRole]
    serializer_class = UpdateDonationStatusSerializer

    def patch(self, request, pk):
        serializer = UpdateDonationStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        with transaction.atomic():
            # select_for_update locks the row so two admins can't overwrite each other
            donation = get_object_or_404(
                Donation.objects.select_for_update().select_related("donor"), pk=pk
            )
            new_status = data.get("status", donation.status)

            if new_status != donation.status:
                if not donation.can_transition_to(new_status):
                    return Response(
                        {"error": f"Cannot change status from '{donation.status}' to '{new_status}'."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Food safety: never send out food that is past its expiry time
                moving_forward = new_status in (
                    Donation.Status.APPROVED,
                    Donation.Status.PICKED_UP,
                    Donation.Status.DISTRIBUTED,
                )
                if moving_forward and donation.expiry_time <= timezone.now():
                    return Response(
                        {"error": "This food has passed its expiry time. Reject it instead."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            donation.status = new_status
            if "admin_note" in data:
                donation.admin_note = data["admin_note"]
            donation.save(update_fields=["status", "admin_note", "updated_at"])

        return Response(
            {"message": "Donation status updated", "donation": DonationSerializer(donation).data}
        )


class RescueCenterListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = RescueCenterSerializer
    queryset = RescueCenter.objects.filter(is_active=True)


class RescueCenterCreateView(generics.CreateAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = RescueCenterSerializer
    queryset = RescueCenter.objects.all()