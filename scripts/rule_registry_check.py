"""Validate or sync rule provenance digests. Does not claim semantic equivalence."""
import argparse, hashlib, json, re
from pathlib import Path

def summary_body(text, marker):
    """Read one explicitly bounded summary; normalize line endings for hashing."""
    text=text.replace('\r\n','\n').replace('\r','\n')
    start='<!-- '+marker+' -->';end='<!-- END '+marker+' -->'
    if text.count(start)!=1 or text.count(end)!=1:
        raise ValueError('SUMMARY_BLOCK_INVALID')
    begin=text.index(start)+len(start);finish=text.index(end)
    if finish<begin or '<!-- SUMMARY of ' in text[begin:finish]:
        raise ValueError('SUMMARY_BLOCK_INVALID')
    body=text[begin:finish].strip()
    if not re.search(r'\w',re.sub(r'<!--.*?-->','',body,flags=re.S)):
        raise ValueError('SUMMARY_EMPTY')
    return body

def authority_payload(path):
    """Read authority text with line endings normalized so digests survive any checkout."""
    text=path.read_bytes().decode('utf-8')
    return text.replace('\r\n','\n').replace('\r','\n').encode('utf-8')

def sync(root):
    """Recompute and write authority_sha256 and summary_sha256 for all registered rules."""
    root=Path(root).resolve()
    reg_path=root/'rules/rule-registry.yaml'
    registry=json.loads(reg_path.read_text(encoding='utf-8'))
    updated=[]
    for rule in registry.get('rules',[]):
        rid=rule['rule_id']
        auth_path=(root/rule['authority']['path']).resolve()
        if not auth_path.is_relative_to(root):
            raise ValueError('PATH_ESCAPE')
        raw=auth_path.read_bytes()
        text=raw.decode('utf-8')
        if 'id="'+rule['authority']['anchor']+'"' not in text:
            raise ValueError(f'ANCHOR_MISSING:{rid}')
        rule['authority_sha256']=hashlib.sha256(authority_payload(auth_path)).hexdigest()
        for ref in rule.get('summary_refs',[]):
            ref['rule_revision']=rule['rule_revision']
            ref['marker']='SUMMARY of '+rid+'@'+rule['rule_revision']
            s_path=(root/ref['path']).resolve()
            if not s_path.is_relative_to(root):
                raise ValueError('PATH_ESCAPE')
            body=summary_body(s_path.read_text(encoding='utf-8'),ref['marker'])
            ref['summary_sha256']=hashlib.sha256(body.encode('utf-8')).hexdigest()
        updated.append(rid)
    reg_path.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return updated

def check(root):
    root=Path(root).resolve(); errors=[]
    def fail(code,where): errors.append({'code':code,'location':where})
    def file(rel):
        p=(root/rel).resolve()
        if not p.is_relative_to(root): raise ValueError('PATH_ESCAPE')
        return p
    try:
        registry=json.loads((root/'rules/rule-registry.yaml').read_text(encoding='utf-8'))
        if registry.get('schema_version')!='1.0.0': raise ValueError('VERSION')
        rules=registry['rules']
        if not isinstance(rules,list) or not rules: raise ValueError('RULES_EMPTY')
    except (OSError,ValueError,KeyError,TypeError) as e:
        return [{'code':'REGISTRY_INVALID','location':str(e)}]
    ids=set();graph={}
    for rule in rules:
        if not isinstance(rule,dict): fail('RULE_INVALID','non-object');continue
        rid=rule.get('rule_id','<missing>')
        if not isinstance(rid,str):fail('RULE_INVALID','rule_id must be string');continue
        if rid in ids: fail('DUPLICATE_ID',rid)
        ids.add(rid)
        try:
            for key in ('rule_id','authority','authority_sha256','rule_revision','summary_refs','review_status','last_reviewed','depends_on'):
                if key not in rule: raise ValueError('MISSING_'+key)
            if rule['review_status'] not in ['reviewed','pending']: raise ValueError('REVIEW_STATUS')
            if not re.fullmatch(r'\d{4}-\d\d-\d\d',rule['last_reviewed']): raise ValueError('DATE')
            if not re.fullmatch(r'\d+\.\d+\.\d+',rule['rule_revision']): raise ValueError('REVISION')
            p=file(rule['authority']['path']);raw=p.read_bytes(); text=raw.decode()
            if 'id="'+rule['authority']['anchor']+'"' not in text: fail('ANCHOR_MISSING',rid)
            if hashlib.sha256(authority_payload(p)).hexdigest()!=rule['authority_sha256']: fail('AUTHORITY_DIGEST_MISMATCH',rid)
            refs=rule['summary_refs']
            if not isinstance(refs,list) or not refs: fail('SUMMARY_REFS_EMPTY',rid);refs=[]
            for ref in refs:
                if ref['rule_revision']!=rule['rule_revision']: fail('SUMMARY_REVISION_MISMATCH',rid)
                if ref['marker']!='SUMMARY of '+rid+'@'+rule['rule_revision']: fail('SUMMARY_MARKER_VERSION',rid)
                digest=ref.get('summary_sha256')
                if not isinstance(digest,str) or not re.fullmatch(r'[0-9a-f]{64}',digest): fail('SUMMARY_DIGEST_INVALID',rid)
                text=file(ref['path']).read_text(encoding='utf-8')
                if '<!-- '+ref['marker']+' -->' not in text: fail('SUMMARY_MISSING',rid)
                else:
                    try: body=summary_body(text,ref['marker'])
                    except ValueError as e: fail(str(e),rid)
                    else:
                        if hashlib.sha256(body.encode('utf-8')).hexdigest()!=digest: fail('SUMMARY_DIGEST_MISMATCH',rid)
            if not isinstance(rule['depends_on'],list) or not all(isinstance(x,str) for x in rule['depends_on']):raise ValueError('DEPENDENCIES_INVALID')
            graph[rid]=rule['depends_on']
        except (OSError,KeyError,TypeError,ValueError) as e: fail('RULE_INVALID',rid+':'+str(e))
    visiting=set();done=set()
    def visit(rid):
        if rid in visiting: fail('RULE_CYCLE',rid);return
        if rid in done: return
        visiting.add(rid)
        for dep in graph.get(rid,[]):
            if dep not in ids: fail('DANGLING_RULE',rid+' -> '+dep)
            else: visit(dep)
        visiting.remove(rid);done.add(rid)
    for rid in graph: visit(rid)
    for p in root.rglob('*.md'):
        for rid,rev in re.findall(r'<!-- SUMMARY of ([A-Z_]+)@([\d.]+) -->',p.read_text(encoding='utf-8')):
            if rid not in ids: fail('ORPHAN_SUMMARY',str(p))
            elif not any(r.get('rule_id')==rid and r.get('rule_revision')==rev for r in rules): fail('SUMMARY_REVISION_MISMATCH',str(p))
    return errors

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument('--sync',action='store_true',help='自动重算并写回权威文件与摘要块的 SHA-256')
    a=ap.parse_args(argv)
    synced=[]
    if a.sync:
        synced=sync(a.root)
    errors=check(a.root)
    report={'status':'FAIL' if errors else 'PASS','errors':errors,'semantic_equivalence':'UNKNOWN'}
    if a.sync:
        report['synced_rules']=synced
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return bool(errors)
if __name__=='__main__': raise SystemExit(main())
