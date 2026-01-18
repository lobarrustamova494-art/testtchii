Sen tajribali computer vision engineer + system architect sifatida ishlaysan.
Maqsad — kamera orqali rasm olishga majbur qilingan, barqaror va aniq ishlaydigan OMR asosidagi imtihon tekshirish tizimini yaratish.

1. Asosiy prinsip

Tizim oddiy rasm upload ga tayanmasin.
Tekshirish faqat kamera orqali olingan, nazorat ostidagi rasm bilan ishlashi shart.

Sabab:

fon shovqini

begona obyektlar

noto‘g‘ri burchak
OMR aniqligini buzadi.

2. Kamera sahifasi (majburiy)

Kamera sahifasi hujjat skaneri kabi ishlashi kerak.

Ekranda doimiy:

A4 nisbatdagi ramka

4 burchak indikator

“Qog‘ozni ramkaga joylashtiring” logikasi

Kamera har frame’da:

varaq konturini aniqlaydi

4 burchakli eng katta to‘rtburchakni topadi

Capture faqat quyidagi shartlarda ruxsat etiladi:

varaq to‘liq kadrda

barcha 4 burchak ko‘rinib turibdi

varaq A4 nisbatga yaqin

kamera qimirlamayapti

ortiqcha obyektlar kadrga chiqmagan

Aks holda capture bloklanadi.

3. Capture’dan keyingi majburiy pipeline

Surat olingach darhol:

Topilgan 4 burchak bo‘yicha:

perspektiva tekislanadi

Varaq:

to‘liq qirqib olinadi

fon, stol, qo‘l, chekka soya yo‘q qilinadi

Varaq:

standart A4 o‘lchamga majburan moslanadi

masalan 2480×3508 px

Shundan keyin tizim faqat toza varaq bilan ishlaydi.

4. Corner markerlarni aniqlash

Corner markerlar:

faqat qirqilgan varaq ichidan qidiriladi

tashqi fon hisobga olinmaydi

Aniqlanadi:

4 ta corner marker markazi

ular orasidagi masofa

Bu masofa:

“Qog‘ozdagi corner markerlar orasidagi masofa” deb belgilanadi

5. Template bilan moslashtirish

Imtihon yaratilganda:

corner markerlar orasidagi masofa

savollar koordinatalari

bubble koordinatalari
aniq saqlangan bo‘ladi.

Tekshiruvda:

template marker masofasi

qog‘oz marker masofasi
nisbati hisoblanadi.

Shu nisbat asosida:

savollar

bubble’lar
qog‘ozdagi real joylashuvga moslab qayta hisoblanadi.

Hardcoded koordinata bo‘lmasin.

6. Bubble tekshirish

Har bir bubble uchun:

alohida ROI olinadi

tashqi doira devori kesib tashlanadi

faqat ichki maydon analiz qilinadi

Aniqlash:

fill ratio

markaziy qorayish

shovqin filtri

Qoidalar:

1 savol → 1 belgi → tekshiriladi

0 belgi → blank

2+ belgi → noto‘g‘ri

yarim chizilgan yoki o‘chirilgan belgilar → belgi emas

7. Natijani vizual ko‘rsatish

Tekshiruv natijasida:

to‘g‘ri belgilangan bubble → ko‘k ramka

noto‘g‘ri belgilangan bubble → qizil ramka

asl to‘g‘ri javob bubble → yashil ramka

Bu ramkalar:

tekshirish sahifasida

rasm ustiga overlay sifatida chiziladi.

8. Majburiy talab

Agar:

bu oqimda xato bo‘lsa

barqarorroq yoki ishonchliroq yechim mavjud bo‘lsa

real imtihon sharoitida xavfli joy bo‘lsa

unda:

muammoni ochiq ayt

sababini tushuntir

yaxshiroq yechim taklif qil

kerak bo‘lsa aniqlashtiruvchi savol ber

Taxmin qilma.
Sukut saqlama.

9. Yakuniy maqsad

Natija:

EvalBee darajasidagi

kamera asosida ishlaydigan

barqaror, aniqligi yuqori

real imtihonda ishlaydigan
OMR tizim bo‘lishi kerak.
