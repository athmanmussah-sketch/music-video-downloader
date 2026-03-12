#!/data/data/com.termux/files/usr/bin/python
import os
import subprocess
import sys
from datetime import datetime

DOWNLOAD_FOLDER = "/storage/emulated/0/Download/music_videos"

if not os.path.exists(DOWNLOAD_FOLDER):
    try:
        os.makedirs(DOWNLOAD_FOLDER)
    except Exception as e:
        print(f"\033[91m[!] Storage permission denied!\033[0m")
        print("\033[93m[i] Run: termux-setup-storage\033[0m")
        sys.exit(1)

def clear_screen():
    os.system('clear')

def print_banner():
    banner = """
\033[96m╔══════════════════════════════════════════════════════════╗
║                                                              ║
║      ██████╗  █████╗ ██████╗ ██╗  ██╗  ██╗                 ║
║      ██╔══██╗██╔══██╗██╔══██╗╚██╗██╔╝  ██║                 ║
║      ██║  ██║███████║██████╔╝ ╚███╔╝   ██║                 ║
║      ██║  ██║██╔══██║██╔══██╗ ██╔██╗   ██║                 ║
║      ██████╔╝██║  ██║██║  ██║██╔╝ ██╗  ██║                 ║
║      ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═╝                 ║
║                                                              ║
║           \033[92mVIDEO DOWNLOADER - TERMUX EDITION\033[96m                ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  \033[93mDeveloper: DarkX Dev\033[96m                                      ║
║  \033[93mContact: 255775710774\033[96m                                      ║
║  \033[93mVersion: 2.0.0\033[96m                                             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝\033[0m
"""
    print(banner)

def check_dependencies():
    try:
        subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
        return True
    except:
        return False

def install_dependencies():
    print("\033[93m[i] Installing required dependencies...\033[0m")
    try:
        subprocess.run(['pkg', 'install', 'python', 'ffmpeg', '-y'], check=True)
        subprocess.run(['pip', 'install', '--upgrade', 'yt-dlp'], check=True)
        print("\033[92m[✓] Dependencies installed successfully!\033[0m")
    except:
        print("\033[91m[!] Failed to install dependencies\033[0m")
        sys.exit(1)

def get_quality_choice():
    print("\n\033[96m[ QUALITY SETTINGS ]\033[0m")
    print("\033[93m╔════════════════════════════════╗")
    print("║  1. 🔥 4K Ultra HD            ║")
    print("║  2. 💫 1080p Full HD           ║")
    print("║  3. ✨ 720p HD                 ║")
    print("║  4. 📱 480p (Mobile)           ║")
    print("║  5. 💾 360p (Small size)       ║")
    print("║  6. 🎵 Audio Only (MP3)         ║")
    print("╚════════════════════════════════╝\033[0m")
    
    quality_map = {
        '1': 'bestvideo[height<=2160]+bestaudio/best[height<=2160]',
        '2': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        '3': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        '4': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
        '5': 'bestvideo[height<=360]+bestaudio/best[height<=360]',
        '6': 'bestaudio'
    }
    
    choice = input("\n\033[92m⚡ Select option (1-6): \033[0m").strip()
    return quality_map.get(choice, quality_map['3'])

def get_format_choice():
    print("\n\033[96m[ OUTPUT FORMAT ]\033[0m")
    print("\033[93m╔════════════════════════════════╗")
    print("║  1. 📹 MP4 Video              ║")
    print("║  2. 🎵 MP3 Audio               ║")
    print("║  3. 🎬 MKV Video               ║")
    print("╚════════════════════════════════╝\033[0m")
    
    choice = input("\n\033[92m⚡ Select format (1-3): \033[0m").strip()
    return choice if choice in ['1', '2', '3'] else '1'

def download_media(url, quality, format_choice):
    filename_template = f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s'
    
    if format_choice == '2':
        command = [
            'yt-dlp',
            '-f', 'bestaudio',
            '--extract-audio',
            '--audio-format', 'mp3',
            '--audio-quality', '0',
            '--embed-thumbnail',
            '--embed-metadata',
            '--no-mtime',
            '-o', filename_template,
            '--progress',
            '--newline',
            '--no-warnings',
            url
        ]
    elif format_choice == '3':
        command = [
            'yt-dlp',
            '-f', quality,
            '--merge-output-format', 'mkv',
            '--embed-thumbnail',
            '--embed-metadata',
            '--no-mtime',
            '-o', filename_template,
            '--progress',
            '--newline',
            '--no-warnings',
            url
        ]
    else:
        command = [
            'yt-dlp',
            '-f', quality,
            '--merge-output-format', 'mp4',
            '--embed-thumbnail',
            '--embed-metadata',
            '--no-mtime',
            '-o', filename_template,
            '--progress',
            '--newline',
            '--no-warnings',
            url
        ]
    
    try:
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def show_downloaded_files():
    if os.path.exists(DOWNLOAD_FOLDER):
        files = [f for f in os.listdir(DOWNLOAD_FOLDER) 
                if f.endswith(('.mp4', '.mp3', '.mkv', '.webm'))]
        if files:
            print("\n\033[96m[ RECENT DOWNLOADS ]\033[0m")
            for i, f in enumerate(sorted(files, key=lambda x: os.path.getmtime(os.path.join(DOWNLOAD_FOLDER, x)), reverse=True)[:5], 1):
                size = os.path.getsize(os.path.join(DOWNLOAD_FOLDER, f)) / (1024*1024)
                print(f"\033[93m  {i}. {f[:40]}... ({size:.1f} MB)\033[0m")

def main():
    while True:
        clear_screen()
        print_banner()
        
        print(f"\033[90m[ Storage: {DOWNLOAD_FOLDER} ]\033[0m\n")
        
        if not check_dependencies():
            print("\033[91m[!] yt-dlp not found!\033[0m")
            choice = input("\n\033[93m⚡ Install dependencies? (y/n): \033[0m").strip().lower()
            if choice == 'y':
                install_dependencies()
            else:
                sys.exit(1)
        
        url = input("\033[92m🎯 Enter YouTube URL: \033[0m").strip()
        if not url:
            print("\033[91m[!] URL required!\033[0m")
            continue
        
        quality = get_quality_choice()
        format_choice = get_format_choice()
        
        print(f"\n\033[96m[ PROCESSING ]\033[0m")
        print(f"\033[93m📁 Saving to: {DOWNLOAD_FOLDER}\033[0m")
        print(f"\033[93m⚡ Quality: {quality[:30]}...\033[0m")
        print(f"\033[93m🎯 Format: {'MP3' if format_choice=='2' else 'MKV' if format_choice=='3' else 'MP4'}\033[0m")
        print("\n\033[92m⬇️  Downloading...\033[0m\n")
        
        if download_media(url, quality, format_choice):
            print(f"\n\033[92m{'═'*50}")
            print("✅ DOWNLOAD COMPLETE!")
            print(f"{'═'*50}\033[0m")
            show_downloaded_files()
        else:
            print(f"\n\033[91m{'═'*50}")
            print("❌ DOWNLOAD FAILED!")
            print("Please check your URL and internet connection")
            print(f"{'═'*50}\033[0m")
        
        print("\n\033[93mOptions:\033[0m")
        print("  \033[92m1. ⬇️  Download another\033[0m")
        print("  \033[91m2. 🚪 Exit\033[0m")
        
        again = input("\n\033[92m⚡ Choose (1-2): \033[0m").strip()
        if again != '1':
            print(f"\n\033[96m{'═'*50}")
            print("🔰 DarkX Video Downloader")
            print("📞 Contact: 255775710774")
            print("👨‍💻 Developer: DarkX Dev")
            print("🙏 Thank you for using!")
            print(f"{'═'*50}\033[0m")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n\033[93m⚠️  Download cancelled by user\033[0m")
        sys.exit(0)
    except Exception as e:
        print(f"\n\033[91m[!] Unexpected error: {e}\033[0m")
        sys.exit(1)
