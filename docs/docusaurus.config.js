// @ts-check

const config = {
  title: 'VibeScaler',
  tagline: 'Setup and facilitation docs for VibeScaler',

  // Deployment target. Defaults serve the docs under the Databricks App at /docs/.
  // The GitHub Pages workflow overrides these via env (.github/workflows/deploy-docs.yml).
  url: process.env.DOCS_URL || 'https://example.com',
  baseUrl: process.env.DOCS_BASE_URL || '/docs/',
  trailingSlash: true,

  organizationName: process.env.DOCS_ORG || 'databricks-solutions',
  projectName: process.env.DOCS_PROJECT || 'project-0xfffff',

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
    [
      '@docusaurus/plugin-content-docs',
      /** @type {import('@docusaurus/plugin-content-docs').Options} */
      ({
        id: 'v2',
        path: '../docs/plans',
        routeBasePath: 'v2',
        // Curated: only the V2 vision docs are published; dated implementation
        // working-plans in the same folder stay internal.
        include: [
          'v2_master_north_star.md',
          'llm_judge_active_learning_prd.md',
          'grading_rubrics_research.md',
        ],
        sidebarPath: require.resolve('./v2Sidebars.js'),
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
        docsRouteBasePath: ['/', '/specs', '/v2'],
        docsDir: ['../doc', '../specs', '../docs/plans'],
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
        title: 'VibeScaler',
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
            type: 'docSidebar',
            docsPluginId: 'v2',
            sidebarId: 'v2Sidebar',
            position: 'left',
            label: 'V2 Vision',
          },
          // App and docs are co-hosted under the Databricks App; on a standalone
          // deploy (GitHub Pages) there is no app to open, so DOCS_STANDALONE drops it.
          ...(process.env.DOCS_STANDALONE
            ? []
            : [
                {
                  // pathname:// escapes baseUrl (/docs/) so this targets the app root on the same host.
                  to: 'pathname:///',
                  label: 'Open App',
                  position: 'right',
                },
              ]),
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
