# derp-verifier

Tailscale [DERP](https://tailscale.com/kb/1232/derp-servers) 节点验证服务。通过查询本机 `tailscale status` 获取网络中所有节点的公钥，对 DERP 服务器的客户端验证请求进行放行或拒绝，从而实现仅允许同一 Tailnet 内的节点使用自建 DERP 中继。

## 工作原理

1. DERP 服务器收到客户端连接时，向本服务发送 POST 请求（包含 `NodePublic` 和 `Source` 字段）。
2. 本服务调用 `tailscale status --json` 获取当前 Tailnet 中所有节点的公钥列表。
3. 若请求中的 `NodePublic` 在公钥列表中，返回 `{"Allow": true}`；否则返回 `{"Allow": false}`。

## 快速开始

### 本地运行

需要本机已安装并登录 Tailscale。

```bash
pip install aiohttp
python main.py
```

服务默认监听 `0.0.0.0:8080`，验证端点为 `POST /verify`。

### Docker

```bash
docker build -t derp-verifier .
docker run -d --name derp-verifier -p 8080:8080 derp-verifier
```

> **注意：** 容器内需要能够访问 `tailscale` 命令并已完成认证，通常需要挂载 Tailscale 的 socket 或以 sidecar 方式运行。

预构建镜像也可从 GitHub Container Registry 获取：

```bash
docker pull ghcr.io/<owner>/derp-verifier:latest
```

## API

### `POST /verify`

**请求体 (JSON)：**

```json
{
  "NodePublic": "nodekey:abc123...",
  "Source": "100.x.y.z"
}
```

**响应：**

- 允许：`{"Allow": true}`（200）
- 拒绝：`{"Allow": false}`（200）
- 请求格式错误：`404: Not Found`（404）

## DERP 服务器配置

在自建 DERP 服务器启动参数中指定验证地址：

```
--verify-clients
--verify-client-url=http://localhost:8080/verify
```

## 技术栈

- Python 3.12
- [aiohttp](https://docs.aiohttp.org/) — 异步 HTTP 服务器
- Tailscale CLI — 获取节点公钥信息

## 许可证

[MIT](LICENSE)