from numpy import *


def solve(model):
    """
        solves the simulation model using newton raphson
    """

    # calculate power injection vector
    s = model.s_g - model.s_d

    # create working variables
    y = model.y
    v = transpose(model.v)

    # calculate selection vectors for the different bus types
    pv = zeros(model.numberOfBusses, dtype=int)
    pq = zeros(model.numberOfBusses, dtype=int)
    pvpq = zeros(model.numberOfBusses, dtype=int)
    for i in model.pvNodeIds:
        pv[i] = 1
        pvpq[i] = 1
    for i in model.pqNodeIds:
        pq[i] = 1
        pvpq[i] = 1

    # check for initial optimium
    if check(v, y, s):
        print "Found optimum"

    # do the NR iterations
    iterationNr = 0
    while iterationNr < 20 and not check(v, y, s):
        iterationNr += 1

        # Calc Jacobian
        j = calculateJacobian(y, v, pv, pq, pvpq)

        # calculate power mismatch
        mis = dot(dot(y, v), v) - s
        x_mis = concatenate((real(mis), imag(mis)))

        # solve power flow and calculate new voltages
        v = complex((-1) * linalg.solve(j, x_mis))


        print v


def calculateJacobian(y, v, pv, pq, pvpq):
    """
        calculates the jacobian matrix for the NR method
    """

    # dS_dVm
    i = dot(y, v)
    diagV = diag(v)
    diagVNorm = diag(v / absolute(v))
    diagIconj = conjugate(diag(i))

    #  diag(V) (Y diag(V / ||V||))* +  diag(I)* diag(V / ||V||)
    dS_dVm = dot(diagV, conjugate(dot(y, diagVNorm))) + \
        dot(diagIconj, diagVNorm)
    # calculate_dS_dVa
    dS_dVa = complex(
        0, 1) * dot(diagV, conjugate(diag(i) - dot(y, diag(v))))

    # FIXME
    j11 = real(dS_dVa[pvpq, pvpq])
    j12 = real(dS_dVm[pvpq, pq])
    j21 = imag(dS_dVa[pq, pvpq])
    j22 = imag(dS_dVm[pq, pq])

    j1 = append(j11, j12)
    print j1
    j2 = append(j21, j22)
    print j2
    j = concatenate((j1, j2), 1)

    return j


def check(v, y, s):
    """
        check if the NR method already converged
    """

    # tolerance
    tol = 1.0e-6

    # check mismatch
    mis = dot(dot(y, v), v) - s

    realmis = real(mis)
    imagmis = imag(mis)

    xmis = concatenate((realmis, imagmis))

    norm_x_mis = linalg.norm(xmis, ord=inf)

    print "[SOLVER] Power mismatch: " + str(norm_x_mis)

    if (norm_x_mis < tol):
        return True
        print "[SOLVER] Power mismatch within tolerance"

    return False
