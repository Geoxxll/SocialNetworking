# templatetags/custom_filters.py
from django import template
import base64

register = template.Library()

@register.filter
def base64_image(value, content_type):
    """
    Prepares a base64-encoded image for direct embedding in an HTML image tag.
    :param value: The base64-encoded image data.
    :param content_type: The MIME type of the image (e.g., 'image/jpeg').
    :return: A data URI string ready for embedding.
    """
    if value is None:
        # Option 1: Return an empty string if no image data is present
        return ''
        # Option 2: Return a placeholder image (ensure you have a suitable placeholder URL)
        # return 'path/to/your/placeholder/image.png'
    if isinstance(value, bytes):
        # If value is bytes, decode to string
        value = value.decode('utf-8')
        
    prefix = f'data:{content_type};base64,'
    if not value.startswith(prefix):
        return prefix + value
    return value
