1. Kamera ochilishi

Maqsad bitta:
varaqni standart holatga majburan keltirish.

Ekranda ko‘rasan:

A4 ramka

4 burchak indikator

“Hold steady” logikasi

Bu dizayn uchun emas.
Bu algoritmga yordam.

2. Real-time varaqni aniqlash

Kamera har frame’da:

Edge detection qiladi

To‘rt burchakni izlaydi

Varaq topilmaguncha capture yo‘q

Agar:

varaq qiyshaygan bo‘lsa

bir qismi kadrdan chiqsa
→ surat olinmaydi

Bu juda muhim qaror.

3. Perspektivani majburiy tekislash

Surat olingach darhol:

4 burchakdan homography

Varaq ideal A4 ga tortiladi

Qiyalik, buralish yo‘q qilinadi

Shundan keyin:

kamera rasmi emas

modelga mos tekis varaq olinadi

EvalBee kuchi shu yerda.

4. Oldindan ma’lum layout ishlatiladi

EvalBee’da:

tasodifiy o‘qish yo‘q

“qayerda savol bor?” deb qidirmaydi

U biladi:

savol 1 qayerda

A/B/C/D doiralari aniq koordinatada

Ya’ni:

template-based OMR

5. Har bir katak alohida ROI

Har doira uchun:

kichik kvadrat ROI olinadi

tashqi doira devori kesib tashlanadi

faqat ichki maydon qoladi

Shu sabab:

doira chizig‘i

yonidagi chiziq
hisobga kirmaydi

6. Belgini aniqlash formulasi

EvalBee bitta shart bilan ishlamaydi.

U kombinatsiya qiladi:

qora piksel foizi

markaziy zichlik

kontur yuzasi

shovqin filtri

Natija:

yarim chizilgan → belgi emas

o‘chirilgan → bo‘sh

to‘liq bo‘yalgan → belgi

7. Savol darajasida validatsiya

EvalBee hech qachon:

“eng qorasi”ni tanlamaydi

Qoidalar:

1 savol → 1 belgi → OK

0 belgi → blank

2+ belgi → invalid

Bu qat’iy. Murosa yo‘q.

8. Real-time feedback

Kamera sahifasida darhol:

xato savollar soni

o‘qilmagan savollar

ogohlantirish chiqadi

Shuning uchun:

foydalanuvchi darhol qayta oladi

serverga yomon data bormaydi

9. Capture → analyze → confirm

Flow:

kamera → preview

tezkor analiz

foydalanuvchi tasdiqlaydi

keyin serverga yuboriladi

Bu:

xatoni oldindan ushlash

backendni yengillashtirish

Qisqa, lekin hal qiluvchi xulosa

EvalBee kuchi:

kamera emas

AI emas

Kuch:

qat’iy layout

majburiy perspektiva

savol-darajali mantiq

Agar sen:

kamera sahifasini shunchaki “rasm olish” deb qilsang
→ hech qachon EvalBee darajasiga chiqolmaysan
