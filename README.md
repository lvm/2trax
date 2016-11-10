# 2trax

```
2trax.py - Split a single file album to individual tracks.
```

Sometimes I download albums from Youtube using [youtube-dl](http://youtube-dl.org/) (which does an awesome job) and most of these times someone posted a tracklist with the minutes for each song so you can skip directly to that moment. The thing is that when I have the full-length mp3 in my phone I just can't skip directly to that precise moment.

## usage

```bash
usage: 2trax.py [-h] [-a AUDIO_FILE] [-o OUTPUT_DIRECTORY] [-t TRACKLIST] [-V]

optional arguments:
  -h, --help            show this help message and exit
  -a AUDIO_FILE, --audio-file AUDIO_FILE
                        Use this audio as source
  -o OUTPUT_DIRECTORY, --output-directory OUTPUT_DIRECTORY
                        Save the audio files in this directory. Default: ~/Music
  -t TRACKLIST, --tracklist TRACKLIST
                        Use this file to cut the audio
  -V, --verbose         Show stdout messages
```

Note: The default directory is the one defined in `~/.local/user-dirs.dirs`, if that file is inaccesible will use `/tmp` (actually, the result of `tempfile.gettempdir()`) instead.  



First you'll need to download the album.  
In this case `Charles Mingus - Pithecanthropus Erectus`  

```bash
$ youtube-dl --extract-audio --audio-format mp3 https://www.youtube.com/watch?v=F3Ltp6U1IJU
...
[ffmpeg] Destination: Charles Mingus - Pithecanthropus Erectus (full album)-F3Ltp6U1IJU.mp3
...
```

And save the tracklist somewhere, for example: `/tmp/mingus-tracklist.txt`  
```
1. Pithecanthropus Erectus 00:06
2. A Foggy Day 10:40
3. Profile of Jackie 18:30
4. Love Chant 21:40
```

Now we can split the album:  
```bash
$ python 2trax.py -a ~/Music/Charles\ Mingus\ -\ Pithecanthropus\ Erectus\ \(full\ album\)-F3Ltp6U1IJU.mp3 \
                  -t /tmp/mingus-tracklist.txt \
                  -o /tmp/mingus-Pithecanthropus
```

That's it.
