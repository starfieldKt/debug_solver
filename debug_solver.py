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

# 格子点の座標読み込み
# --------------------------------------------------
# メモ
# --------------------------------------------------
# CGNSから読み込む時は1次元配列、順番は以下
# --------------------------------------------------
#      j
#      ↑
#     4| 24, 25, 26, 27, 28, 29
#     3| 18, 19, 20, 21, 22, 23
#     2| 12, 13, 14, 15, 16, 17
#     1|  6,  7,  8,  9, 10, 11
#     0|  0,  1,  2,  3,  4,  5
#       ----------------------- →　i
#         0   1   2   3   4   5
# --------------------------------------------------
grid_x_arr, grid_y_arr = iric.cg_iRIC_Read_Grid2d_Coords(fid)
grid_x_arr = grid_x_arr.reshape(jsize, isize).T
grid_y_arr = grid_y_arr.reshape(jsize, isize).T

# 計算時間を読み込み
time_end = iric.cg_iRIC_Read_Integer(fid, "time_end")

# 読み込んだ格子サイズをコンソールに出力
print("Grid size:")
print("    isize= " + str(isize))
print("    jsize= " + str(jsize))

# 各値を何種出すか読み込み
n_n_scalar_r = iric.cg_iRIC_Read_Integer(fid, "n_n_scalar_r")
n_n_scalar_i = iric.cg_iRIC_Read_Integer(fid, "n_n_scalar_i")
n_c_scalar_r = iric.cg_iRIC_Read_Integer(fid, "n_c_scalar_r")
n_c_scalar_i = iric.cg_iRIC_Read_Integer(fid, "n_c_scalar_i")
n_ie_scalar_r = iric.cg_iRIC_Read_Integer(fid, "n_ie_scalar_r")
n_ie_scalar_i = iric.cg_iRIC_Read_Integer(fid, "n_ie_scalar_i")
n_je_scalar_r = iric.cg_iRIC_Read_Integer(fid, "n_je_scalar_r")
n_je_scalar_i = iric.cg_iRIC_Read_Integer(fid, "n_je_scalar_i")

# 何秒で1回転するか

rotation_cycle = iric.cg_iRIC_Read_Integer(fid, "rotation_cycle")

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

# 格子点整数値
if n_n_scalar_i > 0:
    n_scalar_i = [
        np.zeros(shape=(isize, jsize), order="F", dtype=np.int32)
        for _ in range(n_n_scalar_i)
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

# i方向境界面実数
if n_ie_scalar_r > 0:
    ie_scalar_r = [
        np.zeros(shape=(isize, jsize - 1), order="F", dtype=np.float32)
        for _ in range(n_ie_scalar_r)
    ]

# i方向境界面整数
if n_ie_scalar_i > 0:
    ie_scalar_i = [
        np.zeros(shape=(isize, jsize - 1), order="F", dtype=np.int32)
        for _ in range(n_ie_scalar_i)
    ]

# j方向境界面実数
if n_je_scalar_r > 0:
    je_scalar_r = [
        np.zeros(shape=(isize - 1, jsize), order="F", dtype=np.float32)
        for _ in range(n_je_scalar_r)
    ]

# j方向境界面整数
if n_je_scalar_i > 0:
    je_scalar_i = [
        np.zeros(shape=(isize - 1, jsize), order="F", dtype=np.int32)
        for _ in range(n_je_scalar_i)
    ]


# 仮配列のメモリ確保
if n_n_scalar_r > 0:
    tmp_n_scalar = np.zeros(shape=(isize, jsize), order="F", dtype=np.float32)

if n_c_scalar_r > 0:
    tmp_c_scalar = np.zeros(shape=(isize - 1, jsize - 1), order="F", dtype=np.float32)

if n_ie_scalar_r > 0:
    tmp_ie_scalar = np.zeros(shape=(isize, jsize - 1), order="F", dtype=np.float32)

if n_je_scalar_r > 0:
    tmp_je_scalar = np.zeros(shape=(isize - 1, jsize), order="F", dtype=np.float32)

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

# 格子点整数
if n_n_scalar_i > 0:
    for k in range(n_n_scalar_i):
        for j in range(jsize):
            n_scalar_i[k][:, j] = (j + 1) % (k + 2)

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

# i方向境界実数
if n_ie_scalar_r > 0:
    for i in range(isize):
        tmp_ie_scalar[i, :] = (math.cos(i / (isize - 1) * 2 * math.pi) + 1) / 2
    for k in range(n_ie_scalar_r):
        ie_scalar_r[k] = tmp_ie_scalar * (k + 1)

# i方向境界実数
if n_ie_scalar_i > 0:
    for k in range(n_ie_scalar_i):
        for i in range(isize):
            ie_scalar_i[k][i, :] = (i + 1) % (k + 2)

# i方向境界実数
if n_je_scalar_r > 0:
    for j in range(jsize):
        tmp_je_scalar[:, j] = (math.cos(j / (jsize - 1) * 2 * math.pi) + 1) / 2
    for k in range(n_je_scalar_r):
        je_scalar_r[k] = tmp_je_scalar * (k + 1)

# i方向境界実数
if n_je_scalar_i > 0:
    for k in range(n_je_scalar_i):
        for j in range(jsize):
            je_scalar_i[k][:, j] = (j + 1) % (k + 2)


print("----------mainloop start----------")

###############################################################################
# メインループスタート
###############################################################################

for t in range(time_end + 1):

    ###########################################################################
    # パーティクルの座標計算開始
    ###########################################################################

    # 初期位置
    # [i, j, x座標 y座標]
    if t == 0:
        particles = np.array(
            [
                [0, 0, grid_x_arr[0][0], grid_y_arr[0][0], 0],
                [isize - 1, 0, grid_x_arr[isize - 1][0], grid_y_arr[isize - 1][0], 0],
                [
                    isize - 1,
                    jsize - 1,
                    grid_x_arr[isize - 1][jsize - 1],
                    grid_y_arr[isize - 1][jsize - 1],
                    0,
                ],
                [0, jsize - 1, grid_x_arr[0][jsize - 1], grid_y_arr[0][jsize - 1], 0],
            ],
            dtype="object",
        )
    else:
        for i_particle in range(4):

            i_tmp = particles[i_particle][0]
            j_tmp = particles[i_particle][1]

            if j_tmp == 0 and i_tmp < isize - 1:
                i_tmp += 1
            elif j_tmp == jsize - 1 and i_tmp > 0:
                i_tmp -= 1
            elif i_tmp == 0 and j_tmp > 0:
                j_tmp -= 1
            elif i_tmp == isize - 1 and j_tmp < jsize - 1:
                j_tmp += 1

            tmp_angle = float(360 * (t % rotation_cycle / rotation_cycle))

            particles[i_particle] = [
                i_tmp,
                j_tmp,
                grid_x_arr[i_tmp][j_tmp],
                grid_y_arr[i_tmp][j_tmp],
                tmp_angle,
            ]

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

    # 格子点整数値
    if n_n_scalar_i > 0:
        for k in range(n_n_scalar_i):
            iric.cg_iRIC_Write_Sol_Node_Integer(
                fid, "node_scalar_i" + str(k + 1), n_scalar_i[k].flatten(order="F")
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

    # i方向境界実数値
    if n_ie_scalar_r > 0:
        for k in range(n_ie_scalar_r):
            iric.cg_iRIC_Write_Sol_IFace_Real(
                fid, "iedge_scalar_r" + str(k + 1), ie_scalar_r[k].flatten(order="F")
            )

    # i方向境界整数値
    if n_ie_scalar_i > 0:
        for k in range(n_ie_scalar_i):
            iric.cg_iRIC_Write_Sol_IFace_Integer(
                fid, "iedge_scalar_i" + str(k + 1), ie_scalar_i[k].flatten(order="F")
            )

    # j方向境界実数値
    if n_je_scalar_r > 0:
        for k in range(n_je_scalar_r):
            iric.cg_iRIC_Write_Sol_JFace_Real(
                fid, "jedge_scalar_r" + str(k + 1), je_scalar_r[k].flatten(order="F")
            )

    # j方向境界整数値
    if n_ie_scalar_i > 0:
        for k in range(n_ie_scalar_i):
            iric.cg_iRIC_Write_Sol_JFace_Integer(
                fid, "jedge_scalar_i" + str(k + 1), je_scalar_i[k].flatten(order="F")
            )

    # パーティクルの出力 ここから
    # =========================================================================

    # Particleの出力
    iric.cg_iRIC_Write_Sol_Particle_Pos2d(fid, particles[:, 2], particles[:, 3])
    iric.cg_iRIC_Write_Sol_Particle_Integer(fid, "index_i", particles[:][0])
    iric.cg_iRIC_Write_Sol_Particle_Integer(fid, "index_j", particles[:][1])
    iric.cg_iRIC_Write_Sol_Particle_Real(fid, "v1X", particles[:][0].astype(float))
    iric.cg_iRIC_Write_Sol_Particle_Real(fid, "v1Y", particles[:][1].astype(float))
    iric.cg_iRIC_Write_Sol_Particle_Real(fid, "v2X", -particles[:][0].astype(float))
    iric.cg_iRIC_Write_Sol_Particle_Real(fid, "v2Y", -particles[:][1].astype(float))

    # Particle group_1の出力開始
    iric.cg_iRIC_Write_Sol_ParticleGroup_GroupBegin(fid, "ParticleGroup_1")

    # 各Particleの座標と値を書き込み
    for i_particle in range(4):
        iric.cg_iRIC_Write_Sol_ParticleGroup_Pos2d(
            fid, float(particles[i_particle][2]), float(particles[i_particle][3])
        )
        iric.cg_iRIC_Write_Sol_ParticleGroup_Integer(
            fid, "index_i", particles[i_particle][0]
        )
        iric.cg_iRIC_Write_Sol_ParticleGroup_Integer(
            fid, "index_j", particles[i_particle][1]
        )
        iric.cg_iRIC_Write_Sol_ParticleGroup_Real(
            fid, "v1X", float(particles[i_particle][0])
        )
        iric.cg_iRIC_Write_Sol_ParticleGroup_Real(
            fid, "v1Y", float(particles[i_particle][1])
        )
        iric.cg_iRIC_Write_Sol_ParticleGroup_Real(
            fid, "v2X", float(-particles[i_particle][0])
        )
        iric.cg_iRIC_Write_Sol_ParticleGroup_Real(
            fid, "v2Y", float(-particles[i_particle][1])
        )

    # Particle group_1の出力終了
    iric.cg_iRIC_Write_Sol_ParticleGroup_GroupEnd(fid)

    # Particle group_2の出力開始
    iric.cg_iRIC_Write_Sol_ParticleGroup_GroupBegin(fid, "ParticleGroup_2")

    # 各Particleの座標と値を書き込み
    for i_particle in range(4):
        iric.cg_iRIC_Write_Sol_ParticleGroup_Pos2d(
            fid, float(particles[i_particle][2]), float(particles[i_particle][3])
        )
        iric.cg_iRIC_Write_Sol_ParticleGroup_Integer(
            fid, "index_i", particles[i_particle][0]
        )
        iric.cg_iRIC_Write_Sol_ParticleGroup_Integer(
            fid, "index_j", particles[i_particle][1]
        )
        iric.cg_iRIC_Write_Sol_ParticleGroup_Real(
            fid, "v1X", float(particles[i_particle][1])
        )
        iric.cg_iRIC_Write_Sol_ParticleGroup_Real(
            fid, "v1Y", float(particles[i_particle][0])
        )
        iric.cg_iRIC_Write_Sol_ParticleGroup_Real(
            fid, "v2X", float(-particles[i_particle][1])
        )
        iric.cg_iRIC_Write_Sol_ParticleGroup_Real(
            fid, "v2Y", float(-particles[i_particle][0])
        )

    # Particle group_2の出力終了
    iric.cg_iRIC_Write_Sol_ParticleGroup_GroupEnd(fid)

    # Particle group image_1の出力開始
    iric.cg_iRIC_Write_Sol_ParticleGroupImage_GroupBegin(fid, "Particle_imageGroup_1")

    # 各Particleの座標と値を書き込み
    for i_particle in range(4):
        iric.cg_iRIC_Write_Sol_ParticleGroupImage_Pos2d(
            fid,
            float(particles[i_particle][2]),
            float(particles[i_particle][3]),
            float(particles[i_particle][0]),
            float(particles[i_particle][4]),
        )

    iric.cg_iRIC_Write_Sol_ParticleGroupImage_GroupEnd(fid)

    # Particle group image_2の出力開始
    iric.cg_iRIC_Write_Sol_ParticleGroupImage_GroupBegin(fid, "Particle_imageGroup_2")

    # 各Particleの座標と値を書き込み
    for i_particle in range(4):
        iric.cg_iRIC_Write_Sol_ParticleGroupImage_Pos2d(
            fid,
            float(particles[i_particle][2]),
            float(particles[i_particle][3]),
            float(particles[i_particle][1]),
            float(-particles[i_particle][4]),
        )

    iric.cg_iRIC_Write_Sol_ParticleGroupImage_GroupEnd(fid)

    # =========================================================================
    # パーティクルの出力 ここまで

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
