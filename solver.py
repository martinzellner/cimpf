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

    vmagnitude = abs(v)
    vangle = angle(v)

    # calculate selection vectors for the different bus types
    pv = model.pvNodeIds
    pq = model.pqNodeIds
    pvpq = pv
    for pqbus in pq:
        pvpq.append(pqbus)

    # check for initial optimium
    if check(v, y, s):
        print "Found optimum"

    # do the NR iterations
    iterationNr = 0
    while iterationNr < 10 and not check(v, y, s):
        iterationNr += 1

        # Calc Jacobian
        j = calculateJacobian(y, v, pv, pq, pvpq)

        # calculate power mismatch
        mis = dot(dot(y, v), v) - s
        realMis = real(mis)[ix_(pvpq)]
        imagMis = imag(mis)[ix_(pq)]
        x_mis = hstack([realMis, imagMis])

        #print "Mismatch is size " + str(shape(x_mis))
        # solve power flow and calculate new voltages
        vtemp = (-1) * linalg.solve(j, x_mis)

        # update voltages
        vangle_new = vtemp[0:len(pvpq)]
        vmagnitude_new = vtemp[len(pvpq):len(pvpq) + len(pq)]
        for i in range(0, len(vangle_new)):
            vangle[i] += vangle_new[i]
        for i in range(0, len(vmagnitude_new)):
            vmagnitude[i] += vmagnitude_new[i]

        v = vmagnitude * exp(1j*vangle)
        #print "Voltage after iteration " + str(iterationNr) + ": " + str(v)


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

    j11 = real(dS_dVa[ix_(pvpq, pvpq)])
    j12 = real(dS_dVm[ix_(pvpq, pq)])
    j21 = imag(dS_dVa[ix_(pq, pvpq)])
    j22 = imag(dS_dVm[ix_(pq, pq)])

    j1 = hstack([j11, j12])
    j2 = hstack([j21, j22])
    j = vstack([j1, j2])

    #print "Jacobian is size: " + str(shape(j))
    return j


def check(v, y, s):
    """
        check if the NR method already converged
    """

    # tolerance
    tol = 1.0e-6

    # check mismatch
    mis = dot(conjugate(dot(y, v)), v) - s

    realmis = real(mis)
    imagmis = imag(mis)

    xmis = concatenate((realmis, imagmis))

    norm_x_mis = linalg.norm(xmis, ord=inf)

    print "[SOLVER] Power mismatch: " + str(norm_x_mis)

    if (norm_x_mis < tol):
        return True
        print "[SOLVER] Power mismatch within tolerance"

    return False
