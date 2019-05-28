import numpy as np


def nlms(u, d, m, step, eps=0.001, leak=0, init_coeffs=None, n=None,
         return_coeffs=False, adaptive_step=0):
    """
    Perform normalized least-mean-squares (NLMS) adaptive filtering on u to
    minimize error given by e=d-y, where y is the output of the adaptive
    filter.

    Parameters
    ----------
    u : array-like
        One-dimensional filter input.
    d : array-like
        One-dimensional desired signal, i.e., the output of the unknown FIR
        system which the adaptive filter should identify. Must have length >=
        len(u), or N+M-1 if number of iterations are limited (via the N
        parameter).
    m : int
        Desired number of filter taps (desired filter order + 1), must be
        non-negative.
    step : float
        Step size of the algorithm, must be non-negative.

    Optional Parameters
    -------------------
    eps : float
        Regularization factor to avoid numerical issues when power of input
        is close to zero. Defaults to 0.001. Must be non-negative.
    leak : float
        Leakage factor, must be equal to or greater than zero and smaller than
        one. When greater than zero a leaky LMS filter is used. Defaults to 0,
        i.e., no leakage.
    init_coeffs : array-like
        Initial filter coefficients to use. Should match desired number of
        filter taps, defaults to zeros.
    n : int
        Number of iterations to run. Must be less than or equal to len(u)-M+1.
        Defaults to len(u)-M+1.
    return_coeffs : boolean
        If true, will return all filter coefficients for every iteration in an
        N x M matrix. Does not include the initial coefficients. If false, only
        the latest coefficients in a vector of length M is returned. Defaults
        to false.
    adaptive_step : boolean
        If true, it will change step value for every iteration according to
        variance of u signal and filter order m. If false, only passed step
        value used

    Returns
    -------
    y : numpy.array
        Output values of LMS filter, array of length N.
    e : numpy.array
        Error signal, i.e, d-y. Array of length N.
    w : numpy.array
        Final filter coefficients in array of length M if returnCoeffs is
        False. NxM array containing all filter coefficients for all iterations
        otherwise.

    Raises
    ------
    TypeError
        If number of filter taps M is not type integer, number of iterations N
        is not type integer, or leakage leak is not type float/int.
    ValueError
        If number of iterations N is greater than len(u)-M, number of filter
        taps M is negative, or if step-size or leakage is outside specified
        range.

    """

    def check_desired_signal(qd, qn, qm):
        if len(qd) < qn + qm - 1:
            raise ValueError('Desired signal must be >= N+M-1 or len(u)')

    def check_num_taps(qm):
        if type(qm) is not int:
            raise TypeError('Number of filter taps must be type integer')
        elif qm <= 0:
            raise ValueError('Number of filter taps must be greater than 0')

    def check_init_coeffs(qc, qm):
        if len(qc) != qm:
            err = 'Length of initial filter coefficients must match filter order'
            raise ValueError(err)

    def check_iter(qn, maxlen):
        if type(qn) is not int:
            raise TypeError('Number of iterations must be type integer')
        elif qn > maxlen:
            raise ValueError('Number of iterations must not exceed len(u)-M+1')
        elif qn <= 0:
            err = 'Number of iterations must be larger than zero, please increase\
     number of iterations N or length of input u'
            raise ValueError(err)

    def check_step(qstep):
        if type(qstep) is not float and type(qstep) is not int:
            raise TypeError('Step must be type float (or integer)')
        elif qstep < 0:
            raise ValueError('Step size must non-negative')

    def check_leakage(qleak):
        if type(qleak) is not float and type(qleak) is not int:
            raise TypeError('Leakage must be type float (or integer)')
        elif qleak > 1 or qleak < 0:
            raise ValueError('0 <= Leakage <= 1 must be satisfied')

    def check_reg_factor(qeps):
        if type(qeps) is not float and type(qeps) is not int:
            err = 'Regularization (eps) must be type float (or integer)'
            raise ValueError(err)
        elif qeps < 0:
            raise ValueError('Regularization (eps) must non-negative')

    # Check epsilon
    check_reg_factor(eps)
    # Num taps check
    check_num_taps(m)
    # Max iteration check
    if n is None:
        n = len(u)-m+1
    check_iter(n, len(u) - m + 1)
    # Check len(d)
    check_desired_signal(d, n, m)
    # Step check
    check_step(step)
    # Leakage check
    check_leakage(leak)
    # Init. coeffs check
    if init_coeffs is None:
        init_coeffs = np.zeros(m)
    else:
        check_init_coeffs(init_coeffs, m)

    # Initialization
    y = np.zeros(n)  # Filter output
    e = np.zeros(n)  # Error signal
    w = init_coeffs  # Initial filter coeffs
    leakstep = (1 - step*leak)
    wopt = np.zeros((n, m))  # Matrix to hold coeffs for each iteration

    # Perform filtering
    for n in range(n):
        x = np.flipud(u[n:n+m])  # Slice to get view of M latest datapoints
        y[n] = np.dot(x, w)
        e[n] = d[n+m-1] - y[n]

        norm_factor = 1./(np.dot(x, x) + eps)

        # Miguel: adaptive step :)
        if adaptive_step:
            # adaptive step
            step = min(1, 0.0001 / (m * np.var(x)))
            # step = max(step, 0.1)
            # print("n: " + str(n) +", sigma: " + str(np.var(x)) + ", step: " + str(step))

        w = leakstep * w + step * norm_factor * x * e[n]
        y[n] = np.dot(x, w)
        if return_coeffs:
            wopt[n] = w

    if return_coeffs:
        w = wopt

    return y, e, w
