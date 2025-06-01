# SequenceMaster
A tool to load shp unit frames with its sequence ini, and see the frames with animations.

## Usage:
Load your frames, (select transparency color if desired). Select Infantry or Vehicl, and paste the sequence,  
rightclick on frames for copy/pasting and swapping if needed
Press Convert to Vehicle/Infantry to convert.
Save frames

![sequencemaster_convert](https://github.com/user-attachments/assets/6f81b86d-c3a2-4d03-83bd-c50bd14b7e19)





# inf_sequence_completer (the button topleft)
A Infantry Sequence helper tool for RA2/TS to help generate the right ini entries for infantry sequence in the art.ini

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
