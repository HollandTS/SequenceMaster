const VALID_KEYS = [
    "Ready", "Guard", "Prone", "Walk", "FireUp", "FireProne", "Down", "Crawl",
    "Up", "Idle1", "Idle2", "Die1", "Die2", "Die3", "Die4", "Die5",
    "Fly", "Hover", "FireFly", "Tumble", "SecondaryFire", "SecondaryProne",
    "Deploy", "Deployed", "DeployedFire", "DeployedIdle", "Undeploy",
    "Paradrop", "Cheer", "Panic", "Shovel", "Carry", "AirDeathStart",
    "AirDeathFalling", "AirDeathFinish", "Tread", "Swim", "WetAttack",
    "WetIdle1", "WetIdle2", "WetDie1", "WetDie2", "Struggle"
];

function parseIniData(inputData) {
    const data = {};
    const lines = inputData.split("\n");
    lines.forEach(line => {
        line = line.trim();
        if (line.includes("=")) {
            const [key, value] = line.split("=");
            if (VALID_KEYS.includes(key.trim())) {
                data[key.trim()] = value.trim();
            }
        }
    });
    return data;
}

function processInput() {
    const inputText = document.getElementById("inputText").value;
    if (!inputText) {
        alert("Please paste INI data before processing.");
        return;
    }
    const data = parseIniData(inputText);
    const addedKeys = [];
    handleWalkRelatedKeys(data, addedKeys);
    handleCrawlProne(data, addedKeys);
    handleFireSecondaryProne(data, addedKeys);
    handleIdleKeys(data, addedKeys);
    handleSwimRelatedKeys(data, addedKeys);
    handleFlyRelatedKeys(data, addedKeys);
    handleDeployRelatedKeys(data, addedKeys);
    handleDieKeys(data, addedKeys);
    ensureFormattingConsistency(data);

    const outputLines = [];
    VALID_KEYS.forEach(key => {
        if (data[key]) {
            outputLines.push(`${key}=${data[key]}`);
        }
    });

    document.getElementById("outputText").value = outputLines.join("\n");
}

function handleWalkRelatedKeys(data, addedKeys) {
    if (data["Walk"]) {
        const walkValues = data["Walk"].split(",");
        const walkValueStr = `${walkValues[0]},1,${walkValues[1]}`;
        const cheerValueStr = `${walkValues[0]},${walkValues[1]},0,E`;

        if (!data["Ready"] && !data["Guard"]) {
            data["Ready"] = walkValueStr;
            data["Guard"] = walkValueStr;
            addedKeys.push("Ready", "Guard");
        }

        if (!data["Up"] && !data["Down"]) {
            data["Up"] = walkValueStr;
            data["Down"] = walkValueStr;
            addedKeys.push("Up", "Down");
        }

        if (!data["Struggle"]) {
            data["Struggle"] = "0,6,0";
            addedKeys.push("Struggle");
        }

        if (!data["Panic"]) {
            data["Panic"] = data["Walk"];
            addedKeys.push("Panic");
        }

        if (!data["Cheer"]) {
            if (data["FireUp"]) {
                const fireupValues = data["FireUp"].split(",");
                cheerValueStr = `${fireupValues[0]},${fireupValues[1]},0,E`;
            }
            data["Cheer"] = cheerValueStr;
            addedKeys.push("Cheer");
        }

        if (!data["Crawl"]) {
            data["Crawl"] = data["Walk"];
            addedKeys.push("Crawl");
        }

        if (data["Crawl"] && !data["Prone"]) {
            const crawlValues = data["Crawl"].split(",");
            data["Prone"] = `${crawlValues[0]},1,${crawlValues[1]}`;
            addedKeys.push("Prone");
        }
    }

    if (data["Ready"] && !data["Guard"]) {
        data["Guard"] = data["Ready"];
        addedKeys.push("Guard");
    }
    if (data["Guard"] && !data["Ready"]) {
        data["Ready"] = data["Guard"];
        addedKeys.push("Ready");
    }

    if (data["Up"] && !data["Down"]) {
        data["Down"] = data["Up"];
        addedKeys.push("Down");
    }
    if (data["Down"] && !data["Up"]) {
        data["Up"] = data["Down"];
        addedKeys.push("Up");
    }
}

function handleCrawlProne(data, addedKeys) {
    if (data["Crawl"] && !data["Prone"]) {
        const crawlValues = data["Crawl"].split(",");
        data["Prone"] = `${crawlValues[0]},1,${crawlValues[1]}`;
        addedKeys.push("Prone");
    }
}

function handleFireSecondaryProne(data, addedKeys) {
    if (!data["FireProne"] && data["FireUp"]) {
        const fireupValues = data["FireUp"].split(",");
        const fireproneValueStr = `${fireupValues[0]},1,${fireupValues[1]}`;
        data["FireProne"] = fireproneValueStr;
        addedKeys.push("FireProne");
    }

    if (!data["SecondaryProne"] && data["SecondaryFire"]) {
        const values = data["SecondaryFire"].split(",");
        if (values.length > 1) {
            values[1] = "1";
        }
        data["SecondaryProne"] = values.join(",");
        addedKeys.push("SecondaryProne");
    }
}

function handleIdleKeys(data, addedKeys) {
    if (data["Idle1"]) {
        const idle1Values = data["Idle1"].split(",");
        data["Idle1"] = `${idle1Values[0]},${idle1Values[1]},0,E`;
    }
    if (!data["Idle2"] && data["Idle1"]) {
        const idle1Values = data["Idle1"].split(",");
        data["Idle2"] = `${idle1Values[0]},${idle1Values[1]},0,W`;
        addedKeys.push("Idle2");
    }
}

const SWIM_RELATED_KEYS = ["WetAttack", "WetIdle1", "WetIdle2", "WetDie1", "WetDie2"];
function handleSwimRelatedKeys(data, addedKeys) {
    if (data["Swim"]) {
        const values = data["Swim"].split(",");
        SWIM_RELATED_KEYS.forEach(key => {
            if (!data[key]) {
                if (key === "WetIdle1" || key === "WetIdle2") {
                    data[key] = `${values[0]},${values[1]},0,${key === "WetIdle1" ? "E" : "W"}`;
                } else if (key === "WetDie1" || key === "WetDie2") {
                    data[key] = `${values[0]},${values[1]},0`;
                }
                addedKeys.push(key);
            }
        });
        if (!data["Tread"]) {
            data["Tread"] = data["Swim"];
            addedKeys.push("Tread");
        }
    } else {
        SWIM_RELATED_KEYS.forEach(key => {
            delete data[key];
        });
    }
}

const FLY_RELATED_KEYS = ["Hover", "FireFly", "Tumble", "AirDeathStart", "AirDeathFalling", "AirDeathFinish"];
function handleFlyRelatedKeys(data, addedKeys) {
    if (data["Fly"]) {
        const flyValues = data["Fly"].split(",");
        FLY_RELATED_KEYS.forEach(key => {
            if (!data[key]) {
                data[key] = key === "Tumble" ? `${flyValues[0]},${flyValues[1]},0` : data["Fly"];
                addedKeys.push(key);
            }
        });
    } else {
        FLY_RELATED_KEYS.forEach(key => {
            delete data[key];
        });
    }
}

function handleDeployRelatedKeys(data, addedKeys) {
    if (data["Deploy"]) {
        const deployValues = data["Deploy"].split(",");
        const deployValueStr = `${deployValues[0]},${deployValues[1]},0`;

        if (!data["Deployed"]) {
            const deployedFirstValue = parseInt(deployValues[0]) + parseInt(deployValues[1]) - 1;
            data["Deployed"] = `${deployedFirstValue},1,0`;
            addedKeys.push("Deployed");
        }

        if (!data["DeployedFire"]) {
            data["DeployedFire"] = data["FireUp"] ? data["FireUp"] : data["Deploy"];
            addedKeys.push("DeployedFire");
        }

        if (!data["DeployedIdle"]) {
            data["DeployedIdle"] = "0,0,0";
            addedKeys.push("DeployedIdle");
        }

        if (!data["Undeploy"]) {
            data["Undeploy"] = data["Deploy"];
            addedKeys.push("Undeploy");
        }
    }
}

function handleDieKeys(data, addedKeys) {
    VALID_KEYS.forEach(key => {
        if (key.startsWith("Die") && data[key]) {
            const values = data[key].split(",");
            if (values.length < 3) {
                values.push("0");
            }
            data[key] = values.join(",");
        }
    });
    if (data["Die1"]) {
        const die1Value = data["Die1"];
        for (let i = 2; i <= 5; i++) {
            const dieKey = `Die${i}`;
            if (!data[dieKey]) {
                data[dieKey] = die1Value;
                addedKeys.push(dieKey);
            }
        }
    }
}

function ensureFormattingConsistency(data) {
    Object.keys(data).forEach(key => {
        if (!["Idle1", "Idle2", "Die1", "Die2", "Die3", "Die4", "Die5"].includes(key)) {
            const values = data[key].split(",");
            if (values.length === 2) {
                values.push(values[1]);
            }
            data[key] = values.join(",");
        }
    });
}