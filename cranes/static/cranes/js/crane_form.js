/**
 * Vanilla JavaScript for Crane Design Form interactions and dynamic SVG live preview.
 */
document.addEventListener('DOMContentLoaded', () => {
    const craneForm = document.getElementById('crane-design-form');
    const previewContainer = document.getElementById('svg-preview-container');
    const livePreviewBtn = document.getElementById('btn-live-preview');
    const previewSpinner = document.getElementById('preview-spinner');
    const previewNotice = document.getElementById('preview-notice');

    if (!craneForm || !previewContainer) {
        return;
    }

    // Function to collect all 8 parameter values from form inputs
    function getFormData() {
        return {
            design_name: document.getElementById('id_design_name')?.value || 'Interactive Preview',
            capacity: document.getElementById('id_capacity')?.value || '',
            span: document.getElementById('id_span')?.value || '',
            lifting_height: document.getElementById('id_lifting_height')?.value || '',
            girder_depth: document.getElementById('id_girder_depth')?.value || '',
            end_carriage_height: document.getElementById('id_end_carriage_height')?.value || '',
            trolley_width: document.getElementById('id_trolley_width')?.value || '',
            hook_block_height: document.getElementById('id_hook_block_height')?.value || '',
            runway_rail_height: document.getElementById('id_runway_rail_height')?.value || '',
        };
    }

    // Function to clear inline error displays
    function clearFieldErrors() {
        document.querySelectorAll('.field-error-feedback').forEach(el => el.textContent = '');
        document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    }

    // Function to display field-specific validation errors returned from API
    function displayFieldErrors(errors) {
        clearFieldErrors();
        for (const [field, messages] of Object.entries(errors)) {
            const input = document.getElementById(`id_${field}`);
            const errorContainer = document.getElementById(`error_${field}`);
            if (input) {
                input.classList.add('is-invalid');
            }
            if (errorContainer) {
                errorContainer.textContent = Array.isArray(messages) ? messages.join(' ') : messages;
            }
        }
    }

    // Function to request live SVG preview from REST API
    async function updateLivePreview() {
        const payload = getFormData();
        if (previewSpinner) previewSpinner.classList.remove('d-none');
        if (previewNotice) previewNotice.textContent = 'Updating drawing...';

        try {
            const response = await fetch('/api/designs/preview/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (response.ok && data.svg) {
                clearFieldErrors();
                previewContainer.innerHTML = data.svg;
                if (previewNotice) {
                    previewNotice.className = 'text-success small fw-semibold';
                    previewNotice.innerHTML = '<i class="bi bi-check-circle-fill me-1"></i> Drawing updated dynamically from current parameters';
                }
            } else {
                displayFieldErrors(data);
                if (previewNotice) {
                    previewNotice.className = 'text-danger small fw-semibold';
                    previewNotice.innerHTML = '<i class="bi bi-exclamation-triangle-fill me-1"></i> Invalid parameters — check field errors below';
                }
            }
        } catch (err) {
            console.error('Error fetching live preview:', err);
            if (previewNotice) {
                previewNotice.className = 'text-warning small';
                previewNotice.textContent = 'Could not connect to preview server.';
            }
        } finally {
            if (previewSpinner) previewSpinner.classList.add('d-none');
        }
    }

    // CSRF helper
    function getCsrfToken() {
        const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }

    // Attach listeners
    if (livePreviewBtn) {
        livePreviewBtn.addEventListener('click', (e) => {
            e.preventDefault();
            updateLivePreview();
        });
    }

    // Debounced automatic preview on parameter changes
    let debounceTimer;
    const numericInputs = craneForm.querySelectorAll('input[type="number"], input[type="text"]');
    numericInputs.forEach(input => {
        input.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                updateLivePreview();
            }, 600);
        });
    });

    // Initial preview load if container is empty
    if (previewContainer.children.length === 0) {
        updateLivePreview();
    }
});
