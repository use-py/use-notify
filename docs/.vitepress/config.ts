import { defineConfig } from 'vitepress';

export default defineConfig({
  title: 'use-notify',
  description: 'Python 消息通知库',
  lang: 'zh-CN',
  themeConfig: {
    logo: '/favicon.svg',
    nav: [
      { text: '首页', link: '/' },
      { text: '指南', link: '/guide/' },
      { text: 'API', link: '/api/' },
      { text: 'GitHub', link: 'https://github.com/use-py/use-notify' },
    ],
    sidebar: {
      '/guide/': [
        {
          text: '入门',
          items: [
            { text: '简介', link: '/guide/' },
            { text: '快速开始', link: '/guide/getting-started' },
            { text: '装饰器使用', link: '/guide/decorator' },
          ],
        },
        {
          text: '进阶',
          items: [
            { text: '通知渠道', link: '/guide/channels' },
            { text: '配置管理', link: '/guide/configuration' },
            { text: '最佳实践', link: '/guide/best-practices' },
          ],
        },
      ],
      '/api/': [
        {
          text: 'API 参考',
          items: [
            { text: '概述', link: '/api/' },
            { text: 'useNotify', link: '/api/notify' },
            { text: '通知渠道', link: '/api/channels' },
            { text: '装饰器', link: '/api/decorator' },
          ],
        },
      ],
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/use-py/use-notify' },
    ],
    footer: {
      message: '基于 MIT 许可发布',
      copyright: 'Copyright © 2024 use-notify 团队',
    },
  },
});
