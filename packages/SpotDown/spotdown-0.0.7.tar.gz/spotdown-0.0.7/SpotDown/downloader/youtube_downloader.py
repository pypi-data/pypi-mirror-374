# 05.04.2024

import io
import subprocess
from typing import Dict


# External imports
import httpx
from PIL import Image
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console


# Internal utils
from SpotDown.utils.config_json import config_manager
from SpotDown.utils.file_utils import FileUtils


# Variable
quality = config_manager.get("DOWNLOAD", "quality")


class YouTubeDownloader:
    def __init__(self):
        self.console = Console()
        self.file_utils = FileUtils()

    def download(self, video_info: Dict, spotify_info: Dict) -> bool:
        """
        Download YouTube video as mp3 320kbps

        Args:
            video_info (Dict): YouTube video info
            spotify_info (Dict): Spotify track info

        Returns:
            bool: True if download succeeded
        """
        try:
            music_folder = self.file_utils.get_music_folder()
            filename = self.file_utils.create_filename(
                spotify_info.get('artist', 'Unknown Artist'),
                spotify_info.get('title', video_info.get('title', 'Unknown Title'))
            )
            output_path = music_folder / f"{filename}.%(ext)s"

            # Download cover image if available
            cover_path = None
            cover_url = spotify_info.get('cover_url')
            if cover_url:
                try:
                    cover_path = music_folder / f"{filename}_cover.jpg"
                    with httpx.Client(timeout=10) as client:
                        resp = client.get(cover_url)
                        if resp.status_code == 200:

                            # Always save only as jpg
                            if resp.headers.get("content-type", "").endswith("webp") or cover_url.endswith(".webp"):
                                img = Image.open(io.BytesIO(resp.content)).convert("RGB")
                                img.save(cover_path, "JPEG")

                            else:
                                img = Image.open(io.BytesIO(resp.content)).convert("RGB")
                                img.save(cover_path, "JPEG")

                            self.console.print(f"[blue]Downloaded thumbnail: {cover_path}[/blue]")

                        else:
                            cover_path = None
                            
                except Exception as e:
                    self.console.print(f"[yellow]Unable to download cover: {e}[/yellow]")
                    cover_path = None

            ytdlp_options = [
                'yt-dlp',
                '--extract-audio',
                '--audio-format', 'mp3',
                '--audio-quality', quality,
                '--output', str(output_path),
                '--no-playlist',
                '--embed-metadata',
                '--add-metadata',
            ]
            
            if cover_path and cover_path.exists():
                ytdlp_options += ['--embed-thumbnail']
            ytdlp_options.append(video_info['url'])

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Downloading...", total=None)
                process = subprocess.run(
                    ytdlp_options,
                    capture_output=True,
                    text=True
                )
                progress.remove_task(task)

            if process.returncode == 0:

                # Find the downloaded file
                downloaded_files = list(music_folder.glob(f"{filename}.*"))
                if downloaded_files:
                    self.console.print("[red]Download completed![/red]")

                    # Remove cover file after embedding
                    if cover_path and cover_path.exists():
                        try:
                            cover_path.unlink()
                        except Exception:
                            pass
                        
                    return True
                
                else:
                    self.console.print("[yellow]Download apparently succeeded but file not found[/yellow]")
                    return False
                
            else:
                self.console.print("[red]Download error:[/red]")
                self.console.print(f"[red]{process.stderr}[/red]")
                return False

        except Exception as e:
            self.console.print(f"[red]Error during download: {e}[/red]")
            return False