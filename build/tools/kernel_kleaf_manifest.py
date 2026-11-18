#!/usr/bin/env python3
import glob
import os
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import quoteattr

repo_prefix = f'kernel/platform/kernel-{sys.argv[1]}/'
projects = set()
with open('.repo/project.list', encoding='utf-8') as project_list:
    projects.update(line.strip() for line in project_list if line.startswith(repo_prefix))

# Local manifests may describe kernel checkouts maintained outside repo sync.
for manifest in glob.glob('.repo/local_manifests/*.xml'):
    for project in ET.parse(manifest).getroot().iter('project'):
        path = project.get('path', project.get('name', ''))
        if path.startswith(repo_prefix) and os.path.isdir(path):
            projects.add(path)

# Also support standalone Git checkouts inside the kernel workspace.
# Do not descend into Git metadata or Bazel output directories.
for root, dirs, files in os.walk(repo_prefix):
    if '.git' in dirs or '.git' in files:
        projects.add(root)
        dirs[:] = []
        continue
    dirs[:] = [d for d in dirs if d not in ('out', '.repo')]

print('<manifest>')
for path in sorted(projects):
    print(f'  <project path={quoteattr(path[len(repo_prefix):])} />')
print('</manifest>')
