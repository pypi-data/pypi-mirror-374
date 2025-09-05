from netbox.api.viewsets import NetBoxModelViewSet
from django.db.models import Count
from django.http import JsonResponse
from django.views import View
from .. import filtersets, models
from .serializers import OrganizationSerializer, ISDASSerializer, SCIONLinkAssignmentSerializer


class ISDACoreLookupView(View):
    """
    AJAX endpoint to get available cores for a specific ISD-AS
    """
    def get(self, request):
        isdas_id = request.GET.get('isdas_id')
        if not isdas_id:
            return JsonResponse({'cores': []})
        
        try:
            isdas = models.ISDAS.objects.get(id=isdas_id)
            cores = isdas.cores or []
            return JsonResponse({'cores': cores})
        except models.ISDAS.DoesNotExist:
            return JsonResponse({'cores': []})


class OrganizationViewSet(NetBoxModelViewSet):
    queryset = models.Organization.objects.prefetch_related('isd_ases').annotate(
        isd_ases_count=Count('isd_ases')
    )
    serializer_class = OrganizationSerializer
    filterset_class = filtersets.OrganizationFilterSet


class ISDAViewSet(NetBoxModelViewSet):
    queryset = models.ISDAS.objects.select_related('organization').prefetch_related('link_assignments').annotate(
        link_assignments_count=Count('link_assignments')
    )
    serializer_class = ISDASSerializer
    filterset_class = filtersets.ISDAFilterSet


class SCIONLinkAssignmentViewSet(NetBoxModelViewSet):
    queryset = models.SCIONLinkAssignment.objects.select_related('isd_as', 'isd_as__organization')
    serializer_class = SCIONLinkAssignmentSerializer
    filterset_class = filtersets.SCIONLinkAssignmentFilterSet
