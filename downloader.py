#!/data/data/com.termux/files/usr/bin/python
import os,sys,json,time,shutil,subprocess,re,threading,queue
from datetime import datetime
from pathlib import Path
try:
 from tqdm import tqdm
 F=True
except:
 F=False
try:
 from colorama import init,Fore,Style
 init(autoreset=True)
 G=True
except:
 G=False
A=os.path.join(Path.home(),'.darkx_downloader_config.json')
B="/storage/emulated/0/Download/music_videos"
def a():
 if os.path.exists(A):
  with open(A,'r') as f:
   return json.load(f)
 return {'download_folder':B,'default_quality':'bestvideo[height<=720]+bestaudio/best[height<=720]','default_format':'mp4','history_size':10}
def b(c):
 with open(A,'w') as f:
  json.dump(c,f,indent=4)
c=a()
D=c['download_folder']
if not os.path.exists(D):
 try:
  os.makedirs(D)
 except:
  if G:
   print(Fore.RED+"[!] Storage permission denied! Run: termux-setup-storage"+Style.RESET_ALL)
  else:
   print("[!] Storage permission denied! Run: termux-setup-storage")
  sys.exit(1)
E=os.path.join(D,'.download_history.json')
def d(t,g='white',h=False):
 if G:
  i={'red':Fore.RED,'green':Fore.GREEN,'yellow':Fore.YELLOW,'blue':Fore.BLUE,'magenta':Fore.MAGENTA,'cyan':Fore.CYAN,'white':Fore.WHITE}
  j=Style.BRIGHT if h else ''
  print(j+i.get(g,Fore.WHITE)+t+Style.RESET_ALL)
 else:
  print(t)
def e():
 os.system('clear')
def f():
 k=r"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║      ██████╗  █████╗ ██████╗ ██╗  ██╗  ██╗                 ║
║      ██╔══██╗██╔══██╗██╔══██╗╚██╗██╔╝  ██║                 ║
║      ██║  ██║███████║██████╔╝ ╚███╔╝   ██║                 ║
║      ██║  ██║██╔══██║██╔══██╗ ██╔██╗   ██║                 ║
║      ██████╔╝██║  ██║██║  ██║██╔╝ ██╗  ██║                 ║
║      ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═╝                 ║
║                                                              ║
║            NEXT-LEVEL DOWNLOADER - TERMUX EDITION           ║
║                         VERSION 4.0.0                        ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Developer: DarkX Dev                      Contact: 255775710774  ║
║  Features: Playlist, Search, Subtitles, History, Config,    ║
║            Auto-update, TQDM, BACKGROUND WATERMARK, QUEUE   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
 d(k,'cyan',True)
def g():
 l=True
 try:
  subprocess.run(['yt-dlp','--version'],capture_output=True,check=True)
  d("[✓] yt-dlp found",'green')
 except:
  l=False
  d("[!] yt-dlp not found",'red')
 try:
  subprocess.run(['ffmpeg','-version'],capture_output=True,check=True)
  d("[✓] ffmpeg found",'green')
 except:
  l=False
  d("[!] ffmpeg not found (required for watermark)",'yellow')
 if l:
  d("[i] Checking for yt-dlp updates...",'yellow')
  subprocess.run(['pip','install','--upgrade','yt-dlp'],capture_output=True)
 return l
def h():
 d("[i] Installing required dependencies...",'yellow')
 try:
  subprocess.run(['pkg','install','python','ffmpeg','-y'],check=True)
  subprocess.run(['pip','install','--upgrade','yt-dlp'],check=True)
  d("[✓] Dependencies installed successfully!",'green')
 except:
  d("[!] Failed to install dependencies",'red')
  sys.exit(1)
def i(m,n=100):
 try:
  o=subprocess.run(['yt-dlp','--simulate','--print','%(filesize_approx)s',m],capture_output=True,text=True)
  p=o.stdout.strip()
  if p and p!='NA':
   q=int(p)/(1024*1024)
   r=shutil.disk_usage(D)
   s=r.free/(1024*1024)
   if s<q+n:
    d(f"[!] Not enough disk space! Need {q:.0f} MB, only {s:.0f} MB free.",'red')
    return False
 except:
  pass
 return True
def j(t):
 if not os.path.exists(t):
  return
 u=[]
 if os.path.exists(E):
  with open(E,'r') as f:
   u=json.load(f)
 u.append({'file':os.path.basename(t),'path':t,'time':datetime.now().isoformat(),'size':os.path.getsize(t)})
 u=u[-50:]
 with open(E,'w') as f:
  json.dump(u,f,indent=4)
def k():
 if os.path.exists(E):
  with open(E,'r') as f:
   v=json.load(f)
  if v:
   d("\n╔══════════════════════════════════════════════════════════════╗",'cyan',True)
   d("║                     DOWNLOAD HISTORY                        ║",'cyan',True)
   d("╚══════════════════════════════════════════════════════════════╝",'cyan',True)
   for w,x in enumerate(reversed(v[-10:]),1):
    y=x['size']/(1024*1024)
    z=x['time'][:19].replace('T',' ')
    d(f"  {w}. {x['file'][:40]}... ({y:.1f} MB) - {z}",'yellow')
  else:
   d("\n[ No downloads yet ]",'yellow')
 else:
  d("\n[ No history found ]",'yellow')
def l(aa):
 try:
  ab=['yt-dlp','--default-search','ytsearch5','--flat-playlist','--dump-json',f'ytsearch5:{aa}']
  ac=subprocess.run(ab,capture_output=True,text=True,check=True)
  ad=[]
  for ae in ac.stdout.strip().split('\n'):
   if ae:
    ad.append(json.loads(ae))
  return ad
 except:
  return None
def m(af):
 if not shutil.which('ffmpeg'):
  d("[!] ffmpeg not found, skipping watermark",'yellow')
  return False
 ag=af+".temp"+os.path.splitext(af)[1]
 ah=['ffmpeg','-i',af,'-vf',"drawtext=text='DarkX Official tools':fontcolor=white:fontsize=24:x=w-tw-10:y=10:bordercolor=black:borderw=2",'-codec:a','copy','-y',ag]
 try:
  d("[i] Applying video watermark in background...",'cyan')
  subprocess.run(ah,check=True,capture_output=True)
  shutil.move(ag,af)
  d("[✓] Watermark added to video",'green')
  return True
 except subprocess.CalledProcessError:
  d("[!] Failed to apply watermark",'red')
  if os.path.exists(ag):
   os.remove(ag)
  return False
def n(ai):
 aj=os.path.dirname(ai)
 ak=os.path.basename(ai)
 al,am=os.path.splitext(ak)
 an=f"{al} [DarkX Official tools]{am}"
 ao=os.path.join(aj,an)
 ap=1
 while os.path.exists(ao):
  an=f"{al} [DarkX Official tools {ap}]{am}"
  ao=os.path.join(aj,an)
  ap+=1
 os.rename(ai,ao)
 d(f"[✓] Audio filename updated: {an}",'green')
 return ao
def o(aq,ar,as_,at=False,au='en'):
 av=os.path.join(D,'%(title)s.%(ext)s')
 aw=['yt-dlp','--no-mtime','--embed-metadata','--embed-thumbnail','-o',av,'--newline','--no-warnings','--print','after_move:filepath']
 if as_=='mp3':
  aw.extend(['-f','bestaudio','--extract-audio','--audio-format','mp3','--audio-quality','0'])
 elif as_=='mkv':
  aw.extend(['-f',ar,'--merge-output-format','mkv'])
 else:
  aw.extend(['-f',ar,'--merge-output-format','mp4'])
 if at:
  aw.extend(['--write-subs','--sub-lang',au,'--embed-subs'])
 aw.append(aq)
 d("\n╔══════════════════════════════════════════════════════════════╗",'magenta',True)
 d("║                     DOWNLOADING... (BACKGROUND)              ║",'magenta',True)
 d("╚══════════════════════════════════════════════════════════════╝",'magenta',True)
 ax=subprocess.Popen(aw,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1,universal_newlines=True)
 ay=[]
 if F:
  az=None
  for ba in ax.stdout:
   ay.append(ba.rstrip())
   if '%' in ba:
    try:
     for bb in ba.split():
      if bb.endswith('%'):
       bc=float(bb.strip('%'))
       if az is None:
        az=tqdm(total=100,desc="Progress",unit='%')
       az.n=bc
       az.refresh()
       break
    except:
     pass
   print(ba,end='')
  if az:
   az.close()
 else:
  for ba in ax.stdout:
   ay.append(ba.rstrip())
   print(ba,end='')
 ax.wait()
 bd=ax.returncode==0
 if bd:
  d("\n[✓] Download completed successfully!",'green')
  be=[]
  for bf in ay:
   bf=bf.strip()
   if bf.startswith(D) and os.path.exists(bf):
    be.append(bf)
  if not be:
   d("[!] Could not determine downloaded file(s)",'yellow')
  for bg in be:
   if not os.path.exists(bg):
    continue
   if as_=='mp3':
    bh=n(bg)
    j(bh)
   elif as_ in ['mp4','mkv']:
    if m(bg):
     j(bg)
    else:
     j(bg)
   else:
    j(bg)
 else:
  d("\n[✗] Download failed. Check URL and internet.",'red')
 return bd
def p():
 d("\n╔══════════════════════════════════════════════════════════════╗",'cyan',True)
 d("║                     QUALITY OPTIONS                           ║",'cyan',True)
 d("╚══════════════════════════════════════════════════════════════╝",'cyan',True)
 d(" 1. 4K Ultra HD (2160p)",'yellow')
 d(" 2. 1080p Full HD",'yellow')
 d(" 3. 720p HD (Default)",'yellow')
 d(" 4. 480p (Mobile)",'yellow')
 d(" 5. 360p (Small)",'yellow')
 d(" 6. Audio only (MP3)",'yellow')
 d(" 7. Custom resolution (e.g., 720)",'yellow')
 d(" 8. Best quality (no limit)",'yellow')
 bi=input("⚡ Choose (1-8): ").strip()
 bj={'1':'bestvideo[height<=2160]+bestaudio/best[height<=2160]','2':'bestvideo[height<=1080]+bestaudio/best[height<=1080]','3':'bestvideo[height<=720]+bestaudio/best[height<=720]','4':'bestvideo[height<=480]+bestaudio/best[height<=480]','5':'bestvideo[height<=360]+bestaudio/best[height<=360]','6':'bestaudio','8':'bestvideo+bestaudio/best'}
 if bi=='7':
  bk=input("Enter desired height (e.g., 720): ").strip()
  if bk.isdigit():
   return f'bestvideo[height<={bk}]+bestaudio/best[height<={bk}]'
  else:
   d("Invalid input, using 720p.",'red')
   return bj['3']
 return bj.get(bi,bj['3'])
def q():
 d("\n╔══════════════════════════════════════════════════════════════╗",'cyan',True)
 d("║                     FORMAT OPTIONS                            ║",'cyan',True)
 d("╚══════════════════════════════════════════════════════════════╝",'cyan',True)
 d(" 1. MP4 Video",'yellow')
 d(" 2. MP3 Audio",'yellow')
 d(" 3. MKV Video",'yellow')
 bl=input("⚡ Choose (1-3): ").strip()
 bm={'1':'mp4','2':'mp3','3':'mkv'}
 return bm.get(bl,'mp4')
def r():
 d("\n╔══════════════════════════════════════════════════════════════╗",'cyan',True)
 d("║                     SUBTITLES OPTIONS                         ║",'cyan',True)
 d("╚══════════════════════════════════════════════════════════════╝",'cyan',True)
 bn=input("Download subtitles? (y/n): ").strip().lower()
 if bn=='y':
  bo=input("Language code (e.g., en, sw, fr) [default=en]: ").strip() or 'en'
  return True,bo
 return False,'en'
def s(bp):
 try:
  bq=subprocess.run(['yt-dlp','--flat-playlist','--dump-json','--playlist-end','1',bp],capture_output=True,text=True)
  if bq.returncode==0 and bq.stdout:
   br=json.loads(bq.stdout.strip().split('\n')[0])
   if 'playlist_count' in br or 'playlist' in bp:
    d("\n╔══════════════════════════════════════════════════════════════╗",'magenta',True)
    d("║                     PLAYLIST DETECTED                        ║",'magenta',True)
    d("╚══════════════════════════════════════════════════════════════╝",'magenta',True)
    d(f"Title: {br.get('playlist','Unknown')}",'yellow')
    d("Options:",'cyan')
    d(" 1. Download entire playlist",'yellow')
    d(" 2. Select specific videos (by number)",'yellow')
    d(" 3. Download as audio (entire playlist)",'yellow')
    d(" 4. Cancel",'yellow')
    bs=input("⚡ Choose (1-4): ").strip()
    if bs=='2':
     bt=subprocess.run(['yt-dlp','--flat-playlist','--dump-json',bp],capture_output=True,text=True)
     bu=[]
     for bv in bt.stdout.strip().split('\n'):
      if bv:
       bu.append(json.loads(bv))
     d("\nVideos in playlist:",'cyan')
     for bw,bx in enumerate(bu[:20],1):
      d(f" {bw}. {bx.get('title','Unknown')[:60]}",'yellow')
     if len(bu)>20:
      d(f" ... and {len(bu)-20} more",'yellow')
     by=input("Enter video numbers to download (e.g., 1,3,5-10): ").strip()
     bz=[]
     ca=by.split(',')
     for cb in ca:
      if '-' in cb:
       cc,cd=map(int,cb.split('-'))
       bz.extend(range(cc-1,min(cd,len(bu))))
      elif cb.isdigit():
       bz.append(int(cb)-1)
     ce=[bu[cf]['url'] for cf in bz if 0<=cf<len(bu)]
     return ce
    elif bs=='3':
     return [bp]
    elif bs=='1':
     return [bp]
    else:
     return None
 except:
  pass
 return [bp]
def t():
 d("\n╔══════════════════════════════════════════════════════════════╗",'cyan',True)
 d("║                         MAIN MENU                             ║",'cyan',True)
 d("╚══════════════════════════════════════════════════════════════╝",'cyan',True)
 d(" 1. Download from URL(s)",'yellow')
 d(" 2. Search YouTube and download",'yellow')
 d(" 3. Batch download from file (URLs list)",'yellow')
 d(" 4. Show download history",'yellow')
 d(" 5. View queue status",'yellow')
 d(" 6. Settings (change folder, defaults)",'yellow')
 d(" 7. Exit",'yellow')
 cg=input("⚡ Choose (1-7): ").strip()
 return cg
# ---------- QUEUE SYSTEM ----------
dq=queue.Queue()
active_jobs=0
lock=threading.Lock()
def worker():
 global active_jobs
 while True:
  job=dq.get()
  with lock:
   active_jobs+=1
  try:
   d(f"\n[QUEUE] Started: {job['url'][:60]}...",'cyan')
   o(job['url'],job['quality'],job['format_'],job['subtitles'],job['sub_lang'])
  except Exception as e:
   d(f"\n[QUEUE] Error: {e}",'red')
  finally:
   with lock:
    active_jobs-=1
   dq.task_done()
threading.Thread(target=worker,daemon=True).start()
# --------------------------------
def u():
 global c,D
 while True:
  e()
  f()
  with lock:
   d(f"📁 Download folder: {D} | Active: {active_jobs} | Queued: {dq.qsize()}",'green')
  ch=t()
  if ch=='1':
   ci=input("\nEnter YouTube URL(s) (separate with space): ").strip().split()
   if not ci:
    continue
   cj=[]
   for ck in ci:
    cl=s(ck)
    if cl:
     cj.extend(cl)
    else:
     continue
   if not cj:
    continue
   cm=p()
   cn=q()
   co,cp=r()
   # Enqueue each URL
   for cs in cj:
    if not i(cs):
     cq=input(f"Not enough space for {cs[:60]}... Continue anyway? (y/n): ").strip().lower()
     if cq!='y':
      continue
    dq.put({'url':cs,'quality':cm,'format_':cn,'subtitles':co,'sub_lang':cp})
    d(f"[QUEUE] Added: {cs[:60]}...",'yellow')
   input("\nPress Enter to continue...")
  elif ch=='2':
   ct=input("Enter search term: ").strip()
   if not ct:
    continue
   cu=l(ct)
   if not cu:
    d("No results found or error.",'red')
    input("Press Enter...")
    continue
   d("\n╔══════════════════════════════════════════════════════════════╗",'cyan',True)
   d("║                     SEARCH RESULTS                            ║",'cyan',True)
   d("╚══════════════════════════════════════════════════════════════╝",'cyan',True)
   for cv,cw in enumerate(cu,1):
    cx=cw.get('title','Unknown')
    cy=cw.get('duration_string','N/A')
    cz=cw.get('uploader','Unknown')
    d(f" {cv}. {cx[:70]}",'yellow')
    d(f"    👤 {cz}  ⏱️ {cy}",'white')
   da=input("\nEnter video numbers to download (e.g., 1,2,3): ").strip()
   db=[]
   for dc in da.split(','):
    if dc.isdigit():
     dd=int(dc)-1
     if 0<=dd<len(cu):
      db.append(dd)
   if not db:
    d("No valid selection.",'red')
    continue
   de=[cu[df]['webpage_url'] for df in db]
   dg=p()
   dh=q()
   di,dj=r()
   for dk in de:
    if not i(dk):
     cq=input(f"Not enough space for {dk[:60]}... Continue anyway? (y/n): ").strip().lower()
     if cq!='y':
      continue
    dq.put({'url':dk,'quality':dg,'format_':dh,'subtitles':di,'sub_lang':dj})
    d(f"[QUEUE] Added: {dk[:60]}...",'yellow')
   input("\nPress Enter to continue...")
  elif ch=='3':
   dl=input("Enter path to text file with URLs (one per line): ").strip()
   if not os.path.exists(dl):
    d("File not found.",'red')
    continue
   with open(dl,'r') as f:
    dm=[dn.strip() for dn in f if dn.strip()]
   if not dm:
    d("No URLs in file.",'red')
    continue
   do=p()
   dp=q()
   dq_,dr=r()
   for ds in dm:
    if not i(ds):
     cq=input(f"Not enough space for {ds[:60]}... Continue anyway? (y/n): ").strip().lower()
     if cq!='y':
      continue
    dq.put({'url':ds,'quality':do,'format_':dp,'subtitles':dq_,'sub_lang':dr})
    d(f"[QUEUE] Added: {ds[:60]}...",'yellow')
   input("\nPress Enter to continue...")
  elif ch=='4':
   k()
   input("\nPress Enter to continue...")
  elif ch=='5':
   with lock:
    d(f"\nActive downloads: {active_jobs}")
    d(f"Queued downloads: {dq.qsize()}")
   input("\nPress Enter to continue...")
  elif ch=='6':
   while True:
    e()
    d("\n╔══════════════════════════════════════════════════════════════╗",'cyan',True)
    d("║                         SETTINGS                              ║",'cyan',True)
    d("╚══════════════════════════════════════════════════════════════╝",'cyan',True)
    d(f" 1. Download folder: {c['download_folder']}",'yellow')
    d(f" 2. Default quality: {c['default_quality'][:50]}...",'yellow')
    d(f" 3. Default format: {c['default_format']}",'yellow')
    d(f" 4. History size: {c['history_size']}",'yellow')
    d(" 5. Back to main menu",'yellow')
    dt=input("⚡ Choose option (1-5): ").strip()
    if dt=='1':
     du=input("Enter new download folder path: ").strip()
     if du:
      if not os.path.exists(du):
       try:
        os.makedirs(du)
       except:
        d("Cannot create folder. Check permissions.",'red')
        continue
      c['download_folder']=du
      D=du
      b(c)
      d("Folder updated.",'green')
    elif dt=='2':
     d("Select default quality:",'cyan')
     dv=p()
     c['default_quality']=dv
     b(c)
    elif dt=='3':
     dw=q()
     c['default_format']=dw
     b(c)
    elif dt=='4':
     dx=input("Enter max history entries (e.g., 20): ").strip()
     if dx.isdigit():
      c['history_size']=int(dx)
      b(c)
    elif dt=='5':
     break
    time.sleep(1)
  elif ch=='7':
   if dq.qsize()>0 or active_jobs>0:
    d(f"\nPending downloads: {active_jobs} active, {dq.qsize()} queued.",'yellow')
    dy=input("Really exit? (y/n): ").strip().lower()
    if dy!='y':
     continue
   d("\nThank you for using DarkX Next-Level Downloader!",'magenta',True)
   d("Contact: 255775710774",'cyan')
   break
  else:
   d("Invalid choice.",'red')
   time.sleep(1)
if __name__=="__main__":
 try:
  if not g():
   d("[!] Required dependencies missing. Installing...",'yellow')
   h()
  u()
 except KeyboardInterrupt:
  if G:
   print(Fore.YELLOW+"\n\n⚠️  Download cancelled by user"+Style.RESET_ALL)
  else:
   print("\n\n⚠️  Download cancelled by user")
  sys.exit(0)
 except Exception as dy:
  if G:
   print(Fore.RED+f"\n[!] Unexpected error: {dy}"+Style.RESET_ALL)
  else:
   print(f"\n[!] Unexpected error: {dy}")
  sys.exit(1)
