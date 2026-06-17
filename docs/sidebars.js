// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  mainSidebar: [
    {
      type: 'category',
      label: 'Start here',
      collapsed: false,
      items: ['OVERVIEW', 'quickstart', 'ABOUT_THESE_DOCS'],
    },
    {
      type: 'category',
      label: 'How-to guides',
      items: ['lakebase-setup', 'FACILITATOR_GUIDE', 'RUNNING_A_SESSION'],
    },
    {
      type: 'category',
      label: 'Concepts',
      items: ['PARTICIPANT_BRIEF', 'DISCOVERY', 'FAQ'],
    },
    {
      type: 'category',
      label: 'Reference',
      items: ['ERRORS', 'spec-coverage'],
    },
    {
      type: 'category',
      label: 'Changelog & roadmap',
      items: [
        'CHANGELOG',
        {
          type: 'category',
          label: 'Roadmap',
          items: [
            'roadmap/v2_master_north_star',
            'roadmap/llm_judge_active_learning_prd',
            'roadmap/grading_rubrics_research',
          ],
        },
      ],
    },
    // README (a link-index) is intentionally folded — the grouped sidebar is the map.
    // USING_WITH_AGENTS folded into 'How this project works' (ABOUT_THESE_DOCS).
    // No 'Tutorials' category until a real first-run tutorial exists.
  ],
};

module.exports = sidebars;
