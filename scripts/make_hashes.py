import hashlib, json, sys

src = sys.argv[1]
out = sys.argv[2]

def canon(record):
    text = json.dumps(record, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'))
    return text.encode('utf-8')

hashes = {}
for line in open(src, encoding='utf-8'):
    if line.strip():
        record = json.loads(line)
        hashes[record['scenario_id']] = hashlib.sha256(canon(record)).hexdigest()

joined = ''.join(hashes[k] for k in sorted(hashes))
set_hash = hashlib.sha256(joined.encode()).hexdigest()
result = {
    'method': 'sha256 of each scenario as canonical JSON '
              '(sorted keys, compact, UTF-8)',
    'count': len(hashes),
    'set_hash': set_hash,
    'scenarios': dict(sorted(hashes.items())),
}
json.dump(result, open(out, 'w'), indent=2)
print(len(hashes), 'hashes written to', out, '; set hash', set_hash)
