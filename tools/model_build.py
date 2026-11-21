"""Quaternius Universal Base Characters (CC0) glTF -> sahne için küçük model dosyaları.

Kullanım:
    python tools/model_build.py "work/ubc-kaynak/Universal Base Characters[Standard]"

Çıktı app/models/ altına yazılır:
    kadin.json / kadin.bin, erkek.json / erkek.bin  (iskelet + gövde + gözler + kaşlar + saçlar)
    *.jpg dokular (1024 / 512 piksel)
Her köşeye bir "region" değeri eklenir: 0 ten, 1 üst giysi, 2 bacak giysisi, 3 ayakkabı.
Sahne bu değeri kullanarak modeli kendi kıyafet renkleriyle giydirir.
"""
import json, sys, struct
from pathlib import Path
import numpy as np
import cv2

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'app' / 'models'
COMP = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
SIZE = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}

# Bölge sınıflandırması: köşeyi en çok etkileyen kemiğe göre.
GARMENT = {'pelvis', 'spine_01', 'spine_02', 'spine_03', 'clavicle_l', 'clavicle_r', 'upperarm_l', 'upperarm_r', 'lowerarm_l', 'lowerarm_r'}
LEGS = {'thigh_l', 'thigh_r', 'calf_l', 'calf_r'}
SHOES = {'foot_l', 'foot_r', 'ball_l', 'ball_r', 'ball_leaf_l', 'ball_leaf_r'}


def load(path):
    path = Path(path)
    g = json.loads(path.read_text(encoding='utf-8'))
    buffers = [(path.parent / b['uri']).read_bytes() for b in g['buffers']]
    def accessor(i):
        a = g['accessors'][i]; v = g['bufferViews'][a['bufferView']]
        n = SIZE[a['type']]; dt = np.dtype(COMP[a['componentType']])
        start = v.get('byteOffset', 0) + a.get('byteOffset', 0)
        stride = v.get('byteStride', 0)
        raw = buffers[v['buffer']]
        if stride and stride != n * dt.itemsize:
            rows = [np.frombuffer(raw, dt, n, start + k * stride) for k in range(a['count'])]
            return np.array(rows)
        return np.frombuffer(raw, dt, a['count'] * n, start).reshape(a['count'], n)
    return g, accessor


def mesh_data(g, accessor, mesh_index, joint_names):
    p = g['meshes'][mesh_index]['primitives'][0]; at = p['attributes']
    joints = accessor(at['JOINTS_0']).astype(np.uint8)
    weights = accessor(at['WEIGHTS_0']).astype(np.float32)
    region = np.zeros(len(joints), np.float32)
    for k in range(len(joints)):
        score = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0}
        for j, w in zip(joints[k], weights[k]):
            name = joint_names[j]
            score[1 if name in GARMENT else 2 if name in LEGS else 3 if name in SHOES else 0] += float(w)
        region[k] = max(score, key=score.get)
    return dict(
        position=accessor(at['POSITION']).astype(np.float32),
        normal=accessor(at['NORMAL']).astype(np.float32),
        uv=accessor(at['TEXCOORD_0']).astype(np.float32),
        joints=joints, weights=weights, region=region,
        index=accessor(p['indices']).astype(np.uint32 if accessor(p['indices']).max() > 65535 else np.uint16).ravel())


def skeleton(g, accessor):
    skin = g['skins'][0]; nodes = g['nodes']
    parent = {c: i for i, n in enumerate(nodes) for c in n.get('children', [])}
    index_of = {node: k for k, node in enumerate(skin['joints'])}
    joints = []
    for node in skin['joints']:
        n = nodes[node]
        joints.append(dict(name=n['name'], parent=index_of.get(parent.get(node), -1),
                           t=n.get('translation', [0, 0, 0]), r=n.get('rotation', [0, 0, 0, 1]), s=n.get('scale', [1, 1, 1])))
    ibm = accessor(skin['inverseBindMatrices']).astype(np.float32)
    return joints, ibm


def texture(src, name, size, quality=88):
    img = cv2.imread(str(src), cv2.IMREAD_COLOR)
    img = cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA)
    cv2.imwrite(str(OUT / name), img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return name


def pack(name, joints, ibm, meshes):
    blob = bytearray(); meta = dict(joints=joints, meshes=[])
    def put(arr):
        nonlocal blob
        while len(blob) % 4: blob += b'\0'
        off = len(blob); blob += np.ascontiguousarray(arr).tobytes(); return off
    meta['ibm'] = put(ibm)
    for mname, m, material in meshes:
        entry = dict(name=mname, material=material, count=len(m['position']), indexCount=len(m['index']),
                     indexType='u32' if m['index'].dtype == np.uint32 else 'u16')
        for key in ('position', 'normal', 'uv', 'joints', 'weights', 'region', 'index'):
            entry[key] = put(m[key])
        meta['meshes'].append(entry)
    (OUT / f'{name}.bin').write_bytes(bytes(blob))
    (OUT / f'{name}.json').write_text(json.dumps(meta, separators=(',', ':')), encoding='utf-8')
    return len(blob)


def build(src):
    src = Path(src); base = src / 'Base Characters' / 'Godot - UE'; hair = src / 'Hairstyles' / 'Rigged to Head Bone' / 'glTF (Godot -Unreal)'
    tex = src / 'Base Characters' / 'Textures'
    OUT.mkdir(parents=True, exist_ok=True)
    for kind, file, brows, hairs in [('kadin', 'Superhero_Female_FullBody.gltf', 'Eyebrows_Female.gltf', ['Hair_Long', 'Hair_Buns']),
                                     ('erkek', 'Superhero_Male_FullBody.gltf', 'Eyebrows_Regular.gltf', ['Hair_SimpleParted', 'Hair_Beard'])]:
        g, acc = load(base / file)
        joints, ibm = skeleton(g, acc); names = [j['name'] for j in joints]
        # Parça adları modelden modele değişiyor; gövdeyi en büyük parça, gözü malzeme adıyla bul.
        def material_name(i): return g['materials'][g['meshes'][i]['primitives'][0]['material']]['name']
        def vertex_count(i): return g['accessors'][g['meshes'][i]['primitives'][0]['attributes']['POSITION']]['count']
        body_index = max(range(len(g['meshes'])), key=vertex_count)
        eye_index = next(i for i in range(len(g['meshes'])) if 'eye' in material_name(i).lower())
        meshes = [('body', mesh_data(g, acc, body_index, names), 'body'),
                  ('eyes', mesh_data(g, acc, eye_index, names), 'eyes')]
        bg, bacc = load(hair / brows); meshes.append(('brows', mesh_data(bg, bacc, 0, names), 'hair'))
        for h in hairs:
            hg, hacc = load(hair / f'{h}.gltf')
            assert [hg['nodes'][j]['name'] for j in hg['skins'][0]['joints']] == names, h
            meshes.append((h, mesh_data(hg, hacc, 0, names), 'hair'))
        for mesh_name, m, _material in meshes:
            if mesh_name != 'body': m['region'][:] = 0  # gözler, kaşlar ve saçlar kendi renginde kalır
        size = pack(kind, joints, ibm, meshes)
        print(kind, f'{size/1024:.0f} KB', [(n, len(m['index']) // 3) for n, m, _ in meshes])
    texture(tex / 'T_Superhero_Female_Light_BaseColor.png', 'kadin-ten-acik.jpg', 1024)
    texture(tex / 'T_Superhero_Female_Dark_BaseColor.png', 'kadin-ten-koyu.jpg', 1024)
    texture(tex / 'T_Superhero_Female_Normal.png', 'kadin-normal.jpg', 1024, 92)
    texture(tex / 'T_Superhero_Male_Ligh.png', 'erkek-ten-acik.jpg', 1024)
    texture(tex / 'T_Superhero_Male_Dark.png', 'erkek-ten-koyu.jpg', 1024)
    texture(tex / 'T_Superhero_Male_Normal.png', 'erkek-normal.jpg', 1024, 92)
    texture(tex / 'T_Hair_2_BaseColor.png', 'sac.jpg', 512)
    texture(tex / 'T_Eye_Brown.png', 'goz.jpg', 256)
    (OUT / 'LICENSE.txt').write_text('Karakter modelleri: Universal Base Characters, Quaternius (https://quaternius.com)\n'
                                     'Lisans: CC0 1.0 Universal (Public Domain). Sahne için dönüştürüldü: tools/model_build.py\n', encoding='utf-8')
    total = sum(f.stat().st_size for f in OUT.iterdir())
    print(f'app/models toplam {total/1024/1024:.1f} MB')


if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else ROOT / 'work' / 'ubc-kaynak' / 'Universal Base Characters[Standard]')
