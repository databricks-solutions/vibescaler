import React from 'react';
import Link from '@docusaurus/Link';
import coverageReport from '../../static/spec-coverage.json';

type SpecCoverageData = {
  total_requirements: number;
  covered_requirements: number;
  coverage_percent: number;
};

type CoverageReport = {
  specs: Record<string, SpecCoverageData>;
};

type SpecLinkProps = {
  spec: string;
  children?: React.ReactNode;
};

function defaultLabel(spec: string): string {
  return spec
    .replace(/_SPEC$/, '')
    .split('_')
    .map((word) => word.charAt(0) + word.slice(1).toLowerCase())
    .join(' ');
}

function maturity(percent: number | null): { tone: string; hint: string } {
  if (percent === null) return { tone: 'muted', hint: 'no coverage data yet' };
  if (percent >= 70) return { tone: 'success', hint: 'well-tested' };
  if (percent >= 30) return { tone: 'warning', hint: 'maturing' };
  return { tone: 'muted', hint: 'early' };
}

/**
 * Inline link to a spec page with an at-a-glance coverage bar, so readers
 * can tell whether the feature being discussed is speculative or well-tread
 * without a full <SpecCoverage> block interrupting the prose.
 *
 * Freshness is enforced at publish time, not render time: `just docs-gate`
 * fails CI when a doc page references a spec whose tagged tests are failing,
 * so published docs never describe a feature that isn't currently working.
 *
 * Usage: <SpecLink spec="DATASETS_SPEC" /> or <SpecLink spec="DATASETS_SPEC">dataset slicing</SpecLink>
 */
export default function SpecLink({ spec, children }: SpecLinkProps) {
  const data = (coverageReport as CoverageReport).specs[spec];
  const percent = data ? data.coverage_percent : null;
  const { tone, hint } = maturity(percent);
  const explainer =
    'Spec link: opens the full specification for this feature. The bar shows how much of the spec is verified by tests, so you can tell whether this is speculative or well-tread.';
  const title = data
    ? `${explainer} ${data.covered_requirements} of ${data.total_requirements} success criteria covered (${percent}% — ${hint}).`
    : `${explainer} No coverage data yet (${hint}).`;

  return (
    <Link to={`/specs/${spec}/`} className="spec-link" title={title}>
      {children ?? defaultLabel(spec)}
      <span className={`spec-link-bar spec-link-bar--${tone}`} aria-hidden="true">
        <span className="spec-link-bar-fill" style={{ width: `${percent ?? 0}%` }} />
      </span>
    </Link>
  );
}
