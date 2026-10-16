# Cloudflare Pages 上线清单：mengyuan.xyz

## 0. 前置事实（本机实测）

| 项 | 值 |
|---|---|
| 注册商 | Spaceship（有邮件转发：MX `mx1/mx2.efwd.spaceship.net`，TXT `v=spf1 include:spf.efwd.spaceship.net ~all`） |
| DNS 托管 | Cloudflare（NS `fay.ns.cloudflare.com` / `algin.ns.cloudflare.com`） |
| apex `mengyuan.xyz` | **无 A 记录**，未指向任何服务器 |
| `www` | 当前无记录 |
| 待上线文件 | `deploy/glass-landing-site.zip`（内含**根级** `index.html`，145 kB） |

**判据**：DNS 已在 Cloudflare + apex 无 A 记录 → 与现有解析零冲突，绑定时 Cloudflare 自动建 CNAME。
**红线**：MX / TXT(SPF) 记录一律不动，否则邮箱转发会挂。

## 1. 建 Pages 项目（约 2 分钟）

1. 打开 `https://dash.cloudflare.com/?to=/:account/workers-and-pages`
2. 点 **Create application**
3. 点 **Get started** → **Drag and drop your files**
4. **Project name** 填 `mengyuan-xyz`（决定未来的 `<name>.pages.dev` 预览地址）
5. 把 `deploy/glass-landing-site.zip` 直接拖进上传框
6. 点 **Deploy site**（按钮也可能显示 **Save and Deploy**）

**验收**：出现 `https://mengyuan-xyz.pages.dev`，打开能看到落地页首屏。

> 限制：拖拽上传 1,000 文件 / 单文件 25 MiB。我们只有 1 个文件 145 kB，无压力。

## 2. 绑 apex 域名 mengyuan.xyz

1. 进入该项目 → 左侧 **Custom domains**
2. 点 **Set up a domain**
3. 填 `mengyuan.xyz` → **Continue**
4. 因为该 zone 就在你的 Cloudflare 账号内，Cloudflare 会**自动创建 CNAME 记录**并开始签发证书
5. 等状态从 `Initializing` / `Pending` 变成 **Active**（通常 1 到 5 分钟，证书签发最长 15 分钟）

> ⚠️ **不要提前手工加 CNAME**。官方明确：未在 Pages 里先关联域名、就手工加一条指向 `<site>.pages.dev` 的 CNAME，解析会失败并报 **522**。

## 3. 绑 www 并决定跳转

1. 同一个 **Custom domains** 页 → **Set up a domain** → 填 `www.mengyuan.xyz` → **Continue**（同样会自动建 CNAME）
2. 等 Active
3. 二选一定 www 的行为：

| 方案 | 做法 | 适用 |
|---|---|---|
| **A（推荐，SEO 友好）** | www 已直接服务同一站点，再到 **Rules → Redirect Rules** 加一条：`www.mengyuan.xyz/*` → `https://mengyuan.xyz/$1`，状态 301 | 想要唯一主域名 |
| B（最省事） | 不绑 www，只在 **DNS → Records** 加 `www` → CNAME → `mengyuan.xyz`，橙色云朵开启 | 想让 Cloudflare 自己处理 |

## 4. 强制 HTTPS（细化版）

> 先看实测结论：`http://mengyuan.xyz` 已经返回 **301 → https**，说明重定向这条已经通了。
> 本步只需**核对加密模式**并补两个开关。

### 4.1 核对加密模式（最关键，做错会重定向循环）
1. 左侧边栏顶部从 **Workers & Pages** 切回 **mengyuan.xyz** 这个 zone（点左上角账号处的域名，或用顶部搜索框输 `mengyuan.xyz`）
2. 左侧边栏 → **SSL/TLS** → **Overview**
3. 在 **Encryption mode**（加密模式）卡片里选 **Full (strict)**
   - 千万不要选 **Flexible**：Pages 本身已在 443 上提供证书，Flexible 会让 Cloudflare 用 http 回源，直接导致 **ERR_TOO_MANY_REDIRECTS**

### 4.2 Edge Certificates 三个开关
左侧边栏 → **SSL/TLS** → **Edge Certificates**：

| 设置项 | 目标值 | 说明 |
|---|---|---|
| **Always Use HTTPS** | **On** | 实测已生效，确认开关是开的 |
| **Minimum TLS Version** | **TLS 1.2** | 关掉 1.0/1.1 的老客户端 |
| **Automatic HTTPS Rewrites** | **On**（可选） | 自动把页面里的 http 资源改写成 https |

### 4.3 HSTS 建议先不要开
**Edge Certificates → HSTS → Enable HSTS**：一旦开启，浏览器会**长期缓存**「此域名只走 HTTPS」，
之后若配置出错想退回 http 会非常麻烦。上线初期先不开，等站点稳定运行一段时间再考虑。

### 4.4 如果想验证加密模式
```bash
curl -sI http://mengyuan.xyz | head -3     # 期望 301 + Location: https://mengyuan.xyz/
curl -sI https://mengyuan.xyz | head -3    # 期望 200
```
如果 https 访问报 525/526，说明加密模式或证书还没就绪，回到 4.1 检查。

## 5. 上线验收（逐条打勾）

| # | 检查项 | 期望结果 |
|---|---|---|
| 1 | `https://mengyuan.xyz` | 200，正常渲染，地址栏有锁 |
| 2 | `http://mengyuan.xyz` | 301 跳 https |
| 3 | `https://www.mengyuan.xyz` | 200 或 301 到 apex（与第 3 节选择一致） |
| 4 | 亮暗切换 | 点右上开关能切换，刷新后保持选择 |
| 5 | 入场动画 | 滚动时逐块淡入上浮（不是一次性出现） |
| 6 | 轮播 | 每 6 秒自动切换，可鼠标拖拽，悬停暂停 |
| 7 | 订阅表单 | 输入邮箱点 Notify me → 出现 spinner → 底部弹出 toast |
| 8 | 手机打开 | 无横向滚动条，导航收成汉堡菜单 |
| 9 | 邮箱未受影响 | 给 `任意名称@mengyuan.xyz` 发测试信，仍能转发到你的邮箱 |

## 6. 排错速查

| 现象 | 原因 | 处理 |
|---|---|---|
| 522 / 域名不解析 | 手工加了 CNAME 但没在 Pages 关联域名 | 先在 **Custom domains** 走完 Set up a domain |
| 长期 Pending，证书签不出 | zone 有 CAA 记录，不允许 Cloudflare 的 CA | 加 CAA 允许 `letsencrypt.org`、`pki.goog`、`ssl.com` |
| 重定向循环 | SSL/TLS 模式被设成 Flexible | 改成 **Full (strict)** |
| 页面 200 但内容是旧的 | 边缘缓存 | **Caching → Purge Everything** |
| 你打不开但别人能打开 | 本地 DNS 缓存 | `ipconfig /flushdns` |

CAA 检查（Git Bash 执行；Windows 自带 nslookup 不支持 CAA 类型）：

```bash
nslookup -type=CAA mengyuan.xyz 1.1.1.1
```

或在 Cloudflare **DNS → Records** 搜索框输入 `CAA` 直接看。

## 7. 回滚（恢复初始状态）

1. Pages 项目 → **Custom domains** → 域名右侧三点 → **Remove domain**
2. 域名 → **DNS → Records** → 找到该 CNAME → **Edit → Delete**

之后 `mengyuan.xyz` 回到「无 A 记录」状态，**邮箱不受影响**。

## 8. 明确不需要做的事

- **不需要 ICP 备案**：托管在 Cloudflare（境外），无中国大陆服务器，不触发备案要求
- **不需要服务器 / 数据库 / 构建流程**：纯静态单文件，头像已 base64 内联
- **不需要改 NS**：NS 已经在 Cloudflare
- **不需要动 MX / TXT / SPF**：邮箱转发必须保留

---

## 9. 上线实测记录（2026-10-05 11:16 复核：全部通过）

| 检查 | 实测结果 | 结论 |
|---|---|---|
| `http://mengyuan.xyz` | `HTTP/1.1 301 Moved Permanently`，`Location: https://mengyuan.xyz/` | ✓ 强制 HTTPS 生效 |
| `https://mengyuan.xyz` | `HTTP/1.1 200 OK`，`content-type: text/html; charset=utf-8` | ✓ 站点已上线 |
| 传输字节数 | `147850` bytes，与本机 `deploy/index.html` **完全一致** | ✓ 文件无损坏、无截断 |
| 内联资源 | 5 个 `data:image/jpeg;base64` 头像全部存在 | ✓ 单文件自包含生效 |
| TLS | `ssl_verify_result=0`（证书校验通过） | ✓ |
| 响应头 | `x-content-type-options: nosniff`、`referrer-policy: strict-origin-when-cross-origin`、`cache-control: public, max-age=0, must-revalidate` | ✓ 安全头齐全 |
| `https://www.mengyuan.xyz` | `HTTP/1.1 200 OK`（先前 502 已消失，证书签发完成） | ✓ |

### 剩余可选项（非阻塞，站点已可用）

| 项 | 要不要做 | 说明 |
|---|---|---|
| SSL/TLS 加密模式核对为 **Full (strict)** | **建议做** | 唯一有实际风险的项。若误设为 Flexible，会 `ERR_TOO_MANY_REDIRECTS` |
| www → apex **301** | 建议做 | 目前 apex 与 www 都是 200，属同一内容两个地址；加一条 Redirect Rule 更规范 |
| HSTS | **先不做** | 一旦开启浏览器会长期强制 HTTPS，回退麻烦 |
| IC 备案 | 不需要 | 托管在 Cloudflare，无大陆服务器 |
| 邮箱转发复查 | 建议做一次 | 给 `测试@mengyuan.xyz` 发信，确认仍能转发 |

### 日后改内容并重新部署

```bash
python build_thumbs.py          # 只有 CAD / EPLAN 原始渲染换了才需要跑
python build.py                 # 输出到 dist/，逐页校验占位符与 em dash
export PATH="$HOME/.workbuddy/binaries/node/versions/22.22.2-6:$PATH"
"$HOME/.workbuddy/binaries/node/workspace/node_modules/.bin/wrangler" \
  pages deploy dist --project-name mengyuan-xyz --branch main
```

`dist/` 是**唯一**部署源，站内共 7 页：`index.html` + `case/<slug>/index.html` × 6。

**手动方式**：把 `deploy/mengyuan-site.zip` 拖进 **Create a new deployment**。
压缩包里是 `index.html` 与 `case/…/index.html` 的目录树，**不能再多套一层文件夹**。

> 每次上传都会新建部署，Cloudflare Pages 不会覆盖旧版本，出问题可在 Deployments 里一键回滚。

> ⚠️ **Direct Upload 项目不能事后切换成 Git 集成**（官方限制）。若以后想要「push 到 GitHub 自动部署」，
> 必须**新建一个 Git 集成项目**，再把 `mengyuan.xyz` 从旧项目移除、在新项目里重新 Set up a domain。




---

## 10. Git 集成项目（可选，替代 Direct Upload）

**当前线上跑的是 Direct Upload 项目**（拖 zip / wrangler 上传）。若想「push 即自动部署」，
得**新建一个 Git 集成的项目**，因为 Direct Upload 项目**不能中途切换**成 Git 集成。

### 10.1 云端构建配置（已本地验证成立）

`build.py` 只用 Python 标准库；Cloudflare Pages 的 v3 构建镜像**自带 Python 3.13.3**。
所以仓库里**不需要提交 `dist/`**，让云端现建即可。

| 设置项 | 值 |
|---|---|
| 生产分支 | `main` |
| 构建命令 | `python build.py` |
| 构建输出目录 | `dist` |
| 根目录 | 留空（默认仓库根） |
| 环境变量 | 不需要（要锁版本可加 `PYTHON_VERSION=3.13.3`） |

> 已实测：`git archive HEAD` 导出干净检出 → `python build.py` → 产出的 7 个页面与本地 `dist/`
> **逐字节一致**（文件集合相同、无一处内容不一致）。
>
> 注意 `build_thumbs.py` **不能**在云端跑（依赖 Pillow 与 numpy）。它只在你本地换了
> CAD / EPLAN 原始渲染时才需要重跑，生成的 WebP 已提交进仓库。

### 10.2 迁移自定义域的安全顺序（重要）

同一个域名**只能挂在一个 Pages 项目上**，所以搬域名必然有一次切换，切的时候证书要重签（几分钟）。
按这个顺序做，apex 不会中断：

1. 新项目建好后，先在它上面加**子域** `new.mengyuan.xyz`，等状态 Active
2. 逐个打开 `https://new.mengyuan.xyz/` 与 6 个详情页，确认全部 200 且显示正常
3. 确认无误后，到**旧项目** → Custom domains → 移除 `mengyuan.xyz` 与 `www.mengyuan.xyz`
4. 到**新项目** → Custom domains → Set up a domain → 加 `mengyuan.xyz` 与 `www.mengyuan.xyz`
5. 等 Active（通常几分钟），再按第 5 节做一遍上线验收

**回滚**：第 3 步之前旧项目一直可用；万一新项目出问题，把域名按第 3、4 步反向搬回去即可。

### 10.3 需要你做的（浏览器 + 一条命令）

**① 建仓库**：`github.com/new` → 填仓库名 → **不要**勾选初始化 README / .gitignore / license
（会与本地已有提交冲突）→ Create
实际仓库名是 **`mengyuan-xyz`**（不是 `mengyuan.xyz`，后者不存在）。

**② 装 Cloudflare 的 GitHub App**：Cloudflare → Workers & Pages → Create → Pages →
**Connect to Git** → 授权 GitHub → 选仓库。（已完成）

**③ 推送代码**（必须你在自己的终端跑，原因见下）：

```bat
:: cmd.exe 或 PowerShell —— 注意反斜杠与盘符
cd /d D:\AIchat\AIdailychat\WorkBuddy-work\glass-landing
git push -u origin main
```

```bash
# Git Bash —— 路径用正斜杠，/d 是 D 盘的挂载点
cd /d/AIchat/AIdailychat/WorkBuddy-work/glass-landing && git push -u origin main
```

> ⚠️ **别把两种语法混用**：`cd /d/AIchat/...` 在 Git Bash 下正确，在 cmd 下会报「命令语法不正确」
> （cmd 把 `/d` 当切换盘符的开关）。反过来 `cd /d D:\...` 在 Git Bash 下也错。
> 判断你在哪个 shell：cmd 提示符是 `C:\Users\...>`，Git Bash 是 `user@host MINGW64 ~$`。

首次推送走 **Git Credential Manager 的设备码流程**（不用 token、不用粘贴）：

1. 终端会先打印一行提示和一个 **8 位码**（形如 `ABCD-1234`）
2. 浏览器打开下面这个网址（单独一行，直接整行复制）：

```
https://github.com/login/device
```

3. 输入那 8 位码 → **Authorize**
4. 回到终端，推送自动继续，出现 `* [new branch] main -> main` 即成功

凭据会存进 **Windows 凭据管理器**，以后推送静默完成，不用再授权。

> **凭据是怎么配的**：仓库级 `credential.helper` 先置空（清掉系统继承的 `helper-selector`），
> 再指向本机 GCM 的绝对路径；并设 `credential.gitHubAuthModes = device` 强制走设备码。
> 三者都写在 `.git/config`，**不入库**。与 PATH 无关，cmd 与 Git Bash 行为一致。
>
> 想改成浏览器 OAuth：把 `device` 换成 `browser`；想立刻重新登录：
> `git-credential-manager github login --device --force`

> ⚠️ **为什么 AI 这边推不了**：本机沙箱给命令行注入了出口代理（`http(s)_proxy=127.0.0.1:50109`），
> 该代理**放行了 `api.github.com` 但没放行 `github.com`**，而 git 推送走的正是后者。
> 实测两种 TLS 后端都失败：
> schannel → `server closed abruptly (missing close_notify)`；
> openssl → `CONNECT tunnel failed, response 502`；
> 绕过代理直连 → `Connection was reset`。
> 所以这一步只能由你在没有该代理的终端里执行。

### 10.4 推完之后的顺序

1. GitHub 上确认 `main` 分支有 2 个提交（`feat:` 与 `docs:`）
2. Cloudflare → Workers & Pages → Create → Pages → **Connect to Git** → 选 `mengyuan-xyz`
3. 构建配置按 10.1 填（命令 `python build.py`，输出目录 `dist`）→ Save and Deploy
4. 等首次构建完成，先只验证它的 `*.pages.dev` 地址与 6 个详情页
5. 全部正常后再按 10.2 搬自定义域



---

## 11. Git 集成项目现状（2026-10-09）

| 项 | 值 |
|---|---|
| Pages 项目名 | `mengyuan-xyz-git` |
| 源仓库 | `leea16242/mengyuan-xyz`（GitHub，生产分支 `main`） |
| 构建命令 | `python build.py` |
| 输出目录 | `dist` |
| 预览地址 | `https://mengyuan-xyz-git.pages.dev` |
| 正式域名 | 仍在**旧项目** `mengyuan-xyz`（Direct Upload）上，未迁移 |

### 触发构建
往 `main` 推任何提交即自动构建部署，不需要本地跑 wrangler。

### 注意
- 面板里另有一个**同名 Worker** `mengyuan-xyz-git`（Workers 产品，不是 Pages）。
  它没被使用，容易和 Pages 项目混淆，可以删掉：Workers & Pages → 该 Worker → Settings → Delete。
- 本项目是用 Cloudflare API 建的，不是面板的 Connect to Git 流程。
  两者产物相同，但**只有面板流程会自动跑一次首次构建**；API 建的需要一次 push 才触发。


---

## 12. 结论与收尾（2026-10-09）

### 已确认可用
- **Git 集成 Pages 项目**：`mengyuan-xyz-git`，源 `leea16242/mengyuan-xyz`
- **云端构建成功**：`queued → initialize → clone_repo → build → deploy` 五阶段全绿，**耗时 11 秒**
- **7 个页面全部 200**（在部署地址与生产别名上各验一遍）：
  `/` 与 `/case/{pump,crown,gear,funnel,bracket,eplan}/`

### ★ 用 API 触发构建（不需要 push）
```bash
POST /accounts/{account_id}/pages/projects/{project}/deployments
```
对 **Git 项目**也有效：会去克隆仓库并跑构建。返回 `{id, url}`，
再用 `GET .../deployments` 看 `stages` 各阶段状态。
（面板的 Save and Deploy 只是替你做这件事；API 建的项目不会自动跑首次构建。）

### 域名迁移必须在面板做
本机 wrangler 的 OAuth token 权限里有 `pages:write`，但**没有 `dns_records:edit`**，
所以用 API 加自定义域时 **DNS 记录建不出来**（`new.mengyuan.xyz` 一直是
`status=pending / verification=pending`）。面板里有 DNS 权限，会一并建好记录并签证书。

### 迁移步骤（面板，可回滚）
1. 新项目 `mengyuan-xyz-git` → **Domains** 标签 → Add domain → `mengyuan.xyz`
   （此时会提示已被旧项目占用）
2. 旧项目 `mengyuan-xyz` → Domains → 删除 `mengyuan.xyz` 与 `www.mengyuan.xyz`
3. 回到新项目重新加这两个域名 → 等 Active（证书重签几分钟）
4. **回滚**：把两个域名按同样方式搬回旧项目即可（旧项目的部署记录都还在）

---

## 13. 两条 API 兜底通道（github.com 不通时用）

本机 github.com 时通时断（git push 会报 Recv failure: Connection was reset），
但 api.github.com 与 api.cloudflare.com 一直可达，所以有两条兜底：

### 13.1 推代码：GitHub Git Data API

用 `_probe/push_via_api.py`：

- token 自己从 `git credential fill` 取（Windows 凭据管理器里 GCM 存的 OAuth token），不用手输
- 只推远端缺的提交（先读 `GET /git/refs/heads/main`）
- 流程 `blob -> tree -> commit -> 更新 ref`，每步断言 SHA

> ⚠️ 已知限制：API 算出的 **tree SHA 与本地 git 不一致**（用同一份文件列表重建也复现不出），
> 因此推上去的**提交 SHA 与本地不同**。逐文件核对过内容一致（文件集合 + blob SHA 全同）。
> 后果：本地 main 与远端分叉，用户下次手动 `git push` 会被拒，
> 需先 `git fetch && git reset --hard origin/main` 对齐一次。
> **所以 API 推送只当兜底，不要当常规手段。**

### 13.2 部署：Cloudflare API 触发构建

```bash
POST /accounts/{account_id}/pages/projects/mengyuan-xyz-git/deployments
```

对 Git 项目同样有效（会 clone 仓库并构建），返回 `{id, url}`；
用 `GET .../deployments` 看 `stages` 各阶段状态。无需 push、无需 wrangler 凭据有效。

> 顺带验证到：**push 触发自动构建的 webhook 是通的**（API 推送后 Cloudflare 自动起了一次构建）。
> 正常路径仍是「commit + push」，13.1 与 13.2 只在网络不通时使用。

---

## 14. ★ Git Data API 的路径转义坑（2026-10-16 定位并修复）

### 症状
用 API 推上去的提交，**tree SHA 与本地 git 算出的总是不一致**（内容核对却全对），
导致提交 SHA 与本地不同、本地与远端分叉。

### 根因
`git ls-tree` 在 `core.quotePath=true`（默认）下，会**给含非 ASCII 的路径加引号并八进制转义**：
```
100644 blob <sha>	"deploy/Cloudflare-Pages-\344\270\212\347\272\277\346\270\205\345\225\206.md"
```
脚本按原样取用这个字符串当路径 → 远端多出一个名叫 `"deploy` 的目录，
文件名也带着 `\344\270\212...` 这样的八进制串 ✗。树自然对不上。

### 修复
改用 **零分隔输出**，路径原样返回：
```python
git("ls-tree", "-r", "-z", ref).decode().split("\0")   # 注意跳过末尾空条目
```
（`_probe/push_via_api.py` 与 `_probe/push_incremental.py` 都已改）

### 修复后的验证（2026-10-16）
全量重推 11 个提交，**每个都打印「SHA 完全一致」**，最终
`远端 main = 本地 HEAD = 94739e0e`，远端顶层条目与本地完全相同（70 文件）。
**分叉彻底消除**，之后用户的 `git push` 是普通快进。

### 教训（写给自己）
1. **别信「内容对得上就万事大吉」**：blob SHA 一致但路径被转义，树照样是错的。
   要验就验到 **tree/commit 的 SHA 相等**，那才是逐字节相同。
2. **用 `-z` 解析 git 的机器可读输出**，别用会被引号转义的 `ls-tree`/`ls-files` 默认输出。
3. **`git reset --hard origin/main` 只在 fetch 确认成功后才安全**：
   2026-10-10 一次 fetch 失败（网络）后照旧 reset，用的是**过期的** origin/main，
   把 4 个本地提交（含「皮带轮支座」案例）回退了。补救靠 `git reflog` 找回提交 SHA 再 `git reset --hard <sha>`。


