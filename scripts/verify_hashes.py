import hashlib, json, sys

scenarios_file, hashes_file = sys.argv[1], sys.argv[2]
published = json.load(open(hashes_file))['scenarios']

def canon(record):
    text = json.dumps(record, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'))
    return text.encode('utf-8')

bad = 0
seen = set()
for line in open(scenarios_file, encoding='utf-8'):
    if line.strip():
        record = json.loads(line)
        sid = record['scenario_id']
        seen.add(sid)
        digest = hashlib.sha256(canon(record)).hexdigest()
        if digest != published.get(sid):
            print('MISMATCH', sid)
            bad += 1
missing = set(published) - seen
print('missing:', sorted(missing) if missing else 'none', '| mismatches:', bad)
