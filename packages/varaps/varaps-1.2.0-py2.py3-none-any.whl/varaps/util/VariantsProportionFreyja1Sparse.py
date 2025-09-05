import numpy as np
import pandas as pd
import time
from scipy.sparse import csr_matrix
from scipy.optimize import minimize, minimize_scalar

# import cvxpy as cp  # TODO later: use cvxpy instead of scipy.optimize

import warnings

warnings.filterwarnings("ignore")


# my translation from Marie's R code and Siyen's Python code
class VariantsProportionFreyja1Sparse:
    def __init__(self, X_mask, X, mutationsVariants, tol=1e-4, maxIter=1500, alphaInit=0.05, proportionInit=None, readsCount=None):
        # self.bReadsMutations = readsMutations
        # self.mutations_data = mutation_list
        # self.starts_idx = starts_idx
        # self.ends_idx = ends_idx
        self.X_mask = X_mask
        self.X = X

        # pMutationsVariants: matrix of size nb_Mutations x nb_Variants, values in [0,1]
        self.pMutationsVariants = mutationsVariants

        self.tol = tol
        self.maxIter = maxIter
        # alpha: error rate
        self.alpha = alphaInit
        self.params = proportionInit

        if readsCount is None:
            self.readsCount = np.ones(len(self.X_mask))
        else:
            self.readsCount = np.array(readsCount)
        self.startTime = time.time()

    def __call__(self):
        self._compute_attributes()

    def calculate_mafH(self):
        # count mutations
        self.count_mut = self.readsCount @ self.X
        self.count_tot = self.readsCount @ self.X_mask

        self.mafH = self.count_mut / self.count_tot
        self.mafH[np.isnan(self.mafH)] = 0.0

    def clean_data(self):
        # get rid of unmuted reads
        self.nbMutations = self.pMutationsVariants.shape[0]
        self.nbVariants = self.pMutationsVariants.shape[1]

        self.pMutationsVariantsErr = np.zeros_like(self.pMutationsVariants)

        self.likelihood = []  # stays empty if alpha is fixed

        # remove reads with weight 0
        idx = np.where(self.readsCount != 0)[0]
        self.X_mask = self.X_mask[idx]
        self.X = self.X[idx]
        self.readsCount = self.readsCount[idx]
        self.pReadsVariants = np.zeros((self.X_mask.shape[0], self.pMutationsVariants.shape[1]))
        self.nbReads = self.X_mask.shape[0]

    def _compute_attributes(self):
        # "read only" variables (considered as const)
        self.clean_data()

        # count mutations
        self.calculate_mafH()

        self.nbMutations = self.pMutationsVariants.shape[0]
        self.nbVariants = self.pMutationsVariants.shape[1]

        self.pMutationsVariantsErr = np.zeros_like(self.pMutationsVariants)

        self.likelihood = []  # stays empty if alpha is fixed

    def construct_params_vect(self, x, params):
        # error rate to be fitted
        if len(x) != params[-1].shape[1]:
            return x[:-1], x[-1], *params
        # error rate given and frozen
        else:
            return x, *params

    def kern(self, x, params):
        w, alpha, pm, pw, M = self.construct_params_vect(x, params)
        self.alpha = 1 / (1 + np.exp(-alpha))
        M_ = M - 2 * self.alpha * M + self.alpha
        w_ = np.exp(w)  # newly added: avoid using bounds and constraints
        w_ /= w_.sum()  # newly added: avoid using bounds and constraints
        maf = np.dot(M_, w_)
        return np.sum(np.abs(self.mafH - maf) * self.count_tot)  #### norm 1

    def fit(self, freezeAlpha=False):
        print("Fitting Freyja1Sparse...")
        self.alpha = np.log(self.alpha / (1 - self.alpha))
        if freezeAlpha:  # freeze alpha
            x = np.random.dirichlet(np.ones(self.pMutationsVariants.shape[1]))
            params = [self.alpha, self.count_mut, self.count_tot - self.count_mut, self.pMutationsVariants]

        else:
            x = np.hstack((np.random.dirichlet(np.ones(self.pMutationsVariants.shape[1])), [self.alpha]))
            params = [self.count_mut, self.count_tot - self.count_mut, self.pMutationsVariants]
        res = minimize(
            self.kern,
            x0=x,
            args=(params),
            method="TNC",
            options={"eps": self.tol},
        )
        p1 = res.x[: self.pMutationsVariants.shape[1]]
        self.resNormalised = np.exp(p1)
        self.resNormalised /= self.resNormalised.sum()
        self.solution = self.resNormalised

        self.errAlpha = res.x[self.pMutationsVariants.shape[1] :]
        self.errAlpha = 1 / (1 + np.exp(-self.errAlpha))
        self.params = self.solution
        self.time_used = time.time() - self.startTime
        # print(f"Time used: {self.time_used:.4f} seconds")
        self.time_alpha_fixed = time.time() - self.startTime
        self.averageTimePerIterAlpha = 0.0
        self.averageTimePerIterAlphaFixed = self.time_alpha_fixed
        self.nbIter = 1
        self.time_alpha = time.time() - self.startTime
        self.nbIter_alpha_fixed = 0
        self.nbIter_alpha = 0
        self.averageTimePerIter = (time.time() - self.startTime) / self.nbIter
