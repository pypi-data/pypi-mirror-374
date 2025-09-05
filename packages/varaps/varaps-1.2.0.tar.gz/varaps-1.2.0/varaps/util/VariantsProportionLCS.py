import numpy as np
import pandas as pd
from scipy.optimize import minimize
import time
import psutil

# from varaps2.util.mode2 import _proc_mem_mb

# my translation from Marie's R code and Siyen's Python code


class VariantsProportionLCS:
    def __init__(self, X_mask, X, mutationsVariants, tol=1e-4, maxIter=1500, alphaInit=0.05, proportionInit=None, readsCount=None):
        # self.bReadsMutations = readsMutations
        self.X_mask = X_mask
        self.X = X
        # pMutationsVariants: matrix of size nb_Mutations x nb_Variants, values in [0,1]
        self.pMutationsVariants = mutationsVariants

        self.tol = tol
        self.maxIter = maxIter
        # alpha: error rate
        self.alpha = alphaInit
        self.params = proportionInit
        self.PARAMS_HIST = []
        if readsCount is None:
            self.readsCount = np.ones(len(self.starts_idx), dtype=np.uint32)
        else:
            self.readsCount = readsCount
        self.startTime = time.time()

    def __call__(self):
        self._compute_attributes()

    # def count_mutations(self):
    #     # get rid of unmuted reads
    #     readsToKeep = []
    #     for i in range(self.bReadsMutations.shape[0]):
    #         if (self.readsCount[i] != 0) and (not np.isnan(self.bReadsMutations[i, :]).all()):
    #             readsToKeep.append(i)
    #     self.bReadsMutations = self.bReadsMutations[readsToKeep, :]
    #     self.readsCount = self.readsCount[readsToKeep]
    #     mutsToKeep = np.where(~np.isnan(self.bReadsMutations).all(axis=0))[0]
    #     self.bReadsMutations = self.bReadsMutations[:, mutsToKeep]
    #     self.pMutationsVariants = self.pMutationsVariants[mutsToKeep, :]
    #     # count mutations
    #     self.mutationCounts = np.zeros((self.pMutationsVariants.shape[0], 2))
    #     self.mutationCounts[:, 0] = np.nansum(self.bReadsMutations * self.readsCount.reshape(-1, 1), axis=0)  # muted counts
    #     self.mutationCounts[:, 1] = np.nansum((1 - self.bReadsMutations) * self.readsCount.reshape(-1, 1), axis=0)  # unmuted counts
    def clean_data(self):
        # get rid of unmuted reads
        self.nbMutations = self.pMutationsVariants.shape[0]
        self.nbVariants = self.pMutationsVariants.shape[1]

        self.pMutationsVariantsErr = np.zeros_like(self.pMutationsVariants)

        self.likelihood = []  # stays empty if alpha is fixed

        # remove reads with weight 0
        # print("self.readsCount.shape", self.readsCount.shape)
        # print("self.readsCount", self.readsCount)
        # get index of reads with weight > 0
        # idx = np.where(self.readsCount != 0)[0]
        # print("idx", idx)
        # self.mutations_data = self.mutations_data[idx]
        # self.starts_idx = self.starts_idx[idx]
        # self.ends_idx = self.ends_idx[idx]
        # self.readsCount = self.readsCount[idx]
        # self.pReadsVariants = np.zeros((self.starts_idx.shape[0], self.pMutationsVariants.shape[1]))
        # Be robust if self.X has been released to save memory
        self.nbReads = self.X.shape[0] if getattr(self, "X", None) is not None else int(self.readsCount.shape[0])

    def count_mutations(self):
        # count mutations
        # self.count_mut = np.zeros(self.nbMutations)
        # self.count_unmut = np.zeros(self.nbMutations)
        # for i in range(self.nbMutations):
        #     res_mut = 0
        #     res_unmut = 0
        #     for k in range(self.nbReads):
        #         for i_item, mutations_data_item in enumerate(self.mutations_data[k]):
        #             if i >= self.starts_idx[k][i_item] and i < self.ends_idx[k][i_item]:
        #                 if i in mutations_data_item:
        #                     res_mut += self.readsCount[k]
        #                 else:
        #                     res_unmut += self.readsCount[k]
        #     self.count_mut[i] = res_mut
        #     self.count_unmut[i] = res_unmut
        #     self.mutationCounts_sum = np.sum(self.count_mut) + np.sum(self.count_unmut)
        # Use matrix-vector products to avoid allocating large broadcasted intermediates
        # Shapes: (nbReads,) @ (nbReads, nbMutations) -> (nbMutations,)
        self.count_mut = self.readsCount @ self.X
        self.count_covered = self.readsCount @ self.X_mask
        self.count_unmut = self.count_covered - self.count_mut
        self.mutationCounts_sum = np.sum(self.count_mut) + np.sum(self.count_unmut)

        # Release large matrices early to drastically reduce peak memory usage
        del self.X
        del self.X_mask

    def _compute_attributes(self):
        # "read only" variables (considered as const)
        self.clean_data()
        self.count_mutations()
        self.nbMutations = self.pMutationsVariants.shape[0]
        self.nbVariants = self.pMutationsVariants.shape[1]

        self.pMutationsVariantsErr = np.zeros_like(self.pMutationsVariants)

        self.likelihood = []  # stays empty if alpha is fixed

    def initialise_parametres(self):
        # init proportions vector
        # self.params = np.ones(self.nbVariants) / self.nbVariants
        self.params = np.random.dirichlet(np.ones(self.nbVariants))
        # init alpha
        if not (isinstance(self.alpha, float) or isinstance(self.alpha, int)):
            self.alpha = 0.05
        # init errored mutation/variant proportions matrix (abbr. to errored mat below)
        self.compute_pMutationsVariantsErr(self.alpha)  # *

    def compute_pMutationsVariantsErr(self, alpha, inplace=True):
        if inplace:
            self.pMutationsVariantsErr = self.pMutationsVariants * (1 - 2 * alpha) + alpha
        else:
            return self.pMutationsVariants * (1 - 2 * alpha) + alpha

    def compute_expectation(self, pMutationsVariantsErr, one_minus_pMutationsVariantsErr):
        """
        Expectation-step: less information given
        """
        # (un)muted: of shape (nbMutations, nbVariants)
        ## self.params: from last iteration
        ## pMutationsVariantsErr: by alpha from last iteration (const if alpha frozen)
        unmuted = one_minus_pMutationsVariantsErr * self.params.reshape(1, -1)
        muted = pMutationsVariantsErr * self.params.reshape(1, -1)

        # normalisation
        unmuted /= unmuted.sum(axis=1).reshape(-1, 1)
        muted /= muted.sum(axis=1).reshape(-1, 1)

        res = muted * self.count_mut.reshape(-1, 1) + unmuted * self.count_unmut.reshape(-1, 1)
        return res, muted, unmuted

    def maximise_expectation(self, pVariants, muted, unmuted, freezeAlpha):
        """
        Maximisation-step: less information given
        """
        currentProportion = pVariants.sum(axis=0) / self.mutationCounts_sum
        resid = np.nanmax(np.abs(currentProportion - self.params))

        # update params
        self.params = currentProportion

        if not freezeAlpha:
            ## at entry of minimize
            # self.alpha: from last iteration
            # mutationCounts: const
            # muted, unmuted: from E-step, computed with self.params and self.alpha BEFORE update
            alpha = np.log(self.alpha / (1 - self.alpha))  # *
            res = minimize(self.neg_log_likelihood, alpha, args=(muted, unmuted), method="L-BFGS-B")  # , bounds=[(0,0.3)] #*
            # update alpha
            self.alpha = 1 / (1 + np.exp(-res.x[0]))  # *

            # update errored mat (with the updated alpha)
            pMutationsVariantsErr = self.compute_pMutationsVariantsErr(self.alpha, inplace=False)  # *

            return resid, pMutationsVariantsErr

        return resid, self.pMutationsVariantsErr

    def neg_log_likelihood(self, preAlpha, muted, unmuted):
        # TODO: try transpose alpha so that we don't need to put hard constraint? #*
        alpha = 1 / (1 + np.exp(-preAlpha))  # *
        # compute errored mat using the given alpha
        # ATTENTION!!! DO NOT modifiy the matrix INPLACE on self!!!
        pMutationsVariantsErr = self.pMutationsVariants * (1 - 2 * alpha) + alpha

        tmpMuted = muted * self.count_mut.reshape(-1, 1) * np.log(pMutationsVariantsErr)
        tmpUnmuted = unmuted * self.count_unmut.reshape(-1, 1) * np.log(1 - pMutationsVariantsErr)

        # scalar value to be minimised
        return -np.nansum(tmpMuted + tmpUnmuted)

    def fit(self, warmStart=False, freezeAlpha=True):
        # initialisation
        if not warmStart:
            self.initialise_parametres()

        pMutationsVariantsErr = self.compute_pMutationsVariantsErr(self.alpha, inplace=False)  # *
        one_minus_pMutationsVariantsErr = 1 - pMutationsVariantsErr

        c = 0
        while c < self.maxIter:
            # print('iteration number %d...' % (c+1))
            # E-step
            expectedProportion, muted, unmuted = self.compute_expectation(pMutationsVariantsErr, one_minus_pMutationsVariantsErr)  # self.pMutationsVariantsErr

            # M-step
            resid, pMutationsVariantsErr = self.maximise_expectation(expectedProportion, muted, unmuted, freezeAlpha)

            # append the neg_log_likelihood evaluated on new alpha
            self.likelihood.append(self.neg_log_likelihood(np.log(self.alpha / (1 - self.alpha)), muted, unmuted))

            # check convergence
            if (resid < self.tol) and (c > 2):  # *:
                break

            c += 1
            # print('------------------------------')
        self.time_alpha_fixed = time.time() - self.startTime
        self.averageTimePerIterAlpha = 0.0
        self.averageTimePerIterAlphaFixed = self.time_alpha_fixed / c
        print("LCS exit successfully. Number of iterations: %d" % (c))
        self.nbIter = c
        self.time_alpha = time.time() - self.startTime
        self.nbIter_alpha_fixed = c
        self.nbIter_alpha = c
        self.averageTimePerIter = (time.time() - self.startTime) / self.nbIter
        self.time_used = time.time() - self.startTime
        return None
