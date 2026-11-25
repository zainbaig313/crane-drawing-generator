"""
Database models for Crane Design parametric storage.
"""
from decimal import Decimal
from django.db import models
from django.urls import reverse
from .services.drawing_generator import generate_crane_svg


class CraneDesign(models.Model):
    """
    Stores parametric configuration for single-girder overhead travelling cranes.
    Serves as the single source of truth from which SVG drawings are dynamically generated.
    """
    CRANE_TYPE_CHOICES = [
        ('single_girder_overhead', 'Single-Girder Overhead Travelling Crane'),
    ]

    design_name = models.CharField(
        max_length=150,
        help_text="User-defined project or design reference name"
    )
    crane_type = models.CharField(
        max_length=50,
        choices=CRANE_TYPE_CHOICES,
        default='single_girder_overhead',
        help_text="Type of crane configuration"
    )

    # Primary 8 Parameters
    capacity = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Safe Working Load (SWL) capacity in metric Tonnes"
    )
    span = models.PositiveIntegerField(
        help_text="Crane span (center-to-center of runway rails) in mm"
    )
    lifting_height = models.PositiveIntegerField(
        help_text="Maximum vertical lifting height hook travel in mm"
    )
    girder_depth = models.PositiveIntegerField(
        help_text="Main box/I-beam girder overall vertical depth in mm"
    )
    end_carriage_height = models.PositiveIntegerField(
        help_text="Vertical height of end trucks/carriages in mm"
    )
    trolley_width = models.PositiveIntegerField(
        help_text="Overall horizontal width of the hoist/trolley assembly in mm"
    )
    hook_block_height = models.PositiveIntegerField(
        help_text="Vertical height of the hook block assembly in mm"
    )
    runway_rail_height = models.PositiveIntegerField(
        help_text="Vertical height of the runway rails in mm"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Crane Design"
        verbose_name_plural = "Crane Designs"

    def __str__(self) -> str:
        return f"{self.design_name} ({self.capacity}t x {self.span}mm)"

    def get_absolute_url(self) -> str:
        return reverse('cranes:drawing_preview', kwargs={'pk': self.pk})

    def get_parameters_dict(self) -> dict:
        """
        Returns parameters dictionary suitable for validation and SVG generation.
        """
        return {
            'capacity': self.capacity,
            'span': self.span,
            'lifting_height': self.lifting_height,
            'girder_depth': self.girder_depth,
            'end_carriage_height': self.end_carriage_height,
            'trolley_width': self.trolley_width,
            'hook_block_height': self.hook_block_height,
            'runway_rail_height': self.runway_rail_height,
        }

    def generate_svg(self) -> str:
        """
        Dynamically generates the SVG front elevation for this design.
        """
        return generate_crane_svg(self.get_parameters_dict(), design_name=self.design_name)
