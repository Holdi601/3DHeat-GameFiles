---
title: Sorun giderme
nav_order: 11
lang: "tr"
source: troubleshooting.md
source_hash: "3d2cd69d42e4"
nav_exclude: true
search_exclude: true
---
# Sorun giderme {#troubleshooting}

Araç bir şey durdurduğunda yazdığı mesajlar, her birinin ne anlama geldiği ve ne yapılacağı. Mesajlar koddan alıntılanmıştır; yer tutucular açılı parantez içindedir.

## Araç başlamadan önce {#before-the-tool-even-starts}

| Gördüğünüz | Yapın |
|---|---|
| `'python' is not recognized` | Python 3.10 ya da sonrasını kurun ve "Add python.exe to PATH" kutusunu işaretleyin; yeni bir terminal açın ([Başlamadan önce](before-you-start.md)) |
| `No module named heat3d_gamefiles` | terminal yanlış klasörde: `README.md` dosyasının bulunduğu klasöre `cd` yapın |
| `No module named numpy` (ya da başka bir paket) | `pip install -r requirements.txt` çalıştırın |
| bir yol boşluk içerdiği için kesiliyor ya da `unrecognized arguments` | yolu çift tırnak içine alın: `"C:\My Games\lap.json"` |

## Oyunu bulmak {#finding-the-game}

| Mesaj | Anlamı | Yapın |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | hiçbir Steam kütüphanesi ya da `C:\XboxGames` `media\Tracks` içeren bir oyun tutmuyor | `--track "<game>\media\Tracks\<map>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | turun koordinatları kurulu hiçbir parkurda yok | turun bu oyundan olduğunu denetleyin; parkur başka yerdeyse `--track` verin |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | kutunun yakınında karolar var ama sürüşü kapsayan yok | yukarıdaki gibi |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<folder with gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<game folder>"` |
| `no readable IoStore containers in <folder>` | klasörde açılan bir `.utoc` yok | `--install` değerini `.utoc` dosyalarının bulunduğu klasöre yöneltin |

## Yeri bulmak {#finding-the-place}

| Mesaj | Anlamı | Yapın |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG: hiçbir seviye %30 almadı | `--level <name>`; turun görüntüleyici çerçevesinde olduğunu denetleyin |
| `no level called '<name>'; installed: ...` | BeamNG: `--level` eşleşmedi | listelenen klasör adlarından birini kullanın |
| `<level> has no scene (no main/*.level.json and no .mis)` | seviye klasöründe sahne dosyası yok | bozuk ya da eksik bir seviye ya da mod |
| `no terrain of <level> lies along the driving.` | BeamNG: koridorda arazi karesi yok | yanlış seviye, ya da turun olduğu yerde arazisi olmayan bir seviye |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally: hiçbir etap ve çerçeve %50 almadı | `--level <stage>`; turun konumlarının y yukarı metre olduğunu denetleyin |
| `no stage called '<name>'; there are: ...` | AC Rally: `--level` eşleşmedi | listelenen adlardan birini kullanın |
| `no ground of <stage> lies along the driving.` | AC Rally: koridorda zemin karosu yok | yanlış etap |

## Tur {#the-lap}

| Mesaj | Yapın |
|---|---|
| `<file> is not a lap this can read. ...` | desteklenen bir biçim verin, bkz. [Tur girdileri](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON bir tur değil |
| `<file> has no x, y and z columns` | CSV sütunlarını `x`, `y`, `z` olarak adlandırın |
| `'<name>' is not a file, and no course in <library> matches it` | adı denetleyin ya da bir dosya verin |
| `'<name>' matches 3 courses: ...` | adın daha uzun bir parçasını kullanın |
| `<name> holds no driving` | turda ikiden az örnek var |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | `terrain --route`, `heat3d_capture route` ve `laps`'ın yazdığı gibi `bounds` içeren bir rota JSON'u ister; tur dosyası `course` içindir |
| `give exactly one of --box and --route` | `terrain` bir bölge ister |
| `no course export for this lap: <reason>.` | oyun desteklenmiyor, bkz. [Sınırlar ve bilinen eksikler](limits-and-known-gaps.md) |

## Arşivler {#archives}

| Mesaj | Anlamı |
|---|---|
| `no Oodle library found. ...` | `HEAT3D_OODLE` ayarlayın, bkz. [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | şifreli bir pak: anahtarınız varsa `--key <hex>`. Başka yol yok |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | anahtar 64 onaltılık basamak olarak yazılmış 32 bayttır, `0x` isteğe bağlı (çıkış kodu 2) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | bunlardan hiçbiri değil; `identify` ne olduğunu söyler. Bir Unity konteyneri `meshes` ister |
| `<file> is encrypted. This tool holds no keys and recovers none.` | şifreli bir IoStore konteyneri. Okunamaz |
| `pak version <n>; this reader handles 8-12` | daha eski ya da daha yeni bir pak biçimi |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | Python'dan: `.utoc` deneyin; `list` ve `extract` de onu alır |
| `<file> has no directory index, so its chunks carry no names to list` | dosya adı adlandırmayan bir IoStore konteyneri; parçalarına yalnızca başka paketler üzerinden ulaşılır |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | arşivin yanındaki `ChunkContentsMiniZip<n>.txt` başka bir yapıdan ya da başka bir arşivden; o olmadan girdiler numarasıyla listelenir |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | adlar yapım sırasında karmalandı |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | gizlenmiş biçimde bir Frostbite tablosu |
| `no Frostbite game found in a Steam library; give --install` | `levels` ya da `level`, `layout.toc` içeren bir `Data` klasörü olan bir Steam oyunu bulamadı; oyunun klasörünü verin |
| `no level called '<name>'; did you mean one of ...?` | ad hiçbir seviyenin tablosuyla eşleşmedi ya da birden çok eşleşti; `levels` hepsini listeler |
| `nothing was placed: no static model group was recognised` | seviyenin grup üyelerinin tür imzası farklı; bir oyun güncellemesinden sonra ya da başka bir Frostbite oyununda; düzen yeniden ölçülmelidir |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | sıkıştırılmış bir Unity mesh'i |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | `.resS` dosyasını `.assets` dosyasının yanında tutun |
| `<file>: format <n> predates Unity 2020 ...` | eski bir Unity yapısı |
| `<file> is an asset bundle, not a bare SerializedFile` | `meshes` düz bir konteyner alır |
| `texture format <n> has not been identified; refusing to guess` | henüz görülmemiş bir Forza numune biçimi |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | bölünmüş bir VPK'nin parçalarını birlikte tutun |

## Yanlış çıkan dışa aktarımlar {#exports-that-come-out-wrong}

| Belirti | Olası neden |
|---|---|
| parkur, görüntüleyicide turdan kaymış | tur ve dışa aktarım farklı çerçeveler kullanıyor: `--game` değerini denetleyin (örneğin bir BeamNG turunun Forza olarak okunması) |
| bir Forza parkurunda kenar yok | `--no-textures`, ya da karonun o `--season` için haritası yoktu (konsol `N without maps` yazar) |
| bir Forza karosu düz renklerde | zemin haritaları o mevsim için eksik |
| beklenenden çok daha az yerleştirilmiş nesne | açıkça verilen bir `--detail-budget` çok küçük; özet kaç kopyanın bırakıldığını söyler |
| dosya çok büyük (yüzlerce MB) | otomatik bütçe altında bir şehir koridoru; `--detail-budget`, `--texture-size 1024` ya da `--margin 40` kullanın |
| çitler eksik | saydam yüzeyler kasıtlı olarak bırakılır (özet bunları adlandırır) |
| `N meshes could not be read` | bazı modeller okuyucunun reddettiği bir biçim kullanıyor; geri kalanı yine de dışa aktarılır |
| `N of M components could not be read` (AC Rally) | bir oyun yaması özellik yuvalarını kaydırmış olabilir; lütfen bildirin |
