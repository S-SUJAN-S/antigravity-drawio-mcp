import yaml, sys

# Check 2: YAML is valid
with open('.github/workflows/publish.yml') as f:
    data = yaml.safe_load(f)
print('Check 2: YAML parse OK - file is syntactically valid')

# Check 3: Verify job-level env has PYPI_API_TOKEN
job = data['jobs']['test']
job_env = job.get('env', {})
assert 'PYPI_API_TOKEN' in job_env, 'PYPI_API_TOKEN not found in job-level env'
print('Check 3a: job-level env has PYPI_API_TOKEN =', job_env['PYPI_API_TOKEN'])

# Find the publish step and verify its env does NOT shadow PYPI_API_TOKEN
for step in job['steps']:
    if 'Publish' in step.get('name', ''):
        step_env = step.get('env', {})
        assert 'PYPI_API_TOKEN' not in step_env, 'PYPI_API_TOKEN incorrectly duplicated in step env!'
        step_keys = list(step_env.keys())
        print('Check 3b: Publish step env keys =', step_keys, '-- PYPI_API_TOKEN NOT in step env OK')
        break

# Check 4: No old action references remain
with open('.github/workflows/publish.yml') as f:
    raw = f.read()
assert 'actions/checkout@v4' not in raw, 'Found old actions/checkout@v4!'
assert 'actions/setup-python@v5' not in raw, 'Found old actions/setup-python@v5!'
assert 'actions/checkout@v7' in raw, 'actions/checkout@v7 not found!'
assert 'actions/setup-python@v7' in raw, 'actions/setup-python@v7 not found!'
print('Check 4: No references to checkout@v4 or setup-python@v5 -- using v7 OK')

print()
print('ALL CHECKS PASSED')
