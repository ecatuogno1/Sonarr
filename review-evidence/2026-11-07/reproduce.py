#!/usr/bin/env python3
"""Run the same Sonarr fixture against upstream behavior and the reviewed fix.
Requires a clean checkout containing the three published review commits and .NET 10.0.403.
"""
import argparse,datetime,hashlib,json,subprocess,sys,xml.etree.ElementTree as ET
from pathlib import Path
BASE='c018578e4b79ee048575c02d7a8aa2b929e4b837'
CASES={
1:dict(head='94a54f372a9261d4aa5b68b883fb93f7ca1b282e',filter='MediaFiles.EpisodeImport.Manual',files=['src/NzbDrone.Core/MediaFiles/EpisodeImport/Manual/ManualImportService.cs'],failed=1,total=3),
2:dict(head='c1b69fa302c9a2f018046b33bd4bb28946c5524e',filter='GetDownloadClientsFixture',files=['src/NzbDrone.Core/Download/DownloadClientProvider.cs'],failed=1,total=17),
3:dict(head='4c2d872db1018cedb6431217ae3e3bcf53612db4',filter='CompletedDownloadServiceTests',files=['src/NzbDrone.Core.Test/Download/CompletedDownloadServiceTests/ImportFixture.cs','src/NzbDrone.Core.Test/Download/CompletedDownloadServiceTests/ProcessFixture.cs'],failed=8,total=28)}
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--repo',required=True);parser.add_argument('--dotnet',default='dotnet');parser.add_argument('--output',required=True);parser.add_argument('--pr',type=int,choices=[1,2,3]);args=parser.parse_args();repo=Path(args.repo).resolve();out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
def git(*argv):return subprocess.check_output(['git',*argv],cwd=repo,text=True).strip()
if git('status','--porcelain','--untracked-files=no'):sys.exit('Refusing to modify a checkout with tracked changes.')
original=subprocess.run(['git','symbolic-ref','--short','HEAD'],cwd=repo,capture_output=True,text=True);restore=original.stdout.strip() if original.returncode==0 else git('rev-parse','HEAD');records=[]
def run(number,phase,case):
 dest=out/('pr-'+str(number))/phase;dest.mkdir(parents=True,exist_ok=True)
 cmd=[args.dotnet,'test','src/NzbDrone.Core.Test/Sonarr.Core.Test.csproj','-c','Debug','-p:Platform=Posix','-p:SolutionDir='+str(repo)+'/src/','--filter','FullyQualifiedName~'+case['filter'],'--logger','console;verbosity=normal','--logger','trx;LogFileName=tests.trx','--results-directory',str(dest),'--verbosity','quiet']
 print('RUN PR',number,phase,flush=True)
 with (dest/'console.log').open('w') as f:r=subprocess.run(cmd,cwd=repo,stdout=f,stderr=subprocess.STDOUT)
 tree=ET.parse(dest/'tests.trx').getroot();ns={'t':tree.tag.split('}')[0][1:]};c=tree.find('.//t:Counters',ns).attrib
 failures=[]
 for x in tree.findall('.//t:UnitTestResult',ns):
  if x.get('outcome')=='Failed':failures.append(dict(test=x.get('testName'),message=x.findtext('./t:Output/t:ErrorInfo/t:Message',namespaces=ns),stack=x.findtext('./t:Output/t:ErrorInfo/t:StackTrace',namespaces=ns)))
 record=dict(pr=number,phase=phase,head=case['head'],baseline=BASE,restoredFilesFromBaseline=case['files'] if phase=='before' else [],command=cmd,exitCode=r.returncode,counts=c,failures=failures,startedUTC=started)
 (dest/'result.json').write_text(json.dumps(record,indent=2));records.append(record)
 expected=case['failed'] if phase=='before' else 0
 assert int(c['total'])==case['total'] and int(c['failed'])==expected and int(c['passed'])==case['total']-expected,(number,phase,c)
 assert (r.returncode!=0)==(expected>0),(number,phase,r.returncode)
 print('RESULT PR',number,phase,c['passed'],'passed',c['failed'],'failed',flush=True)
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
try:
 for number,case in CASES.items():
  if args.pr and args.pr!=number:continue
  subprocess.run(['git','switch','--detach',case['head']],cwd=repo,check=True,stdout=subprocess.DEVNULL)
  saved={p:(repo/p).read_bytes() for p in case['files']}
  try:
   for p in case['files']:(repo/p).write_bytes(subprocess.check_output(['git','show',BASE+':'+p],cwd=repo))
   run(number,'before',case)
  finally:
   for p,blob in saved.items():(repo/p).write_bytes(blob)
  assert not git('status','--porcelain','--untracked-files=no')
  run(number,'after',case)
finally:
 subprocess.run(['git','switch',restore],cwd=repo,check=True,stdout=subprocess.DEVNULL)
 (out/'results.json').write_text(json.dumps(records,indent=2))
print('Finished. Original source checkout restored.',flush=True)
