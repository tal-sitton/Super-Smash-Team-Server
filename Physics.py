from math import sqrt


def get_t(vi=None, vf=None, d=None, a=None):
    if None not in [vi, vf, a]:
        return (vf - vi) / a  # formula 3
    elif None not in [vi, vf, d]:
        return d * 2 / (vi + vf)  # formula 2
    elif None not in [vf, d, a]:
        return get_t(vi=get_vi(vf=vf, d=d, a=a), vf=vf, d=d, a=a)  # new formula
    elif None not in [vi, d, a]:
        return quadratic_equation(0.5 * a, vi, -d)  # formula 1


def get_d(vi=None, vf=None, t=None, a=None):
    if None not in [vi, t, a]:
        return (vi * t) + (0.5 * a * pow(t, 2))  # formula 1
    elif None not in [vi, vf, a]:
        return (pow(vf, 2) - pow(vi, 2)) / (2 * a)  # formula 2
    elif None not in [vi, vf, t]:
        return ((vi + vf) / 2) * t  # formula 3
    elif None not in [vf, t, a]:
        return get_d(vi=get_vi(vf=vf, t=t, a=a), vf=vf, t=t, a=a)  # new formula
    # elif None not in [t, a]:
    #     return a * pow(t, 2)


def get_vi(vf=None, d=None, t=None, a=None):
    if None not in [d, t, a]:
        return (d - 0.5 * a * pow(t, 2)) / t  # formula 1
    elif None not in [vf, d, a]:
        return sqrt(pow(vf, 2) - 2 * a * d)  # formula 2
    elif None not in [vf, t, a]:
        return vf - a * t  # formula 3
    elif None not in [vf, d, t]:
        return (2 * d) / t - vf  # formula 4


def get_vf(vi=None, d=None, t=None, a=None):
    if None not in [vi, d, a]:
        return sqrt(pow(vi, 2) + 2 * a * d)  # formula 2
    elif None not in [vi, t, a]:
        return vi + a * t  # formula 3
    elif None not in [vi, d, t]:
        return vi - (2 * d) / t  # formula 4
    elif None not in [d, t, a]:
        return get_vf(vi=get_vi(d, t, a), d=d, t=t, a=a)  # new formula


def get_a(vi=None, vf=None, d=None, t=None, m=None, f=None):
    if None not in [vi, d, t]:
        return -(2 * (d - vi * t)) / pow(t, 2)  # formula 1
    elif None not in [vi, vf, d]:
        return (pow(vf, 2) - pow(vi, 2)) / (2 * d)  # formula 2
    elif None not in [vi, vf, t]:
        return -(vf - vi) / t  # formula 3
    elif None not in [vf, d, t]:
        return get_a(vi=get_vi(vf=vf, d=d, t=t), vf=vf, d=d, t=t)  # new formula
    elif None not in [m, f]:
        return f / m


def get_f(m: float, a: float):
    return m * a


def get_m(a: float, f: float):
    return f / a


def quadratic_equation(a, b, c):
    solve1 = (-b + sqrt(pow(b, 2) - 4 * a * c)) / 2 * a
    solve2 = (-b - sqrt(pow(b, 2) - 4 * a * c)) / 2 * a
    return solve1, solve2
