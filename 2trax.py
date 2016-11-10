#!/usr/bin/env

from __future__ import print_function

"""
2trax.py - Convert a single file album to individual tracks.
License: BSD 3-Clause
Copyright (c) 2016, Mauro <mauro@sdf.org>
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:
1. Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its
contributors may be used to endorse or promote products derived from
this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

__author__ = 'Mauro'
__version__ = '0.0.01'
__license__ = 'BSD3'


import os
import re
import shlex
import argparse
import subprocess as sp
from datetime import datetime as dt

TRACK_RE = "(?P<track>.*) (?P<time>\d{2}:\d{2})"
LENGTH_RE = "\d:(\d{2}:\d{2})\.\d+?"
MUSICDIR_RE = '.*="(.*)"'
__file = os.path.basename(__file__)

#
# user music home
#

def music_home():
    try:
        user_dirs = open(os.path.join(os.path.expanduser("~"), ".config", "user-dirs.dirs")).readlines()
        music_dir = filter(lambda line: "XDG_MUSIC_DIR" in line, user_dirs)
        if music_dir:
            music_dir = music_dir.pop() # i prefer other music styles but whatever

        return os.path.expandvars(re.findall(MUSICDIR_RE, music_dir)[0])
    except:
        from tempfile import gettempdir
        return gettempdir()


#
# ffmpeg stuff
#

def ffmpeg(args, verbose=False):
    "Base ffmpeg system call"
    cmd = "ffmpeg {} -y {}".format(
        '' if verbose else '-v quiet',
        args
    )
    sp.call(shlex.split(cmd))


def ffprobe(args, verbose=False):
    "Base ffprobe system call"
    cmd = "ffprobe {} {}".format(
        '' if verbose else '-v quiet',
        args
    )
    return sp.check_output(shlex.split(cmd))


def length(audio_in, show_sexagesimal=True, verbose=False):
    "Returns the length of an audio"
    duration = 'duration='
    args = '-show_format {} -i "{}"'.format(
        '-sexagesimal' if show_sexagesimal else '',
        audio_in)
    output = ffprobe(args, verbose)
    result = map(lambda line: line.replace(duration, ''),
                filter(lambda line: line.startswith(duration),
                       output.split("\n")))[0]
    _length = re.findall(LENGTH_RE, result)
    if _length:
        _length = _length[0]
        return _length


def cut(audio_in, audio_out, start, duration, verbose=False):
    "Cuts a portion of an audio."
    if isinstance(audio_in, (list, tuple)):
        audio_in = audio_in[0]

    args = '-i "{}" -ss "{}" -t "{}" -acodec copy "{}"'.format(
        audio_in, start, duration, audio_out)
    ffmpeg(args, verbose)

#
# shitty sanitization
#

def sanitize_timestamp(timestamp):
    "Tries in a crappy way to sanitize the timestamp"
    return "00:" + timestamp


def sanitize_track(track, file_ext=".mp3", no_spaces=True):
    "Tries in a crappy way to sanitize the trackname"
    if no_spaces:
        track = track.replace(" ", "_")
    return track + file_ext

#
# fs stuff
#

def check_directory(dir_path):
    "Verifies if a directory exists, if not tries to create it"
    if os.path.isdir(dir_path):
        return True
    else:
        try:
            os.makedirs(dir_path)
            return True
        except:
            pass

    return False

#
# does the tracklist exists?
#

def tracklist(tracklist_file=None):
    """Returns a dictionary as timestamp:track_name given a tracklist file with format
    1. trackname 00:00
    2. trackname2 05:10
    3. trackname3 13:25
    ...
    """
    if os.path.isfile(tracklist_file):
        return dict([(timestamp, track) for track, timestamp in \
                     [re.findall(TRACK_RE, track)[0] for track in open(tracklist_file, 'r').readlines()]])
    else:
        return []


#
# time stuff
#


def time_delta(timestamp_a=None, timestamp_b=None):
    "Returns the difference between two timestamps with MM:SS format"
    timeformat = '%H:%M:%S'
    if timestamp_a and timestamp_b:
        timestamp_a = sanitize_timestamp(timestamp_a)
        timestamp_b = sanitize_timestamp(timestamp_b)
        tdelta = dt.strptime(timestamp_a, timeformat) - dt.strptime(timestamp_b, timeformat)
        return sanitize_timestamp(str(tdelta)[2:])
    else:
        return ""


#
# here's where the magic happens
#


def split_audio(audio_file=None, tracklist_file=None, output_dir=None, verbose=False):
    audio_length = length(audio_file)
    _, audio_ext = os.path.splitext(audio_file)
    track_list = tracklist(tracklist_file)
    audio_timestamps = sorted(track_list.keys()) + [audio_length]

    if check_directory(output_dir):
        for n in range(len(audio_timestamps)):
            if n+1 <= len(audio_timestamps)-1:
                audio_out = os.path.join(output_dir,
                                         sanitize_track(track_list.get(audio_timestamps[n]), audio_ext, False))
                start = sanitize_timestamp(audio_timestamps[n])
                duration = time_delta(audio_timestamps[n+1], audio_timestamps[n])

                cut(audio_file, audio_out, start, duration)
                if verbose:
                    print(audio_out)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--audio-file',
                        type=str,
                        help="Use this audio as source")
    parser.add_argument('-o', '--output-directory',
                        type=str,
                        default=music_home(),
                        help="Save the audio files in this directory. Default: {}""".format(music_home()))
    parser.add_argument('-t', '--tracklist',
                        type=str,
                        help="Use this file to cut the audio")
    parser.add_argument('-V', '--verbose',
                        action="store_true",
                        help="Show stdout messages")


    args = parser.parse_args()
    if args.audio_file and args.tracklist:
        split_audio(args.audio_file, args.tracklist, args.output_directory, args.verbose)
    else:
        print("{} -h".format(__file))
