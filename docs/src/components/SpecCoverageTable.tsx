import React, { useState } from 'react';
import Link from '@docusaurus/Link';
import coverageReport from '../../static/spec-coverage.json';

type SpecCoverageData = {
  total_requirements: number;
  covered_requirements: number;
  coverage_percent: number;
  by_type: Record<string, number>;
};

type CoverageReport = {
  generated?: string;
  specs: Record<string, SpecCoverageData>;
  summary?: {
    total_requirements: number;
    covered_requirements: number;
    coverage_percent: number;
  };
};

type Row = {
  spec: string;
  label: string;
  percent: number;
  covered: number;
  total: number;
  tests: number;
};

type SortKey = 'spec' | 'coverage' | 'criteria' | 'tests';

// Mirror SpecLink's label + maturity so the table reads the same as the inline bars.
function defaultLabel(spec: string): string {
  return spec
    .replace(/_SPEC$/, '')
    .split('_')
    .map((word) => word.charAt(0) + word.slice(1).toLowerCase())
    .join(' ');
}

function maturity(percent: number): { tone: 'success' | 'warning' | 'muted'; word: string } {
  if (percent >= 70) return { tone: 'success', word: 'Well-tested' };
  if (percent >= 30) return { tone: 'warning', word: 'Maturing' };
  return { tone: 'muted', word: 'Early' };
}

/**
 * One consolidated, sortable table of every spec's verification status — the
 * whole-project view of the same data <SpecCoverage> shows per page and
 * <SpecLink> shows inline. Reads docs/static/spec-coverage.json, regenerated on
 * every docs build, so it reflects current verification rather than aspiration.
 */
export default function SpecCoverageTable() {
  const report = coverageReport as CoverageReport;
  const [sortKey, setSortKey] = useState<SortKey>('coverage');
  const [asc, setAsc] = useState(false);

  const rows: Row[] = Object.entries(report.specs).map(([spec, d]) => ({
    spec,
    label: defaultLabel(spec),
    percent: d.coverage_percent,
    covered: d.covered_requirements,
    total: d.total_requirements,
    tests: Object.values(d.by_type || {}).reduce((sum, n) => sum + n, 0),
  }));

  const sorted = [...rows].sort((a, b) => {
    let cmp: number;
    switch (sortKey) {
      case 'spec':
        cmp = a.label.localeCompare(b.label);
        break;
      case 'criteria':
        cmp = a.total - b.total;
        break;
      case 'tests':
        cmp = a.tests - b.tests;
        break;
      default:
        cmp = a.percent - b.percent;
    }
    return asc ? cmp : -cmp;
  });

  function onSort(key: SortKey) {
    if (key === sortKey) {
      setAsc((prev) => !prev);
    } else {
      setSortKey(key);
      // Names read best A→Z; numeric columns most-useful high→low.
      setAsc(key === 'spec');
    }
  }

  function header(key: SortKey, text: string) {
    const active = key === sortKey;
    return (
      <th aria-sort={active ? (asc ? 'ascending' : 'descending') : 'none'}>
        <button type="button" className="spec-coverage-table-sort" onClick={() => onSort(key)}>
          {text}
          <span aria-hidden="true" className="spec-coverage-table-arrow">
            {active ? (asc ? '▲' : '▼') : '↕'}
          </span>
        </button>
      </th>
    );
  }

  const summary = report.summary;

  return (
    <div className="spec-coverage-table-wrap">
      {summary ? (
        <p className="spec-coverage-table-summary">
          <strong>{summary.covered_requirements}</strong> of{' '}
          <strong>{summary.total_requirements}</strong> success criteria verified across{' '}
          <strong>{rows.length}</strong> specs (<strong>{summary.coverage_percent}%</strong>).
          {report.generated ? (
            <span className="spec-coverage-muted"> Generated {report.generated.slice(0, 10)}.</span>
          ) : null}
        </p>
      ) : null}

      <table className="spec-coverage-table">
        <thead>
          <tr>
            {header('spec', 'Spec')}
            {header('coverage', 'Coverage')}
            {header('criteria', 'Criteria')}
            {header('tests', 'Tests')}
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((r) => {
            const { tone, word } = maturity(r.percent);
            return (
              <tr key={r.spec}>
                <td>
                  <Link to={`/specs/${r.spec}/`}>{r.label}</Link>
                </td>
                <td>
                  <span className={`spec-link-bar spec-link-bar--${tone}`} aria-hidden="true">
                    <span className="spec-link-bar-fill" style={{ width: `${r.percent}%` }} />
                  </span>
                  <span className="spec-coverage-table-pct">{r.percent}%</span>
                </td>
                <td className="spec-coverage-table-num">
                  {r.covered} / {r.total}
                </td>
                <td className="spec-coverage-table-num">{r.tests}</td>
                <td>
                  <span className={`spec-coverage-badge spec-coverage-badge--${tone}`}>{word}</span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
