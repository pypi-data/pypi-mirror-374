import numpy as np
import pandas as pd
import time

from scipy.optimize import minimize, minimize_scalar
import warnings

warnings.filterwarnings("ignore")


# my translation from Marie's R code and Siyen's Python code
class VariantsProportionFreyjaSparse:
    def __init__(
        self,
        starts_idx,
        ends_idx,
        mutation_list,
        mutationsVariants,
        tol=1e-3,
        maxIter=200,
        alphaInit=0.05,
        proportionInit=None,
        readsCount=None,
    ):
        # self.bReadsMutations = readsMutations
        self.mutations_data = mutation_list
        self.starts_idx = starts_idx
        self.ends_idx = ends_idx

        # pMutationsVariants: matrix of size nb_Mutations x nb_Variants, values in [0,1]
        self.pMutationsVariants = mutationsVariants

        self.tol = tol
        self.maxIter = maxIter
        # alpha: error rate
        self.alpha = alphaInit
        self.params = proportionInit

        if readsCount is None:
            self.readsCount = np.ones(len(self.starts_idx))
        else:
            self.readsCount = readsCount
        self.startTime = time.time()

    def __call__(self):
        self._compute_attributes()

    def calculate_mafH(self):
        # count mutations
        self.count_mut = np.zeros(self.nbMutations)
        self.count_tot = np.zeros(self.nbMutations)
        for i in range(self.nbMutations):
            res_mut = 0
            res_tot = 0
            for k in range(self.nbReads):
                if i >= self.starts_idx[k] and i < self.ends_idx[k]:
                    res_tot += self.readsCount[k]
                    if i in self.mutations_data[k]:
                        res_mut += self.readsCount[k]
            self.count_mut[i] = res_mut
            self.count_tot[i] = res_tot
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
        self.mutations_data = self.mutations_data[idx]
        self.starts_idx = self.starts_idx[idx]
        self.ends_idx = self.ends_idx[idx]
        self.readsCount = self.readsCount[idx]
        self.pReadsVariants = np.zeros((self.starts_idx.shape[0], self.pMutationsVariants.shape[1]))
        self.nbReads = self.starts_idx.shape[0]

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
        w = np.clip(w, -709.78, 709.78)
        self.alpha = 1 / (1 + np.exp(-alpha))
        M_ = M - 2 * self.alpha * M + self.alpha
        w_ = np.exp(w)  # newly added: avoid using bounds and constraints
        w_ /= w_.sum()  # newly added: avoid using bounds and constraints
        maf = np.dot(M_, w_)
        return (((self.mafH - maf) * np.log2(self.count_tot + 1)) ** 2).sum()

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
        )
        p1 = res.x[: self.pMutationsVariants.shape[1]]
        self.resNormalised = np.exp(p1)
        self.resNormalised /= self.resNormalised.sum()
        self.solution = self.resNormalised

        self.errAlpha = res.x[self.pMutationsVariants.shape[1] :]
        self.errAlpha = 1 / (1 + np.exp(-self.errAlpha))
        self.params = self.solution
        self.time_used = time.time() - self.startTime
        self.time_alpha_fixed = time.time() - self.startTime
        self.averageTimePerIterAlpha = 0.0
        self.averageTimePerIterAlphaFixed = self.time_alpha_fixed
        self.nbIter = 1
        self.time_alpha = time.time() - self.startTime
        self.nbIter_alpha_fixed = 0
        self.nbIter_alpha = 0
        self.averageTimePerIter = (time.time() - self.startTime) / self.nbIter
