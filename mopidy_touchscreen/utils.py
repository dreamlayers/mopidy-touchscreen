import mopidy.models

# It is possible that not all tracks loaded into the
# tracklist. Try to play the right track.
def play_track(core, tracklist, idx):
    uri = tracklist[idx].uri
    uricnt = 0
    # Find how many times uri occurs before desired track.
    for i in range(0, idx):
        if tracklist[i].uri == uri:
            uricnt += 1

    tracks = core.tracklist.get_tl_tracks().get()
    for tlt in tracks:
        if tlt.track.uri == uri:
            if uricnt == 0:
                core.playback.play(tl_track=tlt)
                break
            uricnt -= 1
