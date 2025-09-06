import os
import sys
from collections import namedtuple
from typing import List, NamedTuple, Optional, Tuple, Union

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Polygon
from scipy.stats import chi2, hypergeom, norm

from gaste_test.combined_pval import get_pval_comb


class _Result(namedtuple("Result", ["stat", "pvalue"])):
    """
    Represents the result of a statistical test.

    Attributes
    ----------
        stat (float): The calculated statistic value.
        pvalue (float): The p-value associated with the statistic.
    """

    def __str__(self):
        return f"statistic: {self.stat:.4f}, p-value: {(lambda x: f'{x:.2e}' if x < 0.001 else f'{x:.4f}')(self.pvalue)}"


class Table2x2:
    """
    Represents a 2x2 contingency table and provides various statistical calculations.

    Parameters:
    -----------
    table_data : 2D array-like representing the content of the table [[a,b],[c,d]] where `a` is the count of events in the first category, `b` is the count of non-events in the first category, `c` is the count of events in the second category, `d` is the count of non-events in the second category. Or a tuple of 4 integers (N, n, K, a) where `N` is the total count of events and non-events, `n` is the count of events in both categories, `K` is the total count in the first category, and `a` is the count of events in the first category.

    Attributes:
    -----------
    a : int
        The count of events in the first category.
    b : int
        The count of non-events in the first category.
    c : int
        The count of events in the second category.
    d : int
        The count of non-events in the second category.
    N : int
        The total count of events and non-events (a+b+c+d).
    n : int
        The count of events in both categories (a+c).
    K : int
        The total count in the first category (a+b).

    Methods:
    --------
    odd_ratio()
        Calculates the odds ratio of the contingency table.
    support()
        Returns the range of possible support values.
    len_support()
        Returns the number of possible support values.
    variance_log_odd_ratio()
        Calculates the variance of the log odds ratio.
    ci_odd_ratio(alpha=0.05)
        Calculates the confidence interval of the odds ratio.
    mh_weight()
        Calculates the Mantel-Haenszel weight.
    pval_under()
        Calculates the p-value for observing the given count or fewer.
    pval_over()
        Calculates the p-value for observing the given count or more.
    support_pval_under()
        Calculates the p-values for observing each support value or fewer.
    support_pval_over()
        Calculates the p-values for observing each support value or more.
    """

    def __init__(
        self,
        table_data: Union[
            Tuple[Tuple[int, int], Tuple[int, int]], Tuple[int, int, int, int]
        ],
    ) -> None:
        table_data = np.array(table_data, dtype=int)
        if table_data.shape == (2, 2):
            self.a, self.b = table_data[0]
            self.c, self.d = table_data[1]
            self.N = self.a + self.b + self.c + self.d
            self.n = self.a + self.c
            self.K = self.a + self.b
        elif table_data.shape == (4,):
            self.N, self.n, self.K, self.a = table_data
            self.b = self.K - self.a
            self.c = self.n - self.a
            self.d = self.N - self.n - self.K + self.a
        else:
            raise ValueError("The data should be a 2x2 table or a tuple of 4 integers.")

    def odd_ratio(self):
        """
        Calculates the odds ratio of the contingency table.

        Returns:
        --------
        float
            The odds ratio.
        """
        if self.a == 0:
            a = 0.5
        else:
            a = self.a
        if self.c == 0:
            c = 0.5
        else:
            c = self.c
        if self.b == 0:
            b = 0.5
        else:
            b = self.b
        if self.d == 0:
            d = 0.5
        else:
            d = self.d
        return a * d / (b * c)

    def support(self) -> range:
        """
        Returns the range of possible support values.

        Returns:
        --------
        range
            The range of possible support values.
        """
        return range(max(0, self.K + self.n - self.N), min(self.K, self.n) + 1)

    def len_support(self) -> float:
        """
        Returns the number of possible support values.

        Returns:
        --------
        float
            The number of possible support values.

        Notes:
        --------
        The type of the int return value is cast to float to avoid rounding errors during the calculation of the number of combination in Stratified2x2.
        """
        return float(len(self.support()))

    def variance_log_odd_ratio(self):
        """
        Calculates the variance of the log odds ratio.

        Returns:
        --------
        float
            The variance of the log odds ratio.
        """
        if self.a == 0:
            a = 0.5
        else:
            a = self.a
        if self.c == 0:
            c = 0.5
        else:
            c = self.c
        if self.b == 0:
            b = 0.5
        else:
            b = self.b
        if self.d == 0:
            d = 0.5
        else:
            d = self.d
        return 1 / a + 1 / b + 1 / c + 1 / d

    def ci_odd_ratio(self, alpha=0.05):
        """
        Calculates the confidence interval of the odds ratio.

        Parameters:
        -----------
        alpha : float, optional
            The significance level (default is 0.05).

        Returns:
        --------
        tuple
            A tuple containing the lower and upper bounds of the confidence interval.
        """
        or_ = self.odd_ratio()
        se = np.sqrt(self.variance_log_odd_ratio())
        log_ci_inf = np.log(or_) - norm.ppf(1 - alpha / 2) * se
        log_ci_sup = np.log(or_) + norm.ppf(1 - alpha / 2) * se
        return np.exp(log_ci_inf), np.exp(log_ci_sup)

    def mh_weight(self):
        """
        Calculates the Mantel-Haenszel weight.

        Returns:
        --------
        float
            The Mantel-Haenszel weight.
        """
        if self.c == 0:
            c = 0.5
        else:
            c = self.c
        if self.b == 0:
            b = 0.5
        else:
            b = self.b
        return (b * c) / self.N

    def pval_under(self):
        """
        Calculates the p-value for observing the given count or fewer.

        Returns:
        --------
        float
            The p-value.
        """
        return hypergeom(self.N, self.K, self.n).cdf(self.a)

    def pval_over(self):
        """
        Calculates the p-value for observing the given count or more.

        Returns:
        --------
        float
            The p-value.
        """
        return hypergeom(self.N, self.K, self.n).sf(self.a - 1)

    def support_pval_under(self):
        """
        Calculates the p-values for observing each support value or fewer.

        Returns:
        --------
        ndarray
            An array of p-values.
        """
        return hypergeom(self.N, self.K, self.n).cdf(self.support())

    def support_pval_over(self):
        """
        Calculates the p-values for observing each support value or more.

        Returns:
        --------
        ndarray
            An array of p-values.
        """
        return hypergeom(self.N, self.K, self.n).sf(np.array(self.support()) - 1)


class StratifiedTable2x2:
    """
    This module contains the StratifiedTable2x2 class for analyzing stratified 2x2 contingency tables.

    :class:`StratifiedTable2x2` takes in a list of tables, labels, and optional parameters to perform various statistical tests and calculations on the tables.

    Parameters:
    -----------
        tables (list) : A list of ndarray 2x2 representing the contingency tables. One table per stratum.
        labels (list) : A list of labels for each table/stratum.
        decimal (int) : The number of decimal places to round the results to. Default is 3.
        alpha (float) : The significance level for confidence intervals and hypothesis tests. Default is 0.05.
        limit_computation_exact (int) : The limit for exact computation of the combined p-value. Default is 10^7.
        name_rows (tuple) : A tuple of row names for the tables. Optional.
        name_columns (tuple) : A tuple of column names for the tables. Optional.

    Attributes:
    -----------
        nb_combination (float) : The number of combinations for the exact calculation, int cast to float for numeric reason.
        odds_ratio (ndarray) : An array of odds ratios for each table.
        log_odds_ratio (ndarray) : An array of log odds ratios for each table.
        ci_odds_ratio_inf (ndarray) : An array of lower confidence intervals for odds ratios.
        ci_odds_ratio_sup (ndarray) : An array of upper confidence intervals for odds ratios.
        log_ci_odds_ratio_inf (ndarray) : An array of lower confidence intervals for log odds ratios.
        log_ci_odds_ratio_sup (ndarray) : An array of upper confidence intervals for log odds ratios.
        pval_under (ndarray) : An array of p-values for the hypothesis test of odds ratio < 1.
        pval_over (ndarray) : An array of p-values for the hypothesis test of odds ratio > 1.
        weight (ndarray) : An array of weights for each table.
        odds_ratio_pooled (float) : The pooled odds ratio.
        df (DataFrame) : A pandas DataFrame containing the results of the analysis and data.

    Methods:
    --------
        __init__(tables, labels, decimal=3, alpha=0.05, name_rows=None, name_columns=None):
            Initializes a StratifiedTable2x2 object with the given parameters.
        gaste(alternative='less', tau=1, limit_computation_exact=10**7, verbose=True, moment=2, jobs=None):
            Performs the GASTE test on the tables.
        pool_odd_ratio():
            Calculates the pooled odds ratio.
        pool_ci_odd_ratio():
            Calculates the confidence interval for the pooled odds ratio.
        CMH_test(correction=False):
            Performs the Cochran-Mantel-Haenszel test on the tables.
        BD_test(adjust=False):
            Performs the Breslow-Day test for homogeneity of odds ratios.
        resume():
            Prints a summary of the analysis results.
        plot(log_scale=True, fontsize=12, thresh_adjust=0.03, y_figsize=None, save=None):
            Plots a forest plot with odds ratios, confidence intervals and resume of data.
    """

    def __init__(
        self,
        tables: List[Tuple[Tuple[int, int], Tuple[int, int]]],
        labels: Optional[List[str]] = None,
        decimal: Optional[int] = 3,
        alpha: Optional[str] = 0.05,
        limit_computation_exact: Optional[int] = 10**7,
        name_rows: Optional[Tuple[str, str]] = None,
        name_columns: Optional[Tuple[str, str]] = None,
    ) -> None:
        # TODO include random effect model and different method than MH
        self.tables = [Table2x2(table) for table in tables]
        if labels is None:
            self.labels = [f"Stratum {i}" for i in range(len(self.tables))]
        else:
            self.labels = labels
        self.decimal = decimal
        self.alpha = alpha
        self.ai = np.array([table.a for table in self.tables])
        self.bi = np.array([table.b for table in self.tables])
        self.ci = np.array([table.c for table in self.tables])
        self.di = np.array([table.d for table in self.tables])
        self.Ni = np.array([table.N for table in self.tables])
        self.ni = self.ai + self.ci
        self.Ki = self.ai + self.bi
        self.params = np.array([self.Ni, self.ni, self.Ki]).T
        self.name_rows = name_rows
        self.name_columns = name_columns
        self.nb_combination = np.prod(
            [float(table.len_support()) for table in self.tables]
        )
        self.limit_computation_exact = limit_computation_exact

        self.odds_ratio = np.array([table.odd_ratio() for table in self.tables])
        self.log_odds_ratio = np.log(self.odds_ratio)
        self.ci_odds_ratio_inf, self.ci_odds_ratio_sup = np.array(
            [table.ci_odd_ratio(alpha=self.alpha) for table in self.tables]
        ).T
        self.ci_odds_ratio_print = [
            f"[{round(ci_inf, self.decimal):.{self.decimal}f}, {round(ci_sup, self.decimal):.{self.decimal}f}]"
            for ci_inf, ci_sup in zip(self.ci_odds_ratio_inf, self.ci_odds_ratio_sup)
        ]
        self.log_ci_odds_ratio_inf = np.log(self.ci_odds_ratio_inf)
        self.log_ci_odds_ratio_sup = np.log(self.ci_odds_ratio_sup)
        self.log_ci_odd_ratio_print = [
            f"[{round(ci_inf, self.decimal):.{self.decimal}f}, {round(ci_sup, self.decimal):.{self.decimal}f}]"
            for ci_inf, ci_sup in zip(
                self.log_ci_odds_ratio_inf, self.log_ci_odds_ratio_sup
            )
        ]
        self.pval_under = np.array([table.pval_under() for table in self.tables])
        self.pval_over = np.array([table.pval_over() for table in self.tables])
        self.weight = np.array([table.mh_weight() for table in self.tables])
        self.weight = self.weight / np.sum(self.weight)
        self.odds_ratio_pooled = self.pool_odd_ratio()
        self.df = pd.DataFrame(
            {
                "Studies": self.labels,
                "$k_s$": self.ai,
                "$K_s-k_s$": self.bi,
                "$n_s-k_s$": self.ci,
                "$N_s-n_s$\n$-K_s+k_s$": self.di,
                "$p_s^-$": self.pval_under,
                "$p_s^+$": self.pval_over,
                "OR": self.odds_ratio,
                "log(OR)": self.log_odds_ratio,
                "CI": self.ci_odds_ratio_print,
                "log(CI)": self.log_ci_odd_ratio_print,
                "%W(fixed)": np.round(self.weight * 100, 1),
            }
        )
        self.df = self.df.set_index("Studies").round(
            {"OR": self.decimal, "log(OR)": self.decimal}
        )
        if self.name_rows is not None and self.name_columns is not None:
            row1, row2 = self.name_rows
            col1, col2 = self.name_columns
            dict_rename = {
                "$k_s$": f"{col1} {row1}",
                "$K_s-k_s$": f"{col2} {row1}",
                "$n_s-k_s$": f"{col1} {row2}",
                "$N_s-n_s$\n$-K_s+k_s$": f"{col2} {row2}",
            }
            self.df.rename(columns=dict_rename, inplace=True)
            self.name_columns_data = list(dict_rename.values())
        else:
            self.name_columns_data = [
                "$k_s$",
                "$K_s-k_s$",
                "$n_s-k_s$",
                "$N_s-n_s$\n$-K_s+k_s$",
            ]
        self.combined_pval_less = None
        self.combined_pval_greater = None

    def gaste(
        self,
        alternative: Optional[str] = "less",
        tau=1,
        limit_computation_exact=10**7,
        verbose=True,
        moment=2,
        jobs=None,
    ) -> NamedTuple:
        r"""
        Compute the GASTE (Gamma Approximation of Stratified Troncated Exact) test to test the overall association between features and outcome in 2x2 stratified table.

        Parameters
        ----------
        alternative : {'less', 'greater'}, optional
            The alternative hypothesis. Default is "less".

            * 'less': compute the combined p-value of one-sided `less` Fisher exact test of each stratum to test overall under-association.
            * 'greater': compute the combined p-value of one-sided `greater` Fisher exact test of each stratum to test overall over-association.

            See the Notes for more details.

        tau : int or float, optional
            The truncation value used in GASTE. Default is 1.
        limit_computation_exact : int, optional
            The limit for exact computation of the combined p-value. Default is 10^7.
        verbose : bool, optional
            Whether to print verbose output during computation. Default is True.
        moment : int, optional
            The moment to use for the approximation of the combined p-value. Default is 2.
        jobs : int or None, optional
            The number of parallel jobs to use for computation. Default is None, all core is used.

        Returns
        -------
        result : Result
            A named tuple containing attributes :
                stat : float
                    It's the value of the combination of p-value of observed data in each strat.
                pvalue : float
                    The combined p-value resulting from the GASTE test.

        Raises
        ------
        ValueError
            If the `alternative` parameter is not "less" or "greater".

        See Also
        --------
        combined_pval.get_pval_comb : The function that computes the combined p-value.


        Notes:
        ------
        The GASTE statistic is computed as :math:`Y_{\tau} = -2\sum_{i=1}^I \left(\log(P_s) - \log(\tau)\right)\mathbb{I}(P_s\leq\tau)` or each p-value in the given data.

        .. math::
            Y_{\tau} = -2\sum_{i=1}^I \left( \log(P_s) - \log(\tau)\right)\mathbb{I}(P_s\leq\tau)

        The combined p-value is computed exactly by exploring all possible combination of tables if the number of combination is under the limit threshold, else gamma approximation is used.

        If `alternative` is `less`, the combined p-value is stored in `self.combined_pval_less`.
        If `alternative` is `greater`, the combined p-value is stored in `self.combined_pval_greater`. So if the result is needed later in plot method or other, it can be used without recomputing it.

        Globaly this method call the function :py:func:`combined_pval.get_pval_comb`. See documentation for more details
        """
        # Globaly this method call the function `combined_pval.get_pval_comb`_ . See documentation for more details.
        # \(Y_{\tau} = -2\sum_{i=1}^I \left( \log(P_s) - \log(\tau)\right)\mathbb{I}(P_s\leq\tau) \)

        # TODO math formula
        # For the overall under-association, the hypotheses are :
        # $$H^-_0=\cap H^-_{0_s}: "\forall i, \theta_s \geq 1" \text{ against } H^-_1 : "\theta_s < 1 \text{ for at least one stratum } i"$$
        # Similary, for the overall over-association :
        # $$H^+_0=\cap H^+_{0_s}: "\forall i, \theta_s \leq 1" \text{ against } H^+_1 : "\theta_s > 1 \text{ for at least one stratum } i"$$
        if alternative == "less":
            pvals = self.pval_under
            alternative = "under"
        elif alternative == "greater":
            pvals = self.pval_over
            alternative = "over"
        else:
            raise ValueError("alternative should be 'less' or 'greater'")
        gaste_ = -2 * np.sum(np.log([p / tau if p <= tau else 1 for p in pvals]))
        if self.limit_computation_exact == 10**7 and limit_computation_exact != 10**7:
            limit_computation_exact_ = limit_computation_exact
        else:
            limit_computation_exact_ = self.limit_computation_exact
        comb_pval = get_pval_comb(
            pvals,
            self.params,
            alternative,
            tau=tau,
            threshold_compute_explicite=limit_computation_exact_,
            verbose=verbose,
            moment=moment,
            jobs=jobs,
        )
        result = _Result(gaste_, comb_pval)

        if alternative == "under":
            self.combined_pval_less = result
        else:
            self.combined_pval_greater = result

        return result

    def pool_odd_ratio(self):
        """
        Calculate the pooled odds ratio.

        Returns:
        --------
            float: The pooled odds ratio.
        """
        return np.sum(self.odds_ratio * self.weight)

    def pool_ci_odd_ratio(self):
        """
        Calculate the confidence interval for the pooled odds ratio.

        This method calculates the confidence interval for the pooled odds ratio using the Generalized Mantel-Haenszel estimators for K 2xJ tables.

        Returns:
        --------
            tuple: A tuple containing the lower and upper bounds of the confidence interval.

        References:
        -----------
            - Greenland S (1989) Generalized Mantel-Haenszel estimators for K 2xJ tables. Biometrics 45(1):183-191
        """
        pool_od = np.log(self.pool_odd_ratio())
        Pi = self.ai / self.Ni + self.di / self.Ni
        Qi = self.bi / self.Ni + self.ci / self.Ni
        Ri = (self.ai / self.Ni) * self.di
        Si = (self.bi / self.Ni) * self.ci
        R = np.sum(Ri)
        S = np.sum(Si)
        se = np.sqrt(
            1
            / 2
            * (
                np.sum(Pi * Ri) / R**2
                + np.sum(Pi * Si + Qi * Ri) / (R * S)
                + np.sum(Qi * Si) / S**2
            )
        )
        return np.exp(pool_od - norm.ppf(1 - self.alpha / 2) * se), np.exp(
            pool_od + norm.ppf(1 - self.alpha / 2) * se
        )

    def CMH_test(self, correction=False) -> NamedTuple:
        """
        Perform the Cochran-Mantel-Haenszel (CMH) test on a 2x2 stratified table to test the overall association between features and outcomes in 2x2 stratified table.

        Parameters:
        -----------
        correction : bool, optional
            Parameter to apply Yates correction for continuity. Default is False.

        Returns:
        --------
        result : Result
            A named tuple containing attributes :
                stat : float
                    The CMH test statistic
                pvalue : float
                    The p-value associated with the CMH test

        References:
        -----------
            - Cochran, W. G. (1954). Some methods for strengthening the common chi-squared tests. Biometrics, 10(4), 417-451.
            - Mantel, N., & Haenszel, W. (1959). Statistical aspects of the analysis of data from retrospective studies of disease. Journal of the National Cancer Institute, 22(4), 719-748.
        """
        if correction:
            correction = 0.5
        else:
            correction = 0
        cmh = (
            np.abs(np.sum(self.ai - (self.Ki) * (self.ni) / self.Ni)) - correction
        ) ** 2 / np.sum(
            self.Ki
            * self.ni
            * (self.bi + self.di)
            * (self.ci + self.di)
            / self.Ni**2
            / (self.Ni - 1)
        )
        pval = chi2.sf(cmh, 1)
        result = _Result(cmh, pval)
        return result

    def BD_test(self, adjust=False):
        """
        Perform the Breslow-Day test for homogeneity of odds ratios, i.e. test that all odds ratio are equal.

        Parameters:
        -----------
        adjust : bool, optional
            Use the Tarone adjustment to achieve the chi^2 asymptotic distribution.

        Returns:
        --------
        result : Result
            A named tuple containing attributes :
                statistic : float
                    The chi^2 test statistic.
                p-value : float
                    The p-value for the test.

        Notes:
        ------
        The implementation is inspired by the implementation in the `statsmodels` package.
        """

        a = 1 - self.odds_ratio_pooled
        b = self.odds_ratio_pooled * (self.Ki + self.ni) + (self.di - self.ai)
        c = -self.odds_ratio_pooled * self.Ki * self.ni

        # Expected value of first cell
        e_ki = (-b + np.sqrt(b**2 - 4 * a * c)) / (2 * a)

        # Variance of the first cell
        v_ki = (
            1 / e_ki
            + 1 / (self.ni - e_ki)
            + 1 / (self.Ki - e_ki)
            + 1 / (self.di - self.ai + e_ki)
        )
        v_ki = 1 / v_ki

        bd = np.sum((self.ai - e_ki) ** 2 / v_ki)

        if adjust:
            adj = np.sum(self.ai) - np.sum(e_ki)
            adj = adj**2
            adj /= np.sum(v_ki)
            bd -= adj

        pval = chi2.sf(bd, len(self.tables) - 1)
        result = _Result(bd, pval)
        return result

    def resume(self):
        """
        Print the DataFrame containing the data, the odd ration and ci of each stratum, pooled odd ratio with MH method, and the confident interval of the pooled odd ratio.

        Returns:
        --------
            None
        """
        ci_inf, ci_sup = self.pool_ci_odd_ratio()
        print(self.df)
        print("\nPooled odd ratio with MH method : ", round(self.pool_odd_ratio(), 4))
        print(
            f"Confident interval at {round((1-self.alpha)*100, 2)}% of pooled odd ratio : ({round(ci_inf, 4)}, {round(ci_sup, 4)})"
        )

    def plot(
        self,
        log_scale=True,
        fontsize=12,
        thresh_adjust=0.03,
        y_figsize=None,
        save: Optional[str] = None,
    ):
        """
        Plot a forest plot with odds ratios, confidence intervals and resume of data on each side of the CI odd ratio plot. The plot is annotated with the CMH test, BD test, and GASTE test results.

        Parameters:
        -----------
        log_scale : bool, optional
            Whether to use a logarithmic scale for the x-axis, so use odd ratio or log odd ratio. Default is True.
        fontsize : int, optional
            The font size for the plot. Default is 12.
        thresh_adjust : float, optional
            The adjustment value for the figure on y-axis to align confident interval result with data on each side. If you have only 2 or 3 strata, a value of 0.1 is advise. Else, if you have more than 10 strata, a smaller value like 0.001 is advise. Default is 0.03.
        y_figsize : float, optional
            The figure size for the y-axis. Default is None and set automatically based on the number of strata.
        save : str, optional
            The file path to save the plot, a png and svg file will be create. Default is None.

        Notes:
        ------
        At the end `show` is not called, so you can use `plt.show()` to display the plot. But there is an issue with the x-axis size of the display due to the use of annotation to show some information on each side of the CI odd ratio plot. So the option `save` is recommended to save and display the plot, or the use of Jupiter notebook avoid this issue.

        Returns:
        --------
            None
        """
        if y_figsize is None:
            y_figsize = 5 / 6 * len(self.labels) - 0.2
        fig, ax = plt.subplots(figsize=(6.8, y_figsize))

        if log_scale:
            xerr = [
                np.log(self.odds_ratio) - np.log(self.ci_odds_ratio_inf),
                np.log(self.ci_odds_ratio_sup) - np.log(self.odds_ratio),
            ]
            odds_ratio = np.log(self.odds_ratio)
            ci_pool_odd_ratio_inf, ci_pool_odd_ratio_sup = np.log(
                self.pool_ci_odd_ratio()
            )
            pool_odd = np.log(self.odds_ratio_pooled)
            center_val = 0
            print_theta = "\log(\\theta)"
            print_theta_s = "\log(\\theta_s)"
        else:
            xerr = [
                self.odds_ratio - self.ci_odds_ratio_inf,
                self.ci_odds_ratio_sup - self.odds_ratio,
            ]
            odds_ratio = self.odds_ratio
            ci_pool_odd_ratio_inf, ci_pool_odd_ratio_sup = self.pool_ci_odd_ratio()
            pool_odd = self.odds_ratio_pooled
            center_val = 1
            print_theta = "\\theta"
            print_theta_s = "\\theta_s"
        ax.errorbar(
            odds_ratio,
            range(len(self.labels) - 1, -1, -1),
            xerr=xerr,
            marker="None",
            zorder=2,
            ecolor="dimgrey",
            elinewidth=1,
            linewidth=0,
        )
        size_marker = self.weight * 100 * 7
        ax.scatter(
            odds_ratio,
            range(len(self.labels) - 1, -1, -1),
            c="k",
            s=size_marker,
            marker="d",
            zorder=3,
            edgecolors="None",
        )
        ax.add_patch(
            Polygon(
                [
                    [ci_pool_odd_ratio_inf, -1],
                    [pool_odd, -1 + 1 / 4],
                    [ci_pool_odd_ratio_sup, -1],
                    [pool_odd, -1 - 1 / 4],
                ],
                closed=True,
                fill=True,
                edgecolor="k",
                facecolor="k",
            )
        )
        ax.annotate(
            "",
            xy=(-1.1, 1),
            xycoords="axes fraction",
            xytext=(1.6, 1),
            arrowprops=dict(arrowstyle="-", color="k"),
        )
        ax.annotate(
            "",
            xy=(-1.1, 1 / len(self.labels) - thresh_adjust),
            xycoords="axes fraction",
            xytext=(1.6, 1 / len(self.labels) - thresh_adjust),
            arrowprops=dict(arrowstyle="-", color="k"),
        )

        cmh, cmh_pval = self.CMH_test()

        ax.annotate(
            rf"FE Model $\bf{{Overall\,effect\, CMH}}$, test of ${print_theta}={center_val}$, CMH={cmh:.4f} $\bf{{p={(lambda x: f'{x:.2e}' if x < 0.001 else f'{x:.4f}')(cmh_pval)}}}$",
            xy=(-1.1, 1 / len(self.labels) / 2 - thresh_adjust),
            xycoords="axes fraction",
            fontsize=fontsize,
        )
        bd, bd_pval = self.BD_test()
        ax.annotate(
            rf"Test for $\bf{{Homogeneity}}$, test of $\theta_i=\theta_j$, BD={bd:.4f} $\bf{{p={(lambda x: f'{x:.2e}' if x < 0.001 else f'{x:.4f}')(bd_pval)}}}$",
            xy=(
                -1.1,
                1 / len(self.labels) / 2 - thresh_adjust - 0.5 / len(self.labels),
            ),
            xycoords="axes fraction",
            fontsize=fontsize,
        )

        if self.combined_pval_less is None:
            gaste_, gaste_pval_ = self.gaste("less")
        else:
            gaste_, gaste_pval_ = self.combined_pval_less
        if self.combined_pval_greater is None:
            gaste, gaste_pval = self.gaste("greater")
        else:
            gaste, gaste_pval = self.combined_pval_greater
        ax.annotate(
            rf"$\bf{{Overall\,effect,\,Stratified\,Exact\,test\,(GASTE)}}$, $\#\it{{supp}}(Y)={self.nb_combination:.2e}$",
            xy=(-1.1, 1 / len(self.labels) / 2 - thresh_adjust - 1 / len(self.labels)),
            xycoords="axes fraction",
            fontsize=fontsize,
        )
        ax.annotate(
            rf"test of $\forall \, s, \, {print_theta_s}\geq{center_val}$, $Y_1^-$={gaste_:.4f}, $\bf{{p^-={(lambda x: f'{x:.2e}' if x < 0.001 else f'{x:.4f}')(gaste_pval_)}}}$",
            xy=(-1, 1 / len(self.labels) / 2 - thresh_adjust - 1.5 / len(self.labels)),
            xycoords="axes fraction",
            fontsize=fontsize,
        )
        ax.annotate(
            rf"test of $\forall \, s, \, {print_theta_s}\leq{center_val}$, $Y_1^+$={gaste:.4f}, $\bf{{p^+={(lambda x: f'{x:.2e}' if x < 0.001 else f'{x:.4f}')(gaste_pval)}}}$",
            xy=(-1, 1 / len(self.labels) / 2 - thresh_adjust - 2 / len(self.labels)),
            xycoords="axes fraction",
            fontsize=fontsize,
        )

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(True)
        ax.spines["left"].set_visible(False)
        ax.set_ylim(-1.5, (len(self.labels) - 0.5))
        ax.set_yticks([])
        ax.axvline(center_val, color="k", zorder=1, ls=(0, (1, 1)))
        if log_scale:
            ax.set_xlabel("Log Odds Ratio", fontsize=fontsize)
        else:
            ax.set_xlabel("Odds Ratio", fontsize=fontsize)
        ax.axvline(pool_odd, color="gray", zorder=1, ls=(0, (5, 5)))
        ax.tick_params(axis="x", which="major", labelsize=fontsize)

        df_left = self.df[self.name_columns_data + ["$p_s^-$", "$p_s^+$"]].copy()
        if self.name_rows is not None and self.name_columns is not None:
            row1, row2 = self.name_rows
            col1, col2 = self.name_columns
            df_left.rename(
                columns={
                    f"{col1} {row1}": f"{col1}",
                    f"{col2} {row1}": f"{col2}",
                    f"{col1} {row2}": f"{col1}",
                    f"{col2} {row2}": f"{col2}",
                },
                inplace=True,
            )
            ax.annotate(
                f"{row1}",
                xy=(-0.76, 1 + 1 / len(self.labels) - thresh_adjust),
                xycoords="axes fraction",
                fontsize=fontsize,
            )
            ax.annotate(
                f"{row2}",
                xy=(-0.46, 1 + 1 / len(self.labels) - thresh_adjust),
                xycoords="axes fraction",
                fontsize=fontsize,
            )
        df_left["$p_s^-$"] = self.df["$p_s^-$"].apply(
            lambda x: f"{x:.2e}" if x < 0.001 else f"{x:.4f}"
        )
        df_left["$p_s^+$"] = self.df["$p_s^+$"].apply(
            lambda x: f"{x:.2e}" if x < 0.001 else f"{x:.4f}"
        )
        table_left = pd.plotting.table(
            ax,
            df_left,
            loc="center",
            cellLoc="center",
            bbox=(-0.85, 1 / len(self.labels) - thresh_adjust, 0.9, 1),
        )

        table_left.auto_set_font_size(False)
        table_left.set_fontsize(fontsize)
        for key, cell in table_left.get_celld().items():
            cell.set_linewidth(0)

        if log_scale:
            df_right = self.df[["log(OR)", "log(CI)", "%W(fixed)"]].copy()
            df_right["Log Odd ratio\n with 95% CI"] = [
                f"{odd:.{self.decimal}f}" + "  " + ci
                for odd, ci in zip(df_right["log(OR)"], df_right["log(CI)"])
            ]
            prefix = "Log "
        else:
            df_right = self.df[["OR", "CI", "%W(fixed)"]].copy()
            df_right["Odd ratio\n with 95% CI"] = [
                f"{odd:.{self.decimal}f}" + "  " + ci
                for odd, ci in zip(df_right["OR"], df_right["CI"])
            ]
            prefix = ""

        df_right["%W(fixed)"] = df_right["%W(fixed)"].apply(lambda x: f"{x:.1f}%")
        df_right = df_right[[f"{prefix}Odd ratio\n with 95% CI", "%W(fixed)"]]
        df_right = pd.concat(
            [
                df_right,
                pd.DataFrame(
                    {
                        f"{prefix}Odd ratio\n with 95% CI": f"{round(pool_odd, self.decimal):.{self.decimal}f}"
                        + "  "
                        + f"[{round(ci_pool_odd_ratio_inf, self.decimal):.{self.decimal}f},{round(ci_pool_odd_ratio_sup, self.decimal):.{self.decimal}f}]",
                        "%W(fixed)": "100.0%",
                    },
                    index=[0],
                ),
            ]
        )
        the_table_2 = ax.table(
            cellText=df_right.values,
            rowLabels=[""] * (len(self.labels) + 1),
            colLabels=df_right.columns,
            cellLoc="center",
            bbox=(
                1,
                0,
                0.6,
                (len(self.labels) + 1) / len(self.labels) - thresh_adjust,
            ),
            colWidths=[0.2, 0.1],
        )

        the_table_2.auto_set_font_size(False)
        the_table_2.set_fontsize(fontsize)
        for key, cell in the_table_2.get_celld().items():
            cell.set_linewidth(0)
        if save is not None:
            plt.savefig(save, bbox_inches="tight")
            plt.savefig(save.replace(".png", ".svg"), bbox_inches="tight")
