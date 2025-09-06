import multiprocessing as mp
import warnings
from itertools import product
from typing import List, Tuple

import numpy as np
from scipy.stats import gamma, hypergeom
from tqdm import tqdm


def _exact_law(data: Tuple) -> Tuple[float, float]:
    """
    Private function to calculate the combined p-value and probability mass function (pmf) using the exact law method of combination for one combination.

    Parameters:
    -----------
    data (Tuple): A tuple containing the following elements:

        * indexs (list): A list of indices selecting the combination.
        * masse (list): A list of lists representing the probability masses for each hypergeometric distribution.
        * pvals (list): A list of lists containg all p-values (support) of each table.
        * tau (float): The value of the truncation.

    Returns:
    --------
    Tuple[float, float]: A tuple containing the combined p-value (rvs) and the probability mass function (pmf).
    """

    indexs, masse, pvals, tau = data

    proba_tuple = 1.0
    combined = 0.0
    n = 0

    for i, j in enumerate(indexs):
        proba_tuple *= masse[i][j]
        if pvals[i][j] <= tau:
            combined += np.log(pvals[i][j])
            n += 1
    if tau != 1:
        combined = -2 * combined + 2 * n * np.log(tau)
    else:
        combined = -2 * combined

    if tau == 1 or combined >= 0:
        rvs = combined
    else:
        rvs = 0
    pmf = proba_tuple
    return (rvs, pmf)


def explicite_combination(
    list_params: List[List[int]],
    list_pvals: List[float],
    type: str,
    tau=None,
    jobs=None,
    verbose=False,
    distribution=False,
    all_value=False,
):
    """
    Compute explicit law of combination of p-values.

    Parameters
    ----------
    list_params : List[List[int]]
        A list of parameter lists. Each parameter list contains three integers [N, K, n] indicating the data in each stratum (length of List = number of stratum). `N` is the population size, `K` is the number of positive outcome in both categories (with and without the feature), and `n` is the number of both outcomes (positive and negative) with the feature. These three integers are also the parameters of the hypergeometric distribution of each stratum that describes the probability of observing the data
    list_pvals : List[float]
        A list of p-values of each stratum. These p-values are the result of Fisher's exact test for each stratum.
    type : str
        The type of combination. Can be either "under" or "over".
    tau : float, optional
        The threshold value for combining p-values. Defaults to None.
    jobs : int, optional
        The number of parallel jobs to run. Defaults to None.
    verbose : bool, optional
        Whether to print verbose output. Defaults to False.
    distribution : bool, optional
        Whether to return the distribution of combined p-values. Defaults to False.
    all_value : bool, optional
        Whether to return all values of combined p-values. Defaults to False.

    Returns
    -------
    float or tuple
        If `distribution` is True, returns a tuple of array describing exact low of combination through the random variable and survival value (y, P(Y>y)).
        If `all_value` is True, rounded strategy is not used.
        Else, returns the combined p-value.

    Notes
    -----
    This function computes the explicit combination of p-values based on the given parameters.
    The combination can be either "under" or "over" depending on the `type` parameter.
    The threshold value `tau` is used to truncate the combination of p-values.
    The `jobs` parameter controls the number of parallel jobs to run for faster computation.
    Setting `verbose` to True will print a progress bar of the computation.
    Setting `distribution` to True will return the distribution of combined p-values.
    Setting `all_value` to True will return all values of combined p-values without rounded strategy.

    Examples
    --------
    >>> list_params = [[20, 5, 10], [25, 8, 15], [18, 12, 6]]
    >>> list_pvals = [0.15170278637770898, 0.12810484709798212, 0.29427925016160306]
    >>> type = "under"
    >>> explicite_combinaison(list_params, list_pvals, type)
    0.028607013097391977

    """
    if not tau:
        tau = 1

    # Creation of vector of probability
    pvals = []
    masse = []
    max_val = 0
    for p in list_params:
        p = np.int64(p)
        h = hypergeom(p[0], p[1], p[2])
        sup_max = np.min([p[1], p[2]])
        sup_min = np.max([0, p[1] + p[2] - p[0]])
        if "under" in type:
            pvals.append(h.cdf(range(sup_min, sup_max + 1)))
            if (pval_min := h.cdf(sup_min)) < tau and 0.0 not in pvals[-1]:
                max_val += np.log(pval_min / tau)
        elif "over" in type:
            pvals.append(h.sf(range(sup_min - 1, sup_max)))
            if (pval_min := h.sf(sup_max - 1)) < tau and 0.0 not in pvals[-1]:
                max_val += np.log(pval_min / tau)
        else:
            raise ValueError("type must be either 'under' or 'over'")
        if 0.0 in pvals[-1]:
            warnings.warn(
                f"Exact calculation is used, the smallest reachable p-value is below the float value closest to zero ({np.nextafter(0,1)}), and has been converted to it, no particular impact on the result."
            )
            pvals[-1] = np.array(
                [p if p != 0 else np.nextafter(0, 1) for p in pvals[-1]]
            )
            max_val += np.log(np.nextafter(0, 1) / tau)
        masse.append([h.pmf(k) for k in range(sup_min, sup_max + 1)])
    max_val = -2 * max_val
    round_dec = 16 - len(str(int(max_val))) - 3
    pvals = np.array(pvals, dtype=object)
    masse = np.array(masse, dtype=object)
    size_pv = [len(e) for e in masse]
    if verbose:
        print(size_pv, "size", np.prod(size_pv), "max supp", np.max(size_pv))

    cartesian_product = product(*[range(k) for k in size_pv])

    list_rvs = []
    list_pmf = []
    if mp.current_process().name == "MainProcess":
        with mp.Pool(jobs) as pool:
            list_rvs, list_pmf = zip(
                *tqdm(
                    pool.imap_unordered(
                        _exact_law,
                        ((indexs, masse, pvals, tau) for indexs in cartesian_product),
                        chunksize=1000,
                    ),
                    total=np.prod(size_pv),
                    disable=not verbose,
                )
            )
    else:
        list_rvs, list_pmf = zip(
            *map(
                _exact_law,
                ((indexs, masse, pvals, tau) for indexs in cartesian_product),
            )
        )

    list_rvs = np.array(list_rvs)
    list_pmf = np.array(list_pmf)
    list_pmf = list_pmf[np.argsort(list_rvs)]
    list_rvs = np.sort(list_rvs)
    list_sf = np.cumsum(list_pmf[::-1])[::-1]

    if all_value:
        rvs = list_rvs
        sf = list_sf
        dict_comb_pval = {k: v for k, v in zip(list_rvs, list_sf)}
    else:
        dict_comb_pval = {
            k: v
            for k, v in zip(
                reversed(np.round(list_rvs, decimals=round_dec)), reversed(list_sf)
            )
        }
        rvs = np.array(list(dict_comb_pval.keys()))
        sf = np.array(list(dict_comb_pval.values()))

    if distribution:
        if all_value:
            return rvs, sf
        else:
            return rvs[::-1], sf[::-1]
    else:
        comb = -2 * np.sum(np.log([p / tau if p <= tau else 1 for p in list_pvals]))
        pval_cb = dict_comb_pval.get(
            comb,
            dict_comb_pval[min(dict_comb_pval.keys(), key=lambda k: abs(k - comb))],
        )

        # free memory
        del pvals
        del masse
        del list_rvs
        del list_pmf
        del list_sf
        del dict_comb_pval
        del cartesian_product

        return pval_cb


def moment_matching_estimator(
    params,
    type,
    list_pvals=None,
    comb_pvals=None,
    tau=None,
    moment=2,
    get_params=False,
    get_moment=False,
):
    """
    Estimate the parameters of a gamma distribution using the method of moments.

    Parameters
    ----------
    params : list of tuples
        List of tuples containing the parameters of the hypergeometric distribution for each stratum.
        Each tuple should contain three values: (N, K, n), where N is the population size, K is the number of successes in the population, and n is the sample size.
    type : str
        Type of estimation to perform. Can be either "under" or "over".

        * "under": Estimate the parameters for the lower tail of the distribution.
        * "over": Estimate the parameters for the upper tail of the distribution.

    list_pvals : array-like, optional
        Array-like object containing the p-values to combine for each stratum.
        Either `list_pvals` or `comb_pvals` must be provided, but not both.
    comb_pvals : array-like or float, optional
        Float or array-like object containing the value of combination of p-values.
        Either `list_pvals` or `comb_pvals` must be provided, but not both.
    tau : float, optional
        Threshold value for the p-values. Defaults to None.
        If not provided, a default value of 1 will be used.
    moment : int, optional
        Moment to estimate. Can be 2, 3, or 4. Defaults to 2.
    get_params : bool, optional
        Flag indicating whether to return the estimated parameters. Defaults to False.
    get_moment : bool, optional
        Flag indicating whether to return the estimated moment. Defaults to False.

    Returns
    -------
    tuple or float or array-like
    Depending on the input parameters, the function returns:

        * If `get_params` is True, returns a tuple containing the estimated parameters of the gamma distribution.
        * If `get_moment` is True, returns a tuple containing the estimated moment.
        * If `comb_pvals` is an array-like object, returns an array-like object of combined p-value.
        * Else, returns a float value of the combined p-value.

    Raises
    ------
    ValueError

        * If `list_pvals` and `comb_pvals` are both None or both provided when get_params if False.
        * If `moment` is not 2, 3, or 4.
        * If `tau` is provided and is not between 0 (excluded) and 1.

    Warning

        * If the moment of the distribution is negative, a lower moment will be used instead.
        * If all root of alpha in MME are complex, a lower moment will be used instead.
        * If all real root of alpha in MME are negative, a lower moment will be used instead.
        * If the smallest reachable p-values are below the float value closest to zero, a warning will be raised.

    Notes
    -----
    This function estimates the parameters of a gamma distribution using the method of moments.
    The method of moments matches the moments of the gamma distribution to the sample moments.
    The estimation can be performed for the lower tail or the upper tail of the distribution.
    The function supports estimation of moments up to the fourth moment.
    The estimated parameters can be obtained by setting `get_params` to True.
    The estimated moment can be obtained by setting `get_moment` to True.

    Examples
    --------
    >>> params = [(100, 50, 10), (200, 100, 20)]
    >>> moment_matching_estimator(params, "under", list_pvals=[0.15892000985554622, 0.0485035183722576])
    0.01974031791641234
    >>> moment_matching_estimator(params, "over", comb_pvals=9.730946451863904)
    0.01974031791641234
    >>> moment_matching_estimator(params, "over", list_pvals=[0.15892000985554622, 0.0485035183722576], get_moment=True)
    (3.087381868306516, 5.737504083931502)
    >>> moment_matching_estimator(params, "under", list_pvals=[0.15892000985554622, 0.0485035183722576], get_params=True)
    (1.6613368219541702, 1.8583720215596864, 1, 0)
    >>> gaste_test.moment_matching_estimator(params, "under", comb_pvals=9.730946451863904, tau=0.2)
    0.0018928012017953636
    >>> gaste_test.moment_matching_estimator(params, "under", get_params=True, tau=0.2)
    (0.9601452647906275, 1.9215151230936054, 0.2590451096515598, 0.45983274717174016)
    """
    if (
        not isinstance(list_pvals, (np.ndarray, list))
        and comb_pvals is None
        and not get_params
    ):
        raise ValueError(
            "list_pvals or comb_pvals must be not None when get_params is False"
        )
    if isinstance(list_pvals, (np.ndarray, list)) and comb_pvals:
        raise ValueError(
            "list_pvals and comb_pvals cannot be not None at the same time"
        )
    if list_pvals is None and not get_params:
        raise ValueError("list_pvals must be provided when get_params is False")
    if not 2 <= moment <= 4:
        raise ValueError("moment must be 2, 3 or 4")
    if not tau:
        tau = 1  # default value
    if tau <= 0 or tau > 1:
        raise ValueError("tau must be between 0 excluded and 1")

    def _esperance(masse, pvals):
        return -2 * np.sum(
            [
                q * (p - np.log(tau))
                for q, p in zip(masse, np.log(pvals))
                if p <= np.log(tau) and p != -np.inf
            ]
        )

    def _variance(masse, pvals, mean):
        return (
            4
            * np.sum(
                [
                    q * (p - np.log(tau)) ** 2
                    for q, p in zip(masse, np.log(pvals))
                    if p <= np.log(tau) and p != -np.inf
                ]
            )
            - mean**2
        )

    def _third_cumulant(masse, pvals, mean):
        esp_3 = -8 * np.sum(
            [
                q * (p - np.log(tau)) ** 3
                for q, p in zip(masse, np.log(pvals))
                if p <= np.log(tau) and p != -np.inf
            ]
        )
        esp_2 = 4 * np.sum(
            [
                q * (p - np.log(tau)) ** 2
                for q, p in zip(masse, np.log(pvals))
                if p <= np.log(tau) and p != -np.inf
            ]
        )
        return esp_3 - 3 * mean * esp_2 + 2 * mean**3

    def _fourth_cumulant(masse, pvals, mean, var):
        esp_4 = 16 * np.sum(
            [
                q * (p - np.log(tau)) ** 4
                for q, p in zip(masse, np.log(pvals))
                if p <= np.log(tau) and p != -np.inf
            ]
        )
        esp_3 = -8 * np.sum(
            [
                q * (p - np.log(tau)) ** 3
                for q, p in zip(masse, np.log(pvals))
                if p <= np.log(tau) and p != -np.inf
            ]
        )
        esp_2 = 4 * np.sum(
            [
                q * (p - np.log(tau)) ** 2
                for q, p in zip(masse, np.log(pvals))
                if p <= np.log(tau) and p != -np.inf
            ]
        )
        kurt = (esp_4 - 4 * mean * esp_3 + 6 * mean**2 * esp_2 - 3 * mean**4) / var**2
        return var**2 * (kurt - 3)

    esps = []
    vars = []
    skewnesss = []
    excess_kurts = []
    prop = 1
    phi = []
    control_pval = []
    min_pvals_under_tau = []
    for j, param in enumerate(params):
        param = np.int64(param)
        h = hypergeom(param[0], param[1], param[2])
        sup_max = np.min([param[1], param[2]])
        sup_min = np.max([0, param[1] + param[2] - param[0]])
        masse = [h.pmf(k) for k in range(sup_min, sup_max + 1)]
        masse = np.array(masse)
        if "under" in type:
            pvals = h.cdf(range(sup_min, sup_max + 1))
            prop *= np.sum(masse[len(pvals[pvals <= tau]) :])
        else:
            pvals = h.sf(range(sup_min - 1, sup_max))
            prop *= np.sum(masse[: len(pvals[pvals > tau])])
        if 0.0 in pvals:
            warnings.warn(
                "\x1b[33;20m"
                + f"In the stratum {j+1}, the smallest reachable p-value is below the float value closest to zero ({np.nextafter(0,1)}), and has been converted to it"
                + "\x1b[0m"
            )
            control_pval.append(j)
            pvals = np.array([p if p != 0 else np.nextafter(0, 1) for p in pvals])
        phi.append(
            min(pvals / tau, key=lambda x: 1 - x if 1 - x >= 0 else float("inf"))
        )
        min_pvals_under_tau.append(pvals[pvals <= tau])
        esp = _esperance(masse, pvals)
        esps.append(esp)
        var = _variance(masse, pvals, esp)
        vars.append(var)
        if moment == 3:
            skewnesss.append(_third_cumulant(masse, pvals, esp))
        if moment == 4:
            if var != 0:
                excess_kurt = _fourth_cumulant(masse, pvals, esp, var)
                excess_kurts.append(excess_kurt)

    if tau != 1:
        phi = np.array(phi)
        if (
            len(phi[phi <= 1]) == 0
            or len([e for a in min_pvals_under_tau for e in a]) == 1
        ):
            warnings.warn(
                "The smallest reachable p-values of all strata are above the threshold or the distribution have only a support of 1, combined p-value is 1"
            )
            if get_moment:  # the distribution does not exist
                return (0, 0)
            elif get_params:
                return (np.nan, np.nan, 1, np.nan)
            else:
                if isinstance(comb_pvals, np.ndarray):
                    return np.array([1 for _ in comb_pvals])
                else:
                    return 1
        else:
            phi = -2 * np.log(np.max(phi[phi <= 1]))
        prop = 1 - prop
    else:
        phi = 0
        prop = 1
    esp = np.sum(esps)
    var = np.sum(vars)
    skewness = np.sum(skewnesss) / (var**1.5)
    excess_kurt = np.sum(excess_kurts) / (var**2)

    if get_moment:
        if moment == 2:
            return esp, var
        if moment == 3:
            return esp, skewness
        if moment == 4:
            return esp, excess_kurt

    if skewness < 0 or excess_kurt < 0:
        print(Warning("moment of the distribution is negativ, inferior moment used"))
        return moment_matching_estimator(
            params,
            type,
            list_pvals=list_pvals,
            comb_pvals=comb_pvals,
            tau=tau,
            moment=moment - 1,
            get_params=get_params,
        )

    if moment == 2:
        alpha = esp**2 / (prop * var - (1 - prop) * esp**2)
        beta = (prop * var - (1 - prop) * esp**2) / (prop * esp)
    else:
        if tau == 1 and moment == 3:
            alpha = 4 / (skewness**2)
        elif tau == 1 and moment == 4:
            alpha = 6 / (excess_kurt)
        elif tau != 1:
            if moment == 3:
                alpha_root = np.roots(
                    [
                        1
                        - 6 * prop
                        + 13 * prop**2
                        - 12 * prop**3
                        + 4 * prop**4
                        - skewness**2 * prop * (1 - prop) ** 3,
                        6
                        - 24 * prop
                        + 30 * prop**2
                        - 12 * prop**3
                        - 3 * skewness**2 * prop * (1 - prop) ** 2,
                        13
                        - 30 * prop
                        + 17 * prop**2
                        - 3 * skewness**2 * prop * (1 - prop),
                        12 - prop * (12 + skewness**2),
                        4,
                    ]
                )
            if moment == 4:
                alpha_root = np.roots(
                    [
                        1
                        - prop * (7 + excess_kurt)
                        + prop**2 * (12 + 2 * excess_kurt)
                        - prop**3 * (6 + excess_kurt),
                        6
                        - prop * (18 + 2 * excess_kurt)
                        + prop**2 * (12 + 2 * excess_kurt),
                        11 - prop * (11 + excess_kurt),
                        6,
                    ]
                )

            real_alpha_part = [np.real(a) for a in alpha_root]
            imag_alpha_part = [np.imag(a) for a in alpha_root]
            if 0 not in imag_alpha_part:
                print(
                    Warning(
                        "All root of alpha in MME are complexe, inferior moment used"
                    )
                )
                return moment_matching_estimator(
                    params,
                    type,
                    list_pvals=list_pvals,
                    comb_pvals=comb_pvals,
                    tau=tau,
                    moment=moment - 1,
                    get_params=get_params,
                )
            real_positive_alpha = sorted(
                [
                    real_alpha_part[k]
                    for k in [i for i, v in enumerate(imag_alpha_part) if v == 0]
                    if real_alpha_part[k] > 0
                ]
            )
            if not real_positive_alpha:
                print(
                    Warning(
                        "All real root of alpha in MME are negativ, inferior moment used"
                    )
                )
                return moment_matching_estimator(
                    params,
                    type,
                    list_pvals=list_pvals,
                    comb_pvals=comb_pvals,
                    tau=tau,
                    moment=moment - 1,
                    get_params=get_params,
                )

            alpha = real_positive_alpha[0]
        beta = esp / (prop * alpha)

    if control_pval == list(range(len(params))):
        warnings.warn(
            "\x1b[33;20m"
            + f"In all strata the smallest reachable p-values are below the float value closest to zero, the parameters of the gamma distribution are alpha={round(alpha,2)} and beta={round(1/beta,2)}. You can use it or use a chi-squared distribution with 2n degrees of freedom instead (where n is the number of strata)."
            + "\x1b[0m"
        )
    elif len(control_pval) != 0 and len(control_pval) != len(params):
        warnings.warn(
            "\x1b[33;20m"
            + f"In some strata but not all, the smallest reachable p-value are below the float value closest to zero. If the value of combined p-value is under {round(3*var,2)} (3 times variance), use gamma approximation is recommanded, else use a chi-squared distribution with 2n degrees of freedom instead (where n is the number of strata)."
            + "\x1b[0m"
        )

    if get_params:
        return alpha, beta, prop, phi
    else:
        if isinstance(list_pvals, (np.ndarray, list)):
            combinaison_pvals = -2 * np.sum(
                np.log([pval / tau if pval <= tau else 1 for pval in list_pvals])
            )
        elif isinstance(comb_pvals, (int, float)):
            combinaison_pvals = comb_pvals
        elif isinstance(comb_pvals, (np.ndarray, list)):
            return np.array(
                [
                    gamma(alpha, scale=beta).sf(x - phi) * prop if x > phi else 1
                    for x in comb_pvals
                ]
            )
        else:
            raise ValueError("comb_pvals must be a float or a numpy array")
        if combinaison_pvals <= phi:
            return 1
        else:
            return gamma(alpha, scale=beta).sf(combinaison_pvals - phi) * prop


def get_pval_comb(
    data_params,
    data_pvals,
    type,
    tau=0.2,
    threshold_compute_explicite=5 * 10**7,
    moment=4,
    jobs=None,
    verbose=False,
    distribution=False,
    all_value=False,
):
    """
    Compute the combined p-value.

    Parameters
    ----------
    data_pvals : list
        List of p-values.
    data_params : list
        List of parameters.
    type : str
        Type of combination method.
    tau : float, optional
        Threshold value for p-values. Default is None.
    threshold_compute_explicite : int, optional
        Threshold for using explicit calculation. Default is 10**7.
    moment : int, optional
        Moment for moment matching estimator. Default is 4.
    jobs : int, optional
        Number of parallel jobs. Default is None.
    verbose : bool, optional
        Whether to print verbose output. Default is False.
    distribution : bool, optional
        Whether to compute the distribution of the combined p-value. Default is False.
    all_value : bool, optional
        Whether to return all intermediate values. Default is False.

    Returns
    -------
    float
        The combined p-value.

    Notes
    -----
    This function computes the combined p-value based on the given p-values and parameters.
    It uses either explicit calculation or moment matching estimator depending on the support size of the combined p-value.
    If the support size is below the threshold_compute_explicite, explicit calculation is used.
    Otherwise, moment matching estimator is used.

    """

    if not tau:
        tau = 1

    size_HG = [
        float(np.min([p[1], p[2]]) - np.max([0, p[1] + p[2] - p[0]]) + 1)
        for p in data_params
    ]
    support_size = np.prod(size_HG)

    max_val = 0
    for p in data_params:
        p = np.int64(p)
        h = hypergeom(p[0], p[1], p[2])
        sup_max = np.min([p[1], p[2]])
        sup_min = np.max([0, p[1] + p[2] - p[0]])
        if "under" in type:
            if (pval_min := h.cdf(sup_min)) < tau and 0.0 != pval_min:
                max_val += np.log(pval_min / tau)
            else:
                max_val += np.log(np.nextafter(0, 1) / tau)
        elif "over" in type:
            if (pval_min := h.sf(sup_max - 1)) < tau and 0.0 != pval_min:
                max_val += np.log(pval_min / tau)
            else:
                max_val += np.log(np.nextafter(0, 1) / tau)
        else:
            raise ValueError("type must be either 'under' or 'over'")
    max_val = -2 * max_val

    if len(data_pvals) == 0:
        return None
    if len(np.array(data_pvals)[np.array(data_pvals) >= tau]) == len(data_pvals):
        return 1
    if len(data_pvals) == 1:
        return data_pvals[0]
    if 0 < support_size < threshold_compute_explicite:
        if verbose:
            print(
                f"The support of the combined p-value is {support_size:.2e}, under the compute explicite threshold of {threshold_compute_explicite:.2e} , the explicite calculation is used."
            )
        return explicite_combination(
            data_params,
            data_pvals,
            type,
            tau=tau,
            jobs=jobs,
            verbose=verbose,
            distribution=distribution,
            all_value=all_value,
        )
    else:
        var_Y_tau = moment_matching_estimator(
            data_params,
            type,
            list_pvals=data_pvals,
            tau=tau,
            moment=moment,
            get_moment=True,
        )[1]
        if verbose:
            print(
                f"The support of the combined p-value is {support_size:.2e}, over the compute explicite threshold of {threshold_compute_explicite:.2e} , the moment matching estimator is used."
            )
        automatic_moment = moment
        already_check = False
        if tau > 0.2:
            if verbose:
                print(
                    f"You set a truncation threshold tau {tau} above 0.2, the moment matching estimator is used automatically with second moment."
                )
            automatic_moment = 2
            already_check = True
        if var_Y_tau / max_val > 0.1 and not already_check:
            if verbose:
                print(
                    f"The ratio between the variance of the combined p-value ({var_Y_tau:.2f}) and the max value of the statistic ({max_val:.2f}) is above 0.1, the moment matching estimator is used automatically with second moment."
                )
            automatic_moment = 2
        return moment_matching_estimator(
            data_params, type, list_pvals=data_pvals, tau=tau, moment=automatic_moment
        )


# idea find the value of tau given the min combined pvals (pval hacking ???)
# or use the BD test to test the homogeneous
# number of test = number of strata
# test sensibility of approximation comparing the moment (eg coeff variation among 3 values)
