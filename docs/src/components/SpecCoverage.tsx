import React from 'react';
import coverageReport from '../../static/spec-coverage.json';

type TestCoverage = {
  name: string | null;
  type: string;
  file: string;
};

type RequirementCoverage = {
  text: string;
  covered: boolean;
  backend_only: boolean;
  tests: TestCoverage[];
};

type SpecCoverageData = {
  total_requirements: number;
  covered_requirements: number;
  coverage_percent: number;
  by_type: Record<string, number>;
  requirements: RequirementCoverage[];
};

type CoverageReport = {
  specs: Record<string, SpecCoverageData>;
};

type SpecCoverageProps = {
  spec: string;
  requirement?: string;
  video?: string;
  demoNote?: string;
};

function Badge({ children, tone = 'default' }: { children: React.ReactNode; tone?: 'default' | 'success' | 'warning' }) {
  return <span className={`spec-coverage-badge spec-coverage-badge--${tone}`}>{children}</span>;
}

function RequirementTests({ tests }: { tests: TestCoverage[] }) {
  if (!tests.length) {
    return <p className="spec-coverage-muted">No linked tests found yet.</p>;
  }

  return (
    <ul className="spec-coverage-tests">
      {tests.map((test) => (
        <li key={`${test.file}:${test.name ?? 'file'}`}>
          <code>{test.file}</code>
          {test.name ? <span className="spec-coverage-muted"> ({test.name})</span> : null}
          <Badge>{test.type}</Badge>
        </li>
      ))}
    </ul>
  );
}

function RequirementCard({
  requirement,
  video,
  demoNote,
}: {
  requirement: RequirementCoverage;
  video?: string;
  demoNote?: string;
}) {
  return (
    <div className="spec-success-criterion">
      <div className="spec-coverage-heading">
        <h4>{requirement.text}</h4>
        <div>
          <Badge tone={requirement.covered ? 'success' : 'warning'}>
            {requirement.covered ? 'Covered' : 'Uncovered'}
          </Badge>
          {requirement.backend_only ? <Badge tone="warning">Backend only</Badge> : null}
        </div>
      </div>

      <RequirementTests tests={requirement.tests} />

      {video ? (
        <div className="spec-coverage-video">
          <p>
            <strong>UI walkthrough</strong>
          </p>
          <video controls muted playsInline preload="metadata" width="100%">
            <source src={video} type="video/webm" />
            Your browser does not support embedded WebM video.
          </video>
          <p>
            <a href={video}>Open video</a>
          </p>
        </div>
      ) : demoNote ? (
        <p className="spec-coverage-muted">
          <strong>UI walkthrough:</strong> {demoNote}
        </p>
      ) : null}
    </div>
  );
}

export default function SpecCoverage({ spec, requirement, video, demoNote }: SpecCoverageProps) {
  const report = coverageReport as CoverageReport;
  const specCoverage = report.specs[spec];

  if (!specCoverage) {
    return <div className="spec-success-criterion">No coverage data found for <code>{spec}</code>.</div>;
  }

  if (requirement) {
    const requirementCoverage = specCoverage.requirements.find((candidate) => candidate.text === requirement);
    if (!requirementCoverage) {
      return (
        <div className="spec-success-criterion">
          No coverage data found for requirement: <code>{requirement}</code>
        </div>
      );
    }
    return <RequirementCard requirement={requirementCoverage} video={video} demoNote={demoNote} />;
  }

  return (
    <div className="spec-coverage-summary">
      <h3>Spec Coverage</h3>
      <p>
        <strong>{specCoverage.covered_requirements}</strong> of{' '}
        <strong>{specCoverage.total_requirements}</strong> success criteria covered (
        {specCoverage.coverage_percent}%).
      </p>
      <div className="spec-coverage-pyramid">
        {Object.entries(specCoverage.by_type).map(([type, count]) => (
          <Badge key={type}>{type}: {count}</Badge>
        ))}
      </div>
    </div>
  );
}
