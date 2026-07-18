import { defineStore } from 'pinia'

const THEME_STORAGE_KEY = 'theme'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    currentTheme: localStorage.getItem(THEME_STORAGE_KEY) || 'light',
    themes: {
      light: {
        name: '浅色模式',
        primaryColor: '#4F46E5',
        primaryDark: '#3730A3',
        bgBase: '#F8FAFC',
        bgSurface: '#FFFFFF',
        textPrimary: '#0F172A',
        textSecondary: '#64748B'
      },
      dark: {
        name: '深色模式',
        primaryColor: '#818CF8',
        primaryDark: '#A5B4FC',
        bgBase: '#0F172A',
        bgSurface: '#1E293B',
        textPrimary: '#F8FAFC',
        textSecondary: '#94A3B8'
      },
      violet: {
        name: '紫罗兰',
        primaryColor: '#7C3AED',
        primaryDark: '#6D28D9',
        bgBase: '#FAF5FF',
        bgSurface: '#FFFFFF',
        textPrimary: '#0F172A',
        textSecondary: '#64748B'
      },
      emerald: {
        name: '森林绿',
        primaryColor: '#059669',
        primaryDark: '#047857',
        bgBase: '#F0FDF4',
        bgSurface: '#FFFFFF',
        textPrimary: '#0F172A',
        textSecondary: '#64748B'
      }
    }
  }),

  getters: {
    getCurrentTheme: (state) => state.currentTheme,
    getThemeConfig: (state) => state.themes[state.currentTheme],
    getAllThemes: (state) =>
      Object.keys(state.themes).map((key) => ({
        id: key,
        name: state.themes[key].name,
        primaryColor: state.themes[key].primaryColor
      }))
  },

  actions: {
    setTheme(themeName) {
      if (!this.themes[themeName]) return
      this.currentTheme = themeName
      localStorage.setItem(THEME_STORAGE_KEY, themeName)
      this.applyTheme()
    },

    applyTheme() {
      const root = document.documentElement
      const theme = this.themes[this.currentTheme]
      const isDark = this.currentTheme === 'dark'

      // 设置 data-theme 属性
      root.setAttribute('data-theme', this.currentTheme)

      // 切换 body class，保留其他可能的 class
      document.body.classList.remove('theme-dark')
      if (isDark) {
        document.body.classList.add('theme-dark')
      }

      // 计算衍生色
      const primary = theme.primaryColor
      const primaryDark = theme.primaryDark
      const primaryLight = isDark ? `${primary}26` : `${primary}15`
      const primarySoft = isDark ? `${primary}4D` : `${primary}26`

      // 根据主题设置核心变量
      this.applyColorScheme(
        theme.bgBase,
        theme.bgSurface,
        theme.textPrimary,
        theme.textSecondary
      )

      // 覆盖 Vant 变量和自定义强调变量
      const vars = {
        '--primary': primary,
        '--primary-dark': primaryDark,
        '--primary-light': primaryLight,
        '--primary-soft': primarySoft,
        '--van-primary-color': primary,
        '--van-tab-active-text-color': primary,
        '--van-tabs-bottom-bar-color': primary,
        '--van-button-primary-background': primary,
        '--van-button-primary-border-color': primary
      }

      Object.entries(vars).forEach(([key, value]) => {
        root.style.setProperty(key, value)
      })
    },

    applyColorScheme(bgBase, bgSurface, textPrimary, textSecondary) {
      const root = document.documentElement
      const vars = {
        '--bg-base': bgBase,
        '--bg-surface': bgSurface,
        '--text-primary': textPrimary,
        '--text-secondary': textSecondary,
        '--van-background': bgBase,
        '--van-background-2': bgSurface,
        '--van-text-color': textPrimary,
        '--van-text-color-2': textSecondary,
        '--van-nav-bar-background': bgSurface,
        '--van-nav-bar-title-text-color': textPrimary,
        '--van-cell-group-background': bgSurface
      }
      Object.entries(vars).forEach(([key, value]) => {
        root.style.setProperty(key, value)
      })
    },

    initTheme() {
      this.applyTheme()
    }
  }
})
