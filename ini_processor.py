VALID_KEYS = [
    "Ready", "Guard", "Prone", "Walk", "FireUp", "FireProne", "Down", "Crawl", 
    "Up", "Idle1", "Idle2", "Die1", "Die2", "Die3", "Die4", "Die5", 
    "Fly", "Hover", "FireFly", "Tumble", "SecondaryFire", "SecondaryProne", 
    "Deploy", "Deployed", "DeployedFire", "DeployedIdle", "Undeploy", 
    "Paradrop", "Cheer", "Panic", "Shovel", "Carry", "AirDeathStart", 
    "AirDeathFalling", "AirDeathFinish", "Tread", "Swim", "WetAttack", 
    "WetIdle1", "WetIdle2", "WetDie1", "WetDie2", "Struggle"
]

SWIM_RELATED_KEYS = ["WetAttack", "WetIdle1", "WetIdle2", "WetDie1", "WetDie2"]
FLY_RELATED_KEYS = ["Hover", "FireFly", "Tumble", "AirDeathStart", "AirDeathFalling", "AirDeathFinish"]

def parse_ini_data(input_data):
    data = {}
    lines = input_data.split("\n")
    for line in lines:
        line = line.strip()
        if "=" in line:
            key, value = line.split("=", 1)
            # Accept any key, not just those in VALID_KEYS
            data[key.strip()] = value.strip()
    return data

def handle_walk_related_keys(data, added_keys):
    if "Walk" in data:
        walk_values = data["Walk"].split(",")
        walk_value_str = f"{walk_values[0]},1,{walk_values[1]}"
        cheer_value_str = f"{walk_values[0]},{walk_values[1]},0,E"

        if "Ready" not in data and "Guard" not in data:
            data["Ready"] = walk_value_str
            data["Guard"] = walk_value_str
            added_keys.extend(["Ready", "Guard"])

        if "Up" not in data and "Down" not in data:
            data["Up"] = walk_value_str
            data["Down"] = walk_value_str
            added_keys.extend(["Up", "Down"])

        if "Struggle" not in data:
            data["Struggle"] = "0,6,0"
            added_keys.append("Struggle")

        if "Panic" not in data:
            data["Panic"] = data["Walk"]
            added_keys.append("Panic")

        if "Cheer" not in data:
            if "FireUp" in data:
                fireup_values = data["FireUp"].split(",")
                cheer_value_str = f"{fireup_values[0]},{fireup_values[1]},0,E"
            data["Cheer"] = cheer_value_str
            added_keys.append("Cheer")

        if "Crawl" not in data:
            data["Crawl"] = data["Walk"]
            added_keys.append("Crawl")

        if "Crawl" in data and "Prone" not in data:
            crawl_values = data["Crawl"].split(",")
            data["Prone"] = f"{crawl_values[0]},1,{crawl_values[1]}"
            added_keys.append("Prone")

    if "Ready" in data and "Guard" not in data:
        data["Guard"] = data["Ready"]
        added_keys.append("Guard")
    if "Guard" in data and "Ready" not in data:
        data["Ready"] = data["Guard"]
        added_keys.append("Ready")

    if "Up" in data and "Down" not in data:
        data["Down"] = data["Up"]
        added_keys.append("Down")
    if "Down" in data and "Up" not in data:
        data["Up"] = data["Down"]
        added_keys.append("Up")

def handle_crawl_prone(data, added_keys):
    if "Crawl" in data and "Prone" not in data:
        crawl_values = data["Crawl"].split(",")
        data["Prone"] = f"{crawl_values[0]},1,{crawl_values[1]}"
        added_keys.append("Prone")

def handle_fire_secondary_prone(data, added_keys):
    if "FireProne" not in data and "FireUp" in data:
        fireup_values = data["FireUp"].split(",")
        fireprone_value_str = f"{fireup_values[0]},1,{fireup_values[1]}"
        data["FireProne"] = fireprone_value_str
        added_keys.append("FireProne")

    if "SecondaryProne" not in data and "SecondaryFire" in data:
        values = data["SecondaryFire"].split(",")
        if len(values) > 1:
            values[1] = "1"
        data["SecondaryProne"] = ",".join(values)
        added_keys.append("SecondaryProne")

def handle_idle_keys(data, added_keys):
    if "Idle1" in data:
        idle1_values = data["Idle1"].split(",")
        data["Idle1"] = f"{idle1_values[0]},{idle1_values[1]},0,E"
    if "Idle2" not in data and "Idle1" in data:
        idle1_values = data["Idle1"].split(",")
        data["Idle2"] = f"{idle1_values[0]},{idle1_values[1]},0,W"
        added_keys.append("Idle2")

def handle_swim_related_keys(data, added_keys):
    if "Swim" in data:
        values = data["Swim"].split(",")
        for key in SWIM_RELATED_KEYS:
            if key not in data:
                if key in ["WetIdle1", "WetIdle2"]:
                    data[key] = f"{values[0]},{values[1]},0," + ("E" if key == "WetIdle1" else "W")
                elif key in ["WetDie1", "WetDie2"]:
                    data[key] = f"{values[0]},{values[1]},0"
                added_keys.append(key)
        if "Tread" not in data:
            data["Tread"] = data["Swim"]
            added_keys.append("Tread")
    else:
        for key in SWIM_RELATED_KEYS:
            data.pop(key, None)

def handle_fly_related_keys(data, added_keys):
    if "Fly" in data:
        fly_values = data["Fly"].split(",")
        for key in FLY_RELATED_KEYS:
            if key not in data:
                if key == "Tumble":
                    data[key] = f"{fly_values[0]},{fly_values[1]},0"
                else:
                    data[key] = data["Fly"]
                added_keys.append(key)
    else:
        for key in FLY_RELATED_KEYS:
            data.pop(key, None)

def handle_deploy_related_keys(data, added_keys):
    if "Deploy" in data:
        deploy_values = data["Deploy"].split(",")
        deploy_value_str = f"{deploy_values[0]},{deploy_values[1]},0"

        if "Deployed" not in data:
            deployed_first_value = int(deploy_values[0]) + int(deploy_values[1]) - 1
            data["Deployed"] = f"{deployed_first_value},1,0"
            added_keys.append("Deployed")

        if "DeployedFire" not in data:
            if "FireUp" in data:
                data["DeployedFire"] = data["FireUp"]
            else:
                data["DeployedFire"] = data["Deploy"]
            added_keys.append("DeployedFire")

        if "DeployedIdle" not in data:
            data["DeployedIdle"] = "0,0,0"
            added_keys.append("DeployedIdle")

        if "Undeploy" not in data:
            data["Undeploy"] = data["Deploy"]
            added_keys.append("Undeploy")

def handle_die_keys(data, added_keys):
    for key in VALID_KEYS:
        if key.startswith("Die") and key in data:
            values = data[key].split(",")
            if len(values) < 3:
                values.append("0")
            data[key] = ",".join(values)
    if "Die1" in data:
        die1_value = data["Die1"]
        for i in range(2, 6):
            die_key = f"Die{i}"
            if die_key not in data:
                data[die_key] = die1_value
                added_keys.append(die_key)

def ensure_formatting_consistency(data):
    for key, value in data.items():
        if key not in ["Idle1", "Idle2", "Die1", "Die2", "Die3", "Die4", "Die5"]:
            values = value.split(",")
            if len(values) == 2:
                values.append(values[1])
            data[key] = ",".join(values)

def process_ini_data(input_data):
    data = parse_ini_data(input_data)
    added_keys = []
    handle_walk_related_keys(data, added_keys)
    handle_crawl_prone(data, added_keys)
    handle_fire_secondary_prone(data, added_keys)
    handle_idle_keys(data, added_keys)
    handle_swim_related_keys(data, added_keys)
    handle_fly_related_keys(data, added_keys)
    handle_deploy_related_keys(data, added_keys)
    handle_die_keys(data, added_keys)
    ensure_formatting_consistency(data)

    output_lines = []
    for key in VALID_KEYS:
        if key == "; YR Only from here:":
            output_lines.append("; YR Only from here:\n")
        elif key in data:
            output_lines.append(f"{key}={data[key]}")

    return "\n".join(output_lines), added_keys

def infantry_ini_to_vehicle_ini(input_data):
    # Parse infantry INI and output vehicle INI as string
    data = parse_ini_data(input_data) if isinstance(input_data, str) else input_data
    DIR_ORDER = ["N", "NW", "W", "SW", "S", "SE", "E", "NE"]
    VEHICLE_DIR_ORDER = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    mapping = {
        'Walk':    ('StartWalkFrame', 'WalkFrames'),
        'Ready':   ('StartStandFrame', 'StandingFrames'),
        'Die1':    ('StartDeathFrame', 'DeathFrames'),
        'FireUp':  ('StartFiringFrame', 'FiringFrames'),
        'Idle1':   ('StartIdleFrame', 'IdleFrames'),
    }
    vehicle_ini = {}
    for inf_key, (veh_start, veh_count) in mapping.items():
        if inf_key in data:
            parts = [p.strip() for p in data[inf_key].split(",") if p.strip()]
            if len(parts) >= 3:
                start = int(parts[0])
                count = int(parts[1])
                skip = int(parts[2])
                if inf_key in ("Walk", "FireUp"):  # Directional
                    # For each direction in VEHICLE_DIR_ORDER, find the corresponding block in DIR_ORDER
                    blocks = []
                    for vdir, vname in enumerate(VEHICLE_DIR_ORDER):
                        inf_dir = DIR_ORDER.index(vname)
                        block_start = start + inf_dir * skip
                        blocks.append(block_start)
                    # The vehicle format expects the first block's start and the count per direction
                    vehicle_ini[veh_start] = str(blocks[0])
                    vehicle_ini[veh_count] = str(count)
                else:
                    vehicle_ini[veh_start] = str(start)
                    vehicle_ini[veh_count] = str(count)
    # Format as text
    lines = []
    for key in ['StartWalkFrame', 'WalkFrames', 'StartStandFrame', 'StandingFrames', 'StartDeathFrame', 'DeathFrames', 'StartFiringFrame', 'FiringFrames', 'StartIdleFrame', 'IdleFrames']:
        if key in vehicle_ini:
            lines.append(f"{key}={vehicle_ini[key]}")
    return "\n".join(lines)

def vehicle_ini_to_infantry_ini(input_data):
    # Parse vehicle INI and output infantry INI as string
    lines = input_data.split("\n") if isinstance(input_data, str) else input_data
    ini_dict = {}
    for line in lines:
        if '=' in line:
            k, v = line.split('=', 1)
            ini_dict[k.strip()] = v.strip()
    # Map vehicle keys to infantry keys
    mapping = {
        ('StartWalkFrame', 'WalkFrames'): 'Walk',
        ('StartStandFrame', 'StandingFrames'): 'Ready',
        ('StartDeathFrame', 'DeathFrames'): 'Die1',
        ('StartFiringFrame', 'FiringFrames'): 'FireUp',
        ('StartIdleFrame', 'IdleFrames'): 'Idle1',
    }
    infantry_ini = {}
    for (start_key, count_key), inf_key in mapping.items():
        if start_key in ini_dict and count_key in ini_dict:
            infantry_ini[inf_key] = f"{ini_dict[start_key]},{ini_dict[count_key]},8"
    # Format as text
    lines = []
    for key in ['Walk', 'Ready', 'Die1', 'FireUp', 'Idle1']:
        if key in infantry_ini:
            lines.append(f"{key}={infantry_ini[key]}")
    return "\n".join(lines)

def build_frame_grid(data, mode, facings, total_frames):
    """
    Returns:
        frames_grid: {animation: {direction: [frame indices]}}
        shadows_grid: {animation: {direction: [shadow frame indices]}}
    """
    frames_grid = {}
    shadows_grid = {}
    if mode == 'Infantry':
        DIR_ORDER = ["N", "NW", "W", "SW", "S", "SE", "E", "NE"]
        for anim, value in data.items():
            parts = [p.strip() for p in value.split(",") if p.strip()]
            if len(parts) < 3:
                continue
            start = int(parts[0])
            count = int(parts[1])
            skip = int(parts[2])
            frames_grid[anim] = {}
            shadows_grid[anim] = {}
            for i, dir_name in enumerate(DIR_ORDER):
                dir_frames = []
                shadow_frames = []
                for j in range(count):
                    idx = start + i * skip + j
                    dir_frames.append(idx)
                    # Shadow frame index is offset by half the total frames
                    shadow_idx = idx + (total_frames // 2)
                    shadow_frames.append(shadow_idx)
                frames_grid[anim][dir_name] = dir_frames
                shadows_grid[anim][dir_name] = shadow_frames
    elif mode == 'Vehicle':
        # Directions are clockwise, facings can be 8/16/32/64
        VEHICLE_DIR_ORDER = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        vehicle_anims = [
            ("Standing", "StartStandFrame", "StandingFrames"),
            ("Walk", "StartWalkFrame", "WalkFrames"),
            ("Death", "StartDeathFrame", "DeathFrames"),
            ("Firing", "StartFiringFrame", "FiringFrames"),
            ("Idle", "StartIdleFrame", "IdleFrames"),
        ]
        for anim, start_key, count_key in vehicle_anims:
            if start_key in data and count_key in data:
                start = int(data[start_key])
                count = int(data[count_key])
                frames_grid[count_key] = {}
                shadows_grid[count_key] = {}
                for i in range(facings):
                    if facings == 8:
                        dir_name = VEHICLE_DIR_ORDER[i]
                    else:
                        dir_name = f"D{i+1}"  # D1, D2, ... for 16/32/64 facings
                    dir_frames = []
                    shadow_frames = []
                    for j in range(count):
                        idx = start + i * count + j
                        dir_frames.append(idx)
                        shadow_idx = idx + (total_frames // 2)
                        shadow_frames.append(shadow_idx)
                    frames_grid[count_key][dir_name] = dir_frames
                    shadows_grid[count_key][dir_name] = shadow_frames
    return frames_grid, shadows_grid