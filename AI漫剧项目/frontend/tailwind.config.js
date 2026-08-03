/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        // 品牌色：镜光紫 -> 电光青（PRD 8.6.1）
        brand: {
          violet: '#7F77DD',
          cyan: '#1D9E75',
        },
        // 影院级暗色底
        abyss: {
          950: '#08080f',
          900: '#0d0d18',
          850: '#12121f',
          800: '#171726',
          700: '#1f1f33',
        },
      },
      fontFamily: {
        display: ['"Noto Serif SC"', 'serif'],
        body: ['"PingFang SC"', '"Microsoft YaHei"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'Consolas', 'monospace'],
      },
      borderRadius: {
        glass: '16px',
      },
      boxShadow: {
        glow: '0 0 24px rgba(127, 119, 221, 0.25)',
        card: '0 8px 32px rgba(0,0,0,0.45)',
      },
    },
  },
  plugins: [],
}
