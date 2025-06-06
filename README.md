# Siege extra info

Script that hooks into Overwolf's Rainbow Six Tracker and displays extra info:
- players' total lifetime matches, top rank, ubisoft ID
- which players have been previously seen playing together
- round-by-round KDA and your team's picked operators 


```sh
python script.py
```

requires playwright to get squad info

```2025-06-02 21:21:57,065
== Players ==
Maxim_Marmelado                     -  332 matches, BRONZE IV    4a76ff18-a197-4cee-aa77-1b21b729ce73
AristocratFlowd                     -  260 matches, BRONZE IV    7c7d85b9-2176-4e58-b808-3e23cde848f9
Agafolk                             -  664 matches, BRONZE I     b9caa58a-c98d-49fb-9812-f2dac2d3c5df
ashleney (FurryPaws)                -  761 matches, SILVER II    014c2143-2684-486a-b4e2-70702f862513
Y0niZer0                            -  414 matches, SILVER V     34bcc877-4c7d-4908-b65a-f63b99287393
tfhalo5                             -  853 matches, SILVER II    a574f5da-85c6-4817-a402-f00e0b7f3833
ievosas                             -  144 matches, BRONZE V     1d08726c-4d63-42f3-9a1f-b083049bc703
Jus0599                             -  873 matches, SILVER IV    d302f585-5a3c-4797-8639-1d610d7f922c
amybulls                            -  165 matches, COPPER V     e62a4869-2db0-4695-b78f-77a3c80fbe6e
Binnils                             -  771 matches, COPPER V     cbf0ea80-7302-451f-8c57-25824840a477

== Squads ==
- Maxim_Marmelado, Agafolk, AristocratFlowd
- amybulls, Binnils

== Round history ==
amybulls         |           0  0  0 |           0  1  0 |           0  2  0 |           0  3  0 |           0  4  0 |           0  4  0 |           0  5  0 |           1  6  0 |           1  7  0    
Jus0599          |           0  0  0 |           2  0  0 |           5  0  1 |           7  1  1 |           7  2  1 |           9  3  1 |           9  4  1 |          12  4  1 |          12  5  1    
Binnils          |           0  0  0 |           2  1  0 |           3  1  0 |           3  2  0 |           3  3  0 |           3  4  0 |           3  5  0 |           4  5  0 |           7  6  0    
tfhalo5          |           0  0  0 |           1  0  0 |           1  0  1 |           1  1  1 |           3  2  1 |           4  3  2 |           4  4  2 |           4  4  2 |           4  5  2    
ievosas          |           0  0  0 |           0  1  0 |           1  1  0 |           1  2  0 |           2  3  0 |           3  3  0 |           3  4  0 |           3  4  0 |           3  5  0    
NVBEG_STYLX      | Jager     0  0  0 | Tubarao   1  1  0 | Warden    1  2  0 | Ace       2  3  1 | Ace       5  3  1 | Thermite  7  4  1 | Thermite 10  4  1 | Tachanka 10  5  1 | Striker  11  6  1    
FurryPaws165     | Mira      0  0  0 | Mira      0  1  0 | Wamai     0  2  0 | Jackal    0  2  0 | Buck      0  3  0 | Jackal    0  4  0 | Ace       1  4  1 | Mute      2  5  1 | Jackal    4  6  2    
Maxim_Marmelado  | Kaid      0  0  0 | Kaid      1  1  0 | Lesion    2  2  0 | Osa       4  2  0 | Fuze      4  3  3 | Ace       4  4  3 | Fuze      4  4  3 | Kaid      4  5  3 | Fuze      4  6  3    
Y0niZer0         | Castle    0  0  0 | Castle    1  1  0 | Goyo      1  2  0 | Ash       1  3  0 | Ash       3  3  0 | Thatcher  3  4  0 | Ash       3  4  0 | Smoke     3  5  0 | Ash       5  5  0    
Agafolk          | Kapkan    0  0  0 | Alibi     0  1  0 | Doc       0  2  0 | Glaz      1  2  0 | Lion      1  3  0 | Dokkaebi  2  4  0 | Dokkaebi  3  4  0 | Valkyrie  3  5  0 | Iq        3  6  0    
```

(uses ANSI colors for better readability)
