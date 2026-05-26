// @ts-check

const config = {
  title: 'Judge Builder Workshop',
  tagline: 'Setup and facilitation docs for the Databricks workshop app',

  url: 'https://example.com',
  baseUrl: '/docs/',
  trailingSlash: true,

  organizationName: 'databricks-solutions',
  projectName: 'project-0xfffff',

  onBrokenLinks: 'warn',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          path: '../doc',
          routeBasePath: '/',
          sidebarPath: require.resolve('./sidebars.js'),
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  plugins: [
    [
      '@docusaurus/plugin-content-docs',
      /** @type {import('@docusaurus/plugin-content-docs').Options} */
      ({
        id: 'specs',
        path: '../specs',
        routeBasePath: 'specs',
        sidebarPath: require.resolve('./specsSidebars.js'),
      }),
    ],
  ],

  themes: [
    [
      require.resolve('@easyops-cn/docusaurus-search-local'),
      /** @type {import('@easyops-cn/docusaurus-search-local').PluginOptions} */
      ({
        // Query-string cache busting (`?_=hash`) breaks with trailingSlash: true — the
        // dev/prod static server redirects to `search-index.json/?_=…` which 404s.
        hashed: 'filename',
        language: ['en'],
        docsRouteBasePath: ['/', '/specs'],
        docsDir: ['../doc', '../specs'],
        indexBlog: false,
        searchBarShortcut: true,
        searchBarShortcutHint: true,
        searchBarShortcutKeymap: 'mod+k',
        highlightSearchTermsOnTargetPage: true,
        explicitSearchResultPath: true,
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        title: 'Judge Builder Workshop',
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'mainSidebar',
            position: 'left',
            label: 'Docs',
          },
          {
            type: 'docSidebar',
            docsPluginId: 'specs',
            sidebarId: 'specsSidebar',
            position: 'left',
            label: 'Specs',
          },
          {
            href: '/',
            label: 'Open App',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Setup',
            items: [
              {
                label: 'Lakebase Setup',
                to: '/lakebase-setup',
              },
              {
                label: 'Facilitator Guide',
                to: '/FACILITATOR_GUIDE',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Databricks.`,
      },
      prism: {
        additionalLanguages: ['bash', 'json', 'python', 'yaml'],
      },
    }),
};

module.exports = config;
