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

首次推送会弹出 GitHub 授权页，点授权即可。远程、分支、凭据助手都已配好，**只差这一条命令**。

> 凭据助手已改成**绝对路径**：
> `credential.helper = C:/Users/<user>/AppData/Local/hermes/git/mingw64/bin/git-credential-manager.exe`
> （写在 `.git/config`，不入库）。原因：本机 `git` 用的 hermes 发行版把 GCM 放在 `mingw64/bin`，
> 而该目录**不在持久化 PATH 里**，按名字写 `manager` 会找不到。改绝对路径后与 PATH 无关。

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

