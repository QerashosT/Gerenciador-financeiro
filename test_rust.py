# test_rust.py
try:
    from rust_structures import Counter
    print("✓ Módulo Rust importado com sucesso!")
    
    # Teste funcional
    c = Counter()
    print(f"Count inicial: {c.get_count()}")
    c.increment()
    c.increment()
    print(f"Count após 2 incrementos: {c.get_count()}")
    print("✓ Módulo Rust funcionando perfeitamente!")
    
except ImportError as e:
    print(f"✗ Erro na importação: {e}")
    print("O módulo Rust não pôde ser carregado.")

input("Pressione Enter para continuar...")