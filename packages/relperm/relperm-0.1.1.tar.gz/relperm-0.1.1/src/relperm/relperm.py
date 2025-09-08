from math import pow, exp, log, nan
from decimal import Decimal


def dec(x):
    # Used to convert to decimal class whatever float number by first converting it to
    # a string
    return Decimal(str(x))


def pc_thomeer(sw, ift_res, cos_theta_res, swi_th, pce_th, g_th):
    if 0 <= sw < 1:
        term = dec(g_th) / dec(log((1 - sw) / (1 - swi_th)))
        pc_result = dec(pce_th * ift_res * cos_theta_res) / dec(exp(term))
    elif sw == 1:
        pc_result = dec(pce_th * ift_res * cos_theta_res)
    else:
        raise ValueError("Enter a water saturation value between 0 and 1")

    return float(pc_result)


def sw_thomeer(pc, ift_res, cos_theta_res, swi_th, pce_th, g_th):
    return min(
        1,
        max(
            0,
            1
            if pc / (ift_res * cos_theta_res) < pce_th
            else swi_th
            + (1 - swi_th)
            * dec(1 - exp(g_th / dec(log(pce_th / pc / (ift_res * cos_theta_res))))),
        ),
    )


def pc_brooks_corey(sw, ift_res, cos_theta_res, swi_bc, pce_bc, n_bc):
    """pc_brooksCorey(sw, ift_res, cos_theta_res, swi_bc, pce_bc, n_bc)"""
    if 0 <= sw <= 1:
        sw = dec(sw)
        ift_res = dec(ift_res)
        cos_theta_res = dec(cos_theta_res)
        swi_bc = dec(swi_bc)
        pce_bc = dec(pce_bc)
        n_bc = dec(n_bc)

        pc_result = dec(pce_bc * cos_theta_res * ift_res) / dec(
            pow(((sw - swi_bc) / (1 - swi_bc)), n_bc)
        )
    else:
        raise ValueError("Enter a water saturation value between 0 and 1")

    return float(pc_result)


def sw_brooks_corey(pc, ift_res, cos_theta_res, swi_bc, pce_bc, n_bc):
    return min(
        1,
        max(
            0,
            swi_bc
            + (1 - swi_bc)
            * dec(pow((pce_bc / (pc / (ift_res * cos_theta_res))), (1 / n_bc))),
        ),
    )


def sw_denormalized(swn, swirr, sorw):
    swn = dec(swn)
    swirr = dec(swirr)
    sorw = dec(sorw)

    return float(swn * (1 - swirr - sorw) + swirr)


def krw_corey(sw, swirr, sorw, krw_sorw, nw):
    sw = dec(sw)
    swirr = dec(swirr)
    sorw = dec(sorw)
    krw_sorw = dec(krw_sorw)
    nw = dec(nw)

    if sw < swirr:
        return nan
    elif sw > 1 - sorw:
        return nan
    else:
        return float(krw_sorw * dec(pow((sw - swirr) / (1 - swirr - sorw), nw)))


def krow_corey(sw, swirr, sorw, kro_swirr, now):
    sw = dec(sw)
    swirr = dec(swirr)
    sorw = dec(sorw)
    kro_swirr = dec(kro_swirr)

    if sw < swirr:
        return nan
    elif sw > 1 - sorw:
        return nan
    else:
        return float(kro_swirr * dec(pow((1 - sw - sorw) / (1 - swirr - sorw), now)))


def krg_corey(sg, sgc, swirr, sorg, krg_sg_max, ng):
    sg = dec(sg)
    sgc = dec(sgc)
    swirr = dec(swirr)
    sorg = dec(sorg)
    krg_sg_max = dec(krg_sg_max)
    ng = dec(ng)

    return float(
        krg_sg_max * dec(pow(((sg - min(sgc, sg)) / (1 - swirr - sorg - sgc)), ng))
    )


def krog_corey(sg, swirr, sorg, kro_sgi, nog):
    sg = dec(sg)
    swirr = dec(swirr)
    sorg = dec(sorg)
    kro_sgi = dec(kro_sgi)
    nog = dec(nog)

    return float(
        kro_sgi * dec(pow(((1 - sg - swirr - sorg) / (1 - swirr - sorg)), nog))
    )
