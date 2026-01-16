1. Eng katta muammo: yarim belgilashlar hanuz “to‘liq” deb olinmoqda

Ko‘p yashil kataklarda:

faqat bitta egri chiziq

yoki doiraning ichki devoriga tegib ketgan qalam izi

Shunga qaramay tizim:

ularni “belgilangan” deb qabul qilgan

Bu nimani anglatadi:

sen hali ham binary threshold ga haddan tashqari ishonayapsan

“qora piksel bor → belgilandi” logikasi ishlayapti

To‘g‘ri yondashuv:

doira ichidagi to‘liq maydonning foizi hisoblanishi shart

devorga tekkani hisobga olinmasligi kerak

2. To‘liq bo‘yalgan belgilar bilan qisman belgilar farqlanmayapti

Qizil kataklar:

to‘liq qoraygan

markazi to‘la

Yashil kataklar:

faqat chiziq

bo‘shliq katta

Lekin algoritm ikkalasini bir xil sinfga tashlayapti.

Bu yerda yetishmayotgan narsa:

fill ratio normalization

kontur ichidagi real bo‘yalgan maydon

Aks holda:

o‘quvchi xato o‘chirgan bo‘lsa ham

tizim “javob bor” deydi

3. Vertikal ustunlar bo‘yicha siljish hanuz bor

Ayniqsa:

1–5

27–31
oralig‘ida

Belgilar:

to‘g‘ri ustunda emas

yon ustundan o‘qib ketilgan

Bu nimadan:

savollar global grid bilan o‘qilmoqda

savol satri bo‘yicha lokal referensiya yo‘q

To‘g‘ri yechim:

har savol satri uchun alohida y-anchor

keyin faqat o‘sha satr ichidagi variantlar

4. Bir savolda bir nechta belgi muammosi qisman tuzatilgan, lekin to‘liq emas

Ijobiy tomoni:

ayrim joylarda ko‘k bilan to‘g‘ri “invalid” ajratilgan

Salbiy tomoni:

ba’zi savollarda 2 ta belgi bo‘lsa ham

bittasi tanlab yuborilgan

Qat’iy qoida bo‘lishi kerak:

1 savol → 1 ta aniq belgi

2+ belgi → savol bekor

Hech qanday “eng qorasi”ni tanlash yo‘q.

5. Variant ustuni bilan savol raqami yaqin joylarda xato

O‘ng tomondagi ustunda:

savol raqami yonidagi chiziqlar

ba’zan belgi sifatida tushib qolgan

Bu:

ROI (region of interest) haddan tashqari katta

keraksiz joylar ham analiz qilinmoqda

6. Perspektiva hali ham to‘liq kompensatsiya qilinmagan

Belgilar:

yuqorida to‘g‘ri

pastda ko‘proq xato

Bu klassik belgisi:

homography bor, lekin yetarli emas

yoki 4 burchak noto‘g‘ri topilgan

EvalBee bu joyda:

sahifani qat’iy A4 modelga tortadi

keyin gridni joylashtiradi
