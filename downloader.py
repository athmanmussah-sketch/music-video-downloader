#!/data/data/com.termux/files/usr/bin/python
"""
Next-Level Video Downloader for Termux
Developer: DarkX Dev (255775710774)
Version: 4.0.0
Features: Concurrent downloads, background watermark, job queue
"""

import os
import sys
import json
import time
import shutil
import subprocess
import threading
from datetime import datetime
from pathlib import Path

# Optional UI libraries
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False

# ========== CONFIGURATION ==========
CONFIG_FILE = os.path.join(Path.home(), '.darkx_downloader_config.json')
DEFAULT_DOWNLOAD_FOLDER = "/storage/emulated/0/Download/music_videos"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        'download_folder': DEFAULT_DOWNLOAD_FOLDER,
        'default_quality': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        'default_format': 'mp4',
        'history_size': 10
    }

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

config = load_config()
DOWNLOAD_FOLDER = config['download_folder']

# Ensure download folder exists
if not os.path.exists(DOWNLOAD_FOLDER):
    try:
        os.makedirs(DOWNLOAD_FOLDER)
    except Exception as e:
        print_colored("[!] Storage permission denied! Run: termux-setup-storage", 'red')
        sys.exit(1)

HISTORY_FILE = os.path.join(DOWNLOAD_FOLDER, '.download_history.json')

# Global job list and lock
jobs = []
jobs_lock = threading.Lock()

# ========== UTILITY FUNCTIONS ==========
def print_colored(text, color='white', bold=False):
    if HAS_COLORAMA:
        colors = {
            'red': Fore.RED,
            'green': Fore.GREEN,
            'yellow': Fore.YELLOW,
            'blue': Fore.BLUE,
            'magenta': Fore.MAGENTA,
            'cyan': Fore.CYAN,
            'white': Fore.WHITE
        }
        style = Style.BRIGHT if bold else ''
        print(style + colors.get(color, Fore.WHITE) + text + Style.RESET_ALL)
    else:
        print(text)

def clear_screen():
    os.system('clear')

def print_banner():
    banner = r"""
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
║  Features: Concurrent downloads, background watermark, jobs  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print_colored(banner, 'cyan', bold=True)

def check_dependencies():
    deps_ok = True
    try:
        subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
        print_colored("[✓] yt-dlp found", 'green')
    except:
        deps_ok = False
        print_colored("[!] yt-dlp not found", 'red')
    
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print_colored("[✓] ffmpeg found", 'green')
    except:
        deps_ok = False
        print_colored("[!] ffmpeg not found (required for watermark)", 'yellow')
    
    if deps_ok:
        print_colored("[i] Checking for yt-dlp updates...", 'yellow')
        subprocess.run(['pip', 'install', '--upgrade', 'yt-dlp'], capture_output=True)
    
    return deps_ok

def install_dependencies():
    print_colored("[i] Installing required dependencies...", 'yellow')
    try:
        subprocess.run(['pkg', 'install', 'python', 'ffmpeg', '-y'], check=True)
        subprocess.run(['pip', 'install', '--upgrade', 'yt-dlp'], check=True)
        print_colored("[✓] Dependencies installed successfully!", 'green')
    except:
        print_colored("[!] Failed to install dependencies", 'red')
        sys.exit(1)

def add_to_history(filepath):
    if not os.path.exists(filepath):
        return
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    history.append({
        'file': os.path.basename(filepath),
        'path': filepath,
        'time': datetime.now().isoformat(),
        'size': os.path.getsize(filepath)
    })
    history = history[-50:]
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

def show_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
        if history:
            print_colored("\n╔══════════════════════════════════════════════════════════════╗", 'cyan', bold=True)
            print_colored("║                     DOWNLOAD HISTORY                        ║", 'cyan', bold=True)
            print_colored("╚══════════════════════════════════════════════════════════════╝", 'cyan', bold=True)
            for i, entry in enumerate(reversed(history[-10:]), 1):
                size_mb = entry['size'] / (1024*1024)
                date_str = entry['time'][:19].replace('T', ' ')
                print_colored(f"  {i}. {entry['file'][:40]}... ({size_mb:.1f} MB) - {date_str}", 'yellow')
        else:
            print_colored("\n[ No downloads yet ]", 'yellow')
    else:
        print_colored("\n[ No history found ]", 'yellow')

def search_youtube(query):
    try:
        cmd = [
            'yt-dlp',
            '--default-search', 'ytsearch5',
            '--flat-playlist',
            '--dump-json',
            f'ytsearch5:{query}'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        entries = []
        for line in result.stdout.strip().split('\n'):
            if line:
                entries.append(json.loads(line))
        return entries
    except:
        return None

# ========== WATERMARK FUNCTIONS ==========
def apply_video_watermark(filepath):
    """Add 'DarkX Official tools' watermark to video in-place."""
    if not shutil.which('ffmpeg'):
        print_colored("[!] ffmpeg not found, skipping watermark", 'yellow')
        return False
    
    temp_file = filepath + ".temp" + os.path.splitext(filepath)[1]
    cmd = [
        'ffmpeg', '-i', filepath,
        '-vf', "drawtext=text='DarkX Official tools':fontcolor=white:fontsize=24:x=w-tw-10:y=10:bordercolor=black:borderw=2",
        '-codec:a', 'copy',
        '-y', temp_file
    ]
    
    try:
        print_colored(f"[i] Applying video watermark to {os.path.basename(filepath)}...", 'cyan')
        subprocess.run(cmd, check=True, capture_output=True)
        shutil.move(temp_file, filepath)
        print_colored(f"[✓] Watermark added to {os.path.basename(filepath)}", 'green')
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"[!] Failed to apply watermark to {os.path.basename(filepath)}", 'red')
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return False

def apply_audio_watermark(filepath):
    """Rename audio file to include 'DarkX Official tools'."""
    dirname = os.path.dirname(filepath)
    basename = os.path.basename(filepath)
    name, ext = os.path.splitext(basename)
    new_basename = f"{name} [DarkX Official tools]{ext}"
    new_path = os.path.join(dirname, new_basename)
    
    counter = 1
    while os.path.exists(new_path):
        new_basename = f"{name} [DarkX Official tools {counter}]{ext}"
        new_path = os.path.join(dirname, new_basename)
        counter += 1
    
    os.rename(filepath, new_path)
    print_colored(f"[✓] Audio filename updated: {new_basename}", 'green')
    return new_path

# ========== CORE DOWNLOAD (called inside thread) ==========
def perform_download(url, quality, format_choice, subtitles, sub_lang):
    """Actual download routine – runs in a thread."""
    filename_template = os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')
    
    command = [
        'yt-dlp',
        '--no-mtime',
        '--embed-metadata',
        '--embed-thumbnail',
        '-o', filename_template,
        '--newline',
        '--no-warnings',
        '--print', 'after_move:filepath'
    ]
    
    if format_choice == 'mp3':
        command.extend(['-f', 'bestaudio', '--extract-audio', '--audio-format', 'mp3', '--audio-quality', '0'])
    elif format_choice == 'mkv':
        command.extend(['-f', quality, '--merge-output-format', 'mkv'])
    else:  # mp4
        command.extend(['-f', quality, '--merge-output-format', 'mp4'])
    
    if subtitles:
        command.extend(['--write-subs', '--sub-lang', sub_lang, '--embed-subs'])
    
    command.append(url)
    
    # Run yt-dlp and capture output
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, bufsize=1, universal_newlines=True)
    
    output_lines = []
    for line in process.stdout:
        output_lines.append(line.rstrip())
        # We still print to console so user sees progress (though it may interleave)
        print(line, end='')
    
    process.wait()
    if process.returncode != 0:
        raise Exception("yt-dlp failed")
    
    # Extract file paths from output
    file_paths = []
    for line in output_lines:
        line = line.strip()
        if line.startswith(DOWNLOAD_FOLDER) and os.path.exists(line):
            file_paths.append(line)
    
    if not file_paths:
        raise Exception("Could not locate downloaded file")
    
    # Process each file
    for filepath in file_paths:
        if format_choice == 'mp3':
            new_path = apply_audio_watermark(filepath)
            add_to_history(new_path)
        else:  # video formats
            # Add to history immediately (before watermark)
            add_to_history(filepath)
            # Apply video watermark in background? No, it's already in a thread,
            # so we just do it synchronously here; it won't block the main menu.
            apply_video_watermark(filepath)
    
    return file_paths[0]  # return primary file

# ========== JOB MANAGEMENT ==========
class DownloadJob:
    def __init__(self, url, quality, format_choice, subtitles, sub_lang):
        self.url = url
        self.quality = quality
        self.format_choice = format_choice
        self.subtitles = subtitles
        self.sub_lang = sub_lang
        self.status = "pending"
        self.output_file = None
        self.error = None
        self.thread = None
        self.start_time = None
        self.end_time = None

    def start(self):
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.start_time = datetime.now()
        self.status = "downloading"
        self.thread.start()

    def _run(self):
        try:
            self.output_file = perform_download(
                self.url, self.quality, self.format_choice,
                self.subtitles, self.sub_lang
            )
            self.status = "completed"
        except Exception as e:
            self.status = "failed"
            self.error = str(e)
        finally:
            self.end_time = datetime.now()

    def info(self):
        duration = ""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            duration = f" in {delta.seconds}s"
        elif self.start_time:
            delta = datetime.now() - self.start_time
            duration = f" (running {delta.seconds}s)"
        return f"{self.url[:50]}... [{self.status}]{duration}"

def add_job(url, quality, format_choice, subtitles, sub_lang):
    job = DownloadJob(url, quality, format_choice, subtitles, sub_lang)
    with jobs_lock:
        jobs.append(job)
    job.start()
    return job

def list_jobs():
    with jobs_lock:
        if not jobs:
            print_colored("No jobs.", 'yellow')
            return
        print_colored("\n╔══════════════════════════════════════════════════════════════╗", 'cyan', bold=True)
        print_colored("║                         JOB QUEUE                            ║", 'cyan', bold=True)
        print_colored("╚══════════════════════════════════════════════════════════════╝", 'cyan', bold=True)
        for i, job in enumerate(jobs, 1):
            print_colored(f" {i}. {job.info()}", 'yellow')

def clear_completed_jobs():
    with jobs_lock:
        global jobs
        jobs = [j for j in jobs if j.status not in ("completed", "failed")]
    print_colored("Completed/failed jobs removed.", 'green')

# ========== USER MENUS ==========
def quality_menu():
    print_colored("\n╔══════════════════════════════════════════════════════════════╗", 'cyan', bold=True)
    print_colored("║                     QUALITY OPTIONS                           ║", 'cyan', bold=True)
    print_colored("╚══════════════════════════════════════════════════════════════╝", 'cyan', bold=True)
    print_colored(" 1. 4K Ultra HD (2160p)", 'yellow')
    print_colored(" 2. 1080p Full HD", 'yellow')
    print_colored(" 3. 720p HD (Default)", 'yellow')
    print_colored(" 4. 480p (Mobile)", 'yellow')
    print_colored(" 5. 360p (Small)", 'yellow')
    print_colored(" 6. Audio only (MP3)", 'yellow')
    print_colored(" 7. Custom resolution (e.g., 720)", 'yellow')
    print_colored(" 8. Best quality (no limit)", 'yellow')
    choice = input("⚡ Choose (1-8): ").strip()
    
    quality_map = {
        '1': 'bestvideo[height<=2160]+bestaudio/best[height<=2160]',
        '2': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        '3': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        '4': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
        '5': 'bestvideo[height<=360]+bestaudio/best[height<=360]',
        '6': 'bestaudio',
        '8': 'bestvideo+bestaudio/best'
    }
    
    if choice == '7':
        custom = input("Enter desired height (e.g., 720): ").strip()
        if custom.isdigit():
            return f'bestvideo[height<={custom}]+bestaudio/best[height<={custom}]'
        else:
            print_colored("Invalid input, using 720p.", 'red')
            return quality_map['3']
    
    return quality_map.get(choice, quality_map['3'])

def format_menu():
    print_colored("\n╔══════════════════════════════════════════════════════════════╗", 'cyan', bold=True)
    print_colored("║                     FORMAT OPTIONS                            ║", 'cyan', bold=True)
    print_colored("╚══════════════════════════════════════════════════════════════╝", 'cyan', bold=True)
    print_colored(" 1. MP4 Video", 'yellow')
    print_colored(" 2. MP3 Audio", 'yellow')
    print_colored(" 3. MKV Video", 'yellow')
    choice = input("⚡ Choose (1-3): ").strip()
    format_map = {'1': 'mp4', '2': 'mp3', '3': 'mkv'}
    return format_map.get(choice, 'mp4')

def subtitle_menu():
    print_colored("\n╔══════════════════════════════════════════════════════════════╗", 'cyan', bold=True)
    print_colored("║                     SUBTITLES OPTIONS                         ║", 'cyan', bold=True)
    print_colored("╚══════════════════════════════════════════════════════════════╝", 'cyan', bold=True)
    choice = input("Download subtitles? (y/n): ").strip().lower()
    if choice == 'y':
        lang = input("Language code (e.g., en, sw, fr) [default=en]: ").strip() or 'en'
        return True, lang
    return False, 'en'

def handle_playlist(url):
    """Ask user how to handle playlist – returns list of URLs."""
    try:
        result = subprocess.run(
            ['yt-dlp', '--flat-playlist', '--dump-json', '--playlist-end', '1', url],
            capture_output=True, text=True
        )
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout.strip().split('\n')[0])
            if 'playlist_count' in data or 'playlist' in url:
                print_colored("\n╔══════════════════════════════════════════════════════════════╗", 'magenta', bold=True)
                print_colored("║                     PLAYLIST DETECTED                        ║", 'magenta', bold=True)
                print_colored("╚══════════════════════════════════════════════════════════════╝", 'magenta', bold=True)
                print_colored(f"Title: {data.get('playlist', 'Unknown')}", 'yellow')
                print_colored("Options:", 'cyan')
                print_colored(" 1. Download entire playlist", 'yellow')
                print_colored(" 2. Select specific videos (by number)", 'yellow')
                print_colored(" 3. Download as audio (entire playlist)", 'yellow')
                print_colored(" 4. Cancel", 'yellow')
                choice = input("⚡ Choose (1-4): ").strip()
                
                if choice == '2':
                    result2 = subprocess.run(
                        ['yt-dlp', '--flat-playlist', '--dump-json', url],
                        capture_output=True, text=True
                    )
                    videos = []
                    for line in result2.stdout.strip().split('\n'):
                        if line:
                            videos.append(json.loads(line))
                    print_colored("\nVideos in playlist:", 'cyan')
                    for i, v in enumerate(videos[:20], 1):
                        print_colored(f" {i}. {v.get('title', 'Unknown')[:60]}", 'yellow')
                    if len(videos) > 20:
                        print_colored(f" ... and {len(videos)-20} more", 'yellow')
                    indices = input("Enter video numbers to download (e.g., 1,3,5-10): ").strip()
                    selected = []
                    parts = indices.split(',')
                    for part in parts:
                        if '-' in part:
                            start, end = map(int, part.split('-'))
                            selected.extend(range(start-1, min(end, len(videos))))
                        elif part.isdigit():
                            selected.append(int(part)-1)
                    selected_urls = [videos[i]['url'] for i in selected if 0 <= i < len(videos)]
                    return selected_urls
                elif choice == '3':
                    return [url]
                elif choice == '1':
                    return [url]
                else:
                    return None
    except:
        pass
    return [url]

def settings_menu():
    global config, DOWNLOAD_FOLDER
    while True:
        clear_screen()
        print_colored("\n╔══════════════════════════════════════════════════════════════╗", 'cyan', bold=True)
        print_colored("║                         SETTINGS                              ║", 'cyan', bold=True)
        print_colored("╚══════════════════════════════════════════════════════════════╝", 'cyan', bold=True)
        print_colored(f" 1. Download folder: {config['download_folder']}", 'yellow')
        print_colored(f" 2. Default quality: {config['default_quality'][:50]}...", 'yellow')
        print_colored(f" 3. Default format: {config['default_format']}", 'yellow')
        print_colored(f" 4. History size: {config['history_size']}", 'yellow')
        print_colored(" 5. Back to main menu", 'yellow')
        
        opt = input("⚡ Choose option (1-5): ").strip()
        if opt == '1':
            new_folder = input("Enter new download folder path: ").strip()
            if new_folder:
                if not os.path.exists(new_folder):
                    try:
                        os.makedirs(new_folder)
                    except:
                        print_colored("Cannot create folder. Check permissions.", 'red')
                        continue
                config['download_folder'] = new_folder
                DOWNLOAD_FOLDER = new_folder
                save_config(config)
                print_colored("Folder updated.", 'green')
        elif opt == '2':
            print_colored("Select default quality:", 'cyan')
            q = quality_menu()
            config['default_quality'] = q
            save_config(config)
        elif opt == '3':
            f = format_menu()
            config['default_format'] = f
            save_config(config)
        elif opt == '4':
            sz = input("Enter max history entries (e.g., 20): ").strip()
            if sz.isdigit():
                config['history_size'] = int(sz)
                save_config(config)
        elif opt == '5':
            break
        time.sleep(1)

# ========== MAIN LOOP ==========
def main():
    global config, DOWNLOAD_FOLDER
    
    if not check_dependencies():
        print_colored("[!] Required dependencies missing. Installing...", 'yellow')
        install_dependencies()
    
    while True:
        clear_screen()
        print_banner()
        print_colored(f"📁 Download folder: {DOWNLOAD_FOLDER}", 'green')
        print_colored("\n╔══════════════════════════════════════════════════════════════╗", 'cyan', bold=True)
        print_colored("║                         MAIN MENU                             ║", 'cyan', bold=True)
        print_colored("╚══════════════════════════════════════════════════════════════╝", 'cyan', bold=True)
        print_colored(" 1. Download from URL(s)", 'yellow')
        print_colored(" 2. Search YouTube and download", 'yellow')
        print_colored(" 3. Batch download from file (URLs list)", 'yellow')
        print_colored(" 4. Show download history", 'yellow')
        print_colored(" 5. Show running jobs", 'yellow')
        print_colored(" 6. Clear completed/failed jobs", 'yellow')
        print_colored(" 7. Settings", 'yellow')
        print_colored(" 8. Exit", 'yellow')
        choice = input("⚡ Choose (1-8): ").strip()
        
        if choice == '1':
            urls_input = input("\nEnter YouTube URL(s) (separate with space): ").strip().split()
            if not urls_input:
                continue
            
            all_urls = []
            for url in urls_input:
                playlist_urls = handle_playlist(url)
                if playlist_urls:
                    all_urls.extend(playlist_urls)
                else:
                    continue
            
            if not all_urls:
                continue
            
            quality = quality_menu()
            format_choice = format_menu()
            subtitles, sub_lang = subtitle_menu()
            
            for url in all_urls:
                add_job(url, quality, format_choice, subtitles, sub_lang)
                print_colored(f"Job added for {url}", 'green')
            
            input("\nPress Enter to continue...")
        
        elif choice == '2':
            query = input("Enter search term: ").strip()
            if not query:
                continue
            results = search_youtube(query)
            if not results:
                print_colored("No results found or error.", 'red')
                input("Press Enter...")
                continue
            
            print_colored("\n╔══════════════════════════════════════════════════════════════╗", 'cyan', bold=True)
            print_colored("║                     SEARCH RESULTS                            ║", 'cyan', bold=True)
            print_colored("╚══════════════════════════════════════════════════════════════╝", 'cyan', bold=True)
            for i, res in enumerate(results, 1):
                title = res.get('title', 'Unknown')
                duration = res.get('duration_string', 'N/A')
                uploader = res.get('uploader', 'Unknown')
                print_colored(f" {i}. {title[:70]}", 'yellow')
                print_colored(f"    👤 {uploader}  ⏱️ {duration}", 'white')
            
            sel = input("\nEnter video numbers to download (e.g., 1,2,3): ").strip()
            indices = []
            for part in sel.split(','):
                if part.isdigit():
                    idx = int(part)-1
                    if 0 <= idx < len(results):
                        indices.append(idx)
            if not indices:
                print_colored("No valid selection.", 'red')
                continue
            
            urls = [results[i]['webpage_url'] for i in indices]
            quality = quality_menu()
            format_choice = format_menu()
            subtitles, sub_lang = subtitle_menu()
            
            for url in urls:
                add_job(url, quality, format_choice, subtitles, sub_lang)
                print_colored(f"Job added for {url}", 'green')
            
            input("\nPress Enter to continue...")
        
        elif choice == '3':
            file_path = input("Enter path to text file with URLs (one per line): ").strip()
            if not os.path.exists(file_path):
                print_colored("File not found.", 'red')
                continue
            with open(file_path, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            if not urls:
                print_colored("No URLs in file.", 'red')
                continue
            
            quality = quality_menu()
            format_choice = format_menu()
            subtitles, sub_lang = subtitle_menu()
            
            for url in urls:
                add_job(url, quality, format_choice, subtitles, sub_lang)
                print_colored(f"Job added for {url}", 'green')
            
            input("\nPress Enter to continue...")
        
        elif choice == '4':
            show_history()
            input("\nPress Enter to continue...")
        
        elif choice == '5':
            list_jobs()
            input("\nPress Enter to continue...")
        
        elif choice == '6':
            clear_completed_jobs()
            input("\nPress Enter to continue...")
        
        elif choice == '7':
            settings_menu()
        
        elif choice == '8':
            # Optional: wait for running jobs to finish?
            running = [j for j in jobs if j.status in ("pending", "downloading")]
            if running:
                print_colored(f"There are {len(running)} job(s) still running. Exit anyway? (y/n): ", 'yellow', end='')
                if input().lower() != 'y':
                    continue
            print_colored("\nThank you for using DarkX Next-Level Downloader!", 'magenta', bold=True)
            print_colored("Contact: 255775710774", 'cyan')
            break
        
        else:
            print_colored("Invalid choice.", 'red')
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n⚠️  Download cancelled by user", 'yellow')
        sys.exit(0)
    except Exception as e:
        print_colored(f"\n[!] Unexpected error: {e}", 'red')
        sys.exit(1)
