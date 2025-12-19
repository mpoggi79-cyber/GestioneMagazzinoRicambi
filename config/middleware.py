"""
Middleware personalizzati per l'applicazione.
"""

from django.utils.cache import add_never_cache_headers


class NoCacheMiddleware:
    """
    Middleware che impedisce il caching delle pagine per utenti autenticati.
    Questo previene che il browser mostri informazioni di utenti precedenti
    quando si cambia login.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Aggiungi header no-cache solo per utenti autenticati
        if request.user.is_authenticated:
            add_never_cache_headers(response)
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response
