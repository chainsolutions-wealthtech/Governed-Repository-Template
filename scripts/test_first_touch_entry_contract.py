#!/usr/bin/env python3
from __future__ import annotations
import json, tempfile, importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod

fb=load(ROOT/'scripts'/'first_touch_field_block_gate.py','fb')
cp=load(ROOT/'scripts'/'first_touch_connection_completeness.py','cp')
ec=load(ROOT/'scripts'/'first_touch_entry_contract.py','ec')

capture={
 'schema':'first-touch-exhaustive-capture/v1',
 'capture_id':'FTC-entry-contract-test',
 'observed_at':'2026-10-06T05:00:00+00:00',
 'repository':'chainsolutions-wealthtech/Governed-Repository-Template',
 'actor':'Wealthtechinnovations',
 'provider':'chatgpt',
 'connection_ref':'test-anchor-001',
 'client_instance_id':'test-anchor-001',
 'github_event':{
   'sender':{'login':'Wealthtechinnovations','id':94637590},
   'repository':{'id':1386478935,'full_name':'chainsolutions-wealthtech/Governed-Repository-Template','default_branch':'main'},
   'issue':{'number':161}
 },
 'environment':{
   'GITHUB_EVENT_NAME':'issue_comment',
   'GITHUB_REPOSITORY':'chainsolutions-wealthtech/Governed-Repository-Template',
   'GITHUB_ACTOR':'Wealthtechinnovations',
   'GITHUB_RUN_ID':'123',
   'GITHUB_SHA':'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
   'GITHUB_REF_NAME':'main'
 },
 'api_attempts':[{'name':'actor_repository_permission','http_status':200,'response':{'permission':'admin'}}],
 'mutation_authority_granted':False,
 'interpretation_applied':False
}

def main():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)
        cap=root/'capture.json'
        db=root/'capture.sqlite'
        comp=root/'complete.json'
        cap.write_text(json.dumps(capture),encoding='utf-8')
        fb.build_capture_database(cap,db,source_ref='unit-test')
        cp.build_packet(None,comp,capture_path=cap)
        registry=root/'registry.json'
        registry.write_text(json.dumps({'schema':'first-touch-conversation-registry/v1','conversations':[]}),encoding='utf-8')
        anchor='test-anchor-001'
        first=ec.evaluate(comp,db,identity_strength='EXACT',identity_anchor=anchor,first_touch_seen=(ec.registry_match(registry,anchor) is not None))
        assert first['status']=='ENTRY_READY_FOR_Q1'
        assert first['classification']=='FIRST_TOUCH'
        assert first['create_first_touch_snapshot'] is True
        first['identity_anchor']=anchor
        assert ec.persist_registry(registry,first,cap) is True
        saved=ec.load_registry(registry)
        assert len(saved['conversations'])==1
        initial_capture=saved['conversations'][0]['first_capture_id']
        cont=ec.evaluate(comp,db,identity_strength='EXACT',identity_anchor=anchor,first_touch_seen=(ec.registry_match(registry,anchor) is not None))
        assert cont['classification']=='CONTINUATION'
        assert cont['create_first_touch_snapshot'] is False
        cont['identity_anchor']=anchor
        assert ec.persist_registry(registry,cont,cap) is True
        saved2=ec.load_registry(registry)
        assert len(saved2['conversations'])==1
        assert saved2['conversations'][0]['first_capture_id']==initial_capture
        weak=ec.evaluate(comp,db,identity_strength='WEAK',identity_anchor='actor+repo',first_touch_seen=False)
        assert weak['status']=='ENTRY_BLOCKED'
        assert weak['create_first_touch_snapshot'] is False
        print('FIRST_TOUCH_ENTRY_CONTRACT_TEST_PASS')

if __name__=='__main__': main()
