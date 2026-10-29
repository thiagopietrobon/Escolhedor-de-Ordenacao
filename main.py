"""Demonstração interativa do seletor automático no terminal."""
from seletor import escolher, ordenar


def ler_lista() -> list[int]:
    texto = input("Digite inteiros separados por espaço: ").strip()
    if not texto:
        return []
    try:
        return [int(parte) for parte in texto.split()]
    except ValueError as erro:
        raise ValueError("Entrada inválida: informe somente números inteiros.") from erro


def main() -> None:
    while True:
        print("\n=== Seletor automático de ordenação ===")
        print("1. Informar uma lista")
        print("2. Usar uma lista de demonstração")
        print("0. Sair")
        opcao = input("Escolha: ").strip()
        if opcao == "0":
            print("Encerrando.")
            return
        if opcao == "1":
            try:
                valores = ler_lista()
            except ValueError as erro:
                print(erro)
                continue
        elif opcao == "2":
            valores = [17, -4, 9, 9, 0, 31, -12, 5, 1]
            print(f"Lista de demonstração: {valores}")
        else:
            print("Opção inválida.")
            continue
        metodo = escolher(valores)
        resultado = ordenar(valores)
        print(f"Método recomendado: {metodo}")
        print(f"Resultado: {resultado}")
        print(f"Entrada preservada: {valores}")


if __name__ == "__main__":
    main()
