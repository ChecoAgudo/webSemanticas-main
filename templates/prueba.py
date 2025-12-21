"""Utilidades de ejemplo: factorial con explicación paso a paso."""


def factorial(n: int) -> int:
	"""Calcula n! validando que n sea entero no negativo."""
	if not isinstance(n, int):
		raise TypeError("n debe ser un entero")
	if n < 0:
		raise ValueError("n debe ser >= 0")
	resultado = 1
	for i in range(2, n + 1):
		resultado *= i
	return resultado


def explicar_factorial(n: int):
	"""Devuelve (resultado, pasos) donde pasos es una lista de strings explicando el cálculo."""
	res = factorial(n)
	pasos = []
	acumulado = 1
	pasos.append(f"Partimos de 1 (neutro multiplicativo)")
	for i in range(2, n + 1):
		anterior = acumulado
		acumulado *= i
		pasos.append(f"Multiplico {anterior} x {i} = {acumulado}")
	pasos.append(f"Resultado final: {res}")
	return res, pasos


if __name__ == "__main__":
	numero = 5
	resultado, pasos = explicar_factorial(numero)
	print(f"Factorial de {numero} = {resultado}")
	print("Pasos:")
	for paso in pasos:
		print(" - " + paso)
