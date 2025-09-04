from django.http import JsonResponse
from django.views.generic.base import RedirectView
from django.shortcuts import render
from netbox.views import generic
from . import forms, models, tables, filtersets


class PluginHomeView(generic.ObjectListView):
    """Home view for the SCION plugin showing all main sections."""
    queryset = models.SCIONLinkAssignment.objects.select_related('isd_as', 'isd_as__organization')
    table = tables.SCIONLinkAssignmentTable
    filterset = filtersets.SCIONLinkAssignmentFilterSet
    template_name = 'generic/object_list.html'


def get_isdas_cores(request):
    """AJAX view to get cores for a specific ISD-AS"""
    isdas_id = request.GET.get('isdas_id')
    if isdas_id:
        try:
            isdas = models.ISDAS.objects.get(pk=isdas_id)
            cores = isdas.cores or []
            return JsonResponse({'cores': cores})
        except models.ISDAS.DoesNotExist:
            pass
    return JsonResponse({'cores': []})


class OrganizationView(generic.ObjectView):
    queryset = models.Organization.objects.prefetch_related('isd_ases')
    template_name = 'netbox_scion/organization_detail.html'


class OrganizationListView(generic.ObjectListView):
    queryset = models.Organization.objects.prefetch_related('isd_ases')
    table = tables.OrganizationTable
    filterset = filtersets.OrganizationFilterSet
    template_name = 'generic/object_list.html'


class OrganizationEditView(generic.ObjectEditView):
    queryset = models.Organization.objects.all()
    form = forms.OrganizationForm


class OrganizationDeleteView(generic.ObjectDeleteView):
    queryset = models.Organization.objects.all()


class OrganizationChangeLogView(generic.ObjectChangeLogView):
    queryset = models.Organization.objects.all()


class ISDAView(generic.ObjectView):
    queryset = models.ISDAS.objects.select_related('organization')
    template_name = 'netbox_scion/isdas_detail.html'


class ISDAListView(generic.ObjectListView):
    queryset = models.ISDAS.objects.select_related('organization').prefetch_related('link_assignments')
    table = tables.ISDATable
    filterset = filtersets.ISDAFilterSet
    template_name = 'generic/object_list.html'


class ISDAEditView(generic.ObjectEditView):
    queryset = models.ISDAS.objects.all()
    form = forms.ISDAForm


class ISDADeleteView(generic.ObjectDeleteView):
    queryset = models.ISDAS.objects.all()


class ISDAChangeLogView(generic.ObjectChangeLogView):
    queryset = models.ISDAS.objects.all()


class SCIONLinkAssignmentView(generic.ObjectView):
    queryset = models.SCIONLinkAssignment.objects.select_related('isd_as', 'isd_as__organization')
    template_name = 'netbox_scion/scionlinkassignment_detail.html'


class SCIONLinkAssignmentListView(generic.ObjectListView):
    queryset = models.SCIONLinkAssignment.objects.select_related('isd_as', 'isd_as__organization')
    table = tables.SCIONLinkAssignmentTable
    filterset = filtersets.SCIONLinkAssignmentFilterSet
    template_name = 'generic/object_list.html'


class SCIONLinkAssignmentEditView(generic.ObjectEditView):
    queryset = models.SCIONLinkAssignment.objects.all()
    form = forms.SCIONLinkAssignmentForm
    template_name = 'netbox_scion/scionlinkassignment_edit.html'


class SCIONLinkAssignmentDeleteView(generic.ObjectDeleteView):
    queryset = models.SCIONLinkAssignment.objects.all()


class SCIONLinkAssignmentChangeLogView(generic.ObjectChangeLogView):
    queryset = models.SCIONLinkAssignment.objects.all()
