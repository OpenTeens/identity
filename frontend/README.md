# Farm + Vue

This template should help you start developing using Vue and TypeScript in Farm.

## Setup

Install the dependencies:

```bash
pnpm install
```

## Get Started

Start the dev server:

```bash
pnpm start
```

Build the app for production:

```bash
pnpm build
```

Preview the Production build product:

```bash
pnpm preview
```

## Dev Steps

1. 安装依赖，随便用啥包管理器 QAQ
2. 启动后端，一定要在 `35271` 端口，这个端口写在 `farm.config.ts` 里面惹
3. 启动前端，用比如 `pnpm dev` 的命令启动前端，同样可以用其他包管理器
4. 测试 OAuth 流程可以用 [OpenID Connect Playground](https://openidconnect.net/)，注意这里需要一个公网可以访问的服务，可以用
   cf tunnel 啥的

## Prod Steps

1. 安装依赖，随便用啥包管理器 QAQ
2. 构建前端，使用类似 `pnpm build` 的命令，生成的内容在 `dist` 下面
3. 启动后端
4. 使用类似 `nginx` 的服务，`dist` 目录作为静态内容提供，`/api` 代理到后端，没有匹配的 `url` route 到 `index.html`
