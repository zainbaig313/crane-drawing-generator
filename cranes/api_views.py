"""
REST API Views for Crane Design operations and SVG generation.
"""
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CraneDesign
from .serializers import (
    CraneDesignListSerializer,
    CraneDesignDetailSerializer,
    CranePreviewSerializer,
)
from .services.drawing_generator import generate_crane_svg


class CraneDesignListCreateAPIView(APIView):
    """
    GET /api/designs/ - List all saved crane designs.
    POST /api/designs/ - Create and validate a new crane design.
    """
    def get(self, request):
        designs = CraneDesign.objects.all()
        serializer = CraneDesignListSerializer(designs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CraneDesignDetailSerializer(data=request.data)
        if serializer.is_valid():
            design = serializer.save()
            return Response(
                CraneDesignDetailSerializer(design).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CraneDesignDetailAPIView(APIView):
    """
    GET /api/designs/{id}/ - Retrieve design parameters.
    PUT /api/designs/{id}/ - Update design parameters.
    DELETE /api/designs/{id}/ - Delete design.
    """
    def get_object(self, pk):
        return get_object_or_404(CraneDesign, pk=pk)

    def get(self, request, pk):
        design = self.get_object(pk)
        serializer = CraneDesignDetailSerializer(design)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        design = self.get_object(pk)
        serializer = CraneDesignDetailSerializer(design, data=request.data)
        if serializer.is_valid():
            updated = serializer.save()
            return Response(
                CraneDesignDetailSerializer(updated).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        design = self.get_object(pk)
        serializer = CraneDesignDetailSerializer(design, data=request.data, partial=True)
        if serializer.is_valid():
            updated = serializer.save()
            return Response(
                CraneDesignDetailSerializer(updated).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        design = self.get_object(pk)
        design.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CraneDesignGenerateDrawingAPIView(APIView):
    """
    POST /api/designs/{id}/generate-drawing/
    Retrieves the stored design, generates dynamic SVG markup, and returns it.
    """
    def post(self, request, pk):
        design = get_object_or_404(CraneDesign, pk=pk)
        try:
            svg_content = design.generate_svg()
            
            # Check if raw SVG format is requested via query param ?format=svg
            if request.query_params.get('format') == 'svg':
                response = HttpResponse(svg_content, content_type='image/svg+xml')
                response['Content-Disposition'] = f'inline; filename="{design.design_name}.svg"'
                return response

            return Response({
                'design_id': design.id,
                'design_name': design.design_name,
                'crane_type': design.crane_type,
                'capacity': str(design.capacity),
                'span': design.span,
                'svg': svg_content,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f"Failed to generate drawing: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


class CranePreviewAPIView(APIView):
    """
    POST /api/designs/preview/
    Generates dynamic SVG markup on-the-fly without saving to the database.
    """
    def post(self, request):
        serializer = CranePreviewSerializer(data=request.data)
        if serializer.is_valid():
            cleaned = serializer.validated_data
            design_name = cleaned.get('design_name', 'Live Preview')
            try:
                svg_content = generate_crane_svg(cleaned, design_name=design_name)
                return Response({
                    'svg': svg_content,
                    'parameters': {k: str(v) for k, v in cleaned.items() if k != 'design_name'}
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {'error': f"Drawing error: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
