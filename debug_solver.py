import math
import numpy as np
import iric
import sys

print("----------Start----------")

###############################################################################
# CGNSを開く
###############################################################################

# iRICで動かす時用
# =============================================================================
if len(sys.argv) < 2:
    print("Error: CGNS file name not specified.")
    exit()

cgns_name = sys.argv[1]

print("CGNS file name: " + cgns_name)

# CGNSをオープン
fid = iric.cg_iRIC_Open(cgns_name, iric.IRIC_MODE_MODIFY)

# コマンドラインで動かす時用
# =============================================================================

# CGNSをオープン
# fid = iric.cg_iRIC_Open("./project/Case1.cgn", iric.IRIC_MODE_MODIFY)

###############################################################################
# 計算条件を読み込み
###############################################################################

# 格子サイズを読み込み
isize, jsize = iric.cg_iRIC_Read_Grid2d_Str_Size(fid)

# 計算時間を読み込み
time_end = iric.cg_iRIC_Read_Integer(fid, "time_end")

# 読み込んだ格子サイズをコンソールに出力
print("Grid size:")
print("    isize= " + str(isize))
print("    jsize= " + str(jsize))

# 各値を何種出すか読み込み
n_n_scalar_r = iric.cg_iRIC_Read_Integer(fid, "n_n_scalar_r")
n_c_scalar_r = iric.cg_iRIC_Read_Integer(fid, "n_c_scalar_r")
n_c_scalar_i = iric.cg_iRIC_Read_Integer(fid, "n_c_scalar_i")

###############################################################################
# メモリ確保
###############################################################################

# 流速
velocity_1_x = np.ones(shape=(isize, jsize), order="F", dtype=np.float32)
velocity_1_y = np.zeros(shape=(isize, jsize), order="F", dtype=np.float32)
velocity_2_x = np.ones(shape=(isize, jsize), order="F", dtype=np.float32)
velocity_2_y = np.zeros(shape=(isize, jsize), order="F", dtype=np.float32)

# 水深
depth = np.ones(shape=(isize, jsize), order="F", dtype=np.float32)

# 格子点・セルの属性
# 格子点実数値
if n_n_scalar_r > 0:
    n_scalar_r = [
        np.zeros(shape=(isize, jsize), order="F", dtype=np.float32)
        for _ in range(n_n_scalar_r)
    ]

# セル実数値
if n_c_scalar_r > 0:
    c_scalar_r = [
        np.zeros(shape=(isize - 1, jsize - 1), order="F", dtype=np.float32)
        for _ in range(n_c_scalar_r)
    ]

# セル整数値
if n_c_scalar_i > 0:
    c_scalar_i = [
        np.zeros(shape=(isize - 1, jsize - 1), order="F", dtype=np.int32)
        for _ in range(n_c_scalar_i)
    ]

# 仮配列のメモリ確保
if n_n_scalar_r > 0:
    tmp_n_scalar = np.zeros(shape=(isize, jsize), order="F", dtype=np.float32)

if n_c_scalar_r > 0 or n_c_scalar_i > 0:
    tmp_c_scalar = np.zeros(shape=(isize - 1, jsize - 1), order="F", dtype=np.float32)

###############################################################################
# 各種値の計算
###############################################################################

# 流速
for j in range(jsize):
    if j > math.floor(jsize / 2) - 1:
        velocity_1_y[:, j] = -1 * (math.cos(j / (jsize - 1) * 2 * math.pi) + 1) / 2
        velocity_2_y[:, j] = -2 * (math.cos(j / (jsize - 1) * 2 * math.pi) + 1) / 2
    else:
        velocity_1_y[:, j] = 1 * (math.cos(j / (jsize - 1) * 2 * math.pi) + 1) / 2
        velocity_2_y[:, j] = 2 * (math.cos(j / (jsize - 1) * 2 * math.pi) + 1) / 2

# 格子点実数
if n_n_scalar_r > 0:
    for j in range(jsize):
        tmp_n_scalar[:, j] = (math.cos(j / (jsize - 1) * 2 * math.pi) + 1) / 2
    for k in range(n_n_scalar_r):
        n_scalar_r[k] = tmp_n_scalar * (k + 1)

# セル実数
if n_c_scalar_r > 0:
    for j in range(jsize - 1):
        tmp_c_scalar[:, j] = (math.cos(j / (jsize - 2) * 2 * math.pi) + 1) / 2
    for k in range(n_c_scalar_r):
        c_scalar_r[k] = tmp_c_scalar * (k + 1)

# セル整数
if n_c_scalar_i > 0:
    for k in range(n_c_scalar_i):
        for j in range(jsize - 1):
            c_scalar_i[k][:, j] = (j + 1) % (k + 2)

print("----------mainloop start----------")

###############################################################################
# メインループスタート
###############################################################################

for t in range(time_end + 1):
    ###########################################################################
    # 結果の書き込みスタート
    ###########################################################################

    # 時間ごとの書き込み開始をGUIに伝える
    iric.cg_iRIC_Write_Sol_Start(fid)

    # 時刻を書き込み
    iric.cg_iRIC_Write_Sol_Time(fid, float(t))

    # 時間ごとに1つの値を持つ値(今回は流量)を書き込み
    iric.cg_iRIC_Write_Sol_BaseIterative_Real(fid, "discharge1", 1.0)
    iric.cg_iRIC_Write_Sol_BaseIterative_Real(fid, "discharge2", 2.0)

    # 水深を書き込み（格子点実数値）
    iric.cg_iRIC_Write_Sol_Node_Real(fid, "Depth", depth.flatten(order="F"))

    # 流速を書き込み
    iric.cg_iRIC_Write_Sol_Node_Real(
        fid, "velocity_1X", velocity_1_x.flatten(order="F")
    )
    iric.cg_iRIC_Write_Sol_Node_Real(
        fid, "velocity_1Y", velocity_1_y.flatten(order="F")
    )
    iric.cg_iRIC_Write_Sol_Node_Real(
        fid, "velocity_2X", velocity_2_x.flatten(order="F")
    )
    iric.cg_iRIC_Write_Sol_Node_Real(
        fid, "velocity_2Y", velocity_2_y.flatten(order="F")
    )

    # 各種計算結果の出力(あれば)
    # =========================================================================

    # 格子点実数値
    if n_n_scalar_r > 0:
        for k in range(n_n_scalar_r):
            iric.cg_iRIC_Write_Sol_Node_Real(
                fid, "node_scalar_r" + str(k + 1), n_scalar_r[k].flatten(order="F")
            )

    # セル実数値
    if n_c_scalar_r > 0:
        for k in range(n_c_scalar_r):
            iric.cg_iRIC_Write_Sol_Cell_Real(
                fid, "cell_scalar_r" + str(k + 1), c_scalar_r[k].flatten(order="F")
            )

    # セル整数値
    if n_c_scalar_i > 0:
        for k in range(n_c_scalar_i):
            iric.cg_iRIC_Write_Sol_Cell_Integer(
                fid, "cell_scalar_i" + str(k + 1), c_scalar_i[k].flatten(order="F")
            )

    # CGNSへの書き込み終了をGUIに伝える
    iric.cg_iRIC_Write_Sol_End(fid)

    # コンソールに時間を出力
    print("t= " + str(t))

    # 計算結果の再読み込みが要求されていれば出力を行う
    iric.cg_iRIC_Check_Update(fid)

    # 計算のキャンセルが押されていればループを抜け出して出力を終了する。
    canceled = iric.iRIC_Check_Cancel()
    if canceled == 1:
        print("Cancel button was pressed. Calculation is finishing. . .")
        break

print("----------finish----------")

###############################################################################
# 計算終了処理
###############################################################################
iric.cg_iRIC_Close(fid)
