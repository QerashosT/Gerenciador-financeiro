# rust_structures/__init__.py
try:
    from .rust_structures import Counter
    __all__ = ['Counter']
except ImportError:
    print("Aviso: Módulo Rust não pôde ser carregado. Usando fallback Python.")
    
    # Fallback em Python
    class Counter:
        def __init__(self):
            self.count = 0
        
        def increment(self):
            self.count += 1
        
        def get_count(self):
            return self.count