import pyvista as pv
import trimesh
import pandas as pd
import random
import itertools 
import os 

#%% 데이터 로드 

root_path = os.getcwd() 
pv_mesh = pv.read('bunny.stl') # polydata
tri_mesh = trimesh.load('bunny.stl') # base.Trimesh


#%% 전처리

# AABB & OBB 생성
obb = tri_mesh.bounding_box_oriented 
aabb = tri_mesh.bounding_box 


# Bounds 추출 
obb_bounds = obb.bounds
aabb_bounds = aabb.bounds

# trimesh's bounds를 (xMin, xMax, yMin, yMax, zMin, zMax)로 변형 
def align_bounds(bounds):
    temp = []
    for i in range(len(bounds)):
        aa = bounds[i]
        for j in range(len(aa)):
            jj = aa[j]
            temp.append(jj)
    align_bound = [temp[0], temp[3], temp[1], temp[4], temp[2], temp[5]]
    return align_bound 

obb_bounds_a = align_bounds(obb_bounds)
aabb_bounds_a = align_bounds(aabb_bounds)

# pyvista Box 오브젝트 생성 
pv_obb_box = pv.Box(bounds=obb_bounds_a, level=0, quads=True)
pv_aabb_box = pv.Box(bounds=aabb_bounds_a, level=0, quads=True)


#%% 대상 mesh와 두 종류의 BB (AABB, OBB) 시각화

p = pv.Plotter() # 캔버스 정의 
p.add_mesh(pv_mesh, opacity=0.75, color='red')
p.add_mesh(pv_obb_box, opacity=0.25, color='blue')
p.add_mesh(pv_aabb_box, opacity=0.25, color='green')
p.show()


#%% XY축 분할 박스 생성을 위한 좌표값 구하기 

# 바운딩박스를 구성하는 (x, y) 좌표의 최소/최대값 계산
tp = aabb_bounds_a 
x_min, x_max, y_min, y_max, z_min, z_max = tp[0], tp[1], tp[2], tp[3], tp[4], tp[5]


# X축 분할 
x_dist = x_max - x_min # X축 변 길이 계산
n_x = 3 # 몇 등분으로 분할할 것인지 -- 변경 가능 
x_interval = x_dist / float(n_x)
x_min_ls = [x_min + (x_interval*i) for i in range(0, 3)] # x_min 좌표부터 n_x번 간격을 더해줌 
x_max_ls = [x_min + (x_interval*i) for i in range(1, 4)] # 윗줄과 맞물리게끔 n_x번 간격을 더해줌


# Z축 분할 
z_dist = z_max - z_min 
n_z = 2
z_interval = z_dist / float(n_z)

z_min_ls = [z_min + (z_interval*i) for i in range(0, 2)]
z_min_ls = [[i] * 3 for i in z_min_ls]
z_min_ls = list(itertools.chain(*z_min_ls))

z_max_ls = [z_min + (z_interval*i) for i in range(1, 3)]
z_max_ls = [[i] * 3 for i in z_max_ls]
z_max_ls = list(itertools.chain(*z_max_ls))



#%% XY축 분할 박스 생성을 위한 데이터프레임 구축 

bounds_df = pd.DataFrame(data=[], columns=['xmin', 'xmax', 'ymin', 'ymax', 'zmin', 'zmax'])
for i in range(6):
    bounds_df.loc[i] = aabb_bounds_a 
bounds_df['xmin'] = x_min_ls * 2
bounds_df['xmax'] = x_max_ls * 2
bounds_df['zmin'] = z_min_ls
bounds_df['zmax'] = z_max_ls


#%% 분할 파트 시각화 및 STL파일로 export 

for i in range(6):
    globals()['box_{}'.format(i)] = list(bounds_df.iloc[i])
    exec('extract_%s = pv_mesh.clip_box(box_%s, invert=False)'%(i, i))

p = pv.Plotter() 
for i in range(6): 
    color = (random.random(), random.random(), random.random())
    exec("n_cell = extract_%s.n_cells" %(i))
    
    evalCode = 'n_cell != 0'
    if eval(evalCode): 
        exec("pv.save_meshio('extract_%s.stl', extract_%s)" %(i,i))
        exec("p.add_mesh(extract_%s, color=%s)" %(i,color))
        exec("py_box_%s = pv.Box(bounds=box_%s, level=0, quads=True)" %(i,i))
        exec("p.add_mesh(py_box_%s, opacity=0.1, show_edges=True)" %(i))
        
p.show()











