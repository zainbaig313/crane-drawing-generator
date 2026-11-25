"""
Django REST Framework serializers for CraneDesign model and parametric validation.
"""
from rest_framework import serializers
from .models import CraneDesign
from .services.validation import validate_crane_parameters


class CraneDesignListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing designs on dashboard or API index.
    """
    crane_type_display = serializers.CharField(source='get_crane_type_display', read_only=True)

    class Meta:
        model = CraneDesign
        fields = [
            'id',
            'design_name',
            'crane_type',
            'crane_type_display',
            'capacity',
            'span',
            'created_at',
            'updated_at',
        ]


class CraneDesignDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for creating, retrieving, and updating CraneDesign records.
    Leverages centralized validation service for domain rules.
    """
    crane_type_display = serializers.CharField(source='get_crane_type_display', read_only=True)

    class Meta:
        model = CraneDesign
        fields = [
            'id',
            'design_name',
            'crane_type',
            'crane_type_display',
            'capacity',
            'span',
            'lifting_height',
            'girder_depth',
            'end_carriage_height',
            'trolley_width',
            'hook_block_height',
            'runway_rail_height',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        """
        Applies centralized field-level and cross-field validation rules.
        """
        # Ensure design_name is provided and not just whitespace
        design_name = attrs.get('design_name')
        if design_name is not None and not str(design_name).strip():
            raise serializers.ValidationError({'design_name': ['Design name cannot be blank.']})

        # Check required parameters for validation
        # In partial updates, merge existing instance values
        data_to_validate = {}
        for param in [
            'capacity', 'span', 'lifting_height', 'girder_depth',
            'end_carriage_height', 'trolley_width', 'hook_block_height', 'runway_rail_height'
        ]:
            if param in attrs:
                data_to_validate[param] = attrs[param]
            elif self.instance:
                data_to_validate[param] = getattr(self.instance, param)
            else:
                data_to_validate[param] = None

        cleaned, errors = validate_crane_parameters(data_to_validate)
        if errors:
            raise serializers.ValidationError(errors)

        # Update attrs with cleaned types if necessary
        for k, v in cleaned.items():
            if k in attrs:
                attrs[k] = v

        return attrs


class CranePreviewSerializer(serializers.Serializer):
    """
    Serializer for generating SVG previews on-the-fly without saving to the database.
    """
    design_name = serializers.CharField(required=False, default="Preview Design", allow_blank=True)
    capacity = serializers.CharField()
    span = serializers.CharField()
    lifting_height = serializers.CharField()
    girder_depth = serializers.CharField()
    end_carriage_height = serializers.CharField()
    trolley_width = serializers.CharField()
    hook_block_height = serializers.CharField()
    runway_rail_height = serializers.CharField()

    def validate(self, attrs):
        cleaned, errors = validate_crane_parameters(attrs)
        if errors:
            raise serializers.ValidationError(errors)
        attrs.update(cleaned)
        return attrs
