# python3 main.py <CTG_SAMPLE_NO> <EPSILON>
# Example: python3 main.py 4 1.25

from CurveToGraph import CurveToGraph

if __name__ == "__main__":

    CTG_SAMPLE_NO = int(sys.argv[1])

    if CTG_SAMPLE_NO == 1:
        ctg = CurveToGraph("sample_files/P", "sample_files/Q")

    elif CTG_SAMPLE_NO == 2:
        ctg = CurveToGraph("sample_files/H", "sample_files/G")

    elif CTG_SAMPLE_NO == 3:
        ctg = CurveToGraph("sample_files/arc_de_triomphe", "sample_files/vehicle_path")

    elif CTG_SAMPLE_NO == 4:
        ctg = CurveToGraph("sample_files/A", "sample_files/B")

    if len(sys.argv) > 2:
        EPSILON = float(sys.argv[2])
        ctg.buildCells()
        ctg.buildFreeSpace(EPSILON)
        ctg.plotFreeSpace()

    else:
        ctg.plot()
