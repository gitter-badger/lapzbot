import subprocess as sp
import json
import os


def info_extract(fpath):
    # FFProbing for info
    p = sp.Popen(['ffprobe', '-v', 'quiet', '-print_format', 'json=compact=1', '-show_format',
                  str(fpath)], stdout=sp.PIPE, stderr=sp.PIPE)
    op = p.communicate()
    op_json = json.loads(op[0].decode('utf-8'))

    try:
        title = op_json['format']['tags']['title']
        artist = op_json['format']['tags']['artist']
        leng = op_json['format']['duration']
        seconds = float(leng)
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        print('title:', title)
        print('artist:', artist)

        filename = str(title + artist)
        duration = str('%d:%02d:%02d' % (h, m, s))

        return filename, duration

    except LookupError:
        file_name = str(fpath)
        head, tail = os.path.split(file_name)
        filename = os.path.splitext(tail)[0]
        leng = op_json['format']['duration']
        seconds = float(leng)
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        duration = str('%d:%02d:%02d' % (h, m, s))
        return filename, duration


def ytinfo_extractor(savepath):
    p = sp.Popen(['ffprobe', '-v', 'quiet', '-print_format', 'json=compact=1', '-show_format',
                  savepath], stdout=sp.PIPE, stderr=sp.PIPE)
    op = p.communicate()
    op_json = json.loads(op[0].decode('utf-8'))

    head, tail = os.path.split(savepath)
    filename = os.path.splitext(tail)[0]
    leng = op_json['format']['duration']
    seconds = float(leng)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    duration = str('%d:%02d:%02d' % (h, m, s))
    return filename, duration
