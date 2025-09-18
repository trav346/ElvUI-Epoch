#!/usr/bin/env python3
import re

# Read the file
with open('LibHealComm-4.0.lua', 'r') as f:
    content = f.read()
    lines = content.split('\n')

# WotLK spells to remove (with their spell IDs)
wotlk_spells = {
    # Druid
    'WildGrowth': '48438',
    'Nourish': '50464',  
    'MasterShapeshifter': '48411',
    'Genesis': '57810',
    'NaturesSplendor': '57865',
    
    # Paladin
    'TouchedbytheLight': '53592',
    'BeaconofLight': '53563',
    'Divinity': '63646',
    
    # Priest
    'Penance': '53007',
    'Grace': '47517',
    'DivineProvidence': '47567',
    'EmpoweredRenew': '63534',
    'TwinDisciplines': '47586',
    
    # Shaman
    'Riptide': '61295',
    'Earthliving': '52000',
    'TidalWaves': '51566'
}

# Track lines to remove
lines_to_remove = []

# Find variable declarations
for spell_name, spell_id in wotlk_spells.items():
    for i, line in enumerate(lines):
        # Match local variable declarations
        if f'local {spell_name} = GetSpellInfo({spell_id})' in line:
            lines_to_remove.append(i)
            print(f"Found declaration of {spell_name} at line {i+1}")
        
        # Match spell/hot/talent data definitions
        if f'spellData[{spell_name}]' in line or f'hotData[{spell_name}]' in line or f'talentData[{spell_name}]' in line:
            lines_to_remove.append(i)
            print(f"Found data definition for {spell_name} at line {i+1}")
            
        # Match comments about these spells
        if f'-- {spell_name.replace("o", " o").replace("W", " W")}' in line or spell_name in line and line.strip().startswith('--'):
            lines_to_remove.append(i)
            print(f"Found comment about {spell_name} at line {i+1}")

# Find blocks that reference these spells
i = 0
while i < len(lines):
    line = lines[i]
    
    # Check for spell-specific blocks
    for spell_name in wotlk_spells.keys():
        # Conditional blocks
        if f'spellName == {spell_name}' in line or f'unitHasAura(unit, {spell_name})' in line:
            # Find the entire if/elseif block
            start = i
            if 'elseif' in lines[i]:
                # Find the end of this elseif block
                end = i + 1
                indent = len(lines[i]) - len(lines[i].lstrip())
                while end < len(lines):
                    if lines[end].strip() and (lines[end].startswith('\t' * (indent//4) + 'elseif') or 
                                              lines[end].startswith('\t' * (indent//4) + 'else') or
                                              lines[end].startswith('\t' * (indent//4) + 'end')):
                        break
                    end += 1
                for j in range(start, end):
                    lines_to_remove.append(j)
                print(f"Found elseif block for {spell_name} at lines {start+1}-{end}")
            elif 'if' in lines[i]:
                # Find matching end
                end = i + 1
                if_count = 1
                while end < len(lines) and if_count > 0:
                    if 'if ' in lines[end] and 'elseif' not in lines[end]:
                        if_count += 1
                    elif lines[end].strip() == 'end' or lines[end].strip().startswith('end '):
                        if_count -= 1
                    end += 1
                for j in range(start, end):
                    lines_to_remove.append(j)
                print(f"Found if block for {spell_name} at lines {start+1}-{end}")
    i += 1

# Sort and deduplicate
lines_to_remove = sorted(set(lines_to_remove))

# Remove lines (in reverse order to maintain indices)
for i in reversed(lines_to_remove):
    if i < len(lines):
        print(f"Removing line {i+1}: {lines[i][:80]}...")
        del lines[i]

# Clean up the result
result = []
prev_blank = False
for line in lines:
    # Skip multiple blank lines
    if line.strip() == '':
        if not prev_blank:
            result.append(line)
            prev_blank = True
    else:
        result.append(line)
        prev_blank = False

# Write the modified file
with open('LibHealComm-4.0-cleaned.lua', 'w') as f:
    f.write('\n'.join(result))

print(f"\nRemoved {len(lines_to_remove)} lines")
print("Output written to LibHealComm-4.0-cleaned.lua")