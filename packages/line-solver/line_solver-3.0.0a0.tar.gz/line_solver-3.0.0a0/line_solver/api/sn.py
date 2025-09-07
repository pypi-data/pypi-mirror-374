
import jpype
import numpy as np
from line_solver import jlineMatrixToArray, jlineMatrixFromArray


def sn_deaggregate_chain_results(sn, Lchain, ST, STchain, Vchain, alpha, Qchain, Uchain, Rchain, Tchain, Cchain, Xchain):
    ST_matrix = jlineMatrixFromArray(ST) if ST is not None else None
    Qchain_matrix = jlineMatrixFromArray(Qchain) if Qchain is not None else None
    Uchain_matrix = jlineMatrixFromArray(Uchain) if Uchain is not None else None
    Cchain_matrix = jlineMatrixFromArray(Cchain) if Cchain is not None else None

    result = jpype.JPackage('jline').api.sn.SnDeaggregateChainResultsKt.snDeaggregateChainResults(
        sn,
        jlineMatrixFromArray(Lchain),
        ST_matrix,
        jlineMatrixFromArray(STchain),
        jlineMatrixFromArray(Vchain),
        jlineMatrixFromArray(alpha),
        Qchain_matrix,
        Uchain_matrix,
        jlineMatrixFromArray(Rchain),
        jlineMatrixFromArray(Tchain),
        Cchain_matrix,
        jlineMatrixFromArray(Xchain)
    )

    return {
        'QN': jlineMatrixToArray(result.QN),
        'UN': jlineMatrixToArray(result.UN),
        'RN': jlineMatrixToArray(result.RN),
        'TN': jlineMatrixToArray(result.TN),
        'CN': jlineMatrixToArray(result.CN),
        'XN': jlineMatrixToArray(result.XN),
        'lG': result.lG
    }


def sn_get_arv_r_from_tput(sn, TN=None, TH=None):
    TN_matrix = jlineMatrixFromArray(TN) if TN is not None else None

    result = jpype.JPackage('jline').api.sn.SnGetArvRFromTputKt.snGetArvRFromTput(
        sn, TN_matrix, TH
    )

    return jlineMatrixToArray(result)


def sn_get_demands_chain(sn):
    result = jpype.JPackage('jline').api.sn.SnGetDemandsChainKt.snGetDemandsChain(sn)

    return {
        'Lchain': jlineMatrixToArray(result.Lchain),
        'Nchain': jlineMatrixToArray(result.Nchain),
        'Zchain': jlineMatrixToArray(result.Zchain),
        'refstat': result.refstat,
        'alpha': jlineMatrixToArray(result.alpha),
        'sn': result.sn
    }


def sn_get_node_arv_r_from_tput(sn, TN, TH=None, AN=None):
    AN_matrix = jlineMatrixFromArray(AN) if AN is not None else None

    result = jpype.JPackage('jline').api.sn.SnGetNodeArvRFromTputKt.snGetNodeArvRFromTput(
        sn, jlineMatrixFromArray(TN), TH, AN_matrix
    )

    return jlineMatrixToArray(result)


def sn_get_node_tput_from_tput(sn, TN, TH=None, ANn=None):
    ANn_matrix = jlineMatrixFromArray(ANn) if ANn is not None else None

    result = jpype.JPackage('jline').api.sn.SnGetNodeTputFromTputKt.snGetNodeTputFromTput(
        sn, jlineMatrixFromArray(TN), TH, ANn_matrix
    )

    return jlineMatrixToArray(result)


def sn_get_product_form_chain_params(sn):
    result = jpype.JPackage('jline').api.sn.SnGetProductFormChainParamsKt.snGetProductFormChainParams(sn)

    return {
        'L': jlineMatrixToArray(result.L),
        'N': jlineMatrixToArray(result.N),
        'Z': jlineMatrixToArray(result.Z),
        'mu': jlineMatrixToArray(result.mu),
        'phi': jlineMatrixToArray(result.phi),
        'nservers': jlineMatrixToArray(result.nservers),
        'schedid': jlineMatrixToArray(result.schedid),
        'refstat': result.refstat,
        'sn': result.sn
    }


def sn_get_product_form_params(sn):
    result = jpype.JPackage('jline').api.sn.SnGetProductFormParamsKt.snGetProductFormParams(sn)

    return {
        'L': jlineMatrixToArray(result.L),
        'N': jlineMatrixToArray(result.N),
        'Z': jlineMatrixToArray(result.Z),
        'mu': jlineMatrixToArray(result.mu),
        'phi': jlineMatrixToArray(result.phi),
        'nservers': jlineMatrixToArray(result.nservers),
        'schedid': jlineMatrixToArray(result.schedid),
        'refstat': result.refstat,
        'sn': result.sn
    }


def sn_get_resid_t_from_resp_t(sn, RNclass, WH=None):
    result = jpype.JPackage('jline').api.sn.SnGetResidTFromRespTKt.snGetResidTFromRespT(
        sn, jlineMatrixFromArray(RNclass), WH
    )

    return jlineMatrixToArray(result)


def sn_get_state_aggr(sn):
    result = jpype.JPackage('jline').api.sn.SnGetStateAggrKt.snGetStateAggr(sn)

    state_dict = {}
    for entry in result.entrySet():
        node_key = entry.getKey()
        state_matrix = jlineMatrixToArray(entry.getValue())
        state_dict[node_key] = state_matrix

    return state_dict


def sn_is_state_valid(sn):
    return jpype.JPackage('jline').api.sn.SnIsStateValidKt.snIsStateValid(sn)


def sn_refresh_visits(sn, chains=None, rt=None, rtnodes=None):
    chains_matrix = jlineMatrixFromArray(chains) if chains is not None else None
    rt_matrix = jlineMatrixFromArray(rt) if rt is not None else None
    rtnodes_matrix = jlineMatrixFromArray(rtnodes) if rtnodes is not None else None

    return jpype.JPackage('jline').api.sn.SnRefreshVisitsKt.snRefreshVisits(
        sn, chains_matrix, rt_matrix, rtnodes_matrix
    )


def sn_has_class_switching(sn):
    return jpype.JPackage('jline').api.sn.SnHasClassSwitchingKt.snHasClassSwitching(sn)


def sn_has_fork_join(sn):
    return jpype.JPackage('jline').api.sn.SnHasForkJoinKt.snHasForkJoin(sn)


def sn_has_load_dependence(sn):
    return jpype.JPackage('jline').api.sn.SnHasLoadDependenceKt.snHasLoadDependence(sn)


def sn_has_multi_server(sn):
    return jpype.JPackage('jline').api.sn.SnHasMultiServerKt.snHasMultiServer(sn)


def sn_has_priorities(sn):
    return jpype.JPackage('jline').api.sn.SnHasPrioritiesKt.snHasPriorities(sn)


def sn_has_product_form(sn):
    return jpype.JPackage('jline').api.sn.SnHasProductFormKt.snHasProductForm(sn)


def sn_has_closed_classes(sn):
    return jpype.JPackage('jline').api.sn.SnHasClosedClassesKt.snHasClosedClasses(sn)


def sn_has_open_classes(sn):
    return jpype.JPackage('jline').api.sn.SnHasOpenClassesKt.snHasOpenClasses(sn)


def sn_has_mixed_classes(sn):
    return jpype.JPackage('jline').api.sn.SnHasMixedClassesKt.snHasMixedClasses(sn)


def sn_has_multi_chain(sn):
    return jpype.JPackage('jline').api.sn.SnHasMultiChainKt.snHasMultiChain(sn)


def sn_is_closed_model(sn):
    return jpype.JPackage('jline').api.sn.SnIsClosedModelKt.snIsClosedModel(sn)


def sn_is_open_model(sn):
    return jpype.JPackage('jline').api.sn.SnIsOpenModelKt.snIsOpenModel(sn)


def sn_is_mixed_model(sn):
    return jpype.JPackage('jline').api.sn.SnIsMixedModelKt.snIsMixedModel(sn)


def sn_has_product_form_except_multi_class_heter_exp_fcfs(sn):
    return jpype.JPackage('jline').api.sn.SnHasProductFormExceptMultiClassHeterExpFCFSKt.snHasProductFormExceptMultiClassHeterExpFCFS(sn)


def sn_print_routing_matrix(sn, onlyclass=None):
    jpype.JPackage('jline').api.sn.SnPrintRoutingMatrixKt.snPrintRoutingMatrix(sn, onlyclass)


def sn_has_fcfs(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasFCFSKt.snHasFCFS(sn))


def sn_has_lcfs(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasLCFSKt.snHasLCFS(sn))


def sn_has_lcfspr(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasLCFSPRKt.snHasLCFSPR(sn))


def sn_has_ps(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasPSKt.snHasPS(sn))


def sn_has_dps(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasDPSKt.snHasDPS(sn))


def sn_has_gps(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasGPSKt.snHasGPS(sn))


def sn_has_inf(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasINFKt.snHasINF(sn))


def sn_has_hol(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasHOLKt.snHasHOL(sn))


def sn_has_sjf(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasSJFKt.snHasSJF(sn))


def sn_has_ljf(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasLJFKt.snHasLJF(sn))


def sn_has_sept(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasSEPTKt.snHasSEPT(sn))


def sn_has_lept(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasLEPTKt.snHasLEPT(sn))


def sn_has_siro(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasSIROKt.snHasSIRO(sn))


def sn_has_dps_prio(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasDPSPRIOKt.snHasDPSPRIO(sn))


def sn_has_gps_prio(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasGPSPRIOKt.snHasGPSPRIO(sn))


def sn_has_ps_prio(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasPSPRIOKt.snHasPSPRIO(sn))


def sn_has_single_class(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasSingleClassKt.snHasSingleClass(sn))


def sn_has_single_chain(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasSingleChainKt.snHasSingleChain(sn))


def sn_has_fractional_populations(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasFractionalPopulationsKt.snHasFractionalPopulations(sn))


def sn_has_multiple_closed_classes(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasMultipleClosedClassesKt.snHasMultipleClosedClasses(sn))


def sn_has_multiclass_fcfs(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasMultiClassFCFSKt.snHasMultiClassFCFS(sn))


def sn_has_multiclass_heter_fcfs(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasMultiClassHeterFCFSKt.snHasMultiClassHeterFCFS(sn))


def sn_has_multiclass_heter_exp_fcfs(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasMultiClassHeterExpFCFSKt.snHasMultiClassHeterExpFCFS(sn))


def sn_has_homogeneous_scheduling(sn, strategy):
    return bool(jpype.JPackage('jline').api.sn.SnHasHomogeneousSchedulingKt.snHasHomogeneousScheduling(sn, strategy))


def sn_has_multi_class(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasMultiClassKt.snHasMultiClass(sn))


def sn_chain_analysis(sn, options=None):
    if options is None:
        options = {}

    java_result = jpype.JPackage('jline').api.sn.SnChainAnalysisKt.snChainAnalysis(sn, options)

    return {
        'chain_info': dict(java_result.getChainInfo()),
        'analysis_result': dict(java_result.getAnalysisResult())
    }


def sn_get_demands(sn, options=None):
    if options is None:
        options = {}

    from .. import jlineMatrixToArray

    java_result = jpype.JPackage('jline').api.sn.SnGetDemandsKt.snGetDemands(sn, options)

    D = jlineMatrixToArray(java_result.getD())
    ST = jlineMatrixToArray(java_result.getST())
    V = jlineMatrixToArray(java_result.getV())

    return D, ST, V


def sn_get_visits_chain(sn, options=None):
    if options is None:
        options = {}

    from .. import jlineMatrixToArray

    java_result = jpype.JPackage('jline').api.sn.SnGetVisitsChainKt.snGetVisitsChain(sn, options)

    return jlineMatrixToArray(java_result)


def sn_check_balance(sn, options=None):
    if options is None:
        options = {}

    java_result = jpype.JPackage('jline').api.sn.SnCheckBalanceKt.snCheckBalance(sn, options)

    return {
        'is_balanced': bool(java_result.isBalanced()),
        'violations': list(java_result.getViolations()),
        'details': dict(java_result.getDetails())
    }


def sn_check_consistency(sn, options=None):
    if options is None:
        options = {}

    java_result = jpype.JPackage('jline').api.sn.SnCheckConsistencyKt.snCheckConsistency(sn, options)

    return {
        'is_consistent': bool(java_result.isConsistent()),
        'errors': list(java_result.getErrors()),
        'warnings': list(java_result.getWarnings()),
        'details': dict(java_result.getDetails())
    }


def sn_check_feasibility(sn, options=None):
    if options is None:
        options = {}

    java_result = jpype.JPackage('jline').api.sn.SnCheckFeasibilityKt.snCheckFeasibility(sn, options)

    return {
        'is_feasible': bool(java_result.isFeasible()),
        'issues': list(java_result.getIssues()),
        'recommendations': list(java_result.getRecommendations())
    }


def sn_has_blocking(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasBlockingKt.snHasBlocking(sn))


def sn_has_caches(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasCachesKt.snHasCaches(sn))


def sn_has_delays(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasDelaysKt.snHasDelays(sn))


def sn_has_finite_capacity(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasFiniteCapacityKt.snHasFiniteCapacity(sn))


def sn_has_loadindep(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasLoadindepKt.snHasLoadindep(sn))


def sn_has_state_dependent(sn):
    return bool(jpype.JPackage('jline').api.sn.SnHasStateDependentKt.snHasStateDependent(sn))


def sn_validate_model(sn, options=None):
    if options is None:
        options = {}

    java_result = jpype.JPackage('jline').api.sn.SnValidateModelKt.snValidateModel(sn, options)

    return {
        'is_valid': bool(java_result.isValid()),
        'consistency': dict(java_result.getConsistency()),
        'feasibility': dict(java_result.getFeasibility()),
        'balance': dict(java_result.getBalance()),
        'summary': dict(java_result.getSummary())
    }