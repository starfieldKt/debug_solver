import math
import numpy as np
import iric


print("----------Start----------")

# CGNSをオープン
fid = iric.cg_iRIC_Open("Case1.cgn", iric.IRIC_MODE_MODIFY)

# 格子サイズを読み込み
isize, jsize = iric.cg_iRIC_Read_Grid2d_Str_Size(fid)

time_end = iric.cg_iRIC_Read_Integer(fid, "time_end")

print("isize= " + str(isize))
print("jsize= " + str(jsize))

# メモリ確保

velocity_1_x = np.zeros(shape=(isize, jsize), order="F", dtype=np.float32)
velocity_1_y = np.zeros(shape=(isize, jsize), order="F", dtype=np.float32)

velocity_2_x = np.zeros(shape=(isize, jsize), order="F", dtype=np.float32)
velocity_2_y = np.zeros(shape=(isize, jsize), order="F", dtype=np.float32)

depth = np.zeros(shape=(isize, jsize), order="F", dtype=np.float32)

n_scolar_r_1 = np.zeros(shape=(isize, jsize), order="F", dtype=np.float32)
n_scolar_r_2 = np.zeros(shape=(isize, jsize), order="F", dtype=np.float32)
n_scolar_r_3 = np.zeros(shape=(isize, jsize), order="F", dtype=np.float32)
n_scolar_r_4 = np.zeros(shape=(isize, jsize), order="F", dtype=np.float32)
n_scolar_r_5 = np.zeros(shape=(isize, jsize), order="F", dtype=np.float32)

c_scolar_r_1 = np.zeros(shape=(isize - 1, jsize - 1), order="F", dtype=np.float32)
c_scolar_r_2 = np.zeros(shape=(isize - 1, jsize - 1), order="F", dtype=np.float32)
c_scolar_r_3 = np.zeros(shape=(isize - 1, jsize - 1), order="F", dtype=np.float32)
c_scolar_r_4 = np.zeros(shape=(isize - 1, jsize - 1), order="F", dtype=np.float32)
c_scolar_r_5 = np.zeros(shape=(isize - 1, jsize - 1), order="F", dtype=np.float32)

c_scolar_i_1 = np.zeros(shape=(isize - 1, jsize - 1), order="F", dtype=np.int32)
c_scolar_i_2 = np.zeros(shape=(isize - 1, jsize - 1), order="F", dtype=np.int32)
c_scolar_i_3 = np.zeros(shape=(isize - 1, jsize - 1), order="F", dtype=np.int32)
c_scolar_i_4 = np.zeros(shape=(isize - 1, jsize - 1), order="F", dtype=np.int32)
c_scolar_i_5 = np.zeros(shape=(isize - 1, jsize - 1), order="F", dtype=np.int32)

# 値を入れていく
velocity_1_x.fill(1.0)
velocity_2_x.fill(1.0)
depth.fill(1.0)

for j in range(jsize):
    if j > math.floor(jsize / 2) - 1:
        velocity_1_y[:, j] = -1 * (math.cos(j / (jsize - 1) * 2 * math.pi) + 1) / 2
        velocity_2_y[:, j] = -2 * (math.cos(j / (jsize - 1) * 2 * math.pi) + 1) / 2
    else:
        velocity_1_y[:, j] = 1 * (math.cos(j / (jsize - 1) * 2 * math.pi) + 1) / 2
        velocity_2_y[:, j] = 2 * (math.cos(j / (jsize - 1) * 2 * math.pi) + 1) / 2

for j in range(jsize):
    n_scolar_r_1[:, j] = 1 * (math.cos(j / (jsize - 1) * 2 * math.pi) + 1) / 2
    n_scolar_r_2[:, j] = 2 * (math.cos(j / (jsize - 1) * 2 * math.pi) + 1) / 2
    n_scolar_r_3[:, j] = 3 * (math.cos(j / (jsize - 1) * 2 * math.pi) + 1) / 2
    n_scolar_r_4[:, j] = 4 * (math.cos(j / (jsize - 1) * 2 * math.pi) + 1) / 2
    n_scolar_r_5[:, j] = 5 * (math.cos(j / (jsize - 1) * 2 * math.pi) + 1) / 2

for j in range(jsize - 1):
    c_scolar_r_1[:, j] = 1 * (math.cos(j / (jsize - 2) * 2 * math.pi) + 1) / 2
    c_scolar_r_2[:, j] = 2 * (math.cos(j / (jsize - 2) * 2 * math.pi) + 1) / 2
    c_scolar_r_3[:, j] = 3 * (math.cos(j / (jsize - 2) * 2 * math.pi) + 1) / 2
    c_scolar_r_4[:, j] = 4 * (math.cos(j / (jsize - 2) * 2 * math.pi) + 1) / 2
    c_scolar_r_5[:, j] = 5 * (math.cos(j / (jsize - 2) * 2 * math.pi) + 1) / 2

for j in range(jsize - 1):
    c_scolar_i_1[:, j] = (j + 1) % 1
    c_scolar_i_2[:, j] = (j + 1) % 2
    c_scolar_i_3[:, j] = (j + 1) % 3
    c_scolar_i_4[:, j] = (j + 1) % 4
    c_scolar_i_5[:, j] = (j + 1) % 5

# 結果の書き込み
iric.cg_iRIC_Write_Sol_Start(fid)


print("----------mainloop start----------")

for t in range(time_end + 1):
    iric.cg_iRIC_Write_Sol_Time(fid, float(t))
    iric.cg_iRIC_Write_Sol_BaseIterative_Real(fid, "discharge1", 1.0)
    iric.cg_iRIC_Write_Sol_BaseIterative_Real(fid, "discharge2", 2.0)
    iric.cg_iRIC_Write_Sol_Node_Real(fid, "Depth", depth.flatten(order="F"))
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
    iric.cg_iRIC_Write_Sol_Node_Real(
        fid, "node_scolar_r1", n_scolar_r_1.flatten(order="F")
    )
    iric.cg_iRIC_Write_Sol_Node_Real(
        fid, "node_scolar_r2", n_scolar_r_2.flatten(order="F")
    )
    iric.cg_iRIC_Write_Sol_Node_Real(
        fid, "node_scolar_r3", n_scolar_r_3.flatten(order="F")
    )
    iric.cg_iRIC_Write_Sol_Node_Real(
        fid, "node_scolar_r4", n_scolar_r_4.flatten(order="F")
    )
    iric.cg_iRIC_Write_Sol_Node_Real(
        fid, "node_scolar_r5", n_scolar_r_5.flatten(order="F")
    )
    iric.cg_iRIC_Write_Sol_Cell_Real(
        fid, "cell_scolar_r1", c_scolar_r_1.flatten(order="F")
    )
    iric.cg_iRIC_Write_Sol_Cell_Real(
        fid, "cell_scolar_r2", c_scolar_r_2.flatten(order="F")
    )
    iric.cg_iRIC_Write_Sol_Cell_Real(
        fid, "cell_scolar_r3", c_scolar_r_3.flatten(order="F")
    )
    iric.cg_iRIC_Write_Sol_Cell_Real(
        fid, "cell_scolar_r4", c_scolar_r_4.flatten(order="F")
    )
    iric.cg_iRIC_Write_Sol_Cell_Real(
        fid, "cell_scolar_r5", c_scolar_r_5.flatten(order="F")
    )
    iric.cg_iRIC_Write_Sol_Cell_Integer(
        fid, "cell_scolar_i1", c_scolar_i_1.flatten(order="F")
    )
    iric.cg_iRIC_Write_Sol_Cell_Integer(
        fid, "cell_scolar_i2", c_scolar_i_2.flatten(order="F")
    )
    iric.cg_iRIC_Write_Sol_Cell_Integer(
        fid, "cell_scolar_i3", c_scolar_i_3.flatten(order="F")
    )
    iric.cg_iRIC_Write_Sol_Cell_Integer(
        fid, "cell_scolar_i4", c_scolar_i_4.flatten(order="F")
    )
    iric.cg_iRIC_Write_Sol_Cell_Integer(
        fid, "cell_scolar_i5", c_scolar_i_5.flatten(order="F")
    )
    print("t= " + str(t))

iric.cg_iRIC_Write_Sol_End(fid)

iric.cg_iRIC_Close(fid)
