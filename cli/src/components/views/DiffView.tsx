import React, { useState } from 'react';
import { Box, Text, useInput } from 'ink';
import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import { DiffPatch } from '../../api/apiTypes.js';

interface DiffViewProps {
  patches?: DiffPatch[];
  activeFileFilter?: string;
  runCount?: number;
  maxDiffLines?: number;
  repoPath?: string;
}

function resolveTargetDir(targetRepo?: string): string {
  try {
    if (targetRepo && path.isAbsolute(targetRepo) && fs.existsSync(targetRepo)) {
      return targetRepo;
    }
    const localTarget = path.resolve(process.cwd(), targetRepo || '.');
    if (fs.existsSync(localTarget) && fs.statSync(localTarget).isDirectory()) {
      return localTarget;
    }
    const parentClonedDir = path.resolve(process.cwd(), '..', 'cloned_repos');
    if (fs.existsSync(parentClonedDir)) {
      const subdirs = fs.readdirSync(parentClonedDir, { withFileTypes: true });
      const firstDir = subdirs.find((s) => s.isDirectory());
      if (firstDir) {
        return path.join(parentClonedDir, firstDir.name);
      }
    }
    return process.cwd();
  } catch {
    return process.cwd();
  }
}

function parseGitDiffString(rawDiff: string): DiffPatch[] {
  const patches: DiffPatch[] = [];
  const files = rawDiff.split(/^diff --git /m).filter(Boolean);

  for (const fileBlock of files) {
    const lines = fileBlock.split('\n');
    const headerMatch = lines[0].match(/a\/(.+?)\s+b\/(.+)/);
    const filePath = headerMatch ? headerMatch[2] : 'modified_file.py';

    let additions = 0;
    let deletions = 0;
    const diffHunks: string[] = [];
    let lineNo = 1;

    for (let i = 1; i < lines.length; i++) {
      const line = lines[i];
      if (line.startsWith('---') || line.startsWith('+++') || line.startsWith('index ')) {
        continue;
      }
      if (line.startsWith('@@')) {
        diffHunks.push(` ${line}`);
        continue;
      }
      if (line.startsWith('+')) {
        additions++;
        diffHunks.push(`  ${lineNo} + ${line.slice(1)}`);
        lineNo++;
      } else if (line.startsWith('-')) {
        deletions++;
        diffHunks.push(`  ${lineNo} - ${line.slice(1)}`);
      } else if (line.startsWith(' ')) {
        diffHunks.push(`  ${lineNo}   ${line.slice(1)}`);
        lineNo++;
      }
    }

    if (diffHunks.length > 0) {
      patches.push({
        filePath,
        additions,
        deletions,
        diffHunks
      });
    }
  }

  return patches;
}

function getLiveWorkspacePatches(targetDir: string): DiffPatch[] {
  // 1. Try real git diff
  try {
    const rawDiff = execSync('git diff', { cwd: targetDir, stdio: 'pipe' }).toString();
    if (rawDiff.trim()) {
      return parseGitDiffString(rawDiff);
    }
    const stagedDiff = execSync('git diff --staged', { cwd: targetDir, stdio: 'pipe' }).toString();
    if (stagedDiff.trim()) {
      return parseGitDiffString(stagedDiff);
    }
    const headDiff = execSync('git diff HEAD~1', { cwd: targetDir, stdio: 'pipe' }).toString();
    if (headDiff.trim()) {
      return parseGitDiffString(headDiff);
    }
  } catch {
    // Fall back to reading disk files
  }

  // 2. Fall back to reading files from workspace disk
  try {
    const patches: DiffPatch[] = [];
    const entries = fs.readdirSync(targetDir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.isFile() && (entry.name.endsWith('.py') || entry.name.endsWith('.md') || entry.name.endsWith('.json'))) {
        const fullPath = path.join(targetDir, entry.name);
        const content = fs.readFileSync(fullPath, 'utf-8');
        const lines = content.split('\n').slice(0, 30);
        const hunks = lines.map((l, i) => `  ${i + 1}   ${l}`);
        patches.push({
          filePath: entry.name,
          additions: lines.length,
          deletions: 0,
          diffHunks: hunks
        });
      }
    }
    return patches;
  } catch {
    return [];
  }
}

export const DiffView: React.FC<DiffViewProps> = ({
  patches,
  activeFileFilter,
  runCount = 1,
  maxDiffLines = 10,
  repoPath
}) => {
  const targetDir = resolveTargetDir(repoPath);
  const livePatches = getLiveWorkspacePatches(targetDir);

  const displayPatches: DiffPatch[] =
    patches && patches.length > 0
      ? patches
      : livePatches.length > 0
        ? livePatches
        : [
            {
              filePath: 'No modified files detected',
              additions: 0,
              deletions: 0,
              diffHunks: ['  1   Clean working tree. Workspace matched HEAD cleanly.']
            }
          ];

  const filteredPatches = activeFileFilter
    ? displayPatches.filter((p) => p.filePath.toLowerCase().includes(activeFileFilter.toLowerCase()))
    : displayPatches;

  const [activeFileIndex, setActiveFileIndex] = useState(0);
  const safeIndex = Math.min(activeFileIndex, Math.max(0, filteredPatches.length - 1));
  const currentPatch = filteredPatches[safeIndex] || displayPatches[0];

  useInput(
    (input, key) => {
      if (key.rightArrow) {
        setActiveFileIndex((prev) => (prev + 1) % filteredPatches.length);
      } else if (key.leftArrow) {
        setActiveFileIndex((prev) => (prev - 1 + filteredPatches.length) % filteredPatches.length);
      }
    },
    { isActive: true }
  );

  const folderName = path.basename(targetDir);
  const visibleHunks = currentPatch.diffHunks.slice(0, maxDiffLines);

  return (
    <Box flexDirection="column" paddingX={1} paddingY={0} flexGrow={1} overflow="hidden">
      {/* Run Badge & Active Directory */}
      <Box justifyContent="space-between" marginBottom={1} flexShrink={0}>
        <Text color="cyan" bold wrap="truncate">
          LIVE WORKSPACE DIFF [{folderName}]
        </Text>
        <Text color="gray">
          File {safeIndex + 1} of {filteredPatches.length} (left/right to switch)
        </Text>
      </Box>

      {/* File Selector Tabs */}
      <Box gap={1} marginBottom={1} flexShrink={0} overflow="hidden">
        {filteredPatches.map((p, idx) => {
          const isSelected = idx === safeIndex;
          return (
            <Box key={p.filePath + idx} paddingX={1}>
              <Text
                color={isSelected ? 'yellow' : 'gray'}
                bold={isSelected}
                underline={isSelected}
                wrap="truncate"
              >
                [{p.filePath} +{p.additions}/-{p.deletions}]
              </Text>
            </Box>
          );
        })}
      </Box>

      {/* Diff Box */}
      <Box
        flexDirection="column"
        borderStyle="single"
        borderColor="yellow"
        paddingX={1}
        flexGrow={1}
        overflow="hidden"
      >
        <Box justifyContent="space-between" marginBottom={1} flexShrink={0}>
          <Text color="yellow" bold wrap="truncate">
            {currentPatch.filePath}
          </Text>
          <Text color="gray">
            +{currentPatch.additions} / -{currentPatch.deletions}
          </Text>
        </Box>

        <Box flexDirection="column" flexGrow={1} overflow="hidden">
          {visibleHunks.map((hunk, idx) => {
            let lineCol = 'gray';
            if (hunk.includes(' + ')) lineCol = 'green';
            else if (hunk.includes(' - ')) lineCol = 'red';
            else if (hunk.startsWith(' @@')) lineCol = 'cyan';

            return (
              <Text key={idx} color={lineCol} wrap="truncate">
                {hunk}
              </Text>
            );
          })}
        </Box>
      </Box>

      {/* Footer Navigation */}
      <Box marginTop={0} gap={3} flexShrink={0}>
        <Text color="gray">left/right: switch files</Text>
        <Text color="magenta">/graph: task graph</Text>
        <Text color="yellow">/benchmark: swe-bench</Text>
      </Box>
    </Box>
  );
};
