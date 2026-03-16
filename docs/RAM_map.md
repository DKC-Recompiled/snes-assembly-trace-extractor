# DKC1 — RAM Memory Map (WRAM $7E0000–$7FFFFF)

Source : `RAM_Map_DKC1.asm` from Yoshifanatic1 framework, using Mesen-S trace log.

## Page zéro ($0000–$00FF) — Direct Page

| Adresse | Nom | Description |
|---|---|---|
| $0000–$003D | — | Non documenté |
| $003E–$003F | `EntranceID` | ID de l'entrée/salle actuelle |
| $0082–$0083 | `NorSpr_CurrentIndex` | Index sprite courant |
| $008E–$008F | `OAMIndex` | Index dans le buffer OAM |

## Page 2 ($0200–$03FF) — OAM Buffer

| Adresse | Taille | Description |
|---|---|---|
| $0200 | 512 o | OAM Buffer basse (128 sprites × 4 octets : X, Y, Tile, Prop) |
| $0400 | 32 o  | OAM Buffer haute (bits de taille/position X bit 8) |

## Contrôles ($0500–$051F)

| Adresse | Nom | Description |
|---|---|---|
| $0500–$0501 | `HeldButtons_P1` | Boutons tenus joueur 1 |
| $0502–$0503 | `HeldButtons_P2` | Boutons tenus joueur 2 |
| $0504–$0505 | `PressedButtons_P1` | Boutons pressés ce frame P1 |
| $0506–$0507 | `PressedButtons_P2` | Boutons pressés ce frame P2 |
| $050E–$050F | `HeldButtons` | Boutons tenus (joueur actif) |
| $0510–$0511 | `PressedButtons` | Boutons pressés (joueur actif) |
| $051A | `ScreenDisplay` | Copie de INIDISP ($2100) |

## État joueur ($056F–$058F)

| Adresse | Nom | Description |
|---|---|---|
| $056F–$0570 | `CurrentKong` | Kong actif (0=DK, 1=Diddy) |
| $0571 | `WinkyTokenCount` | Jetons Winky collectés |
| $0572 | `ExpressoTokenCount` | Jetons Expresso collectés |
| $0573 | `RambiTokenCount` | Jetons Rambi collectés |
| $0574 | `EnguardeTokenCount` | Jetons Enguarde collectés |
| $0575–$0576 | `CurrentLifeCount` | Vies actuelles |
| $0577–$0578 | `DisplayedLifeCount` | Vies affichées (peut différer pendant animation) |
| $057B–$057C | `CurrentBananaCount` | Bananes collectées |
| $057F–$0580 | `CollectedKONGLetters` | Lettres KONG collectées (bits) |

## Sprites — tableaux SoA ($0B19–$1699)

Le système de sprites utilise une structure **SoA (Structure of Arrays)** :
chaque propriété a son propre tableau de 52 slots (un par sprite actif).
Chaque slot = 2 octets. Stride entre slots = 2.

| Base | Nom | Description |
|---|---|---|
| $0B19 | `NorSpr_XPos` | Position X (tableau 52 entrées) |
| $0BC1 | `NorSpr_YPos` | Position Y |
| $0B8D | `NorSpr_OAMZPos` | Profondeur Z pour le tri OAM |
| $0D11 | `NorSpr_CurrentPose` | Pose affichée actuellement |
| $0D45 | `NorSpr_SpriteID` | Type de sprite (voir Misc_Defines) |
| $0AE5 | `NorSpr_DisplayedPose` | Pose dans l'animation |
| $0E89 | `NorSpr_XSpeed` | Vitesse horizontale |
| $0EF1 | `NorSpr_YSpeed` | Vitesse verticale |
| $10D1 | `NorSpr_AnimationID` | Animation courante |
| $1105 | `NorSpr_AnimTimer` | Timer d'affichage de la pose |
| $1139 | `NorSpr_AnimSpeed` | Vitesse d'animation |
| $116D | `NorSpr_AnimScriptIndex` | Index dans le script d'animation |

## Caméra ($1A4C–$1A63)

| Adresse | Nom | Description |
|---|---|---|
| $1A4C–$1A4D | `CameraYPos` | Position caméra Y |
| $1A62–$1A63 | `CameraXPos` | Position caméra X |

## Buffers étendus

| Adresse | Nom | Description |
|---|---|---|
| $7E79FC | `DecompressionBuffer` | Buffer décompression GFX |
| $7F2779 | `SpritePaletteBuffer` | Buffer palettes sprites |
