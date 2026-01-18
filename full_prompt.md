Sen tajribali computer vision + backend engineer sifatida ishlaysan.
Sening vazifang — mavjud loyihani to‘liq o‘rganish, tahlil qilish va takomillashtirish.

1. Loyihani tushunish

Loyihadagi barcha kodlarni o‘qi

Mavjud barcha tizimlarni tahlil qil

Imtihon yaratish, PDF generation va tekshirish oqimini to‘liq tushun

Agar:

mantiqsiz joy

noaniqlik

yaxshiroq alternativ yechim
bo‘lsa, albatta ayt va taklif qil.

2. Imtihon yaratish bosqichi (template generation)

Imtihon yaratilganda quyidagilar aniq koordinatalashtirilishi shart:

Qog‘ozda joylashgan 4 ta corner marker

Corner markerlar orasidagi:

masofa

nisbat

A4 o‘lchamga nisbati

Har bir savol uchun:

savol satrining koordinatalari

har bir variant (bubble) uchun:

markaz koordinatasi

radius / o‘lcham

savol ID bilan bog‘lanishi

Bu ma’lumotlar:

JSON ko‘rinishida

imtihon template’iga bog‘lanib saqlanishi kerak

Ya’ni:
Imtihon = qat’iy koordinatali OMR template

3. Javob kalitlarini belgilash

Imtihon yaratilgach

Maxsus sahifada:

har bir savol uchun to‘g‘ri bubble belgilanadi

Bu javoblar:

template koordinatalari bilan bog‘lanadi

keyinchalik tekshiruvda ishlatiladi

4. PDF generation

Imtihon:

titul / javob varaq ko‘rinishida

corner markerlar bilan

PDF qilib yuklab olinadi

O‘quvchiga chop etib beriladi

5. O‘quvchi javoblarni belgilashi

O‘quvchi qog‘ozda bubble’larni belgilaydi

Qog‘oz rasmga olinadi

Tekshirish sahifasiga rasm fayl sifatida yuklanadi

6. Tekshirish (scan & analyze)

Yuklangan rasm bilan ishlash ketma-ketligi:

Rasmda corner markerlarni top

Corner markerlar orasidagi masofani hisobla
→ bu “Qog‘ozdagi corner markerlar orasidagi masofa” deb belgilanadi

Imtihon yaratilgandagi:

“Template corner marker masofasi”
bilan

“Qog‘ozdagi corner marker masofasi”
o‘rtasidagi nisbatni hisobla

Shu nisbat asosida:

savollar koordinatalari

bubble’lar koordinatalari
qog‘ozdagi real joylashuvga moslab qayta hisobla

7. Javoblarni aniqlash va tekshirish

Har bir savol uchun:

o‘quvchi belgilagan bubble aniqlansin

Belgilangan bubble:

savol ID bilan bog‘lansin

To‘g‘ri javob bilan solishtirilsin

Vizual natija:

To‘g‘ri belgilangan bubble → ko‘k ramka

Noto‘g‘ri belgilangan bubble → qizil ramka

Asl to‘g‘ri javob bubble → yashil ramka

Bu ramkalar:

tekshiruv sahifasida rasm ustiga overlay qilinishi kerak

8. Qoidalar va validatsiya

1 savolda:

0 belgi → blank

1 belgi → tekshiriladi

2+ belgi → noto‘g‘ri

Yarim chizilgan, o‘chirilgan, devorga tekkan belgilar:

alohida tahlil qilinishi kerak

9. Muhim talab

Tizim:

hardcoded joylashuvsiz

faqat corner marker + nisbat asosida
ishlashi shart.

10. Yakuniy talab

Agar:

bu oqimda xato bo‘lsa

yoki yaxshiroq algoritm mavjud bo‘lsa

yoki hozirgi yondashuv xavfli bo‘lsa

buni ochiq ayt, sababini tushuntir va yaxshiroq yechim taklif qil.
