import numpy as np
import pandas as pd
from scipy.optimize import minimize, minimize_scalar
import time
import os
import psutil

try:
    from pympler.asizeof import asizeof  # type: ignore
except Exception:  # pragma: no cover

    def asizeof(_obj):
        return -1


def _proc_mem_mb():
    return psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024


def _print_mem(label: str, **objs):
    # debug memory prints disabled
    return


# my translation from Marie's R code and Siyen's Python code
class VariantsProportionCoOcc:
    def __init__(
        self,
        starts_idx,
        ends_idx,
        mutation_list,
        mutationsVariants,
        X_mask=None,
        X=None,
        tol=1e-4,
        maxIter=1500,
        alphaInit=0.05,
        proportionInit=None,
        readsCount=None,
    ):
        # self.bReadsMutations = readsMutations
        self.mutations_data = mutation_list
        self.starts_idx = starts_idx
        self.ends_idx = ends_idx
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
        self.readsCount = readsCount
        self.startTime = time.time()

    def __call__(self):
        self._compute_attributes()

    def _compute_attributes(self):
        # "read only" variables (considered as const)
        # get rid of unmuted reads
        readsToKeep = []
        # for i in range(self.bReadsMutations.shape[0]):
        #     if (self.readsCount[i] != 0) and (not np.isnan(self.bReadsMutations[i, :]).all()):
        #         readsToKeep.append(i)
        # self.bReadsMutations = self.bReadsMutations[readsToKeep, :]
        # self.readsCount = self.readsCount[readsToKeep]
        # mutsToKeep = np.where(~np.isnan(self.bReadsMutations).all(axis=0))[0]
        # self.bReadsMutations = self.bReadsMutations[:, mutsToKeep]
        # self.pMutationsVariants = self.pMutationsVariants[mutsToKeep, :]

        # self.maskedMuted = np.ma.array(self.bReadsMutations, mask=np.isnan(self.bReadsMutations))
        # self.maskedUnmuted = np.ma.array(1 - self.bReadsMutations, mask=np.isnan(self.bReadsMutations))

        self.nbMutations = self.pMutationsVariants.shape[0]
        self.nbVariants = self.pMutationsVariants.shape[1]
        self.nbReads = self.starts_idx.shape[0]
        self.pMutationsVariantsErr = np.zeros_like(self.pMutationsVariants)
        self.pReadsVariants = np.zeros((self.starts_idx.shape[0], self.pMutationsVariants.shape[1]))
        self.likelihood = []  # stays empty if alpha is fixed
        self.neg_log_res_temp = np.zeros((self.nbReads, self.nbVariants))
        self.neg_log_res = np.zeros(self.nbReads)

    def initialise_parametres(self):
        # init proportions vector
        if self.params is None:
            # self.params = np.ones(self.nbVariants) / self.nbVariants
            self.params = np.random.dirichlet(np.ones(self.nbVariants))
        # init alpha
        if not (isinstance(self.alpha, float) or isinstance(self.alpha, int)):
            self.alpha = 0.01
        # init errored mutation/variant proportions matrix (abbr. to errored mat below)
        self.compute_pMutationsVariantsErr(self.alpha)  # *

    def compute_pMutationsVariantsErr(self, alpha, inplace=True):
        if inplace:
            self.pMutationsVariantsErr = self.pMutationsVariants * (1 - 2 * alpha) + alpha
            self.one_minus_pMutationsVariantsErr = 1 - self.pMutationsVariantsErr
        else:
            return self.pMutationsVariants * (1 - 2 * alpha) + alpha

    def compute_expectation_helper(self, pMutationsVariantsErr, one_minus_pMutationsVariantsErr):
        start_time = time.time()
        self.temp_Tkj = np.ones((self.nbReads, self.nbVariants))
        for k in range(self.pReadsVariants.shape[0]):
            self.temp_Tkj[k] *= np.prod(pMutationsVariantsErr[self.X[k]], axis=0) * np.prod(one_minus_pMutationsVariantsErr[self.X_mask[k] & ~self.X[k]], axis=0)
        # Product of pMutationsVariantsErr over the variants that are TRUE in self.X
        # prod_selected = np.prod(pMutationsVariantsErr[None, :, :], axis=1, where=self.X[:, :, None])  # → shape (N, F)  # expand to (1, V, F)  # (N, V, 1) broadcast

        # # Product of (1-p) over the variants that are TRUE in self.X_mask
        # prod_not_selected = np.prod(one_minus_pMutationsVariantsErr[None, :, :], axis=1, where=self.X_mask[:, :, None])

        # # Update every row at once
        # self.temp_Tkj *= prod_selected * prod_not_selected

        # for k in range(self.pReadsVariants.shape[0]):
        #     for i_item, mutations_data_item in enumerate(self.mutations_data[k]):
        #         if mutations_data_item:
        #             unmuted_idx = [x for x in range(self.starts_idx[k][i_item], self.ends_idx[k][i_item]) if x not in mutations_data_item]
        #             self.temp_Tkj[k] *= np.prod(pMutationsVariantsErr[list(mutations_data_item)], axis=0) * np.prod(one_minus_pMutationsVariantsErr[unmuted_idx], axis=0)
        #         else:
        #             self.temp_Tkj[k] *= np.prod(
        #                 one_minus_pMutationsVariantsErr[self.starts_idx[k][i_item] : self.ends_idx[k][i_item]],
        #                 axis=0,
        #             )
        # dur = time.time() - start_time
        # _print_mem("CoOcc: after compute_expectation_helper", temp_Tkj=self.temp_Tkj)
        # print(f"[TIMER] compute_expectation_helper | {dur:.4f}s | RSS={_proc_mem_mb():.2f} MB")

    def compute_expectation(self):  # , pMutationsVariantsErr
        """
        Expectation-step
        """
        self.pReadsVariants = self.temp_Tkj * self.params
        # for k in range(self.pReadsVariants.shape[0]):
        #     if self.mutations_data[k]:
        #         unmuted_idx = [x for x in range(self.starts_idx[k], self.ends_idx[k]) if x not in self.mutations_data[k]]
        #         self.pReadsVariants[k] = np.prod(pMutationsVariantsErr[list(self.mutations_data[k])], axis=0)  * np.prod(one_minus_pMutationsVariantsErr[unmuted_idx], axis=0) * self.params
        #     else:
        #         self.pReadsVariants[k] = np.prod(one_minus_pMutationsVariantsErr[self.starts_idx[k]: self.ends_idx[k]], axis = 0) * self.params

        self.pReadsVariants /= np.sum(self.pReadsVariants, axis=1, keepdims=True)

    def maximise_expectation(self, freezeAlpha):
        """
        Maximisation-step
        """
        # MODIFYME: weighted avg
        # currentProportion = np.nanmean(self.pReadsVariants,axis=0)
        currentProportion = (self.readsCount.reshape(-1, 1) * self.pReadsVariants).sum(axis=0) / self.readsCount.sum()
        resid = np.nanmax(np.abs(currentProportion - self.params))

        # update params
        self.params = currentProportion

        if not freezeAlpha:
            self.logparams = np.log(self.params)
            alpha = np.log(self.alpha / (1 - self.alpha))
            # res = minimize(self.neg_log_likelihood, alpha, method="L-BFGS-B")  # , bounds=[(0,0.3)] #*
            res = minimize(self.neg_log_likelihood, alpha)  # , bounds=[(0,0.3)] #*

            # update errored mat (with the updated alpha)
            self.alpha = 1 / (1 + np.exp(-res.x[0]))  # *
            pMutationsVariantsErr = self.compute_pMutationsVariantsErr(self.alpha, inplace=False)  # *

            # append the neg_log_likelihood evaluated on new alpha
            self.likelihood.append(self.neg_log_likelihood(np.log(self.alpha / (1 - self.alpha))))
            self.pMutationsVariantsErr = pMutationsVariantsErr
            self.one_minus_pMutationsVariantsErr = 1 - self.pMutationsVariantsErr
            # no per-iteration mem prints inside alpha loop
            return resid, pMutationsVariantsErr

        return resid, self.pMutationsVariantsErr

    def neg_log_likelihood(self, preAlpha):
        # TODO: try transpose alpha so that we don't need to put hard constraint? #*
        alpha = 1 / (1 + np.exp(-preAlpha))  # *
        # compute errored mat using the given alpha
        # ATTENTION!!! DO NOT modifiy the matrix INPLACE on self!!!
        pMutationsVariantsErr = self.pMutationsVariants * (1 - 2 * alpha) + alpha
        # shape of log(Un)Muted: (nbMutations, nbVariants)
        log_pMutationsVariantsErr = np.log(pMutationsVariantsErr)
        log_one_minus_pMutationsVariantsErr = np.log(1 - pMutationsVariantsErr)

        ## numpy masked scalar product
        # logMuted = np.ma.dot(self.maskedMuted, log_pMutationsVariantsErr)
        # logUnmuted = np.ma.dot(self.maskedUnmuted, log_one_minus_pMutationsVariantsErr)
        # MODIFYME: weighted pReadsVariants instead of simple pReadsVariants
        # res = np.nansum(self.pReadsVariants * (logMuted.data+logUnmuted.data+np.log(self.params.reshape(1,-1))),
        #                axis=0)

        for k in range(self.pReadsVariants.shape[0]):
            # self.neg_log_res[k] = np.sum(self.pReadsVariants[k] *(self.logparams + np.sum(log_pMutationsVariantsErr[list(self.mutations_data[k])]) + np.sum(log_one_minus_pMutationsVariantsErr[unmuted_idx])))
            self.neg_log_res_temp[k] = np.sum(log_pMutationsVariantsErr[self.X[k]], axis=0) + np.sum(log_one_minus_pMutationsVariantsErr[self.X_mask[k] & ~self.X[k]], axis=0)

        # for k in range(self.pReadsVariants.shape[0]):
        #     if self.mutations_data[k]:
        #         unmuted_idx = [x for x in range(self.starts_idx[k], self.ends_idx[k]) if x not in self.mutations_data[k]]
        #         # self.neg_log_res[k] = np.sum(self.pReadsVariants[k] *(self.logparams + np.sum(log_pMutationsVariantsErr[list(self.mutations_data[k])]) + np.sum(log_one_minus_pMutationsVariantsErr[unmuted_idx])))
        #         self.neg_log_res_temp[k] = np.sum(log_pMutationsVariantsErr[list(self.mutations_data[k])], axis=0) + np.sum(log_one_minus_pMutationsVariantsErr[unmuted_idx], axis=0)
        #     else:
        #         # self.neg_log_res[k] = np.sum(self.pReadsVariants[k] *(self.logparams + np.sum(log_one_minus_pMutationsVariantsErr[self.starts_idx[k]: self.ends_idx[k]])))
        #         self.neg_log_res_temp[k] = np.sum(
        #             log_one_minus_pMutationsVariantsErr[self.starts_idx[k] : self.ends_idx[k]],
        #             axis=0,
        #         )
        res = np.sum(np.sum(self.pReadsVariants * (self.neg_log_res_temp + self.logparams), axis=1) * self.readsCount)
        return -res

    # def neg_log_likelihood(self, preAlpha):
    #     # TODO: try transpose alpha so that we don't need to put hard constraint? #*
    #     alpha = 1 / (1 + np.exp(-preAlpha))  # *
    #     # compute errored mat using the given alpha
    #     # ATTENTION!!! DO NOT modifiy the matrix INPLACE on self!!!
    #     pMutationsVariantsErr = self.pMutationsVariants * (1 - 2 * alpha) + alpha
    #     # shape of log(Un)Muted: (nbMutations, nbVariants)
    #     log_pMutationsVariantsErr = np.log(pMutationsVariantsErr)
    #     log_one_minus_pMutationsVariantsErr = np.log(1 - pMutationsVariantsErr)

    #     ## numpy masked scalar product
    #     # logMuted = np.ma.dot(self.maskedMuted, log_pMutationsVariantsErr)
    #     # logUnmuted = np.ma.dot(self.maskedUnmuted, log_one_minus_pMutationsVariantsErr)
    #     # MODIFYME: weighted pReadsVariants instead of simple pReadsVariants
    #     # res = np.nansum(self.pReadsVariants * (logMuted.data+logUnmuted.data+np.log(self.params.reshape(1,-1))),
    #     #                axis=0)
    #     for k in range(self.pReadsVariants.shape[0]):
    #         if self.mutations_data[k]:
    #             unmuted_idx = [x for x in range(self.starts_idx[k], self.ends_idx[k]) if x not in self.mutations_data[k]]
    #             self.neg_log_res[k] = np.sum(self.pReadsVariants[k] *(self.logparams + np.sum(log_pMutationsVariantsErr[list(self.mutations_data[k])]) + np.sum(log_one_minus_pMutationsVariantsErr[unmuted_idx])))
    #         else:
    #             self.neg_log_res[k] = np.sum(self.pReadsVariants[k] *(self.logparams + np.sum(log_one_minus_pMutationsVariantsErr[self.starts_idx[k]: self.ends_idx[k]])))
    #     res = self.neg_log_res * self.readsCount
    #     res = np.sum(res)
    #     return -res

    def fit(self, warmStart=False, freezeAlpha=True):
        # initialisation
        if not warmStart:
            self.initialise_parametres()

        t0 = time.time()
        pMutationsVariantsErr = self.compute_pMutationsVariantsErr(self.alpha, inplace=False)  # *
        one_minus_pMutationsVariantsErr = 1 - pMutationsVariantsErr
        self.compute_expectation_helper(pMutationsVariantsErr, one_minus_pMutationsVariantsErr)
        # print(f"[TIMER] init E-helper | {time.time()-t0:.4f}s | RSS={_proc_mem_mb():.2f} MB")

        c = 0
        c_alpha = 0
        self.PARAMS_HIST.append(self.params)

        while c < self.maxIter:
            # print('iteration number %d...' % (c+1))

            # E-step
            # print('\nExpectation step')
            # tt = time.time()
            self.compute_expectation()  # self.pMutationsVariantsErr
            # print('done in %.2f seconds.' % (time.time()-tt))

            # M-step
            # print('\nMaximisation step')
            # tt = time.time()
            resid, pMutationsVariantsErr = self.maximise_expectation(True)
            # print('done in %.2f seconds.' % (time.time()-tt))
            # check convergence
            if (resid < self.tol) and (c > 2):  # *:
                # print('parametres change little.')
                break

            c += 1
            self.PARAMS_HIST.append(self.params)
        self.time_alpha_fixed = time.time() - self.startTime

        self.startTimeAlpha = time.time()
        while (not freezeAlpha) and (c_alpha < self.maxIter):
            # print('iteration number %d...' % (c+1))

            # E-step
            # print('\nExpectation step')
            # tt = time.time()

            # print('done in %.2f seconds.' % (time.time()-tt))

            # M-step
            # print('\nMaximisation step')
            # tt = time.time()
            resid, pMutationsVariantsErr = self.maximise_expectation(freezeAlpha)
            # print('done in %.2f seconds.' % (time.time()-tt))
            # check convergence
            if (resid < self.tol) and (c_alpha > 2):  # *:
                # print('parametres change little.')
                break

            c_alpha += 1
            self.compute_expectation_helper(pMutationsVariantsErr, 1 - pMutationsVariantsErr)
            self.compute_expectation()  # self.pMutationsVariantsErr

        self.time_alpha = time.time() - self.startTimeAlpha
        self.nbIter_alpha_fixed = c
        self.nbIter_alpha = c_alpha
        self.averageTimePerIterAlphaFixed = self.time_alpha_fixed / c
        if c_alpha:
            self.averageTimePerIterAlpha = self.time_alpha / c_alpha
        else:
            self.averageTimePerIterAlpha = 0.0
        self.time_used = self.time_alpha_fixed + self.time_alpha
        if freezeAlpha:
            print(f"CoOcc exited successfully. Number of iterations: {c+1}")
        else:
            print(f"CoOcc exited successfully. Number of iterations: {c+1} + {c_alpha+1}")
        return None
