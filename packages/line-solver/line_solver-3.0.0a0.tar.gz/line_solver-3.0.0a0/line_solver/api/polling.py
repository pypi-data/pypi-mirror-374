
import jpype
import numpy as np
from line_solver import jlineMatrixToArray, jlineMatrixFromArray


def polling_qsys_1limited(arv_maps, svc_maps, switch_maps):
    def convert_to_matrix_cell_array(maps_list):
        java_array = jpype.JArray(jpype.JPackage('jline').util.matrix.MatrixCell)(len(maps_list))
        for i, map_item in enumerate(maps_list):
            if isinstance(map_item, tuple):
                D0, D1 = map_item
                java_cell = jpype.JPackage('jline').util.matrix.MatrixCell(2)
                java_cell.add(jlineMatrixFromArray(D0))
                java_cell.add(jlineMatrixFromArray(D1))
                java_array[i] = java_cell
            else:
                java_array[i] = map_item
        return java_array

    java_arv_maps = convert_to_matrix_cell_array(arv_maps)
    java_svc_maps = convert_to_matrix_cell_array(svc_maps)
    java_switch_maps = convert_to_matrix_cell_array(switch_maps)

    result = jpype.JPackage('jline').api.polling.Polling_qsys_1limitedKt.polling_qsys_1limited(
        java_arv_maps, java_svc_maps, java_switch_maps
    )

    return np.array(result)


def polling_qsys_exhaustive(arv_maps, svc_maps, switch_maps):
    def convert_to_matrix_cell_array(maps_list):
        java_array = jpype.JArray(jpype.JPackage('jline').util.matrix.MatrixCell)(len(maps_list))
        for i, map_item in enumerate(maps_list):
            if isinstance(map_item, tuple):
                D0, D1 = map_item
                java_cell = jpype.JPackage('jline').util.matrix.MatrixCell(2)
                java_cell.add(jlineMatrixFromArray(D0))
                java_cell.add(jlineMatrixFromArray(D1))
                java_array[i] = java_cell
            else:
                java_array[i] = map_item
        return java_array

    java_arv_maps = convert_to_matrix_cell_array(arv_maps)
    java_svc_maps = convert_to_matrix_cell_array(svc_maps)
    java_switch_maps = convert_to_matrix_cell_array(switch_maps)

    result = jpype.JPackage('jline').api.polling.Polling_qsys_exhaustiveKt.polling_qsys_exhaustive(
        java_arv_maps, java_svc_maps, java_switch_maps
    )

    return np.array(result)


def polling_qsys_gated(arv_maps, svc_maps, switch_maps):
    def convert_to_matrix_cell_array(maps_list):
        java_array = jpype.JArray(jpype.JPackage('jline').util.matrix.MatrixCell)(len(maps_list))
        for i, map_item in enumerate(maps_list):
            if isinstance(map_item, tuple):
                D0, D1 = map_item
                java_cell = jpype.JPackage('jline').util.matrix.MatrixCell(2)
                java_cell.add(jlineMatrixFromArray(D0))
                java_cell.add(jlineMatrixFromArray(D1))
                java_array[i] = java_cell
            else:
                java_array[i] = map_item
        return java_array

    java_arv_maps = convert_to_matrix_cell_array(arv_maps)
    java_svc_maps = convert_to_matrix_cell_array(svc_maps)
    java_switch_maps = convert_to_matrix_cell_array(switch_maps)

    result = jpype.JPackage('jline').api.polling.Polling_qsys_gatedKt.polling_qsys_gated(
        java_arv_maps, java_svc_maps, java_switch_maps
    )

    return np.array(result)