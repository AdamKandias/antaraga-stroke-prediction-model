# ANTARAGA BPM — hitung denyut dari SON1303, di perangkat

XIAO ESP32-S3. Mencuplik SON1303 dengan front-end **identik** dengan
[../Firmware](../Firmware) (A1/GPIO2, 200 Hz, oversample 16x, atenuasi 12 dB,
12 bit), lalu menghitung **BPM di tempat** dan mencetaknya ke serial. Tanpa
WiFi, tanpa cloud, tanpa MAX30102.

Front-end yang identik itu inti programnya: BPM di sini dihitung dari deretan
angka yang persis sama dengan yang dikirim firmware streaming ke cloud. Jadi
kalau hasilnya berbeda dari hitungan cloud, penyebabnya **algoritma** — bukan
beda cara mencuplik.

| | ../Firmware | program ini |
|---|---|---|
| Sensor | MAX30102 + SON1303 | SON1303 saja |
| Pemrosesan sinyal | **tidak ada** (mentah dikirim) | band-pass + deteksi puncak |
| BPM dihitung | di cloud | **di perangkat** |
| Jaringan | WiFi + HTTPS + OTA | tidak ada |
| Keluaran | POST JSON tiap 1000 ms | baris serial tiap 1000 ms + LED per detak |

Dua tujuan yang bertolak belakang, karena itu dua firmware: analisis morfologi
(PWA/VPG/APG) di cloud butuh sinyal mentah yang tak tersentuh, sedangkan
mencari puncak butuh sinyal yang sudah dibersihkan. Menggabungkannya berarti
salah satu harus dikompromikan.

## Algoritma — enam lapis

Tiap lapis menangkap kelas kesalahan yang lapis lain **tidak bisa lihat**.
Seluruhnya di [src/bpm.cpp](src/bpm.cpp); ambangnya di
[include/config.h](include/config.h).

```
ADC mentah (200 Hz, 12-bit)
      │
 (1)  ├─ BAND-PASS 0,5–5 Hz   Butterworth orde-2 bertingkat (HP lalu LP).
      │                        Buang baseline wander di bawah, dengung
      │                        jala-jala 50/100 Hz di atas.
      │
 (2)  ├─ PELACAK AMPLITUDO    Serangan seketika, peluruhan 0,6/detik.
      │                        Ambang jadi relatif terhadap amplitudo yang
      │                        sedang berjalan, bukan angka mati.
      │
 (3)  ├─ EKSURSI HISTERESIS   Naik di 60% amplitudo, selesai di 40%,
      │                        blanking 260 ms setelah tiap puncak.
      │
 (4)  ├─ PUNCAK SUB-SAMPEL    Maksimum lokal TERBESAR dalam eksursi,
      │                        diperhalus interpolasi parabola 3 titik.
      │
 (5)  ├─ GERBANG INTERVAL     Rentang 30–220 bpm + simpangan maks 30% dari
      │                        MEDIAN riwayat 8 interval, dengan perbaikan
      │                        denyut terlewat dan jalur re-sync.
      │
 (6)  └─ SKOR KEYAKINAN       MINIMUM dari 4 sub-skor → status LOCKED / NOISY /
                               SEARCHING / NO_CONTACT / SETTLING.
```

### Keputusan rancangan yang perlu diketahui

**Band-pass 0,5–5 Hz, bukan lebih lebar.** LP 5 Hz menumpulkan *dicrotic
notch* — di sini itu **diinginkan**, supaya notch tidak pernah ikut terhitung
sebagai denyut. Koefisiennya **dihitung saat runtime** dari `PPG_FS_HZ`, bukan
ditempel sebagai angka mati: koefisien mati yang didesain untuk 200 Hz akan
menggeser pita lolosnya diam-diam kalau laju sampel diubah — filter tetap
jalan, hasilnya saja yang salah, tanpa satu pun pesan error. Pada 200 Hz,
fungsi desainnya menghasilkan koefisien yang **sama** dengan yang dipakai
`PPG_SEN0203_recorder_raw_pwa_60s.ino`, jadi jalur sinyalnya identik dengan
rekaman yang sudah kamu validasi.

**Ambang adaptif, bukan tetap.** Amplitudo PPG pergelangan berubah beberapa
kali lipat hanya karena tekanan kontak. Ambang tetap selalu salah: kalau pas
untuk sinyal kuat, ia melewatkan seluruh denyut lemah.

**Histeresis 60%/40%.** Dengan satu ambang, riak kecil di sekitarnya memicu
belasan "denyut" per detak.

**Interpolasi parabola.** Di 200 Hz, kuantisasi 5 ms saja sudah bernilai
~0,4 bpm pada 60 bpm. Tiga titik menghapus hampir seluruh jitter itu.

**Median, bukan rerata** — di gerbang interval maupun di penilaian
kestabilan. Satu interval sampah tidak boleh menggeser acuan yang menilainya
sendiri. Alasan yang sama dipakai gerbang SQI di
[../Firmware/src/sqi.cpp](../Firmware/src/sqi.cpp).

**Skor = MINIMUM sub-skor, bukan rata-rata.** Rata-rata menyamarkan outlier;
satu aspek rusak harus bisa menjatuhkan seluruh keputusan.

**Basis waktu = cacahan sampel, bukan `millis()`.** Cacahan sampel dikunci
tick FreeRTOS; `millis()` di dalam task yang juga meladeni USB-CDC bisa
tergeser beberapa milidetik, dan pergeseran itu masuk langsung ke interval
sebagai jitter BPM.

**Jalur re-sync.** Gerbang median menolak apa pun yang melenceng >30% — tanpa
jalan keluar, laju jantung yang berubah cepat (mulai bergerak, berdiri) akan
ditolak selamanya dan detektor mengunci dirinya sendiri. Setelah 4 penolakan
berurutan, riwayat dibuang dan kunci dibangun ulang.

**Angka basi dinolkan.** BPM terakhir ditahan maksimal 5 detik setelah sinyal
memburuk, lalu dinolkan. Di layar, "72" yang membeku terlihat persis seperti
pengukuran hidup — itu satu-satunya salah baca yang benar-benar berbahaya di
sini. Nilai yang sedang ditahan dicetak **dalam tanda kurung**.

## Struktur

| File | Isi |
|---|---|
| [include/config.h](include/config.h) | semua yang bisa disetel: akuisisi, filter, ambang detektor, gerbang mutu |
| [include/bpm.h](include/bpm.h) | kontrak mesin BPM — **tanpa Arduino**, supaya bisa dikompilasi di PC |
| [src/bpm.cpp](src/bpm.cpp) | seluruh algoritma (6 lapis di atas) |
| [include/ppg.h](include/ppg.h), [src/ppg.cpp](src/ppg.cpp) | lapisan ADC (shim core 2.x/3.x) + task pencuplik 200 Hz |
| [src/main.cpp](src/main.cpp) | banner, LED per detak, baris `[BPM ]` & `[STAT]` |
| [tools/bpm_csv.cpp](tools/bpm_csv.cpp) | penguji di PC — **bukan** bagian firmware |

## Flash & pakai

```
pio run -e seeed_xiao_esp32s3 -t upload
pio device monitor
```

Tempelkan sensor, **diam**, tunggu status `LOCKED` (~4 detik: 1 detik settle
sensor + 3 detik transien filter, lalu 4 denyut valid).

```
[BPM ]  72.4 bpm  conf  88  LOCKED     | inst  72.1 | ibi  829 ms sdnn  14
       ac=214    dc=1832   pi=117 permil clip=0 | denyut=53 tolak=2 interp=1 resync=0
[STAT] up=25s | sampel=4800 (fs_ukur~200.0 Hz) | overrun=0 adc_gagal=0 | heap=298476
```

Yang perlu dibaca:

- **status** — hanya `LOCKED` yang layak dipakai. `SEARCHING` = sinyal ada,
  denyut valid belum cukup. `NOISY` = denyut terdeteksi tapi mutunya di bawah
  `BPM_MIN_CONF`. `NO_CONTACT` = sensor tidak menempel.
- **bpm dalam tanda kurung** — nilai tertahan, bukan pengukuran hidup.
- **overrun** — harus **0**. Kalau tidak nol, jadwal 5 ms tidak terpenuhi dan
  seluruh basis waktu interval ikut meleset dengan faktor yang sama.
- **fs_ukur** — harus ~`PPG_FS_HZ`. Ini yang membuktikan basis waktunya sehat.
- **interp** tinggi → yang perlu dibetulkan kontak sensornya, bukan ambangnya.
- **tolak/resync** tinggi saat diam → ambang atau kontak perlu disetel.

### LED D10

| pola | arti |
|---|---|
| kedip sedang (250 ms) | settle, atau sensor tidak menempel |
| kilat per detak | sedang mengukur ← normal |

## Kalibrasi ambang — lihat sinyalnya, jangan menduga

Ambang yang **paling perlu** disetel untuk unitmu adalah jendela DC
(`BPM_DC_MIN` / `BPM_DC_MAX`) dan amplitudo minimum (`BPM_AC_MIN_LSB`), karena
keduanya bergantung pada rangkaian dan titik pemasangan, bukan pada algoritma.

Setel `BPM_STREAM_CSV 1` di [include/config.h](include/config.h) → tiap sampel
dicetak sebagai CSV:

```
t_ms,raw,ac,thr_hi,thr_lo,beat,bpm,status
```

Buka Serial Plotter (atau simpan ke file lalu plot). Yang dicari: `ac` naik
melewati `thr_hi` tepat sekali per detak, `beat` menyala di puncaknya, dan
`raw` tidak menyentuh 0 atau 4095. Catat `dc` saat menempel dan saat dilepas —
dua angka itu yang menentukan jendela DC-mu.

Mode ini mencetak dari dalam task pencuplik, jadi `overrun` akan naik.
Matikan lagi saat mengukur sungguhan.

## Uji algoritma di PC (tanpa board)

`src/bpm.cpp` sengaja tidak menyentuh Arduino, jadi **file yang sama** bisa
dijalankan di host terhadap sinyal yang laju denyutnya sudah diketahui. Serial
monitor tidak bisa memberi tahu apakah "72 bpm" itu benar; uji ini bisa.

```
pio run -e native -t exec                          # 14 uji regresi
.pio/build/native/program rekaman.csv > out.csv    # rekaman recorder-mu
```

Tanpa PlatformIO, dari folder ini:

```
g++ -std=c++11 -O2 -Iinclude src/bpm.cpp tools/bpm_csv.cpp -o bpmtest
```

Hasil uji regresi saat ini (galat terhadap laju yang diketahui):

```
bradikardia 45 bpm       rerata 44,98   galat maks 0,02   OK
istirahat 60 bpm         rerata 60,00   galat maks 0,01   OK
normal 75 bpm            rerata 75,00   galat maks 0,02   OK
jalan cepat 100 bpm      rerata 100,00  galat maks 0,03   OK
olahraga 150 bpm         rerata 150,00  galat maks 0,04   OK
maksimal 190 bpm         rerata 190,01  galat maks 0,11   OK
sinyal lemah (ac 40)     rerata 72,05   galat maks 0,11   OK
derau tinggi (25 LSB)    rerata 71,96   galat maks 0,08   OK
baseline melayang kuat   rerata 71,99   galat maks 0,07   OK
1 dari 5 denyut hilang   rerata 72,01   galat maks 0,03   OK   (interp=6)
DC rendah / DC tinggi    rerata 72,00   galat maks 0,01   OK
loncatan 72->130 bpm     kunci ulang 3,9 detik            OK
sensor dilepas (datar)   NO_CONTACT, bpm=0                OK
```

Gelombang sintetisnya **sengaja tidak sinus** — ia memuat dicrotic notch,
karena notch itulah kandidat denyut-palsu utama. Sinus akan membuat detektor
terlihat sempurna secara palsu.

Uji "sensor dilepas" yang paling penting: detektor yang mengarang 70 bpm dari
derau ADC saat sensor tidak menempel jauh lebih berbahaya daripada detektor
yang sesekali kehilangan kunci.

**Angka di atas membuktikan algoritmanya, bukan sensornya.** Yang belum diuji
di sini: sinyal SON1303 nyata dari pergelangan tangan yang bergerak. Untuk
itu, rekam dengan
`../Firmware/.claude/programoptimasi/PPG_SEN0203_recorder_raw_pwa_60s.ino`
lalu jalankan CSV-nya lewat mode kedua di atas, dan bandingkan dengan alat
ukur acuan.

## Kalau `PPG_FS_HZ` atau `PPG_OVERSAMPLE` diubah di ../Firmware

Ubah juga di sini, supaya bagian `[AKUISISI]` kedua config tetap sama.
Koefisien filter, blanking, dan panjang jendela dihitung ulang otomatis dari
`PPG_FS_HZ` — tidak ada angka mati yang perlu disentuh.
