from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()


@register.inclusion_tag("materialize/forms/text.html")
def text_field(field, icon=None, **kwargs):
    if isinstance(field, str):
        kwargs["name"] = field
    else:
        kwargs["name"] = field.name
        kwargs["value"] = field.value
        kwargs["errors"] = field.errors

    if not "label" in kwargs:
        kwargs["label"] = kwargs["name"]

    return dict(icon=icon, **kwargs)


@register.simple_tag
def init_form():
    return mark_safe(
        """
<script>
  document.addEventListener('DOMContentLoaded', function() {
    M.updateTextFields();
  });
</script>
    """
    )
