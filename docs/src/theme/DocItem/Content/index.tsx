import React from 'react';
import Content from '@theme-original/DocItem/Content';
import { useDoc } from '@docusaurus/plugin-content-docs/client';
import SpecCoverage from '@site/src/components/SpecCoverage';

/**
 * Theme wrapper that injects a SpecCoverage summary at the top of every spec
 * page (the target of inline <SpecLink>s). Spec markdown sources are the
 * canonical spec-driven-workflow files and must stay free of MDX imports, so
 * the block is added at render time instead of in the files.
 */
export default function ContentWrapper(props: React.ComponentProps<typeof Content>) {
  const { metadata } = useDoc();
  const isSpecPage = metadata.id.endsWith('_SPEC') && metadata.permalink.includes('/specs/');

  return (
    <>
      {isSpecPage ? <SpecCoverage spec={metadata.id} /> : null}
      <Content {...props} />
    </>
  );
}
