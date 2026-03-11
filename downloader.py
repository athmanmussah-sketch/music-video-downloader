#!/data/data/com.termux/files/usr/bin/python
import os
import subprocess
import sys

# Badili hapa - tumia njia kamili ya kuhifadhi kwenye Download folder
DOWNLOAD_FOLDER = "/storage/emulated/0/Download/music_videos"

# Unda folda ikiwa haipo
if not os.path.exists(DOWNLOAD_FOLDER):
    try:
        os.makedirs(DOWNLOAD_FOLDER)
        print(f"[+] Folda '{DOWNLOAD_FOLDER}' imeundwa.")
    except Exception as e:
        print(f"[!] Hitilafu wakati wa kuunda folda: {e}")
        print("[!] Hakikisha umetoa ruhusa ya kuhifadhi kwa Termux.")
        print("[!] Endesha: termux-setup-storage")
        sys.exit(1)

# Anza
print("="*50)
print("       MUSIC VIDEO DOWNLOADER (YouTube)")
print("="*50)
print(f"[+] Mahala pa kuhifadhi: {DOWNLOAD_FOLDER}")

# Uliza URL
video_url = input("\nIngiza URL ya video au playlist ya YouTube: ").strip()
if not video_url:
    print("[!] URL haipo. Inatoka...")
    sys.exit(1)

# Uliza ubora
print("\nChagua ubora wa video:")
print("  1. Juu Kabisa (default)")
print("  2. 720p")
print("  3. 480p")
print("  4. 360p")
quality_choice = input("Chaguo lako (1-4, bonyeza Enter kwa default 1): ").strip()

# Amua ubora (format ya yt-dlp)
if quality_choice == '2':
    quality = 'best[height<=720]'
elif quality_choice == '3':
    quality = 'best[height<=480]'
elif quality_choice == '4':
    quality = 'best[height<=360]'
else:
    quality = 'best' # Default

# Uliza aina ya faili
print("\nChagua aina ya faili:")
print("  1. Video (MP4) - default")
print("  2. Audio tu (MP3)")
file_type = input("Chaguo lako (1-2, bonyeza Enter kwa default 1): ").strip()

# Tengeneza amri ya kupakua
print(f"\n[+] Inaanza kupakua...")
print(f"[+] Ubora: {quality}")
print(f"[+] Mahala pa kuhifadhi: {DOWNLOAD_FOLDER}")

if file_type == '2':
    # Pakua audio tu (MP3)
    command = [
        'yt-dlp',
        '-f', 'bestaudio',
        '--extract-audio',
        '--audio-format', 'mp3',
        '--audio-quality', '0',  # Ubora bora wa audio
        '-o', f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        '--embed-thumbnail',
        '--embed-metadata',
        '--no-mtime',
        video_url
    ]
else:
    # Pakua video (MP4)
    command = [
        'yt-dlp',
        '-f', f'{quality}+bestaudio/best',
        '--merge-output-format', 'mp4',
        '-o', f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        '--no-mtime',
        '--embed-thumbnail',
        '--embed-metadata',
        video_url
    ]

# Endesha amri
try:
    subprocess.run(command, check=True)
    print("\n" + "="*50)
    print("[✓] Umefanikiwa!")
    print(f"[✓] Tafuta faili yako kwenye: {DOWNLOAD_FOLDER}")
    
    # Onyesha faili zilizopo
    if os.path.exists(DOWNLOAD_FOLDER):
        files = os.listdir(DOWNLOAD_FOLDER)
        if files:
            print("\nFaili zilizopo kwenye folder:")
            for f in files[-5:]:  # Onyesha faili 5 za mwisho
                if f.endswith(('.mp4', '.mp3', '.mkv', '.webm')):
                    print(f"  - {f}")
    
    print("="*50)
    
except subprocess.CalledProcessError as e:
    print(f"\n[!] Kuna hitilafu ilitokea: {e}")
    print("[!] Hakikisha URL yako ni sahihi na una muunganisho wa intaneti.")
except FileNotFoundError:
    print("\n[!] 'yt-dlp' haijasakinishwa. Endesha:")
    print("    pkg install python ffmpeg -y")
    print("    pip install yt-dlp")
except Exception as e:
    print(f"\n[!] Hitilafu nyingine: {e}")
