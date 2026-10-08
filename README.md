# glass-landing · mengyuan.xyz 个人站

**7 页静态站**，视觉系统沿用「未来玻璃」（深色宇宙背景 + 毛玻璃卡片 + CSS 3D 透视 mockup）。
原生 CSS/JS，零框架、零外链、零 CDN、零 Emoji，每页自包含（CSS 与图片全部内联）。
**已上线 https://mengyuan.xyz**

> 目录名 `glass-landing` 指的是这套**视觉系统**，不指内容。内容在 2026-10-07 从
> AetherFlow（虚构产品落地页）换成现在的个人站：**机械设计 × Agent 工作流**。
> v1 完整留档在 `v1_aetherflow/`（含 src、build.py、旧版单文件、5 张 AI 人像原图），未被覆盖。

## 一、产物

| 路径 | 说明 |
|---|---|
| `dist/` | **构建产物，也就是部署源**。7 个 HTML：首页 + `case/<slug>/index.html` × 6 |
| `src/` | 源分片：首页 9 个 + `45_detail.css`（详情页样式）+ `70/75_detail*`（详情页模板），**改这里** |
| `cases.py` | 6 个案例的内容数据（标题 / 参数 / 步骤 / 接口清单 / 图注），全部取自原始脚本 |
| `build.py` | 构建：拼装分片 → 内联 `assets/cases/*.webp` → 输出 `dist/` → 逐页校验（占位符、em dash） |
| `build_thumbs.py` | 从 `cad-sample` / `eplan_work` 的原始渲染自动取景，生成 600×375 缩略图与 1000×625 详情图 |
| `assets/cases/` | 24 张 WebP（共 184 kB）。**原始渲染换了要重跑 `build_thumbs.py`** 再 `build.py` |
| `deploy/mengyuan-site.zip` | 手动拖拽上传用的压缩包（目录树在压缩包根级） |
| `deploy/Cloudflare-Pages-上线清单.md` | 逐步操作清单 + 排错 + 回滚 |
| `v1_aetherflow/` | 上一版 AetherFlow 落地页的完整留档 |
| `_probe/` | 验证脚本与截图（`make_test.py` 首页、`make_test_detail.py` 详情页、`make_diag.py` 性能、`make_pal.py` 搜索面板） |

## 二、重建与上线

```bash
# 0. 只有 CAD / EPLAN 原始渲染换了才需要重跑
python build_thumbs.py

# 1. 改 src/ 或 cases.py 后重建（输出到 dist/，并逐页校验）
python build.py

# 2. 部署（wrangler 已装在受管工作区并完成 OAuth 授权，凭据在本机）
export PATH="$HOME/.workbuddy/binaries/node/versions/22.22.2-6:$PATH"
"$HOME/.workbuddy/binaries/node/workspace/node_modules/.bin/wrangler" \
  pages deploy dist --project-name mengyuan-xyz --branch main
```

**手动方式**：把 `deploy/mengyuan-site.zip` 拖进 Pages 的 Create a new deployment。
压缩包里必须是 `index.html` + `case/…/index.html` 的目录树，不能多套一层文件夹。

上传完成会打印一个 `https://<hash>.mengyuan-xyz.pages.dev` 预览地址，同时自动成为生产版本。

**若改用浏览器拖拽**：把 `deploy/site/index.html` 压成 zip（`index.html` 必须在压缩包根目录）
→ Pages 项目 → **Create a new deployment** → 拖入 → Deploy。域名与 DNS 全程不用动。

> 环境备注（2026-10-07 实测）：官方 npm 源走代理会 `ECONNRESET`，只能用 npmmirror；
> 而 npmmirror 不装可选平台二进制，需显式补两条：
> `npm i @cloudflare/workerd-windows-64 @esbuild/win32-x64 --registry=https://registry.npmmirror.com`
> 否则 wrangler 启动即报 `could not be found, and is needed by workerd / esbuild`。

> 上线备注（2026-10-08 实测）：Cloudflare 的 **Email Address Obfuscation**（Scrape Shield，注册默认开启）
> 会把页面里的 `mailto:` 与可见邮箱改写成 `/cdn-cgi/l/email-protection` 和 `[email protected]`。
> 页脚邮箱已用 `<!--email_off-->` 与 `<!--/email_off-->` 包住豁免（Cloudflare 会吃掉这对标记本身）。
> 想整站关掉：dashboard → Security → Settings → Email Address Obfuscation → Off。

详细逐步操作见 `deploy/Cloudflare-Pages-上线清单.md`。

### Git 与云端构建

本站已纳入 git 版本管理（`main` 分支），入库 **54 个文件 / 0.59 MB**。
`.gitignore` 排除：`dist/`（构建产物）、`_probe/` 下的临时件与截图（脚本保留）、
`v1_aetherflow/assets/`（6 MB 人像原图）、`deploy/*.zip`。

**云端构建配置**（Pages v3 镜像自带 Python 3.13.3）：

| 设置项 | 值 |
|---|---|
| 生产分支 | `main` |
| 构建命令 | `python build.py` |
| 构建输出目录 | `dist` |

- `build.py` 只用标准库，可在云端跑；`build_thumbs.py` **不行**（依赖 Pillow 与 numpy），
  它只在你本地换了 CAD / EPLAN 原始渲染时重跑，产出的 WebP 已入库。
- 已实测：`git archive HEAD` 导出干净检出 → `python build.py` → 与本地 `dist/` **逐字节一致**（7/7 页）。
- 迁移自定义域的安全顺序（先挂子域验证、再搬 apex、可回滚）见
  `deploy/Cloudflare-Pages-上线清单.md` 第 10 节。



| 区块 | id | 内容 |
|---|---|---|
| 导航 | - | 技能 / 案例 / 问答 / 联系 + 亮暗切换 + 订阅按钮 |
| Hero | - | 「正在构建 · 机械设计 × Agent」+ 渐变大标题 + 双 CTA + 3D mockup（skill 调用 + 自检面板 + 四步条） |
| 技能库 | `#skills` | 9 张卡片：SW 建模 / SW 装配 / Motion / EPLAN / CAXA / 渲染出图 / Photoshop / 视频蒸馏 / MCP 接入 |
| 工作流案例 | `#cases` | 6 个案例轮播，每张卡带**真实渲染图**：齿轮油泵装配 / 王冠瓶盖 / 参数化齿轮 / 漏斗杯 / 安装板 / 电机正反转控制图 |
| 问答 | `#faq` | 6 条手风琴 |
| 订阅 | `#contact` | 邮箱校验 + loading + toast |
| 站内搜索 | 任意 | 导航栏搜索按钮，或快捷键 `/` 与 `Ctrl/⌘+K`。索引 25 条（9 技能 + 6 案例 + 6 问答 + 4 区块），选中即跳转并闪烁高亮 |
| 案例详情页 | `/case/<slug>/` | 6 个独立页：大图 + 概览 + 参数表 + 步骤 + 细节图 + 接口清单 + 上/下案例导航。首页每张案例卡的「查看详情」与页脚都能进 |

### 详情页内容从哪来（重要）

`cases.py` 里每一条都不许编，来源只有三处：

1. **脚本头部的 docstring** —— 例如王冠瓶盖的「图片反求」段落写着 FFT 主频 18、齿尖间距 20.0°、
   归一化半径 0.907 / 0.844 / 0.702、拔模 11.08°，安装板的头部写着 5 条本机 API 坑位；
2. **脚本里真实出现过的调用与次数** —— 例如齿轮的 `CreateEquationSpline2 x8`、
   `FeatureCircularPattern3 x4`，用 grep 统计出来的；
3. **磁盘上真实存在的产物** —— `motion_run.py` 头部写着「齿轮油泵装配 + 旋转马达 + 计算 + 采样角速度」，
   且 `motion_curve.png` 与 `motion_result.csv` 确实存在，所以油泵那页才敢放 Motion 曲线。

顺手改掉的两处旧措辞（原来的写法与脚本不符）：
- 装配原来写「先解轻化再约束」，实际脚本是「插入后趁还原态立即用 `GetCorrespondingEntity` 取配合面」；
- Motion 原来写「验证行程与干涉」，实际是「加旋转马达、计算、采样角速度」。


### 交互与跳转（2026-10-08 追加）

| 能做什么 | 怎么触发 |
|---|---|
| 搜索技能 / 案例 / 问答 / 区块 | 点导航栏「搜索」，或按 `/`、`Ctrl/⌘+K`；↑↓ 选择，Enter 跳转，Esc 关闭 |
| 跳到某个案例 | 点技能卡任意处（整卡可点，链接铺满卡片），会切到对应案例并高亮 |
| 按标签找相关内容 | 点案例卡下方的标签（如 `SolidWorks`）→ 用该标签发起搜索 |
| 回到顶部 | 滚动超过一屏后右下角出现按钮 |

搜索索引在运行时从 DOM 构建，不另存一份文案，改内容不会漏。跳转位置自己算纵向偏移，
不用 `scrollIntoView`：轮播是 `overflow:hidden` 的横向滚动容器，用它会连带改掉 `scrollLeft`、打乱 transform 定位。
高亮只用 `opacity` 动画（`.hit::after`），不碰颜色与布局。

## 四、配色系统（v2）

从 v1 的「紫罗兰 → 霓虹粉 + 青」换成**蓝图蓝 → 青碧 + 机械琥珀**，贴合机械设计 + 工程软件的调性。

| 角色 | Token | 暗色 | 亮色 |
|---|---|---|---|
| 主色（渐变起） | `--g1` | `#3B82F6` | `#2563EB` |
| 副色（渐变止 / 图标） | `--a2` | `#2DD4BF` | `#0D9488` |
| 主色（图标描边） | `--a1` | `#60A5FA` | `#2563EB` |
| 第三色（点缀） | `--a3` | `#FBBF24` | `#B45309` |
| 背景 | `--bg` | `#0A0B1A` | `#E9EEF7` |

- 渐变：`--grad: linear-gradient(100deg, var(--g1), var(--a2))`，用于 CTA、标题、进度条
- **明暗两套只调明度、不改色相**（单一主题锁）。亮色主题下 `#2DD4BF` 在白底对比度不足，
  故降到 `#0D9488`；图标描边同理，这是分辨率对比度的必要调整。
- 改配色只需动 `src/10_tokens.css` 里的 token；散落在别处的硬编码色值只有：品牌标渐变
  （`40_body_a.html` / `60_body_c.html` 的 `#markGrad`）、favicon（`00_head.html`）、
  mockup 顶栏三个缩写圆（`20_components.css` 的 `.mock__people i:nth-child`）。

## 五、待你补齐的占位内容

| 项 | 现状 | 怎么改 |
|---|---|---|
| 品牌名 | **已确认就是 `MENGYUAN`**（2026-10-08 用户拍板），7 个页面标题与导航、页脚都在用 | 不用动 |
| 页脚联系方式 | **已落地**：GitHub `https://github.com/leea16242`（核准过账号存在）+ 邮箱 `mailto:leea16242@gmail.com`，都是「图标 + 文字」胶囊样式。X 与 LinkedIn 已删除 | 换账号改 `src/60_body_c.html` 的 `.socials` 两处即可 |
| 头像 / 个人照片 | **已全部移除**。AI 人像场景换成 SVG 工具徽标，页面现在零图片 | 若要放本人照片，把图片转 base64 内嵌进 `.qcard__badge` 位置 |
| 社交链接 | 4 个图标都指向 `#top` 占位 | 已处理，见上行「页脚联系方式」 |
| 页脚链接 | 全部指向真实锚点（无死链），但不是独立页面 | 案例列已改为指向 6 个详情页 |
| 案例描述 | 用你自己项目的技术描述，**未含客户名** | 公开前请复核一遍措辞 |
| 案例配图 | 已放 6 张真实渲染（`assets/cases/`）。**名片版式故意没放**：那两张预览带客户品牌，公开有法律风险 | 要放就说一声，或者换别的件 |

## 六、规格落实

| 要求 | 实现 |
|---|---|
| 硬编码 Lucide 风格 SVG，无 CDN / Emoji | 全部内联 `<svg>`，`stroke-width 1.6~1.9` |
| 动画只动 transform / opacity | 入场、hover、拖拽、旋钮、toast、浮 chip、光晕漂移均为 transform/opacity |
| 入场用 IntersectionObserver | `rootMargin 0 0 -6%` + `threshold .1`，逐个 unobserve，另有 2.6s 兜底定时器 |
| 暗色默认、亮色可切 | `html[data-theme]` 双套 token，`localStorage.af-theme` 记忆 |
| prefers-reduced-motion 塌缩 | 全局 transition/animation → `.001ms`，入场直接可见，mockup 去 3D，关自动播与视差 |
| 零 em-dash | `build.py` 强制校验，命中即报错不出包 |

## 七、性能：为什么之前卡，怎么修的

首屏卡顿的根因是**两个叠加的填率炸弹**，而不是「毛玻璃本身有问题」。

### 实测数据（无头 Chrome，1440×900）

| 指标 | 修复前 | 修复后 |
|---|---|---|
| `backdrop-filter` 层数 | 34 | 11 |
| 模糊采样总面积 | 3191k px² = **视口 2.79 倍** | 104k px² = 0.09 倍 |
| 首屏内采样面积 | 531k px² | 88k px²（导航层 `opacity:0` 时不绘制） |
| `filter: blur()` 层 | **5 层**：3 个光斑各 96px（约 100 万 px²）+ 2 个大光晕 48/52px | **0** |
| 视口内像素变化（对比截图） | — | 平均差 5/255；仅 5.97% 像素差 >25，且集中在刻意调整的 mockup 窗口 |

### 根因链条
1. 3 个 **96px 高斯模糊**的巨型光斑在无限循环漂移；
2. 它们是最底层背景，于是**每帧都在变**；
3. 上面有 **34 层毛玻璃**要对自己的背景取景模糊；
4. 背景每帧变 → 34 层每帧全部失效、全部重算。`34 × 每帧` 的重复模糊就是卡顿来源。

### 做的四件事
1. **光斑不再用 `filter: blur(96px)`**：改成 `radial-gradient(closest-side, currentColor, transparent)`
   直接画出柔和边界。省掉百万像素级高斯模糊，动画层只剩 `transform` 变化。
2. **`mock__glow` / `sub__halo` 去掉 `filter: blur()`**：它们本身已经是径向渐变，模糊纯属重复劳动。
3. **毛玻璃只留在「背后真有内容」的地方**（导航条、浮动 chip、移动端导航面板、toast）。
   卡片 / FAQ / 订阅卡片背后是平滑渐变，模糊在视觉上看不出差别，代价却是一整个表面的全量重采样
   → `.glass` 去掉 `backdrop-filter`，靠边框 + 内高光维持玻璃板观感。
4. **`mock__win` 去掉模糊**，改用更实的 `--panel` 底色 + 顶部高光。顺带把光晕挪到窗口下方，
   避免透进窗口内部形成一块突兀亮斑。
5. 附带：`reveal` 入场位移 22px→16px、时长 0.85s→0.65s；`--shadow` 缩小一档。

### 顺手修掉的真 bug
`.nav__bar>*{position:relative}` 的选择器权重与 `.nav__glass` 相同且书写在后，
把导航毛玻璃层的 `position:absolute` 覆盖成了 `relative` → 它一直是个 **0×0 的空元素**，
**导航的毛玻璃从未渲染过**。已改为只作用于 `.brand / .nav__links / .nav__tools`。

### 还想更快的话
- 浏览器设置里确认**硬件加速已开启**（关掉的话任何模糊都会退化成软件渲染，必卡）
- 低配设备可以再加一层降级：检测 `navigator.hardwareConcurrency <= 4` 时把剩下的 4 个小模糊也去掉
- 长页面可上 `content-visibility: auto`（需配 `contain-intrinsic-size`，否则滚动条会跳）

## 八、自检结果（2026-10-07 实测，性能修复后复跑）

- **交互自测**（无头 Chrome 驱动真实 DOM 事件）：FAQ 手风琴、主题切换 + 持久化、
  轮播 next/prev 与 `aria-current`、表单非法/合法/loading/按钮置灰/toast/输入清空
  —— 全部通过，**无 `window.onerror`**
- **无横向溢出**：390px 布局下 `scrollWidth == clientWidth`，最右元素 355px < 375px
- **合规**：零 em-dash / en-dash、零 Emoji、零非拉丁字符，唯一 `http://` 是 SVG 命名空间
- **看图确认**：1440 暗色首屏、1440 亮色首屏、1440 整页三片、390 移动首屏均已亲自核对
