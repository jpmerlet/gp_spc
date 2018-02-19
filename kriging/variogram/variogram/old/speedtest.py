# import numpy
# import timer
# import math
#
# @timer.timeit
# def raizmath(a,n):
#     for i in range(n):
#         x = math.sqrt(a)
#
# @timer.timeit
# def suma(a,b,n):
#     for i in range(n):
#         x = a + b
#
# @timer.timeit
# def comparavalores(a,b,n):
#     for i in range(n):
#         x = a < b
#
# @timer.timeit
# def alcuadrado(a,n):
#     for i in range(n):
#         x = a ** 2
# @timer.timeit
# def dividir(a,b,n):
#     for i in range(n):
#         x = a / b
#
# @timer.timeit
# def raiznumpy(a,n):
#     for i in range(n):
#         x = numpy.sqrt(a)
#
#
# @timer.timeit
# def expmath(a, n):
#     for i in range(n):
#         x = math.exp(a)
#
#
# @timer.timeit
# def expnumpy(a, n):
#     for i in range(n):
#         x = numpy.exp(a)
#
#
# @timer.timeit
# def comprension(a, n):
#     x = [a * 1.5 * i for i in range(n)]
#     y = [a * 3 * i for i in range(n)]
#     z = [a * 5 * i for i in range(n)]
#     aa = [a * 2.4 * i for i in range(n)]
#     bb = [a * 0.2 * i for i in range(n)]
#
# @timer.timeit
# def nocomp(a, n):
#
#     x = []
#     y = []
#     z = []
#     aa = []
#     bb = []
#
#     for i in range(n):
#         x.append(a * 1.5 * i)
#         y.append(a * 3 * i)
#         z.append(a * 5 * i)
#         aa.append(a * 2.4 * i)
#         bb.append(a * 0.2 * i)
#
# @timer.timeit
# def numpycos(a, n):
#     for i in range(n):
#         x = numpy.cos(a)
#
# @timer.timeit
# def mathcos(a, n):
#
#     for i in range(n):
#         x = math.cos(a)
#
# n = 10000000
# a = 13
# b = 52.5
#
#
# # suma(a, b, n)
# # comparavalores(a, b, n)
# # alcuadrado(a, n)
# # dividir(a, b, n)
# # raiznumpy(a, n)
# # raizmath(a, n)
# # expmath(a, n)
# # expnumpy(a, n)
# # comprension(a, n)
# # nocomp(a, n)
# numpycos(a, n)
# mathcos(a, n)
