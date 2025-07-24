import { reactRouter } from "@react-router/dev/vite";
import { defineConfig } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig({
  plugins: [
    reactRouter({
      // プリフェッチを無効化
      future: {
        unstable_optimizeDeps: false,
      },
    }),
    tsconfigPaths(),
  ],
  server: {
    port: 5174, // 5173と被らないように
    host: "0.0.0.0",
    watch: {
      // 分析HTMLファイルの変更を監視しない
      ignored: ['**/public/analysis/**', '**/node_modules/**'],
      // ポーリングを無効化
      usePolling: false,
    },
    fs: {
      strict: false,
      // 大きなファイルの処理を許可
      allow: ['..'],
    },
  },
  // publicディレクトリの最適化
  publicDir: 'public',
  build: {
    // ビルド時も分析ファイルを除外
    copyPublicDir: true,
    rollupOptions: {
      external: [/^\/analysis\//],
    },
  },
  // 最適化設定
  optimizeDeps: {
    exclude: ['public/analysis'],
  },
});