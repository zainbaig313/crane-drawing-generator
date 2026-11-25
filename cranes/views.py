"""
Frontend template views for crane generator.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, Http404
from .models import CraneDesign
from .services.validation import (
    CRANE_VALIDATION_CONFIG,
    validate_crane_parameters,
)


def dashboard(request):
    """
    Dashboard showing list of previously saved crane designs and quick summary metrics.
    """
    designs = CraneDesign.objects.all()
    context = {
        'designs': designs,
        'total_designs': designs.count(),
        'validation_config': CRANE_VALIDATION_CONFIG,
    }
    return render(request, 'cranes/dashboard.html', context)


def create_design(request):
    """
    Page to enter parameters, live preview drawing, and save a new crane design.
    """
    errors = {}
    form_data = {
        'design_name': 'Workshop Crane V1',
        'capacity': '10.0',
        'span': '25000',
        'lifting_height': '7900',
        'girder_depth': '1200',
        'end_carriage_height': '500',
        'trolley_width': '1000',
        'hook_block_height': '700',
        'runway_rail_height': '100',
    }

    if request.method == 'POST':
        form_data = {
            'design_name': request.POST.get('design_name', '').strip(),
            'capacity': request.POST.get('capacity', '').strip(),
            'span': request.POST.get('span', '').strip(),
            'lifting_height': request.POST.get('lifting_height', '').strip(),
            'girder_depth': request.POST.get('girder_depth', '').strip(),
            'end_carriage_height': request.POST.get('end_carriage_height', '').strip(),
            'trolley_width': request.POST.get('trolley_width', '').strip(),
            'hook_block_height': request.POST.get('hook_block_height', '').strip(),
            'runway_rail_height': request.POST.get('runway_rail_height', '').strip(),
        }

        if not form_data['design_name']:
            errors['design_name'] = ['Design name is required.']

        cleaned, val_errors = validate_crane_parameters(form_data)
        if val_errors:
            errors.update(val_errors)

        if not errors:
            design = CraneDesign.objects.create(
                design_name=form_data['design_name'],
                capacity=cleaned['capacity'],
                span=cleaned['span'],
                lifting_height=cleaned['lifting_height'],
                girder_depth=cleaned['girder_depth'],
                end_carriage_height=cleaned['end_carriage_height'],
                trolley_width=cleaned['trolley_width'],
                hook_block_height=cleaned['hook_block_height'],
                runway_rail_height=cleaned['runway_rail_height'],
            )
            messages.success(request, f"Crane design '{design.design_name}' successfully created and saved!")
            return redirect('cranes:drawing_preview', pk=design.pk)

    context = {
        'form_data': form_data,
        'errors': errors,
        'validation_config': CRANE_VALIDATION_CONFIG,
    }
    return render(request, 'cranes/create_design.html', context)


def drawing_preview(request, pk):
    """
    Full view of generated SVG drawing, parameter specification, and download actions.
    """
    design = get_object_or_404(CraneDesign, pk=pk)
    try:
        svg_content = design.generate_svg()
    except Exception as e:
        messages.error(request, f"Could not render drawing: {str(e)}")
        svg_content = f"<div class='alert alert-danger'>Drawing Generation Error: {str(e)}</div>"

    context = {
        'design': design,
        'svg_content': svg_content,
        'validation_config': CRANE_VALIDATION_CONFIG,
    }
    return render(request, 'cranes/drawing_preview.html', context)


def design_detail(request, pk):
    """
    View stored design, edit parameters, and re-generate drawing.
    """
    design = get_object_or_404(CraneDesign, pk=pk)
    errors = {}
    form_data = {
        'design_name': design.design_name,
        'capacity': str(design.capacity),
        'span': str(design.span),
        'lifting_height': str(design.lifting_height),
        'girder_depth': str(design.girder_depth),
        'end_carriage_height': str(design.end_carriage_height),
        'trolley_width': str(design.trolley_width),
        'hook_block_height': str(design.hook_block_height),
        'runway_rail_height': str(design.runway_rail_height),
    }

    if request.method == 'POST':
        form_data = {
            'design_name': request.POST.get('design_name', '').strip(),
            'capacity': request.POST.get('capacity', '').strip(),
            'span': request.POST.get('span', '').strip(),
            'lifting_height': request.POST.get('lifting_height', '').strip(),
            'girder_depth': request.POST.get('girder_depth', '').strip(),
            'end_carriage_height': request.POST.get('end_carriage_height', '').strip(),
            'trolley_width': request.POST.get('trolley_width', '').strip(),
            'hook_block_height': request.POST.get('hook_block_height', '').strip(),
            'runway_rail_height': request.POST.get('runway_rail_height', '').strip(),
        }

        if not form_data['design_name']:
            errors['design_name'] = ['Design name is required.']

        cleaned, val_errors = validate_crane_parameters(form_data)
        if val_errors:
            errors.update(val_errors)

        if not errors:
            design.design_name = form_data['design_name']
            design.capacity = cleaned['capacity']
            design.span = cleaned['span']
            design.lifting_height = cleaned['lifting_height']
            design.girder_depth = cleaned['girder_depth']
            design.end_carriage_height = cleaned['end_carriage_height']
            design.trolley_width = cleaned['trolley_width']
            design.hook_block_height = cleaned['hook_block_height']
            design.runway_rail_height = cleaned['runway_rail_height']
            design.save()

            messages.success(request, f"Crane design '{design.design_name}' updated successfully!")
            return redirect('cranes:drawing_preview', pk=design.pk)

    # Generate current SVG for reference on edit page
    try:
        svg_content = design.generate_svg()
    except Exception:
        svg_content = ""

    context = {
        'design': design,
        'form_data': form_data,
        'errors': errors,
        'svg_content': svg_content,
        'validation_config': CRANE_VALIDATION_CONFIG,
    }
    return render(request, 'cranes/design_detail.html', context)


def delete_design(request, pk):
    """
    Deletes an existing crane design.
    """
    design = get_object_or_404(CraneDesign, pk=pk)
    if request.method == 'POST':
        name = design.design_name
        design.delete()
        messages.info(request, f"Crane design '{name}' has been deleted.")
    return redirect('cranes:dashboard')


def download_svg(request, pk):
    """
    Direct endpoint to download the generated SVG file.
    """
    design = get_object_or_404(CraneDesign, pk=pk)
    svg_content = design.generate_svg()
    filename = f"{design.design_name.replace(' ', '_').lower()}_front_elevation.svg"
    response = HttpResponse(svg_content, content_type='image/svg+xml')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
