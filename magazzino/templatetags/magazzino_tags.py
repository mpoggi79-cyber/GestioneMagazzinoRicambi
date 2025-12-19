"""
Template tags personalizzati per l'ordinamento delle tabelle
"""
from django import template
from django.utils.http import urlencode
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def order_link(context, field, label):
    """
    Genera un link per ordinare una colonna.
    Usage: {% order_link 'nome_campo' 'Etichetta' %}
    """
    request = context['request']
    current_order = request.GET.get('order', '')
    params = request.GET.copy()
    
    # Determina il nuovo ordinamento
    if current_order == field:
        # Se già ordinato crescente, inverti a decrescente
        new_order = f'-{field}'
        icon = '<i class="fas fa-sort-up"></i>'
    elif current_order == f'-{field}':
        # Se già ordinato decrescente, torna a crescente
        new_order = field
        icon = '<i class="fas fa-sort-down"></i>'
    else:
        # Non ordinato, imposta crescente
        new_order = field
        icon = '<i class="fas fa-sort text-muted"></i>'
    
    params['order'] = new_order
    
    # Mantieni la paginazione alla prima pagina quando si ordina
    if 'page' in params:
        params['page'] = '1'
    
    url = f"?{params.urlencode()}"
    
    return mark_safe(f'<a href="{url}" class="text-decoration-none text-dark">{label} {icon}</a>')


@register.filter
def get_sort_icon(current_order, field):
    """
    Restituisce l'icona di ordinamento appropriata.
    Usage: {{ current_order|get_sort_icon:'nome_campo' }}
    """
    if current_order == field:
        return '<i class="fas fa-sort-up"></i>'
    elif current_order == f'-{field}':
        return '<i class="fas fa-sort-down"></i>'
    else:
        return '<i class="fas fa-sort text-muted"></i>'
