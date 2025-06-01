# convert.py
"""
Bulletproof conversion logic for Infantry <-> Vehicle INI and frame order, including frame/shadow reordering and renumbering.
"""

INFANTRY_TO_VEHICLE_KEYS = {
    'Walk':    ('StartWalkFrame', 'WalkFrames'),
    'Ready':   ('StartStandFrame', 'StandingFrames'),
    'Die1':    ('StartDeathFrame', 'DeathFrames'),
    'FireUp':  ('StartFiringFrame', 'FiringFrames'),
    'Idle1':   ('StartIdleFrame', 'IdleFrames'),
}
VEHICLE_TO_INFANTRY_KEYS = {
    ('StartWalkFrame', 'WalkFrames'): 'Walk',
    ('StartStandFrame', 'StandingFrames'): 'Ready',
    ('StartDeathFrame', 'DeathFrames'): 'Die1',
    ('StartFiringFrame', 'FiringFrames'): 'FireUp',
    ('StartIdleFrame', 'IdleFrames'): 'Idle1',
}
INFANTRY_DIRS = ["N", "NW", "W", "SW", "S", "SE", "E", "NE"]
VEHICLE_DIRS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def parse_ini(text):
    result = {}
    for line in text.splitlines():
        if '=' in line:
            k, v = line.split('=', 1)
            result[k.strip()] = v.strip()
    return result

def comment_out_ini(text):
    return '\n'.join([f';{line}' if line.strip() else '' for line in text.splitlines()])

def reorder_block(frames, from_dirs, to_dirs, count):
    """
    Reorder a block of frames from one direction order to another.
    frames: list of frames (main or shadow)
    from_dirs: current direction order
    to_dirs: desired direction order
    count: frames per direction
    """
    blocks = [frames[i*count:(i+1)*count] for i in range(len(from_dirs))]
    dir_map = {d: i for i, d in enumerate(from_dirs)}
    reordered = []
    for d in to_dirs:
        idx = dir_map[d]
        reordered.extend(blocks[idx])
    return reordered

def extract_inf_block(frames, start, count, skip):
    # For each direction, collect 'count' frames, starting at start + i*skip
    block = []
    for i in range(8):
        for j in range(count):
            idx = start + i*skip + j
            if idx < len(frames):
                block.append(frames[idx])
    return block

def extract_vehicle_block(frames, start, count):
    # For each direction, collect 'count' frames, starting at start + i*count
    block = []
    for i in range(8):
        for j in range(count):
            idx = start + i*count + j
            if idx < len(frames):
                block.append(frames[idx])
    return block

def convert_infantry_to_vehicle(ini_text, frames, shadows):
    ini = parse_ini(ini_text)
    vehicle_ini = {}
    new_frames = []
    new_shadows = []
    DIRECTIONAL_VEHICLE = {"WalkFrames", "StandingFrames", "FiringFrames"}
    for inf_key, (veh_start, veh_count) in INFANTRY_TO_VEHICLE_KEYS.items():
        if inf_key in ini:
            parts = [p.strip() for p in ini[inf_key].split(",") if p.strip()]
            if len(parts) >= 3:
                start = int(parts[0])
                count = int(parts[1])
                skip = int(parts[2])
                block_start = len(new_frames)
                if veh_count in DIRECTIONAL_VEHICLE:
                    # Directional (8 per direction)
                    block = []
                    shadow_block = [] if shadows else None
                    for i in range(8):
                        for j in range(count):
                            idx_ = start + i*skip + j
                            if idx_ < len(frames):
                                block.append(frames[idx_])
                                if shadows:
                                    shadow_block.append(shadows[idx_])
                    reordered = reorder_block(block, INFANTRY_DIRS, VEHICLE_DIRS, count)
                    reordered_shadows = reorder_block(shadow_block, INFANTRY_DIRS, VEHICLE_DIRS, count) if shadows else None
                    new_frames.extend(reordered)
                    if reordered_shadows:
                        new_shadows.extend(reordered_shadows)
                    vehicle_ini[veh_start] = str(block_start)
                    vehicle_ini[veh_count] = str(count)
                else:
                    # Non-directional (DeathFrames, IdleFrames)
                    block = [frames[start + j] for j in range(count) if (start + j) < len(frames)]
                    shadow_block = [shadows[start + j] for j in range(count)] if shadows else None
                    new_frames.extend(block)
                    if shadow_block:
                        new_shadows.extend(shadow_block)
                    vehicle_ini[veh_start] = str(block_start)
                    vehicle_ini[veh_count] = str(count)
    lines = []
    for key in ['StartWalkFrame', 'WalkFrames', 'StartStandFrame', 'StandingFrames', 'StartDeathFrame', 'DeathFrames', 'StartFiringFrame', 'FiringFrames', 'StartIdleFrame', 'IdleFrames']:
        if key in vehicle_ini:
            lines.append(f"{key}={vehicle_ini[key]}")
    return '\n'.join(lines), new_frames, new_shadows

def convert_vehicle_to_infantry(ini_text, frames, shadows):
    ini = parse_ini(ini_text)
    infantry_ini = {}
    new_frames = []
    new_shadows = []
    idx = 0
    for (start_key, count_key), inf_key in VEHICLE_TO_INFANTRY_KEYS.items():
        if start_key in ini and count_key in ini:
            start = int(ini[start_key])
            count = int(ini[count_key])
            if count_key == "IdleFrames":
                # Only IdleFrames is non-directional
                block = [frames[start + j] for j in range(count) if (start + j) < len(frames)]
                shadow_block = [shadows[start + j] for j in range(count)] if shadows else None
                new_frames.extend(block)
                if shadow_block:
                    new_shadows.extend(shadow_block)
                infantry_ini[inf_key] = f"{idx},{count},{count}"
                idx += count
            else:
                # All others are directional (8 per direction)
                block = extract_vehicle_block(frames, start, count)
                shadow_block = extract_vehicle_block(shadows, start, count) if shadows else None
                if inf_key in ("Walk", "FireUp", "Ready"):
                    reordered = reorder_block(block, VEHICLE_DIRS, INFANTRY_DIRS, count)
                    reordered_shadows = reorder_block(shadow_block, VEHICLE_DIRS, INFANTRY_DIRS, count) if shadow_block else None
                    new_frames.extend(reordered)
                    if reordered_shadows:
                        new_shadows.extend(reordered_shadows)
                else:
                    # For non-directional infantry keys, just take the first direction's worth
                    block = block[:count]
                    shadow_block = shadow_block[:count] if shadow_block else None
                    new_frames.extend(block)
                    if shadow_block:
                        new_shadows.extend(shadow_block)
                infantry_ini[inf_key] = f"{idx},{count},{count}"
                idx += 8*count if inf_key in ("Walk", "FireUp", "Ready") else count
    lines = []
    for key in ['Walk', 'Ready', 'Die1', 'FireUp', 'Idle1']:
        if key in infantry_ini:
            lines.append(f"{key}={infantry_ini[key]}")
    return '\n'.join(lines), new_frames, new_shadows 