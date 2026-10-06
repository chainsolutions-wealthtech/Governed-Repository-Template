#!/usr/bin/env python3
from __future__ import annotations
import json, tempfile, importlib.util, sqlite3
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
fts=load(ROOT/'scripts'/'gscc'/'first_touch_store.py','fts')

capture={
 'schema':'first-touch-exhaustive-capture/v1',
 'capture_id':'FTC-entry-contract-test',
 'observed_at':'2026-10-06T05:00:00+00:00',
 'repository':'chainsolutions-wealthtech/Governed-Repository-Template',
 'actor':'Wealthtechinnovations',
 'provider':'chatgpt',
 'safe_ingress':{
   'schema':'gscc-first-touch-safe-ingress/v1',
   'status':'VALID',
   'ingress_type':'FIRST_TOUCH',
   'comment_id':6010194437,
   'connection_ref':'test-anchor-001',
   'client_instance_id':'test-client-001',
   'conversation_ref':None,
   'provider_conversation_ref':None,
   'conversation_ref_status':'UNAVAILABLE',
   'provider_conversation_ref_status':'UNAVAILABLE',
   'source':'GITHUB_ISSUE_COMMENT_STRUCTURED_PREFIX',
   'source_method':'ISSUE_COMMENT',
   'observed_at':'2026-10-06T05:00:00+00:00',
   'freeform_body_persisted':False
 },
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

        strength, discovered=ec.discover_identity(cap)
        assert strength=='STRONG'
        assert discovered=='provider_connection_ref:test-anchor-001'
        anchor='test-anchor-001'
        first=ec.evaluate(comp,db,identity_strength='STRONG',identity_anchor='provider_connection_ref:'+anchor,first_touch_seen=False)
        assert first['status']=='ENTRY_READY_FOR_Q1'
        assert first['classification']=='FIRST_TOUCH'

        conn=sqlite3.connect(db); conn.execute('PRAGMA foreign_keys=ON')
        try:
            identity=fts.register_first_touch(conn,anchor='provider_connection_ref:'+anchor,identity_strength='STRONG',capture_id=capture['capture_id'])
            conn.commit()
            assert identity['classification']=='FIRST_TOUCH'
            snap_count=conn.execute('SELECT COUNT(*) FROM gscc_first_touch_snapshots').fetchone()[0]
            assert snap_count==1
            assert conn.execute('SELECT COUNT(*) FROM gse_session_twins').fetchone()[0]==0
        finally:
            conn.close()

        conn=sqlite3.connect(db); conn.execute('PRAGMA foreign_keys=ON')
        try:
            assert fts.find_identity(conn,'provider_connection_ref:'+anchor) is not None
            identity2=fts.register_first_touch(conn,anchor='provider_connection_ref:'+anchor,identity_strength='STRONG',capture_id=capture['capture_id'])
            conn.commit()
            assert identity2['classification']=='CONTINUATION'
            assert conn.execute('SELECT COUNT(*) FROM gscc_first_touch_snapshots').fetchone()[0]==1
            assert conn.execute('SELECT COUNT(*) FROM gse_session_twins').fetchone()[0]==0
        finally:
            conn.close()

        weak=ec.evaluate(comp,db,identity_strength='WEAK',identity_anchor='actor+repo',first_touch_seen=False)
        assert weak['status']=='ENTRY_BLOCKED'
        assert weak['create_first_touch_snapshot'] is False
        print('FIRST_TOUCH_ENTRY_CONTRACT_TEST_PASS')

if __name__=='__main__':
    main()
