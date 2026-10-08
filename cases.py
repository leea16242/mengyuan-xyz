# -*- coding: utf-8 -*-
"""Case content for mengyuan.xyz.

Every claim here is taken from the original scripts: the header docstrings in
cad-sample/ and WorkBuddy-work/eplan_work/, the feature/API calls actually used,
and the artifacts that exist on disk. Nothing is embellished.

Fields:
  slug / num / title / tags / summary
  facts   list of (label, value)
  overview  2 short paragraphs
  steps   list of (title, body), 4 to 5 items
  apis   list of real API calls, with the call counts found in the scripts
  shots  gallery captions; len() decides how many assets/cases/<slug>-N.webp get inlined
"""

CASES = [
    {
        "slug": "pump",
        "num": "01",
        "title": "齿轮油泵装配",
        "tags": ["SolidWorks", "COM API", "Motion"],
        "summary": "11 个零件从零建模到装配约束，再用旋转马达跑 Motion 算例采样角速度。",
        "facts": [
            ("脚本", "8 个，共 1413 行"),
            ("零件", "11 件，装配体 齿轮油泵_重建.SLDASM"),
            ("装配", "AddComponent + AddMate3，配合面用 GetCorrespondingEntity 取"),
            ("Motion", "sw_motion.py 封装 318 行，输出 motion_result.csv"),
        ],
        "overview": [
            "泵体、轴与键、齿轮分件建模，再进装配体按约束装成。这一步真正的坑不是约束写法，而是轻化："
            "11 个件插进装配体之后，必须趁它们还在还原态立刻用 GetCorrespondingEntity 取配合面，"
            "慢一步就得先去解轻化。",
            "装好后用 Motion API 建算例、加旋转马达、计算并采样角速度，把运动量在出图之前先量出来，"
            "结果写成 CSV 并画出曲线图。",
        ],
        "steps": [
            ("分件建模", "泵体、轴与键、齿轮分别由 p1 / p2 / p3 三个脚本生成，全程 COM API 后期绑定，"
                       "一共 15 次拉伸、4 次旋转。"),
            ("交代轴线与基准", "p19_axes_geo.py 建轴线几何与 5 个参考面，给后面的装配约束留抓手。"),
            ("装配 11 件", "p30_build_and_mate.py 用 AddComponent 插入全部零件，趁还原态立即取面，"
                         "再用 AddMate3 打约束，一次装成。"),
            ("跑 Motion 算例", "motion_run.py 打开装配体，建算例、加旋转马达、计算，采样角速度写成 "
                           "motion_result.csv，并画出 motion_curve.png。"),
            ("渲染", "p40_render.py 出装配视图与侧视图。"),
        ],
        "apis": ["InsertSketch x38", "FeatureCut3 x16", "FeatureExtrusion3 x15",
                 "FeatureRevolve2 x4", "InsertRefPlane x5", "AddComponent x2",
                 "AddMate3 x2", "GetCorrespondingEntity", "SaveAs x7"],
        "shots": ["装配渲染", "侧视", "Motion 采样出的角速度曲线（motion_result.csv）"],
    },
    {
        "slug": "crown",
        "num": "02",
        "title": "王冠瓶盖",
        "tags": ["SolidWorks", "拔模", "图片反求"],
        "summary": "从参考图反求几何：FFT 定出 18 齿，归一化半径对表，再用拔模收出折瓣。",
        "facts": [
            ("脚本", "1 个，283 行"),
            ("齿数", "18（极坐标轮廓 FFT 主频 18，齿尖间距 20.0°）"),
            ("裙部", "底 齿尖 R15.00 / 齿谷 R13.60，高 4.80，拔模 11.08°"),
            ("尺寸", "壁厚 0.30，肩锥角 68.65°"),
        ],
        "overview": [
            "没有图纸，只有参考图。先把俯视图外轮廓转成极坐标做 FFT，主频落在 18，齿尖间距正好 20.0°，"
            "齿数就定了；再按齿尖半径归一化，量出齿谷 / 齿尖 0.907、裙顶 0.844、顶盘 0.702 三组比值，"
            "结构拆成薄壁裙（18 折瓣）+ 圆锥肩 + 平顶盘。",
            "建模时踩到一个坑：本机 SolidWorks 的拔模是按「面法向」算的，不是按竖直方向，"
            "所以齿尖和齿谷收的量不一样（1.703 对 0.94），裙顶半径必须按这个重算才对得上图。",
        ],
        "steps": [
            ("读图定齿数", "轮廓转极坐标做 FFT，主频 18，齿尖间距 20.0°，与参考图逐齿对上。"),
            ("归一化量比例", "以齿尖半径为 1，量出齿谷 0.907、裙顶 0.844、顶盘 0.702。"),
            ("建裙", "齿尖 R15.00 / 齿谷 R13.60 的 18 折瓣往上拉 4.80，带 11.08° 拔模。"),
            ("处理拔模偏差", "实测 SW 按面法向算拔模，齿尖与齿谷收缩量不同，重算裙顶半径让折瓣向肩自然收细。"),
            ("肩与顶盘", "68.65° 锥角收成单实体避免碎面，壁厚 0.30，内腔由 Z4.80 / Z5.70 两个内部参考面向下切出。"),
        ],
        "apis": ["FeatureExtrusion3", "FeatureCut3", "InsertRefPlane", "InsertSketch x4", "SaveAs x2"],
        "shots": ["王冠瓶盖渲染（绿色为同件内腔视图）"],
    },
    {
        "slug": "gear",
        "num": "03",
        "title": "参数化齿轮",
        "tags": ["SolidWorks", "方程曲线", "参数化"],
        "summary": "齿廓由方程曲线驱动，改模数与齿数即换型号，齿形图同步更新。",
        "facts": [
            ("脚本", "8 个，共 2006 行"),
            ("齿廓", "CreateEquationSpline2 调用 8 次生成渐开线样条"),
            ("成型", "FeatureCircularPattern3 圆周阵列 4 次，CreateArc 圆弧 15 次"),
            ("两套参数", "m2 / 30 齿，m1 / 20 齿"),
        ],
        "overview": [
            "齿廓不用近似圆弧去拼，直接按渐开线方程生成样条，再把单齿轮廓拉伸、圆周阵列成整圈。"
            "参数写在脚本顶部，换模数或齿数只改数字，齿轮与齿形图一起更新。",
            "gear_profile_plot.py 单独画齿廓曲线与齿形图，用来核对压力角与齿顶、齿根。",
        ],
        "steps": [
            ("写齿廓方程", "按模数与齿数算出渐开线参数，交给 CreateEquationSpline2 生成样条。"),
            ("单齿成型", "单齿轮廓拉伸，圆弧倒圆修齿顶与齿根。"),
            ("圆周阵列", "FeatureCircularPattern3 阵列成整圈，30 齿那次一次成。"),
            ("换参数验证", "把参数改成 m1 / 20 齿，同一套脚本再跑一遍，确认确实是参数化的而不是手画的。"),
            ("出齿形图", "gear_profile_plot.py 画齿廓曲线与齿形图，对照压力角。"),
        ],
        "apis": ["CreateEquationSpline2 x8", "CreateArc x15", "FeatureCircularPattern3 x4",
                 "FeatureRevolve2 x5", "FeatureCut3 x10", "InsertSketch x19", "SaveAs x6"],
        "shots": ["齿廓与齿形图（右图为齿轮参数表）", "同一套脚本换成 m1 / 20 齿"],
    },
    {
        "slug": "funnel",
        "num": "04",
        "title": "漏斗杯",
        "tags": ["SolidWorks", "曲面", "圆角"],
        "summary": "锥形杯体与吸管的交界处反复出褶，靠一组探针脚本试出可用参数。",
        "facts": [
            ("脚本", "9 个，共 1057 行"),
            ("其中探针", "5 个：fillet_probe 1 到 4 + fillet_fix"),
            ("成型", "回转体 2 个，圆角 2 处"),
            ("迭代痕迹", "保留 funnel_cup_under90 / under35 等多组对比图"),
        ],
        "overview": [
            "杯体与吸管各自回转出来不难，难在两者交界的圆角过渡：半径给小了出硬边，给大了过渡面起褶，"
            "而且没有现成的合适参数。",
            "所以先写了 fillet_probe 一到四，逐组试半径与相邻面，把能用的区间量出来，再用 fillet_fix.py 定型，"
            "最后 final_colors.py 上色出图。",
        ],
        "steps": [
            ("两个回转体", "锥形杯体与吸管分别回转成型，这一步很顺。"),
            ("撞上圆角过渡", "交界处直接倒圆角会出褶，硬边与起褶之间没有现成参数可用。"),
            ("写探针试参数", "fillet_probe 1 到 4 逐组试半径与相邻面，把可用区间量出来。"),
            ("定型", "fillet_fix.py 按量出来的参数落定，交界过渡面在多个视角下都不再出褶。"),
            ("上色出图", "final_colors.py 上材质，输出 FINAL 系列视图。"),
        ],
        "apis": ["FeatureRevolve2 x2", "FeatureFillet x4", "InsertSketch x2", "SaveAs x2"],
        "shots": ["整体等轴测", "吸管与杯体的交界近景", "另一视角的交界过渡"],
    },
    {
        "slug": "bracket",
        "num": "05",
        "title": "安装板",
        "tags": ["SolidWorks", "板件", "通孔"],
        "summary": "100×60×10 的底板加四个通孔，所有尺寸都是脚本顶部的变量。",
        "facts": [
            ("脚本", "3 个，共 686 行"),
            ("尺寸", "板 100 × 60 × 10 mm，通孔 Ø8，孔心距板边 12 mm"),
            ("调用", "草图 20 次，切除 4 次，圆角 3 处"),
        ],
        "overview": [
            "一个参数化的板件：长、宽、厚、孔径、孔心边距全写在脚本顶部，改数字就换规格。"
            "板件本身简单，坑都在 API 细节上。",
            "脚本头部留了本机 SolidWorks 2024 中文版实测的 5 条坑位，是这一件最值钱的部分。",
        ],
        "steps": [
            ("参数化草图", "长宽厚与孔位全部用变量表达，草图调用 20 次。"),
            ("拉伸成板", "100 × 60 × 10 一次拉伸成型。"),
            ("切四个通孔", "Ø8 通孔，孔心距板边 12，分四次 FeatureCut3 切出。"),
            ("倒圆角", "棱边与孔的圆角共 3 处。"),
            ("记下踩过的坑", "脚本头部留了 5 条：API 单位一律是米；基准面是中文名；COM 只能后期绑定；"
                          "SelectByID2 的 Callout 必须传 VT_DISPATCH 空指针；"
                          "FeatureCut3 的 NormalCut 必须传 False，传 True 会静默返回 None 且不报错。"),
        ],
        "apis": ["InsertSketch x20", "FeatureCut3 x4", "FeatureExtrusion3 x3",
                 "FeatureFillet x3", "InsertCombineFeature x2", "InsertRefPlane x1", "SelectByID2 x15"],
        "shots": ["底板与四个通孔"],
    },
    {
        "slug": "eplan",
        "num": "06",
        "title": "电机正反转控制图",
        "tags": ["EPLAN", "MCP", "电气图"],
        "summary": "用本地 MCP 驱动 EPLAN Electric P8 出图，主电路与控制电路分两页。",
        "facts": [
            ("脚本", "47 个，共 3472 行"),
            ("两页", "正反转_主电路 / 正反转_控制电路"),
            ("设备代号", "add_labels.py"),
            ("交叉引用", "add_xref.py 改了三版"),
        ],
        "overview": [
            "不是手工画图，是通过本地 EPLAN MCP 驱动正在运行的 EPLAN Electric P8：建页、放符号、画连线，"
            "含换相交叉；再给每个器件打设备代号、补交叉引用。",
            "做完把导出的页与参考图放在一起逐项比对，确认符号、交叉引用和代号都对得上，最后导出 PDF 与 DXF 留档。",
        ],
        "steps": [
            ("接通 EPLAN", "本地 MCP 连上正在运行的 Electric P8，用动作接口建页。"),
            ("主电路", "三相电源、接触器、热继电器与电机，一页画完。"),
            ("控制电路", "正反转控制回路单独一页，含换相交叉。"),
            ("代号与交叉引用", "add_labels.py 打设备代号，add_xref.py（改了三版）补交叉引用。"),
            ("比对与导出", "与参考图逐项比对确认一致，导出 PDF 与 DXF 留档。"),
        ],
        "apis": ["本地 EPLAN MCP 动作接口（建页 / 放符号 / 连线）", "导出 PDF", "导出 DXF"],
        "shots": ["控制电路页", "主电路页"],
    },
]
