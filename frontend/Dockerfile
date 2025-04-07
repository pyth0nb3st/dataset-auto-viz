# 使用Node.js LTS作为基础镜像
FROM node:18-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制所有项目文件
COPY . .

# 构建Next.js应用
RUN npm run build

# 生产环境镜像
FROM node:18-alpine AS runner

# 声明构建参数
ARG NEXT_PUBLIC_API_URL
# 将构建参数设置为环境变量，以便 npm run build 可以访问
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL


WORKDIR /app

# 设置为生产环境
ENV NODE_ENV=production

# 从builder阶段复制必要文件
COPY --from=builder /app/next.config.mjs ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules

# 暴露Next.js运行端口
EXPOSE 3000

# 启动Next.js应用
CMD ["npm", "start"]
