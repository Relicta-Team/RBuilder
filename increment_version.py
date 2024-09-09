import sys
import re

vt = sys.argv[1] #major,minor,patch

#text to index
chind = {
	'major':0,
	'minor':1,
	'patch':2
}[vt]

with open('APP_VERSION.py', 'r') as f:
	content = f.read()
	version = re.search(r'(\d+)\.(\d+)\.(\d+)', content).group()
	verOld = version
	version = list(map(int, version.split('.')))

	version[chind] += 1

	#semver logic
	if vt == 'major':
		version[1] = 0
		version[2] = 0
	elif vt == 'minor':
		version[2] = 0

	version = [str(i) for i in version]
	version = '.'.join(version)
	with open('APP_VERSION.py', 'w') as fhd:
		fhd.write(content.replace(verOld, version, 1))

print(f'New version: {version}')