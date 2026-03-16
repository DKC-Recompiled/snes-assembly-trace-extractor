#!/usr/bin/env python3
"""
DKC1 — Log tracer converter to ASM
==================================
Read txt files from folder traces/
Generate asm files in src/Bank_XX/
Usage :
    python3 tools/trace_to_asm.py
"""

import re
import sys
from pathlib import Path
from collections import Counter, OrderedDict, defaultdict

# /-----/ Paths /-----/

REPO_ROOT  = Path(__file__).parent.parent   # dkc-decompiled-code/
TRACES_DIR = REPO_ROOT / 'traces'
SRC_DIR    = REPO_ROOT / 'src'

# /-----/ Pattern parsing /-----/

PAT_65816 = re.compile(
    r'^([0-9A-F]{6})\s+(\S.*?)\s{2,}'
    r'A:([0-9A-F]{4}) X:([0-9A-F]{4}) Y:([0-9A-F]{4}) '
    r'S:[0-9A-F]{4} D:[0-9A-F]{4} DB:[0-9A-F]{2} '
    r'P:(\S+)'
)
PAT_SPC700 = re.compile(
    r'^([0-9A-F]{4})\s+(\S.*?)\s{2,}'
    r'A:[0-9A-F]{2} X:[0-9A-F]{2} Y:[0-9A-F]{2} '
    r'S:[0-9A-F]{2} P:(\S+)'
)

# /-----/ hardware registers SNES /-----/

HW = {
    0x2100:'INIDISP', 0x2101:'OBSEL',    0x2102:'OAMADDL', 0x2103:'OAMADDH',
    0x2104:'OAMDATA', 0x2105:'BGMODE',   0x2106:'MOSAIC',  0x2107:'BG1SC',
    0x2108:'BG2SC',   0x2109:'BG3SC',    0x210A:'BG4SC',   0x210B:'BG12NBA',
    0x210C:'BG34NBA', 0x210D:'BG1HOFS',  0x210E:'BG1VOFS', 0x210F:'BG2HOFS',
    0x2110:'BG2VOFS', 0x2111:'BG3HOFS',  0x2112:'BG3VOFS', 0x2115:'VMAIN',
    0x2116:'VMADDL',  0x2117:'VMADDH',   0x2118:'VMDATAL', 0x2119:'VMDATAH',
    0x211A:'M7SEL',   0x211B:'M7A',      0x211C:'M7B',
    0x2121:'CGADD',   0x2122:'CGDATA',   0x2123:'W12SEL',  0x2124:'W34SEL',
    0x2130:'CGWSEL',  0x2131:'CGADSUB',  0x2132:'COLDATA', 0x2133:'SETINI',
    0x4016:'JOYA',    0x4017:'JOYB',
    0x4200:'NMITIMEN',0x4201:'WRIO',     0x4202:'WRMPYA',  0x4203:'WRMPYB',
    0x4204:'WRDIVL',  0x4205:'WRDIVH',   0x4206:'WRDIVB',
    0x420B:'MDMAEN',  0x420C:'HDMAEN',   0x420D:'MEMSEL',
    0x4300:'DMAP0',   0x4301:'BBAD0',    0x4302:'A1T0L',   0x4304:'A1B0',
    0x4305:'DAS0L',
    0x2180:'WMDATA',  0x2181:'WMADDL',   0x2182:'WMADDM',  0x2183:'WMADDH',
}

def load_traces():
    """Read .txt from traces folder and return uniques instructions."""
    files = sorted(TRACES_DIR.glob('*.txt'))
    if not files:
        print(f"[!] No .txt found in {TRACES_DIR}")
        print(f"    Export log from Mesen-S and place it in traces/")
        sys.exit(1)

    seen   = OrderedDict()
    hits   = Counter()
    seen_s = OrderedDict()
    hits_s = Counter()

    for file in files:
        taille = file.stat().st_size // 1024
        print(f"  Lecture {file.name}  ({taille} Ko)")
        for line in file.open(encoding='utf-8', errors='replace'):
            line = line.rstrip()
            m = PAT_65816.match(line)
            if m:
                addr = m.group(1)
                hits[addr] += 1
                if addr not in seen:
                    seen[addr] = {'instr': m.group(2).strip(), 'P': m.group(6)}
                continue
            m = PAT_SPC700.match(line)
            if m:
                addr = m.group(1)
                hits_s[addr] += 1
                if addr not in seen_s:
                    seen_s[addr] = m.group(2).strip()

    return seen, hits, seen_s, hits_s

def comment_instr(instr, hits_addr):
    """Generate comment from a instruction."""

    mnem = instr.split()[0]
    parts = []

    # Hardware register name
    m = re.search(r'\$([0-9A-F]{4})', instr)
    if m:
        reg = int(m.group(1), 16)
        if reg in HW:
            parts.append(HW[reg])

    # Change 8/16 bits mode
    if mnem in ('REP', 'SEP'):
        m2 = re.search(r'#\$([0-9A-F]{2})', instr)
        if m2:
            v = int(m2.group(1), 16)
            taille = '16' if mnem == 'REP' else '8'
            if v & 0x20: parts.append(f'A={taille}b')
            if v & 0x10: parts.append(f'X/Y={taille}b')

    # Loop detected
    if hits_addr > 1:
        parts.append(f'loop x{hits_addr} in traces')

    return ('  ; ' + ', '.join(parts)) if parts else ''

def write_bank(bank_id, adresses, seen, hits):
    """Write src/Bank_XX/Bank_XX.asm"""

    folder_path = SRC_DIR / f'Bank_{bank_id}'
    folder_path.mkdir(parents=True, exist_ok=True)
    file = folder_path / f'Bank_{bank_id}.asm'

    content = [
        f'; DKC1 (SNES) — Bank ${bank_id}',
        f'; {len(adresses)} uniques instructions',
        f'; Generated from traces — Do not modify it',
        f'; To write comments: Bank_{bank_id}_annotated.asm in the folder',
        '',
    ]

    prev = None
    for addr in adresses:
        addr_int = int(addr, 16)
        d = seen[addr]

        if prev is not None and addr_int > prev + 8:
            content.append(f'')
            content.append(f'; --- gap ${addr_int - prev:04X} bytes (non traced) ---')
            content.append(f'')

        com = comment_instr(d['instr'], hits[addr])
        content.append(f'CODE_{addr}:  {d["instr"]:<36}{com}')
        prev = addr_int

    file.write_text('\n'.join(content) + '\n')
    return file

def write_spc(seen_s, hits_s):
    """Write src/SPC700/SPC700.asm"""

    folder = SRC_DIR / 'SPC700'
    folder.mkdir(exist_ok=True)
    file = folder / 'SPC700.asm'

    content = [
        '; DKC1 — SPC700 (CPU audio Sony)',
        '; Boot ROM standard, do not modify',
        '',
    ]
    for addr, instr in seen_s.items():
        c = hits_s[addr]
        com = f'  ; loop x{c} in traces' if c > 1 else ''
        content.append(f'SPC_{addr}:  {instr:<30}{com}')

    file.write_text('\n'.join(content) + '\n')
    return file

def trace_to_asm():

    print(f'Reading in {REPO_ROOT}/traces')
    seen, hits, seen_s, hits_s = load_traces()

    total_lines_nb   = sum(hits.values())
    unique_lines_nb = len(seen)
    redond_lines_nb  = total_lines_nb - unique_lines_nb
    banks   = sorted(set(a[:2] for a in seen))

    # /------------------------------/

    print(f'')
    print(f'Results :')
    print(f'    65c816  : {total_lines_nb} lines -> {unique_lines_nb} uniques ({redond_lines_nb} double code deleted)')
    print(f'    SPC700  : {sum(hits_s.values())} lines -> {len(seen_s)} uniques')
    print(f'    Banks : {banks}')

    # /------------------------------/

    print(f'')
    print(f'Writing in {REPO_ROOT}/src')

    by_bank = defaultdict(list)
    for addr in seen:
        by_bank[addr[:2]].append(addr)

    for bank, addrs in sorted(by_bank.items()):
        f = write_bank(bank, addrs, seen, hits)
        print(f'    -> {f.relative_to(REPO_ROOT)}  ({len(addrs)} instrs)')

    if seen_s:
        f = write_spc(seen_s, hits_s)
        print(f'    -> {f.relative_to(REPO_ROOT)}  ({len(seen_s)} instrs)')


def main():
    print(f'Starting cleaning and exporting code : {REPO_ROOT}')
    print(f'')

    trace_to_asm()

    print(f'')
    print(f'Finished')

if __name__ == '__main__':
    main()
