# ANTARAGA - Perekam & Plotter 3 Kanal PPG Mentah

Mengambil **data mentah** tiga panjang gelombang sekaligus dan menampilkannya
sebagai tiga kurva langsung di GUI, masing-masing bisa dimatikan/dinyalakan.

| kanal | panjang gelombang | sensor | rentang |
|---|---|---|---|
| MERAH | 660 nm | MAX30102 LED1 (I2C, FIFO) | 0..262143 (18-bit) |
| INFRAMERAH | 880 nm | MAX30102 LED2 (I2C, FIFO) | 0..262143 (18-bit) |
| HIJAU | 525 nm | SON1303 (analog A1/GPIO2) | 0..4095 (12-bit, oversample 16x) |

```
pio run -t upload                 # firmware
pip install pyserial              # sekali saja
python gui/plotter.py             # GUI (atau: python gui/plotter.py COM7)
```

Jangan buka serial monitor PlatformIO bersamaan dengan GUI - satu port hanya
bisa dipegang satu proses.

## Catu daya menurut skematik

**MAX30102 (J3) mendapat 3V3 LANGSUNG lewat ferrite B2 + C5/C6. Ia tidak
melewati Q2.** Yang dicatu lewat Q2 (DMP2130L, P-MOS) hanya SON1303 (J2):
D2 LOW = nyala, dan R5 100k menariknya ke 3V3 supaya default-nya mati saat
boot.

Konsekuensi praktis, dan ini dipakai sebagai fitur: tombol **"Hijau
mati/nyala"** di GUI (perintah `g`) hanya mematikan SON1303 - kanal merah dan
inframerah terus mengalir. Itu cara termurah membuktikan apakah LED hijau
525 nm ikut terbaca fotodioda MAX30102 lewat casing translusen: matikan hijau
sambil melihat kolom DC merah/inframerah di panel statistik. Kalau DC-nya
tidak bergeser, tidak ada penerangan silang.

## Kontrak serial

Baris data, satu per sampel MAX30102:

```
t_ms,green,red,ir,av
128450,1832,95312,185649,1
```

Baris yang diawali `#` adalah metadata/log dan ikut tersimpan saat merekam:

```
#ANTARAGA3CH v1
#ch=t_ms,green,red,ir,av
#max spo2=0x4F fifo=0x30 led_red=0x6F led_ir=0x5F rev=0x03 part=0x15
#stat t=5000 rows=982 fs=196.4 late=0 i2c_err=0 adc_fail=0 green=on
```

Perintah satu karakter (GUI punya tombolnya, atau ketik di serial monitor):

| | |
|---|---|
| `i` | cetak ulang blok info |
| `p` | jeda / lanjut aliran |
| `g` | SON1303 (hijau) mati/nyala |
| `z` | nolkan cacahan |
| `r` / `R` | arus MERAH turun / naik (langkah ~3,2 mA) |
| `f` / `F` | arus INFRAMERAH turun / naik |
| `d` / `D` | rentang ADC lebih peka / lebih kasar |
| `a` / `A` | SMP_AVE turun / naik |
| `=r6F` | setel absolut: arus merah. Juga `=f5F` (inframerah), `=d1` (rentang ADC), `=a1` (SMP_AVE), `=s3` (SR) |

Bentuk absolut itu yang dipakai `tune.py`: perintah relatif tidak cukup untuk
sapuan, karena satu perintah yang hilang membuat seluruh sisa sapuan mengukur
setelan yang salah tanpa ada yang tahu. Tiap perubahan digemakan sebagai baris
`#cfg`, dan penyetel menunggunya sebelum mulai mengukur.

### Dua keputusan rancangan yang perlu diketahui

**`t_ms` adalah `millis()` SUNGGUHAN saat sampel dibaca**, bukan indeks
dikalikan laju nominal. Ini bukan detail sepele: recorder lamamu
(`max30102_recorder_pwa_xiao_c3.ino`) menghitung `t_ms` dari FS nominal, dan
karena MAX30102 diam-diam meng-clamp SR ke 400 Hz, seluruh timing di file itu
meleset 2× tanpa satu pun tanda. Dengan `t_ms` nyata, kelas kesalahan itu
tidak bisa terjadi lagi - dan GUI menghitung `fs terukur` dari kolom itu.

**Loop dikendalikan FIFO MAX30102, bukan tick FreeRTOS.** Setiap kali chip
menghasilkan satu sampel, sampel itu diambil dan ADC hijau dibaca saat itu
juga, lalu satu baris dikirim. Akibatnya tidak ada baris berisi merah/
inframerah basi, hijau selalu tercuplik dalam ~1 ms dari pasangannya, dan laju
baris = laju nyata chip. Kolom `av` (sampel yang menunggu di FIFO saat dibaca)
= 1 berarti sehat; > 1 berarti pembacaan tertinggal.

Setelan bawaan: SR 400 Hz, SMP_AVE=2, PW 411 µs → **~196 Hz** keluaran.
Mau ~392 Hz? Ganti `CFG_FIFO` ke `0x10` (SMP_AVE=1) di
[src/main.cpp](src/main.cpp); tidak ada lagi yang perlu disentuh karena loop
mengikuti laju chip. Jangan meminta SR di atas 400 Hz - chip meng-clamp diam-
diam (sudah terukur di [../DiagMAX30102](../DiagMAX30102/)).

## Penyetel otomatis - `gui/tune.py`

```
python gui/tune.py COM3
```

Menyapu **rentang ADC × arus LED**, mengukur SNR nyata di tiap titik, lalu
merekomendasikan setelan terbaik lengkap dengan baris yang tinggal ditempel
ke `config.h`. Sekitar 50 detik; tempelkan sensor dan diam sampai selesai.

Kenapa rentang ADC ikut disapu, bukan cuma arus LED: `ADC_RGE` menentukan arus
foto skala penuh (2048/4096/8192/16384 nA). Rentang lebih kecil = lebih peka,
jadi arus foto yang sama menghasilkan lebih banyak cacahan **tanpa menambah
arus LED sedikit pun**. Karena derau di sini didominasi elektronik ADC - pada
DC 81.552 LSB derau tembakan foton hanya ~1 LSB sementara derau terukur ~5,1
LSB - memperkecil rentang menaikkan SNR hampir sebanding, dan malah
memungkinkan arus LED *diturunkan* untuk cacahan yang sama. Menaikkan arus LED
saja sampai ke DC yang sama dengan ongkos daya jauh lebih besar.

Sapuannya memakai dua titik per rentang (lantai gelap + satu arus uji) lalu
mengekstrapolasi arus yang mendaratkan DC di target 160k, karena hubungan
arus→DC memang linear (terbukti di sapuan [../DiagMAX30102](../DiagMAX30102/)).
Pemenangnya dipilih berdasarkan SNR terendah antar dua kanal, dengan daya LED
terkecil sebagai pemutus seri.

Firmware harus versi yang punya perintah setel-absolut (`=r6F`, `=d1`, …);
skrip menolak jalan kalau tidak, supaya tidak melaporkan sapuan yang tidak
pernah berlaku.

## GUI

- **3 kurva, masing-masing bisa dimatikan.** Kanal yang dimatikan sumbunya
  benar-benar dibuang, bukan disembunyikan, jadi tidak menyisakan ruang kosong.
- **Tumpuk 1 sumbu (ternormalisasi)** - ketiga kanal jadi z-score di satu
  sumbu. Ini satu-satunya cara membandingkan bentuk dan waktu-tunda antara
  hijau (525 nm, pantulan dangkal) dan inframerah (880 nm, menembus lebih
  dalam), karena skala mentahnya berbeda 60×.
- **Tampilkan AC saja** - buang baseline, untuk melihat riak denyut saja.
- Jendela 5/10/20/30/60 detik, tombol **Beku**, tombol **Bersihkan**.
- **Rekam CSV** - menyimpan aliran mentah apa adanya plus blok `#` metadata,
  jadi filenya menjelaskan dirinya sendiri.
- Tombol arus LED dan hijau mati/nyala, supaya bisa menyetel sambil melihat
  bentuk gelombangnya berubah.

### Panel statistik

Diperbarui 4×/detik dari jendela yang sedang tampil:

| kolom | arti |
|---|---|
| DC | rerata mentah |
| AC p2p (1 dtk) | puncak-ke-palung 1 detik terakhir, sebanding dengan `[T8]` di ../DiagMAX30102 |
| perfusi permil | 1000 × AC/DC |
| acuan permil | dari `rekam_ppg_merah_v2_irred1.txt`: merah 1,44 ‰, inframerah 3,03 ‰ |
| BPM | autokorelasi, memakai fs terukur |
| periodisitas | 0..1; **< 0,30 = tidak ada denyut**, BPM di sebelahnya cuma menafsir derau |

Kolom perfusi itu alat penempatan sensor yang paling berguna: geser sensor
sambil melihat angkanya, berhenti di posisi tertinggi.

## Yang sudah diverifikasi

Firmware compile bersih (RAM 6,4%, tanpa warning). Sisi Python diuji tanpa
perangkat, dan **dua bug nyata ketangkap oleh uji itu**:

1. **Penanganan tepi `detrend` merusak analisis.** `np.convolve(mode='same')`
   menganggap di luar array nilainya nol, dan tambalan "ratakan tepi ke satu
   konstanta" justru lebih buruk - plateau konstan berkorelasi sempurna dengan
   dirinya di semua lag, sehingga derau murni pun terlihat periodik (conf 0,45
   padahal seharusnya 0,05). Diganti rerata bergerak berjendela terpangkas.
2. **High-pass satu tingkat membuat BPM selalu ~220.** Gelombang napas
   0,25 Hz hanya tertekan ke ~53%, dan sisanya membuat autokorelasi meluruh
   monoton sepanjang rentang lag sehingga puncaknya selalu di lag terpendek.
   43 dan 60 bpm sintetis dilaporkan sebagai 222 bpm. High-pass dua tingkat
   menekan napas ke ~28% sementara 43 bpm lolos dengan gain 1,23.

Bug kedua ada juga di alat diagnostik C++, jadi
[../DiagMAX30102](../DiagMAX30102/) ikut diperbaiki dan diuji ulang dengan
fungsi aslinya diekstrak dan dijalankan di PC.

Hasil uji sekarang (PPG sintetis + napas 0,25 Hz, fs 200 Hz):

| target | Python | C++ (DiagMAX30102) |
|---|---|---|
| 43 bpm | 43,0 (conf 0,49) | 43,2 (conf 0,58) |
| 60 bpm | 60,3 (conf 0,40) | 60,0 (conf 0,51) |
| 75 bpm | 75,5 (conf 0,57) | 75,0 (conf 0,67) |
| 100 bpm | 100,8 | 100,0 |
| 150 bpm | 151,9 | 150,0 |
| 190 bpm | 190,5 | 190,5 |
| derau murni | conf 0,21 ✓ | conf 0,10 ✓ |

Uji asap GUI juga dijalankan: UI terbangun, data sintetis 15 detik masuk lewat
jalur antrean yang sama dengan pembaca serial, BPM di panel keluar 72,3 untuk
target 72,0, keempat kombinasi tampilan tergambar, kanal dimatikan satu-satu
sampai kosong, dan kelima ukuran jendela dicoba.

Uji itu juga mengungkap **bug ketiga**: dengan `constrained_layout=True`,
matplotlib menyelesaikan ulang tata letak pada setiap penggambaran sampai
menembus interval timer - callback Tk lalu menumpuk lebih cepat daripada yang
bisa dilayani, CPU penuh, jendela berhenti merespons. Sekarang tata letak
diatur sekali di `_rebuild_axes()`, dan tiap tick menjadwalkan tick berikutnya
berdasarkan biaya nyatanya sendiri. Biaya gambar terukur **27–43 ms (23–36
FPS)**; `ac_signal` 3 kanal 0,4 ms, `bpm_autocorr` 3 kanal 1,5 ms.

Yang belum teruji: aliran serial sungguhan dari papan (belum ada port
terdeteksi saat ini), jadi laju baris nyata dan perilaku sambung/putus baru
terbukti saat kamu menjalankannya dengan perangkat terpasang.
