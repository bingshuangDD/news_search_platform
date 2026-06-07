import { defineStore } from 'pinia';

export const useThemeStore = defineStore('theme', {
  state: () => ({
    currentTheme: localStorage.getItem('theme') || 'light',
    themes: {
      light: {
        name: '浅色模式',
        primaryColor: '#4F46E5',
        backgroundColor: '#F8FAFC',
        surfaceColor: '#FFFFFF',
        textColor: '#0F172A',
        textSecondary: '#64748B',
        shadowCard: '0 1px 3px rgba(15,23,42,0.04), 0 4px 12px rgba(15,23,42,0.06)'
      },
      dark: {
        name: '深色模式',
        primaryColor: '#818CF8',
        backgroundColor: '#0F172A',
        surfaceColor: '#1E293B',
        textColor: '#F8FAFC',
        textSecondary: '#94A3B8',
        shadowCard: '0 1px 3px rgba(0,0,0,0.3), 0 4px 12px rgba(0,0,0,0.4)'
      },
      violet: {
        name: '紫罗兰',
        primaryColor: '#7C3AED',
        backgroundColor: '#FAF5FF',
        surfaceColor: '#FFFFFF',
        textColor: '#0F172A',
        textSecondary: '#64748B',
        shadowCard: '0 1px 3px rgba(15,23,42,0.04), 0 4px 12px rgba(15,23,42,0.06)'
      },
      emerald: {
        name: '森林绿',
        primaryColor: '#059669',
        backgroundColor: '#F0FDF4',
        surfaceColor: '#FFFFFF',
        textColor: '#0F172A',
        textSecondary: '#64748B',
        shadowCard: '0 1px 3px rgba(15,23,42,0.04), 0 4px 12px rgba(15,23,42,0.06)'
      }
    }
  }),

  getters: {
    getCurrentTheme: (state) => state.currentTheme,
    getThemeConfig: (state) => state.themes[state.currentTheme],
    getAllThemes: (state) => Object.keys(state.themes).map(key => ({
      id: key,
      name: state.themes[key].name,
      primaryColor: state.themes[key].primaryColor
    }))
  },

  actions: {
    setTheme(themeName) {
      if (this.themes[themeName]) {
        this.currentTheme = themeName;
        localStorage.setItem('theme', themeName);
        this.applyTheme();
      }
    },

    applyTheme() {
      const theme = this.themes[this.currentTheme];
      const root = document.documentElement;

      // 设置 data-theme 属性用于 CSS 选择器
      root.setAttribute('data-theme', this.currentTheme);

      // 主题 class（用于 body.theme-dark 等全局覆盖）
      document.body.className = '';
      if (this.currentTheme !== 'light') {
        document.body.classList.add(`theme-${this.currentTheme}`);
      }

      // 批量注入 CSS 自定义属性
      const vars = {
        '--primary-color': theme.primaryColor,
        '--background-color': theme.backgroundColor,
        '--surface-color': theme.surfaceColor,
        '--text-color': theme.textColor,
        '--text-color-light': theme.textSecondary,
        '--shadow-card': theme.shadowCard,
        '--van-primary-color': theme.primaryColor,
        '--van-background': theme.backgroundColor,
        '--van-background-2': theme.surfaceColor,
        '--van-text-color': theme.textColor,
        '--van-text-color-2': theme.textSecondary,
        '--van-nav-bar-background': theme.surfaceColor,
        '--van-nav-bar-title-text-color': theme.textColor,
        '--van-tab-active-text-color': theme.primaryColor,
        '--van-tabs-bottom-bar-color': theme.primaryColor,
        '--van-button-primary-background': theme.primaryColor,
        '--van-button-primary-border-color': theme.primaryColor,
      };

      Object.entries(vars).forEach(([key, value]) => {
        root.style.setProperty(key, value);
      });
    },

    initTheme() {
      this.applyTheme();
    }
  }
});