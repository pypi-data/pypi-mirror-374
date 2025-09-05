from django.http import JsonResponse
from django.views.generic.base import RedirectView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from netbox.views import generic
from . import forms, models, tables, filtersets


class PluginHomeView(generic.ObjectListView):
    """Home view for the SCION plugin showing all main sections."""
    queryset = models.SCIONLinkAssignment.objects.select_related('isd_as', 'isd_as__organization')
    table = tables.SCIONLinkAssignmentTable
    filterset = filtersets.SCIONLinkAssignmentFilterSet
    filterset_form = forms.SCIONLinkAssignmentFilterForm
    template_name = 'generic/object_list.html'


def get_isdas_cores(request):
    """AJAX view to get cores and appliance type for a specific ISD-AS"""
    isdas_id = request.GET.get('isdas_id')
    
    if isdas_id:
        try:
            isdas = models.ISDAS.objects.get(pk=isdas_id)
            cores = isdas.cores or []
            appliance_type = getattr(isdas, 'appliance_type', 'CORE')
            
            return JsonResponse({
                'cores': cores,
                'appliance_type': appliance_type
            })
        except models.ISDAS.DoesNotExist:
            return JsonResponse({
                'error': 'ISD-AS not found',
                'cores': [],
                'appliance_type': None
            })
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'cores': [],
                'appliance_type': None
            })
    
    return JsonResponse({
        'error': 'No ISD-AS ID provided',
        'cores': [],
        'appliance_type': None
    })


class OrganizationView(generic.ObjectView):
    queryset = models.Organization.objects.prefetch_related('isd_ases')
    template_name = 'netbox_scion/organization_detail.html'


class OrganizationListView(generic.ObjectListView):
    queryset = models.Organization.objects.prefetch_related('isd_ases')
    table = tables.OrganizationTable
    filterset = filtersets.OrganizationFilterSet
    filterset_form = forms.OrganizationFilterForm


class OrganizationEditView(generic.ObjectEditView):
    queryset = models.Organization.objects.all()
    form = forms.OrganizationForm


class OrganizationDeleteView(generic.ObjectDeleteView):
    queryset = models.Organization.objects.all()


class OrganizationBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Organization.objects.all()
    table = tables.OrganizationTable


class OrganizationChangeLogView(generic.ObjectChangeLogView):
    queryset = models.Organization.objects.all()


class ISDAView(generic.ObjectView):
    queryset = models.ISDAS.objects.select_related('organization')
    template_name = 'netbox_scion/isdas_detail.html'


class ISDAListView(generic.ObjectListView):
    queryset = models.ISDAS.objects.select_related('organization').prefetch_related('link_assignments')
    table = tables.ISDATable
    filterset = filtersets.ISDAFilterSet
    filterset_form = forms.ISDAFilterForm


class ISDAEditView(generic.ObjectEditView):
    queryset = models.ISDAS.objects.all()
    form = forms.ISDAForm


class ISDADeleteView(generic.ObjectDeleteView):
    queryset = models.ISDAS.objects.all()


class ISDABulkDeleteView(generic.BulkDeleteView):
    queryset = models.ISDAS.objects.all()
    table = tables.ISDATable


class ISDAChangeLogView(generic.ObjectChangeLogView):
    queryset = models.ISDAS.objects.all()


def add_core_to_isdas(request, pk):
    """Add a core to an ISD-AS"""
    isdas = get_object_or_404(models.ISDAS, pk=pk)
    
    if request.method == 'POST':
        form = forms.CoreManagementForm(request.POST)
        if form.is_valid():
            core_name = form.cleaned_data['core_name']
            cores = isdas.cores or []
            
            if core_name not in cores:
                cores.append(core_name)
                isdas.cores = cores
                isdas.save()
                messages.success(request, f'Core "{core_name}" added successfully.')
            else:
                messages.error(request, f'Core "{core_name}" already exists.')
            
            return redirect('plugins:netbox_scion:isdas', pk=pk)
    else:
        form = forms.CoreManagementForm()
    
    return render(request, 'netbox_scion/add_core.html', {
        'form': form,
        'isdas': isdas,
        'return_url': request.GET.get('return_url', f"/plugins/scion/isdas/{pk}/"),
        'action': 'Add'
    })


def edit_core_in_isdas(request, pk, core_name):
    """Edit a core name in an ISD-AS"""
    isdas = get_object_or_404(models.ISDAS, pk=pk)
    cores = isdas.cores or []
    
    if core_name not in cores:
        messages.error(request, f'Core "{core_name}" not found.')
        return redirect('plugins:netbox_scion:isdas', pk=pk)
    
    if request.method == 'POST':
        form = forms.CoreManagementForm(request.POST)
        if form.is_valid():
            new_core_name = form.cleaned_data['core_name']
            
            if new_core_name != core_name:
                if new_core_name in cores:
                    messages.error(request, f'Core "{new_core_name}" already exists.')
                else:
                    # Update core name in the list
                    core_index = cores.index(core_name)
                    cores[core_index] = new_core_name
                    isdas.cores = cores
                    isdas.save()
                    
                    # Update all SCION link assignments that use this core
                    assignments = models.SCIONLinkAssignment.objects.filter(
                        isd_as=isdas, core=core_name
                    )
                    assignments.update(core=new_core_name)
                    
                    messages.success(request, f'Core renamed from "{core_name}" to "{new_core_name}".')
            else:
                messages.info(request, 'No changes made.')
            
            return redirect('plugins:netbox_scion:isdas', pk=pk)
    else:
        form = forms.CoreManagementForm(initial={'core_name': core_name})
    
    return render(request, 'netbox_scion/add_core.html', {
        'form': form,
        'isdas': isdas,
        'return_url': request.GET.get('return_url', f"/plugins/scion/isdas/{pk}/"),
        'action': 'Edit',
        'core_name': core_name
    })


def remove_core_from_isdas(request, pk, core_name):
    """Remove a core from an ISD-AS and all associated SCION link assignments"""
    isdas = get_object_or_404(models.ISDAS, pk=pk)
    
    cores = isdas.cores or []
    if core_name in cores:
        # Check how many SCION link assignments will be deleted
        assignments_to_delete = models.SCIONLinkAssignment.objects.filter(
            isd_as=isdas, core=core_name
        )
        assignments_count = assignments_to_delete.count()
        
        # Remove the core
        cores.remove(core_name)
        isdas.cores = cores
        isdas.save()
        
        # Delete all associated SCION link assignments
        if assignments_count > 0:
            assignments_to_delete.delete()
            messages.warning(
                request, 
                f'Core "{core_name}" removed successfully. '
                f'{assignments_count} SCION link assignment(s) were also deleted.'
            )
        else:
            messages.success(request, f'Core "{core_name}" removed successfully.')
    else:
        messages.error(request, f'Core "{core_name}" not found.')
    
    return redirect('plugins:netbox_scion:isdas', pk=pk)


class SCIONLinkAssignmentView(generic.ObjectView):
    queryset = models.SCIONLinkAssignment.objects.select_related('isd_as', 'isd_as__organization')
    template_name = 'netbox_scion/scionlinkassignment_detail.html'


class SCIONLinkAssignmentListView(generic.ObjectListView):
    queryset = models.SCIONLinkAssignment.objects.select_related('isd_as', 'isd_as__organization')
    table = tables.SCIONLinkAssignmentTable
    filterset = filtersets.SCIONLinkAssignmentFilterSet
    filterset_form = forms.SCIONLinkAssignmentFilterForm


class SCIONLinkAssignmentEditView(generic.ObjectEditView):
    queryset = models.SCIONLinkAssignment.objects.all()
    form = forms.SCIONLinkAssignmentForm
    template_name = 'netbox_scion/scionlinkassignment_edit.html'


class SCIONLinkAssignmentDeleteView(generic.ObjectDeleteView):
    queryset = models.SCIONLinkAssignment.objects.all()


class SCIONLinkAssignmentBulkDeleteView(generic.BulkDeleteView):
    queryset = models.SCIONLinkAssignment.objects.all()
    table = tables.SCIONLinkAssignmentTable


class SCIONLinkAssignmentChangeLogView(generic.ObjectChangeLogView):
    queryset = models.SCIONLinkAssignment.objects.all()
