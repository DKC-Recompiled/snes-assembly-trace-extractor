# SNES Assembly extractor 

This tool converts [Mesen](https://github.com/SourMesen/Mesen2) emulator `.txt` log traces, into structured `.asm` files.

It handles code repetitions and SPC700 audio code.

This was developed using [Mesen](https://github.com/SourMesen/Mesen2), but I guess any `.txt` log traces from any emulator would work.
This tool has no dependencies with Mesen.

> [!IMPORTANT]
> **No rom, assets, nor extracted code in this repository**.

## How to use it ?

**1. Code capture from Mesen-S (or any emulator)**

```txt
Mesen-S -> Debug -> Trace Logger -> Log to file
Launch Game -> Stop -> Save traces as .txt
```

**2. Place logs in `traces/`**

```txt
traces/super_mario_world_assembly_logs.txt
```

**3. Run script**

```bash
bash run.sh
```

This will reads **all** `.txt` from `traces/`, delete double code, and generate `.asm` files in `src/`.