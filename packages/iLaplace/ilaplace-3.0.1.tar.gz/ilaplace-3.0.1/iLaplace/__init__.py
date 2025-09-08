"""
inverse_laplace - A numerical inverse Laplace transform library.

This module provides efficient computation of the inverse Laplace transform using Talbot’s method,
suitable for engineering, physics, and mathematical applications.

Dependencies:
    - sympy
    - mpmath
"""

import sympy as sp
import mpmath
import math
from functools import lru_cache
from multiprocessing import Pool, cpu_count

t, s = sp.symbols('t s', real=True)

@lru_cache(maxsize=None)
def _get_lambdified_func(F):
    """Creates a callable function from a sympy expression."""
    return sp.lambdify(s, F, 'mpmath')

def inverse_laplace(F, t_val):
    """
    Performs the numerical inverse Laplace transform using Talbot's method.

    :param F: The Laplace-domain expression.
    :param t_val: The time value for evaluation.
    :return: The numerical result of the inverse transform.
    """
    if t_val <= 0:
        return 0.0
    F_func = _get_lambdified_func(F)
    return float(mpmath.invertlaplace(F_func, t_val, method='talbot'))

def pretty_ilaplace(X, prec=34):
    """
    Performs the symbolic inverse Laplace transform and formats the output.

    :param X: The Laplace-domain expression.
    :param prec: The precision for numerical evaluation.
    :return: A simplified symbolic expression of the inverse transform.
    """
    f = sp.inverse_laplace_transform(X, s, t)
    f = f.subs(sp.Heaviside(t), 1)
    f = f.subs(sp.cos(sp.I*t/2), sp.cosh(t/2))
    f = sp.simplify(f.subs(sp.cosh(t/2) - sp.sinh(t/2), sp.exp(-t/2)))
    f = sp.expand_trig(f)
    f = sp.simplify(f)
    f_num = sp.N(f, prec)
    terms = f_num.as_ordered_terms()
    output_terms = []
    for term in terms:
        term = sp.expand(term)
        if term.has(sp.exp):
            exp_factors = [e for e in term.atoms(sp.exp)]
            exp_factor = sp.prod(exp_factors)
            term_no_exp = term / exp_factor
        else:
            exp_factor = 1
            term_no_exp = term
        coeff_cos = sum(term_no_exp.coeff(func) for func in term_no_exp.atoms(sp.cos))
        coeff_sin = sum(term_no_exp.coeff(func) for func in term_no_exp.atoms(sp.sin))
        if math.isclose(coeff_cos, 0) and math.isclose(coeff_sin, 0):
            output_terms.append(term)
            continue
        trig_funcs = [f for f in term_no_exp.atoms(sp.Function) if isinstance(f, sp.sin) or isinstance(f, sp.cos)]
        omega = sp.N(trig_funcs[0].args[0] / t, prec) if trig_funcs else None
        C = sp.N(coeff_cos, prec)
        k = sp.N(coeff_sin / C, prec) if not math.isclose(C, 0) else 1.0
        standardized = C * exp_factor * (sp.cos(omega * t) + k * sp.sin(omega * t)) if not math.isclose(C, 0) else coeff_sin * exp_factor * sp.sin(omega*t)
        output_terms.append(standardized)
    final_expr = sp.Add(*output_terms)
    return final_expr


class iLaplace:
    """
    A class-based interface for the iLaplace library.
    """
    def __init__(self):
        self.inverse_laplace = inverse_laplace
        self.pretty_ilaplace = pretty_ilaplace

# Create an instance of the class to expose it to the user.
Fu = iLaplace()

__all__ = ['inverse_laplace', 'pretty_ilaplace', 'Fu']