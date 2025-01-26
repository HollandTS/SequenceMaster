# inf_sequence_completer
A Infantry Sequence helper tool for RA2/TS to help generate the right ini entries for infantry sequence in the art.ini
![infseqhlpgif](https://github.com/user-attachments/assets/c8d64bc5-0869-4416-9a31-1f18f678af35)

I made this to simplify writing the Infantry Sequence. All you have to know now is the first and second value, which are:
Starting Frame and Animation frame count (e.g.: Walk=0,6)
The tool does the rest.

Parent keys:
I created parent keys that add keys that can take their parent's values, they will appropriately change any value as needed.
These are the base minimum to get all the keys needed for a complete working sequence
The parent keys are:

Walk
FireUp
Die1
Idle1

Make sure to enter at least these keys!

Other parent keys are:
Fly
Swim
Deploy

There are other mechanics to optimize the sequence too: like Guard and Ready will take each other's values if the one is missing; Prone will take Crawl's values and changes framecount to 1, etc.

* Underlined keys mean:
Its automatically added, and uses the best values of a related key assuming its frames are missing, until defined by the user.

* The TS checkbox:
Simply removes the keys that are used by RA2/YR only

**Click the Help button in the UI for more info about the keys and value explanations**

## The same ini processor is also integrated in my blender addon: https://github.com/HollandTS/cnc_anim_addon
